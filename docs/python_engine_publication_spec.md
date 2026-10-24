# Python engine checkpoint publication

## Requirements

Publish the existing standalone Python battle implementation on a new branch. Preserve the accepted 68-item entry point and keep the accepted, unpromoted 75-item candidate separate. Do not change battle behavior, run Godot, train a model, change master, or create a pull request.

## Design

Use two isolated, immutable source snapshots under `python_engine/`, each containing the same fifteen-file runtime closure used in its recorded validation. Include small JSON layouts, standard-library-only package checks, curated validation summaries, source hashes, and third-party attribution. The historical original-game comparisons are summarized; proprietary game sources/assets and private raw capture bundles are excluded.

## Implementation

Copy only files named in the two verified source manifests, without editing their bytes. Build a publication manifest for the explicit export set. Document the input schema and commands separately from the repository's older simulator. Run only source-integrity checks, a small formal68 regression/smoke suite, and one standalone CLI invocation. Review the entire new-commit diff for credentials, private records, binary payloads, and raw game sources before publishing.

## Acceptance

All thirty runtime snapshot files match their recorded SHA-256 values. The exported package runs with Python and its standard library alone. Candidate75 remains unpromoted; unsupported and unverified domains are documented. Only the new branch is pushed, with one reviewed publication commit; read back its remote SHA and file tree. Existing source workspaces and checkpoints remain untouched.
