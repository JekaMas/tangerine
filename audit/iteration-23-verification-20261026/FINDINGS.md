# Findings and sibling dispositions

Baseline fa8b1d6; root-cause repairs use existing production owners.

| Finding | Evidence and cause | Repair / siblings |
|---|---|---|
| P2 terminal recovery misclassification | red-provider.jsonl: payment402, modern/legacy403 and model404 fail literal expected categories. Gemini adapter treated them as generic PROVIDER_FAILURE, so saved UI advised waiting for availability. | gemini.go maps them to existing LOCAL_BUDGET_EXCEEDED / CONSTRAINT_CONFLICT. Preserve private error reason, exact request, one terminal call and zero fallback. Authentication401, modern/legacy bodies, quota429, unknown400 and temporary503/recovery are exercised. No new error family or runtime gate. |
| P2 credential/access guidance missing immediately | red-messages.log: MISSING_CREDENTIALS and CONSTRAINT_CONFLICT fall through to generic refresh guidance. The immediate map handled only singular MISSING_CREDENTIAL. | prepare/response.js handles both spellings and settings/access changes; requestError.js owns the shared authored reason; prepare/failureMessage.js owns persisted projection. Actual native403 row and immediate Resume show correct guidance; controlled401/429 UI cases exercise terminal alternatives with no native redispatch. |

Native checkpoint siblings: current canonical→mutation errors for quota, denial,
credentials and unavailable all retain clean text/settings and no invented audio.
Read recovery is still owned by clientRequest (bounded read retries, logging,
no POST replay);21 existing client/preparation literal sibling cases pass after
the shared authored-message addition. The actual native503 and new modern503
retry identical input on the same selected model. No quota exhaustion is used.

Generation/Resume share the preparation messages; reloading does not dispatch a
provider request. Successful explicit Resume reuses the saved canonical/settings,
accepts the controlled mutation reply, renders actual local speech and publishes
stored audio. Native and browser observations distinguish that controlled
dependency from the retained actual Gemini Free qualification. Completed records
clear stale guidance and remain playable. Viewing errors leaves controls usable.

Interpretation/feedback callers share the repaired classifier. Their unchanged
HTTP/session owners preserve the submitted answer and any score, expose authored
recovery and do not print provider diagnostics; successful actual scoring/context
evidence remains retained. No new interpretation schema/UI contract is needed.
Provider setup screens also consume existing safe categories. No additional
defect was established in those unchanged presentation paths.

UI/UX: keyboard mobile-menu open/close, Refresh, retained topic, catalogue Retry,
native denial, immediate credential/allowance guidance, saved denial after reload,
explicit Resume, reopened complete record, Library→Listen and actual playback
were observed. Typography: Source Sans3 loaded, body17px/24.65px, guidance14/16px,
no page overflow at1280/390/320. Screenshots inspected directly; no visual quality
claim follows from the mechanical reader alone. No CSS/font redesign required.

No unresolved finding in this selected scope after focused observations. Final
committed-clean acceptance is a separate step recorded in ACCEPTANCE.json.
