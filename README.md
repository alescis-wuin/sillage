# Sillage source repository — P0 bootstrap

This directory is a **proposed source tree**, not a Git repository or proof of a published branch. The owner must approve local and remote Git operations before creating the real repository.

## Scope

P0 provides a versioned Git hook setup, a minimal Makefile, GitHub issue/PR templates, a retained French design reference, and a local declarative **development phase** preparer. It does not implement the Sillage product, its user-project mirror, package installer, preflight sandbox, or publication workflow.

## Requirements

- One owner-selected host with Python 3.11+, Git, GNU Make, and GitHub CLI **2.94.0+**.
- Python package `jsonschema` 4.18 or later, below 5 (`requirements.txt`) to enforce JSON Schema Draft 2020-12. Installing dependencies is an explicit owner action.
- An existing authorized owner signing identity. The authorized **public fingerprint only** is stored outside this repository at `~/.config/sillage/signing-fingerprint`. Do not include signing keys or credentials in this source tree.
- `gh` authenticated by the owner with rights to read the source repository, create/list issues and use native sub-issues. The AI has no need for these write rights.

These requirements describe a **proposed Python implementation**. The owner host, tool versions, key, credentials, repository, branch protections and GitHub plan have not been verified.

## Read-only controls

```sh
make help
make check
make syntax
```

`make check` validates P0 file structure and the provided `phase-start` JSON Schema and example; `make syntax` parses Python sources without executing tests or creating bytecode. No test command, CI workflow, or test runner is included.

## Owner-only operations

`make hooks-install` changes the **local Git configuration** to use `.githooks/`. Run it only after approval. The hooks contain no unit-test or E2E invocation.

`make phase-start BUNDLE=/path/to/phase-start.zip FRENCH_SMART=/path/to/SMART.fr.md APPROVAL_RECORD=/path/to/approval.json` invokes a read-only phase-start plan. It rejects missing evidence before any mutation. The approval receipt belongs to the owner and stays outside the ZIP and source control.

A separate interactive `python3 -m sillage_dev.phase_cli apply ... --authorize-effects` command (with `PYTHONPATH=src`) is needed for mutations, and must be run **by the owner only**, after all P0 and phase-specific approvals. It is deliberately **not** an automatic Make target.

Details: [Bootstrap](docs/development/BOOTSTRAP.md), [phase start](docs/development/PHASE_START.md), [Git and signatures](docs/development/GIT_AND_SIGNATURES.md), and [contributing](docs/development/CONTRIBUTING.md).

## Documentation

- [French roadmap](design/fr/ROADMAP.md) — phase scope and milestones.
- [French technical specifications](design/fr/specifications/README.md) — normative source copies; note that product JSON schemas beyond phase-start have not been provided in P0.
- [Source architecture](docs/development/ARCHITECTURE.md) — P0 module boundaries and trust model.
- [GitHub labels catalog](.github/labels.json), [phase issue](.github/ISSUE_TEMPLATE/phase.md), [step issue](.github/ISSUE_TEMPLATE/step.md), [PR template](.github/PULL_REQUEST_TEMPLATE.md).
- [Phase templates](templates/phase/) — SMART FR/EN, PROMPT FR, SUMMARY EN, HANDOFF FR.

## Explicit limitations

The phase preparer is **not a secure sandbox**. It never runs code from the ZIP and uses fixed Git/`gh` commands, but owner-supplied Git hooks, signing helpers and local Git configuration may execute external processes after explicit authorization. The read-only plan does not prove write permissions, the authenticity of a human approval receipt, actual signing capability, or compatibility of remote protected-branch rules. Those require owner-controlled checks and independent validation.
