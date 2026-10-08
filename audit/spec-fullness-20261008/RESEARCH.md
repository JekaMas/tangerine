# Primary-source research and resolved distinctions

These observations inform the specification audit. They do not establish downloaded releases, source-use permission, live adapter conformance or measured quality. Source access was read-only. No request was sent to a person or inference provider.

## DeepSeek Responses transport

The official transport reference resolves instruction-role, reasoning-budget and response-format distinctions. Their explicit specification binding appears in docs/llm-configuration.md. Complete schema-keyword qualification remains open. [DeepSeek API reference](https://api-docs.deepseek.com/api/create-response/)

## SpeechOcean762

Author documentation also lists `spk2utt`, `spk2age` and `spk2gender`, beyond the abbreviated initial inventory. Preserve all metadata and individual ratings. The documentation illustrates a completeness-scale difference between detailed and aggregate data; freeze each acquired field's actual scale and quarantine unexplained mixtures. Phone markers and explicit mispronunciation records must remain distinct from ratings. An author-repository revision and the selected OpenSLR archive are separate identities. [Author README](https://github.com/jimbozhang/speechocean762/blob/main/README.md), [official release page](https://www.openslr.org/101/)

## L2-ARCTIC v5

Official documentation separates `/textgrid` automatic alignment from `/annotation` manual records. Full source includes README, LICENSE, PROMPTS, read-speaker directories and the suitcase extension. Read WAV uses44.1kHz. Manual phone markers distinguish canonical/perceived phone and substitution/addition/deletion; `err` and `*` preserve uncertainty/deviation. ARPAbet tiers and IPA comments must retain original representation before an approved conversion. These facts tighten component obligations; a complete parser and product-use permission remain open. [Official documentation](https://psi.engr.tamu.edu/l2-arctic-corpus-docs/), [source/access page](https://psi.engr.tamu.edu/l2-arctic-corpus/)

## W&I+LOCNESS and FCE

The BEA totals3700 texts,43169 sentences and801361 tokens describe the combined release, including100 native LOCNESS essays. They are not W&I-only counts. Native essays occur in dev/test; no native training set is released. M2 retains half-open token edits, correction strings and annotator identities; `noop` represents a no-change judgment. Source data release2.1 is distinct from the evaluation-tool version. The current BEA page announces evaluation with ERRANT3.0.0 replacing2.0.0; preserve the chosen tool/version instead of assuming old and current evaluations are equivalent. FCE's underlying1244 answers are not a verified acquired M2-record count. [Official BEA data, M2 and evaluation documentation](https://www.cl.cam.ac.uk/research/nl/bea2019st/)

The authors' ERRANT code preserves detection-only `UNK`/`Um` and no-change annotations. A faithful parser must retain these distinctions; they do not automatically map to a narrow Tangerine leaf. [Author code](https://github.com/chrisjbryant/errant/blob/main/errant/commands/m2_to_m2.py), [author documentation](https://github.com/chrisjbryant/errant/blob/main/README.md)

## EFCAMDAT

The official page distinguishes full releases from cleaned and error-coded derivatives. The posted2023 agreement describes academic private study and noncommercial research access, with conditions for derivatives. That document is evidence about the published terms, not a grant of this project's particular product or cloud-transfer use. Exact selected-release schema and intended-use permission remain unresolved. No access form was submitted. [Official resource page](https://ef-lab.mmll.cam.ac.uk/EFCAMDAT.html), [posted agreement](https://ef-lab.mmll.cam.ac.uk/assets/pdf/EFCamDat-User-Agreement-2023.pdf)

## Azure synthesis and advisory observations

Microsoft documents locale-specific phoneme alphabets and rejection of unknown phones. Requested SSML does not prove the realized target. Pronunciation-assessment responses have named statuses and offset/duration units of100ns; those require an explicit conversion to final-audio milliseconds. The detailed lexical field differs from display/ITN text. Preserve raw responses, reference conditioning and missing outcomes. [SSML pronunciation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-pronunciation), [short-audio API](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-speech-to-text-short)

## Audio methods

ITU-R BS.1770-5 defines loudness and true-peak measurement algorithms. FFmpeg exposes measurement/normalization options whose defaults and resampling can affect results. A numerical threshold alone does not select a complete method. GAP-034 requests an exact algorithm/tool/options contract; this audit does not silently change inherited QC thresholds or adopt a new normalization procedure. [ITU recommendation](https://www.itu.int/rec/R-REC-BS.1770-5-202311-I/), [FFmpeg filter documentation](https://www.ffmpeg.org/ffmpeg-filters.html)

## API and canonical bytes

OpenAPI3.1.1 can document the missing operation/request/response/security contract; naming a standard does not fill that contract. RFC8785 specifies JSON canonicalization with numeric/Unicode constraints. It is a possible explicit future choice, not a necessary replacement for the existing rule to hash immutable stored bytes. No cross-language canonicalization is claimed or silently introduced. [OpenAPI specification](https://spec.openapis.org/oas/v3.1.1.html), [RFC8785](https://www.rfc-editor.org/rfc/rfc8785)

## Resolved by actual package reads

- Taxonomy, schemas, five prompts, formulas, scoring and validation policy are present in the recovered archive. The quoted missing-attachments statement is obsolete.
- Explanation `option_id` is explicitly null in the reference validator. Do not invent an explanation-options table to close a nonexistent gap. Feedback's approved-rationale identity contract remains GAP-021.
- `violated_proposition_ids` means existing forbidden propositions in the data dictionary. That meaning is present; the complete status/credit transformation remains GAP-020/022.
- All core zero-denominator reasons can be recovered from the actual reference `values` table. FORMULAS.md records them explicitly. No imported executable was run.
- Existing thresholds, deadlines, retries, synthetic-only origin and human review requirements are defined. Unperformed live calls, missing real recordings/people and unbuilt images belong in EVIDENCE.md.

The publisher PDF and some vendor pages had access/time-out limitations in the earlier source recheck. No underlying Doubao or vendor release has been verified. Do not convert a failed fetch into a claim that data cannot exist; request an actual authorized release contract in GAP-044/045.
