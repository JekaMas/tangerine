# Provider setup and development evidence

Run `sh scripts/tangerine start`, then open Settings at `http://localhost:3000/settings`.
ChatGPT uses Tangerine's own documented plan authorization. Continue with ChatGPT,
finish the `127.0.0.1:3000/auth/callback`, and disable credit use after plan limits
for Tangerine in ChatGPT Usage settings. Confirm that exclusion in Settings,
select the registration and list its actual models, then choose a returned model.
A consent page alone does not establish a usable local connection. Missing scope,
unconfirmed credit exclusion, expired/revoked grants and unavailable usage remain
visible states. Reconnect or retry explicitly; no other account or billed key is
selected automatically.

Settings also retains complete model profiles and explicit stage overrides.
Advanced configuration saves with revision and idempotency headers and reads back
the complete safe effective configuration. Secrets remain environment references
or protected local grant files. The default DeepSeek/OpenAI API profiles retain
unknown billing and cannot execute merely because a key exists. A deliberately
configured local Responses profile or independently confirmed free/included
profile is required for those routes. Ordinary readiness checks configuration;
they do not call an LLM or prove hosted entitlement/model quality.

Protected grants live in the API-only provider-credentials volume, outside ordinary
document exports/backups. Safe account metadata and actual model catalogue bytes
have native durable lineage. Disconnect removes the local secret and reports when
remote revocation could not be confirmed. Restoring data without its original
installation/credential volume requires reconnecting the account. The native
repository serializes rotating-grant and identity transitions across API and CLI
processes. A late model response cannot restore a disconnected registration.
Actual token scope is rechecked even if a previous metadata write failed.

The internal `tangerine provider` command invokes the same `Server.InvokeLLM`
owner used by subsequent trainer pipelines. Its JSON request has operation,
stage, optional phase, typed input and explicit context components. Optional
`trace_enabled` and `capture_content` booleans form a frozen development overlay;
they do not change ordinary workspace capture settings. Final request bytes,
raw framed response, binding, full context and every attempted-call receipt are
saved before a result is usable. Successful replay/readback makes no new call and checks the saved completed
operation before obtaining or refreshing credentials.
No secret is accepted in that command payload.

Start the optional Lab through `sh scripts/tangerine lab`. Native diagnostic
packets can be explicitly synchronized through the existing SDK helper. Content
capture is opt-in. The application sanitizes a separate export copy using its
ephemeral credential values, including values embedded inside wire-text strings.
The original private bytes remain exact; original and copy hashes and redaction
reasons remain distinct. The credential set itself is never persisted in a packet.
Repeated diagnostics reuse the saved immutable copy without another model call.
Enabled trace export uses the actual receipt interval/trace/span identities,
sends one bounded OTLP attempt and reports unexported state without discarding
native evidence. Artifact readback and actual span readback are distinct checks.
Exporter `provider_calls: 0` means the exporter invokes no model; it does not
mean the original native provider execution made zero transport attempts.

The current native protocol acceptance uses explicit test-owned hosted-provider
substitutions with real PostgreSQL, MinIO, browser and MLflow owners. It establishes
transport/persistence behavior, not actual hosted inference or linguistic quality.
The audit records live authorization/network witnesses separately. New trainer,
speech and semantic-quality iterations retain their full existing obligations.
