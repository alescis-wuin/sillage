# Owner-controlled P0 bootstrap checklist

**No command on this page has been executed against the owner's repository.** This checklist does not authorize Git/GitHub mutations; obtain a distinct explicit decision for each applicable category (repository, branches, labels, protections, hook installation, commits, tags and pushes). Substitute actual approved repository and signing identity before use.

## 1. Select the host and verify prerequisites

- Record the operating system and terminal of the **owner's** chosen host, the source language (the delivered candidate uses Python), Git version, `gh --version`, `make --version`, Python version and installed `jsonschema` version.
- Confirm the full GitHub source repository name and intended visibility. Distinguish it from future user-project mirrors and diagnostic repositories.
- Confirm local Git identity and owner-approved **public fingerprint**; keep signing key material, auth secrets and approval receipts outside source control.
- Independently review every Python dependency before the owner installs it. Do not run installer commands from an archive.

## 2. Initialize source Git and authorized branches

These are command **patterns**, not an instruction to run automatically. On a newly approved empty destination the owner may create `main` from the supplied source files, make a personally signed bootstrap commit, then create `develop` and configure `origin`. The owner must record actual results, including commit object, key fingerprint and both branch SHAs. Do not guess them.

```sh
git init -b main
git add -- README.md Makefile .gitignore .github .githooks design docs src templates requirements.txt
git commit -S -m "chore (bootstrap) : Establish P0 source repository" -m "Set up the approved source development baseline." -m "- Add documentation, contracts, hooks and phase-start tooling." -m "Phase: P0"
git branch develop
git remote add origin https://github.com/OWNER/REPOSITORY.git
```

Pushes and remote GitHub creation require **separate owner authorization**. They are deliberately omitted from this command block. Inspect `git status`, the recorded signatures and the exact remote URLs before any push.

## 3. Owner-managed labels, hooks and protections

- Create the labels listed in `.github/labels.json` manually on the approved GitHub repository. Verify with `gh label list -R OWNER/REPOSITORY`. Source catalog presence does not prove remote creation.
- On the real repository, after explicit permission, run `make hooks-install` to set the local `core.hooksPath` and verify `git config --local --get core.hooksPath` returns `.githooks`. The executable bits on `pre-commit`, `commit-msg` and `pre-push` must be preserved.
- Configure both `main` and `develop` against force-pushes and deletions, require verified signatures if the plan supports it, and restrict writers to the intended identity. Avoid required linear history and rules that prevent an owner-signed `--no-ff` local merge. A mandatory PR rule can conflict with the required local merge push. Verify actual rule behavior; if incompatible, **block** rather than use an unsigned or GitHub-generated merge.
- Record the complete effective branch protection/ruleset settings and owner-verified push behavior, or explicitly record the missing capability. A YAML/JSON file cannot activate server protections.

## 4. Verify signing under the owner's identity

The owner may create an **isolated temporary Git repository** (only after approving local Git mutations) with a personally signed commit, annotated signed tag, divergent signed commit and `--no-ff -S` merge. Verify the exact fingerprints of **all three object types**, plus the two merge parents. Do not treat GitHub's `Verified` badge as sufficient. Do not run signing demonstrations in an unapproved production branch.

Read-only inspection commands on already-created objects include:

```sh
git verify-commit <EXACT_COMMIT_SHA>
git show --no-patch --format='%H %G? %GF %GS' <EXACT_COMMIT_SHA>
git verify-tag <SIGNED_TAG_NAME>
git verify-tag --format='%(signature:grade) %(signature:fingerprint)' <SIGNED_TAG_NAME>
git rev-list --parents -n 1 <EXACT_MERGE_SHA>
```

Check that `git show` and `git verify-tag` report the identity **actually approved**, compare the fingerprint with the external fingerprint file, and confirm the merge has exactly two distinct parents and a valid personal signature. A signature valid for a different identity is a failure.

## 5. GitHub CLI sub-issue capability and permissions

Verify at the actual host: `gh issue create --help` includes `--parent`; `gh issue view --help` provides JSON fields `parent` and `subIssues`; `gh issue close --help` includes explicit close behavior. CLI release 2.94.0 introduced these features (see [GitHub announcement](https://github.blog/changelog/2026-06-10-manage-sub-issues-types-and-dependencies-from-github-cli/)). Confirm the local authenticated repository access and independently authorized native issue create, read, parent attachment, issue ID recovery and explicit close. A read-only CLI capability check is **not** sufficient to establish write permissions.

Do not create P1 merely to prove that the command exists. A separately authorized isolated demonstration, if required, must have a clear target, finite real effects and verifiable cleanup procedure. The IA does not perform these operations.

## 6. Evidence before independent P0 validation

Record real SHA values for `main` and `develop`, actual GitHub URL, CLI version outputs, authenticated capabilities, signing objects and fingerprints, GitHub protection configuration, label names, actual Make output/exit codes, verified hooks demonstrations, and phase-start rejection and positive-path evidence. Submit these to the independent validator with the French AC01–AC10 matrix. P0 is not accepted, and P1 must not start, simply because these instructions or files are present.
