# Tangerine OpenSpec workflow

Use OpenSpec 1.13.1 and shared workflow commit 3a2cccefa17aa7ba76594a94a4695741bfcbda5e, the current Smart Example origin/main workflow pin inspected for this setup. Read .agents/workflow/docs/project-flow.md and the installed operation instructions. Use one canonical tasks.md in implement-teacher-error-trainer. Preserve supplied source and explicit missing-source dependencies.

Use verification.json and discovery.json for requirement/property/positive/negative evidence. Structural graph validity is not behavioral acceptance. Planned cases remain not_run; blocked cases do not pass. Do not rerun valid greens without recording the changed input. Read AGENT_CHECKS.md for concrete commands. No installation, subagent, publication, provider substitution or invented approval follows from workflow adoption.

For AI-affecting increments, load AI_DEVELOPMENT.md and the active AI development spec. Record the affected properties/cases, inventory and Lab-linked evidence in the same canonical change; do not create a second task list or treat optional learner Lab settings as a development exemption. Pure spec exploration has no inference requirement.

For `openspec-verify-change`, the existing project profile routes review through
`REVIEW_AND_VALIDATION.md`, which requires
`UI_UX_TYPOGRAPHY_VERIFICATION.md`. This is the project-specific place to maintain
UI/UX, typography and evidence review; do not edit generated skill adapters or
the pinned shared workflow to add Tangerine-only checks. Continuation iterations
17–30 and their selectors/dependencies are in the canonical change’s
`completion-iterations.json`; the readable overview is
`completion-iterations.md`. Verify-only remains read-only; apply plus repair
authority continues through fixes and affected revalidation.

The 2026-10-25 planning observation found installed OpenSpec **1.14.3**, while
this project’s recorded intended version above remains **1.13.1**. Report the
version actually used; do not claim the intended version was executed. Iteration
17 owns reconciliation without silent installation, global downgrade or shared
workflow upgrade. Existing receipts retain their original tool versions.

## Iteration 17 tool reconciliation

The global CLI is 1.14.3; its earlier strict result with 253 warnings remains a
non-pass at that tool/version. The existing project pin is 1.13.1 and the selected
shared workflow remains unchanged. Use an already available 1.13.1 package explicitly;
do not silently run the global version, upgrade/downgrade it or install anything.
The observed local package is:

```sh
export TANGERINE_OPENSPEC_CLI="$PWD/data/ux-controls-20261023/pinned-tool/package/bin/openspec.js"
node "$TANGERINE_OPENSPEC_CLI" --version
OPENSPEC_TELEMETRY=0 DO_NOT_TRACK=1 OPENSPEC_NO_UPDATE_CHECK=1 \
  node "$TANGERINE_OPENSPEC_CLI" validate implement-teacher-error-trainer --strict
```

The first command must report 1.13.1. That ignored local path is a developer-tool
observation, not a source-ZIP runtime prerequisite. Another checkout may bind its
existing 1.13.1 package via the same variable; a missing package remains a stated
tool dependency. I17's committed check records the actual native result/version.
No historical 1.14.3 warning receipt is relabelled a 1.13.1 pass. Use the existing
shared local adapter with a process-scoped wrapper to this selected CLI when
that adapter needs an `openspec` executable on PATH.
