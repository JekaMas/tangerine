# full-source-coverage specification

## ADDED Requirements

Current native/source-access observations are owned by audit/corpus-acquisition-20261009/REPORT.md and acquisition-manifest.json. The optional supplemental source contract is specification/v2/docs/sources/alternatives.md. Preserve all eleven required identities and scopes; supplementation cannot satisfy a missing original release.

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
- **THEN** Missing raw hashes or undeclared count drift prevents a complete acquired-release claim; unauthorized cloud transfer is not performed and auto-alignment is never relabeled as manual. Valid raw intake and unrelated local use remain available.

### Requirement: DATAFULL-01 TET-GOLD-1 full release

The source plan SHALL retain TET-GOLD-1: project-owned versioned full-domain release. Required components: JSONL, content-addressed WAV, all eight domains, machine reviews and imported native annotation/consent records when supplied, development/calibration/holdout manifests. Rights/access boundary: not_created; approved counting and LLM/native label provenance. Observed local native hashes/counts SHALL be populated only from actual acquisition receipts; every unavailable component SHALL be reported rather than invented. Native acquisition SHALL NOT establish implemented import or normalized completeness.

#### Scenario: DATAFULL-01 Complete supported behavior

- **GIVEN** Inspect the exact TET-GOLD-1 release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full TET-GOLD-1 manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-01 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned TET-GOLD-1 release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-02 SPEECHOCEAN762 full release

The source plan SHALL retain SPEECHOCEAN762: OpenSLR 101 speechocean762.tar.gz; author Git revision is a separate release. Required components: Complete train and test, WAV/text/utt2spk/wav.scp, scores.json and scores-detail.json; all five raters and original score scales. Rights/access boundary: full native OpenSLR archive and pinned owner snapshot acquired on 2026-10-09; CC BY 4.0 attribution/change notices retained; external API transfer remains governed by actual source terms and selected local settings. Application import/normalization is not observed. Observed local native hashes/counts SHALL be populated only from actual acquisition receipts; every unavailable component SHALL be reported rather than invented. Native acquisition SHALL NOT establish implemented import or normalized completeness.

#### Scenario: DATAFULL-02 Complete supported behavior

- **GIVEN** Inspect the exact SPEECHOCEAN762 release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full SPEECHOCEAN762 manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-02 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned SPEECHOCEAN762 release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-03 L2-ARCTIC full release

The source plan SHALL retain L2-ARCTIC: official v5.0, March 12 2020, including suitcase extension. Required components: All 24 read-speech speakers across six L1 groups; WAV/transcripts/TextGrid; distinguish automatic and manual tiers; include unscripted suitcase data for 22 speakers and release README/LICENSE/PROMPTS. Rights/access boundary: official acquisition form submitted and automatic access email received on 2026-10-09; full ZIP returned download-quota HTML and supplied individual components returned disabled-download/404 responses. A complete31-member raw mirror at cc02fd37197966e5de11ad737f7affd577c61992 is separately acquired and hash/CRC checked, with26,867read recordings/3,599manual files and22suitcase speakers. Phones-tier operation counts differ from the official README; preserve both under the L2 source contract. Official byte equivalence/full-source conformance remains unresolved; raw mirror availability does not block ordinary local use. CC BY-NC 4.0 or an actual separate permission governs its uses. Observed local native hashes/counts SHALL be populated only from actual acquisition receipts; every unavailable component SHALL be reported rather than invented. Native acquisition SHALL NOT establish implemented import or normalized completeness.

#### Scenario: DATAFULL-03 Complete supported behavior

- **GIVEN** Inspect the exact L2-ARCTIC release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full L2-ARCTIC manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-03 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned L2-ARCTIC release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-04 WILOCNESS-2.1 full release

The source plan SHALL retain WILOCNESS-2.1: official BEA W&I+LOCNESS 2.1. Required components: Full train/dev/test and native controls; every available M2/README/licence component; source A/B/C CEFR, annotator IDs, alternative corrections/noop; held-out scoring/label availability recorded explicitly. Rights/access boundary: complete official native v2.1 archive acquired on 2026-10-09 with source noncommercial terms retained; actual LOCNESS development has988blocks, differing from the owner-page998 expectation. Preserve both observations. Combined/component views overlap; no invented inaccessible test labels or commercial permission. Application import/normalization is not observed. Observed local native hashes/counts SHALL be populated only from actual acquisition receipts; every unavailable component SHALL be reported rather than invented. Native acquisition SHALL NOT establish implemented import or normalized completeness.

#### Scenario: DATAFULL-04 Complete supported behavior

- **GIVEN** Inspect the exact WILOCNESS-2.1 release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full WILOCNESS-2.1 manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-04 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned WILOCNESS-2.1 release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-05 FCE-2.1 full release

The source plan SHALL retain FCE-2.1: official BEA FCE 2.1. Required components: Every supplied partition and M2, README/licence; preserve original essay/learner group, all edits/annotators/alternative corrections. Rights/access boundary: complete official native v2.1 archive acquired on 2026-10-09 with source noncommercial terms retained; actual train/dev/test have28,350/2,191/2,695S-blocks. The underlying1244 is not assumed equal to M2 record count; acquisition grants no invented commercial permission. Application import/normalization is not observed. Observed local native hashes/counts SHALL be populated only from actual acquisition receipts; every unavailable component SHALL be reported rather than invented. Native acquisition SHALL NOT establish implemented import or normalized completeness.

#### Scenario: DATAFULL-05 Complete supported behavior

- **GIVEN** Inspect the exact FCE-2.1 release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full FCE-2.1 manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-05 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned FCE-2.1 release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-06 EFCAMDAT-R2 full release

The source plan SHALL retain EFCAMDAT-R2 (legacy EFCAMDAT identity): the complete second-release XML, task prompts, annotations and source documentation. The public 2023 agreement and documented XML profile SHALL be retained with actual acquired-release bindings when available. Expected 1,180,310 writings/174,743 learners are upstream expectations, not local counts. Academic approved-account access and applicable supplied permissions remain operational inputs; native data/rights are not manufactured by Apache-2.0 or product approval. Full raw intake and normalized completeness SHALL be reported separately. Observed local hashes/counts SHALL remain absent until acquired; missing actual source members SHALL be reported without blocking local startup or unrelated exercise use.

#### Scenario: DATAFULL-06 Complete supported behavior

- **GIVEN** Inspect the exact EFCAMDAT release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full EFCAMDAT manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-06 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned EFCAMDAT release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-07 DOUBAO-STUDY-RECORDS full release

The source plan SHALL retain DOUBAO-STUDY-RECORDS under specification/v2/docs/sources/doubao-study.md: all actual participant/submission records, instruments, weekly prompts, original/invalid media, journals, feedback and supplied consent/use metadata. The now-readable publisher paper supplies documentary expectations, not a participant-data release. Its single-cohort four-cycle design and post-program instruments SHALL remain explicit; invalid/missing submissions SHALL be preserved/reconciled. Actual native data/wording/scales/files remain unavailable until supplied; no aggregate reconstruction counts as acquisition. Observed local hashes/counts SHALL remain absent until acquired; missing actual source members SHALL be reported without blocking local startup or unrelated exercise use.

#### Scenario: DATAFULL-07 Complete supported behavior

- **GIVEN** Inspect the exact DOUBAO-STUDY-RECORDS release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full DOUBAO-STUDY-RECORDS manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-07 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned DOUBAO-STUDY-RECORDS release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-08 MOODRICK-DATA full release

The source plan SHALL retain MOODRICK-DATA separately from NIR-DATA: all authorized full-export sessions/turns/profiles/prompts/rubrics/feedback/media and native documentation/use terms. The official public HTML was read on 2026-10-09; it supplies a product description and contact route, not a complete native export or documented private API. Local-export adapter target meanings are defined in specification/v2/docs/sources/private-vendors-and-study.md. Demonstration values and personal/subset exports SHALL NOT satisfy the full vendor-release claim. Observed local hashes/counts SHALL remain absent until acquired; missing actual source members SHALL be reported without blocking local startup or unrelated exercise use.

#### Scenario: DATAFULL-08 Complete supported behavior

- **GIVEN** Inspect the exact MOODRICK-DATA release/component inventory, with real rights and immutable raw manifests when available.
- **WHEN** the authorized owner checks the full frozen contract
- **THEN** The full MOODRICK-DATA manifest reconciles every required component, or truthfully reports its blocked unavailable release without claiming acquired coverage.

#### Scenario: DATAFULL-08 Incomplete or forbidden behavior

- **GIVEN** an omitted, altered or unauthorized dependency in that same contract
- **WHEN** the caller requests acceptance
- **THEN** A partial/unpinned MOODRICK-DATA release, unsupported label or missing permission cannot receive full-source PASS.

### Requirement: DATAFULL-09 EFCAMDAT-SHATZ2020 separate full release

The source plan SHALL retain the complete separately versioned EFCAMDAT-SHATZ2020 entry, both 406,062/317,220 sample expectations and every supplied intermediate version, glossary, script, workbook/sheet/member. The alternate sample copied prompt text SHALL NOT be represented as observed elicitation; absent source corrections SHALL be recorded without invention. Actual workbook/glossary bindings remain source inputs. All native data remain preserved, and no single sample or another derivative SHALL substitute for the full release. Observed local hashes/counts SHALL remain absent until acquired; missing actual source members SHALL be reported without blocking local startup or unrelated exercise use.

#### Scenario: DATAFULL-09 Complete separately bound release
- **GIVEN** the exact authorized EFCAMDAT-SHATZ2020 full release and required native format are available.
- **WHEN** every partition/member/record and permission is reconciled.
- **THEN** its actual immutable manifest and transformations remain separate from all other profiles.

#### Scenario: DATAFULL-09 Missing source or false equivalence
- **GIVEN** the release/rights/format are absent or only another derivative/vendor is supplied.
- **WHEN** full-source acceptance is requested.
- **THEN** EFCAMDAT-SHATZ2020 stays blocked and no acquired coverage or equivalence is invented.

### Requirement: DATAFULL-10 EFCAMDAT-OKSUZ2025 separate full release

The source plan SHALL retain the complete separately versioned EFCAMDAT-OKSUZ2025 entry and full original/corrected/POS/error-coded Cambridge release. Its published article, deposited appendices and public OSF analysis companion SHALL be separately inventoried. Upstream member metadata, nine code-confirmed input names, complete 19/20-column public companion CSV headers and SOC/CEFR semantics in specification/v2/docs/sources/efcamdat.md SHALL be retained. All four public OSF companion files are acquired and hash verified; both CSVs are fully inspected with453,958definite/417,043indefinite rows. This does not establish a complete native method/type dictionary, inspected private workbook headers or acquired full Cambridge release. The public companion alone SHALL NOT satisfy the full owner derivative. Actual companion hashes/counts SHALL remain separate from absent full Cambridge release receipts; missing actual source members SHALL be reported without blocking local startup or unrelated exercise use.

#### Scenario: DATAFULL-10 Complete separately bound release
- **GIVEN** the exact authorized EFCAMDAT-OKSUZ2025 full release and required native format are available.
- **WHEN** every partition/member/record and permission is reconciled.
- **THEN** its actual immutable manifest and transformations remain separate from all other profiles.

#### Scenario: DATAFULL-10 Missing source or false equivalence
- **GIVEN** the release/rights/format are absent or only another derivative/vendor is supplied.
- **WHEN** full-source acceptance is requested.
- **THEN** EFCAMDAT-OKSUZ2025 stays blocked and no acquired coverage or equivalence is invented.

### Requirement: DATAFULL-11 NIR-DATA separate full release

The source plan SHALL retain NIR-DATA separately from Moodrick: every authorized full-export component, native session/profile/stage/turn/transcript/report/media/rubric and actual native documentation/use terms. The inspected SIM/research/privacy descriptions and personal portability route SHALL NOT be treated as a bulk API, dataset release or general vendor-corpus permission. Separate NIR product origins remain distinct; no provider is inferred for SIM from another product. Complete local export intake is available without a remote API. Observed local hashes/counts SHALL remain absent until acquired; missing actual source members SHALL be reported without blocking local startup or unrelated exercise use.

#### Scenario: DATAFULL-11 Complete separately bound release
- **GIVEN** the exact authorized NIR-DATA full release and required native format are available.
- **WHEN** every partition/member/record and permission is reconciled.
- **THEN** its actual immutable manifest and transformations remain separate from all other profiles.

#### Scenario: DATAFULL-11 Missing source or false equivalence
- **GIVEN** the release/rights/format are absent or only another derivative/vendor is supplied.
- **WHEN** full-source acceptance is requested.
- **THEN** NIR-DATA stays blocked and no acquired coverage or equivalence is invented.
