# Interface and exercise-control redesign

Status: complete for this increment. Baseline:
`99f86777809679a0621d1878767ba419946eb452` on
`tangerine/iteration-16-release`. Deployed at http://localhost:3000/prepare.
The sole canonical task list is openspec/changes/implement-teacher-error-trainer/tasks.md,
UX.R1–UX.R5. The user requested a whole-service visual refresh and category,
severity and mistake-amount controls. Existing features, records and provider
settings remain. No paid API use, purchase, overage or remote publication occurred.

## Design and behavior

Applied the existing [Typography skill](/Users/jekamas/.codex/skills/typography/SKILL.md)
and inspected [Anthropic Frontend Design guidance](https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md).
No skill was installed. The shared shell covers Library, preparation,
listening/results, attempts, audio, reviews, reports, sources, Settings, recovery
and cleanup. It provides grouped navigation, current-route indication, keyboard
focus, skip link, narrow-screen menu, reduced motion and contained long content.
Source Sans 3 is bundled locally with its SIL OFL; no font CDN request is needed.
Blue-gray canvas, white surfaces, navy text and orange actions replace inconsistent
headers. Library and preparation have dedicated layouts; existing actions remain.

Searchable exact categories and selected chips supplement broad families. A
cached read-only projection uses the existing taxonomy without inference/database
access: 122 records, with 114 errors and eight acceptable-variant controls.
Ordinary injection excludes those controls. Collocations and style/register are
discoverable. Exact and broad simple selections are mutually exclusive; advanced
fields retain precedence and ordinary compatibility admission. Exact selections
restrict generation and require a primary true error per category unless count=0.

Severity allows any or one/more of Minor, Moderate, Major and Communication
breakdown. The saved request, mutation prompt and single output admission use it,
independently of count/CEFR. Existing 1/2/3/4 weights remain unchanged.
Low/Medium/High resolve from requested words at 1/2/4 mistakes per 100, rounded,
with at least one and enough to cover selected categories/distinct broad domains.
Overlapping pronunciation families do not double count coverage. The total is
visible before generation; requested length is approximate. Automatic remains
null and Exact preserves nonnegative integers, including zero. Insufficient
positive counts are explained before dispatch. Existing blueprints/checkpoints
retain the effective request; no migration or repeated stored-data audit is added.
Reviews now offers an exercise picker; selecting one reads history without
running a review. Failure/retry and malformed advanced input retain other choices.

## Owners and repairs

AppShell owns navigation; shared CSS owns presentation; CategoryPicker and
AmountControl own controls; request.js owns pure projection; usePreparation owns
foreground requests. Native metadata, mutation selection, acoustic routing and
single new-output admission remain separate. Scoring/imports/providers are not
rewritten. A real preparation exposed category_ids being mistaken for database
references: the checkpoint projection now recognizes frozen taxonomy labels while
preserving actual settings associations. Exact pronunciation selects existing
controlled acoustic capability; exact text-only requests do not acquire it.

## Executed evidence

[RECONCILIATION.json](RECONCILIATION.json) maps all 34 selected DAG cases to their
passing receipts and independent expectations; none remains planned:

- 13 native race-detector cases: catalogue/control distinction, exact selection,
  distinct-category coverage, severity, zero/legacy behavior, acoustic capability
  and checkpoint projection.
- Eight pure shipped-JavaScript request cases: presets/floors, Automatic/Exact/zero,
  invalid counts, clearing, advanced precedence and severity independence.
- Eleven readbacks of actual CUA/Chrome observations and saved HTTP data: all
  eleven routes at desktop/390px, mobile/keyboard navigation, unchanged learner
  data/settings, catalogue outage/retry, saved selections, interrupted transport,
  review selection/recovery, malformed advanced input and explicit-zero copy.
  Twenty-two retained pictures show the actual desktop/mobile screens.
- Two actual-model evidence readbacks: minor collocation and explicit zero,
  through clean text → mutation/key → local speech → saved Library case.

All 20 existing browser regressions passed with their real web/API/PostgreSQL/MinIO
boundaries and explicitly constructed model-output/timing fixtures. Only the driver
was adapted to the new controls. Existing affected native mutation/default/selection
greens are retained. No unrelated full-suite rerun is represented.

Actual generation used the existing ChatGPT included-plan profile and local
Kokoro. Before inference, ChatGPT Usage showed Tangerine access on, purchased-credit
use after limits off and automatic reload off; no financial setting changed.
One flow produced a single lexis.collocation unit at minor/weight 1; zero retained
clean text/empty key. Both stored WAVs. Twelve native capture packets retain actual
prompt/context, bindings, model outputs and speech observations. Local MLflow
experiment 7, run `11d2c3c8f45549acbfe3c2cc904ce2b5`, read back both flows, WAVs and
all packets without additional inference. Unknown native costs remain unknown.

Stable Go vet/gofmt, the production Next.js build, 387 artifact assertions, DAG
and discovery validation passed. Native strict OpenSpec 1.13.1 passed without
issues. The global CLI had changed independently to 1.14.3; its unsuccessful
receipt remains. Existing cached 1.13.1 bytes were run in ignored evidence storage
without installing/changing a global tool. The pinned wrapper reported
invalid_output on its large apply preview; all six full native JSON artifacts
pass the same pinned validators when read completely. Original failure and
full-artifact reconciliation remain; the wrapper itself is not relabelled green.

## Retention and limits

Original failures remain: a seven-control fixture assumption corrected to eight;
a negative assertion corrected to inspect typed Detail; a PNG-only assumption
corrected for native JPEGs; the actual category-reference preparation defect; and
the CLI/parser receipts. Only invalidated cases were repeated. Record/commit-only
edits do not invalidate passing behavior. Reconciliation names each actual receipt.

The learner's original attempt and configuration/credential presence match their
baseline. A compose recreation briefly picked up an existing .env DeepSeek key
where the old API had none; runtime absence was restored before inference. No
private settings were committed or persistently changed. All 122 category IDs/
recipes, 42 formulas, eleven original source scopes and migrations remain;
29 protected tracked files were compared with baseline. The canonical checkout's
unrelated GAPS.md edit is preserved.

This finite interface/control evidence does not establish universal linguistic/
acoustic accuracy, new hosted-provider qualification or renewed full-release
acceptance. Unselected release cases remain unexecuted this round. Semantic search
reported no index for the exact worktree; exact owner tracing and this agent's
source review are the actual review evidence.

Private observations, pictures, WAVs and native logs are in data/ux-controls-20261023/.
The browser is left on Prepare with collocation/formality, minor severity and
Medium (four mistakes in approximately 200 words), ready for the user to generate.
