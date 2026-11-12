"""Read-only repository structure, JSON Schema and Python syntax controls."""

import argparse
import ast
from pathlib import Path
import sys

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError, SchemaError

from .common import PhaseError, read_json

SCHEMA = Path("design/fr/specifications/schemas/development/v1/phase-start.schema.json")
EXAMPLE = Path("design/fr/specifications/examples/development/v1/phase-start.json")
REQUIRED = (
    "README.md", "Makefile", "design/fr/ROADMAP.md", ".github/ISSUE_TEMPLATE/phase.md",
    ".github/ISSUE_TEMPLATE/step.md", ".github/PULL_REQUEST_TEMPLATE.md",
    ".githooks/pre-commit", ".githooks/commit-msg", ".githooks/pre-push",
    "templates/phase/SMART.fr.md", "templates/phase/SMART.en.md",
    "templates/phase/SUMMARY.en.md", "templates/phase/PROMPT.fr.md",
    "templates/phase/HANDOFF.fr.md",
)


def validate_schema(schema: dict, instance: dict) -> None:
    try:
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(instance)
    except (SchemaError, ValidationError) as exc:
        raise PhaseError(f"Invalid development JSON contract: {exc.message[:200]}") from exc


def syntax_source(source: str, filename: str) -> None:
    try:
        ast.parse(source, filename=filename)
    except SyntaxError as exc:
        raise PhaseError(f"Python syntax failure: {filename}:{exc.lineno}") from exc


def structure(root: Path) -> None:
    for item in REQUIRED:
        candidate = root / item
        if not candidate.is_file() or candidate.is_symlink():
            raise PhaseError(f"Missing/unsafe required repository file: {item}")
    if (root / ".github/workflows").exists():
        raise PhaseError("GitHub Actions workflows are not part of P0")
    schema = read_json(root / SCHEMA)
    example = read_json(root / EXAMPLE)
    validate_schema(schema, example)
    labels = read_json(root / ".github/labels.json")
    expected = {"type:feature", "type:fix", "type:refactor", "type:docs", "type:chore",
                "phase:0", "phase:1", "phase:2", "phase:3", "phase:4"}
    if set(labels) != expected or any(not isinstance(value, str) or not value for value in labels.values()):
        raise PhaseError("P0 label catalog does not match required labels")


def syntax_all(root: Path) -> None:
    for source in sorted((root / "src/sillage_dev").glob("*.py")):
        syntax_source(source.read_text(encoding="utf-8"), str(source.relative_to(root)))


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only Sillage source checks")
    parser.add_argument("check", choices=["structure", "syntax"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        if args.check == "structure":
            structure(args.root)
        else:
            syntax_all(args.root)
        print(f"PASSED: {args.check} (read only)")
        return 0
    except (PhaseError, UnicodeError, OSError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
