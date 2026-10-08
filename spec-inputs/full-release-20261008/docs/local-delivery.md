# Local delivery contract

The operator needs Docker with Compose, a POSIX shell, and a browser.
The publisher supplies all application images, dependency locks, manifests, migrations, and the launcher.
The operator supplies only provider credentials and the explicit intended-use configuration.
The operator does not install Go, Node, PostgreSQL, MinIO, or Python on the host.

## First start

The launcher checks that Docker and Compose respond before it changes data.
It reads the supplied release manifest and the actual image digest file.
It rejects absent, floating, unsupported-architecture, or conflicting image references.
It creates `.state` with mode 0700 and new internal random secrets with mode 0600.
Each secret uses at least 32 bytes from the operating system's cryptographic random source.
Do not print secret values, store them in images, or send them to the browser.
Do not regenerate existing secrets during an ordinary restart.
The launcher starts the real database and private object store with persistent volumes.
The migration container waits for database readiness, checks stored migration checksums, and applies only supported forward migrations.
The storage initialization container creates only the required private bucket and internal access configuration.
The API starts after both initialization steps finish successfully.
The web proxy starts after API readiness. No sleep-based readiness assumptions are permitted.

An empty exercise bank is displayed as empty. Do not seed fabricated exercises or reviewer approvals.
Missing provider credentials disable only the related provider action and give an explicit configuration error.
A full-release acceptance report still requires actual content, grants, and qualification evidence.
Local startup is not an air-gapped LLM or TTS implementation. Provider calls require network access.

## Networking and secrets

Bind only `127.0.0.1:3000` on the host. Do not expose database, MinIO, API, or speech ports by default.
The browser uses same-origin `/api/v1/` requests. It never resolves Docker hostnames.
The web proxy supplies internal service authentication without putting the token in public JavaScript.
`/internal/v1/` routes are not proxied to the browser.
Validate Host and Origin. Reject cross-origin state changes, unsafe content types, and DNS-rebinding hostnames.
Do not enable permissive CORS. Permit only the declared localhost origin and an explicit configured loopback variant.
Use no user accounts or role-permission platform.

API/provider secrets mount read-only only into services that need them.
MinIO and database internal credentials are distinct from cloud keys.
The browser sees only whether a credential exists. It cannot read the stored value.
No raw source or teacher text enters general logs. Use IDs, statuses, durations, and safe error codes.
Reject arbitrary outbound URLs. Private connectors use exact owner-documented allowlisted hosts.

## Restart and failure

Ordinary stop/start retains all persistent volumes and internal secret files.
A failed migration does not start the API in a partially compatible state.
A changed migration checksum stops startup with the exact safe migration ID.
A missing image or application binary is an error. It is not a reason to start mock behavior.
An interrupted paid operation remains recoverable through its persisted state and lease protocol.
The launcher never erases volumes automatically to fix a startup problem.

## Internal secret rotation

Rotation is an explicit maintenance operation with a preview and backup recommendation.
Stop dependent writers and verify that no paid operation is active.
Create the new secret in a separate protected file.
Update the corresponding real dependency credential, restart its dependents, and confirm local readiness.
Only then replace the old active secret reference. Keep rollback material only as permitted by the approved rotation plan.
If a step fails, preserve the old working reference or restore it explicitly. Do not claim successful rotation from file generation alone.

## Release artifacts

The release manifest names actual image digests for linux/amd64 and linux/arm64, source commit, SBOMs, locks, and migration checksums.
It also freezes prompts, schemas, taxonomy, alias policy, scoring, measurement methods, source adapters, and capability qualification IDs.
Image digest placeholders cannot satisfy this manifest.
Every architecture needs real startup, browser, persistence, restore, and provider-path qualification.
An x86 inspection is not an ARM execution result.
The reference Compose file describes this topology. This specification package does not contain built application images.
