# Design

## Context

See proposal.md and audit/completeness.md. The user confirmed that the supplied nine files constitute the input package. Their referenced taxonomy/schema/prompt bodies are absent. The project is new, on main, and owns no previous application behavior. Imported reports are historical.

## Goals / Non-Goals

Deliver independent executable foundation code and a complete task-derived requirement/evidence map in English. Keep semantic scoring, content publication, live capability and held-out acceptance dependent on exact original contracts and real evidence. No source-invented taxonomy, approval, corpus, model fallback, background queue or realtime interaction.

## Decisions

Use Smart Example's current origin/main workflow pin 3a2cccefa17aa7ba76594a94a4695741bfcbda5e and installed OpenSpec 1.13.1, with Tangerine-local extensions. The canonical Smart Example checkout is older; it is not the workflow source used by this project. No other checkout is mutated.

Use real Go pgx/minio adapters. Account/session/migration tables and a foundation exercise catalog support the explicitly independent runtime. The catalog has no publication API, and is not represented as the absent original exercise schema. Original domain-contract recovery must precede domain migration design.

Initialize only the configured local account; never seed exercises, attempts or approvals. Existing account credentials and media policies are preserved. Private media initialization creates the requested bucket if absent and refuses existing public policies. Passwords use salted PBKDF2 SHA-256; sessions persist only token hashes and expiry in PostgreSQL.

The browser calls a whitelist of same-origin routes. Server code alone reads configuration; provider keys are absent from the web container. CSRF rejection precedes storage. The 270-second constant is present in API/proxy/browser; the full attempt owner still needs implementation and a common propagated end-to-end deadline.

Arithmetic is a pure source-registry interpreter with exact fractions and independent vectors for all 27 core formulas. It does not determine claims, correction propositions, weights or semantic counter validity. Zero-denominator reason is supplied explicitly by the future validated domain owner, avoiding an invented per-metric policy. Auxiliary formulas remain preserved with planned property cases.

MinIO community is source-only and its upstream repository is archived as observed in official documentation. Build the requested implementation from exact source commit 7aac2a2c5b7c882e68c1ce017d8256be2feea27f and verified archive SHA-256; do not silently switch object stores. Base-image index digests were read from the official registry. They establish source identity and available architectures, not successful application builds/runs.

## Risks / Trade-offs

Missing original taxonomy/contracts/prompts → block semantic handlers and never claim all original requirements were recovered.
Unresolved DEC-001 through DEC-008 → separate proposals under audit/decisions, separate genuine owner decisions required.
No reviewers/corpus/provider keys supplied → no publication or empirical correctness claim.
Foundation tables are provisional infrastructure → reconcile exact domain schemas before adding domain tables or importing content.
Live FFmpeg apt repository dependencies → fixed FFmpeg version is selected, but complete transitive package/build identity still needs capture in actual built images for release.

## Migration Plan

Apply embedded numbered migrations transactionally with a PostgreSQL advisory transaction lock and stored checksums. Reject altered applied migration bytes. Keep account initialization separate and idempotent. Compose waits for database/storage health and successful migration/media/account jobs. Named volumes retain database and media. Never run down --volumes as routine cleanup.

## Decision boundaries

The eight separate drafts are reviewable proposals, not approvals. Missing original values/IDs are source blockers, not discretionary implementation assumptions. See audit/completeness.md and tasks.md for the affected work and next action.
