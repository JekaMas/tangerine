# Local deployment

From the project root, run `sh scripts/tangerine start`; Docker with Compose v2.20 or newer is the application prerequisite. The helper builds the supplied sources and initializes durable internal credentials, PostgreSQL migrations and private MinIO automatically. Open http://localhost:3000 without login. The empty Library is the actual initial database result.

Only web port 3000 binds to host loopback. All storage and internal-service ports remain unpublished. Optional operator provider settings belong in root `.env`; do not add manual database/media/account secrets. Generated infrastructure secrets belong to ignored `data/config/runtime.env`. Retain it together with the database/media Docker volumes. `stop` retains both; `start` does not rotate secrets, replace existing rows or download models. Do not use `down --volumes` on an installation you intend to keep.

Use `sh scripts/tangerine status` for actual Compose state and `sh scripts/tangerine logs` for redacted diagnostic output. First build needs access to locked third-party build dependencies. Dockerfiles contain pinned upstream versions/digests; historical image receipts are in images.lock.json and current iteration receipts in audit/iteration-1-local-foundation-20261010.

The API release label currently identifies the foundation increment, not full-product completion. Provider configuration readiness records key presence only, with no inference, entitlement or synthesis claim. Real FFmpeg/ffprobe availability is the speech foundation readiness signal. Provider/model setup and explicit backup/restore/switch are available through scripts/tangerine; see the Recovery page and active recovery runtime specification.
