# Local deployment contract

This directory describes the required local deployment. It does not contain the application images.
The publisher must supply actual images and their digest lock. Do not use substitute images to claim application readiness.

## Prerequisites

The host requires Docker, Docker Compose, and a browser. The deployment contains the application language runtimes.
The operator supplies real OpenAI and Azure credentials. An unavailable provider must stop the affected operation.

The operator must also supply local passwords and signing secrets. Each secret belongs only to its stated service.
The image lock must contain the real amd64 or arm64 image references. No guessed digest is permitted.

## Start a released application

1. Obtain a released application bundle with its actual image lock.
2. Copy `.env.example` to `.env` in this directory.
3. Enter real keys, passwords, and image references in `.env`.
4. From the repository root, start the deployment with the command that follows.

```sh
docker compose --env-file deploy/local/.env -f deploy/local/compose.reference.yaml up
```

Open `http://localhost:3000` after service readiness. The browser uses same-origin API and media paths.
Only port 3000 binds to host loopback. PostgreSQL, MinIO, API, and speech ports remain internal.

## Startup behavior

The migration service waits for PostgreSQL readiness. Storage initialization creates the private bucket and its scoped credentials.
Account initialization does not create exercises or scores. A fresh library contains no approved media until actual content passes publication review.

The API requires completed initialization and a healthy speech service. The web service requires a ready API.
No fixed sleep substitutes for readiness. Provider credentials do not enter the web environment.

## Restart and data removal

Normal stop and start retain the named volumes. The operator must examine the backup procedure before destructive volume removal.
CAUTION: Do not remove the database or media volumes without explicit approval. Volume removal erases persistent attempts and audio.

No destructive reset command appears in the default startup procedure. Development authentication must refuse startup outside local mode.
Read `docs/runtime-v1.md` for the request deadlines and access rules. Docker execution remains unperformed in this review environment.
