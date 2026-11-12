"""Fast Git hooks using the same read-only validators as the Makefile."""

import argparse
from pathlib import Path
import re
import sys

from .common import PhaseError
from .local_git import git
from .repo_check import syntax_source, validate_schema
from .signatures import expected_signer, verify_annotated_tag, verify_commit
from .common import load_json_bytes

BRANCH = re.compile(r"^(feature|fix|refactor|docs|chore)/p0[1-4]-[a-z0-9]+(?:-[a-z0-9]+)*$")
HEADER = re.compile(r"^(feature|fix|refactor|docs|chore) \(([a-z0-9]+(?:-[a-z0-9]+)*)\) : ([A-Z][^\r\n]{2,72})$")
OID = re.compile(r"^[0-9a-f]{40}$")


def pre_commit(root: Path) -> None:
    branch = git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch not in ("main", "develop") and not BRANCH.fullmatch(branch):
        raise PhaseError("Invalid work branch name (feature/...; P01-P04 required)")
    names = git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    for filename in filter(None, names.split("\0")):
        if filename.startswith(".github/workflows/"):
            raise PhaseError("GitHub Actions are outside the P0 scope")
        if filename.endswith((".pyc", ".pyo")) or "__pycache__" in filename.split("/"):
            raise PhaseError("Compiled Python artifacts must not be committed")
        if filename.endswith(".py"):
            syntax_source(git(root, "show", ":" + filename), filename)
        if filename.endswith(".json"):
            value = load_json_bytes(git(root, "show", ":" + filename).encode("utf-8"))
            schema_path = "design/fr/specifications/schemas/development/v1/phase-start.schema.json"
            example_path = "design/fr/specifications/examples/development/v1/phase-start.json"
            if filename in (schema_path, example_path):
                schema = value if filename == schema_path else load_json_bytes(
                    git(root, "show", ":" + schema_path).encode("utf-8")
                )
                example = value if filename == example_path else load_json_bytes(
                    git(root, "show", ":" + example_path).encode("utf-8")
                )
                validate_schema(schema, example)


def commit_message(root: Path, message_file: Path) -> None:
    text = message_file.read_text(encoding="utf-8").strip()
    lines = text.splitlines()
    if len(lines) < 5 or lines[1] != "" or not lines[2].strip():
        raise PhaseError("Commit must contain a header, descriptive body and references")
    header = HEADER.fullmatch(lines[0])
    if not header:
        raise PhaseError("Commit header must match type (name) : Imperative title")
    kind, name, _ = header.groups()
    branch = git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch not in ("main", "develop"):
        if branch != f"{kind}/{name}":
            raise PhaseError("Commit header does not match the actual work branch")
        match = re.match(r"^p0([1-4])-", name)
        if match is None:
            raise PhaseError("Work branch does not carry a P01-P04 prefix")
        phase = "P0" + match.group(1)
        if f"Phase: {phase}" not in lines:
            raise PhaseError("Commit is missing the exact Phase footer")
        if not any(re.fullmatch(r"Refs: #[1-9][0-9]*(?:, #[1-9][0-9]*)*", x) for x in lines):
            raise PhaseError("Commit is missing valid issue reference numbers")
    elif "Phase: P0" not in lines and not any(re.fullmatch(r"Phase: P0[1-4]", x) for x in lines):
        raise PhaseError("Bootstrap or merge commit must identify its phase")


def _ref_type(ref: str) -> str:
    if ref in ("refs/heads/main", "refs/heads/develop"):
        return "head"
    if ref.startswith("refs/heads/") and BRANCH.fullmatch(ref.removeprefix("refs/heads/")):
        return "head"
    if re.fullmatch(r"refs/tags/step/p0[1-4]-e0[12]", ref):
        return "tag"
    if re.fullmatch(r"refs/tags/v[0-9]+\.[0-9]+\.[0-9]+", ref):
        return "tag"
    raise PhaseError(f"Disallowed ref name: {ref}")


def pre_push(root: Path, lines: str) -> None:
    path = Path.home() / ".config/sillage/signing-fingerprint"
    fingerprint = expected_signer(path)
    for line in lines.splitlines():
        parts = line.split()
        if len(parts) != 4:
            raise PhaseError("Malformed pre-push reference")
        local_ref, local_oid, remote_ref, remote_oid = parts
        if not OID.fullmatch(local_oid) or not OID.fullmatch(remote_oid):
            raise PhaseError("Git SHA-1 ref identities are required")
        if remote_ref != local_ref:
            raise PhaseError("Pushing to another reference name is not allowed")
        kind = _ref_type(remote_ref)
        if local_oid == "0" * 40:
            raise PhaseError("Reference deletion is not allowed")
        if remote_oid != "0" * 40:
            if kind == "tag":
                raise PhaseError("Replacing existing tags is prohibited")
            git(root, "merge-base", "--is-ancestor", remote_oid, local_oid)
        if kind == "tag":
            verify_annotated_tag(local_ref, fingerprint, root)
            tip = git(root, "rev-parse", local_ref + "^{commit}")
        else:
            tip = local_oid
        if remote_oid != "0" * 40 and kind == "head":
            commits = git(root, "rev-list", remote_oid + ".." + tip)
        else:
            commits = git(root, "rev-list", tip, "--not", "--remotes")
        # Recheck the tag's target even if it is already reachable remotely.
        to_verify = set(commits.splitlines())
        if kind == "tag":
            to_verify.add(tip)
        for sha in sorted(to_verify):
            verify_commit(sha, fingerprint, root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sillage versioned Git hooks")
    parser.add_argument("kind", choices=["pre-commit", "commit-msg", "pre-push"])
    parser.add_argument("message_file", nargs="?", type=Path)
    args = parser.parse_args(argv)
    root = Path.cwd()
    try:
        if args.kind == "pre-commit":
            pre_commit(root)
        elif args.kind == "commit-msg":
            if args.message_file is None:
                raise PhaseError("Git commit-msg hook needs the message path")
            commit_message(root, args.message_file)
        else:
            pre_push(root, sys.stdin.read())
        return 0
    except (PhaseError, OSError, UnicodeError) as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
