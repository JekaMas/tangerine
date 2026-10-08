---
name: openspec-archive-change
description: Archive a completed OpenSpec change.
metadata:
  owner: agent-workflow
---

# OpenSpec archive

Rendered from the pinned shared integration; edit canonical source, not this copy.
Read applicable project instructions and `.agents/workflow-project.json`.
Use `.agents/workflow/docs/operations.md` for relevant operation loading and
`docs/development/OPENSPEC_WORKFLOW.md` for project commands. Keep user authority and task scope.

Read native archive instructions and current requirements/tasks/evidence. Establish the shared DONE criteria and archive authority before `openspec archive <name> --json --yes`. Inspect resulting spec/archive diff. Missing required evidence remains incomplete; archive does not authorize deployment.

For each newly introduced capability, supply a meaningful `## Purpose` before
synchronization; native archive can otherwise insert a placeholder that fails
strict main-spec validation. After sync/archive, run
`openspec validate <capability> --type spec --strict --json --no-interactive`
for every affected main spec, preserving the selected store/root. Inspect its
requirements, links and scenarios. A successful archive command alone is not
valid synchronization; repair any resulting spec defect and revalidate.
