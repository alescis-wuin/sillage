"""Verify personal signing identity; GitHub's Verified badge is insufficient."""

from pathlib import Path
import re

from .common import PhaseError, command


def expected_signer(path: Path) -> str:
    try:
        fingerprint = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise PhaseError("Owner-approved signing fingerprint file is unavailable") from exc
    # Supports OpenPGP hexadecimal and Git SSH SHA256 fingerprints.
    if not re.fullmatch(r"(?:[0-9A-Fa-f]{40,64}|SHA256:[A-Za-z0-9+/=]{16,})", fingerprint):
        raise PhaseError("Approved signing fingerprint has invalid syntax")
    return fingerprint


def verify_commit(sha: str, expected: str, root: Path) -> None:
    command(["git", "verify-commit", sha], cwd=root)
    details = command(["git", "show", "--no-patch", "--format=%G?%x09%GF", sha], cwd=root)
    try:
        grade, fingerprint = details.splitlines()[0].split("\t", 1)
    except (IndexError, ValueError) as exc:
        raise PhaseError("Git did not expose a verifiable commit signer") from exc
    if grade not in ("G", "U") or fingerprint.casefold() != expected.casefold():
        raise PhaseError("Commit signing identity differs from the owner's approved key")


def verify_annotated_tag(tag: str, expected: str, root: Path) -> None:
    kind = command(["git", "cat-file", "-t", tag], cwd=root)
    if kind != "tag":
        raise PhaseError("Only annotated, signed tags are allowed")
    details = command(["git", "verify-tag", "--format=%(signature:grade)%09%(signature:fingerprint)", tag], cwd=root)
    try:
        grade, fingerprint = details.splitlines()[-1].split("\t", 1)
    except (IndexError, ValueError) as exc:
        raise PhaseError("Git did not expose a verifiable tag signer") from exc
    if grade not in ("G", "U") or fingerprint.casefold() != expected.casefold():
        raise PhaseError("Tag signing identity differs from the owner's approved key")
