# Iteration 33 — saved-audio diagnostics

Entry: clean `0dadf31d0aac7fc7502a9d63de909cfbb04aafbe`, existing release
worktree. Scope is QUAL-04: retained weak-form, linking, pause and intonation
disagreements, their actual context/recordings/measurements/model replies.

## Anchors and ownership before implementation

- Production diagnostic context: `services/speech/diagnostic_context.py` owns
  `project_audio_intent`; `diagnostic_models.auditory` is the exact transport
  hook. Gemini currently bypasses that projection for ordinary diagnostics.
  Unify the projection before serialization; retain the actual projected wire
  through the existing capture and native diagnostic finalizer.
- Authored fixture/expectation owner: `services/speech/category_validation.py`,
  `make_probe` and `compare_probe`. A nominal mutated role currently always
  expects a demonstrated error. Permit an explicitly unresolved expectation;
  do not coerce a valid strong form into an error or a new model result.
- Durable lineage: original I26 `selected/*/{frozen,response,dispatch,comparison}.json`,
  original category linking observation, and connected-speech WAV/native/physical
  records. These files remain untouched. New reconciliation points to them and
  keeps historical judgments separate from fixture repairs and unperformed
  future observations.
- Evidence keys: category, exact clip ID/role/path, original public context,
  actual model reason, physical sample/F0 observation, current expectation basis
  and unresolved item. No private generator fact or punctuation proves function.
- Finalization: save the zero-call reconciliation and local Lab export/readback;
  run exact positive/negative DAG cases on committed-clean source, then update
  canonical tasks and acceptance. No new learner or release gate.

## Findings and work

- [ ] F1: demonstrate/fix Gemini's ordinary-diagnostic context projection;
  test the same boundary with target/reference, blind clips, private canaries,
  uncertain output, failure, no credentials and forbidden billing siblings.
- [ ] F2: allow authored ambiguous expectations. Strong function words,
  careful/linking variants, accents and legitimate question contours remain
  acceptable; changed contexts do not retroactively become observed calls.
- [ ] F3: reconcile every selected original clip/reply and physical observation.
  Preserve the missed 600 ms pause and intonation control false alarm. Acoustic
  direction is distinct from pragmatic correctness; no renderer repair follows
  from an unsupported judge opinion.
- [ ] F4: literal tests, exact DAG/discovery registration, relevant native/spec
  and language checks, evidence inspection, Lab readback and clean acceptance.

## Execution boundaries

Zero new inference, synthesis, provider calls, acquisition, installs, paid
credits/overage, deployments, PBT, publication or financial operations are planned.
Keep app3000, settings/data/media/tabs and canonical GAPS.md intact. Reuse valid
greens; only changed inputs or newly missing assertions require execution.

Preimplementation graph/discovery validation passed. OpenSpec apply context is
`data/iteration-33-diagnostics-20261027/apply-context.json`. Exact semantic CLI
search returned no index for `github.com/jekamas/tangerine`; direct tracing of
the named owners continues. No semantic or IDE evidence is claimed.

## Stable implementation checkpoint

Five demonstrated findings are repaired: Gemini projection bypass, compulsory
error expectation for an ambiguous carrier, failed observations confirming
favorable findings, physical-change conflict on a valid contour, and missing
“car” in future intonation context. The renderer is unchanged; the retained
pause and F0/model disagreements do not demonstrate a transform defect.

Actual stable native closure:512 category tests,6 original saved-evidence tests
and62 diagnostic/context/fixture/recovery tests, all passed.18 new regressions
also pass under installed speech Python3.12 with network disabled. Original
transcripts/source bindings are retained; typed unittest readers reconcile all
580 exact identities without repeating their execution for a commit.

The full informational I33 gate passed10/10 on dirty source. Current selection
is I33.P1–I33.P4 (six positive/four negative readers); graph/discovery, strict
OpenSpec1.13.1,390 specification assertions and stable Python syntax pass. The
source hashes/literal active aliases are updated against actual observed tests;
no old receipt hash is rewritten. Relevant unchanged Go/web evidence is retained.

Final local Lab22/run653686660f7547f59383cfc6056f2d3d retains57 artifacts;
nine actual downloaded files match original bytes. Both original model opinions
and changed-but-unobserved fixture inputs are preserved. All122categories,
42formulas,11sources and canonical GAPS.md remain unchanged. No user app restart,
provider call, synthesis, purchase or other external operation occurred.

Next: commit this complete implementation/evidence registration, run the same
four-property selection with --require-clean, then record acceptance and check
the canonical I33 tasks. Task boxes remain unchecked until that clean result.
