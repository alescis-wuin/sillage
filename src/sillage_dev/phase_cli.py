"""Owner-facing phase-start CLI. Inspect and plan do not mutate Git or GitHub."""

import argparse
import json
from pathlib import Path
import sys

from .bundle import inspect_bundle
from .common import PhaseError
from .validation import inspect_cross_fields
from .workflow import PhaseStart


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare a Sillage phase P01-P04")
    sub = parser.add_subparsers(dest="action", required=True)
    for action in ("inspect", "plan", "apply"):
        part = sub.add_parser(action)
        part.add_argument("--bundle", type=Path, required=True)
        if action != "inspect":
            part.add_argument("--french-smart", type=Path, required=True)
            part.add_argument("--approval-record", type=Path, required=True)
            part.add_argument("--signer-file", type=Path,
                              default=Path.home() / ".config/sillage/signing-fingerprint")
            part.add_argument("--state-dir", type=Path,
                              default=Path.home() / ".local/state/sillage/phase-start")
            part.add_argument("--repo-root", type=Path, default=Path.cwd())
            part.add_argument("--resume", action="store_true")
        if action == "apply":
            part.add_argument("--authorize-effects", action="store_true", required=False,
                              help="Confirm a separate authorization for Git/GitHub side effects")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.action == "inspect":
            schema = (Path(__file__).resolve().parents[2] / "design/fr/specifications/schemas/development/v1/phase-start.schema.json")
            manifest, _, digest = inspect_bundle(args.bundle, schema)
            inspect_cross_fields(manifest)
            print(json.dumps({"phase": manifest["phase"], "bundle_sha256": digest,
                              "result": "offline structure and cross-fields valid",
                              "git_github_checked": False}, indent=2))
            return 0
        worker = PhaseStart(root=args.repo_root, bundle=args.bundle,
                            french_smart=args.french_smart, approval_record=args.approval_record,
                            signer_file=args.signer_file, state_directory=args.state_dir)
        plan = worker.preflight(resume=args.resume)
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        if args.action == "plan":
            return 0
        if not args.authorize_effects:
            raise PhaseError("Separate --authorize-effects is required (not supplied by ZIP)")
        if not sys.stdin.isatty():
            raise PhaseError("Apply requires an interactive owner terminal")
        expected = f"OPEN {plan['phase']} {plan['repository']} {plan['expected_develop_sha']}"
        print("This action creates remote GitHub issues, a local branch, and a signed commit.")
        print("No push or PR is performed. Approval of SMART contents is independent.")
        print(f"Type exactly: {expected}")
        if input("Authorization: ") != expected:
            raise PhaseError("Human authorization not confirmed")
        print(json.dumps(worker.apply(), indent=2))
        return 0
    except PhaseError as exc:
        print(f"BLOCKED: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
