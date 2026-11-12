"""Offline SMART comparisons and explicit approval receipt outside the ZIP."""

import re
from pathlib import Path

from .bundle import sha256
from .common import PhaseError, read_json

AC_PATTERN = re.compile(r"(?m)^\|\s*(AC[0-9]{2})\s*\|")


def _structure(markdown: str, language: str) -> set[str]:
    required = ["## S", "## M", "## A", "## R"]
    required += (["## Périmètre inclus", "## Hors périmètre"] if language == "fr" else ["## In scope", "## Out of scope"])
    for heading in required:
        if not re.search(rf"(?m)^{re.escape(heading)}(?:\s|\s*—|$)", markdown):
            raise PhaseError(f"SMART {language.upper()} missing required section: {heading}")
    acs = AC_PATTERN.findall(markdown)
    if not acs or len(acs) != len(set(acs)):
        raise PhaseError(f"SMART {language.upper()} must contain unique ACxx table IDs")
    return set(acs)


def inspect_approvals(english: bytes, french_path: Path, receipt_path: Path, phase: str) -> dict:
    """Require documented human decisions, not infer semantics from matching IDs."""
    try:
        french = french_path.read_bytes()
        french_text = french.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise PhaseError("Approved French SMART unavailable outside ZIP") from exc
    french_acs = _structure(french_text, "fr")
    english_acs = _structure(english.decode("utf-8"), "en")
    if french_acs != english_acs:
        raise PhaseError("SMART FR/EN acceptance IDs differ")
    record = read_json(receipt_path)
    required = {
        "phase", "smart_fr_sha256", "smart_en_sha256", "smart_fr_approved",
        "semantic_equivalence_approved", "decision_reference", "approved_by",
    }
    if set(record) != required:
        raise PhaseError("Approval record must contain exactly the documented fields")
    if (record["phase"] != phase
            or record["smart_fr_sha256"] != sha256(french)
            or record["smart_en_sha256"] != sha256(english)
            or record["smart_fr_approved"] is not True
            or record["semantic_equivalence_approved"] is not True
            or not isinstance(record["decision_reference"], str)
            or not record["decision_reference"].strip()
            or not isinstance(record["approved_by"], str)
            or not record["approved_by"].strip()):
        raise PhaseError("SMART approvals missing, outdated, or mismatched")
    return {"french_sha256": sha256(french), "english_sha256": sha256(english),
            "acceptance_ids": sorted(french_acs), "decision_reference": record["decision_reference"]}
