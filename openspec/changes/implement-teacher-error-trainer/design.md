# Design

## Context

See proposal.md and audit/completeness.md. The first nine-file input is now supplemented by the complete 95-file v6-ste archive. Exact taxonomy/schema/prompt/policy/reference requirements are recovered with preserved provenance. The latest user scope is exploration, research and specification updates only. The project is new, on main, and owns no previous application behavior. Imported reports are historical.

## Goals / Non-Goals

Deliver independent executable foundation code and a complete task-derived requirement/evidence map in English. Keep semantic scoring, content publication, live capability and held-out acceptance dependent on exact original contracts and real evidence. No source-invented taxonomy, approval, corpus, model fallback, background queue or realtime interaction.

## Decisions

Use Smart Example's current origin/main workflow pin 3a2cccefa17aa7ba76594a94a4695741bfcbda5e and installed OpenSpec 1.13.1, with Tangerine-local extensions. The canonical Smart Example checkout is older; it is not the workflow source used by this project. No other checkout is mutated.

Use real Go pgx/minio adapters. Account/session/migration tables and a foundation exercise catalog support the explicitly independent runtime. The catalog has no publication API, and is not represented as implementing the recovered original exercise schema. Recovered domain contracts must be reconciled with provisional foundation tables before future domain migration design.

Initialize only the configured local account; never seed exercises, attempts or approvals. Existing account credentials and media policies are preserved. Private media initialization creates the requested bucket if absent and refuses existing public policies. Passwords use salted PBKDF2 SHA-256; sessions persist only token hashes and expiry in PostgreSQL.

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

Apply embedded numbered migrations transactionally with a PostgreSQL advisory transaction lock and stored checksums. Reject altered applied migration bytes. Keep account initialization separate and idempotent. Compose waits for database/storage health and successful migration/media/account jobs. Named volumes retain database and media. Never run down --volumes as routine cleanup.

## Decision boundaries

The eight separate drafts are reviewable proposals, not approvals. Remaining genuinely unspecified values/methods and eight decisions are explicit dependencies, not discretionary implementation assumptions. See audit/completeness.md and tasks.md for the affected work and next action.


## Recovered full-contract overlay

All fifteen original capability specifications are retained in active v6-* deltas. Original IDs remain literal; the graph uses V6- prefixes to avoid collisions with task-derived MET/APR IDs. The only active original-text adjustment is PROV-01 lookup admitting the explicitly versioned configurable profile registry. Immutable archive bytes remain under spec-inputs/v6-ste; every adjustment is inspectable against that source. Original summary and delta documents cannot override current user authority.

Case lifecycle is draft -> rendered -> needs_review -> verified -> published, with transactionally authorized audit. A nonretired case may enter quarantined with reason; renewed review goes to needs_review, never directly published. Published cases may retire while historical access remains. Payload changes create a distinct draft and invalidate old final-hash approvals. Attempt lifecycle is draft -> submitted -> evaluating -> complete/review_required/evaluation_failed; explicit expired-lease recovery and append-only adjudicated result revisions preserve original answer/result references. These source contract states differ from derived UI labels.

Full source and taxonomy inventories are audit/full-source-inventory.json and audit/full-taxonomy-coverage.json. Every listed profile remains a completeness obligation. Exact permissions/raw manifests/parser mappings precede ingest; unavailable paper/vendor releases block an all-sources-acquired claim. Every leaf/control retains its source context, realization and scoring limits. Imported illustrations are unapproved references. Exact acquired counts are currently zero and upstream hashes are unknown.

LLM selection follows docs/llm-configuration.md and the specification-only configurable registry. DeepSeek fast local testing is explicitly user-selected and uses the existing secret environment reference. It needs full schema/transport/retention qualification and applicable independent held-out measurements before production acceptance; original speech profiles and all numeric scoring remain unchanged. Changing model/profile/settings/prompts invalidates affected caches/calibration, not unrelated valid foundation receipts.

Scoring follows recovered scoring-v1/contract-invariants documents in full: separate detection/category/correction/explanation credit, exact rational proposition and hierarchical rules, substantive false-clause handling, negative control denominators, preserved domain ownership and micro pooling, null unresolved/unobserved results. Code may not infer semantic counters from arithmetic vectors or provider agreement.

This increment adds planned positive and negative cases for each recovered scenario, every source and every leaf. No executable test is added; state remains blocked/planned. Reference/inherited code is inert source comparison material, not application implementation or current oracle evidence.
