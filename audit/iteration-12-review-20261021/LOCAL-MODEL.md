# Iteration 12 local observation profile

This is the development observation resource, independent of ordinary application setup. It reuses already installed `qwen3.5:9b` weights. No provider account, purchased credits, weight download or automatic hosted fallback is used. The existing mutation-generation profile remains untouched.

`LOCAL-MODEL-CREATE.json` is the exact local parameter-only definition; `LOCAL-PROFILE.json` is the actual application profile. `RUNTIME-BINDINGS.json` records the base/selected model digests and effective runner parameters. The selected profile has no custom system prompt, uses neutral repetition penalties and disables speculative decoding after a retained MLX cache-offset panic. Existing operation deadlines are unchanged.

On a qualification host with that base model already installed, the local definition can be created with:

```sh
curl --fail --silent --show-error http://127.0.0.1:11434/api/create \
  --header 'Content-Type: application/json' \
  --data-binary @audit/iteration-12-review-20261021/LOCAL-MODEL-CREATE.json
```

The test helper does not install or pull weights. Its native receipts/context and separate MLflow reconciliation remain required. See [Ollama's creation API](https://docs.ollama.com/api/create). Earlier failed model/profile/prompt observations retain their actual status; this definition is no claim of universal linguistic correctness.
