# Design

## Context

See proposal.md and audit/completeness.md. The first nine-file input is now supplemented by the complete 95-file v6-ste archive. Exact taxonomy/schema/prompt/policy/reference requirements are recovered with preserved provenance. The latest user scope is exploration, research and specification updates only. The project is new, on main, and owns no previous application behavior. Imported reports are historical.

## Goals / Non-Goals

Specify a simple single-person local product and complete requirement/evidence map in English. This increment changes specifications only. Keep semantic scoring, content publication, live capability and held-out acceptance dependent on exact original contracts and real evidence. No source-invented taxonomy, approval, corpus, model fallback, background queue or realtime interaction.

## Decisions

Use Smart Example's current origin/main workflow pin 3a2cccefa17aa7ba76594a94a4695741bfcbda5e and installed OpenSpec 1.13.1, with Tangerine-local extensions. The canonical Smart Example checkout is older; it is not the workflow source used by this project. No other checkout is mutated.

Use real Go pgx/minio adapters. Existing account/session tables and login code belong to the historical foundation; they are superseded by the no-account local requirements and require future removal/alignment. Migration tables and the foundation exercise catalog remain provisional. The catalog has no publication API, and is not represented as implementing the recovered original exercise schema. Recovered domain contracts must be reconciled with provisional foundation tables before future domain migration design.

Initialize migrations and private media idempotently without accounts, exercises, attempts or approvals. Generate internal service secrets automatically for the installation; users supply provider keys only. Preserve existing private bucket policies and refuse public media policies. docs/simple-local-product.md defines the launcher and activity views; exact bootstrap details remain GAP-054.

The browser calls a whitelist of same-origin routes. Server code alone reads configuration; provider keys are absent from the web container. CSRF rejection precedes storage. The existing 270-second constant is present in API/proxy/browser. Recovered runtime-v1 requires a propagated 270-second attempt deadline and 285/300/310-second API/proxy/browser outer timeouts. SYNC-01/02 schedule this mismatch for future implementation.

Arithmetic is a pure source-registry interpreter with exact fractions and independent vectors for all 27 core formulas. It does not determine claims, correction propositions, weights or semantic counter validity. Zero-denominator reason is supplied explicitly by the future validated domain owner, avoiding an invented per-metric policy. Auxiliary formulas remain preserved with planned property cases.

MinIO community is source-only and its upstream repository is archived as observed in official documentation. Build the requested implementation from exact source commit 7aac2a2c5b7c882e68c1ce017d8256be2feea27f and verified archive SHA-256; do not silently switch object stores. Base-image index digests were read from the official registry. They establish source identity and available architectures, not successful application builds/runs.

## Risks / Trade-offs

Recovered originals → preserve every category, schema, prompt and requirement; do not treat source recovery as implemented semantic guards or approved gold.
Unresolved DEC-001 through DEC-008 → separate proposals under audit/decisions, separate genuine owner decisions required.
No genuine reviewed corpus or live qualification → no publication or empirical correctness claim. The DeepSeek secret reference is discovered, but no live call or source transfer is authorized this turn.
Foundation tables are provisional infrastructure → reconcile exact domain schemas before adding domain tables or importing content.
Live FFmpeg apt repository dependencies → fixed FFmpeg version is selected, but complete transitive package/build identity still needs capture in actual built images for release.

## Migration Plan

Apply embedded numbered migrations transactionally with a PostgreSQL advisory transaction lock and stored checksums. Reject altered applied migration bytes. Do not initialize accounts or sessions in the target local mode. Compose waits for database/storage health and successful migration/media jobs. Named volumes retain database and media. Never run down --volumes as routine cleanup.

## Decision boundaries

The eight separate drafts are reviewable proposals, not approvals. Remaining genuinely unspecified values/methods and eight decisions are explicit dependencies, not discretionary implementation assumptions. See audit/completeness.md and tasks.md for the affected work and next action.


## Recovered full-contract overlay

All fifteen original capability specifications are retained in active v6-* deltas. Original IDs remain literal; the graph uses V6- prefixes to avoid collisions with task-derived MET/APR IDs. Active original-text adjustments include PROV-01 configurable profile lookup and explicit local scope for PLAT-01/02, LOCAL-02, LIFE-01 and SES-01/03. Original IDs and archived bytes remain intact; docs/simple-local-product.md supersedes account/tenant/access-role semantics. Immutable archive bytes remain under spec-inputs/v6-ste; every adjustment is inspectable against that source. Original summary and delta documents cannot override current user authority.

Case lifecycle is draft -> rendered -> needs_review -> verified -> published, with transactional state/source/evidence guards and audit. A nonretired case may enter quarantined with reason; renewed review goes to needs_review, never directly published. Published cases may retire while historical access remains. Payload changes create a distinct draft and invalidate old final-hash approvals. Attempt lifecycle is draft -> submitted -> evaluating -> complete/review_required/evaluation_failed; explicit expired-lease recovery and append-only adjudicated result revisions preserve original answer/result references. These source contract states differ from derived UI labels.

Full source and taxonomy inventories are audit/full-source-inventory.json and audit/full-taxonomy-coverage.json. Every listed profile remains a completeness obligation. Exact permissions/raw manifests/parser mappings precede ingest; unavailable paper/vendor releases block an all-sources-acquired claim. Every leaf/control retains its source context, realization and scoring limits. Imported illustrations are unapproved references. Exact acquired counts are currently zero and upstream hashes are unknown.

LLM selection follows docs/llm-configuration.md and the specification-only configurable registry. DeepSeek fast local testing is explicitly user-selected and uses the existing secret environment reference. It needs full schema/transport/retention qualification and applicable independent held-out measurements before production acceptance; original speech profiles and all numeric scoring remain unchanged. Changing model/profile/settings/prompts invalidates affected caches/calibration, not unrelated valid foundation receipts.

Scoring follows recovered scoring-v1/contract-invariants documents in full: separate detection/category/correction/explanation credit, exact rational proposition and hierarchical rules, substantive false-clause handling, negative control denominators, preserved domain ownership and micro pooling, null unresolved/unobserved results. Code may not infer semantic counters from arithmetic vectors or provider agreement.

This increment adds planned positive and negative cases for each recovered scenario, every source and every leaf. No executable test is added; state remains blocked/planned. Reference/inherited code is inert source comparison material, not application implementation or current oracle evidence.


## Exhaustive specification audit boundary

The latest user explicitly requires every data/flow/API/formula definition and a list of remaining gaps, with no implementation. The recovered archive fixes missing-source claims; it does not supply a complete product specification. audit/spec-fullness-20261008/GAPS.md records55 grouped missing/conflicting definitions with exact source locations, required input and positive/negative closure. Every finding maps to SPEC-001–055 and task11.5.1–55; audit/simple-local-20261008/gap-disposition.json supersedes the two account/access-role gaps, leaving 53 open definitions in the local scope. API obligations, all42 formulas, all122 leaves, all15 schemas/140 objects/864 field occurrences and all8 corpus profiles have separate audit matrices. Real recordings, permissions, human observations, provider calls and runtime acceptance remain evidence/implementation obligations in EVIDENCE.md. Existing behavior receipts are preserved. Full-specification readiness remains blocked until all definitions and material decisions are closed; no gap-free or full-product acceptance is claimed.

## Current simple local product

The latest user removes accounts, access roles, tenants and complex public APIs. docs/simple-local-product.md is the normative overlay and contracts/local/attempt.schema.json is the active local attempt contract. The bundled prescribed services stay internal; the future launcher performs readiness and initialization without manual infrastructure setup. Local person attestations preserve real review evidence without claiming authenticated independence. Teaching/blind-review disclosure is a view contract; the local owner can separately inspect authoring. Existing source contracts and login code stay historical until explicit future migration/alignment; no service code is changed here.
