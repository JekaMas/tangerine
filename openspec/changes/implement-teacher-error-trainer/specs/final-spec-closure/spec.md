## ADDED Requirements

### Requirement: CLOSE-01 Persistable existing-role key repair

The existing LLM adjudication role SHALL use the supplied clean/surface text, mutation manifest and frozen answer to return the complete key-repair-proposal when a key/rubric defect needs a new version. The server SHALL materialize units/options/rationale propositions, total correspondence and supported revised decisions under key-repair-projection.md without changing the heard audio or inventing observations. A supplied complete new-key decision set avoids another mapper call; otherwise only the conditional repaired-key mapping branch uses that existing role. Explanation-only repair SHALL preserve supported primary statistics. No corpus/human review/new service SHALL be required.

#### Scenario: CLOSE-01 Omitted second error

- **GIVEN** clean She works here. They are ready., surface She work here. They is ready., an old key listing only work and an answer repairing both verbs
- **WHEN** existing adjudication returns complete proposed units with same and added correspondence on the unchanged audio
- **THEN** the appended repaired key/result have G=GC=TP=2,CQ=2,primary100 and the original key/result/mutation history remain readable

#### Scenario: CLOSE-01 Rationale-only repair or incomplete proposal

- **GIVEN** a saved primary100 and a reason-only rubric dispute, or resolution=key_defect with no substantive key_repair
- **WHEN** reconsideration processes the response
- **THEN** a complete rationale repair changes only its optional component unless primary evidence changes; a reason string alone cannot create a revised key and retains the old result with explicit unresolved repair diagnostics

### Requirement: CLOSE-02 Durable preparation and explicit recovery

The application SHALL persist preparation-state and its complete private preparation-settings asset before dispatch, checkpoint completed canonical/mutation/render outputs atomically with their actual receipts, and expose saved readback using the existing operations plus the local preparation listing. Resume SHALL identify the exact saved preparation and reuse its original bindings/completed artifacts under preparation-persistence.md. GET/readback SHALL dispatch no inference. A late prior operation SHALL NOT overwrite a selected checkpoint. No background queue SHALL be introduced.

#### Scenario: CLOSE-02 Resume after settings change

- **GIVEN** p1 saved clean c1 and M1/B1/S1, mutation failed, the process restarted and active settings are now M2/B2/S2
- **WHEN** an explicit generate continuation selects preparation_id=p1
- **THEN** it reads c1 and M1/B1/S1, calls only the incomplete mutation phase and later renders with S1; new generation with null preparation_id creates p2 using M2/B2/S2

#### Scenario: CLOSE-02 Response loss and late writer

- **GIVEN** p1 has committed mutation assets or verified final audio but its response was lost, and a prior expired operation later returns
- **WHEN** saved readback/idempotent explicit continuation occurs
- **THEN** committed assets are returned or their verified bytes linked without repeating the completed paid phase; the expired operation is diagnostic and cannot replace p1 checkpoints

### Requirement: CLOSE-03 Generate only self-contained contextual exercises

Ordinary generation SHALL produce self-contained audible text under self-contained-generation.md. Every decisive contextual fact SHALL be in the surface dialogue or already disclosed general task settings; private generator assumptions/external stories SHALL NOT determine a scored mistake. All 122 categories SHALL remain available using suitable audible instances. No extra briefing/review gate SHALL be added. A fixed clean script with no valid requested placement SHALL retain its existing failure/new-text path rather than silently remove targets.

#### Scenario: CLOSE-03 Audible address preference

- **GIVEN** the dialogue audibly states I am Dr Lee; please call me Dr Lee before a later Good morning, mate turn
- **WHEN** the requested contextual mutation is generated and assessed
- **THEN** its rationale cites those actual audible turns, with no private context requirement and no category removed

#### Scenario: CLOSE-03 Hidden preference cannot create an error

- **GIVEN** only Good morning, mate is audible and the generator privately assumed the Dr Lee preference
- **WHEN** generation or answer matching considers that private assumption
- **THEN** that mistake instance is not generated/scored on the hidden assumption; a self-contained instance is selected within the requested category or the existing explicit new-text condition is returned

### Requirement: CLOSE-04 Concrete fixtures for every declared property and case

Every declared property and positive/negative case SHALL bind to a concrete fixture and independently stated expected inputs/state/artifacts/counts/fraction/failure in domain/verification-fixtures.v1.json. Category fixtures SHALL parameterize every one of the 122 preserved recipes, and numerical fixtures SHALL preserve every one of the 42 equations. Fixture origin, actual semantic/native/provider evidence limits and missing future observations SHALL remain explicit. Generic labels, assertion mirroring and structural counts SHALL NOT substitute for designed cases or actual passing behavior. Existing observation receipts SHALL retain their original scope and explicitly changed contracts SHALL invalidate only affected current evidence.

#### Scenario: CLOSE-04 Exact voice and arithmetic fixtures

- **GIVEN** five en-US roles and local voice order af_heart/am_adam, plus a stipulated one-error correct detection and classification/two-of-five-credit repair packet
- **WHEN** concrete expected results are bound to their cases
- **THEN** assignments are af_heart,am_adam,af_heart,am_adam,af_heart with shared-voice disclosure and primary score80; missing or different expected assignments/fraction are identifiable counterexamples

#### Scenario: CLOSE-04 No generic or fabricated passing plans

- **GIVEN** the complete current property/case graph and no current model/audio/application run for the new fixtures
- **WHEN** fixture and evidence coverage are reported
- **THEN** every identity resolves a positive/negative literal fixture and oracle while unperformed observations remain unexecuted; adding fixture records cannot fabricate a corpus, provider call, audio or passing test
