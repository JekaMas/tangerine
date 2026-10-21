# Iteration 15 verification and repair

Starting revision: 0517e1e4026bc49b3c08aa2255e83688916ff413, clean isolated iteration15 worktree. Full scope: I15-01 through I15-08. Retain the original 74-case accepted join and raw failures. Current request authorizes repair and local commits; paid inference remains forbidden.

Reviewed native stage coordination/HTTP, archive codec/storage snapshot, local Docker controller/launcher, source/report/experiment erasure and local pages against the approved contracts. New counterexamples will exercise partial-stop recovery, selected-workspace Lab configuration, expired foreground cleanup and complete experiment evidence deletion. No prompt/model/scoring changes or repeated stored-data validation are planned.

In scope findings and completion live in the canonical tasks.md; this file retains investigation and evidence. Exact semantic search for experiment storage returned No index found for this checkout; no semantic or IDE evidence is inferred.

## Confirmed counterexamples and repairs

1. Failed stop: both backup and switch omitted rollback because recovery was installed after the stop command. Two command-boundary subcases failed. Recovery is installed before stopping; failed recovery is reported accurately.
2. Selected Lab: scripts/lab used root runtime rather than the selected workspace; an absent restore runtime silently used the original credentials. CLI counterexamples failed. Shared scripts/workspace-env now owns workspace selection for both entrypoints. Initial CLI fixture expected /var paths while shell pwd returned /private/var; that fixture path was resolved before keeping the decisive red receipt.
3. Expired writer: deletion treated every running operation as active forever, ignoring the existing270s foreground deadline. Native counterexample failed. Preserve the actual evaluation/import/experiment leases and live writer guard.
4. Experiment erasure: native experiment receipts and comparison bytes were absent from the preview. Native counterexample failed. Native source membership now includes comparison artifacts and recorded receipt roots; existing storage closure follows the linked operations/bindings/context/diagnostic copies.

Red artifacts: data/iteration15/verify-partial-stop-red.jsonl, verify-launcher-admitted-red.stderr, verify-deletion-red.jsonl. All failures retained; no paid/model inference.

Invalidation: localctl backup/switch behavior and used command fixture changed; rerun those lifecycle cases. Deletion owner changed: rerun native erasure/active/shared/stale cases. scripts/workspace-env changes extracted-source startup/maintenance/Lab routing: rerun actual workspace scenarios plus the added native selected-Lab read. Archive codec, generation semantics/prompts, arithmetic and deterministic MLflow artifact semantics remain unchanged; retain their prior exact greens.

Stable repair scope:82edges/73physical tests/8properties (42positive,40negative).61affected/newedges will execute once on the committed-clean repair;21unchanged archive/generation/deterministic-Lab edges retain their exact earlier clean receipts. verify_reconcile.py checks the complete membership, actual fresh statuses/fingerprints, original retained assertions/commands and bounded runtime diff.

423static and5160property/fixture assertions pass. Strict OpenSpec, current DAG/discovery pass. Pinned Go1.26.5 vet/gofmt completed once after stable Go edits; original scope/prompts/migrations and canonical GAPS preservation pass. Structural receipts are not behavior claims. Fresh acceptance is next.
