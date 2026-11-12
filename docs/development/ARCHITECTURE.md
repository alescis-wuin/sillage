# P0 source tooling architecture

## Modules

- `src/sillage_dev/bundle.py` verifies ZIP membership, entry type and size, UTF-8 JSON, schema version and the exact `SMART.en.md` digest. It does not extract files or run scripts.
- `validation.py` enforces cross-field invariants absent from the normative JSON Schema: P01–P04 only, branch prefix, exact SMART target, matching `type:*` and `phase:*` labels, and E01/E02.
- `approvals.py` checks the French/English AC IDs and checks an **owner-provided external** record carrying both SHA-256 digests and two explicit approval decisions. Matching IDs cannot certify semantic equivalence.
- `local_git.py`, `remote_github.py` and `signatures.py` read Git/GitHub state and contain the narrowly scoped owner-only operations. No remote push or issue closing is part of phase start.
- `workflow.py`, `journal.py` and `phase_cli.py` coordinate preflight, interactive consent, immutable reference checks and recovery.
- `hooks.py` and `repo_check.py` implement focused checks. Make and the hooks reuse the same Python syntax and JSON Schema routines.

The code uses no imported GitHub token and does not ask for access to a private key. `gh` inherits the local credentials **only in the owner's execution environment**. No untrusted ZIP member is a command, path for arbitrary writes, authorization token, or signing-key selector.

## Operations and failure handling

The default `inspect` path requires only the ZIP and the bundled schema. `plan` adds external SMART approval checks and live read-only Git/GitHub checks. `apply` repeats preflight, displays remaining steps and requires an explicit flag plus typed approval in an interactive owner terminal. It creates a recovery journal outside the Git worktree, then the parent issue, two native sub-issues, the local branch, and the personal signed `SMART.md`-only opening commit, in that order.

A Linux advisory file lock prevents concurrent `apply`/`resume` instances; other operating systems are outside the proposed pilot configuration. After each confirmed issue creation the journal records its actual number. If an API call creates an issue but its acknowledgement cannot be recovered, the phase marker/title collision scan blocks a duplicate retry. Resume requires `--resume` and re-verifies existing issues and signing references. If a local branch or commit is created but its journal update fails, manual reconciliation is required; silent recreation is forbidden.

This sequence is **not an atomic transaction** across GitHub, the worktree and the local journal. An interactive approval is an operational guard, not a cryptographic proof that its user is the owner. GitHub side-effect permissions and branch protections are finally demonstrated only on the owner's actual configuration.

## Design boundary

French specifications reside under `design/fr/`; English technical docs and Git metadata remain English. The copied specification README references several product-v1 schemas and examples that were **not provided** with the P0 sources. These missing product artefacts are deferred, not fabricated or claimed implemented. The development `phase-start` schema and its sample **were** provided unchanged.
