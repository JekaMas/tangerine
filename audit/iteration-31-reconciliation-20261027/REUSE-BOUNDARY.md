# Retained native component source review

The original `native-contract-final.jsonl` contains the exact LF context and
recipe subtest passes. Its adjacent `native-contract-final.receipt.json`
records exit zero and the original 244-case invalidation scope. These original
outputs are retained, not rewritten or rerun. The source anchor `99f8677`
contains the original linguistic implementation and reference set; it is not
presented as a newly invented committed-clean test receipt.

Inspection of `99f8677..ab91a99` found these unchanged inputs/owners:

- The entire `linguistic_coverage_test.go` and `testdata/linguistic-contrasts.json`.
- Embedded taxonomy and recipe registries, and the canonical contrast set.
- The actual `generationRegistry`, `mappingTaxonomyContext`,
  `mutationScopedChanges`, `mutationDifference` and `mutationFamilyMatches`
  function bodies.

`mutation_selection.go` gained the later opt-in `exercise_request.category_ids`
filter in `51b1da6`. The retained `TestLinguisticContextPositive` calls it with
only a single `targets` entry and **no exercise_request**. The new exact-ID map
therefore remains empty; its two non-empty-map branches do not execute. The
selected-identity and complete correct-control context assertions use the same
inputs and path as the retained observation. The family helper is unchanged.

The native recipe test still compares the exact canonical/surface reference and,
when present, its written edit against the unchanged scope owner. Ledger recipe
joins require the original literal canonical and surface to equal that exact
reference. A later illustration or different utterance cannot qualify merely
because it has the same category ID.

This permits only the explicitly recorded context/reference/replay component.
It supplies no original free-text interpretation, empirical frequency, observed
phone, full audio-key mapping, optional-provider qualification or whole-category
acceptance. Every such unmet assertion remains in the original ledger entry.
No old evidence fingerprint is refreshed to hide a semantic source change.

## Directed repair of the new auxiliary adapter

The first new native run at clean `7b490a4` exited1:50selected edges passed
and13second-set auxiliary negatives failed. The adapter incorrectly assumed
every negative had missing observations. Those thirteen original packets supply
valid inputs and a wrong proposed value (or an invented value for an unobservable
teacher trait). The fixture data and production owner are unchanged.

The repair adds the previously ignored `proposed_result` string and a branch
used only when `inputs_missing` is false. It runs the actual population owner,
compares the correct independent fraction with the proposed wrong value, keeps
teacher traits null and compares original inputs before/after. The old
missing-observation branch is unchanged for its actual `inputs_missing=true`,
`invented_value=100` inputs. The positive function, population construction,
reference JSON and application text tests are unchanged. The newly decoded
field is not read on their paths.

Retain the44actual passing physical identities (50logical edges) with the
original nonzero command exit and original source hash. Record the explicitly
reviewed current source hash and unaffected identities separately. Rerun only
the13failed second-set negatives plus their parent container. Reconciliation
must read every original failed identity and require its actual pass in that
directed zero-exit repair; dropping a sibling or treating the first command as
successful is not allowed. Neither metadata nor a refreshed file hash supplies
a missing native observation.
