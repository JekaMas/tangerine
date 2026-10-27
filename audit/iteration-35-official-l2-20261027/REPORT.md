# Iteration 35 — Official L2-ARCTIC application import

Status: accepted; complete committed-clean I35 selection passed8/8 at47d171d. Canonical
checklist: OpenSpec tasks.md, iteration35. Entry revision: eb6ac96.

The actual user selected DATA-07: the complete official v5 archive already
admitted in I27, full native normalization in disposable application dependencies,
speaker/layer/media/provenance preservation, counts, durable resume and readback.
The original source ZIP is the byte source. Its admission metadata is reused;
no download, corpus rehash campaign, provider call, installation or user-stack
change is performed. Unaffected historical greens retain their original scope.

## Concrete repairs

1. **Accepted stream storage reuse.** Ordinary new uploads still admit bytes once.
   A private shared storage tail now also accepts retained admission metadata;
   there is no public trusted-digest endpoint. Existing source_file rows return
   without reading a stream. Short failed writes cannot become linked files.
2. **Declared speaker context.** The official README supplies 24 speaker rows,
   declared gender/L1 and source read/manual counts. Those rows now normalize
   through a source-specific parser and join transcripts in memory. Conflicting
   or absent declarations remain unknown; no accent/L1 stereotype is inferred.
3. **Native tier order.** Each interval/point retains its one-based tier_index
   alongside original name, kind, tier-local index, label and exact decimals.
   Repeated/unnamed and mixed point/interval tiers therefore stay distinguishable.
4. **Ancillary comments.** The official README documents additional annotator
   comment tiers. Supported interval/point ancillary tiers, including unnamed
   tiers, normalize structurally as ancillary_comment with no linguistic
   interpretation. Unsupported structural classes stay raw-only; uninterpretable clocks and invalid native
   interval structure retain their original severity. Comments are not precise IPA/gold.
5. **Conversion provenance.** New native L2 imports identify the additive
   conversion as source-native-l2-v5-v2 in the frozen method, report, corpus
   records and transformations. Accepted earlier versions remain trusted and
   unchanged. Other adapters keep their existing version selection.

6. **Current diagnostics.** Count findings use current named populations and
   numeric expectations; recovered findings remain historical. Earlier code
   displayed stale count warnings and a Go pointer instead of an expected count.
7. **Clock representation and source quality.** Correct binary64 serialization
   is distinguished from an actual native/media extent mismatch. The latter
   preserves the original annotation, actual WAVE duration, unverified alignment
   and unknown processing rate. It does not become an invented resampling claim
   or a gate on lossless normalization. Generated-exercise timing is untouched.
   Primary MFA1.0 source code does not establish the HKK processing provenance.
8. **Bounded traversal.** The live old query rescanned333,641 accepted rows to
   fetch64 staged rows (773.586ms). The corrected keyset probe fetched64 rows
   using15 shared blocks in0.195ms. Sparse accepted ranges, end/foreign import
   and crossing member/table boundaries have actual native race observations.
   These are bounded diagnostic probes, not general performance guarantees.
9. **Ordinary test packaging.** New pure units now own their literal assertion
   helpers and compile/run in an empty copied Go module without native fixtures.

## Evidence and proof boundaries

PLAN.json fixes independent official speaker/file/layer and corrected native
operation populations before full conversion. Prior I27 admission and corrected
I13 native-grammar counts are inputs, not newly observed imports. The new fixture
copies official members through the real private asset owner and drives the real
parser, staging, projection, commit and HTTP handlers against PostgreSQL/MinIO.
No native row, normalized result, corpus license or model decision is substituted.
Native tests retain actual positive and negative storage, parser, metadata,
unknown/ambiguous context and clock behavior. Full execution/readback and exact counts passed. The complete committed-clean I35 receipt is recorded in ACCEPTANCE.json.

The harness deliberately interrupts staging and mapping. Database reopen, stale
revision/incomplete-commit rejection, unchanged accepted-row contents, explicit
foreground resumes and final full application status/readback are required.
The conversion uses the existing270-second operations and persistent cursors.
Whole-population development assertions do not become ordinary-use checks.

UI/UX and product typography: not applicable to this backend/source increment;
no web presentation, interaction or learner-flow owner changes. Actual production
source record/status/progress/media handlers are included in native readback.
No screenshot or browser-interaction evidence is claimed.

All122 taxonomy IDs/recipes,42 formulas and11 source scopes remain preserved.
Native source annotations are optional data, not a complete project taxonomy gold
or a prerequisite for independently generated exercises. CC BY-NC4.0 source
terms remain separate from Apache-2.0 software and do not invent model-transfer
or commercial permission. Corpus bytes and private test dependencies stay local.

Research: the actual official README and original [MFA1.0 corpus implementation](https://raw.githubusercontent.com/MontrealCorpusTools/Montreal-Forced-Aligner/v1.0.0/aligner/corpus.py)
were inspected. The latter reads input WAVE durations/rates; a16k timestamp
lattice alone therefore remains an inference, not measured resampling history.
No source code from that corpus or upstream project was executed.

## Actual full-release results

- 84,296 release assets linked, including all25 nested containers, four original
 documents, every native file and the original delivery ZIP.
- 26,889 original WAVE/transcript links:26,867 read and22 suitcase, with actual
44,100Hz mono16-bit clocks.
- 24 source speaker rows across six declared L1 groups.
- 30,488 TextGrid files:26,867 automatic,3,599 manual read and22 manual suitcase.
- 1,547,927 intervals plus26,889 transcripts and24 speaker rows:1,574,840
 accepted normalized rows. No staged, raw-only, rejected or quarantined rows.
-Read operations14,098/3,420/1,092 and suitcase1,673/456/90 for substitution/
 deletion/addition agree with the independent pre-execution receipt.
-All1,574,840 raw asset/hash/transformation associations and all1,547,927
 labels/boundaries/tier ordinals are preserved.89,849 bareS/D labels remain
 non-errors,273 unknown perceived realizations and1,823 approximate labels
 remain uncertain;44 unnamed ancillary intervals remain present.
-Initial400 staged rows survived actual interruption/reopen. A64-row accepted
 anchor remained unchanged through later mapping/reopen/resume.11 foreground
 resume observations and both targeted repair receipts are retained.
-Real release/status/progress/record/media handlers returned saved data; an
 invalid cursor was rejected. Ordinary stored playback bytes are original
 RIFF/WAVE; there was no synthesis.

The final native test passed under Go1.26.5 race instrumentation. The eight
positive/negative I35 reconciliation methods and complete selected working-tree
DAG also passed. The committed-clean receipt passed8/8 at47d171d. Root failures and
intermediate observations remain in ignored evidence instead of being relabelled.

Source-quality readback independently observes73 native interval extents outside
the supplied WAVE duration; all73 explicitly retain unverified alignment and
unknown processing rate.20,068 binary64 endpoint representations are separately
identified. The actual HKK mismatch is returned by the production record handler
with its original1.201375s label and actual44,100Hz media clock. None is
relabelled exact alignment or a new16k derivative. The v1 strict bound contract
remains intact and its original source_contract_test.go is byte-identical.

## Acceptance and retained data

The complete selected I35 DAG passed8/8 with --require-clean at
`47d171d5aa0845dbf2fbb1fb96848f92541f8c3e`. Pinned OpenSpec1.13.1 strict
validation, graph/discovery, affected Go1.26.5 race/pure/native cases, relevant
vet and catalogue/GAPS preservation passed. Unaffected earlier full-source
imports and model observations were reused within their original scope.

The disposable PostgreSQL and private MinIO containers are stopped with the
complete imported data retained for reuse. Their private runtime state is in
ignored data/iteration-35-official-l2-20261027/retention.json. No live user-stack
data was populated or restarted. Acceptance bookkeeping follows the accepted
code commit; no implementation/test/data inputs change during that bookkeeping.
