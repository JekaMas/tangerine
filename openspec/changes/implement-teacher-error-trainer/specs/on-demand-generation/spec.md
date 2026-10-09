## ADDED Requirements

### Requirement: DEMAND-01 Request-driven LLM text and mutation generation
Ordinary use SHALL follow user request -> configured LLM clean text -> configured LLM mutations -> generated/stored audio -> listener answer -> LLM comparison/comments and exact formula-based scores. No pregenerated corpus, seed library, all-category batch or full benchmark SHALL be required or automatically created at startup. The existing evaluation projection SHALL supply the same saved original/surface text and mutation units; found/missed/false-positive/correction/optional-explanation feedback SHALL be grounded in them. Local validation/replay/arithmetic SHALL NOT substitute a recipe-only content generator. Stored replay and exact saved checkpoint resume remain supported, and all optional source/import/benchmark scopes remain preserved.

#### Scenario: DEMAND-01 First request works with an empty corpus and library
- **GIVEN** an empty exercise library and no acquired corpus, with configured LLM and speech resources
- **WHEN** the user requests a new two-speaker exercise
- **THEN** startup makes zero generation calls, the request invokes the clean and mutation LLM phases before speech, and a failed mutation does not trigger a bank/recipe fallback or render a fake successful exercise.

#### Scenario: DEMAND-01 Original text and mutations ground findings and misses
- **GIVEN** clean text She likes coffee. and I have a red car., mutated text She like coffee. and I have red car., and a response identifying/correcting only the first error
- **WHEN** the LLM checks the same saved exercise and native arithmetic computes scores
- **THEN** u1 is found, u2 is missed, TP=1,FN=1,FP=0,precision=1,recall=1/2,F1=2/3; feedback explains both, absent optional explanation has no omission penalty, and unrelated exercise versions never replace the saved originals/key.
