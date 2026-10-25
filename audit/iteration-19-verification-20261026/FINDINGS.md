# Verified findings and sibling disposition

V19-01 (P2, demonstrated defect): Refresh is reachable while reads overlap, but
four independent page implementations applied whichever response arrived last.
The baseline Attempts browser shows Latest saved snapshot, then Earlier saved
snapshot after releasing the older request. The same missing response ownership
exists in Prepare/usePreparation, Audio and ChooseCase. Repair: one savedList
owner commits only the latest requested read, retains accepted items/cursor on
failure, and ignores superseded completion/loading/error after refresh/navigation.
The React adapter owns existing envelope projection, not record validation.

V19-02 (P2, demonstrated defect): Audio and Prepare represent unread state as an
empty array and show No saved preparations yet before success and after terminal
read failure. Both baseline states are observed. Repair: distinguish loaded from
loading/error in the same shared owner; only a successful empty read produces the
empty-state claim. Attempts and ChooseCase already guard parts of this behavior;
use the same owner to prevent inconsistent siblings and separate preparation list
errors from generation feedback. No generation/rendering action is blocked.

Known sibling scope: Prepare saved preparations, Attempts, Audio, review exercise
picker. All four adopt the shared list owner and receive literal browser ordering,
retention/error/recovery/empty/loading tests. Existing requestError/clientFetch
retain safe logging and bounded transient GET retry; writes keep their explicit
idempotency/resume owner. Parsing errors now reach requestError for redacted
logging rather than disappearing into page-specific catches. No repeated schema,
stored-byte or integrity check is introduced.

Native title/excerpt/date projections, original heard snapshots, pagination,
response schemas and rendering persistence were inspected and match the accepted
contracts. Their unchanged native receipts are retained. Existing renderer/key,
LLM, speech, corpus and scoring owners are outside this presentation repair.
