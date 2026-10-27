# JFLEG written-correction supplement

JFLEG adds native written originals and alternative fluency/grammar repairs. It is a supplemental source alongside the eleven original full-source scopes. Ordinary topic → clean text → mutations → speech → answer → scoring still works independently of all source imports. Importing or browsing JFLEG does not generate an exercise, dispatch an LLM, create acoustic gold or change any learner score.

The selected complete release is the already acquired owner repository at `ee06ff806a208aba815ac45313f4e750a48330a5`. Retain all 29 owner files and the original archive as inert source assets. Keep the owner's README, paper, experimental dictionaries and scripts. Never run their code during intake. The owner's root README is the authority for core file meanings; the nested evaluator README is a different document.

## Native inventory and identity

| Representation | Development | Test | Meaning |
|---|---:|---:|---|
| Original `.src` lines | 754 | 747 | The owner's intended system input |
| `.ref0` through `.ref3` lines | 3,016 | 2,988 | Four supplied correction positions per original |
| `.spellchecked.src` lines | 754 | 747 | Separate source tool output; never a replacement for the input |
| Experimental M2 sentences | 754 | 747 | Unofficial converted view, not additional originals |
| Experimental M2 annotation rows | 11,611 | 10,938 | Tool conversion labels and offsets, not Tangerine categories |

The 100 manual-analysis rows, 1,629 pairwise rows and four sample rows remain experimental native CSV records with their original fields. Original text and every reference position stay intact even when reference strings are identical, unchanged, awkward or incomplete. These views yield 34,789 retained native rows and 1,501 primary written examples, not 34,789 independent exercises.

An example's logical ID is `dev:<zero-based line index>` or `test:<zero-based line index>`. Join `.src`, each reference and spellchecked text only within the exact same native directory, partition and line index. Each text carries its actual member, admitted asset ID/SHA, native line index and line terminator. Preserve whitespace, spelling, tokenization and Unicode. Missing references are absent, with `reference_completeness: partial`; do not infer text from adjacent lines or another partition.

A versioned `group_id` joins one original and its alternatives across exports and repeated imports. It is a reference family, not an invented learner or author identity. Preserve JFLEG's own `dev`/`test` naming: their relationship to GUG's earlier split names must not swap JFLEG partitions. Portable datasets mark them `development` and `held_out`. Using test material for development forfeits an unseen-test claim; export is not itself proof of an unseen experiment.

## Annotations and derived mappings

Source-provided corrected text has origin `source_annotation`. The spellchecked text and unofficial experimental M2 have origin `source_tool_derivation`. Manual/MTurk codes are `source_experimental_annotation`. Retain their native dictionaries: manual `A/O/U`, `F/M` and `S` codes remain source codes, not a crosswalk to Tangerine's 122 leaves.

Each reference also receives a **coarse text difference**, derived by `unicode-common-ends-v1`: find the maximal common codepoint prefix, then maximal common suffix that does not overlap that prefix. Save the original and reference half-open codepoint spans and their exact text. Replacing the saved original span with `replacement_text` reproduces the reference; equality is `kind: unchanged`. This is an exact whole-difference summary. It neither computes minimal linguistic edits nor assigns categories, individual error counts, simultaneous mutations or audible intervals. `linguistic_alignment: not_computed` and `category_mapping: not_supplied` make those limits explicit, including repeated-word ambiguity.

The selected owner's unofficial M2 contains 19 out-of-bounds edit annotations affecting five sentence rows. Preserve all 24 affected native rows, raw invalid flags and source warnings as experimental metadata. `tool_annotation_usable_as_gold: false` prevents their presentation as admitted gold; their presence does not quarantine the independent original/reference family. Generic M2/invalid-primary admission retains its existing behavior. Do not silently clamp, repair or project those bad offsets into original text.

## Import and persistence

Use the existing local Sources archive/directory intake, release manifest, documented native preset, staged rows, frozen parser/method, mapping checkpoint and atomic source commit. JFLEG uses parser version `source-native-jfleg-v1`. No new service or migration is required. The complete named release requires all 29 owner members and the documented 754/747 counts in each of its six parallel core files, both M2 sentence/edit populations and all three experimental CSV populations. A partial upload remains browsable and exportable without a false complete-release claim.

The full staging phase precedes reference projection. Load the parallel rows once per import/resume, then project originals through the existing accepted-write owner. On interruption, reopen the saved association and resume staged work; accepted rows remain trusted. Do not repeatedly re-admit assets, reparse originals, recalculate differences or verify saved hashes during readback. Full-release assessment is saved at completion rather than used as a recurring read gate.

## Examples and portable evaluation datasets

Sources shows a separate JFLEG card and, after opening an import, written examples. Each disclosure shows the original, every supplied reference, separate spellcheck and the derivation/provenance details. Refresh retains displayed examples after temporary failure. The shared request owner logs diagnostics, retries transient reads and then gives authored recovery guidance; backend payloads are not shown to the user. No JSON editing or source-qualification approval is needed to browse or download.

Refresh stays available during reads and supersedes any older example-page response or error. A late page cannot append to a freshly reset list or clear a newer loading state. The same precedence applies within saved issue history. Dataset exports have their own progress and recovery state: refreshing examples does not cancel an explicitly requested export or prematurely enable another one. Leaving the selected import ignores late results. Partial imports describe only their actual references; no-reference/empty states retain working read/download controls without inventing examples.

The existing authenticated local source API gains:

- `GET /api/v1/imports/{id}/corrections?limit=20&cursor=<opaque cursor>&partition=dev|test` returns `{items, next_cursor}`. Empty partition reads both. The tuple cursor follows saved member/line order. Limits use the existing small-page convention (default 20, maximum 200).
- `GET /api/v1/imports/{id}/corrections?format=dataset&partition=dev|test` downloads a `source-correction-dataset` document. The ordinary buttons export 754 development or 747 test examples. Empty partition exports all 1,501. A partial import exports only its actual saved originals/references.

The dataset includes release/version/origin/manifest, source partition, source terms/attribution, scorer version and typed examples. It is `kind: written_correction_references`. These are reference datasets for written-correction examples and native evaluation; no generated dialogue, teacher answer, taxonomy label or audio ground truth is fabricated to fit a different Lab task schema. It does not automatically condition the ordinary generation path or claim a model benchmark.

## Local evaluation consumer

The existing storage-backed `tangerine lab` command accepts `action: source-correction-evaluate` with `payload: {dataset, outputs}`. Each output is `{example_id, text}`. Admit fresh portable input once through `source-correction-evaluation-request`; evaluation trusts that admitted in-memory dataset. Do not use the storage-free `lab-json` command for this action. In the existing local Compose stack, the storage-backed invocation is:

```sh
docker compose --env-file .env --env-file data/config/runtime.env \
  -f deploy/local/compose.yaml exec -T api /usr/local/bin/tangerine lab \
  < local-evaluation-request.json
```

This is internal evaluation tooling. Ordinary source browsing and dataset downloads use the Sources controls.

The exact scorer is `source-reference-membership-v1`, policy `exact_native_text_v1`. It compares strings without normalization, preserves all matching reference IDs and supports more than one output per logical original. A row is `reference_match`, `not_in_reference_set` or `unknown_example`, with `semantic_judgment: not_run`. An unseen correction can be valid; membership never calls it incorrect or becomes a semantic/learner grade. Totals record logical examples, submitted outputs, reference matches, outside-set/unknown outputs, covered logical examples and unsubmitted examples. Retain the admitted dataset and actual outputs once through the existing private asset owner. The saved report identifies that input asset, source version/manifest/partition and scorer; return both asset IDs and zero provider calls. Report readback can therefore reproduce what was compared without re-importing or revalidating stored data. No model/client exists in this evaluation owner.

This native test establishes that all supplied references survive and can be consumed. It is not GLEU, a reproduction of the source paper, a linguistic-accuracy result or qualification of an LLM. The bundled source evaluator remains inert. Future selected model experiments can consume exported references under their existing authorization and terms; no model experiment is required by this import.

## Terms and provenance

The acquired owner README states CC BY-NC-SA 4.0 and requests citation of Napoles, Sakaguchi and Tetreault (2017), and the GUG origin paper by Heilman et al. (2014). Retain that notice and attribution with source-derived exports. Tangerine's Apache-2.0 software license does not replace the data license. No commercial, external-transfer, training or voice-cloning permission is inferred. This iteration uses private local, noncommercial source examples/evaluation and creates no new permission ceremony.

Source evidence: `audit/corpus-acquisition-20261009/jfleg-owner-snapshot-receipt.json`, `jfleg-revision.json` and `jfleg-m2-corrected-inventory.json`; actual native admission/import/consumer observations: `audit/iteration-36-jfleg-20261027/`. All claims refer to that selected acquired commit, not an assumed future upstream release.
