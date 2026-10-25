"""Reuse actual accepted native recordings; clip derivatives make zero inference.

Decoder scopes locate a listening window. They are never relabelled as an
independent phonetic observation. Original source/transform receipts stay intact.
"""
import io
import json
from pathlib import Path
import wave
from run import ROOT, HERE, OUT, save

ALL = ROOT / "data/pronunciation-all-20261023/output"
CONNECTED = ROOT / "data/connected-speech-20261023/output"


def clip(source, scope, destination):
    with wave.open(str(source)) as w:
        count = w.getnframes()
        a, b = max(0, scope["start"] - 24000), min(count, scope["end"] + 24000)
        if b - a > 240000:
            return None
        w.setpos(a); pcm = w.readframes(b - a)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(destination), "wb") as w:
        w.setparams((1, 2, 24000, 0, "NONE", "not compressed")); w.writeframes(pcm)
    return dict(source_path=str(source.relative_to(ROOT)), source_start=a, source_end=b,
                sample_rate_hz=24000, target_scope_basis="retained_decoder_proposal_not_independent_hearing")


def main():
    material = json.loads((ALL / "shared-material.json").read_text())
    fixtures = {r["taxonomy_id"]: r for r in json.loads((HERE / "FIXTURES.json").read_text())["fixtures"]}
    for target in material["targets"]:
        category, unit, turn = target["taxonomy_id"], target["unit_id"], target["turn_id"]
        directory = OUT / "recordings" / category
        if (directory / "index.json").exists(): continue
        original, source, initial = None, None, None
        for path in sorted(ALL.glob("kokoro-" + turn + "-*-response.json")):
            value = json.loads(path.read_text())
            if "receipt" not in value: continue
            scope = next((s for s in value["receipt"].get("native", {}).get("acoustic_scopes", []) if s["unit_id"] == unit), None)
            if scope: original, source, initial = path, value, scope; break
        if original is None: continue
        prefix = original.name.removesuffix("-response.json")
        final = None
        for candidate in sorted(ALL.glob(prefix + "-transform-*-response.json")):
            value = json.loads(candidate.read_text())
            selected = next((s for s in value.get("native", {}).get("acoustic_scopes", []) if s["unit_id"] == unit), None)
            if selected: final = (candidate, selected)
        if not initial or not final: continue
        sources = {"clean": (ALL / (prefix + "-clean.wav"), initial),
                   "mutated": (ALL / (prefix + "-mistakes.wav"), final[1])}
        paths, derivatives = {}, {}
        for role, (path, scope) in sources.items():
            if not path.exists(): break
            dest = directory / (role + ".wav")
            derivative = clip(path, scope, dest)
            if derivative is None: break
            paths[role], derivatives[role] = str(dest.relative_to(ROOT)), derivative
        if len(paths) != 2: continue
        paths.update(acceptable=paths["clean"], misleading_metadata=paths["clean"])
        reference = target.get("reference_ipa")
        context = ("Explicit local pronunciation drill at the phrase '" + target["word"] + "'. " +
                   ("The public target pronunciation is /" + reference + "/." if reference else
                    "The public target is neutral clear delivery with normal phrasing and prominence."))
        # This is a correct rendering under a permitted broad context, not a new
        # allophone recording. Specific allophone controls are separately below.
        override = dict(context=context, question="Does the actual sound at the named phrase fail that explicit target? Describe the heard cues.",
                        control_context="Any intelligible ordinary American pronunciation of this phrase is permitted. No narrow drill target.",
                        control_question="Is there an actual pronunciation defect, allowing ordinary accent and delivery variants?")
        save(directory / "index.json", dict(paths=paths, derivatives=derivatives,
             binding=dict(backend="local_kokoro_controlled", model="Kokoro-82M", voice=source["receipt"]["voice_id"], locale=source["receipt"]["locale"]),
             retained_native=[str(original.relative_to(ROOT)), str(final[0].relative_to(ROOT))], fixture_override=override,
             limitation="Correct broad-context control reuses actual clean sound; not a newly qualified alternate allophone."))

    # These earlier short contrasts have particularly useful actually rendered
    # careful/connected variants and concrete task-specific prosody contexts.
    mapping = {"assimilation": "blend_dj", "linking_resyllabification": "linking", "weak_form": "weak_form",
               "elision_reduction": "elision", "rhythm": "rhythm", "intonation_contour": "statement",
               "intonation_function": "statement", "thought_group_chunking": "chunking"}
    rows = {r["id"]: r for r in json.loads((CONNECTED / "recordings.json").read_text())}
    for leaf, case in mapping.items():
        category = "pronunciation.suprasegmental." + leaf
        directory = OUT / "recordings" / category
        row = rows[case]
        paths = {"clean": str((CONNECTED / row["reference_file"]).relative_to(ROOT)),
                 "mutated": str((CONNECTED / row["candidate_file"]).relative_to(ROOT)),
                 "acceptable": str((CONNECTED / (row.get("allowed_file") or row["reference_file"])).relative_to(ROOT))}
        paths["misleading_metadata"] = paths["clean"]
        context = {
            "assimilation": "This explicit voiced coalescent drill targets would-you with /dʒ/, allowing the careful /d j/ alternative as correct. A voiceless affricate loses that stated contrast.",
            "linking_resyllabification": "An explicit smooth-joining drill for turn it off. Intrusive glottal breaks are outside this narrow exercise; ordinary careful speech is permitted elsewhere.",
            "weak_form": "A narrow neutral weak-form drill explicitly targets /tə/ in to be. Emphatic strong forms are correct when emphasis is intended.",
            "elision_reduction": "Several documents are meant. The audible plural s must remain; optional t elision is permitted.",
            "rhythm": "A matched-pace timing drill: do not prolong the selected weak function-word interval; the adjacent words stay at their original pace.",
            "intonation_contour": "A controlled final falling-contour exercise on You have insurance. A final rise does not meet this explicit target.",
            "intonation_function": "You have insurance is intended as a neutral assertion in this local task. A questioning confirmation reading does not fit that specified function.",
            "thought_group_chunking": "The word policy must remain uninterrupted; phrase-boundary pauses are permitted.",
        }[leaf]
        override = dict(context=context, question="Does the heard phrase fail the explicit public target? Describe the sound rather than the punctuation.",
                        control_context=context, control_question="Does the heard phrase fail the explicit public target? Describe the sound rather than the punctuation.")
        if leaf in ("linking_resyllabification", "weak_form"):
            override["control_context"] = "Ordinary careful or connected English is permitted here; emphasis and clear word boundaries are not themselves errors."
            override["control_question"] = "Does this contain an actual pronunciation error, allowing that stated variety of delivery?"
        source_request = json.loads((CONNECTED / (case + "-source-request.json")).read_text())
        physical_rows = json.loads((CONNECTED / "physical-reconciliation.json").read_text())["checks"]
        actual = [r for r in physical_rows if r["case_id"] == case]
        physical = dict(status="supported" if all(r["passed"] for r in actual) else "uncertain", observations=actual,
                        retained_receipt="data/connected-speech-20261023/output/physical-reconciliation.json") if actual else None
        save(directory / "index.json", dict(paths=paths, binding=dict(backend="local_kokoro_controlled", model="Kokoro-82M",
             voice=source_request["turn"]["voice_id"], locale=source_request["turn"]["locale"]), physical=physical,
             retained_native=["data/connected-speech-20261023/output/recordings.json"], fixture_override=override,
             limitation="Prior synthesis reused without new inference; auditory confirmation is a separate new observation."))
    print(json.dumps(dict(retained_acoustic=len(list((OUT / "recordings").glob("pronunciation.*/index.json"))))))


if __name__ == "__main__": main()
