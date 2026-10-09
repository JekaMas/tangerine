# Provider registration and remaining dependencies

Date: 2026-10-09. Baseline: 6fd4899 on main. Scope: necessary free account setup, existing-account readback and specification reconciliation. No implementation, installation, token exchange, inference, audio generation, purchase or publication. Preserve the unrelated edit in audit/spec-fullness-20261008/GAPS.md.

## Actual account observations

The signed-in ChatGPT Account page displays Pro and the user's previously selected identity. Usage displays automatic reload off. No Tangerine app entry or app-specific purchased-credit exclusion was visible in that readback. Existing credits can still matter even with reload off; these two settings are not equivalent. Financial balances and unrelated activity are excluded from this public report.

OpenAI's current official OSS flow dynamically registers the app during its own OAuth authorization. No separate Platform account or developer client-registration form is needed for this route. Tangerine's specified loopback callback/token adapter has not been implemented. Consequently no Tangerine grant, issued client ID, model catalogue or Responses request is observed. A browser-only signup, Codex login or borrowed Codex credentials would not close that dependency. Sources: [overview](https://developers.openai.com/siwc/token-sharing-open-source), [registration](https://developers.openai.com/siwc/token-sharing-open-source/sign-in), [app usage controls](https://developers.openai.com/siwc/token-sharing-open-source/profiles-and-sessions).

ElevenLabs Free signup is prepared in Chrome. Its Google signup button explicitly accepts Terms of Service and acknowledges the Privacy Policy. The browser tool requires confirmation at that exact step; the user has been asked and the page is retained for continuation. No button accepting terms, Google account selection, account creation or API-key creation occurred. Status is pending_confirmation, not registered. Screenshot is private/local at data/provider-registration-20261009/elevenlabs-signup.jpg. The previously selected identity will be used after confirmation; no replacement password will be created by the agent.

Kokoro and Qwen3-TTS public local models need no account. Local setup/inference is not performed. Azure F0 remains an alternative for SSML rather than an additional required account. Gemini, Claude and separately billed OpenAI Platform accounts are unnecessary for the chosen starter. Existing DeepSeek access is retained; no duplicate account, token-billed call or purchased balance is created.

## Written clarification repaired

Provider setup now distinguishes verified account plan, app-specific authorization, external purchased-credit exclusion, available model catalogue and observed inference. Automatic reload off cannot qualify purchased-credit exclusion. Ordinary on-demand generation remains independent of corpus acquisition, prebuilt exercises and Lab setup.

ElevenLabs Free-generated speech is subject to non-commercial terms and attribution when published. A later upgrade does not retroactively change earlier Free media rights. The spec records generation-time provider/plan and terms provenance without introducing a publication approval gate or changing Apache-2.0 for software. Source: [ElevenLabs publication terms](https://help.elevenlabs.io/hc/en-us/articles/13313564601361-Can-I-publish-the-content-I-generate-on-the-platform).

## Remaining core setup and runtime work

| Dependency | Exact missing evidence/input | Product use and completion | Decision needed? |
|---|---|---|---|
| Tangerine ChatGPT connection | Its own working callback/token adapter, completed OAuth, validated plan-use scope and issued registration | Connect the specified app, retain its protected credentials, read the actual model catalogue. This requires future implementation; existing Pro readback is insufficient. | No new product decision. Implementation remains outside this task. |
| Subscription-only spending | Actual Tangerine per-app setting excluding purchased credits, once registration exists | Disable credit use after limits, record the existing confirmation and observe correct quota exhaustion. Auto-reload off only prevents automatic purchasing. | No policy decision; current no-purchased-usage rule is explicit. |
| Optional ElevenLabs setup | Agreement confirmation, completed Free account and actual plan/model/voice allowance | Finish prepared free signup, inspect entitlements. Secure key provisioning belongs to the selected adapter setup; account creation is not synthesis qualification. | Only the pending browser legal-terms confirmation. |
| Local speech setup | Actual Kokoro assets/dependencies and local rendering; Qwen only if selected | Produce and save the requested exercise audio, observe runtime fit and sound. No registration is needed. | No new product decision; install/run remains outside this task. |
| Main five-step behavior | Actual clean-text and mutation inference, saved text/key/audio, answer checking, exact score/feedback and persistence/resume observations | Implement and run the designed positive/negative cases through real owners. A failed stage must preserve its completed checkpoint. | No new product decision. |
| Acoustic control coverage | Actual target-specific pronunciation/prosody output for a compatible backend | Realize phone/stress mutations when requested. Kokoro cannot claim arbitrary IPA support; use an explicitly selected supporting backend. All122categories remain defined. | No category removal or prior corpus recording needed. |
| Development quality measurements | Selected independent reference fixtures, actual model receipts/context and MLflow/native reconciliation | Measure prompt/context/model changes and grading quality during future AI development. Constructed fixtures are already specified, not executed observations. Ordinary use does not require a prebuilt benchmark. | No new product decision. |

These are unimplemented behavior or missing observations, not unspecified formulas, missing user-flow definitions or unresolved product policy. No universal zero-gap implementation claim is made.

## Remaining optional data, mapped to its consumer

| Selected feature/source | Still missing | How it is used / why it matters only there |
|---|---|---|
| Empirical122category frequency and relationships | Complete native/mapped annotated event populations, exposure denominators, versioned crosswalk and population definitions | Descriptive source-scoped prevalence/co-occurrence; taxonomy structure and generated selection are not empirical frequencies. Unknown remains N/A. |
| Observed difficulty/recommendation effectiveness | Genuine attempts, timing/outcomes and optional follow-up population | Claims about observed difficulty/improvement. Ordinary feedback can target actual misses before population calibration. |
| TET-GOLD-1 full benchmark | The actual explicitly selected minimum732distinct stimuli and their independent expected judgments/observations | Optional full benchmark report; no startup or ordinary-use pregeneration. |
| EFCAMDAT original, SHATZ2020 and OKSUZ2025 | Each separate complete authorized release, dictionaries/workbooks and applicable use terms | Full original-source import and authentic learner examples/statistics. Public Oksuz companion files do not replace any full native original; Cambridge has requested an academic email. |
| DOUBAO-STUDY-RECORDS | Authorized participant/instrument responses, transcripts/media, instrument/source prompts, coding dictionary and reuse terms | Optional study-context import. Paper aggregates do not supply participant records; source prompts are not Tangerine generation prompts. |
| MOODRICK-DATA | Separate complete native export/media, dictionary and source-use terms | Optional authentic simulation/profile/native-feedback import. No private API/account prerequisite. |
| NIR-DATA | Its own separate complete export/media, dictionary and terms | Its separate optional source import. Moodrick data cannot be counted as NIR acquisition. |
| Official L2-ARCTICv5 delivery | Successful authorized download/readback of supplied official links if that original provenance is requested | The full pinned mirror is usable under its recorded provenance; official byte equivalence is unproved and unnecessary for generated exercises. Access email is not download proof. |
| ICNALE linked media | Separately linked recordings/videos not fully downloaded | Optional authentic speaking/media import. All9package archives/text/metadata are already acquired in the prior bounded receipts. |
| Speak&Improve2025 | Eligible release bytes and actual terms | Optional rated learner-speech reference; request history is not acquisition. |

SpeechOcean762, BEA public WILOCNESS2.1/FCE2.1, the full pinned L2 mirror and acquired supplementary JFLEG/EdAcc/DRAL/ELRD/DiPlomat releases keep their prior receipts and provenance. Withheld BEA test gold remains withheld rather than invented. No large download is rehashed or claimed newly verified here. The existing empirical-data-needs.md ledger owns exact acquired-versus-missing scope.

Nothing in this table is an external dataset prerequisite for: user request -> LLM clean text -> LLM mutations -> stored generated audio -> answer -> LLM checking/comments and exact scores. All122categories/recipes,42formulas and11original full-source scopes remain preserved.

## Verification boundary

This increment checks account/UI observations, documentation reconciliation, unchanged scope/graph/fixture definitions and current version hashes. It does not run application/model/audio tests. Previous unaffected green receipts retain their original boundaries. New document/provenance facts invalidate only their associated document snapshot, not earlier scoring, corpus or runtime observations. The application change remains open; prepared registration is not a completed account.

Validation:27affected static checks passed (including constructed positive/negative ledger checks, original-scope/fixture/graph byte preservation and all current version hashes). Strict OpenSpec validation passed after the canonical task update. Graph/discovery inputs are byte-identical to6fd4899; their retained green structural receipts are reused rather than rerun. The unchanged397requirements/412properties/1,648case edges do not become executed behavior. Actual new evidence is only browser account/signup-page readback, with no completed registration or inference.
