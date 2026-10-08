# full-source-coverage specification

## ADDED Requirements

### Requirement: FULL-01 Require full source releases

The system SHALL retain the original eight-profile provenance and all eleven separately bound entries in specification/v2/domain/corpus-sources.v1.yaml. Every obtainable authorized source SHALL have its full named release, all partitions, files, labels and populations inventoried. A sample, latest unpinned mirror or cleaned derivative SHALL NOT satisfy full-release acceptance. Historical required:false SHALL NOT excuse omission from this planning scope. Unavailable research/vendor data SHALL retain blocked acquisition status and prevent an all-sources-acquired claim.

#### Scenario: FULL-01 Complete supported behavior

- **GIVEN** Compare the eleven exact active source IDs and release manifests against the reviewed source inventory.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** All eleven inventories name exact release components, permissions, acquired counts and missing data.

#### Scenario: FULL-01 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A five-source subset, ten-file sample, omitted partition or substituted derivative is rejected as full coverage.

### Requirement: FULL-02 Verify release manifests and rights

The importer SHALL freeze upstream release/version, archive and every raw-file SHA-256, licence/attribution/permission hashes, parser/mapping versions, record/label/partition counts, exclusions and duplicate groups. It SHALL reconcile expected and observed counts with documented reasons. Actual source terms for each use SHALL be retained, without a grant-closure service or human legal-review ceremony. Acquisition is independent of original reviewed gold coverage.

#### Scenario: FULL-02 Complete supported behavior

- **GIVEN** Use a complete authorized release manifest and a manifest missing one partition, annotation tier or licence artifact.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** Every source record links exact raw bytes, original scales/annotators/offsets and its permitted use; unavailable fields remain explicitly unknown.

#### Scenario: FULL-02 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** Missing raw hashes, undeclared count drift, unauthorized cloud transfer or auto-alignment relabeled as manual evidence blocks ingest or release.

### Requirement: DATAFULL-01 TET-GOLD-1 full release

The source plan SHALL retain TET-GOLD-1: project-owned versioned full-domain release. Required components: JSONL, content-addressed WAV, all eight domains, machine reviews and imported native annotation/consent records when supplied, development/calibration/holdout manifests. Rights/access boundary: not_created; approved counting and LLM/native label provenance. Observed hashes/counts SHALL remain absent until acquired; every unavailable component SHALL be reported rather than invented.

#### Scenario: DATAFULL-01 Complete supported behavior

- **GIVEN** Inspect the exact TET-GOLD-1 release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full TET-GOLD-1 manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-01 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned TET-GOLD-1 release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-02 SPEECHOCEAN762 full release

The source plan SHALL retain SPEECHOCEAN762: OpenSLR 101 speechocean762.tar.gz; author Git revision is a separate release. Required components: Complete train and test, WAV/text/utt2spk/wav.scp, scores.json and scores-detail.json; all five raters and original score scales. Rights/access boundary: not_downloaded; CC BY 4.0 attribution/change notices; cloud upload consent evaluated separately. Observed hashes/counts SHALL remain absent until acquired; every unavailable component SHALL be reported rather than invented.

#### Scenario: DATAFULL-02 Complete supported behavior

- **GIVEN** Inspect the exact SPEECHOCEAN762 release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full SPEECHOCEAN762 manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-02 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned SPEECHOCEAN762 release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-03 L2-ARCTIC full release

The source plan SHALL retain L2-ARCTIC: official v5.0, March 12 2020, including suitcase extension. Required components: All 24 read-speech speakers across six L1 groups; WAV/transcripts/TextGrid; distinguish automatic and manual tiers; include unscripted suitcase data for 22 speakers and release README/LICENSE/PROMPTS. Rights/access boundary: licence_blocked for product use; CC BY-NC 4.0 or exact separate permission; acquisition form has not been submitted. Observed hashes/counts SHALL remain absent until acquired; every unavailable component SHALL be reported rather than invented.

#### Scenario: DATAFULL-03 Complete supported behavior

- **GIVEN** Inspect the exact L2-ARCTIC release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full L2-ARCTIC manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-03 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned L2-ARCTIC release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-04 WILOCNESS-2.1 full release

The source plan SHALL retain WILOCNESS-2.1: official BEA W&I+LOCNESS 2.1. Required components: Full train/dev/test and native controls; every available M2/README/licence component; source A/B/C CEFR, annotator IDs, alternative corrections/noop; held-out scoring/label availability recorded explicitly. Rights/access boundary: licence_blocked for product use; expected counts describe W&I, LOCNESS native component counted separately from acquired release; no invented inaccessible test labels. Observed hashes/counts SHALL remain absent until acquired; every unavailable component SHALL be reported rather than invented.

#### Scenario: DATAFULL-04 Complete supported behavior

- **GIVEN** Inspect the exact WILOCNESS-2.1 release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full WILOCNESS-2.1 manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-04 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned WILOCNESS-2.1 release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-05 FCE-2.1 full release

The source plan SHALL retain FCE-2.1: official BEA FCE 2.1. Required components: Every supplied partition and M2, README/licence; preserve original essay/learner group, all edits/annotators/alternative corrections. Rights/access boundary: licence_blocked for product use; release partition counts must be inspected, underlying 1244 is not assumed equal to M2 record count. Observed hashes/counts SHALL remain absent until acquired; every unavailable component SHALL be reported rather than invented.

#### Scenario: DATAFULL-05 Complete supported behavior

- **GIVEN** Inspect the exact FCE-2.1 release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full FCE-2.1 manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-05 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned FCE-2.1 release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-06 EFCAMDAT-R2 full release

The source plan SHALL retain EFCAMDAT-R2 (legacy EFCAMDAT identity): full second release (XML); cleaned/error-coded XLSX subcorpora are separately versioned derivatives. Required components: Full XML, task prompts, all available learner/task/proficiency groups; keep second release distinct from Shatz 2020 and Oksuz et al. 2025 derivatives; inspect accepted agreement, schema, offsets and annotation coverage before approved ingest contract. Rights/access boundary: access_and_licence_blocked; academic affiliation, university Google account and administrator approval required; baseline discovery-only profile not automatically ingest-enabled. Observed hashes/counts SHALL remain absent until acquired; every unavailable component SHALL be reported rather than invented.

#### Scenario: DATAFULL-06 Complete supported behavior

- **GIVEN** Inspect the exact EFCAMDAT release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full EFCAMDAT manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-06 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned EFCAMDAT release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-07 DOUBAO-STUDY-RECORDS full release

The source plan SHALL retain DOUBAO-STUDY-RECORDS: no publicly verified downloadable corpus release. Required components: Research paper inventory only; full participant recordings/annotations require author/participant permissions and exact release contract; do not fabricate the reported 545 videos as acquired data. Rights/access boundary: unavailable; archive reports no accessible recordings or permission; publisher PDF fetch timed out during independent research. Observed hashes/counts SHALL remain absent until acquired; every unavailable component SHALL be reported rather than invented.

#### Scenario: DATAFULL-07 Complete supported behavior

- **GIVEN** Inspect the exact DOUBAO-STUDY-RECORDS release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full DOUBAO-STUDY-RECORDS manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-07 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned DOUBAO-STUDY-RECORDS release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-08 MOODRICK-DATA full release

The source plan SHALL retain MOODRICK-DATA, the Moodrick member of historical MOODRICK-NIR-DATA: no supplied actual annotated data release. Required components: Retain Moodrick as a separate vendor comparison source; NIR is bound under DATAFULL-11. public simulator descriptions do not supply private answer banks, prompts, rubrics, teacher interaction data or consent. Rights/access boundary: unavailable; NIR public page inspected as comparison only; Moodrick page fetch timed out, so data availability is unverified beyond supplied review. Observed hashes/counts SHALL remain absent until acquired; every unavailable component SHALL be reported rather than invented.

#### Scenario: DATAFULL-08 Complete supported behavior

- **GIVEN** Inspect the exact MOODRICK-DATA release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full MOODRICK-DATA manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-08 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned MOODRICK-DATA release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-09 EFCAMDAT-SHATZ2020 separate full release

The source plan SHALL retain the complete separately versioned EFCAMDAT-SHATZ2020 entry and every required component in specification/v2/domain/corpus-sources.v1.yaml and specification/v2/docs/sources/efcamdat.md. It SHALL retain exact actual native-format/rights/count bindings or an explicit unavailable status. It SHALL NOT substitute another derivative/vendor, an account credential, partial data or a public description for the actual full release. The attached transcribed decisions are not evidence of actual rights or owner approvals.

#### Scenario: DATAFULL-09 Complete separately bound release
- **GIVEN** the exact authorized EFCAMDAT-SHATZ2020 full release and required native format are available.
- **WHEN** every partition/member/record and permission is reconciled.
- **THEN** its actual immutable manifest and transformations remain separate from all other profiles.

#### Scenario: DATAFULL-09 Missing source or false equivalence
- **GIVEN** the release/rights/format are absent or only another derivative/vendor is supplied.
- **WHEN** full-source acceptance is requested.
- **THEN** EFCAMDAT-SHATZ2020 stays blocked and no acquired coverage or equivalence is invented.

### Requirement: DATAFULL-10 EFCAMDAT-OKSUZ2025 separate full release

The source plan SHALL retain the complete separately versioned EFCAMDAT-OKSUZ2025 entry and every required component in specification/v2/domain/corpus-sources.v1.yaml and specification/v2/docs/sources/efcamdat.md. It SHALL retain exact actual native-format/rights/count bindings or an explicit unavailable status. It SHALL NOT substitute another derivative/vendor, an account credential, partial data or a public description for the actual full release. The attached transcribed decisions are not evidence of actual rights or owner approvals.

#### Scenario: DATAFULL-10 Complete separately bound release
- **GIVEN** the exact authorized EFCAMDAT-OKSUZ2025 full release and required native format are available.
- **WHEN** every partition/member/record and permission is reconciled.
- **THEN** its actual immutable manifest and transformations remain separate from all other profiles.

#### Scenario: DATAFULL-10 Missing source or false equivalence
- **GIVEN** the release/rights/format are absent or only another derivative/vendor is supplied.
- **WHEN** full-source acceptance is requested.
- **THEN** EFCAMDAT-OKSUZ2025 stays blocked and no acquired coverage or equivalence is invented.

### Requirement: DATAFULL-11 NIR-DATA separate full release

The source plan SHALL retain the complete separately versioned NIR-DATA entry and every required component in specification/v2/domain/corpus-sources.v1.yaml and specification/v2/docs/sources/private-vendors-and-study.md. It SHALL retain exact actual native-format/rights/count bindings or an explicit unavailable status. It SHALL NOT substitute another derivative/vendor, an account credential, partial data or a public description for the actual full release. The attached transcribed decisions are not evidence of actual rights or owner approvals.

#### Scenario: DATAFULL-11 Complete separately bound release
- **GIVEN** the exact authorized NIR-DATA full release and required native format are available.
- **WHEN** every partition/member/record and permission is reconciled.
- **THEN** its actual immutable manifest and transformations remain separate from all other profiles.

#### Scenario: DATAFULL-11 Missing source or false equivalence
- **GIVEN** the release/rights/format are absent or only another derivative/vendor is supplied.
- **WHEN** full-source acceptance is requested.
- **THEN** NIR-DATA stays blocked and no acquired coverage or equivalence is invented.
