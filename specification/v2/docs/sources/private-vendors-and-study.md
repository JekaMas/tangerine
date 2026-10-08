# Complete private/export and study adapter protocol

DOUBAO-STUDY-RECORDS, MOODRICK-DATA and NIR-DATA are separate full-source identities. No paper, demo, public description or one vendor's export substitutes for another. Their actual data, agreements and private interfaces are external operational inputs, not unresolved product policy.

## Complete local export path

This path is supported without a vendor API: supply a directory/archive containing every data file plus its actual release documentation. Intake stores every member and all native fields losslessly. A source-release record names source_id, actual release_version, origin, documentation assets, component/partition files, actual hashes/sizes and documented expected counts. Unknown expected counts are explicitly null during planning; acquired files always have actual hashes. No fabricated full-release count is required.

A source-format-binding maps each native selector to its meaning using exact sheet/header/XML/JSON/path locators, source raw type, null markers and documented conversion. Preserve all original fields through raw-record even if not mapped. Required semantic meanings: native record/writing/response identity; source release/component/partition; prompt/task text and identity; original response; learner/speaker/group identity when supplied; corrected response/options; scores with scale; errors/categories/spans with offset clock; rubric/feedback; annotator/model origin; timestamps; media links and original audio clock. An absent meaning is null/raw_only, never a guessed field or substituted learner. Conversion emits corpus-record/evidence/transformation with exact raw links and missingness. LLM context may propose semantic122-leaf mappings, marked inferred rather than original source labels.

If private headers are unavailable, preserve raw intake and show format_unbound for semantic conversion until a documented binding is supplied. This fully defines product behavior without asserting undocumented vendor headers. A default native-column mapping cannot honestly be invented from a product page.

## Optional documented remote adapter

A configured adapter must supply exact HTTPS endpoint/authentication/header/query/body/response schema, credential reference, actual allowed host, dataset version, native count unit and completion marker. Initial request uses the documented initial cursor; each response retains raw bytes, record array, next_cursor or documented end flag and optional source total. Repeat only transient connection/408/429/502/503/504 once within270s operation; respect Retry-After within deadline. Never retry authentication/undocumented format by guessing another endpoint. A next cursor already seen -> pagination_cycle; absent declared completion marker -> incomplete_export. Empty page alone is not EOF unless documented. Resuming uses the saved cursor/page hash; duplicate native IDs keep conflicting raw versions and report conflict. Actual count reconciliation is mandatory for declaring that export complete.

Missing credentials -> credentials_missing. No actual API documentation/adapter -> interface_missing with complete local-export alternative. Unknown native semantic binding -> format_unbound. Missing required members/pages -> incomplete. Rights notices/agreements remain actual metadata; do not create a grant. Operator-supplied login/password is never sent to an LLM or browser bundle. No scrape is substituted for an undocumented private API.

## Doubao participant data

Retain the complete actual participant/group allocation, all responses and attempts, prompt/instruction versions, condition/assignment, pre/post/follow-up records, scores/rubrics, feedback/model settings, exclusions/missingness, media and consent/de-identification metadata as supplied. Preserve participant-response relationships and actual study timepoints. Published summary tables are documentary data, never reconstructed individual records. Missing release remains not_acquired; no generated participants or rows fill it.

Moodrick/NIR public descriptions may inform comparison; private prompts, answer banks, rubrics and exports need actual supplied data/documentation. This adapter contract is finalized; unavailable private native schemas and bytes remain explicitly listed operational dependencies. No runtime source is falsely complete.
