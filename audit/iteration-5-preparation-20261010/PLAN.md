# Iteration 5: request expansion and durable clean-text preparation

Start: 9f8faf5ab192a24b3a620545cf8568d975e6b190. The existing clean isolated checkout is reused on tangerine/iteration-5-generation. Canonical GAPS.md and preview data remain protected.

The fifth development increment implements the minimal/advanced blueprint, frozen preparation settings, canonical-text generation and durable checkpoint/readback/resume. Mutation, rendering and answer/scoring owners remain subsequent increments; no partial canonical candidate is reported as a completed generated exercise or put in the Library.

Anchors: simple-generation-flow.md, generation-contract-details.md, preparation-persistence.md; blueprint-write/blueprint, generation-input, preparation-settings/preparation-state and case-candidate contracts. Existing app.InvokeLLM owns context, frozen configuration, transport and native receipts. Existing Storage owns linked private assets, operation idempotency and document/head CAS. Preparation's original foreground operation owns phase writes; the final checkpoint transaction compares its head, active operation and actual deadline. No transaction spans inference.

The application preparation entrypoint dispatches through InvokeLLM, never through another SDK. Settings and registry bytes are saved before dispatch. The canonical candidate must preserve clean/surface equality, empty mutations, speaker participation and actual word count, without an exact-length gate. Read/list/resume use saved settings, not active settings. New settings require a new preparation.

Native controlled HTTP fixtures exercise production dispatch and persistence but do not prove linguistic quality, real account entitlement or live hosted generation. Actual included-only provider/MLflow quality observations remain required and currently blocked by audit/iteration-4-providers-20261010/LIVE-BLOCKER.json. No paid-credit case is authorized. This dependency must not be marked passed by fixture evidence.

Validation: materialize independent positive/negative request/output/state/sequence cases, bind every new property into the canonical DAG/discovery, run directly affected cases first, then the stable complete native selection on a clean committed candidate. Retain exact original source/schema/registry bytes and old receipts. Record all fresh and reused checks with their actual proof limits.
