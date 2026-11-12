# Git, signing and verification boundaries

## Branch and commit conventions

Permanent branches are `main` and `develop`. Work branch examples: `feature/p01-private-context`, `fix/p02-package-validation`; never `feat/` or a third permanent testing branch. Use English ASCII and exactly the documented header `type (branch_name) : Imperative title`. Reference a real phase and issue in the commit footer; P0 bootstrap is the documented exception.

P01–P04 use one branch and one PR each. Both principal step commits and `step/pXX-eYY` annotated tags are personally signed. The first approved SMART commit and last SUMMARY commit each contain only the specified single file; the PR is opened after SUMMARY. Integration occurs through a locally signed **non-fast-forward** merge, never a GitHub merge/squash/rebase button. Issues are explicitly closed only after GitHub confirms the actual merge.

## Hooks and limitations

- `pre-commit`: verify branch name and only changed Python/JSON syntax/schema. No checkout or autoformat.
- `commit-msg`: enforce header, body and phase/reference trailers, with a P0/merge context exception.
- `pre-push`: refuse deletion and non-fast-forward updates, inspect new commits and annotated tag signatures against the externally approved public key fingerprint. Refuse a tag overwrite and nonconforming refs. The hook is not a substitute for GitHub server protection.

No hook executes unit tests or E2E tests. The static code that hooks use is shared with the Makefile check routines. A missing signer fingerprint or Git signature verification capability makes the push fail closed, not automatically unsigned.

## Owner responsibility

The authorized fingerprint is stored outside Git. `git config user.signingkey` is a configuration check, **not** proof of signing. A real `git verify-commit` / `git verify-tag`, a match of the signer identity to the owner-approved fingerprint, and a check of the merge parents remain obligatory. Neither our delivered hooks nor local dry-run validations prove that an owner-controlled signing key is actually usable; the owner must produce signed objects in an authorized environment.

`core.hooksPath` is installed explicitly with `make hooks-install`. Git does not distribute active hooks on clone. Hooks can be bypassed locally; GitHub protections and the owner's review must provide independent boundaries. If branch protection prevents pushing the locally signed merge, do **not** switch to a GitHub-generated merge as a workaround.
