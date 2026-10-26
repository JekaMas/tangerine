"""Build a read-only research inventory, never application acceptance.

Reads tracked plans/receipts and writes only this audit directory. It does not
run tests, infer case equivalence, call models, inspect secrets or rehash corpora.
"""
import collections
import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = pathlib.Path(__file__).resolve().parent
CHANGE = ROOT / "openspec/changes/implement-teacher-error-trainer"
BASELINE = "324d8e7d378a21f4fe43d9f25231b62fe70320e3"


def read(path):
    return json.loads((ROOT / path).read_text())


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def link(path, label=None):
    return f"[{label or path}](../../{path})"


# Each row is a reviewed finite historical scope, not a fresh run at BASELINE.
ITERATIONS = [
    (1, "Local foundation", "accepted_scoped", "I1/I2 combined 104/104 clean at c8338f2", "audit/iterations-1-2-repair-20261010/REPORT.md", ["TRACE-01", "VER-03"]),
    (2, "Domain storage/assets", "accepted_scoped", "Same combined 104/104; no new run", "audit/iterations-1-2-repair-20261010/REPORT.md", ["TRACE-01"]),
    (3, "Prompt/context/Lab development tooling", "accepted_scoped", "88/88 I3 plus 32/32 affected foundation; 944e0a3", "audit/iteration-3-verification-20261010/REPORT.md", ["TRACE-01"]),
    (4, "Provider connections/text transport", "native_accepted_later_selected_live_scope", "332 native cases; later own-Pro connection/inference supersedes old hosted blocker; no invented whole-I4 retrospective receipt", "audit/iteration-4-verification-20261010/REPORT.md", ["TRACE-01", "QUAL-06", "SCOPE-01"]),
    (5, "Request expansion/durable preparation", "native_accepted_later_selected_live_scope", "48/48 own and 380 predecessor native observations; later Pro flow; historical whole-I5 receipt remains bounded", "audit/iteration-5-verification-20261010/REPORT.md", ["TRACE-01", "VER-02"]),
    (6, "Clean text/mutations/key", "accepted_scoped", "316 selected native cases and five actual local dispatch/context/Lab observations", "audit/iteration-6-review-20261020/REPORT.md", ["TRACE-01", "QUAL-05"]),
    (7, "Speech/accent generation", "accepted_scoped", "112/112 I7, 588/588 I1–I7 reconciliation at 4e935a8", "audit/iteration-7-verification-20261020/REPORT.md", ["TRACE-01", "QUAL-01", "QUAL-02", "QUAL-07", "SCOPE-01"]),
    (8, "Controlled acoustic mutations", "accepted_scoped", "108/108 I8, 696/696 implemented closure; e5a9c51; selected clock repairs later in I16", "audit/iteration-8-acoustic-20261020/REPORT.md", ["ENG-01", "QUAL-03", "QUAL-04"]),
    (9, "Listening/answer persistence", "accepted_scoped", "52/52 current cases; 3063180", "audit/iteration-9-verification-20261020/REPORT.md", ["TRACE-01"]),
    (10, "LLM answer interpretation", "accepted_scoped", "144/144 current/dependency cases; 59d46f2; finite actual local semantic observations", "audit/iteration-10-verification-20261021/REPORT.md", ["TRACE-01", "EMP-02"]),
    (11, "Scoring/results/recommendations", "accepted_scoped", "322/322 repaired closure; 010a4d5", "audit/iteration-11-verification-20261021/REPORT.md", ["TRACE-01", "EMP-04"]),
    (12, "Optional LLM review/disputes", "accepted_scoped", "Original 139/139 on clean 691714a plus six actual contrasts; I17/I16 reconcile old report mismatch", "audit/iteration-12-review-20261021/REPORT.md", ["TRACE-01"]),
    (13, "All source-import mechanisms", "accepted_scoped", "251 logical cases / 142 physical identities; 7c11447; unavailable originals never certified", "audit/iteration-13-source-imports-20261021/REPORT.md", ["DATA-01", "DATA-02", "DATA-03", "DATA-04", "DATA-05", "DATA-06", "DATA-07", "DATA-08", "SUP-01", "SUP-02", "SUP-03", "SUP-04"]),
    (14, "Empirical reports/quality experiments", "accepted_scoped", "173/173 case edges / 144 physical identities; b905352; populations separate", "audit/iteration-14-empirical-20261021/REPORT.md", ["EMP-01", "EMP-02", "EMP-03", "EMP-04", "DATA-08"]),
    (15, "Recovery/usability", "accepted_scoped", "83/83 edges, 74 physical tests at dd64bca; eight-property expanded scope; no open I15 defect", "audit/iteration-15-recovery-20261021/VERIFY-REPORT.md", ["VER-03"]),
    (16, "Selected release/frontend/media", "accepted_scoped", "373/373 edges / 333 physical tests; 27b10be; physical Windows/x86 not claimed", "audit/iteration-16-verification-20261022/REPORT.md", ["TRACE-01", "QUAL-03", "VER-03", "SCOPE-01"]),
    (17, "Historical reconciliation/recovery review", "accepted_scoped", "Latest 47/47 on clean b048d91 supersedes the quoted six-case initial selection", "audit/iteration-17-verification-20261025/ACCEPTANCE.json", ["TRACE-01"]),
    (18, "Preparation summary/controls/captions", "accepted_scoped", "53/53 clean d15661f", "audit/iteration-18-verification-20261026/ACCEPTANCE.json", []),
    (19, "Saved records/persistent recovery", "accepted_scoped", "55/55 clean 185e25d", "audit/iteration-19-verification-20261026/ACCEPTANCE.json", []),
    (20, "Results-first/finite passage replay", "accepted_scoped", "60/60 clean abfef76", "audit/iteration-20-verification-20261026/ACCEPTANCE.json", []),
    (21, "Guided reports/experiments/cleanup", "accepted_scoped", "32/32 clean fd95394", "audit/iteration-21-guided-tools-20261026/VERIFY-ACCEPTANCE.json", []),
    (22, "Production ElevenLabs dictionaries", "accepted_scoped", "13/13 clean 0ee1f51; actual Free Flash v2 ordinary flow/target/reference", "audit/iteration-22-elevenlabs-20261026/ACCEPTANCE.json", []),
    (23, "Actual Gemini Free text flow", "accepted_scoped", "21/21 clean de1c7b2; actual seven-dispatch complete selected flow retained", "audit/iteration-23-verification-20261026/ACCEPTANCE.json", []),
    (24, "Actual Azure F0 comparison", "incomplete", "28 passed / 2 skipped of 30; 4c28284; actual audio/access missing", "audit/iteration-24-azure-20261026/STATUS.json", ["QUAL-01", "VER-01"]),
    (25, "Complete local Qwen dialogue pair", "incomplete", "37 passed / 2 skipped of 39; c6cad2f; first actual CPU piece timed out", "audit/iteration-25-qwen-20261026/STATUS.json", ["QUAL-02", "VER-01"]),
    (26, "Selected acoustic confirmation/CV reuse", "incomplete", "541 passed / 1 skipped of 542; ec24071; actual interaction missing, mixed acoustic outcomes retained", "audit/iteration-26-acoustic-20261026/STATUS.json", ["VER-01", "ENG-01", "QUAL-03", "QUAL-04"]),
    (27, "Selected complete original sources/provenance", "incomplete", "49 passed / 2 skipped of 51; adcedb5; six owner releases and actual Sources activation missing", "audit/iteration-27-sources-20261026/VERIFY-ACCEPTANCE.json", ["VER-01", "DATA-01", "DATA-02", "DATA-03", "DATA-04", "DATA-05", "DATA-06", "DATA-07", "SUP-01", "SUP-02", "SUP-03", "SUP-04"]),
    (28, "Saved-data empirical reports", "accepted_scoped", "38/38 clean 4bbcd5d; zero new model calls; real populations not invented", "audit/iteration-28-reports-20261026/ACCEPTANCE.json", ["EMP-01", "EMP-02", "EMP-03", "EMP-04", "DATA-08"]),
    (29, "Eleven routes/real full flow/media", "accepted_scoped", "57/57 clean 6fa76e0; Gemini generation/Kokoro/local checking, retained Gemini feedback failure", "audit/iteration-29-full-flow-20261026/VERIFY-STATUS.json", ["QUAL-05"]),
    (30, "Main/public source ZIP/start/restart", "incomplete", "17 individual passes / 18 identities; no full clean gate; main/ZIP/native runtime already observed", "audit/iteration-30-release-20261027/VERIFY-STATUS.json", ["VER-02"]),
]

# These mappings are current closure routing, never semantic proof equivalence.
SOURCE_ITEMS = [f"DATA-{n:02}" for n in range(1, 9)]
SUPPLEMENTS = [f"SUP-{n:02}" for n in range(1, 5)]
HMAP = {
    "H010": ["QUAL-06", "SCOPE-01"],
    "H011": ["ENG-01", "QUAL-03", "QUAL-04", "VER-01"],
    "H014": SOURCE_ITEMS + SUPPLEMENTS,
    "H015": ["QUAL-03", "EMP-01", "DATA-08"],
    "H016": ["EMP-02"], "H020": SOURCE_ITEMS,
    "H021": ["DATA-08", "EMP-02", "QUAL-03"],
    "H032": ["EMP-02"], "H036": ["EMP-03", "EMP-04"],
    "H052": ["ENG-01", "QUAL-03", "QUAL-04"],
    "H058": ["ENG-01", "QUAL-03", "QUAL-04"],
    "H063": ["DATA-01", "DATA-02", "DATA-03"],
    "H064": ["DATA-04"], "H065": ["DATA-05", "DATA-06"],
    "H078": [f"DATA-{n:02}" for n in range(1, 7)],
    "H080": ["EMP-01"],
    "H092": ["ENG-01", "TRACE-01", "VER-02", "VER-03", "QUAL-03"],
    "H093": ["ENG-01", "TRACE-01", "VER-02", "VER-03", "QUAL-03"] + SOURCE_ITEMS,
    "H094": ["TRACE-01", "VER-01", "VER-02", "VER-03"],
    "H096": ["VER-02"], "H098": ["TRACE-01", "VER-02"],
    "H099": [], "H100": ["QUAL-01", "VER-01"], "H101": ["QUAL-02", "VER-01"],
}

FAMILY_CANDIDATES = {
    "AUT": [5, 6, 7, 18, 29], "PUB": [6, 7, 8, 29],
    "COR": [13, 14, 26, 28], "DOM": [2, 10, 11], "AUX": [11, 14],
    "RUN": [1, 2, 15, 16, 30], "PRV": [4, 7, 8, 16, 22, 23],
    "REL": [15, 16, 29, 30], "APR": [12, 17], "DEC": [6, 8, 10, 11, 12, 14, 17],
    "TCH": [9, 10, 11, 12], "CFG": [4, 5, 7], "SYNC": [5, 9, 10, 15],
    "SRC": [13, 27], "COV": [26, 28], "SPEC": list(range(1, 17)),
    "ANS": [10, 11, 12], "CMP": [10, 11, 12], "FLOW": [5, 6, 7, 9, 10, 11, 29],
    "LAB": [3, 14, 21, 28], "DEV": [3, 4, 6, 7, 8, 10, 11, 12, 14, 16, 29],
    "MDC": [6, 8, 13, 14], "DREL": [5, 6, 13, 29], "CLOSE": [6, 9, 10, 11, 12, 15],
    "CAP": [4, 7, 16, 22, 23], "DEMAND": [5, 6, 7, 9, 10, 11, 29],
    "READY": [7, 8, 16], "BUILD": [7, 8, 13, 15, 16, 29], "MET": [11, 14],
    "V6-SES": [9, 10, 11], "V6-GEN": [5, 6, 7, 8], "V6-VER": [12, 14, 26],
    "V6-TAX": [6, 10, 11, 26], "V6-MET": [11, 14, 28], "V6-PROV": [4, 7, 16],
    "V6-TTS": [7, 8, 16, 22], "V6-DATA": [13, 27], "V6-GOLD": [13, 14, 26, 28],
    "V6-LIFE": [5, 9, 12, 15], "V6-LLM": [3, 4, 10, 14], "V6-LOCAL": [1, 15, 16, 30],
    "V6-BP": [5, 6, 7, 18], "V6-PLAT": [15, 16, 30], "V6-APR": [12, 17],
    "VALFULL": [14, 26, 28],
}


def graph_route(prop, category):
    req = prop["requirement_id"]
    family = re.sub(r"-\d+$", "", req)
    candidates = FAMILY_CANDIDATES[family]
    items = ["TRACE-01"]
    disposition = "candidate_successor_scope_requires_exact_literal_join"
    if family == "COV":
        items += ["DATA-08", "QUAL-03", "EMP-01", "EMP-02"]
        disposition = "native_category_cases_available_full_empirical_literal_unproved"
    elif family == "SPEC":
        num = re.search(r"SPEC-(\d+)", req)[1]
        for h in historical:
            if re.search(rf"GAP-0*{int(num)}\b", h["original_text"]):
                items += HMAP.get(h["id"], [])
    elif family in {"VALFULL", "V6-GOLD", "V6-VER", "COR"}:
        items += ["DATA-08", "EMP-01", "EMP-02", "QUAL-03"]
        disposition = "conditional_data_or_native_measurement_scope_no_bulk_campaign"
    elif family in {"PRV", "V6-PROV", "CAP", "V6-TTS", "READY", "BUILD"}:
        items += ["SCOPE-01", "QUAL-01", "QUAL-02", "QUAL-03", "QUAL-06"]
    elif family in {"SRC", "V6-DATA"}:
        items += SOURCE_ITEMS
    elif family in {"REL", "V6-PLAT", "V6-LOCAL"}:
        items += ["VER-02", "VER-03"]
    return {
        "disposition": disposition,
        "closure_item_ids": sorted(set(items)),
        "candidate_iterations": candidates,
        "candidate_evidence": [iteration_by_id[n]["evidence"] for n in candidates],
        "exact_equivalence_established_by_this_audit": False,
        "category_native_case_ids": category.get("implementation", {}).get("case_ids", []),
        "remaining_action": "Compare this original literal fixture and oracle with the actual successor assertion/receipt. Reuse only a full exact match; preserve unmet data/observations and materialize only uncovered behavior. This routing is not a pass.",
    }


historical = read("audit/iteration-17-reconciliation-20261025/LEDGER.json")["items"]
work = read("audit/all-iterations-remaining-20261027/WORK-ITEMS.json")["items"]
work_ids = {x["id"] for x in work}
iterations = [dict(zip(("iteration", "title", "status", "proof", "evidence", "remaining_item_ids"), row)) for row in ITERATIONS]
iteration_by_id = {x["iteration"]: x for x in iterations}
save("ITERATIONS.json", {"baseline_revision": BASELINE, "receipt_policy": "Retained finite observations; no fresh runtime tests or automatic whole-iteration supersession.", "iterations": iterations})

hist_rows = []
for h in historical:
    row = dict(h)
    row["i17_disposition"] = row.pop("disposition")
    row["i17_scope"] = row.pop("scope")
    row["remaining_item_ids"] = HMAP.get(h["id"], [])
    row["current_disposition"] = "retained_" + row["i17_disposition"]
    row["current_note"] = "Retain the I17 finite definition/implementation scope and original references; do not upgrade empirical or unseen-provider claims."
    if h["id"] in HMAP and h["id"] != "H099":
        row["current_disposition"] = "remaining_scope_explicitly_routed"
        row["current_note"] = "Use the linked concrete closure items. Later accepted work narrows the original umbrella; this does not create a new whole-graph acceptance."
    if h["id"] == "H099":
        row["current_disposition"] = "closed_by_later_selected_qualification"
        row["current_note"] = "I23 actual Gemini Free text flow and21-case repaired clean acceptance de1c7b2 close this previously optional selected qualification; I29's later outage remains a separate actual observation."
        row["references"] += ["audit/iteration-23-verification-20261026/ACCEPTANCE.json"]
    if h["id"] in {"H011", "H052", "H058"}:
        row["current_note"] += " Production ElevenLabs dictionaries/ordinary flow are already accepted inI22; retain only actual remaining acoustic/subtype/interaction scope."
        row["references"] += ["audit/iteration-22-elevenlabs-20261026/ACCEPTANCE.json"]
    if h["id"] == "H096":
        row["current_disposition"] = "landing_done_final_release_review_remaining"
        row["current_note"] = "Original landing and current main/publication are done. Both checkouts point to324d8e7. I30's full UI/clean acceptance remains open; no new merge is needed merely to repair this dated row."
    if h["id"] == "H098":
        row["current_note"] = "I5 native cases, later own-Pro flow, actual I29 complete flow and current main landing exist. Reconcile their literal scopes without inventing a retrospective I5 receipt; I30 full review remains open."
    if h["id"] in {"H014", "H020"}:
        row["current_note"] += " Official L2 acquisition/provenance is now resolved; actual full normalized import remains distinct. Six original owner releases remain unavailable."
    hist_rows.append(row)
save("HISTORICAL-101.json", {"baseline_revision": BASELINE, "items": hist_rows})

task_rows = []
section = ""
baseline_task_text = subprocess.run(
    ["git", "show", f"{BASELINE}:openspec/changes/implement-teacher-error-trainer/tasks.md"],
    cwd=ROOT, check=True, capture_output=True, text=True,
).stdout
baseline_open = [line for line in baseline_task_text.splitlines() if re.match(r"\s*- \[ \]", line)]
assert len(baseline_open) == 42
for number, line in enumerate((CHANGE / "tasks.md").read_text().splitlines(), 1):
    if line.startswith("#"):
        section = line
    if not re.match(r"\s*- \[ \]", line):
        continue
    h = re.search(r"I17 (H\d{3})", line)
    if h:
        items = HMAP[h[1]]
        note = next(x["current_note"] for x in hist_rows if x["id"] == h[1])
    elif re.search(r"\bI24[.\s]", line):
        items, note = ["QUAL-01", "VER-01"], "Native repairs pass; actual resource/audio/interaction and full acceptance remain incomplete."
    elif re.search(r"\bI25[.\s]", line):
        items, note = ["QUAL-02", "VER-01"], "Controlled implementation passes; full actual pair and activation remain unobserved."
    elif re.search(r"\bI26[.\s]", line):
        items, note = ["VER-01"], "The selected I26 gate lacks its one actual interaction case; no universal acoustic certification is required."
    elif re.search(r"\bI27[.\s]", line):
        items, note = ([f"DATA-{n:02}" for n in range(1, 7)] + ["VER-01"]), "Six actual owner releases plus selected interaction remain unavailable; repaired import mechanisms retain their scope."
    elif re.search(r"\bI30[.\s]", line):
        items, note = ["VER-02"], "Publication/archive/native startup and harness repairs have observations; workflow boxes stay unchecked until the complete clean acceptance."
    elif "ALL-AUDIT" in line:
        items, note = ["TRACE-01", "ENG-01"], "Newly explicit follow-up routes from this audit; no implementation claimed."
    else:
        raise ValueError(f"Unrouted open task {number}: {line}")
    task_rows.append({"line_at_audit": number, "section": section, "text": line, "historical_id": h[1] if h else None, "closure_item_ids": items, "current_note": note})
assert {row["text"] for row in task_rows}.issuperset(baseline_open)
save("OPEN-TASKS.json", {"baseline_revision": BASELINE, "baseline_unchecked_rows": 42, "baseline_literals_all_preserved": True, "current_unchecked_rows": len(task_rows), "acceptance_rule": "Unchecked is not necessarily unimplemented. None is checked by this research audit.", "tasks": task_rows})

coverage = read("audit/category-realization-20261025/COVERAGE.json")
gaps = read("audit/category-realization-20261025/QUALIFICATION-GAPS.json")
categories = []
group_by_category = {r["category_id"]: group for group, rows in gaps["groups"].items() for r in rows}
for c in coverage["categories"]:
    c = dict(c)
    c["historical_outcome_group"] = group_by_category.get(c["category_id"], "confirmed")
    c["closure_item_ids"] = [] if c["audio"]["audio_confirmation"] == "confirmed" else ["QUAL-03"]
    if c["category_id"] == "discourse.turn_taking":
        c["unimplemented_subtype"] = gaps["unimplemented_subtype"]
        c["closure_item_ids"] += ["ENG-01"]
    c["later_selected_evidence"] = "audit/iteration-26-acoustic-20261026/REPORT.md (separate finite contrasts; original population is not rewritten)"
    categories.append(c)
save("CATEGORIES.json", {"baseline_revision": BASELINE, "scope": "Exact original finite population and bindings, not a new listening campaign or universal accuracy.", "counts": gaps["counts"], "categories": categories})

graph = read("openspec/changes/implement-teacher-error-trainer/verification.json")
properties = {p["id"]: p for p in graph["properties"]}
category_by_id = {x["category_id"]: x for x in categories}
unmaterialized = []
prop_rows = {}
states_by_property = collections.defaultdict(collections.Counter)
for case in graph["cases"]:
    states_by_property[case["property_id"]][case["state"]] += 1
for case in graph["cases"]:
    if case["state"] == "implemented":
        continue
    prop = properties[case["property_id"]]
    cat = next((category_by_id[x] for x in re.findall(r"`([^`]+)`", prop["statement"]) if x in category_by_id), {})
    route = graph_route(prop, cat)
    row = {k: case.get(k) for k in ["id", "property_id", "polarity", "state", "test_id"]}
    row["routing_property_id"] = prop["id"]
    unmaterialized.append(row)
    if prop["id"] not in prop_rows:
        prop_rows[prop["id"]] = {
            "property_id": prop["id"], "requirement_id": prop["requirement_id"],
            "owner": prop["owner"], "states": dict(states_by_property[prop["id"]]),
            "disposition": route["disposition"], "closure_item_ids": route["closure_item_ids"],
            "candidate_iterations": route["candidate_iterations"],
            "category_id": cat.get("category_id"), "case_ids": [],
            "exact_equivalence_established_by_this_audit": False,
        }
    prop_rows[prop["id"]]["case_ids"].append(case["id"])
counts = dict(collections.Counter(c["state"] for c in graph["cases"]))
triage = {
    "baseline_revision": BASELINE,
    "source_manifest": "openspec/changes/implement-teacher-error-trainer/verification.json",
    "lookup": "Read the exact canonical property/case by its retained ID at the baseline. Original statements, setup, fixture/oracle and blockers are not duplicated here. Candidate iteration receipts are in ITERATIONS.json; native category case IDs are in CATEGORIES.json.",
    "graph_counts": {"requirements": len(graph["requirements"]), "properties": len(graph["properties"]), "cases": len(graph["cases"]), "commands": len(graph["commands"]), "case_states": counts},
    "unmaterialized_property_count": len(prop_rows),
    "warning": "Routing/candidate evidence only. This audit does not prove exact literal equivalence, execute cases or modify graph states.",
    "remaining_action": "Compare each original literal fixture/oracle with the actual successor assertion/receipt. Reuse only a full exact match; preserve unmet data/observations and materialize only uncovered behavior. No blanket prefix match is proof.",
    "properties": list(prop_rows.values()), "cases": unmaterialized,
}
# One JSON object per row keeps all identities without duplicating thousands of
# lines of canonical fixtures or the same candidate-receipt text per case.
lines = ["{"]
for key, value in triage.items():
    if key in {"properties", "cases"}:
        lines.append(f'  "{key}": [')
        lines.extend("    " + json.dumps(row, ensure_ascii=False) + ("," if n < len(value) - 1 else "") for n, row in enumerate(value))
        lines.append("  ]" + ("," if key != "cases" else ""))
    else:
        lines.append("  " + json.dumps(key) + ": " + json.dumps(value, ensure_ascii=False) + ",")
lines.append("}")
(OUT / "GRAPH-TRIAGE.json").write_text("\n".join(lines) + "\n")

sources = [
    ("TET-GOLD-1", "definition/fixtures; complete independent gold population absent", "conditional fixed-benchmark data, not a startup exercise bank", ["DATA-08", "EMP-02"]),
    ("SPEECHOCEAN762", "complete native bytes and actual full import", "60,427accepted native rows; all5,245WAV including245unrated, not only5,000rated", []),
    ("L2-ARCTIC", "official v5 bytes/provenance complete; full normalized import unobserved", "24speakers+suitcase+4documents; original annotation layers/media", ["DATA-07"]),
    ("WILOCNESS-2.1", "complete bytes and actual full import", "all native partitions including4,477withheld-label originals; no invented test gold", []),
    ("FCE-2.1", "complete bytes and actual full import", "all native components and33,236sentence representations", []),
    ("EFCAMDAT-R2", "metadata/dictionary research; owner release unavailable", "separate full original XML/prompts/docs/use scope", ["DATA-01"]),
    ("EFCAMDAT-SHATZ2020", "documentary scope; owner release unavailable", "both complete samples and supplied intermediates/glossary/scripts", ["DATA-02"]),
    ("EFCAMDAT-OKSUZ2025", "four public companions present; full owner derivative unavailable", "full paired/error-coded/POS workbook and actual dictionary", ["DATA-03"]),
    ("DOUBAO-STUDY-RECORDS", "paper/docs present; participant/instrument release unavailable", "authorized full native study export/terms, not recreated study features", ["DATA-04"]),
    ("MOODRICK-DATA", "public docs/inquiry; export unavailable", "its own complete authorized scoped sessions/media/dictionary/terms", ["DATA-05"]),
    ("NIR-DATA", "public docs/inquiry; export unavailable", "separate authorized scoped sessions/media/dictionary/terms", ["DATA-06"]),
]
save("SOURCES.json", {"baseline_revision": BASELINE, "original_source_count": 11, "scope": "Acquisition, native import and empirical gold are separate states; no source definition or actual data is dropped.", "sources": [dict(zip(("source_id", "current_state", "full_scope", "closure_item_ids"), row)) for row in sources], "supplements": [{"source_id": n, "closure_item_ids": items} for n, items in [("JFLEG", ["SUP-04"]), ("EdAcc", ["SUP-04"]), ("ELRD", ["SUP-04"]), ("DiPlomat", ["SUP-04"]), ("DRAL", ["SUP-02", "SUP-04"]), ("ICNALE", ["SUP-03"]), ("Speak&Improve2025", ["SUP-01"])]]})

report_paths = sorted({p for p in (ROOT / "audit").glob("iteration-*/*") if p.name in {"REPORT.md", "VERIFY.md", "VERIFY-REPORT.md", "ACCEPTANCE.md"}} | set((ROOT / "audit").glob("iterations-1-2*/REPORT.md")))
pattern = re.compile(r"block|remain|optional|external|not_run|not run|partial|unavailable|incomplete|missing|pending|qualification|not accepted|cannot", re.I)
scan = []
for path in report_paths:
    lines = path.read_text().splitlines()
    scan.append({"path": str(path.relative_to(ROOT)), "line_count": len(lines), "residual_line_excerpts": [{"line": n, "excerpt": line[:350]} for n, line in enumerate(lines, 1) if pattern.search(line)]})
save("REPORT-SCAN.json", {"baseline_revision": BASELINE, "method": "Complete lexical scan of every listed report; dated history is not automatically current. The iteration/work-item tables identify reviewed authoritative successors.", "reports": scan})

md = ["# All iterations: current status and closure routes", "", f"Baseline `{BASELINE}`; research dated 2026-10-27. Retained receipts are not fresh execution.", "", "The quoted I17 six-case report is historical. Latest I17 verification accepted 47/47; later iterations 18–23, 28 and 29 also have scoped acceptance. I24/I25/I26/I27/I30 remain incomplete. I4/I5 have native acceptance plus later selected live evidence, requiring truthful scope reconciliation rather than a fabricated retrospective receipt.", "", "| Iteration | Scope | Current finite evidence | Remaining routes |", "|---|---|---|---|"]
for row in iterations:
    md.append(f"| {row['iteration']} | {row['title']} | {link(row['evidence'], row['proof'])}; `{row['status']}` | {', '.join(row['remaining_item_ids']) or 'No new in-scope residual identified'} |")
md += ["", "Scope links name associated broader/optional work, not newly failed iteration acceptance. All original receipts keep their exact revision, inputs and proof boundary.", "", "See [the full closure plan](CLOSURE-PLAN.md), [101 historical rows](HISTORICAL-101.json), [every unchecked task](OPEN-TASKS.json), [all historical graph placeholders](GRAPH-TRIAGE.json), [all 122 categories](CATEGORIES.json) and [all 11 original sources](SOURCES.json)."]
(OUT / "ITERATIONS.md").write_text("\n".join(md) + "\n")

md = ["# Complete remaining-work closure plan", "", "This is a research plan, not an implementation receipt or a second checklist. Canonical task status remains in the selected OpenSpec tasks.md. The30items include a repaired documentation item, conditional/excluded scopes and evidence work; they are not30missing product features.", "", "Use valid retained greens and materialize only missing literal behavior. No paid credits/overage, silent fallback, human peer review, corpus prerequisite, repeated stored-data audit or new learner gate is introduced.", ""]
for item in work:
    md += [f"## {item['id']} — {item['title']}", "", f"**Classification:** `{item['kind']}`; **status:** `{item['status']}`; **iterations:** {', '.join(map(str,item['iterations']))}.", "", f"**Product use.** {item['product_use']}", "", f"**Already implemented/observed.** {item['implemented']}", "", f"**Exact remainder.** {item['missing']}", "", "**Closure actions.**", ""]
    md += [f"{n}. {step}" for n, step in enumerate(item["steps"], 1)]
    md += ["", f"**Positive expectation.** {item['positive']}", "", f"**Negative expectation.** {item['negative']}", "", f"**Required input/decision.** {item['prerequisite']}", "", f"**Single owners.** {', '.join(link(p) for p in item['owners'])}.", "", f"**Retained evidence.** {', '.join(link(p) for p in item['references'])}.", "", f"**Dependencies.** {', '.join(item['depends_on']) or 'None beyond the input stated above.'}", ""]
(OUT / "CLOSURE-PLAN.md").write_text("\n".join(md))

# Structural inventory coverage only; not a product test or execution gate.
assert len(iterations) == 30 and {x["iteration"] for x in iterations} == set(range(1, 31))
assert len(hist_rows) == 101 and len({x["id"] for x in hist_rows}) == 101
assert len(task_rows) == 44
assert len(categories) == 122 and len({x["category_id"] for x in categories}) == 122
assert len(sources) == 11
assert counts == {"blocked": 1895, "planned": 14, "implemented": 4797}
assert len(unmaterialized) == 1909 and len(prop_rows) == 389
assert sum(gaps["counts"].values()) == 122
for item in work:
    assert item["positive"] and item["negative"] and item["steps"] and item["prerequisite"]
    assert set(item["depends_on"]) <= work_ids
    for path in item["owners"] + item["references"]:
        assert (ROOT / path).exists(), (item["id"], path)
for row in iterations:
    assert (ROOT / row["evidence"]).exists()
    assert set(row["remaining_item_ids"]) <= work_ids
for row in hist_rows + task_rows:
    assert set(row.get("remaining_item_ids", row.get("closure_item_ids", []))) <= work_ids
for row in unmaterialized:
    route = prop_rows[row["routing_property_id"]]
    assert set(route["closure_item_ids"]) <= work_ids
    assert route["exact_equivalence_established_by_this_audit"] is False
save("INVENTORY-CHECK.json", {"status": "passed", "proof": "Research inventory coverage/reference assertions only; no application/model/UI test ran.", "baseline_revision": BASELINE, "iterations": 30, "historical_rows": 101, "baseline_open_tasks": 42, "current_open_tasks": len(task_rows), "categories": 122, "original_sources": 11, "work_items": len(work), "report_files_scanned": len(scan), "graph_cases": 6706, "blocked_cases": 1895, "planned_cases": 14, "unmaterialized_properties": 389, "exact_placeholder_equivalence_proved": 0, "new_model_calls": 0, "new_synthesis_calls": 0, "new_product_tests": 0})
print(json.dumps(read("audit/all-iterations-remaining-20261027/INVENTORY-CHECK.json"), indent=2))
