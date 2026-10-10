"""Source-policy document checks only; no acquisition, import or model execution."""
import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent
checks = []


def pair(name, value, predicate, change):
    assert predicate(value), name
    checks.append({"id": name + ".positive", "status": "pass"})
    bad = copy.deepcopy(value)
    change(bad)
    assert not predicate(bad), name + " counterexample"
    checks.append({"id": name + ".negative", "status": "pass"})


reply = json.loads((AUDIT / "owner-reply.json").read_text())
pair("download_denied", reply,
     lambda x: x["sound_video_download"] == "denied_by_owner" and not x["new_media_download_attempts_allowed"],
     lambda x: x.update(new_media_download_attempts_allowed=True))
pair("commercial_and_purpose_scoped_ai_denial", reply,
     lambda x: x["commercial_material_development"] == x["ai_transfer_for_commercial_material_development"] == "denied_by_owner",
     lambda x: x.update(ai_transfer_for_commercial_material_development="permitted"))
pair("no_noncommercial_grant_or_blanket_ai_ban", reply,
     lambda x: x["noncommercial_ai_transfer"] == x["noncommercial_app_reuse"] == "not_granted_by_this_reply" and not x["blanket_all_ai_transfer_prohibition_claimed"],
     lambda x: x.update(noncommercial_ai_transfer="permitted"))
pair("receipts_retained_and_independent_generation", reply,
     lambda x: x["prior_text_survey_rating_acquisition_receipts_preserved"] and not x["independently_generated_exercises_require_icnale"],
     lambda x: x.update(independently_generated_exercises_require_icnale=True))
pair("no_fabricated_mailbox_verification_or_outreach", reply,
     lambda x: "not independently verified" in x["received_via"] and not x["external_reply_sent"],
     lambda x: x.update(external_reply_sent=True))
research = json.loads((ROOT / "specification/v2/domain/source-research.v1.json").read_text())
pair("active_source_policy", research["icnale_owner_reply"],
     lambda x: x["current_tangerine_source_exercise_and_llm_use"] == "disabled_pending_applicable_permission" and (ROOT / "specification/v2" / x["active_policy"]).is_file(),
     lambda x: x.update(current_tangerine_source_exercise_and_llm_use="enabled"))
fixtures = json.loads((ROOT / "specification/v2/domain/verification-fixtures.v1.json").read_text())
graph = json.loads((ROOT / "openspec/changes/implement-teacher-error-trainer/verification.json").read_text())
for polarity in ("positive", "negative"):
    fixture = next(x for x in fixtures["fixtures"] if x["id"] == "set2-COR-01.P1-" + polarity)
    binding = next(x for x in fixtures["case_bindings"] if x["case_id"] == "COR-01.P1.SET2." + polarity.upper())
    pair("literal_dag_packet_" + polarity, binding,
         lambda x: x["input"] == fixture[polarity]["input"] and x["expected"] == fixture[polarity]["expected"] and x["observation_state"] == "not_run" and any(c["id"] == x["case_id"] and c["state"] == "blocked" for c in graph["cases"]),
         lambda x: x.update(observation_state="passed"))
result = {"passed": len(checks), "failed": 0, "checks": checks,
          "proof_boundary": "Static recorded-policy and literal planned-DAG checks with constructed metadata counterexamples; no runtime enforcement, acquisition, inference or mailbox verification."}
(AUDIT / "validation-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({"passed": len(checks), "failed": 0, "scope": "static source policy"}))
