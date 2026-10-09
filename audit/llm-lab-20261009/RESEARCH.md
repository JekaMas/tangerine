# Prompt/context/LLM-quality tooling selection

Research date:2026-10-09. These are primary documentation observations and an engineering selection, not an executed comparison or integration.

| Option | Relevant documented capabilities | Fit for Tangerine |
|---|---|---|
| MLflow | Prompt registry/version diff, experiments/evaluation, trace UI, local SQLite/artifacts, OTLP/HTTP ingestion, Apache-2.0 offering | Selected: one optional local service can cover the requested management/debug/comparison surface while using existing native adapters. |
| Langfuse | Integrated prompt/tracing/evaluation workspace; self-hosting includes web/worker, PostgreSQL, ClickHouse, Redis/Valkey and blob storage | Useful alternative; more persistent service/storage dependencies than this local project needs. |
| Promptfoo | File-based prompt/provider/test configurations, derived assertions/metrics, local SQLite trace receiver and result UI | Good focused evaluation alternative. Its file-config model would still require a prompt/context activation and ordinary-call management layer for this project. Avoid adding a second required framework. |

Evidence:

- [MLflow registry](https://www.mlflow.org/genai/prompt-registry/): Apache-2.0 self-hosted option, prompt/version management.
- [Editing prompts](https://mlflow.org/docs/latest/genai/prompt-registry/create-and-edit-prompts/), [aliases](https://mlflow.org/docs/latest/genai/prompt-registry/manage-prompt-lifecycles-with-aliases/), [application use](https://mlflow.org/docs/latest/genai/prompt-registry/use-prompts-in-apps/): immutable template versions and explicit loading.
- [MLflow server](https://mlflow.org/docs/latest/self-hosting/architecture/tracking-server/): SQLite metadata, local artifact proxy and container host/port configuration.
- [OTLP ingestion](https://mlflow.org/docs/latest/genai/tracing/opentelemetry/ingest): HTTP endpoint and experiment header, support for Go/native OpenTelemetry clients. OTLP/gRPC is not the selected interface.
- [Evaluation overview](https://mlflow.org/docs/latest/genai/eval-monitor/), [scorers](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/), [datasets](https://mlflow.org/docs/latest/genai/datasets/): evaluation primitives, custom scorers and experiment/result surfaces. Tangerine's expectations retain their actual authored/native/LLM basis; upstream human-feedback features are not requirements.
- [Usage tracking](https://mlflow.org/docs/latest/community/usage-tracking/): MLFLOW_DISABLE_TELEMETRY=true disables server/SDK/UI telemetry when inherited by those processes.
- [Release3.17.0](https://github.com/mlflow/mlflow/releases/tag/v3.17.0), [PyPI3.17.0](https://pypi.org/project/mlflow/3.17.0/): current selected release, published2026-10-07. Source-package SHA-2567c1566b1aca61aec58520516df085948874c7956798dd6ae8ca17560ce06b089 is published metadata, not a downloaded/verified artifact here.
- [Langfuse self-hosting](https://langfuse.com/self-hosting): current deployment dependencies.
- [Promptfoo configuration](https://www.promptfoo.dev/docs/configuration/reference/), [traces](https://www.promptfoo.dev/docs/tracing/), [self-hosting](https://www.promptfoo.dev/docs/usage/self-hosting/): local configuration/evaluation/trace persistence. Provider-specific credential-shaped redaction is not sufficient to promise arbitrary text-secret stripping.

The minimal package/port/trace integration is specified, but image architecture/dependency locks, actual SDK server behavior, local resources/latency and provider quality remain future build/run observations. Registry context-policy JSON, frozen local activation, production-owner replay and the22diagnostic formulas are Tangerine integration decisions. No claim that MLflow natively supplies an automatic context assembler is made.

No tools were installed, Docker was not run, no SDK/provider calls or benchmarks were executed, and no credentials were read or changed. Failed web openings of guessed singular lifecycle/evaluation URLs and the release LICENSE file were not used as evidence; working official plural lifecycle/evaluation pages and the documented Apache-2.0 offering provide the cited evidence instead.
