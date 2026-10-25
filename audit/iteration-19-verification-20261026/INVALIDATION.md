# Evidence reuse and semantic invalidation

Baseline acceptance is b21fd83 over tested application revision4133f9b, with25
registered clean passes. This review found two missing counterexamples; the
prior acceptance is superseded for full iteration19 by the expanded55-case set.
It was valid only for its original cases.

Changed production inputs are savedList/useSavedList and the four saved-list
callers. Read ordering, loading/error/empty distinction, retention/recovery,
pagination wiring and changed action-to-list refresh are therefore observed
again on the source-built frontend. Twelve literal state-owner tests and18
current browser/review tests supply the additional positive/negative cases.
The DAG includes these dependencies and no planned placeholders for this scope.

The25 original identities remain registered. Native metadata projections,
original-heard titles, full-ID links, excerpt/date fallbacks, stored failure codes,
completed audio pieces and persisted answers retain their original native
receipts. Their production API/storage/schema/fixture inputs are unchanged.
Stored observation assertions do not represent another browser, database,
LLM or speech execution. Current browser facts cover the changed views.

The final source build is web-build-final.log. No production edits occurred after
that build and the current CUA observations. Graph/discovery/compatibility
validation is graph-stable.json. New report/progress and acceptance-only records
do not invalidate application observations. The clean-revision gate must be
run once after the implementation commit because its revision/clean input
changes. No repeated native/provider campaign, blanket tests or PBT is needed.

During registration, equal test-method names in two classes initially collided.
The class-qualified case IDs fix that manifest-only issue before stable graph
validation. No test or product failure is hidden by this correction.
