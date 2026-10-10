# Tangerine

A local, open-source Teacher Error Trainer. Original software is licensed under [Apache-2.0](LICENSE); imported data and third-party components retain their own terms. All project artifacts are in English.

## Run locally

Download and extract the complete GitHub source ZIP, or clone this repository. Install and start Docker Desktop, or Docker Engine with Docker Compose v2.20 or newer. No host Go, Node, Python, Git or workflow submodule is required to run the downloaded application.

```sh
sh scripts/tangerine start
```

Open **http://localhost:3000**. There is no application login. First startup builds the supplied Next.js, Go, Python/FFmpeg and MinIO sources, starts PostgreSQL and private media storage, applies checksum-verified migrations and creates one workspace automatically. An empty Library means no exercises have been saved; startup does not seed demonstration content or download models.

First startup needs network access to the pinned build dependencies and enough disk space for the images. Runtime has only port 3000 published, bound to loopback. Internal database, media and API credentials are generated automatically in `data/config/runtime.env`, with private file permissions; they are retained across restarts. Keep this file with the installation's data. Do not delete it while retaining its Docker volumes, and do not use `docker compose down --volumes` for ordinary shutdown.

```sh
sh scripts/tangerine status
sh scripts/tangerine logs
sh scripts/tangerine stop
sh scripts/tangerine start
```

`stop` retains the database, private media and configuration. `logs` redacts known secret values. Startup errors identify missing Docker/Compose, unavailable Docker, incomplete source, damaged configuration, failed builds or failed service startup. For `START_FAILED`, check whether port 3000 is occupied and inspect `logs`. Fix the reported cause and retry; the launcher does not delete your data.

`.env` is created from [.env.example](.env.example). Provider keys are optional during startup and stay out of browser assets and build layers. Use plain `KEY=value` entries from the template. Provider sign-in, included-only usage controls and supported operation choices are specified in [service setup](specification/v2/docs/service-setup-guide.md) and [provider access](specification/v2/docs/provider-access.md); those operations are implemented in later iterations.

## Current implementation

Iteration 1 implements the download/build/start/stop/status/logs foundation, automatic durable configuration, real dependency health and no-login empty Library. Database-backed public Library projections are implemented without exposing transcripts or answer keys. Speech readiness checks the actual FFmpeg/ffprobe binaries; it does not claim synthesis capability.

The full product remains the on-demand flow: requested LLM clean text → LLM mutations and saved answer key → generated stored audio → listener's free-text response → LLM answer checking, exact scores and recommendations. Iteration 2 adds the shared typed domain store: immutable complete documents and frozen references, revision heads, idempotent operations, private asset reserve/upload/readback/link and interruption recovery. Existing foundation data is backed up and verified before the additive storage migration. Generation, synthesis, grading, their domain action integration, LLM Lab, imports and full user backup/restore remain subsequent engineering iterations, not working controls in this foundation. No provider inference or generated-audio acceptance is claimed here.

## Specification and evidence

The active [full specification](specification/v2/README.md) preserves all 122 taxonomy/recipe identities, 42 scoring formulas and 11 original full-source scopes. External corpora remain optional for ordinary generated exercises. There are no human peer-review prerequisites.

The canonical implementation task list is [OpenSpec tasks](openspec/changes/implement-teacher-error-trainer/tasks.md). [Iteration 1 evidence](audit/iteration-1-local-foundation-20261010/REPORT.md) and [iteration 2 evidence](audit/iteration-2-domain-storage-20261010/REPORT.md) separate actual native observations from later full-product obligations. Structural OpenSpec/DAG checks are not runtime acceptance. Development follows the pinned [workflow](docs/development/OPENSPEC_WORKFLOW.md).

Historical login/manual-setup instructions and backup scripts predate the current local-workspace contracts. They are retained in Git history and audit records; current deployment uses the helper above. Backup/restore implementation and complete architecture qualification remain visible in the full task list.
