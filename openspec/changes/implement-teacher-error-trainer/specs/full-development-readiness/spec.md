## ADDED Requirements

### Requirement: READY-01 Full scope has no product deferral
The complete product SHALL preserve all accepted features, 122 categories/recipes, 42 original equations and eleven original full-source scopes. Development iterations MAY repair code, models, prompts and tests; they SHALL NOT turn optional activation or an unavailable dependency into omitted product implementation or complete acceptance. The feature/service/data map in full-development-readiness.md SHALL govern readiness claims. Account registration, static checks and ordinary exercise success SHALL NOT establish all-feature operation.

#### Scenario: READY-01 A starter flow does not stand for full acceptance
- **GIVEN** successful ordinary text/audio/answer use but unobserved acoustic targets or unavailable original source bytes
- **WHEN** full-product readiness is reported
- **THEN** those exact feature dependencies remain open and all scope identities remain retained.

#### Scenario: READY-01 Development repairs preserve product scope
- **GIVEN** a provider limit or an unsupported target during development
- **WHEN** the implementation is revised
- **THEN** saved artifacts and requested scope remain; no MVP feature omission or silent purchased fallback is recorded as completion.

### Requirement: READY-02 Controlled local phonemes preserve actual intent and evidence
The kokoro-phonemes-v1 configured extension SHALL implement the vocabulary-scoped conversion, target-local substitution, pre-call token-boundary 510-character chunking, saved actual output and prediction/measurement distinction in full-development-readiness.md. The original plain-text profile SHALL remain unchanged. Unsupported symbols/overlong indivisible targets SHALL preserve the request/key and fail that operation without dropped phones or invented observations. Recorded contrasts MAY use our generated recordings and SHALL NOT require an external corpus before ordinary generation.

#### Scenario: READY-02 A phone target affects one occurrence
- **GIVEN** the surface words three then three and a phoneme operation on the second three
- **WHEN** the controlled local adapter compiles and renders sɹiː for that target
- **THEN** only that occurrence receives those phones and the actual recording is saved; intent alone gives no observed consonant label.

#### Scenario: READY-02 Unsupported or oversized targets are not truncated
- **GIVEN** an unsupported IPA symbol or an indivisible compiled target longer than 510 characters
- **WHEN** the local renderer prepares inference
- **THEN** the request/key remain saved, that inference is not dispatched and no success/realization is claimed.

### Requirement: READY-03 Voice locale and model transport are independent bindings
English voice locales SHALL resolve against the frozen configured voice catalogue independently of en-US/en-GB assessment defaults. The renderer SHALL use the selected model's documented transport and supported settings. ElevenLabs v4/v3 SHALL use the specified text-to-dialogue route and its target-safe reliable request size; other supported single-voice models SHALL use their explicit text-to-speech route. A model flag or accepted locale string SHALL NOT manufacture a compatible voice, transport or entitlement.

#### Scenario: READY-03 A configured English accent uses its actual locale
- **GIVEN** a configured en-IN voice with an en-US task variety policy
- **WHEN** it is selected for English audio
- **THEN** the voice locale is retained, the task variety policy is preserved and the accent is not scored as an error.

#### Scenario: READY-03 Dialogue models receive dialogue payloads
- **GIVEN** a selected available eleven_v4 model and ordered target-safe text pieces
- **WHEN** audio is generated
- **THEN** text-to-dialogue receives inputs text/voice_id plus supported fields; TTS voice_settings and unsupported transport claims are absent.

### Requirement: READY-04 Independent ASR and uncertain measurements require no humans
The local faster-whisper method SHALL use the frozen local model, CPU/int8 parameters, unconditioned complete hypothesis and raw timestamps defined in full-development-readiness.md. It SHALL NOT receive reference/key/answer context or substitute for native phone assessment. Unknown acoustic observations SHALL use not_measurable/null/reason; no human_required measurement status or human-review gate SHALL be produced. ChatGPT-plan text access SHALL NOT be claimed to provide audio-input assessment.

#### Scenario: READY-04 ASR preserves an independent mistaken hypothesis
- **GIVEN** actual audio and a separate reference text
- **WHEN** the local ASR returns a different word
- **THEN** its raw word is retained, WER reflects the difference and no reference prompt or phone score is invented.

#### Scenario: READY-04 Unknown acoustic evidence stays unknown
- **GIVEN** uncertain rhythm or a missing selected pronunciation diagnostic
- **WHEN** results are stored
- **THEN** the missing measurement has null value and explicit reason without a human queue or fabricated acoustic perfection.
