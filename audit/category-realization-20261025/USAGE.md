# Running the finite category validation

Run commands from the Tangerine checkout. The service and selected local model
must already exist. These commands never install a model, activate a provider,
create an account or allow billed use. The listening action requires the existing
explicitly verified unbilled Gemini project; default provider settings are read,
never changed. Its current free allocation can return unavailable or quota errors.

1. `python3 -B audit/category-realization-20261025/run.py prepare-candidate`
   copies the selected speech source into a private candidate directory. The
   ordinary running server, user exercises and Settings stay untouched.
2. `python3 -B audit/category-realization-20261025/run.py render`
   materializes concrete textual contrasts and the26 committed acoustic plans through existing native speech owners. `retain_acoustic.py` optionally reuses historic native WAVs/receipts when those local files exist; it is not needed for fresh regeneration. `prepare_remaining.py` renders the short controlled acoustic contrasts and measurements, and `prepare_interaction.py` creates the explicit cutoff/handoff scene. Symbolic captions are not
   spoken as if they were the target event.
3. `python3 -B audit/category-realization-20261025/run.py listen --variant gemini31 --judge-model gemini-3.1-flash-lite --continue-503`
   explicitly selects the existing free project's named development model. Each
   finite case is dispatched at most once. `--continue-503` means try the other
   cases after a service-unavailable response; it does not retry that failed case.
   Quota and other failures stop the action with their complete native evidence.
   This is a development variant, not an application provider fallback.
4. `python3 -B audit/category-realization-20261025/run.py report --variant gemini31`
   reads saved evidence and writes the complete matrix. It makes no inference.
   `readmit --variant gemini31` applies a repaired native output decoder to the
   original retained response, making zero new calls and preserving old failures.
5. `python3 -B audit/category-realization-20261025/export_lab.py` copies and reads
   back the actual selected evidence in the existing local Lab. It makes no calls
   to a model. The native and Lab record retain all failed attempts and original
   responses, not only favorable judgments.

Use `--categories` with comma-separated exact IDs for an affected subset. A changed
fixture population uses a separate `--output` experiment directory. The directory
freezes its fixture population once; later reads trust it. A changed judge/prompt
uses a separately named `--variant`. A prepared/possibly initiated operation with
no response is an interrupted observation, not an invitation to redispatch on a
read. Inspect its capture or explicitly start a separate experiment.

`reconcile --variant gemini31` recomputes a changed comparison from retained native output and actual measurements without redispatch. The original comparisons remain preserved.

The native cases in `tests/test_category_validation.py` cover the comparison
mechanism on constructed independent judgments for every original category.
`tests/test_category_evidence.py` reads actual WAVs and actual provider replies.
Neither test source turns a model opinion into empirical accuracy or unselected
voice/provider qualification. `COVERAGE.md` and `COVERAGE.json` show the current
finite results, including unavailable/unconfirmed categories.
