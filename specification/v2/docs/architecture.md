# Local architecture and responsibilities

One source project runs a browser UI, a Go API, a Python speech worker, PostgreSQL and private MinIO through one Compose launcher. Keep this existing component topology rather than introduce a cloud platform or rewrite persistence during a specification audit. MinIO is internal storage hidden by the helper; ordinary users configure only provider keys and optional corpus paths. No distributed queue, login, tenant, public SDK, hosted service or access-role framework is required.

The UI provides preparation, a case library, listening/answering, results, retry, LLM case review, LLM dispute resolution, corpus import/status, settings, benchmark reports and backup/restore. Author, teacher and review describe activities in the same local workspace. There are no separate human reviewers.

The API freezes submitted answers before LLM calls, keeps immutable case/key/audio versions, normalizes model claims and decisions, computes all exact metrics and returns saved results. It owns local operation identity, timestamps, revisions and storage links. The LLM interprets answers and semantics; it does not calculate authoritative fractions, synthesize missing answers or grant source rights.

The speech worker renders actual synthetic WAV, runs available ASR/assessment/acoustic measurements and returns versioned observations. Acoustic inference and measurements retain their modality and confidence. A text-only LLM cannot claim it heard a recording. Missing advisory providers affect those observations, not startup or unrelated scoring.

A normal answer uses blind extraction, mapping and deterministic scoring followed by feedback. Mapping audit is optional. A case uses simple topic/speaker/word-length input, saved clean LLM text, a separate novel mutation phase with its answer key, then local or service rendering and stored playback. The LLM compares the listener answer with that mutation list and supplies recommendations. Case review and speech measurements are optional diagnostics; failed synthesis yields no playable fake audio. A dispute uses LLM adjudication and appends a corrected result/key version when supported. All functions inherit a configurable default LLM profile, with optional stage overrides.

Corpora use one generic lossless intake and native versioned semantic converters. All eleven full-source entries remain visible. Store actual complete files/records separately from derived excerpts. Unknown columns and labels remain raw; conversion can continue for understood records without discarding unknown data. No full-corpus or benchmark milestone blocks a fresh local installation or independently generated case.

Optional LLM Lab adds one local MLflow container/profile with SQLite and artifact volume when explicitly opened. Existing Go/Python owners emit native traces and experiment outputs; prompt/context bundles are saved locally, so MLflow is never a live dependency for learner requests. See llm-lab.md.
