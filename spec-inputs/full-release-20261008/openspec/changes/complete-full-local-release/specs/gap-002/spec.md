## ADDED Requirements

### Requirement: SPEC-002 Public and private transport projections

The API MUST apply the activity and phase allowlists. Before submission, the teacher response contains no key, transcript, count, or target category.

The normative artifacts are:

- `contracts/library-item.schema.json`.
- `contracts/teacher-start-view.schema.json`.
- `contracts/prepare-view.schema.json`.
- `contracts/key-disclosure.schema.json`.
- `docs/interface-contract.md`.

#### Scenario: The declared successful path

- **GIVEN** the exact permitted input and required evidence exist.
- **WHEN** the application applies `SPEC-002`.
- **THEN** A frozen submitted attempt requests its result. The response can show the exact full key under the selected disclosure policy.

#### Scenario: An invalid or unsupported input

- **GIVEN** the input or evidence violates the declared contract.
- **WHEN** the application applies `SPEC-002`.
- **THEN** An unsubmitted attempt or blind review requests a hidden field. The serializer omits it from payloads, errors, and media metadata.

#### Scenario: No genuine acceptance evidence exists

- **GIVEN** no actual test or provider observation supports a release claim.
- **WHEN** an implementer reports completion.
- **THEN** the report distinguishes this written requirement from implementation and observed evidence.
