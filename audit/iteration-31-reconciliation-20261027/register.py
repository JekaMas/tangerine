"""Register the inspected I31 population. Does not execute any product/test call.

New full bindings are enumerated by tests that consume the actual old literals.
Candidate ranking is only inspection routing and never promotes a case.
"""
import ast
from collections import defaultdict
import copy
import hashlib
import json
from pathlib import Path
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reconcile as r
from requirement_tests import parse_delta_specs

ROOT, BASE = r.ROOT, r.ROOT / r.CHANGE
graph = json.loads((BASE / "verification.json").read_text())
original = r.original_cases()
bindings = r.original_bindings()
old_graph = r.frozen(r.CHANGE + "/verification.json")
old_cases = {c["id"]: c for c in old_graph["cases"]}
old_props = {p["id"]: p for p in old_graph["properties"]}
triage = {p["property_id"]: p for p in json.loads((ROOT / "audit/all-iterations-remaining-20261027/GRAPH-TRIAGE.json").read_text())["properties"]}
source_hashes = {}


def digest(path):
    if path not in source_hashes:
        source_hashes[path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    return source_hashes[path]



lf_recon = json.loads((ROOT / "audit/linguistic-fullness-20261023/RECONCILIATION.json").read_text())
lf_refs = {x["taxonomy_id"]: x for x in json.loads((ROOT / "services/api/internal/app/testdata/linguistic-contrasts.json").read_text())["examples"]}
lf_log = "data/linguistic-fullness-20261023/native-contract-final.jsonl"
lf_receipt = "data/linguistic-fullness-20261023/native-contract-final.receipt.json"
lf_observed = r.parse_go_events((ROOT / lf_log).read_text())
assert json.loads((ROOT / lf_receipt).read_text())["exit_code"] == 0


def partials(b):
    if b["action"] != r.CATEGORY_ACTION:
        return []
    leaf = b["input"].get("leaf")
    if leaf not in lf_refs:
        return []
    out = []
    for prefix, method, assertion in [
        ("LF-01.P1.", "TestLinguisticContextPositive", "Native generation and mapper context retain the exact selected identity and explicit correct-control criteria; this does not decide the old answer or hear audio."),
        ("LF-03.P1.", "TestLinguisticRecipePositive", "The actual native recipe/reference equality and written-edit replay retain this same authored canonical/surface pair; mapping and audio remain unproved.")]:
        if "Recipe" in method:
            x = b["input"]
            if x.get("canonical") != lf_refs[leaf]["canonical"] or x.get("surface") != lf_refs[leaf]["surface"]:
                continue
        case_id = prefix + method + "." + leaf
        candidate = old_cases.get(case_id)
        if not candidate or lf_recon["native_case_receipts"].get(case_id) != "native-contract-final.jsonl" or lf_observed.get(candidate["test_id"]) != "pass":
            continue
        out.append(dict(case_id=case_id,test_id=candidate["test_id"],receipt=lf_log,command_receipt=lf_receipt,
                        assertion=assertion,proves_entire_original_case=False))
    return out


def source_excerpt(c):
    path = ROOT / c["source_path"]
    text = path.read_text()
    method = c["test_id"].rsplit("::",1)[-1].split("/",1)[0].rsplit(".",1)[-1]
    lines = text.splitlines()
    if path.suffix == ".go":
        start = next((i for i,line in enumerate(lines) if re.match(r"func " + re.escape(method) + r"\(",line)),0)
        end = next((i for i in range(start+1,len(lines)) if lines[i].startswith("func ")),min(start+75,len(lines)))
    else:
        node = next((x for x in ast.walk(ast.parse(text)) if isinstance(x,(ast.FunctionDef,ast.AsyncFunctionDef)) and x.name==method),None)
        start,end = (node.lineno-1,node.end_lineno) if node else (0,30)
    assertions = [line.strip() for line in lines[start:end] if any(k in line for k in ["assert", "if ", "t.Fatal", "expect(", "require"])]
    return dict(case_id=c["id"],test_id=c["test_id"],source_path=c["source_path"],line=start+1,
                assertion_excerpt=assertions[:10],classification="candidate_not_equivalence")


def candidates(pid):
    selected = []
    text = old_props[pid]["statement"]
    words = set(re.findall(r"[a-z]{5,}",text.lower())) - {"system","shall","their","actual","which","without"}
    iterations = triage[pid]["candidate_iterations"]
    ranked = []
    for c in old_graph["cases"]:
        if c["state"] != "implemented":continue
        scope = c["property_id"] + " " + c["command_id"]
        if not any(re.search(r"(?:^I|iteration|completion-i)"+str(n)+r"(?:-|\.|$)",scope) for n in iterations):continue
        tokens = set(re.findall(r"[a-z]{5,}",(c["test_id"]+" "+c["observable"]+" "+c["source_path"]).lower()))
        ranked.append((len(words & tokens),c))
    seen = set()
    for _,c in sorted(ranked,key=lambda x:(-x[0],x[1]["id"])):
        if c["source_path"] in seen:continue
        seen.add(c["source_path"]);selected.append(source_excerpt(c))
        if len(selected)==3:break
    return selected


rows = []
property_rows = []
current = {c["id"]:c for c in graph["cases"]}
for pid in triage:
    source_candidates = candidates(pid)
    property_rows.append(dict(property_id=pid,statement=old_props[pid]["statement"],scenarios=old_props[pid]["scenarios"],
                              inspected_candidates=source_candidates,warning="These inspected successor assertions are not full literal equivalence; only explicit literal/component bindings below carry proof."))
    for cid in triage[pid]["case_ids"]:
        old,b=original[cid],bindings[cid]
        c=copy.deepcopy(old)
        owner=old_props[pid]["owner"]
        literal=r.literal_binding(cid,b)
        retained=partials(b)
        disposition="literal_observation_missing"
        remainder=[dict(path="expected."+k,value=v) for k,v in b["expected"].items()]
        comparison="Successor native owners exist, but the original complete input/action/expected packet has no exact registered physical observation. Candidate assertions are retained as candidates, not promoted by their name, counts or report status."
        if literal:
            disposition="materialized_literal";remainder=[]
            comparison="The enumerated literal test consumes these original inputs and independently authored expectations. A paired stateless scope may reuse the exact union of its accepted and rejected observations; no original lexical text, counter or expected result is replaced."
            c.update(state="implemented",test_id=literal["test_id"],command_id=literal["command_id"],source_path=literal["source_path"],source_sha256=digest(literal["source_path"]),
                     substitution=dict(classification="NO_TEST_DOUBLE",proof_claims=[literal["proof"]],forbidden_claims=["Full product/provider/source/empirical or heard-audio acceptance"]),
                     distinct_reason=old["scenario"]+": exact historical literal "+cid+"; the physical method explicitly covers this input/expectation packet.")
            c.pop("blocker",None)
            c["fixture_observation_state"]="implemented_observation_retained_separately"
            dependencies=[literal["source_path"],"specification/v2/domain/verification-fixtures.v1.json"]
            if "Auxiliary" in literal["test_id"]:
                dependencies += ["services/api/internal/scoring/auxiliary.go","services/api/internal/scoring/rational.go","services/api/internal/scoring/testdata/historical-auxiliary.json"]
            if "HistoricalMutation" in literal["test_id"]:
                dependencies += ["services/api/internal/app/mutation_content.go","services/api/internal/app/mutation_manifest.go","services/api/internal/app/mutation_content_test.go","services/api/internal/contracts/**"]
            if "HistoricalUnicode" in literal["test_id"]:
                dependencies += ["services/api/internal/app/interpretation_claims.go"]
            if literal["command_id"]=="i31-arithmetic-literals":
                dependencies += ["services/speech/metrics.py","domain/metrics.v1.yaml"]
            if literal["command_id"]=="completion-i31":
                dependencies += ["audit/iteration-31-reconciliation-20261027/OBSERVATIONS.json","audit/iteration-31-reconciliation-20261027/reconcile.py",".agents/workflow/scripts/requirement_tests.py"]
            c["invalidation_dependencies"]=list(dict.fromkeys(old["invalidation_dependencies"]+dependencies))
        else:
            if retained:disposition="partial_exact_reuse"
            if triage[pid]["disposition"]=="conditional_data_or_native_measurement_scope_no_bulk_campaign":
                comparison="The earlier triage linked this property to a conditional empirical/source consumer. Inspection of this exact packet finds constructed counts, absent-observation behavior or controlled native state, not a need to acquire people, source bytes or a provider account to test it. It remains local literal test work; the authentic consumer population remains separately unobserved."
            if pid.startswith("DOM-05.") and b["input"]==dict(numerator="1",denominator="0"):
                disposition="fixture_conflict"
                comparison="The historical variant expects N/A for inconsistent 1/0, while the specified public ratio owner and its existing invalid-counter test reject it. New actual witness retains that rejection; this is not a missing product feature or permission. Original input/expectation is preserved and is not relabelled passed."
            c["state"]="blocked" if disposition in ["conditional_population_or_qualification","fixture_conflict"] else "planned"
            c["blocker"]=comparison+" Exact unresolved fields: "+", ".join(x["path"] for x in remainder)+". See I31 ledger for actual successor/partial scope."
        c["reconciliation"]="audit/iteration-31-reconciliation-20261027/LEDGER.json#"+cid
        current[cid]=c
        rows.append(dict(case_id=cid,property_id=pid,owner=owner,original_state=old["state"],original_test_id=old["test_id"],fixture_id=b["fixture_id"],fixture_mode=b["mode"],
                         original_binding="specification/v2/domain/verification-fixtures.v1.json#case_bindings/"+cid,
                         original_expected=b["expected"],disposition=disposition,literal_test=literal,
                         partial_evidence=retained,candidate_case_ids=[x["case_id"] for x in source_candidates],
                         comparison=comparison,remaining_assertions=remainder,
                         continuation_item_ids=triage[pid]["closure_item_ids"]))

# The original accepted cases are copied intact, not refreshed or promoted.
graph["cases"]=[current[c["id"]] for c in graph["cases"] if c["property_id"] not in {"TRACE31.P1","TRACE31.P2","TRACE31.P3","TRACE31.P4","TRACE31.P5"}]
packet=dict(baseline_revision=r.BASELINE,scope="All 1909 original planned/blocked literals. Original unmatched product assertions remain open; complete reconciliation is not whole-product acceptance.",cases=rows)
(HERE/"LEDGER.json").write_text(json.dumps(packet,indent=2,ensure_ascii=False)+"\n")
(HERE/"PROPERTY-COMPARISONS.json").write_text(json.dumps(property_rows,indent=2,ensure_ascii=False)+"\n")

new_commands=[
 dict(id="completion-i31",runner="python-unittest",argv=["python3","-B","-m","unittest","-v","tests.test_completion_i31"],cwd=".",env={},timeout_seconds=180,authority="local"),
 dict(id="i31-arithmetic-literals",runner="python-unittest",argv=["python3","-B","-m","unittest","-v","tests.test_historical_literals"],cwd=".",env={},timeout_seconds=30,authority="local"),
 dict(id="i31-go-literals",runner="go-test-json",argv=["./tests/go-docker","test","-json","-race","-count=1","-run",r"^TestHistorical(Unicode.*|Mutation.*|Auxiliary(Positive|Negative))$/^(AUX-[0-9]+\.P1(\.SET2)?\.POSITIVE|AUX-[0-9]+\.P1\.NEGATIVE)$","./internal/app","./internal/scoring"],cwd=".",env={},timeout_seconds=1200,authority="local"),
 dict(id="i31-aux-counterexamples",runner="go-test-json",argv=["./tests/go-docker","test","-json","-race","-count=1","-run",r"^TestHistoricalAuxiliaryNegative$/^AUX-(01|02|03|04|05|06|07|08|09|12|13|14|15)\.P1\.SET2\.NEGATIVE$","./internal/scoring"],cwd=".",env={},timeout_seconds=1200,authority="local")]
graph["commands"]=[x for x in graph["commands"] if x["id"] not in {x["id"] for x in new_commands}]+new_commands
pending=next(x for x in graph["commands"] if x["id"]=="pending")
pending["expected_markers"]=[c["test_id"] for c in graph["cases"] if c["command_id"]=="pending"]
spec=parse_delta_specs(BASE)[("evidence-reconciliation","TRACE31 Historical literal evidence reconciliation")]
graph["requirements"]=[x for x in graph["requirements"] if x["id"]!="TRACE31"]+[dict(id="TRACE31",capability="evidence-reconciliation",title="TRACE31 Historical literal evidence reconciliation",fingerprint=spec["fingerprint"])]
graph["properties"]=[x for x in graph["properties"] if x["requirement_id"]!="TRACE31"]
selections=[
 (1,"TRACE31 Original population and independent expectations",["test_population_positive","test_population_omission_negative","test_expected_literal_change_negative","test_test_identity_negative","test_discovery_aliases_positive","test_retired_discovery_identity_negative","test_joint_literal_alias_negative","test_discovery_prior_rewrite_negative"]),
 (2,"TRACE31 Typed observations and literal execution",["test_new_literal_observations_positive","test_counterfeit_observation_negative","test_ratio_pair_positive","test_ratio_pair_negative","test_unicode_pair_positive","test_unicode_pair_negative","test_missing_literal_population_negative","test_native_receipt_drift_negative"]),
 (3,"TRACE31 Exact partial reuse without promotion",["test_retained_component_reuse_positive","test_missing_partial_receipt_negative","test_partial_promotion_negative","test_partial_leaf_alias_negative"]),
 (4,"TRACE31 Unchanged product and accepted history",["test_product_sources_preserved_positive","test_prior_accepted_case_rewrite_negative","test_false_external_blocker_negative","test_historical_scope_positive","test_historical_scope_change_negative","test_browser_read_recovery_positive","test_browser_no_dispatch_negative"]),
 (5,"TRACE31 Static validation is not execution",["test_unobserved_scope_positive","test_static_summary_not_execution_negative"])]
for n,scenario,methods in selections:
 pid="TRACE31.P"+str(n)
 graph["properties"].append(dict(id=pid,requirement_id="TRACE31",statement=scenario+" through exact original fixtures, actual typed native outputs and unchanged source bindings; no optional population or unsupported behavior is promoted.",scenarios=[scenario],owner="audit/iteration-31-reconciliation-20261027/reconcile.py",oracle="Original frozen case IDs/expectations; actual exact typed native test observations, independently stated literal counters/spans/edits and contrary input cases.",source_globs=["audit/iteration-31-reconciliation-20261027/**","audit/iteration-31-verification-20261027/**","tests/test_completion_i31.py","tests/test_historical_literals.py","services/api/internal/app/historical_literals_test.go","services/api/internal/scoring/historical_literals_test.go"],iteration=31))
 for method in methods:
  graph["cases"].append(dict(id=pid+"."+method,property_id=pid,polarity="positive" if method.endswith("positive") else "negative",scenario=scenario,scenario_fingerprint=spec["scenario_fingerprints"][scenario],setup="Run the exact I31 reconciliation test on the frozen 1909-case population and actual retained native outputs; controlled forged metadata is confined to temporary development receipts.",observable=scenario+": "+method,red_expectation="A changed original fixture, incomplete/forged observation or unsupported full-case promotion violates the independently authored assertion.",green_expectation="The original exact identities/expectations and native observations hold; every counterexample is detected without provider dispatch or a product gate.",test_id="unittest::tests.test_completion_i31.CompletionI31."+method,command_id="completion-i31",state="implemented",source_path="tests/test_completion_i31.py",source_sha256=digest("tests/test_completion_i31.py"),invalidation_dependencies=["tests/test_completion_i31.py","audit/iteration-31-reconciliation-20261027/reconcile.py","audit/iteration-31-reconciliation-20261027/LEDGER.json","audit/iteration-31-reconciliation-20261027/OBSERVATIONS.json"],substitution=dict(classification="NO_TEST_DOUBLE",proof_claims=["Actual development reconciliation/runner and retained native test observations"],forbidden_claims=["Application UI/provider/linguistic or whole-release acceptance"]),distinct_reason=scenario+": this exact reconciliation assertion is owned by "+method+"; retained literal components are not reexecuted."))
  if "discovery" in method:
   graph["cases"][-1]["invalidation_dependencies"] += ["openspec/changes/implement-teacher-error-trainer/discovery.json",".agents/workflow/scripts/discovery_ledger.py","audit/iteration-31-verification-20261027/APPLY-ACCEPTANCE.json"]
  if "browser" in method:
   graph["cases"][-1]["invalidation_dependencies"] += ["services/web/app/**","services/web/public/fonts/SourceSans3.ttf","data/iteration-31-verification-20261027/ui-observations.json","data/iteration-31-verification-20261027/requests.jsonl"]

(BASE/"verification.json").write_text(json.dumps(graph,indent=2)+"\n")
props=["TRACE31.P"+str(n) for n in range(1,6)]
selected=[c["id"] for c in graph["cases"] if c["command_id"]=="completion-i31"]
selection=dict(iteration=31,verify_property_ids=props,run_selectors=dict(commands="completion-i31"),iteration_case_ids=selected,expected_case_count=len(selected),retained_literal_case_ids=[x["case_id"] for x in rows if x["disposition"]=="materialized_literal"],execution="Run actual new physical literal tests once; the full I31 metadata selection reuses their typed outputs and existing unchanged components. No full-product run, benchmark or provider dispatch.",baseline_revision=r.BASELINE)
(HERE/"SELECTION.json").write_text(json.dumps(selection,indent=2)+"\n")
# Retired planned names stay historical. Do not rewrite an old review to claim
# that it already inspected these newly materialized test methods.
discovery_path=BASE/"discovery.json"
discovery=json.loads(discovery_path.read_text())
known={c["test_id"] for c in graph["cases"]}
for scope in [discovery["scope"]]+discovery["reviews"]:
 retired=[t for t in scope["test_ids"] if t not in known]
 if retired:
  scope["historical_test_ids"]=list(dict.fromkeys(scope.get("historical_test_ids",[])+retired))
  scope["test_ids"]=[t for t in scope["test_ids"] if t in known]
  scope["history_note"]="I31 retains these retired planned identities as history; their replacement methods are reviewed only by the dated I31 review, not retroactively by this earlier record."
active=list(dict.fromkeys(c["test_id"] for c in graph["cases"] if c["id"] in set(selected+selection["retained_literal_case_ids"])))
discovery["scope"]["test_ids"]=list(dict.fromkeys(discovery["scope"]["test_ids"]+active))
discovery["scope"]["property_ids"]=list(dict.fromkeys(discovery["scope"]["property_ids"]+props))
review=next((x for x in discovery["reviews"] if x["id"]=="iteration31-verification-20261027"),None)
if review is None:
 review=copy.deepcopy(next(x for x in discovery["reviews"] if x["id"]=="iteration31-literal-reconciliation-20261027"))
 review["id"]="iteration31-verification-20261027"
 discovery["reviews"].append(review)
review["question"]="Verify I31 literal/partial identity, complete observation population, actual command outcomes, retained history and requested UI recovery evidence."
review["rationale"]="Five fixed review counterexamples, exact original command receipts and browser GET-only failure/recovery observations. Preserve the prior apply review and its actual scope. No product/provider acceptance is inferred."
review["test_ids"]=active
stats=r.counts(packet)
review["searches"][0]["outcome"]=f"{stats['materialized_literal']} original literal edges materialized;{stats['partial_exact_reuse']} exact category-workflow components retained without full promotion;{stats['literal_observation_missing']} complete literal joins unestablished;{stats['fixture_conflict']} conflicting ratio vectors remain open. Shared leaf identifiers in unrelated operations are not component proof. The51 coarse conditional labels are constructed native fixtures and ordinary planned test work. All original accepted registrations and retired planned discovery identities are preserved."
review["searches"][0]["query"]="Actual fixture-to-method projection, all literal outputs/command receipts, missing/aliased/failed counterexamples, prior review preservation and read-only browser route/recovery observations."
review["searches"][0]["results"] += [{"path":path,"classification":"interface_dependency","reason":"Current I31 verification/repair source or actual review evidence inspected."} for path in ["audit/iteration-31-reconciliation-20261027/reconcile.py","tests/test_completion_i31.py","audit/iteration-31-verification-20261027/REPORT.md"] if path not in {item["path"] for item in review["searches"][0]["results"]}]
review["searches"][1]["query"]="jbcontext search: Where is the local browser review gateway which proxies the built frontend and injects controlled read failures while preventing provider calls?"
discovery_path.write_text(json.dumps(discovery,indent=2)+"\n")
print(json.dumps(dict(original_cases=len(rows),properties=len(property_rows),dispositions=r.counts(packet),literal_case_edges=len(selection["retained_literal_case_ids"])),indent=2))
