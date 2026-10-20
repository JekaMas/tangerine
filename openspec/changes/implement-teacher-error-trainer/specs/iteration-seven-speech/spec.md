## ADDED Requirements

### Requirement: I7-01 Frozen literal dialogue plan

The application SHALL compile ordered literal turns with stable speakers and configured voice locales, reject unknown speakers and leave controlled acoustic operations to iteration8. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-01 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-01 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-02 Finite audio and safe listener projection

The application SHALL assemble finite PCM16 mono24kHz and exact samples, exclude answer keys from listener summaries and avoid exposing incomplete audio. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-02 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-02 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-03 Selected profiles without fallback

The application SHALL resolve the selected registered or extension profile; missing and malformed configuration SHALL fail without substitution. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-03 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-03 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-04 Complete derived answer key

The application SHALL preserve all planned units/corrections/explanations and empty keys, use the frozen taxonomy and actual containing-turn intervals, and invent no accent or character-based timing. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-04 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-04 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-05 Durable render finalization

The application SHALL persist ordered completed pieces, final audio and rendered case/key atomically; missing mutations or wrong next attempts SHALL not dispatch. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-05 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-05 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-06 Immutable result and explicit resume

The application SHALL resume incomplete pieces with frozen inputs, trust completed stored output after restart and preserve immutable failed-result replay; conflicting keys and cancelled operations SHALL not synthesize. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-06 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-06 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-07 Stored playback and byte ranges

The application SHALL play stored WAV repeatedly with exact byte ranges, no new synthesis and actionable missing/unready behavior. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-07 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-07 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-08 Native speech evidence and ownership

The application SHALL retain actual piece context/receipts and original frozen profile on retry; competing owners and mismatched action identity SHALL not dispatch. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-08 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-08 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-09 Public readback and completed child recovery

The application SHALL project public availability/counters without keys and recover completed child output after lost parent linkage; partial audio and invalid paging SHALL not be presented as ready. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-09 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-09 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-10 Reachable render and playback routes

The application SHALL wire actual preparation render/playback into the HTTP mux and retain its local private access boundary; unknown actions SHALL not dispatch. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-10 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-10 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-11 Actual local synthesis and paid-call exclusion

The application SHALL generate actual local Kokoro/eSpeak output with storage/receipt evidence and refuse unknown voices or paid profiles before provider dispatch. Hosted qualification is separate. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-11 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-11 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-12 Actual Qwen saved voice paths

The application SHALL synthesize locally through actual CustomVoice and saved Base conditioning with native stored receipts; absent conditioning or unsupported operations SHALL fail without fallback. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-12 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-12 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-13 Private speech service admission

The application SHALL report actual engine/model state and admit private requests; unauthenticated or malformed requests SHALL not become successful synthesis. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-13 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-13 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-14 Foreground speech child lifetime

The application SHALL reap actual successful/failed workers and kill the actual process group on deadline or client disconnect; no detached synthesis remains. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-14 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-14 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-15 WAV admission and assembly

The application SHALL admit newly produced finite mono PCM16 24kHz once and assemble exact samples/pauses; invalid or all-silent output SHALL fail. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-15 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-15 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-16 Included-only speech dispatch

The application SHALL permit local or explicitly included/free profiles with overage disabled; metered, S0 and billed OpenAI TTS SHALL be refused. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-16 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-16 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-17 Complete text splitting

The application SHALL preserve complete Unicode surface text, voice and speaker across word-boundary splits; indivisible over-capacity input and unavailable voices SHALL fail. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-17 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-17 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-18 Typed hosted request adaptation

The application SHALL escape literal XML and emit the declared hosted model/voice payload; absent credentials and unsupported operations SHALL fail. Controlled fixtures establish protocol behavior only. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-18 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-18 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-19 Trusted setup and honest quality

The application SHALL reuse accepted model manifests without a network/hash audit and report mechanical audio warnings without invented accents; missing/incomplete setup SHALL be actionable. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-19 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-19 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-20 Measured advisory quality

The application SHALL record measurable loudness/peak/silence and exact planned pauses; short/unmeasurable output and quality issues SHALL be explicit warnings, not publication gates. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-20 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-20 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-21 Native browser playback and recovery

The application SHALL render actually stored preparations and play actual local audio in Chrome, recover list/playback through Refresh after test-owned database/media failure, and preserve all data. No DOM/network substitution is permitted. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-21 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-21 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-22 Actual local preprocessing capture

The application SHALL retain actual framed tokenizer output and resolved decoder inputs with one native invocation; preserve original results/exceptions and restore observers without fabricating a call. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-22 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-22 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-23 Saved voice setup lifecycle

The application SHALL persist admitted reference audio/text and clone conditioning, reuse an accepted voice without another inference, and reject changed identities or missing reference before inference. Learned model output is an explicit boundary fixture. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-23 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-23 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-24 Explicit resumable model acquisition

The application SHALL admit new downloaded bytes once, resume partial Range responses or restart when Range is ignored, and retain no accepted file for wrong ranges or hashes. Ordinary inference reuses accepted manifests offline. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-24 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-24 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-25 Single audio admission and advisory failures

The application SHALL normalize audio as a transformation, admit newly generated output once, reject silence and preserve usable output when advisory loudness measurement times out. Runtime executable rehashing is unnecessary; retain method/version and build identity. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-25 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-25 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

### Requirement: I7-26 Explicit voice and assessment variety

The application SHALL preserve explicitly supplied speaker voices independently of assessment variety, skip unused default-voice requirements, and reject a wrong speaker count or a missing required default without silent substitution. Literal tests and independent expectations SHALL be retained in audit/iteration-7-speech-20261011/CASES.json. These cases do not establish hosted account entitlement, perceived accent fidelity or later acoustic/listening/scoring features.

#### Scenario: I7-26 packet 1

- **WHEN** the first positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold

#### Scenario: I7-26 packet 2

- **WHEN** the second distinct positive or negative literal packet executes
- **THEN** its independently declared state, bytes, error or dispatch count SHALL hold
