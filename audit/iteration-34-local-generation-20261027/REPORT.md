# Iteration 34 — installed-local generation repair

**Status: implementation and scoped observations complete; committed-clean acceptance pending.**

The selected product path is the existing Qwen 9B non-speculative profile with plain output and the repaired native projection.30 actual local calls across14 fixed preparation requests are retained, including every failed attempt. Four additional provider-boundary replays exercise the current mechanical projection and real persistence using retained actual Qwen replies, with blueprint identity rebound only. They are not new inference.

## Repairs and ownership

1. The canonical prompt now preserves explicitly requested wording/counts. The mutation prompt gives explicit requested placement priority, keeps recurring-ledger rules conditional, and aligns preferred corrections with the quoted scope. These are prompt repairs, not new learner checks.
2. `mutation_shape.go` derives an omitted fixed severity weight and supports optional explanation from the actual supplied rationale/propositions. Missing linguistic explanations and malformed explicit values remain errors; correct controls are not relabelled.
3. `mutation_projection.go` admits an explicitly supplied unique final `surface_span` when the original quote is absent. Repeated, missing, ambiguous or acoustic operands are not guessed.
4. `mutation_correction_projection.go` trims only already supplied unchanged canonical context around a preferred textual replacement. The complete supplied correction must uniquely cover the mapped canonical scope, with unchanged context outside it. It preserves other valid alternatives, never adds missing words, and clears an IPA that described a wider phrase.

All projections run once before ordinary admission. Stored accepted keys are trusted and remain unchanged. Transport/retry, preparation/persistence and numerical scoring retain their own owners. No route, auth, queue, publication review, repeated DB audit or ordinary qualification gate was added.

## Bounded alternatives

The common authored requests are the frozen two-error noun-number/collocation case and a zero-error control. This is a repair comparison of the three ORIGINAL failed installed profiles, not a catalogue/model/parameter sweep. Versions were recorded before each directly required execution.

| Checkpoint | Native admission | Strict precision | Strict recall | Matching accuracy | Actual generation seconds: positive / control |
|---|---:|---:|---:|---:|---|
| Qwen 9B plain, original | 2/2 | 50.0% | 50.0% | 77.8% | 150.3 / 64.7 |
| Qwen 9B full decoder schema | 0/2 | N/A | N/A | N/A | 29.9 / 12.9 |
| GPT-OSS 20B, scope prompt | 1/2 | N/A | N/A | N/A | 102.8 / 45.3 |
| GPT-OSS 20B, weight/rationale projection | 1/2 | N/A | N/A | N/A | 125.0 / 38.8 |
| GPT-OSS 20B, final locator projection | 2/2 | 50.0% | 50.0% | N/A | 111.3 / 93.7 |
| Original27B, thinking off | 1/2 | N/A | N/A | N/A | 91.3 / 191.6 |
| Qwen 9B, repaired prompts | 2/2 | 50.0% | 50.0% | 77.8% | 140.4 / 61.2 |
| Qwen 9B replies + current scope projection | 2/2 | 100.0% | 100.0% | 100.0% | Retained140.4 /61.2; no new inference |

Precision/recall require both the requested mutation and its exact scoped preferred repair. Accuracy follows the frozen matching-event formula; a mismatched predicted correction can be FP while the missed required correction is FN. It is not a population accuracy or a learner-grading benchmark. Missing outputs/controls have no full-population accuracy. The final native projection has TP2, FP0, FN0 and TN6. The raw latest Qwen candidate still has one incorrectly scoped preferred correction; the improvement is the system projection, not a claim that the raw model became perfect.

The final source model generated the two mistakes at the requested locations. Its noun-number correction and explanation concern singular `book` after `two`; its collocation correction/rationale concern `do a decision`. The correction condition and the optional explanation remain separate. The final native key uses `make a` for the quoted `do a`, so literal replacement yields one `decision`, rather than duplicating it.

The model repeated `help with the event` twice in the zero-error clean text despite the once-only construction instruction. This remains an instruction-following deviation in comparison.json. Both occurrences are correct and preserved, so that distinct control type counts once as TN. No phrase-count enforcement or rejection was added to ordinary use.

## Cost and resources

| Checkpoint | Actual new calls | Returned input/output tokens | Local API charge |
|---|---:|---:|---:|
| Qwen 9B plain, original | 5 | 31,678 / 3,001 | $0 |
| Qwen 9B full decoder schema | 2 | 13,401 / 895 | $0 |
| GPT-OSS 20B, scope prompt | 5 | 42,759 / 4,112 | $0 |
| GPT-OSS 20B, weight/rationale projection | 5 | 42,905 / 3,927 | $0 |
| GPT-OSS 20B, final locator projection | 5 | 42,272 / 6,665 | $0 |
| Original27B, thinking off | 3 | 15,853 / 576 | $0 |
| Qwen 9B, repaired prompts | 5 | 32,200 / 2,788 | $0 |
| Qwen 9B replies + current scope projection | 0 | 0 / 0 | $0 |

Total returned usage: 221,068 input and 21,964 output tokens from 27/30 calls. The two HTTP500 replies and timed-out request lack token usage; missing usage is not zero compute. Local electricity/hardware cost was not measured. No API key, purchased credit, overage, cloud model, new installation or model pull was used.

Observed model-memory peaks are retained in MEASUREMENTS.json and two-second resource samples. These are descriptive observations, not isolated hardware or throughput benchmarks. Runs include cold loads, cache effects, retry/repair and native storage work. The1.83s/1.76s replay times exclude generation and cannot support a speedup claim.

## Remaining observations and recommendation

- The non-speculative Qwen runner still produced an actual MLX cache-offset panic. Its existing same-profile retry succeeded within270 s; no host runtime or model installation was changed. The old threadgroup failure and current cache failures remain distinct.
- The full schema option exceeded the64K conservative byte budget before mutation dispatch. Plain output is the selected setting; the full owned contract and single native admission still apply.
- GPT-OSS 20B produced wrong placement or correction/metadata despite protocol acceptance. It is not qualified here for arbitrary generation. Its separately retained answer-checking evidence is unchanged.
- The27B thinking-off positive canonical call still timed out. The control completed in191.6 s; neither a longer deadline nor a warm control qualifies the failed positive.
- Exact once-only wording adherence and broad122-category prose quality are not established by these two requests. Native scoped mechanics are verified; uncertainty and failed alternatives remain visible.

The [local setup](../../docs/local-llm-generation.md) records the exact generation profile. It applies to NEW preparations. The running user app, its selected provider and saved attempts were not reconfigured or restarted. All122 categories/recipes,42 formulas and 11 full-source scopes remain byte-identical; canonical GAPS.md is preserved.

## Evidence and verification

- Actual model wires, contexts, receipts, bindings, accepted/failed preparations and model metadata: `data/iteration-34-local-generation-20261027/` and its named strategy subdirectories. All30 actual dispatches join native request/reply/context/binding records.
- Native current projection/finalization: `projection-replay/native.jsonl`, its four labelled boundary replays and saved candidate/manifest readback. Only blueprint identities are rebound; linguistic reply content is retained.
-109 affected Go race cases and10 new literal methods: NATIVE-COVERAGE.json; actual current outputs are go-final.jsonl. Controlled runner/invalid-quote siblings are reused from their unchanged passing subtests; the corrected real parent-deadline case has its own passing receipt.
- Original failed red cases and oracle failures remain retained. The metric now compares the entire repaired turn, distinguishes repeated correct controls from missed construction instructions, and reports incomplete populations as N/A.
- Eight actual local MLflow runs with artifact downloads/readback: MLFLOW.json. The final run is explicitly tagged retained-reply projection replay; logging/export makes zero inference calls.
- Static390 schema/prompt/assembly assertions passed. The final exact selected DAG, strict OpenSpec, discovery, language/preservation and committed-clean results are recorded in ACCEPTANCE.json when accepted.

## Review boundaries

This is self-review against independent literal expectations, not a second reviewer or corpus/human gold. UI/UX and typography follow the project procedure and the typography skill. No web rendering, interaction, error-presentation or font owner changed; actual I33 visual/playback evidence retains its original scope and was not rerun. Typography guidance was applied to the readable report tables and explicit units/N/A. No new screenshot/video, speech synthesis, answer-checking inference, deployment, publication, PBT or financial execution is claimed.

Ollama documentation used for narrow capability research: [Responses compatibility and thinking aliases](https://docs.ollama.com/api/openai-compatibility), [structured output](https://docs.ollama.com/capabilities/structured-outputs). Actual runtime/model metadata and returned wires take precedence over generic documentation.
