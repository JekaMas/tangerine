## ADDED Requirements

### Requirement: CAP-01 Included-only provider access and simple startup
The product SHALL use the current provider-access.v1.json included_only policy, prefer eligible existing ChatGPT-plan Responses plus local Kokoro, preserve original profiles and reject unknown/metered/purchased-credit/overage routes under this policy without silent fallback. The existing GitHub download/run local product SHALL have no application account or mandatory corpus/review/Lab setup.

#### Scenario: CAP-01 Eligible startup route
- **GIVEN** an authorized ChatGPT-plan connection with credit-after-plan use disabled and local Kokoro assets
- **WHEN** the operator generates an exercise
- **THEN** only the selected included LLM route and local speech dispatch, and no Platform/DeepSeek key fallback occurs.

#### Scenario: CAP-01 Metered key is not a subscription
- **GIVEN** a configured DeepSeek key with unknown included API entitlement
- **WHEN** included_only selects that profile
- **THEN** no inference occurs, the actionable billing mismatch is shown and saved playback still works.

### Requirement: CAP-02 Durable provider authorization without application login
Provider connections SHALL use the documented public-client loopback PKCE/OIDC flow, validated identity/granted scope, stable host and issued client IDs, protected rotating credentials and safe metadata. Explicit connect/select/disconnect SHALL never create application accounts, copy Codex credentials or change a frozen running registration. Exact pending state SHALL be the narrow callback-origin exception.

#### Scenario: CAP-02 Reconnect preserves registration
- **GIVEN** an issued registration and stable host identity after restart
- **WHEN** the operator reconnects successfully with the expected validated subject and required scope
- **THEN** the same registration is updated atomically and future calls use that selected binding.

#### Scenario: CAP-02 Denied or mismatched callback
- **GIVEN** an active connection and a pending new authorization
- **WHEN** the callback has a wrong state or lacks plan-use permission
- **THEN** the active connection is not overwritten; wrong state is rejected and absent permission makes that new registration connected_no_usage with zero inference.

### Requirement: CAP-03 Subscription Responses transport and terminal outcomes
The ChatGPT-plan adapter SHALL send the exact supported stateless full context with store=false/stream=true, omit unsupported fields and commit a stage only on response.completed. Actual interrupted/incomplete/failed/usage-limit outcomes SHALL preserve earlier content and native receipts without grading partial text or invoking a new billing route. Account model choices and auth/billing/policy identity SHALL be frozen; credential refresh does not change registration identity.

#### Scenario: CAP-03 Complete streamed stage
- **GIVEN** a frozen supported model and exact user/instructions context
- **WHEN** output events finish with response.completed
- **THEN** the complete visible output is projected through existing tolerant semantics and the actual request/terminal receipt is saved.

#### Scenario: CAP-03 Late quota failure
- **GIVEN** partial output text and earlier clean-text or answer checkpoints
- **WHEN** response.failed reports subscription_sharing_usage_limit_exceeded
- **THEN** that stage remains failed, earlier artifacts remain and the app offers Manage usage/explicit recovery with zero additional provider calls.

### Requirement: CAP-04 Explicit speech and accent control
The existing speech owners SHALL preserve122categories and compile actual selected text/phone/prosody operations only through documented model/voice capabilities, as specified in speech-service-selection.md. Voice/accent design is not phoneme proof. Per-speaker identities, dictionary/conditioning versions, target-specific scope and final WAV/interval provenance SHALL persist. No purchased speech quota or implicit backend substitution is allowed under included_only.

#### Scenario: CAP-04 Scope-local pronunciation dictionary
- **GIVEN** two occurrences of three and a supported English IPA dictionary backend, with only the second targeted
- **WHEN** the render plan compiles the phoneme replacement
- **THEN** only the target segment receives that dictionary, the other occurrence stays unmodified, and actual joined audio intervals/receipts are saved.

#### Scenario: CAP-04 Unsupported acoustic intent
- **GIVEN** local Kokoro and an explicit arbitrary IPA target
- **WHEN** generation/render resolves required capabilities
- **THEN** that request remains saved with a compatible-backend choice; no grammar substitution, removed category or fabricated sound observation is emitted.

### Requirement: CAP-05 Exact empirical inputs and source-scoped reports
The product SHALL apply empirical-data-needs.md and the existing product-data-relevance policy: external corpora are unnecessary for ordinary authored exercises, while selected empirical frequency/relationship/difficulty/benchmark/full-source reports require their actual scoped observations and denominators. All11full original identities/scopes and42equations SHALL remain. Constructed/provider judgments/native source labels SHALL retain distinct origin and unknowns; missing originals cannot be replaced by public companions or supplemental releases.

#### Scenario: CAP-05 Defined population association
- **GIVEN**100fully annotated windows with nA=20,nB=10,nAB=5 and a versioned crosswalk
- **WHEN** a source relationship report is requested
- **THEN** support=0.05, conditional=0.25 and lift=2.5 are reported with population/source/window, without changing the learner score.

#### Scenario: CAP-05 Missing empirical denominator
- **GIVEN** native error examples but unknown annotation completeness or exposure denominator
- **WHEN** a122leaf frequency/relationship or full-source completeness claim is requested
- **THEN** unsupported estimates stay unknown/N/A and missing scope is identified; ordinary generation still works.

### Requirement: CAP-06 Research candidates and actual setup observations
The dated primary-source service catalogue SHALL distinguish current recommendation, possible documented alternatives, installed adapter compatibility and actual observed account/model/voice/hardware quality. Selected setup SHALL retain all exact configuration/secret/provenance owners and positive/negative Lab plans, without pretending research executed inference or buying an unnecessary subscription.

#### Scenario: CAP-06 Existing subscription first
- **GIVEN** the operator reports ChatGPT Pro and DeepSeek access
- **WHEN** setup recommendations are shown
- **THEN** existing eligible ChatGPT plan plus local Kokoro is first, with optional free/subscription speech alternatives and explicit unverified entitlement/quality limits.

#### Scenario: CAP-06 Catalogue is not an adapter
- **GIVEN** a researched Claude/Gemini/Qwen candidate without a compatible installed adapter or actual entitlement observations
- **WHEN** a profile is selected
- **THEN** unsupported dispatch is not invented and no claimed execution/quality/price allowance is fabricated.
