# Local phase-start preparer

## Inputs

`phase-XX-start.zip` contains **exactly** `manifest.json` and `SMART.en.md`, following `design/fr/specifications/schemas/development/v1/phase-start.schema.json`. The external, approved French `SMART.fr.md`, the external owner approval receipt, and the owner-approved **public signer fingerprint** are not ZIP entries.

Receipt format, created and approved by the owner (not generated from an untrusted bundle):

```json
{
  "phase": "P02",
  "smart_fr_sha256": "sha256:<64 lowercase hexadecimal characters>",
  "smart_en_sha256": "sha256:<64 lowercase hexadecimal characters>",
  "smart_fr_approved": true,
  "semantic_equivalence_approved": true,
  "decision_reference": "<owner-approved decision reference>",
  "approved_by": "<owner identifier>"
}
```

Replace placeholders only with verified values. This JSON is **evidence entered by the owner**, not a digitally verified approval. Semantic equivalence of the actual texts must be reviewed and explicitly approved by the owner. Store the receipt outside Git and outside the ZIP.

## Fixed entry points

All commands below are **examples for the owner to inspect and run** on the selected host, after authorizations; they have not been executed on the owner's system.

```sh
PYTHONPATH=src python3 -m sillage_dev.phase_cli inspect --bundle /path/to/phase.zip

PYTHONPATH=src python3 -m sillage_dev.phase_cli plan \
  --bundle /path/to/phase.zip \
  --french-smart /path/to/SMART.fr.md \
  --approval-record /path/to/approval.json

PYTHONPATH=src python3 -m sillage_dev.phase_cli apply \
  --bundle /path/to/phase.zip \
  --french-smart /path/to/SMART.fr.md \
  --approval-record /path/to/approval.json \
  --authorize-effects
```

`plan` is read-only with respect to Git and GitHub. `apply` has no noninteractive approval option: it requires an interactive console and an exact typed statement including the phase, repository and expected SHA. It does **not** push commits or create a PR. The user may choose a separate `--signer-file` and `--state-dir`, both outside Git, for trusted local configuration. Use `--resume` only after inspecting the recovery journal and the remote results.

## Preflight

The preparer rejects invalid ZIP members, collisions, links, size limits, invalid JSON or schema, incorrect hash, cross-field contradictions and duplicate steps. It requires the same AC IDs in both SMART files and the explicit owner receipt, then checks local Git root, clean worktree/index, current branch, expected local/develop SHA, configured personal signer, GitHub remote identity, remote `develop`, missing work branch, issue collisions, existing labels and CLI capabilities. The semantic meaning of SMART documents cannot be checked automatically; the receipt captures the separate human approval.

The `gh` checks require **v2.94.0+** and native `--parent`, `parent`/`subIssues` JSON and issue closing support. Before the actual initial action, `gh api` checks repository identity and reported account write capabilities. Reported permissions alone do **not** prove actual creation/closure permission. Issues are created only by the owner's authorized local `gh` session; each actual child is checked against both its `parent` field and the parent's `subIssues` list. GitHub issue numbers are not guessed or generated from the manifest.

## Recovery

An authorized `apply` writes a state journal to `~/.local/state/sillage/phase-start/` with mode 0600. It records phase, repository location, bundle hash, real issue IDs, branch creation and the verified signed SMART commit. Partial writes may remain after a failure; do not delete them as a normal retry. Check issue markers and journal before using `--resume`. If a command succeeded but confirmation or journaling failed, stop for manual reconciliation. Never create a replacement issue or change the manifest solely to avoid a collision.

## Completion boundary

P0 acceptance **does not** require opening P1. The approved P0 AC09 requires rejection demonstrations **and** sufficient positive-path evidence when separately authorized, which may use an isolated setup. A successful offline rejection, or a hypothetical positive path, is not a `passed` result. P1 can start only after independent P0 validation, the owner's P0 acceptance, SMART FR/EN approval and separate Git/GitHub authorization.
