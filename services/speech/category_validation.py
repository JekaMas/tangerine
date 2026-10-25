"""Finite development probes over saved audio, separate from learner grading.

The withheld bindings are authored test expectations. A successful comparison
is a model observation on that population, never human or empirical gold.
"""
import copy
import json
import random
from pathlib import Path


ROLES = ("clean", "mutated", "acceptable", "misleading_metadata")


def blind_input(request):
    """The only model-visible projection for a blind category probe.

    In particular, filenames, category IDs, clean/mutant roles, intended IPA,
    expected answers and the deliberately false manifest stay outside the call.
    """
    return {
        "task": "blind_category_probe",
        "clips": [
            {key: row[key] for key in ("unit_id", "public_context", "question")}
            for row in request["clips"]
        ],
    }


def make_probe(fixture, recordings, binding, seed):
    """Freeze a randomized finite test and its private correspondence once."""
    roles = list(ROLES)
    random.Random(seed).shuffle(roles)
    clips, withheld = [], []
    for number, role in enumerate(roles):
        control = role == "acceptable"
        unit_id = "clip-" + str(number + 1)
        clips.append({
            "unit_id": unit_id,
            "public_context": fixture["control_context"] if control else fixture["context"],
            "question": fixture["control_question"] if control else fixture["question"],
        })
        withheld.append({
            "unit_id": unit_id,
            "role": role,
            "audio_path": recordings[role],
            "expected": "supported" if role == "mutated" and not fixture["control"] else "contradicted",
            "claimed_mutation": role in ("mutated", "misleading_metadata"),
        })
    return {
        "category_id": fixture["taxonomy_id"],
        "binding": copy.deepcopy(binding),
        "clips": clips,
        "withheld": withheld,
        "requires_physical": fixture.get("requires_physical", False),
        "origin": "constructed_author_reference_not_corpus_or_perceptual_gold",
    }


def compare_probe(probe, observation):
    """Compare a completed observation once; unknown and conflicts stay visible."""
    rows = []
    findings = (observation or {}).get("output", {}).get("findings", [])
    dispatched = bool(observation and (observation.get("receipt", {}).get("inference_calls")
                                      or observation.get("wire", {}).get("http_status") is not None))
    for expected in probe["withheld"]:
        supplied = [f for f in findings if f.get("unit_id") == expected["unit_id"]
                    and f.get("feature") == "category_probe"]
        judgments = {f.get("status") for f in supplied}
        reasons = [f.get("reason") or f.get("description") for f in supplied]
        if not dispatched:
            actual, outcome = None, "not_run"
        elif len(judgments) != 1 or not reasons or not all(isinstance(r, str) and r.strip() for r in reasons):
            actual, outcome = None, "uncertain"
        else:
            actual = next(iter(judgments))
            outcome = ("uncertain" if actual in ("uncertain", "not_applicable")
                       else "passed" if actual == expected["expected"] else "failed")
        rows.append({**expected, "actual": actual, "outcome": outcome,
                     "findings": supplied})
    controls = [r for r in rows if r["role"] != "mutated"]
    false_alarms = sum(r["outcome"] == "failed" and r["actual"] == "supported" for r in controls)
    physical = (observation or {}).get("physical", {})
    physical_ok = not probe["requires_physical"] or (physical.get("status") == "supported" and bool(physical.get("observations")))
    conflict = bool(probe["requires_physical"] and physical_ok and
                    any(r["role"] == "mutated" and r["actual"] == "contradicted" for r in rows))
    statuses = {r["outcome"] for r in rows}
    if "not_run" in statuses:
        confirmation = "not_run"
    elif conflict:
        confirmation = "uncertain"
    elif "failed" in statuses:
        confirmation = "not_realized" if any(r["role"] == "mutated" and r["outcome"] == "failed" for r in rows) else "uncertain"
    elif "uncertain" in statuses or not physical_ok:
        confirmation = "uncertain"
    else:
        confirmation = "confirmed"
    return {
        "category_id": probe["category_id"], "binding": probe["binding"],
        "audio_confirmation": confirmation, "cases": rows,
        "false_alarms": false_alarms, "correct_controls": len(controls),
        "controls_passed": all(r["outcome"] == "passed" for r in controls),
        "dispatch_status": "not_run" if not dispatched else "failed" if (observation or {}).get("error") else "observed",
        "physical": physical or None,
        "physical_auditory_conflict": conflict,
        "physical_evidence_missing": bool(probe["requires_physical"] and not physical_ok),
        "basis": "blind_model_observation_on_authored_cases_not_perceptual_gold",
    }


def saved_observation(path, action=None):
    """One explicit check, then reuse the admitted local record without a call.

    A changed model/voice/fixture uses a different experiment directory. This is
    an operator experiment, not an automatic requalification on database reads.
    """
    path = Path(path)
    if path.exists():
        return json.loads(path.read_text())
    if action is None:
        return None
    result = action()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)
    return result


def coverage(fixtures, observations, implementation):
    """Enumerate every leaf; never turn an unselected binding into a pass."""
    rows = []
    for fixture in fixtures:
        category = fixture["taxonomy_id"]
        rows.append({
            "category_id": category, "control": fixture["control"],
            "implementation": implementation.get(category, {"status": "not_run"}),
            "audio": observations.get(category, {"audio_confirmation": "not_run"}),
        })
    return {"scope": "finite_category_and_explicit_binding_coverage",
            "categories": rows, "category_count": len(rows),
            "confirmed": sum(r["audio"]["audio_confirmation"] == "confirmed" for r in rows),
            "unconfirmed": [r["category_id"] for r in rows if r["audio"]["audio_confirmation"] != "confirmed"]}
