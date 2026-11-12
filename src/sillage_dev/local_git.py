"""Read-only Git preflight and narrowly scoped owner-authorized local operations."""

from pathlib import Path
import re

from .common import PhaseError, command


def git(root: Path, *args: str, input_text: str | None = None) -> str:
    return command(["git", *args], cwd=root, input_text=input_text)


def inspect_repository(root: Path, manifest: dict, *, allow_phase_branch: bool = False) -> None:
    if git(root, "rev-parse", "--is-inside-work-tree") != "true":
        raise PhaseError("Target is not a Git worktree")
    if Path(git(root, "rev-parse", "--show-toplevel")).resolve() != root.resolve():
        raise PhaseError("Run the phase preparer at the repository root")
    current = git(root, "symbolic-ref", "--quiet", "--short", "HEAD")
    desired = manifest["git"]["work_branch"]
    if current != (desired if allow_phase_branch else "develop"):
        raise PhaseError("Unexpected current branch (expected develop or recorded resumed branch)")
    if git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise PhaseError("Git index or worktree contains changes")
    head = git(root, "rev-parse", "HEAD")
    if allow_phase_branch:
        base = git(root, "rev-parse", "develop")
        if base != manifest["git"]["expected_head"]:
            raise PhaseError("Local develop base does not match the manifest")
    elif head != manifest["git"]["expected_head"]:
        raise PhaseError("Local HEAD differs from the manifest's expected_head")
    remote = git(root, "remote", "get-url", "origin")
    full_name = manifest["git"]["github_repository"]
    acceptable = (
        f"https://github.com/{full_name}",
        f"git@github.com:{full_name}",
        f"ssh://git@github.com/{full_name}",
    )
    if remote.removesuffix(".git").lower() not in [x.lower() for x in acceptable]:
        raise PhaseError("Git origin does not match the declared GitHub repository")
    if not allow_phase_branch:
        refs = git(root, "branch", "--list", desired)
        if refs:
            raise PhaseError("Local work branch already exists")


def verify_signature_configuration(root: Path, fingerprint_file: Path) -> str:
    from .signatures import expected_signer
    fingerprint = expected_signer(fingerprint_file)
    name = git(root, "config", "--get", "user.name")
    email = git(root, "config", "--get", "user.email")
    signing_key = git(root, "config", "--get", "user.signingkey")
    if not name or not email or not signing_key:
        raise PhaseError("Git user/signing identity is not configured")
    # git config is only a prerequisite, not proof of signing capability.
    return fingerprint


def create_phase_branch(root: Path, branch: str) -> None:
    git(root, "switch", "-c", branch)


def commit_english_smart(root: Path, target: str, english: bytes, phase: str,
                         branch: str, parent_issue: int, signer: str) -> str:
    from .signatures import verify_commit
    destination = root / target
    if destination.exists() or destination.is_symlink():
        raise PhaseError("SMART target already exists")
    # Reject a symlink at any component, not only the final directory.
    current = root
    for part in Path(target).parts:
        current = current / part
        if current.is_symlink():
            raise PhaseError("SMART destination crosses a symbolic link")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(english)
    git(root, "add", "--", target)
    staged = git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMRD")
    if staged.splitlines() != [target]:
        raise PhaseError("Unexpected staged paths; commit refused")
    branch_type, branch_name = branch.split("/", 1)
    message = (f"{branch_type} ({branch_name}) : Add approved phase SMART\n\n"
               f"Record the approved English brief for {phase}.\n\n"
               f"- Preserve the agreed acceptance criteria and scope.\n\n"
               f"Refs: #{parent_issue}\nPhase: {phase}\n")
    git(root, "commit", "-S", "-F", "-", input_text=message)
    new_head = git(root, "rev-parse", "HEAD")
    changed = git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD^", "HEAD")
    if changed.splitlines() != [target]:
        raise PhaseError("Commit contains files beyond the approved English SMART")
    verify_commit(new_head, signer, root)
    return new_head
