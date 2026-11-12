"""GitHub CLI read-only preflight and gated native issue creation."""

import json
import re
from pathlib import Path

from .common import PhaseError, command


def gh(*args: str) -> str:
    return command(["gh", *args])


def gh_json(*args: str) -> object:
    try:
        return json.loads(gh(*args))
    except (ValueError, TypeError) as exc:
        raise PhaseError("GitHub CLI did not return valid JSON") from exc


def inspect_gh_capabilities() -> str:
    version = gh("--version").splitlines()[0]
    match = re.search(r"gh version (\d+)\.(\d+)\.(\d+)", version)
    if not match or tuple(map(int, match.groups())) < (2, 94, 0):
        raise PhaseError("GitHub CLI 2.94.0+ is required for native sub-issues")
    for subcommand, expected in [
        (("issue", "create", "--help"), "--parent"),
        (("issue", "view", "--help"), "--json"),
        (("issue", "close", "--help"), "--reason"),
    ]:
        if expected not in gh(*subcommand):
            raise PhaseError("Installed gh lacks a required native issue capability")
    return version


def _marker(manifest: dict, step: str | None = None) -> str:
    text = f"Sillage-Phase: {manifest['phase']}"
    return text + (f"\nSillage-Step: {step}" if step else "")


def _all_issues(repo: str) -> list[dict]:
    issues = gh_json("issue", "list", "-R", repo, "--state", "all", "--limit", "1000",
                     "--json", "number,title,body,state")
    if not isinstance(issues, list) or len(issues) >= 1000:
        raise PhaseError("Cannot establish an exhaustive issue collision scan")
    return issues


def inspect_github(manifest: dict, *, recorded_issues: set[int] | None = None) -> dict:
    repo = manifest["git"]["github_repository"]
    actual = gh_json("api", f"repos/{repo}")
    if not isinstance(actual, dict) or actual.get("full_name", "").casefold() != repo.casefold():
        raise PhaseError("GitHub repository identity mismatch")
    if actual.get("archived") or actual.get("disabled") or not actual.get("has_issues"):
        raise PhaseError("Repository is archived, disabled, or has issues disabled")
    permissions = actual.get("permissions") or {}
    if not (permissions.get("push") or permissions.get("maintain") or permissions.get("admin")):
        raise PhaseError("Authenticated account has no reported write permission")
    branch = gh_json("api", f"repos/{repo}/branches/develop")
    try:
        remote_head = branch["commit"]["sha"]
    except (TypeError, KeyError) as exc:
        raise PhaseError("GitHub develop SHA unavailable") from exc
    if remote_head != manifest["git"]["expected_head"]:
        raise PhaseError("Remote develop differs from manifest expected_head")
    remote_branches = gh(
        "api", "--method", "GET", f"repos/{repo}/branches", "-F", "per_page=100",
        "--paginate", "--jq", ".[ ].name".replace(" ", ""),
    ).splitlines()
    if manifest["git"]["work_branch"] in remote_branches:
        raise PhaseError("Work branch already exists remotely")
    found = _all_issues(repo)
    known = recorded_issues or set()
    expected_titles = {manifest["issues"]["parent"]["title"].casefold()}
    expected_titles.update(item["title"].casefold() for item in manifest["issues"]["steps"])
    phase_mark = _marker(manifest)
    for issue in found:
        if issue["number"] in known:
            continue
        title = (issue.get("title") or "").casefold()
        body = issue.get("body") or ""
        if title in expected_titles or phase_mark in body or re.search(
            rf"\b(?:P0?{int(manifest['phase'][1:])}|Phase\s+0?{int(manifest['phase'][1:])})\b",
            title, re.IGNORECASE,
        ):
            raise PhaseError(f"Existing issue #{issue['number']} conflicts with the phase")
    labels = gh_json("label", "list", "-R", repo, "--limit", "100", "--json", "name")
    label_names = {x["name"] for x in labels}
    for expected in manifest["issues"]["parent"]["labels"]:
        if expected not in label_names:
            raise PhaseError(f"Required GitHub label is missing: {expected}")
    return {"repository": actual["full_name"], "remote_develop": remote_head,
            "existing_issues_scanned": len(found), "github_write_permission_reported": True}


def get_issue(repo: str, number: int) -> dict:
    value = gh_json("issue", "view", str(number), "-R", repo,
                    "--json", "number,title,body,labels,parent,state")
    if not isinstance(value, dict) or value.get("number") != number:
        raise PhaseError("New issue could not be confirmed by GitHub")
    return value


def verify_issue(repo: str, number: int, item: dict, manifest: dict,
                 *, parent_number: int | None = None, step: str | None = None) -> None:
    value = get_issue(repo, number)
    if (value.get("title") != item["title"] or
            _marker(manifest, step) not in (value.get("body") or "") or
            {x["name"] for x in value.get("labels", [])} != set(item["labels"])):
        raise PhaseError("Created issue does not match its approved manifest")
    if parent_number is not None:
        parent = value.get("parent")
        if not isinstance(parent, dict) or parent.get("number") != parent_number:
            raise PhaseError("GitHub native parent relationship is unconfirmed")
        # Independent confirmation from the parent side, not a Markdown link.
        response = gh_json("issue", "view", str(parent_number), "-R", repo,
                           "--json", "subIssues")
        sub_issues = response.get("subIssues") or {}
        nodes = sub_issues.get("nodes") or []
        if not any(x.get("number") == number for x in nodes):
            raise PhaseError("Native child link missing from the parent issue")


def create_issue(repo: str, item: dict, manifest: dict,
                 *, parent_number: int | None = None, step: str | None = None) -> int:
    body = item["body"].rstrip() + "\n\n" + _marker(manifest, step) + "\n"
    args = ["issue", "create", "-R", repo, "--title", item["title"], "--body", body]
    for label in item["labels"]:
        args.extend(["--label", label])
    if parent_number is not None:
        args.extend(["--parent", str(parent_number)])
    output = gh(*args)
    matched = re.fullmatch(r"https://github\.com/([^/]+/[^/]+)/issues/(\d+)", output.strip())
    if not matched or matched.group(1).casefold() != repo.casefold():
        raise PhaseError("Cannot recover a unique issue ID from gh; reconcile manually")
    number = int(matched.group(2))
    verify_issue(repo, number, item, manifest, parent_number=parent_number, step=step)
    return number
