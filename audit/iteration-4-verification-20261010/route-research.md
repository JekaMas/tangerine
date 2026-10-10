# Current provider route cross-check

Refuted hypothesis: DeepSeek might require Chat Completions rather than the configured Responses endpoint. Current primary documentation defines POST /responses with base https://api.deepseek.com, stateless full input, compatible OpenAI response objects, terminal SSE events and nullable usage. No route change is needed. Documentation is not actual account admission, subscription-covered billing or provider-call evidence. No authenticated call was made.

Sources: [DeepSeek Responses API](https://api-docs.deepseek.com/api/create-response/), [compatibility and streaming guide](https://api-docs.deepseek.com/guides/responses_api/). Read on2026-10-10.
