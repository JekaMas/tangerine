# Iteration 27 — full-source acquisition, native imports and provenance

Status: **partially applied; full iteration acceptance is incomplete**.
Started from clean `8cac484a9cb0c067d15e9ee988f739dc95d5251f` on
`tangerine/iteration-16-release`. Canonical scope is I27.1–I27.3 in the existing
OpenSpec task list. I27.1 is complete; I27.2 and I27.3 remain open for the exact
external-input and browser-observation limits below. No feature/source was
removed to turn missing evidence into a passing result.

## Acquired and observed

The actual official L2-ARCTIC v5 archive supplied by the owner is now downloaded:

- Private path: `/Users/jekamas/projects/0xatelerix/tangerine/data/corpora/l2-arctic/official-v5-20261026.zip`.
- Size: 7,515,454,814 bytes. SHA-256: `490d5a43e48b0af84f6bce8e766ad453e8cd670521d5876bb4d0741cca304fda`.
- 29 outer members: 24 speaker ZIPs, one suitcase ZIP and four documents.
- Expanded population: 84,266 speech-data files plus four documents. The
  84,295-entry hierarchical inventory also counts the 25 ZIP containers; it is
  not an utterance population.
- All 25 component ZIP digests and all 84,266 native data-file digests match the
  previously accepted pinned mirror receipts. LICENSE, PROMPTS and README.pdf
  also match. The official README.md is retained separately and differs from
  the mirror README files. Whole-repository/bundle equality is not claimed.
- CC BY-NC 4.0 remains the source license. Apache-2.0 licenses Tangerine software.
  Acquisition/native inventory does not claim a full normalized L2 database import.

One intake digest/inventory was performed; ordinary use trusts saved results.
The suitcase comparison's initial wrapper-path mismatch was repaired from the
saved metadata without rereading or rehashing the corpus. `L2-OFFICIAL.json`
records the sanitized acquisition/provenance result.

Three complete actual source imports passed through the real API storage,
PostgreSQL and MinIO owners in disposable test stacks:

| Source | Actual observation |
| --- | --- |
| FCE 2.1 | Full native import passed; 33,236 sentence representations retained. |
| W&I+LOCNESS 2.1 | Full native import passed; 4,477 withheld originals retained without invented labels. |
| SpeechOcean762 | Full native import passed; 60,427 accepted native rows, zero quarantines/raw-only rows, raw/normalized completeness and saved complete Sources status. All 5,245 WAV files remain, including 245 unrated recordings alongside the 5,000 rated utterances. |

These are disposable-stack observations, not imports into the user's running
workspace. Actual foreground timeout/resume behavior was exercised. The two BEA
individual passes remain valid even though their original combined command was
intentionally stopped before its new SpeechOcean case; its package exit is not
reported green. The final standalone SpeechOcean package exited successfully.

## Repairs and sibling review

1. **One saved full-release assessment.** Import completion saves the assessment;
   status reads no longer recount accepted source rows. Existing legacy reports
   retain their data and explicitly say that an assessment was not saved.
2. **Correct saved-release associations.** Status projects reports per release.
   Reopening an older release selects its own report, binding and saved permission
   selectors, clearing the previous upload/notice selection. Progress returns
   the frozen saved selectors instead of inventing new grants.
3. **Honest missing components.** A count-reconciliation explanation cannot stand
   for an entirely absent required component. Explicit expected-zero components
   and documented nonzero count differences still work. Companion CSVs, mirrors
   and constructed private fixtures do not certify missing owner populations.
4. **Standard TAR metadata.** The full SpeechOcean archive exposed rejection of
   a standard global PAX header. The archive owner now recognizes it as metadata;
   the retained original archive preserves its bytes. Links/devices/unsafe
   entries still have the existing negative cases.
5. **Native Kaldi joins.** Real tab-delimited sentence lines exposed a parser
   choosing a later space as the delimiter. The parser now uses the first space
   or tab, preserving IDs, the raw line and the whole sentence. Fresh tab-based
   native positive/negative fixtures pass.
6. **Complete SpeechOcean media scope.** Native inspection established 5,245 WAVs,
   not the 5,000 scored subset initially expected by the new test. The spec,
   independent oracle and full-source count retain the extra 245. A trimmed
   5,000-member synthetic metadata control cannot certify the full release.
7. **Recovery guidance.** Resolved foreground failures remain in original issue
   and event history but no longer appear as current records needing attention
   after a successful import. Real failure/recovery tests assert both facts.

The source parser, import summary/storage, status projection and web selection
retain separate ownership. No periodic audit, hash sweep, human approval gate or
new model validation is added to ordinary exercise use.

## Actual UI, UX and typography evidence

The source-built native fixture rendered all eleven source identities and the
saved releases at 1280×720, 390×844 and 320×740. Actual Source Sans 3 was loaded;
body text was 17px/24.65px, saved-release controls 16px, keyboard focus 3px, and
there was no page horizontal overflow. Screenshots were visually inspected.
A controlled cold dependency failure made three requests before displaying
human-readable recovery guidance; it did not leak the backend diagnostic.
Actual navigation/reload after recovery restored all eleven cards.

**Input activation remains unverified.** Pointer, locator and Enter/Refresh
activation in the selected in-app browser did not dispatch saved-release reads.
No synthetic DOM event, alternate hidden browser driver or browser switch was
used to manufacture this observation. The previously asked alternative-browser
choice is still unanswered. Native release/report/binding association tests pass,
but they do not replace the missing browser interaction. Later selection-handler
edits do not invalidate the retained initial rendering/style/reload observations.

Native/private evidence is in `data/iteration-27-sources-20261026/browser/`:
`fixture.json`, `observations.json`, `requests.jsonl`, screenshots and
`native-final.json`. The finalizer reports zero provider receipts. The fixture
containers and proxy were removed. The user's port 3000 and saved data/settings
were untouched.

## Exact outstanding source inputs

| Source identity | Missing original input and current observation |
| --- | --- |
| EFCAMDAT-R2 | Complete owner XML, prompts and documentation. Current Cambridge requirements and actual administrator reply require academic affiliation/university email; selected personal-account access was refused. |
| EFCAMDAT-SHATZ2020 | Both complete samples, intermediate versions, glossary/scripts and actual terms. The selected account's owner folder still denies access. |
| EFCAMDAT-OKSUZ2025 | Complete error-coded owner workbook, native dictionary and terms. Owner folder still denies access. Four public OSF analysis companions remain separately acquired. |
| DOUBAO-STUDY-RECORDS | Authorized participant records, complete instruments/scales and consent/use terms. The downloaded public paper is documentation; its reported populations/examples are not a participant release. |
| MOODRICK-DATA | Separate complete authorized export, dictionary, population manifest and use terms. Current public material and the request thread supply no release. |
| NIR-DATA | Separate complete authorized export, dictionary, population manifest and use terms. Current public material and the request thread supply no release. |

The original optional TET-GOLD-1 remains generated from actual use, with no
pregeneration campaign. Four of the eleven original identities have complete
native bytes; the six named owner releases remain unavailable. No product
approval or software license can supply those bytes/terms. Their absence does
not block the on-demand clean-text → mutations → audio → answer → scoring flow.

Supplement limits remain explicit: ICNALE media acquisition is prohibited by the
retained owner reply and was not attempted; the exact third-party DRAL link still
returns HTTP403. Existing complete base/latest increments retain their scope.
Speak & Improve has a visible reply mentioning license limitations in its preview,
but the full message could not be opened with current IAB input; exact conditions
are unread, not inferred. No new source-owner message was sent.

## Validation and retained proof boundaries

- 60 native regression identities passed, followed by directly affected saved
  permission, component reconciliation, PAX, Kaldi, tab-join, recovery and media
  scope cases. Actual full FCE, W&I and SpeechOcean imports passed separately.
- The selected DAG receipt observers finished **18 passed, 2 skipped, 0 failed**.
  The skips are actual unavailable owner releases and actual browser activation;
  the iteration's acceptance status is incomplete.
- Pinned strict OpenSpec 1.13.1, evidence graph and discovery validation passed.
  Source-fact/requirement and shared-file test identities were reconciled with
  unchanged scenario/body comparisons and exact fresh affected receipts; old
  receipts were not rewritten. `SPEC-RECONCILIATION.json`,
  `TEST-RECONCILIATION.json` and `FUNCTION-REUSE.json` record that boundary.
- Final stable `go vet` and web production build passed. Native failures and the
  incorrect initial new-test WAV expectation remain retained alongside repairs.
- Original taxonomy/recipes, 42 formulas, source identity definitions and preset
  definitions are byte-identical to the starting revision. Schema copies match;
  the status/report additions are additive. See `PRESERVATION.json`.
- Committed-clean candidate `6ba7e7257992069888ff4c5db458dfc5f5c8bc98` records
  **18 passed, 2 skipped, 0 failed** in `ACCEPTANCE.json` and the private clean
  receipt. Overall acceptance remains incomplete. This reused observed native
  evidence without repeating downloads, imports or browser work solely because
  a commit changed. The follow-up evidence-only commit does not change those
  semantic inputs.

No model inference, speech generation, paid credits/overage, account creation,
installation, deployment, publication, property-based campaign or financial
execution occurred. Actual source downloads were acquisition, not provider calls.
The protected unrelated canonical `GAPS.md` edit is preserved.
