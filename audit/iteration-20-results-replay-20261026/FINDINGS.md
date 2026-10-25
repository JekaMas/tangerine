# Iteration 20 findings and disposition

I20-F1 — superseded playback ownership (P2, repaired). The actual controller used
a shared starting flag and unconditionally cancelled/rethrew an older rejected
play promise. A controlled event sequence proves that an old rejection removes
the newer range, and an old resolution can clear the new range's starting flag.
Cancelled stale rejection can also emit obsolete playback guidance. One current
range object now owns its promise; only that object's rejection affects the UI.
The exact red receipt has four failing cases; all six new owner cases pass.
Existing full-playback/seek/replacement/disposal/media-error siblings remain in
the complete selection, with no new controller or repeated data check.

I20-F2 — minute rollover (P2, repaired). Rounding the seconds remainder separately
produced 0:60.00 and 59:60.00. Round total hundredths first, then divide minutes.
Tests preserve 9.590–14.839 labels and cover both minute/hour boundaries.

I20-F3 — numeric score grouping (P2, repaired). Actual 320 px screenshot split 60.0
and /100 across lines. A numeric-only inline group keeps the value together.
Maximum 100.0/100 fits inside the actual 189 px text area; unavailable words retain
normal wrapping. Source score values, counts and optional explanation policy
remain authoritative. No font shrinkage or hidden detail substitutes for repair.

All findings are within the approved iteration. No product decision, native
storage/API/schema/prompt change, inference, synthesis or release operation is
needed. The retained original FX/core/native evidence is not relabelled as a
new provider or native run. Current UI/media facts and proof limits are in REVIEW.
