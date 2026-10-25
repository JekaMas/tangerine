# Iteration 19 verification and repair

Verification covers UX-02/UX-03: persisted failure guidance and recognizable
saved attempts, preparations, audio and review choices, including their native
metadata. Baseline b21fd83 is clean and follows tested revision 4133f9b.

Two demonstrated P2 defects were repaired. An older list response could overwrite
newer records or guidance; Audio and Prepare could falsely announce an empty
library while the first read was unresolved or failed. FINDINGS.md records the
counterexamples and all four sibling dispositions. One small savedList owner
now retains accepted records/cursor, applies only the latest requested read and
distinguishes unread, loading, failure and successful empty. useSavedList adapts
existing transport envelopes; the pages retain presentation/action ownership.
No schema or stored-data revalidation, additional approval or write retry is
introduced. Generation and explicit resume remain available independently of
saved-list reads. Existing bounded GET retry/logging remains the transport owner.

Current browser observations exercise all four views through initial loading,
terminal error, explicit recovery, empty success, populated failure, old/new
success/error ordering and retained full-ID links. Three paginated adapters send
the next cursor and append once. An unreadable response logs a redacted error
kind and shows authored guidance. Generate retains Topic and submits one
explicit intercepted request during saved-history failure. One controlled
resume outcome refreshes into complete state and survives reload. Native
persistence/audio-piece observations are retained separately, not simulated into
new native proof.

UI/UX review uses the project procedure and actual clicks, keyboard focus,
mobile navigation and screenshots. Typography review uses the installed
typography skill: Source Sans 3 is observed loaded; body 17px/24.65px and 14px
identity text wrap without horizontal overflow in 12 actual route/width views
(1280x720, 390x844, 320x740). Reviewed screens include attempts-320.jpg,
audio-390.jpg, prepare-320.jpg and reviews-1280.jpg. No additional learner gate
or blocking error panel was added. REVIEW.json identifies exact evidence and
self-review limits; it is not independent human approval.

The 55-case selection comprises 25 retained regression identities, 12 new
production state-owner tests and 18 current browser/review assertions. Actual
CUA facts and independent literal expectations are distinct from test-owned
HTTP responses. A constructed PCM fixture supplies media metadata only; it is
not speech or acoustic confirmation. INVALIDATION.md records why changed read
behavior is re-observed and which native receipts remain valid.

Focused 30 new cases, the final Next.js source build and scoped graph/discovery/
compatibility validation passed. The full stable selection passed 55/55 across
four commands before the source commit (stable-informational.json, dirty tree).
Committed-clean acceptance will be recorded in ACCEPTANCE.json once observed;
this preliminary result alone does not establish the required clean gate.

No provider inference/synthesis, purchased credits, overage, PBT, deployment,
postdeployment, installation or publication is included. The user app on 3000,
its settings/database/media and unrelated canonical GAPS.md remain untouched.
API, speech, migrations, 122 categories/recipes, 42 formulas and 11 source scopes are
unchanged. The Context status reports no index for this checkout; ownership was
known and exact source/runtime inspection was used, with no semantic/IDE proof
claimed. There is no additional product decision or unresolved finding in the
selected iteration after the recorded repairs; final acceptance awaits the
clean gate.

Evidence directory: data/iteration-19-verification-20261026/ (ignored).
Original native receipts: data/iteration-19-saved-records-20261026/ (ignored).
