# Iteration 24 verification and repair

**Not green: actual Azure access and complete interaction/audio evidence remain
unavailable.** Verification started from clean `75801c2`. The prior clean
`d9af363` receipt remains valid for its original inputs and 18-case scope; it
does not prove the following repairs. Final source/run identities are in
`STATUS.json`. No I24 task is checked from partial evidence.

## Findings, causes and sibling disposition

1. **Comparison failure recovery — repaired.** The helper called native render
   once, allowed connection/provider exceptions to escape and journalled only
   ValueError failures. The existing shared transport also discarded the HTTP
   status needed to distinguish credential denial from an outage. The transport
   now retains only safe status/Retry-After facts. The comparison owns up to
   three attempts within the existing deadline, safe logs, authored recovery and
   durable paused/progress state. No repeated stored-data validation was added.
   Credential/unsupported/invalid-output and unknown-allowance failures stop
   without blind retries; a provider-supplied rate-limit delay can be respected.
   The same owner handles URL errors, timeouts, 503, 401/403, quota and deadline
   siblings. No provider fallback or paid use is introduced.
2. **Completed reference hidden by later failure — repaired.** Assembly occurred
   only after all eight turns. The reference is now assembled as soon as its four
   turns finish. A failure in the mutated variant retains the playable reference
   and all accepted pieces/responses. Resume trusts these saved values and calls
   only for missing pieces. The full pair is still incomplete until both finish.
3. **Misleading player recovery — repaired.** Missing media always claimed that
   Azure access was absent, including after a quota or connection failure. The
   player now reads saved authored progress/recovery and keeps available audio
   and Refresh enabled. A media fetch error first logs a redacted diagnostic and
   retries that same stored WAV once; only then does it show human guidance.
   Actual controlled browser requests confirm exactly two GETs per WAV for both
   persistent-503 and transient-503-then-success cases, with no synthesis calls.
4. **Cancellation sibling — repaired.** Keyboard interruption escaped with a
   traceback and left rendering status behind. A literal red test exited130
   without a completed unittest case. The helper now records paused progress,
   retains two completed pieces in the fixture and returns130 with an authored
   stopped/resume message. Cancellation does not trigger a retry.
5. **Incomplete acoustic-review oracle — repaired.** A playback boolean alone
   did not require observations for all four targets. The live review case now
   requires the exact turn/speaker/word correspondence, both variant filenames,
   an honest outcome and actual observation text. Missing/mismatched targets,
   another exercise's audio and empty notes have literal negative expectations.
   These are development evidence checks, not application or learner gates.

Related ordinary application owners were inspected: speechExchange and
speechPublicFailure, preparationResponse, failureMessage and failureReason.
The frontend already uses authored messages instead of displaying backend
strings. No Go/web product edit or deployment follows from that inspection.
The native status metadata preserves existing ValueError codes and wire behavior.
The six prior hosted/SSML sibling observations remain valid because their
success/compilation inputs did not change.

## Tests and evidence limits

`tests/test_azure_recovery.py` exercises the existing render/transport/comparison
owners using controlled responses and PCM. The original 13 native cases remain
selected. Three additional cases reconcile actual retained browser/HTTP/layout
observations; they explicitly replay those observations and do not run a new
browser or certify Azure speech. No test merely accepts a report saying pass.
Final iteration selection includes the original five completion/review cases,
with actual Azure synthesis/full playback still explicitly skipped.

Initial red recovery/cancellation outputs, the first media-error screenshot,
controlled HTTP logs, later observations and exact commands remain under
`data/iteration-24-verify-20261026/`. One intermediate retry test patched the
process-wide time.sleep and counted unrelated library polling. That test-isolation
failure is preserved. The comparison's own sleep binding is now patched, and
the isolated observations passed. No real quota was exhausted to induce errors.

## UI, UX and typography

Used OpenSpec verify, SDD workflow, verification-design (implementation inspection
and hypothesis debugging), the typography skill and the project's
UI_UX_TYPOGRAPHY_VERIFICATION.md. This is sequential self-review against
independent requirements and literal fixtures, not a separate reviewer.

- **UI/UX: incomplete overall.** Actual waiting, partial, retrying, complete,
  persistent media failure and automatic recovery states were inspected through
  the real read-only player with controlled PCM. Native media loaded, recovery
  cleared on success, both recordings remained paused, and no inference route
  was called. The first complete recording stays available through failure.
  Disclosure/play activation attempts returned unchanged state. An independent
  plain HTML form also failed to focus/activate, without any player JavaScript.
  Native ChatGPT app inspection was rejected by the tool's safety restriction.
  Therefore input delivery is an external testing limitation; its exact cause is
  not established. No product click defect, successful activation or keyboard
  pass is claimed, and no protection was bypassed.
- **Typography: pass for inspected rendered states.** Desktop1280×720,
  390×844 and320×740 show loaded Source Sans3, 17px body/24.65px line height,
  readable cards/actions and no page overflow. Headers wrap naturally and media
  controls remain within their cards. Expanded hidden content is not accepted.
- **Evidence: incomplete for I24.** The saved public observation JSON files
  identify controlled origin and preserve failed activation. The actual common
  source, speakers and four IPA targets are unchanged. There is no actual Azure
  pair, audible-mutation observation or completed real playback review.

## External blocker and resume

This verify rechecked only Azure configuration presence, without printing keys:
`.env`, the existing runtime environment and ambient environment have no Azure
key/region, and no observed resource metadata file is present. Microsoft still
awaits the existing account's passkey/security-window confirmation in tab25.
The separate Chrome authentication tab from earlier work was observed in the
inventory and left untouched. No trial, resource, billing link or credential was
created. No model or Azure synthesis call occurred.

Finish the protected sign-in, inspect actual F0 key/region/allowance/voice access,
then follow README.md to complete both real recordings and target/player review.
Retest manual activation once browser input is available. These are external
execution/evidence dependencies, not an unresolved product decision. Keep all
I24 tasks unchecked and do not issue an acceptance record until the complete
selection passes on a committed-clean revision with that actual evidence.
