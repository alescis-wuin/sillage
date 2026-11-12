"""Shared failure reporting, constrained subprocess execution and JSON parsing."""

import json
import os
from pathlib import Path
import subprocess


class PhaseError(Exception):
    """A rejected input or an unverifiable prerequisite (never implicit success)."""


def command(argv: list[str], *, cwd: Path | None = None, input_text: str | None = None) -> str:
    """Run only caller-selected argv; never use a shell or executable from a bundle."""
    try:
        result = subprocess.run(
            argv,
            cwd=cwd,
            input=input_text,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GH_PROMPT_DISABLED": "1"},
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        raise PhaseError(f"Unavailable command: {argv[0]} ({type(exc).__name__})") from exc
    if result.returncode:
        # Do not print stderr: a credential helper or external tool can expose private data.
        raise PhaseError(f"Command failed ({argv[0]} {argv[1] if len(argv) > 1 else ''}), exit={result.returncode}")
    return result.stdout.strip()


def no_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    obj = {}
    for key, value in pairs:
        if key in obj:
            raise PhaseError(f"Duplicate JSON key: {key}")
        obj[key] = value
    return obj


def load_json_bytes(raw: bytes) -> dict:
    def reject_constant(value: str) -> None:
        raise PhaseError(f"Non-standard JSON value: {value}")

    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=no_duplicate_keys,
            parse_constant=reject_constant,
        )
    except (UnicodeError, ValueError) as exc:
        raise PhaseError("Invalid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise PhaseError("Expected a JSON object")
    return value


def read_json(path: Path) -> dict:
    try:
        return load_json_bytes(path.read_bytes())
    except OSError as exc:
        raise PhaseError(f"JSON input unavailable: {path.name}") from exc
