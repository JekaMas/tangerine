# Iteration 12 local observation profiles

The active application observation profile is LOCAL-PROFILE.json, using the already installed gpt-oss:20b. RUNTIME-BINDINGS.json records the exact model digest and runner parameters. No account, hosted call, purchased credits or model-weight download is required for these observations. The test helper never silently installs models.

The Qwen profile definitions are retained experimental evidence. LOCAL-MODEL-CREATE.json creates an owned parameter-only variant from already installed qwen3.5:9b weights; its selected digest is in the retained runtime/observation records. MLX cache-offset panics still occurred after disabling speculative decoding, so the Qwen experiment is not the active qualification profile and no engine fix is claimed. Existing base/mutation profiles remain untouched.

A qualification host that already has the Qwen base weights can reproduce that experimental variant with:

```sh
curl --fail --silent --show-error http://127.0.0.1:11434/api/create \
  --header 'Content-Type: application/json' \
  --data-binary @audit/iteration-12-review-20261021/LOCAL-MODEL-CREATE.json
```

See [Ollama's creation API](https://docs.ollama.com/api/create). Actual native dispatch/context/receipt/MLflow observations, including failures, remain separate from any universal linguistic-quality claim. Existing operation deadlines are unchanged.
