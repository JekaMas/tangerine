# Tangerine

Teacher Error Trainer, started from the nine supplied specification/audit files. Work and code are in English. The real local runtime foundation is implemented; full language scoring, author/reviewer/publication workflows, provider integration and validated content are still incomplete. Read audit/completeness.md before treating this as a complete trainer.

## Start the local foundation

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

## Required next inputs

Recover the original referenced taxonomy, contracts, prompts, validation policy and scoring requirements. Review the separate DEC-001–DEC-008 drafts without treating them as approvals. Provider keys, qualified independent reviewers, permitted real audio/teacher answers and fixed held-out validation policy are necessary for the full release. None is replaced with invented evidence.
