# Contributing to the Sillage source repository

- Source code, identifiers, comments, repository technical documentation, commit messages, issues, PRs and tags are in **English**. French roadmap, IA mandates and normative specifications remain under `design/fr/`.
- Python modules use `snake_case`; classes use `PascalCase`; constants use `UPPER_SNAKE_CASE`. Documentation resources use meaningful file names; work branches use `type/pXX-topic` with `feature`, **never** `feat`.
- P01–P04 consist of exactly two stages, E01 and E02. The opening signed commit contains only `docs/phase-XX/SMART.md`; the two principal stage commits and signed stage tags follow, then the final signed commit contains only `docs/phase-XX/SUMMARY.md`.
- A single phase PR is created **after** the SUMMARY commit, targeting `develop`. Do not merge via GitHub buttons. The owner performs a **locally signed `--no-ff` merge**, checks the signer fingerprint and both parents, and pushes after separate authorization.
- Before any phase opening, a French SMART and a semantically equivalent English SMART must each be approved. A checksum or mechanical AC-ID comparison is necessary but not sufficient.
- Only structure, static analysis, syntax, read-only formatting, and applicable compilation checks may run automatically. **Never introduce or run automatic unit tests, including transitively.** A unit test requires independent approvals for creation and manual execution; no E2E suite.
- Do not add CI, watchers, daemons, product installers, extra operating-system targets, or unsupported build/format targets during P0.
- No local credentials, signing keys, owner approval receipts, or recovery journals may be committed. GitHub read-only integrations are distinct from local owner Git/`gh` privileges.

## Commit format

```text
feature (p02-package-install) : Validate incremental bundles

Explain the intended result.

- List substantive changes in English.

Refs: #42
Phase: P02
Step: E02
```

P0 bootstrap commits can use `chore (bootstrap) : ...` with a `Phase: P0` footer. A locally signed merge uses an authorized type and descriptive context; it does not imitate a GitHub-generated merge.
