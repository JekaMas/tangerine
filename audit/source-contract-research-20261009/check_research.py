"""Static document/metadata audit; never an application or corpus-ingest test."""
from pathlib import Path
import copy
import csv
import sys
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
META = ROOT / "specification/v2/domain/source-research.v1.json"
data = json.loads(META.read_text())
checks = []
selected = set(sys.argv[1:])


def pair(name, oracle, mutation):
    if selected and name not in selected:
        return
    assert oracle(data), name + ": supported metadata failed"
    changed = copy.deepcopy(data)
    mutation(changed)
    assert not oracle(changed), name + ": contradictory metadata accepted"
    checks.extend([
        {"id": name + ".positive", "status": "pass", "scope": "static_research_metadata"},
        {"id": name + ".negative", "status": "pass", "scope": "constructed_metadata_mutation_rejected"},
    ])


pair("apache_choice", lambda d: d["software_license"]["spdx"] == "Apache-2.0"
     and d["software_license"]["status"] == "resolved_by_actual_user",
     lambda d: d["software_license"].update(spdx="MIT"))
if not selected:
    license_hash = hashlib.sha256((ROOT / "LICENSE").read_bytes()).hexdigest()
    assert license_hash == "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30"
    checks.append({"id": "official_license_bytes", "status": "pass", "sha256": license_hash})

ids = ["TET-GOLD-1", "SPEECHOCEAN762", "L2-ARCTIC", "WILOCNESS-2.1", "FCE-2.1",
       "EFCAMDAT-R2", "EFCAMDAT-SHATZ2020", "EFCAMDAT-OKSUZ2025",
       "DOUBAO-STUDY-RECORDS", "MOODRICK-DATA", "NIR-DATA"]
pair("full_source_identity", lambda d: d["source_ids_preserved"] == ids,
     lambda d: d["source_ids_preserved"].remove("EFCAMDAT-SHATZ2020"))
if not selected:
    registry = (ROOT / "specification/v2/domain/corpus-sources.v1.yaml").read_text()
    assert re.findall(r"^  - id: (.+)$", registry, re.M) == ids
    assert registry.count("acquired: false") == 11
    assert registry.count("actual_manifest_id: null") == 11
    checks.append({"id": "actual_registry_not_acquired", "status": "pass", "sources": 11})

def shatz(d):
    s = d["efcamdat"]["shatz_expected_samples"]
    return s == {"main_prompts": 406062, "alternate_prompts": 317220, "total": 723282}

pair("both_shatz_samples", shatz,
     lambda d: d["efcamdat"]["shatz_expected_samples"].update(alternate_prompts=0))
pair("source_prompt_missingness",
     lambda d: not d["efcamdat"]["shatz_second_sample_actual_prompt_known"],
     lambda d: d["efcamdat"].update(shatz_second_sample_actual_prompt_known=True))
pair("source_correction_missingness",
     lambda d: not d["efcamdat"]["shatz_source_correction_layer_promised"],
     lambda d: d["efcamdat"].update(shatz_source_correction_layer_promised=True))

upstream = []
for name in ["osf-data.json", "osf-analysis.json"]:
    page = json.loads((AUDIT / name).read_text())
    assert page["links"]["next"] is None
    upstream.extend(page["data"])
expected = {x["id"]: (x["attributes"]["name"], x["attributes"]["size"],
                       x["attributes"]["extra"]["hashes"]["sha256"]) for x in upstream}

def osf(d):
    files = d["efcamdat"]["osf_metadata_members"]
    return len(files) == 4 and {
        x["id"]: (x["name"], x["size"], x["upstream_sha256"]) for x in files
    } == expected and all(not x["record_bytes_acquired"] and x["local_data_sha256"] is None for x in files)

pair("upstream_metadata_is_not_local_acquisition", osf,
     lambda d: d["efcamdat"]["osf_metadata_members"][0].update(
         record_bytes_acquired=True,
         local_data_sha256=d["efcamdat"]["osf_metadata_members"][0]["upstream_sha256"]))
pair("analysis_companion_is_not_full_derivative",
     lambda d: not d["efcamdat"]["osf_analysis_pair_substitutes_full_cambridge_derivative"],
     lambda d: d["efcamdat"].update(osf_analysis_pair_substitutes_full_cambridge_derivative=True))

confirmed = ["writingID", "learnerID", "level", "unit", "nationality", "topic",
             "word_count", "Noof_obl_context", "SOC_scores"]
pair("code_fields_vs_complete_native_header",
     lambda d: d["efcamdat"]["osf_code_confirmed_input_names"] == confirmed
     and d["efcamdat"]["csv_headers_fully_inspected"]
     and not d["efcamdat"]["csv_record_rows_inspected"],
     lambda d: d["efcamdat"].update(csv_record_rows_inspected=True))

header_receipts = json.loads((AUDIT / "header-research.json").read_text())
header_expected = {x["member"]: next(csv.reader([x["header"].strip()])) for x in header_receipts}
assert all(x["status"] == 206 and x["newline_complete"] for x in header_receipts)
pair("exact_csv_native_headers",
     lambda d: d["efcamdat"]["csv_native_headers"] == header_expected
     and [len(d["efcamdat"]["csv_native_headers"][n]) for n in
          ["ef2_def_analyse.csv", "ef2_indef_analyse.csv"]] == [19, 20],
     lambda d: d["efcamdat"]["csv_native_headers"]["ef2_indef_analyse.csv"].remove("Phonological_variant_errors"))

pair("cefr_source_discrepancy",
     lambda d: d["efcamdat"]["cefr_code_paper_discrepancy"]["paper_bands"]
     == {"A1": [1, 3], "A2": [4, 6], "B1": [7, 9], "B2": [10, 12]},
     lambda d: d["efcamdat"]["cefr_code_paper_discrepancy"]["paper_bands"].update(A1=[1, 4]))

def doubao(d):
    s = d["doubao"]
    return (s["video_expected"] == 560 and s["video_collected"] == 548
            and s["video_collected"] == s["video_valid"] + s["video_invalid"]
            and s["video_missing"] == s["video_expected"] - s["video_collected"]
            and s["journal_missing"] == s["journal_expected"] - s["journal_collected_valid"]
            and s["journal_collected_valid"] == 550)

pair("study_count_units", doubao,
     lambda d: d["doubao"].update(video_collected=545))
pair("study_design_not_invented",
     lambda d: d["doubao"]["cohorts_documented"] == 1
     and not d["doubao"]["control_pre_post_followup_datasets_documented"]
     and not d["doubao"]["exact_instrument_wording_and_score_scale_available"],
     lambda d: d["doubao"].update(control_pre_post_followup_datasets_documented=True))
pair("paper_is_not_participant_release",
     lambda d: not d["doubao"]["participant_release_verified"]
     and not d["doubao"]["aggregate_data_are_participant_records"],
     lambda d: d["doubao"].update(aggregate_data_are_participant_records=True))
pair("separate_vendor_contracts",
     lambda d: set(d["vendors"]) == {"MOODRICK-DATA", "NIR-DATA"}
     and not any(x["private_export_or_api_contract_obtained"] for x in d["vendors"].values()),
     lambda d: d["vendors"].pop("NIR-DATA"))
pair("personal_portability_not_bulk_api",
     lambda d: not d["vendors"]["NIR-DATA"]["bulk_export_rights_or_api_implied"]
     and d["vendors"]["NIR-DATA"]["different_nira_asset_api_excluded"],
     lambda d: d["vendors"]["NIR-DATA"].update(bulk_export_rights_or_api_implied=True))

if not selected or "llm_only_scoring_contradiction_repaired" in selected:
    scoring = (ROOT / "specification/v2/docs/scoring-v1.md").read_text()
    assert "require case-specific approval" not in scoring
    assert "The LLM cannot add that alternative" not in scoring
    assert "The LLM accepts a valid novel alternative" in scoring
    assert "A changed weight requires explicit approval" not in scoring
    assert "new saved policy version" in scoring
    checks.append({"id": "llm_only_scoring_contradiction_repaired", "status": "pass"})

if not selected:
    plan = json.loads((ROOT / "openspec/changes/implement-teacher-error-trainer/verification.json").read_text())
    reconciliation = json.loads((AUDIT / "graph-reconciliation.json").read_text())
    for p in reconciliation["affected_property_ids"]:
        edges = [c for c in plan["cases"] if c["property_id"] == p]
        assert {c["polarity"] for c in edges} == {"positive", "negative"}
        assert all(c["state"] == "blocked" for c in edges)
    checks.append({"id": "every_changed_property_has_planned_positive_negative_edges",
                   "status": "pass", "properties": len(reconciliation["affected_property_ids"]),
                   "application_tests_executed": False})

prior = None
retained = []
if selected:
    prior = json.loads((AUDIT / "research-validation.json").read_text())
    retained = [x for x in prior["checks"] if x["id"].rsplit(".", 1)[0] not in selected]
    checks = retained + checks
result = {"scope": "Static source/license document and metadata consistency only",
          "constructed_mutations_are_not_source_records": True,
          "checks": checks, "pass": len(checks), "fail": 0,
          "application_ingestion_provider_benchmark_claims": False,
          "affected_rechecks": sorted(selected),
          "retained_valid_original_checks": len(retained)}
(AUDIT / "research-validation.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"pass": len(checks), "fail": 0, "scope": result["scope"]}))
