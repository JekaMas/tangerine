"""Append only CV properties and exact executable cases to the existing DAG."""
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CHANGE = ROOT / "openspec/changes/implement-teacher-error-trainer"
sys.path.insert(0, str(ROOT / ".agents/workflow/scripts"))
from requirement_tests import parse_delta_specs


def main():
    graph = json.loads((CHANGE / "verification.json").read_text())
    discovery = json.loads((CHANGE / "discovery.json").read_text())
    specs = parse_delta_specs(CHANGE)
    for kind in ("requirements", "properties", "cases"):
        graph[kind] = [r for r in graph[kind] if not r["id"].startswith("CV-")]
    graph["commands"] = [r for r in graph["commands"] if not r["id"].startswith("category-realization-")]
    property_ids, test_ids, added = [], [], []
    dependencies = ["services/speech/category_validation.py", "services/speech/diagnostic_models.py",
                    "services/speech/diagnostic_runtime.py", "specification/v2/prompts/audio-category-probe-v1.txt",
                    "audit/category-realization-20261025/FIXTURES.json"]
    statements = {
        "01": "Enumerate every leaf with separate implementation and explicit-binding audio coverage; missing audio remains not_run.",
        "02": "Project actual neutral numbered clips and public questions without the withheld roles/key/expected answers.",
        "03": "Require the intended contrast and correct controls; retain missing, conflicting, false-positive and unrealized outcomes.",
        "04": "Persist one explicit observation and read it without inference or repeated stored-byte checking.",
        "05": "Keep numeric acoustic confirmation uncertain until an actual physical observation accompanies the auditory result.",
        "06": "Retain actual finite speech/auditory outputs, failures, model bindings and proof limits rather than equating fixtures with heard audio.",
    }
    owners = {"01": "coverage", "02": "blind_input", "03": "compare_probe", "04": "saved_observation", "05": "compare_probe", "06": "coverage"}
    for number, statement in statements.items():
        rid = "CV-" + number
        spec = next(v for v in specs.values() if v["title"].startswith(rid + " "))
        graph["requirements"].append(dict(id=rid, capability=spec["capability"], title=spec["title"], fingerprint=spec["fingerprint"]))
        pid = rid + ".P1"; property_ids.append(pid)
        graph["properties"].append(dict(id=pid, requirement_id=rid, statement="The application SHALL " + statement,
                                       scenarios=spec["scenarios"], owner="services/speech/category_validation.py::" + owners[number],
                                       oracle="Literal withheld authored expectations, actual wire/WAV readback and explicit model-evidence limits.", source_globs=dependencies))

    def add(number, module, cls, method, polarity, setup, mocked=False):
        rid = "CV-" + number; spec = next(v for v in specs.values() if v["title"].startswith(rid + " "))
        source = "tests/" + module + ".py"
        tid = "unittest::" + module + "." + cls + "." + method
        test_ids.append(tid)
        substitution = dict(classification="NO_TEST_DOUBLE", proof_claims=[setup],
                            forbidden_claims=["Universal perceptual accuracy", "All voices/providers qualified", "Constructed judgments are actual audio inference"])
        if mocked:
            substitution = dict(classification="EXTERNAL_BOUNDARY", owner_replaced="Auditory provider transport/model call only",
                                allowed_proof="Real native request construction/projection/dispatch with literal returned wire fixtures",
                                forbidden_claims=["Actual hosted accuracy or entitlement", "Actual local auditory inference"])
        case_dependencies = dependencies + [source]
        if number in ("04", "06"):
            case_dependencies += ["audit/category-realization-20261025/run.py"]
        if number == "06":
            case_dependencies += ["audit/category-realization-20261025/generate_acoustic.py", "audit/category-realization-20261025/RENDER-PLANS.json"]
        if number == "06":
            case_dependencies += ["audit/category-realization-20261025/retain_acoustic.py", "audit/category-realization-20261025/prepare_remaining.py", "audit/category-realization-20261025/prepare_interaction.py"]
        row = dict(id=rid + ".P1." + method, property_id=rid + ".P1", polarity=polarity,
                   scenario=spec["scenarios"][0], scenario_fingerprint=spec["scenario_fingerprints"][spec["scenarios"][0]],
                   setup=setup, observable=setup, red_expectation="The named independently expected result is absent or incorrect.",
                   green_expectation=setup, test_id=tid, command_id="category-realization-evidence" if module.endswith("evidence") else "category-realization-native",
                   state="implemented", source_path=source, source_sha256=hashlib.sha256((ROOT / source).read_bytes()).hexdigest(),
                   invalidation_dependencies=case_dependencies, substitution=substitution)
        graph["cases"].append(row); added.append(row)

    mapping = {
        "01": ["inventory_positive", "unselected_binding_negative"],
        "02": ["blind_projection_positive", "private_claims_cannot_change_input_negative", "order_is_explicit_positive", "native_auditory_clip_labels_positive", "ordinary_diagnostic_unchanged_positive", "gemini_wire_blind_positive", "native_blind_dispatch_positive"],
        "03": ["conflicting_findings_negative", "unheard_mutation_negative", "missing_requested_finding_negative", "actual_clips_wrapper_positive", "wrong_clips_wrapper_negative"],
        "04": ["persist_once_positive", "missing_is_not_cached_pass_negative", "saved_request_is_not_overwritten_positive", "interrupted_request_not_redispatched_negative", "alternate_report_keeps_default_evidence_negative"],
        "05": ["physical_observation_positive", "intention_is_not_measurement_negative", "status_without_measurement_negative", "measured_change_with_deaf_judge_negative"],
    }
    for number, methods in mapping.items():
        for method in methods:
            add(number, "test_category_validation", "CategoryValidation", "test_" + method,
                "negative" if method.endswith("negative") else "positive",
                "Execute the literal independent assertions in tests/test_category_validation.py::test_" + method,
                method in ("gemini_wire_blind_positive", "native_blind_dispatch_positive"))
    add("06", "test_category_validation", "CategoryValidation", "test_missing_acoustic_plan_negative", "negative", "An unknown plan returns no recording and makes no native/model dispatch.")
    fixtures = json.loads((HERE / "FIXTURES.json").read_text())["fixtures"]
    for fixture in fixtures:
        for kind in ("complete_positive", "false_metadata_negative", "missing_audio_negative", "uncertain_negative"):
            method = "test_" + fixture["taxonomy_id"].replace(".", "_") + "_" + kind
            add("03", "test_category_validation", "CategoryComparisons", method,
                "positive" if kind.endswith("positive") else "negative",
                "Category=" + fixture["taxonomy_id"] + "; exact four-role authored comparison: " + kind + ". Constructed judgments test native logic, not actual hearing.")
    for name in ("real_recordings_positive", "blind_actual_observation_positive", "actual_unrealized_contrast_negative", "actual_provider_failure_negative", "fresh_acoustic_regeneration_positive", "fresh_acoustic_cache_negative"):
        add("06", "test_category_evidence", "CategoryEvidence", "test_" + name,
            "negative" if name.endswith("negative") else "positive",
            "Read retained actual local/free recordings or actual failed/accepted observations with independently specified outcomes: " + name + "; zero new inference.")
    for kind, file in (("native", "test_category_validation.py"), ("evidence", "test_category_evidence.py")):
        graph["commands"].append(dict(id="category-realization-" + kind, runner="python-unittest",
                                     argv=["python3", "-B", "-m", "unittest", "discover", "-s", "tests", "-p", file, "-v"], cwd=".", env={}, timeout_seconds=120, authority="local"))
    discovery["scope"]["property_ids"] = [v for v in discovery["scope"]["property_ids"] if not v.startswith("CV-")] + property_ids
    discovery["scope"]["test_ids"] = [v for v in discovery["scope"]["test_ids"] if "::test_category_" not in v] + test_ids
    discovery["reviews"] = [v for v in discovery["reviews"] if v["id"] != "category-realization-20261025"]
    discovery["reviews"].append(dict(id="category-realization-20261025", question="Verify every category's implementation versus actual audio with blind correct/false-metadata controls.",
        property_ids=property_ids, test_ids=test_ids, searches=[
            dict(kind="exact", status="completed", query="Known linguistic category fixtures, acoustic controllers, diagnostic projection/transport and retained receipts",
                 outcome="Add neutral probe and per-category evidence joining; actual outage and model/renderer uncertainty stay visible.",
                 results=[dict(path=p, classification="change_candidate", reason="Actual owned dependency of this scoped validation.") for p in dependencies]),
            dict(kind="semantic", status="not_applicable", query="Known owners from the preceding category/audio inspection", reason="Exact identified files answer this implementation scope.", outcome="No semantic-index claim.", results=[]),
            dict(kind="jetbrains-index", status="not_applicable", query="Native Python owners and retained audio observations", reason="No symbol refactor or index setup is needed.", outcome="No IDE-index claim.", results=[])],
        disposition="current_change", rationale="Explicit user authorization; no human review, new service, paid fallback, repeated stored-value checks or universal auditory claim."))
    for path, obj in ((CHANGE / "verification.json", graph), (CHANGE / "discovery.json", discovery),
                      (HERE / "CASES.json", dict(properties=property_ids, canonical_details="../../openspec/changes/implement-teacher-error-trainer/verification.json", cases=[{k: row[k] for k in ("id", "property_id", "polarity", "test_id", "source_path")} for row in added]))):
        path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(dict(properties=len(property_ids), cases=len(added))))


if __name__ == "__main__": main()
