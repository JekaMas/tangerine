"""Freeze authored category references, not model-generated expected answers."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent


def build():
    refs = json.loads((ROOT / "specification/v2/domain/linguistic-contrast-set.v1.json").read_text())["examples"]
    controllers = {r["taxonomy_id"]: r for r in json.loads((ROOT / "specification/v2/domain/acoustic-production.v1.json").read_text())["rows"]}
    # The old symbolic references explicitly were not recordings. These two
    # concrete utterances preserve their obligations without speaking a caption.
    spoken = {
        "fluency.self_repair": ("Go left. Sorry, I mean go right.", "Go left, no right, or left, I don't know."),
        "pragmatics_register.speech_act": ("I'm sorry I broke your phone.", "Congratulations on your broken phone."),
    }
    rows = []
    for ref in refs:
        category = ref["taxonomy_id"]
        mode = controllers[category]["controller"]
        control = ref["surface_status"] == "acceptable"
        clean, changed = spoken.get(category, (ref["canonical"], ref["surface"]))
        family = category.split(".")[0].replace("_", " ")
        question = ("Does the heard utterance contain an actual " + family +
                    " defect in the stated context? Identify the heard words or acoustic cues, "
                    "and retain permitted variants.")
        acoustic = mode not in ("surface_text", "control_variant") or category == "acceptable_variant.pronunciation_variant"
        if acoustic:
            question = ("Does the actual sound fail the explicit target in the public context? "
                        "Describe what you hear; do not infer pronunciation from spelling.")
        rows.append({
            "taxonomy_id": category, "control": control,
            "context": ref["contrast_context"], "clean_text": clean, "mutated_text": changed,
            "control_context": ref["correct_control"]["context"],
            "control_text": ref["correct_control"]["text"],
            "question": question, "control_question": question,
            "correction": clean, "controller": mode,
            "render_kind": "acoustic" if acoustic else "interaction" if category == "discourse.turn_taking" else "text",
            "requires_physical": mode in ("pitch_duration", "vowel_duration", "vot_edit", "pause_insert"),
            "origin": "constructed_author_reference_not_corpus_or_perceptual_gold",
        })
        if category == "fluency.disfluency_density":
            rows[-1].update(context="This explicit speaking exercise permits at most two filler events per 100 spoken words. No general clinical or English norm is implied.",
                clean_text="Please bring the parcel to the front desk and tell the receptionist that I will collect it tomorrow morning.",
                mutated_text="Um, please, um, bring, um, the parcel, um, to the, um, front desk, um, and tell, um, the receptionist, um, I will collect it tomorrow.",
                control_text="Please bring the parcel to the front desk. I will collect it tomorrow.",
                control_context="This explicit speaking exercise permits at most two filler events per 100 spoken words.",
                question="Does the actual heard speech exceed the explicit ceiling of two filler events per 100 spoken words? Count audible filler events rather than treating ordinary hesitation as a universal defect.",
                control_question="Does the actual heard speech exceed the explicit ceiling of two filler events per 100 spoken words?")
    target = HERE / "FIXTURES.json"
    target.write_text(json.dumps({"version": 1, "fixtures": rows}, indent=2, ensure_ascii=False) + "\n")
    tests = ROOT / "tests/test_category_validation.py"
    raw = tests.read_text()
    start = raw.index("class CategoryComparisons(unittest.TestCase):")
    end = raw.index("\n\ndef category_case", start)
    methods = ["class CategoryComparisons(unittest.TestCase):"]
    for row in rows:
        for kind in ("complete_positive", "false_metadata_negative", "missing_audio_negative", "uncertain_negative"):
            name = "test_" + row["taxonomy_id"].replace(".", "_") + "_" + kind
            methods += ["    def " + name + "(self):",
                        "        category_case(next(r for r in FIXTURES if r['taxonomy_id'] == " + repr(row["taxonomy_id"]) + "), " + repr(kind) + ")(self)", ""]
    raw = raw[:start] + "\n".join(methods).rstrip() + raw[end:]
    loop_start = raw.find("\nfor fixture in FIXTURES:")
    if loop_start >= 0:
        loop_end = raw.index("\n\nclass CategoryValidation", loop_start)
        raw = raw[:loop_start] + raw[loop_end:]
    tests.write_text(raw)
    print(json.dumps({"categories": len(rows), "controls": sum(r["control"] for r in rows)}))


if __name__ == "__main__":
    build()
