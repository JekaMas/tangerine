# Tangerine: full local release specification

This archive consolidates the available specification and all 53 reported gap entries.
It preserves the full first-release scope. It is not a working application distribution.
It does not claim that all 53 gaps are closed or that missing private data has been acquired.
Read `audit/FINAL-REPORT.md` and `audit/gap-status.json` before implementation.

## Included

The package includes 122 taxonomy leaves, 27 main formulas, 15 auxiliary measurements, and their exact data contracts.
It includes local operation contracts, reference DDL, process rules, six LLM stage bindings, audio methods, source profiles, and release gates.
The original v6 archive, the previous resolution draft, and both user-supplied gap reports remain unchanged in `inputs/`.
They are historical source material, not a second active specification.

The product has one local workspace. It has no user accounts, user sessions, access roles, tenants, or public API setup.
The teacher listens, writes an answer, submits it, and waits for synchronous evaluation.
The application stores the original answer before provider calls. Code calculates all authoritative numeric scores.
No active mock provider, fake exercise seed, or invented approval is included.

## Source scope

EFCAMDAT R2, Shatz2020, and Oksuz2025 are separate required source profiles.
Moodrick and NIR have separate licensed-export or documented private-interface contracts.
The operator supplies real credentials through configuration. Credentials do not create source-use rights or an undocumented API.
The full source inventory remains explicit. Missing access cannot silently reduce it to a sample.

This archive contains no acquired corpus bytes, genuine reviewer observations, or live provider receipts.
No current repository snapshot for commit `203c1f1` was available. This archive is not an applied patch to that commit.

## Inspect this package

Use Python with the exact review dependencies:

```bash
python -m pip install -r requirements-review.txt
python scripts/verify.py
```

The program inspects actual local artifacts and symbolic equations. It creates no synthetic teacher answers or empirical fixtures.
It is not the official OpenSpec CLI, a database migration, a Docker test, or a live provider benchmark.
The delivered results are in `audit/validation-results.json`.

## Implement the full product

Read `AGENTS.md`, `docs/authority.md`, and the active OpenSpec change.
Use `domain/operations.yaml` and `contracts/openapi.yaml` for internal calls.
Use `db/schema.sql`, `domain/persistence-map.json`, and the process documents for storage and recovery.
Resolve the explicit approval and external-source obligations without fabricating their evidence.
Do not treat an empty working interface, an adapter shell, or one successful exercise as the full release.

The Compose file is a reference contract. The actual application images and launcher are not included.
Do not report that Docker starts this product until actual compatible builds and the required runtime checks exist.
