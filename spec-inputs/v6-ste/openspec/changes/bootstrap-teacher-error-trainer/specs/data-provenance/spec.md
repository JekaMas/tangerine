## ADDED Requirements

### Requirement: DATA-01 Source permissions
Each corpus operation MUST have permission for that source and use. The importer MUST obey `domain/corpus-sources.v1.yaml`. Public access MUST NOT count as permission for commercial use, redistribution, or cloud upload.

#### Scenario: DATA-01 Permitted behavior
- **GIVEN** A source has the required license and use approvals.
- **WHEN** The importer acquires its release.
- **THEN** The record retains the release hash, attribution, and permitted uses.

#### Scenario: DATA-01 Boundary behavior
- **GIVEN** An intended use exceeds a noncommercial license.
- **WHEN** The importer has no separate written permission.
- **THEN** The importer blocks that use.

### Requirement: DATA-02 Faithful import
The importer MUST retain raw files, source offsets, annotator identities, and score scales. Normalized records MUST link their exact origin. Automatic alignment MUST NOT become a claim of manual observation.

#### Scenario: DATA-02 Permitted behavior
- **GIVEN** A parser reads a permitted M2 release.
- **WHEN** It makes a normalized record.
- **THEN** The record preserves token spans, correction alternatives, and annotator identity.

#### Scenario: DATA-02 Boundary behavior
- **GIVEN** A source score lacks an observed-phone label.
- **WHEN** The importer processes that score.
- **THEN** The importer does not invent the substituted phone.

### Requirement: DATA-03 Evidence and consent
Every evidence record MUST identify its source, subjects, and asset hash. Personal voice data MUST have permission for the intended operation. The application MUST NOT create consent or reviewer identities.

#### Scenario: DATA-03 Permitted behavior
- **GIVEN** A reviewer submits an authorized observation.
- **WHEN** The API stores the evidence.
- **THEN** The record links the reviewer, exact case, and final audio.

#### Scenario: DATA-03 Boundary behavior
- **GIVEN** A file has no required permission for provider upload.
- **WHEN** An operator requests cloud analysis.
- **THEN** The request stops before the upload.
