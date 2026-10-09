# EFCAMDAT releases

The required scope includes the full second release and both named derivatives.
Register EFCAMDAT-R2, EFCAMDAT-SHATZ2020, and EFCAMDAT-OKSUZ2025 separately.
A derivative does not replace the full source or another derivative.

Owner access page: https://ef-lab.mmll.cam.ac.uk/EFCAMDAT.html
Published agreement: https://ef-lab.mmll.cam.ac.uk/assets/pdf/EFCamDat-User-Agreement-2023.pdf
The owner page supplies access by an approved Google account for eligible academic researchers.
The agreement restricts ordinary use to the stated academic/non-commercial scope and imposes additional conditions on derivatives and transfer.
Obtain separate written permission for commercial use, unrestricted distribution, or other uses outside that grant.
Do not assume that an API key or a Google account changes the terms.

## Second-release XML

The author guide describes selection/meta and selection/writings/writing structures.
Retain the selection ID and every metadata field, including title, version, URL, key/user fields, date, nationality selection, and unit selection.
Treat account-related metadata as private source data. Do not send it to an LLM.
Each writing has source id, level, and unit attributes.
Retain learner id/nationality, topic id/text, date, grade, original text, corrections, and annotations.
Nationality is source metadata. It is not a direct observation of an individual's first language.

Inside text, preserve mixed XML content in exact document order.
A change element contains the original selection and its tag/correct information.
Build the original-text view from literal text and selection content, excluding correction suggestions.
Build a proposed corrected view only through a separate declared transformation.
Preserve empty selections, empty corrections, tag symbols, multiple corrections, and ambiguous/nested markup.
Compute offsets against the original-text projection, not against XML markup bytes or corrected text.
Store XML byte locators and the projection method so both representations remain traceable.

Retain annotation id, sentence count, sentence id/tokencount, token id, lemma, pos, head, rel, and token text.
Keep each annotation layer distinct. The source's automatic parse is not a manually validated syntactic truth.
Source teacher corrections are pedagogical feedback. They are not guaranteed exhaustive error gold.
The label map retains AG, AR, AS, CO, C, D, EX, HL, IS, MW, NS, NSW, PH, PL, PO, PR, PS, PU, RS, SI, SP, VT, WC, WO, and XC.
Broad labels generate candidate mappings only. Unknown labels remain preserved and unbound.

The guide's XML examples do not prove that a privately supplied full release uses an identical complete schema.
During semantic conversion, compare actual release documentation and all observed elements with the exact `source-format-binding`.
Unknown required semantics keep that semantic projection unbound; complete raw intake remains usable. They do not disappear from the full-source inventory.

## Shatz2020 complete derivative

The [publisher report](https://benjamins.com/catalog/ijlcr.20009.sha) identifies XML-to-tabular curation and two prompt samples. The [author's Cambridge thesis, chapter 2](https://api.repository.cam.ac.uk/server/api/core/bitstreams/c89528c0-46af-436c-8b6c-7597ceb2908b/content) supplies these expectations: 406,062 first-sample and 317,220 second-sample texts (723,282 combined), 120/89 topics, 11 nationalities, EF levels 1–15/CEFR A1–C1. Both samples and supplied intermediate versions, variable glossary and R scripts are required. The second sample retains first-sample prompt text for structural continuity; actual second prompts were unavailable. Do not treat that copied prompt as observed elicitation. This derivative was made from annotation-free text; it does not promise retained teacher corrections. No-correction is source missingness, not import failure. Publicly described cleanup replaces line-break markup, decodes quotation markup and changes ampersands; preserve the supplied cleaned text and transformation provenance rather than redoing cleanup on every import.

Owner-listed [Shatz folder](https://drive.google.com/drive/folders/1AJy7u_PHV02HupcOZ_DDJYPW7F6rPwoL?usp=share_link) redirected anonymous access to Google sign-in on 2026-10-09. The actual variable glossary and complete workbook headers were not available to this session. A third-party notebook is not the source dictionary. Bind actual sheet/header names at intake; never invent them. All raw sheets/cells/fields survive regardless of binding.

## Öksüz2025 complete derivative and public analysis companion

Keep source ID EFCAMDAT-OKSUZ2025 stable. [Published article](https://journals.sagepub.com/doi/10.1177/02676583251395876): online December 31, 2025, issue April 2026; the owner page's under-review wording is stale. It describes 527,758 writings, 104,541 learners, 34,037,354 tokens, 11 national-language groups,EF 1–12/CEFR A1–B2, paired original/teacher-corrected texts and POS layers. Article omission/substitution are derived by comparing obligatory article contexts; overuse was excluded. Suppliance in obligatory context (SOC)=correct uses/obligatory contexts, not all-error accuracy or target-like-use with overuse. Zero contexts means unavailable ratio; never 100% or 0 by default. Published totals are expectations, not observed local counts. The article also prints 8.33 mean writings/learner, which differs from 527,758/104,541; preserve the printed mean as documentary metadata rather than using it to fabricate counts.

The [author-deposited manuscript, appendices 2–4](https://api.repository.cam.ac.uk/server/api/core/bitstreams/e2e1ef4c-65fa-46be-b086-0876099517ac/content) gives cleanup stages, paired-text markup and retrieval limitations. Preserve original corrections, POS origin and analysis exclusions. Its Appendix 4 prints F1=0.1 for 100% precision/recall and 0.935 for 96%/90%; retain those printed values as documentary values with inconsistency notes, never use them as Tangerine's calculated metrics. The published DOCX supplement is linked but its retrieval returned403 in this session; the deposited appendices are separately versioned documentary evidence, not a claim that the final supplement was read.

The article links [public OSF project r638b](https://osf.io/r638b/). Anonymous OSF API metadata was readable. Its complete listed tree at research time has two Data CSVs and two Statistical Analysis files. Exact member metadata is in domain/source-research.v1.json. Project metadata names CC0-1.0; retain that notice with underlying Cambridge provenance rather than declaring all EFCAMDAT rights waived. Neither public analysis files nor article/supplement license substitutes for the owner-hosted full error-coded workbook release. That [owner folder](https://drive.google.com/drive/folders/1P28gRsF3W4A4_kcjTmze3AVBCQIdKslD?usp=share_link) redirected anonymous access to sign-in.

The [authors' article_accuracy.Rmd](https://osf.io/42ynj) was retrieved as inert documentation (26,784 bytes; upstream SHA-256 verified). It reads ef2_def_analyse.csv and ef2_indef_analyse.csv and explicitly selects these native fields:

| Native field | Target meaning and conversion |
|---|---|
| writingID | record_id as unchanged text; preserve any numeric source representation in raw data |
| learnerID | learner_id as unchanged text; genuine grouping across article tables |
| level | EF teaching level; integer conversion; raw value retained |
| unit | Native lesson unit; integer; retain separately from task/prompt identity |
| nationality | Source nationality code; nationality, never directly observed personal L1 |
| topic | Native task/topic grouping as text; not automatically an exact prompt |
| word_count | Source word count; integer; do not replace with Tangerine tokenizer count |
| Noof_obl_context | Article-specific obligatory-context count; integer, source population |
| SOC_scores | Source article-specific SOC ratio; decimal and raw precision retained |

The nine names above are source-code-confirmed consumed fields. Header-only HTTP 206 range requests subsequently verified the full native headers: 19 columns for the definite file, 20 for the indefinite file. That header-only inspection did not read records. The subsequent authorized acquisition downloaded all four OSF companion members and verified their upstream SHA256 hashes. Full CSV inspection counted 453,958 definite rows and 417,043 indefinite rows, with unique writingID values within each table and consistent 19/20-column widths. These two counts are not additive unique essays. See audit/corpus-acquisition-20261009/oksuz-full-csv-inventory.json and download receipts. Exact ordered headers and header receipts are recorded in domain/source-research.v1.json and the current audit. The source variable glossary and ambiguous text-column meanings still require owner documentation; observed cells do not justify invented semantic bindings. Raw acquisition does not establish a finalized semantic source-format-binding or normalized_complete; neither has been observed. Use vendor_export with explicit CSV dialect in the release binding; do not pretend CSV is XLSX. The two CSV components carry distinct definite/indefinite article identities even when writingID matches. Unique scripts are not the sum of both table row counts.

The additional header-confirmed fields are: unnamed first column, topicID, text, original, corrected, orig_POS, corr_POS and Noof_Correct_supp. Definite errors use omis_errors/subs_errors. Indefinite errors use Omission_errors/Phonological_variant_errors/Substitution_errors. Preserve exact case, order and all fields; do not homogenize the native error names. Bind the blank first header by ordinal selector csv:column[0], retain its original empty name and treat it as raw-only, not writing identity. topicID is distinct from topic; do not collapse either into unit. Original/corrected/POS columns retain paired source content; text's exact role relative to original remains explicitly unbound until documented. Count columns have source population context; never infer localized spans or acoustic observations from counts. Phonological_variant_errors in an article analysis is not a phone-level audio label. Its exact inclusion in SOC requires the native method dictionary; don't silently merge it into substitutions. Normalized count fields use integers, SOC uses a decimal ratio with original precision, text/POS fields preserve strings; missing markers are bound from the actual release, not guessed from the header.


The R document recodes kr/cn/de/br/ru/sa/mx/tr/fr/it/jp and derives art_type,nat_lang,obl_context,L1_type,level_cat,level_scaled,level_scaled_sq,correct,incorrect. Preserve these as derived analysis metadata. Its cut breaks4/7/10/13 use default right-closed bins, assigning level 4 to A1, unlike the article's1–3/4–6/7–9/10–12 bands. Tangerine's normalized CEFR uses the documented article bands, retains source-derived level_cat separately and records the discrepancy. The document obtains correct by rounding SOC_scores*obl_context: this reconstructs an analysis count, not exact native error gold. Do not create error spans from a SOC ratio.

## R2 documented XML field bindings

[Huang et al.'s second-release guide](https://static1.squarespace.com/static/5e9da0a288532d74bde29f9c/t/5e9ef9cc13418a090e2e3152/1587476965096/EFCamDat-Intro_release2.pdf), pp.15/18, describes XML selection/export. Figure 10 was visually inspected. Documented relative locators: writing/@id,@level,@unit; learner/@id,@nationality; topic/@id and text; date; grade; text mixed content; text/change/selection; text/change/tag/symbol,correct; annotation/@id; annotation/sentences/@count; sentence/@id,@tokencount; token/@id,@lemma,@pos,@head,@rel and token text. These are a documented profile, not a discovered complete XSD. Preserve every observed extra element/attribute. IDs remain text, integers/decimals get separate normalized values, source-local dates retain original strings without guessed timezone. Correction offsets are computed on the declared original projection; no original phone/timing annotation is inferred from writing.

## Published agreement and intended-use settings

The public 2023 agreement is available and hashed in this audit; it is no longer an unknown agreement. Clauses2.1–2.3 provide academic/noncommercial study, conditions for derivative deposit on the Cambridge portal and brief teaching/publication excerpts with attribution/disclaimer. Other transfer/distribution/use requires Cambridge written consent. An approved account and applicable supplied permission remain operational inputs. Apache-2.0 applies to original Tangerine software, not these corpora. Preserve license notices as ordinary source metadata and saved intended-use settings; no permission graph or legal reviewer workflow is added.

## Leakage, completion and remaining artifacts

Join genuine source writing/learner/task identities across releases; documented derivative links take precedence. Exact text hashes are possible-duplicate evidence, not identity proof. Related records share a connected split group. Retain all original partitions, intermediate files, sheets, scripts as inert bytes and supplied documentation. Unknown fields/corrections stay raw-only or explicitly absent. Full raw intake and complete normalized data are separate claims. Expectations and upstream metadata hashes are not local acquisition receipts.

Positive: separately reconcile full R2, both Shatz samples and supplied intermediate/glossary/script members, and the full Öksüz original/corrected/POS/error-coded release plus all supplied analysis companion files. Preserve source differences and genuine grouping.
Negative: a 406,062-row first sample, public analysis CSV pair alone, copied alternate prompt, ratio-derived invented spans or rounding-derived counts cannot stand in for all three full releases and native gold. Correct imported evidence can still be used without a full-bank approval prerequisite.

Actual remaining release files/dictionaries/access are precisely listed in [the current input ledger](../../../../audit/source-contract-research-20261009/REMAINING-INPUTS.md). No corpus records were downloaded.

## Current access requests

On 2026-10-09 the selected user account sent the EFCAMDAT administrator a complete-release/derivative/native-dictionary/use inquiry. Viewer access requests to the owner-linked Shatz and Öksüz Drive folders visibly returned Request sent. The administrator replied that an academic email is required; the selected personal Gmail cannot obtain access through that route. Access and workbook bytes have not been granted. The downloaded OSF companion remains a separate published component, not the full R2, Shatz or Öksüz workbook release. Outreach is recorded in audit/corpus-acquisition-20261009/outreach.json.
