"""Normative cross-field checks not enforced by the JSON Schema."""

import re

from .common import PhaseError


def inspect_cross_fields(manifest: dict) -> None:
    phase = manifest["phase"]
    if not re.fullmatch(r"P0[1-4]", phase):
        raise PhaseError("Only P01, P02, P03, P04 are supported")
    phase_num = int(phase[1:])
    prefix = phase.lower()
    branch = manifest["git"]["work_branch"]
    branch_type, branch_name = branch.split("/", 1)
    if not branch_name.startswith(prefix + "-") or len(branch_name) <= len(prefix) + 1:
        raise PhaseError("Work branch does not start with the declared phase prefix")
    if manifest["documents"]["smart_target"] != f"docs/phase-{phase_num:02d}/SMART.md":
        raise PhaseError("SMART target path disagrees with the phase")
    steps = manifest["issues"]["steps"]
    if {s["step_id"] for s in steps} != {"E01", "E02"}:
        raise PhaseError("Exactly two distinct steps E01 and E02 are required")
    if len({s["title"].casefold() for s in steps}) != 2:
        raise PhaseError("Step issue titles must differ")
    expected_labels = {f"phase:{phase_num}", f"type:{branch_type}"}
    for item in (manifest["issues"]["parent"], *steps):
        labels = set(item["labels"])
        if labels != expected_labels:
            raise PhaseError("Each issue must have matching phase and branch-type labels")
    if manifest["checks"]["profile"] != "phase-start":
        raise PhaseError("Unsupported controls profile")
