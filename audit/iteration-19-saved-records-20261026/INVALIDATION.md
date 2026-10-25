# I19 selected evidence and invalidations

Start: bb88023, clean. Select FIN-UI-02.P1, FIN-UI-03.P1, FIN-VERIFY.I19.
The14 literal continuation cases become executable;11 owner/sibling regressions
extend them. Existing metadata projections and embedded schemas are retained.

- Shared savedRecord/RecordIdentity changes invalidate ambiguous title/date
  presentation in Prepare, Attempts, Audio and review choices. Observe equal
  titles/dates/first8ID bytes, full links, long content and legacy fields at
  1280/390/320px. Native original-heard identity/pagination receive exact new
  native fixtures. No new metadata store or migration is added.
- failureMessage changes invalidate failed-phase/missing-detail/credential-code
  presentation in Prepare and Audio. Observe actual persisted phase/reason,
  reload, native resume and completed rows. Rerun only the six relevant existing
  FX helper cases; no replay of their unrelated media/report/experiment tests.
- ChooseCase now retains prior rows on read failure and provides explicit
  Refresh. Observe initial empty/loading/error, retained failure and Retry,
  plus read-only full-ID selection. It adds no review or generation gate.
- New Go fixture setup initially attempted a normal backdate and a checkpoint
  without a live operation. Corrected to explicitly constructed native display
  writes and a test-only historical timestamp seed. Retain failed setup logs;
  they are not product defects or passing observations.
- The interactive Go server reached the default10minute test deadline after
  useful browser observations. The two exact native projection/pagination
  subtests and saved browser/native records remain valid. The tracked tests/history-browser
  launcher now sets70minutes and an explicit done file; repeat only that failed
  harness on fresh owned storage and close it after the explicit UI resume. Independently
  execute TestI19HistoryPersistedReadback against the exact observed IDs and
  first-piece asset to close persistence/recovery, without replaying green UI
  or model calls. The original timed-out server root is not represented as a passing test; the
  corrected fresh harness must provide its own full-root pass.
- Go vet found a pre-existing lock-copy in TestNativeSpeechRestartPositive,
  mounted as a fixture dependency. Construct a fresh Server with NewServer;
  execute precisely that race case. No production Go owner changes. Other
  functions in native_speech_test.go retain their semantics and original proof.
- The first browser failure observer switched the failure control before three
  read attempts finished. It is not a counterexample or acceptance. Wait for
  actual terminal UI, then inspect three journaled GETs and explicit recovery.
- A disposable10px head-injection trial remained14px after framework handling.
  Retain it as an attempted variant, never claim an actual10px UI observation.
  The alternative literal typography omission and constructed10px review-input
  negatives exercise the review owner; normal typography uses actual screenshots.

Request admission, generation, LLM context, scoring, speech rendering, schemas,
source acquisition, taxonomy, formulas and shared workflow/tool pins are unchanged.
Do not rerun unrelated accepted provider, audio, source or whole-product campaigns.
Only the final clean-state gate is invalidated by a new commit; retained native
and browser behavior is not repeated to manufacture new revision hashes.
