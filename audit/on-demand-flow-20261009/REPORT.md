# On-demand exercise generation clarification

Date:2026-10-09. Baseline:503723e. Actual user requirement: LLM generates text from each user request, LLM generates mutations, audio follows, listener responds, and LLM checks against the original text/mutations with findings/misses/comments/scoring. No exercise corpus needs pregeneration. Scope remains specification-only.

The main flow already allowed first use without an empirical corpus or benchmark. One wording ambiguity permitted a local recipe operator to supply mutations. The updated contract makes both content phases LLM-owned: local code validates/materializes/replays the returned edits and calculates exact scores; it does not replace inference with a recipe bank or prebuilt exercise. Matching original/surface text is already present in evaluation-key.utterances and reaches mapping/feedback; the revised flow/prompt makes that use explicit without adding a DTO or model stage.

No startup corpus, seed library or all-category batch is created. Completed user-requested exercises remain stored for replay; matching checkpoint resume remains available. Optional corpus imports, empirical reports and explicitly selected full benchmark retain their original scope and are not normal-use requirements. The122categories/recipes,42formulas and11full-source identities/scopes are byte-preserved, as are original provider profiles. No application service, launcher or credential changed.

FLOW-02 and FLOW-05 are clarified. DEMAND-01 adds two literal scenarios/four positive-negative plans: empty-bank phase dispatch with no recipe fallback on failure; original/surface/mutations/answer matching with found/missed feedback and independently stated TP=1,FN=1,FP=0,precision=1,recall=1/2,F1=2/3. Optional explanation omission has no penalty. Wrong-version comparison preserves the saved answer/key.

39affected static checks, strict OpenSpec and property-graph/discovery validation passed. Current graph:397requirements,412properties,1,648case edges. New four plans remain blocked/not_run; no model, audio, runtime dispatch, corpus creation or Lab observation occurred. All prior case states/receipts are preserved. Changed prompt texts/hashes, generation semantics and finite fixture identities invalidate their corresponding previous static proof scope; unchanged behavior/corpus checks are not rerun. The stable active version vector is reconciled separately.

No further product decision is needed for this clarification. The unrelated audit/spec-fullness-20261008/GAPS.md edit is preserved and excluded from the commit.
