# Local architecture

An exercise is a prepared recording with a versioned answer key.
A claim is an assertion extracted from the exact teacher answer.
A detection unit is one independently correctable linguistic event.
An evidence record links an observation to exact artifact bytes.

## Components

`web` serves the local interface and proxies `/api/v1/` to `api`.
`api` owns state changes, schema checks, evidence links, provider admission, and exact arithmetic.
`postgres` stores typed documents, indexes, references, operation state, and the audit log.
`minio` stores immutable private bytes.
`speech` compiles typed speech requests and calculates registered audio measurements.
The operator starts these containers through one supplied launcher.
Only the web port binds to the host, at `127.0.0.1:3000`.

There are no user accounts, user sessions, access roles, tenants, or cloud identity prerequisites.
Person records describe actual reviewers and consent subjects. They do not authenticate people.
A process token protects private service calls. It is not a user identity or an assessment secret from the installation owner.
The web view hides answers at the required phase. The installation owner can still open preparation activities or inspect local storage.

## Preparation flow

The operator saves a versioned blueprint.
The API freezes the generation profile, taxonomy, source selections, and allowed-use grants.
The generator creates a schema-valid candidate with canonical text and separate mutations.
The linguistic audit identifies text concerns. It cannot approve a case or invent acoustic observations.
The speech service makes each ordered turn and assembles the exact delivery WAV.
Mechanical and advisory measurements refer to the final file digest.
Two independent people submit observations before key disclosure.
After disclosure, reviewers reconcile observed events, controls, corrections, and rationales.
An unresolved disagreement blocks publication until genuine adjudication resolves it.
Two final approvals bind the same key, context, and audio digest.
The API publishes that immutable version only after all guards pass.

## Teacher flow

The API creates an attempt when the operator selects Start.
The teacher activity receives public context, component requirements, audio, and a blank answer field.
It receives no transcript, target categories, error count, planned intervals, or hidden key.
The teacher listens and writes an English or Russian answer.
On submission, the API commits the answer, its digest, the case identity, and the effective policies.
The API acquires the evaluation lease and calls the provider stages synchronously.
Extraction has no key or transcript. Mapping receives only the authorized frozen context.
A separate mapping audit does not receive the first mapper output.
The API derives counts and exact fractions from accepted semantic decisions.
Feedback cites accepted decisions and approved unit rationales.
The API saves the result before it returns the response.

An unresolved semantic issue produces provisional item evidence and no final aggregate.
A technical failure preserves the answer and permits only the declared explicit retry.
Stored playback does not depend on provider availability or generation budget.

## Local activities

Library lists published eligible cases and historical cases with explicit availability labels.
Prepare creates and revises blueprints, candidates, recordings, and source selections.
Review records actual people, blind observations, key disclosure, final decisions, and adjudication.
Practice contains the listener, answer form, pending response, result, and retry action.
Disputes preserves original results and appends reviewed revisions.
Sources shows each required release, rights, credentials, formats, import counts, and blockers.
Configuration stores key references and explicit use declarations without browser disclosure of secret values.
Maintenance provides explicit recovery, cleanup, backup, restore, and qualification commands.
No maintenance task starts a background queue.

## Trust boundaries

All supplied text, source files, teacher answers, and model outputs are untrusted data.
They cannot invoke tools, execute SQL, create XML instructions, select external URLs, or approve themselves.
Only installed adapters use predeclared outbound origins.
Source transfer requires permission for the exact recipient, purpose, content class, and current time.
Schema checks do not prove semantic truth. Human gold, bounded model decisions, and abstention remain necessary.
