# Installed local text generation

The iteration34 reference setup uses the existing
`tangerine-qwen35-9b-review-nospec-20261021` Ollama model for clean text and
mutation generation. It needs no API key or usage purchase. The observed model
digest is `f53e68038d114252fc8c888a7dbd2f8e0fade74c0bea6649bb467ed3430ff9bd`.
This is a measured local setup, not an automatic model download or a claim that
all topics and 122 categories have been qualified on this model.

Add an explicit generation profile in Settings and select it for
`stage_profiles.case_generation` in a new configuration:

```json
{
  "id": "local-generation-qwen9b",
  "provider": "local_responses",
  "model": "tangerine-qwen35-9b-review-nospec-20261021",
  "endpoint": "http://ollama:11434/v1/responses",
  "reasoning_effort": "none",
  "temperature": 0.2,
  "max_output_tokens": 8000,
  "context_budget_tokens": 65536,
  "adapter_version": "local-responses-v1",
  "credential_ref": "local-none",
  "store": false,
  "stream": false,
  "tools": [],
  "roles": ["case_generation"],
  "auth_method": "local_none",
  "billing_mode": "local",
  "structured_output": false
}
```

The endpoint above is the Docker-to-host alias used in the actual test. A host
API process can use its supported loopback endpoint instead. Answer checking
keeps its separately selected profile. Changes apply to new preparations;
resuming saved work keeps its frozen configuration and prompt bundle.

Use plain output for this 64K profile. The full decoder-schema alternative was
rejected before mutation dispatch by its conservative byte budget. The complete
output contract still appears in the ordinary owned prompt, and native admission
remains unchanged. No ordinary benchmark or Lab run is required to use an exercise.

The actual positive generation took140.4 s including one MLX cache-error retry;
the zero-error control took61.2 s. The repaired mechanical correction projection
was subsequently tested with those retained replies through real PostgreSQL,
private MinIO and the existing preparation/finalization owners. This replay made
no new inference call and does not supply a new generation-time measurement.

The finite population has two requested mutations and six distinct correct
control types across two requests. Its final system projection passes their
independent literal checks. The model repeated a requested once-only phrase;
that instruction-following deviation remains in the report. Actual local runtime
errors and larger-model timeouts also remain recorded. Failed attempts preserve
clean text and receipts for explicit recovery, without switching providers.

See the [comparison, findings and evidence](../audit/iteration-34-local-generation-20261027/REPORT.md).
