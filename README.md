# Tangerine

Teacher Error Trainer, started from nine initial files and the recovered complete 95-file v6-ste specification archive. Work and code are in English. The real local runtime foundation is implemented; full language scoring, author/reviewer/publication workflows, provider integration and validated content are still incomplete. Read audit/completeness.md before treating this as a complete trainer.

## Current specification

The active full specification is [specification/v2](specification/v2/README.md). [Current reconciliation](audit/local-simplification-20261008/REPORT.md) and [remaining decisions/inputs](audit/local-simplification-20261008/DECISIONS-AND-INPUTS.md) supersede earlier audits. All122taxonomy IDs/examples,27core/15aux equations and11full-source entries remain. LLMs check answers, review cases and adjudicate disputes; there are no human peer reviewers or qualification prerequisites. Eight stages are configurable, with DeepSeek fast as the future test default.

The target is a simple local GitHub source ZIP/clone: supply required operation keys, run the helper and open localhost. No accounts, complex public API setup, mandatory repeat audit or whole-corpus certification is required. Complete source imports and all benchmark features remain supported and report actual missing data independently of ordinary use.

Only specifications were updated. The existing foundation below still has historical login/manual setup and does not implement the revised launcher or complete trainer. No provider inference, corpus acquisition or runtime acceptance occurred in this increment.

## Start the historical local foundation

Docker Desktop must be running. Local development secrets were generated in deploy/local/.env for this checkout; the file is ignored and secret values are never printed in evidence. The owner email is owner@localhost. Read INITIAL_PASSWORD locally from that file to sign in.

For a fresh checkout:

```sh
git submodule update --init --recursive
cp deploy/local/.env.example deploy/local/.env
# Fill database/media/account secrets and the matching URL-encoded DATABASE_URL.
# Add provider keys only when implementing/using the dependent live operations.
docker compose --env-file deploy/local/.env -f deploy/local/compose.yaml up --build --wait
```

Open http://localhost:3000. No other container port is published. After authentication the library reads PostgreSQL and shows no published exercises until authentic reviewed content is available. No demo content or fake scoring is seeded.

The web container receives only internal API routing and origin configuration. Provider keys stay server-side. The Python speech container has actual FFmpeg/ffprobe; provider operations are not yet implemented. MinIO is built from pinned official source because the community distribution is source-only. Base image digests and actual build records are documented in deploy/local/images.lock.json.

## Checks and evidence

Read docs/development/AGENT_CHECKS.md and openspec/changes/implement-teacher-error-trainer/evidence/RESULTS.md. The single canonical task list is that change's tasks.md. OpenSpec/graph structure is not full product acceptance. Arithmetic tests validate all 27 preserved core formulas, not language judgments or complete scoring counter construction.

## Backup and isolated restore

Backups contain private account/session data; keep them in ignored data/backups. Runtime secrets are excluded and must be preserved separately. Backup creation stops application writers and resumes them after the dump/media archive. Never use down --volumes as routine cleanup.

```sh
python3 -B scripts/backup.py data/backups/<unique-name>
python3 -B scripts/verify_backup.py data/backups/<unique-name>
python3 -B scripts/restore_isolated.py data/backups/<unique-name> --project tangerine-restore-<unique-name>
```

Restore refuses any project that already owns resources and creates separate PostgreSQL/MinIO volumes. It never overwrites the running project. Full promotion/replacement of an existing installation requires an explicit operational plan; the script is an isolated recovery check.

## Current verification limits

The application was observed healthy at localhost:3000, while Docker management operations later timed out or returned HTTP 500. Fresh restart/architecture checks remain failed, and the source/image reconciliation after the speech arithmetic fix is pending. Full AMD64 runtime acceptance has not run. Exact results and preserved failures are in the canonical acceptance record.

## Historical v6 recovery and dependency snapshot

The original taxonomy, 15 schemas, five prompts, policy/reference documents and 48 original requirements are recovered. Read [the completeness review](audit/completeness.md), [complete source research](audit/corpus-release-research.md), [all-source inventory](audit/full-source-inventory.json) and [configurable LLM contract](docs/llm-configuration.md). The plan covers all 122 categories/control leaves and full versions/components of all eight listed sources. No corpus was acquired or review fabricated.

The latest increment is specification-only. DeepSeek 4.1 fast is planned through model deepseek-flash, low reasoning and the existing server secret reference; no Codex setting or service code was changed and no inference call was made. Supplied policy proposals are approved subject to current LLM-only simplification. Actual private data/documentation, real provider observations and future implementation remain outstanding; current owner choices are in the linked audit. The current application is still the incomplete local foundation.
