"""Phase-start orchestration with fail-closed preflight and explicit human consent."""

from pathlib import Path

from .approvals import inspect_approvals
from .bundle import inspect_bundle
from .common import PhaseError
from .journal import exclusive_apply_lock, journal_path, read_existing, save
from .local_git import (commit_english_smart, create_phase_branch, git, inspect_repository,
                        verify_signature_configuration)
from .remote_github import (create_issue, inspect_gh_capabilities, inspect_github,
                            verify_issue)
from .signatures import verify_commit
from .validation import inspect_cross_fields


class PhaseStart:
    def __init__(self, *, root: Path, bundle: Path, french_smart: Path,
                 approval_record: Path, signer_file: Path, state_directory: Path):
        self.root = root.resolve()
        self.bundle = bundle
        self.french_smart = french_smart
        self.approval_record = approval_record
        self.signer_file = signer_file
        self.state_directory = state_directory
        self.manifest: dict = {}
        self.english: bytes = b""
        self.digest: str = ""
        self.journal: Path | None = None
        self.record: dict | None = None
        self.signer: str = ""

    def preflight(self, *, resume: bool = False) -> dict:
        schema_path = (Path(__file__).resolve().parents[2] / "design" / "fr" /
                       "specifications" / "schemas" / "development" / "v1" /
                       "phase-start.schema.json")
        self.manifest, self.english, self.digest = inspect_bundle(self.bundle, schema_path)
        inspect_cross_fields(self.manifest)
        for local_evidence in (self.approval_record, self.signer_file):
            external = local_evidence.expanduser().resolve()
            if external == self.root or self.root in external.parents:
                raise PhaseError("Owner approval/signing metadata must remain outside source Git")
        approval = inspect_approvals(self.english, self.french_smart,
                                     self.approval_record, self.manifest["phase"])
        self.journal = journal_path(self.root, self.state_directory, self.manifest)
        self.record = read_existing(self.journal, resume=resume, digest=self.digest,
                                    root=self.root)
        branch_created = bool(self.record and self.record.get("branch_created"))
        inspect_repository(self.root, self.manifest, allow_phase_branch=branch_created)
        self.signer = verify_signature_configuration(self.root, self.signer_file)
        gh_version = inspect_gh_capabilities()
        known = set()
        if self.record:
            if self.record.get("parent_issue"):
                known.add(self.record["parent_issue"])
            known.update(self.record.get("step_issues", {}).values())
        remote = inspect_github(self.manifest, recorded_issues=known)
        if self.record:
            self._verify_record()
        return {
            "phase": self.manifest["phase"],
            "repository": remote["repository"],
            "branch": self.manifest["git"]["work_branch"],
            "expected_develop_sha": remote["remote_develop"],
            "bundle_sha256": self.digest,
            "smart": approval,
            "installed_gh": gh_version,
            "issues_scanned": remote["existing_issues_scanned"],
            "reported_write_permission": remote["github_write_permission_reported"],
            "journal": str(self.journal),
            "resuming": resume,
            "remaining": self._remaining(),
            "signature_capability": "not proven by preflight; must verify the actual signed commit",
            "note": "Semantic approval record provenance must be checked by the owner.",
        }

    def _remaining(self) -> list[str]:
        record = self.record or {}
        todo = []
        if not record.get("parent_issue"):
            todo.append("create parent issue")
        for step in ("E01", "E02"):
            if step not in record.get("step_issues", {}):
                todo.append(f"create native {step} sub-issue")
        if not record.get("branch_created"):
            todo.append("create local work branch")
        if not record.get("smart_commit"):
            todo.append("write and personally sign SMART-only opening commit")
        return todo

    def _verify_record(self) -> None:
        assert self.record is not None
        repo = self.manifest["git"]["github_repository"]
        parent_number = self.record.get("parent_issue")
        steps = self.record.get("step_issues", {})
        if steps and not parent_number:
            raise PhaseError("Recovery record contains children without a parent")
        if parent_number:
            verify_issue(repo, parent_number, self.manifest["issues"]["parent"], self.manifest)
        for step, number in steps.items():
            if step not in ("E01", "E02"):
                raise PhaseError("Unknown step in recovery record")
            item = next(x for x in self.manifest["issues"]["steps"] if x["step_id"] == step)
            verify_issue(repo, number, item, self.manifest, parent_number=parent_number, step=step)
        if self.record.get("branch_created"):
            base = git(self.root, "merge-base", self.manifest["git"]["work_branch"], "develop")
            if base != self.manifest["git"]["expected_head"]:
                raise PhaseError("Resumed branch is not based on the approved develop commit")
        if self.record.get("smart_commit"):
            actual = git(self.root, "rev-parse", "HEAD")
            if actual != self.record["smart_commit"]:
                raise PhaseError("Resume HEAD differs from the recorded signed commit")
            verify_commit(actual, self.signer, self.root)
            target = self.manifest["documents"]["smart_target"]
            files = git(self.root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD^", "HEAD")
            if files.splitlines() != [target]:
                raise PhaseError("Recorded opening commit includes unexpected files")

    def apply(self) -> dict:
        """Only call after preflight and a separate interactive authorization."""
        if self.journal is None or not self.manifest:
            raise PhaseError("Read-only preflight must succeed before any operation")
        with exclusive_apply_lock(self.journal):
            updated = read_existing(self.journal, resume=self.record is not None,
                                    digest=self.digest, root=self.root)
            if updated != self.record:
                raise PhaseError("Recovery state changed after preflight; restart the plan")
            return self._apply_locked()

    def _apply_locked(self) -> dict:
        """Apply under a per-phase local advisory lock."""
        repo = self.manifest["git"]["github_repository"]
        record = self.record
        if record is None:
            record = {"repository_root": str(self.root), "bundle_sha256": self.digest,
                      "phase": self.manifest["phase"], "parent_issue": None,
                      "step_issues": {}, "branch_created": False, "smart_commit": None}
            save(self.journal, record, first=True)
        self.record = record
        # After every externally visible operation, keep the real confirmed ID.
        if not record["parent_issue"]:
            record["parent_issue"] = create_issue(repo, self.manifest["issues"]["parent"],
                                                  self.manifest)
            save(self.journal, record)
        for step in self.manifest["issues"]["steps"]:
            step_id = step["step_id"]
            if step_id not in record["step_issues"]:
                number = create_issue(repo, step, self.manifest,
                                      parent_number=record["parent_issue"], step=step_id)
                record["step_issues"][step_id] = number
                save(self.journal, record)
        # GitHub state can change between a plan and a side effect. Refuse if develop moves.
        if not record["branch_created"]:
            inspect_repository(self.root, self.manifest)
            current_develop = self.manifest["git"]["expected_head"]
            from .remote_github import gh_json
            latest = gh_json("api", f"repos/{repo}/branches/develop")
            if latest["commit"]["sha"] != current_develop:
                raise PhaseError("Remote develop moved before local branch creation")
            create_phase_branch(self.root, self.manifest["git"]["work_branch"])
            record["branch_created"] = True
            save(self.journal, record)
        if not record["smart_commit"]:
            inspect_repository(self.root, self.manifest, allow_phase_branch=True)
            new_head = commit_english_smart(
                self.root, self.manifest["documents"]["smart_target"], self.english,
                self.manifest["phase"], self.manifest["git"]["work_branch"],
                record["parent_issue"], self.signer,
            )
            record["smart_commit"] = new_head
            save(self.journal, record)
        return {"parent_issue": record["parent_issue"], "step_issues": record["step_issues"],
                "local_branch": self.manifest["git"]["work_branch"],
                "signed_smart_commit": record["smart_commit"],
                "pushed": False, "pull_request_created": False,
                "journal": str(self.journal)}
