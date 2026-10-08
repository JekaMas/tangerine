# Spec-only change and receipt preservation

Changed semantic planning inputs: complete recovered source bodies; PRV-01 allows explicitly configured DeepSeek development profile; full-source obligations now include every listed profile/release component; new per-leaf and deadline/state qualification requirements. New/changed unimplemented nodes have no observed PASS and remain blocked/planned. No production owner, test source, runtime fixture/data or toolchain changed.

All previous implemented requirement/property/scenario/test bindings remain unchanged. Existing foundation native logs and current-foundation-results.json remain byte-identical. The PRV-01 fingerprint changed only for its already blocked, unimplemented provider cases. No historical evidence fingerprint or test-source hash was refreshed to hide invalidation. New source recovery does not retroactively make missing-source tests pass.

The expanded graph is a plan, not a new executed test run. Revalidate native OpenSpec and graph/discovery structure for the changed specification inputs only. No app tests/builds, Docker operations, acquired corpus, inherited linguistic test execution or model inference are authorized this turn. Future implementation must adapt the old build_spec_inventory generator before using it; it is an earlier task-derived generator and would overwrite the enriched recovered plan.
