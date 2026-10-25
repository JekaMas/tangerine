"""Explicit finite local/free observations; report reads never make model calls.

Uses the application's native speech/auditory owners. No SDK, account change,
download, automatic retry, paid fallback or ordinary configuration activation.
"""
import argparse
import base64
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.request
import uuid
import wave

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "data/category-realization-20261025"
DEFAULT_OUT = OUT
sys.path.insert(0, str(ROOT / "services/speech"))
from category_validation import blind_input, compare_probe, coverage, make_probe, saved_observation

ENV = {**os.environ, "DOCKER_HOST": "unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock",
       "DOCKER_CONFIG": str(ROOT / "data/local-preview/docker-config")}
PROFILE = dict(id="kokoro-local-en-v1", provider="local_kokoro", adapter_version="kokoro-local-v1",
               model="Kokoro-82M", billing_mode="local", voices=[dict(id="af_heart", locale="en-US")])
REMOTE = "/tmp/tangerine-category-candidate"


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def docker(*args, data=None, timeout=280):
    result = subprocess.run(["docker", *args], input=data, cwd=ROOT, env=ENV,
                            capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError("Native command failed; inspect retained local stderr: " + result.stderr.decode(errors="replace")[-600:])
    return result.stdout


def worker(packet, directory, candidate=False):
    request, response = directory / "request.json", directory / "response.json"
    if request.exists() and not response.exists():
        return {"error": "INTERRUPTED_OBSERVATION", "reason": "A prior prepared/initiated operation has no result; inspect its capture or select a new explicit experiment. No redispatch."}
    def perform():
        save(request, packet)
        remote_capture = REMOTE + "/captures/" + uuid.uuid4().hex + ".json"
        if candidate:
            code = ("import sys,json,os,pathlib;pathlib.Path(" + repr(remote_capture) + ").parent.mkdir(exist_ok=True);"
                    "os.environ['TANGERINE_DIAGNOSTIC_CAPTURE']=" + repr(remote_capture) + ";sys.path.insert(0," + repr(REMOTE) + ");"
                    "from backends import execute_packet;p=json.load(sys.stdin);"
                    "result,code=execute_packet(p);print(json.dumps(result));sys.exit(code)")
        else:
            code = """import os,json,sys,urllib.request,urllib.error
p=json.load(sys.stdin);route=p.get('action','piece')
r=urllib.request.Request('http://127.0.0.1:8090/internal/v1/'+route,data=json.dumps(p).encode(),headers={'Authorization':'Bearer '+os.environ['SPEECH_INTERNAL_TOKEN'],'Content-Type':'application/json'})
try:
 with urllib.request.urlopen(r,timeout=270) as v:print(v.read().decode())
except urllib.error.HTTPError as e:print(e.read().decode())
"""
        result = subprocess.run(["docker", "exec", "-i", "tangerine-local-speech-1", "python", "-B", "-c", code],
                                input=json.dumps(packet).encode(), capture_output=True, timeout=280, env=ENV)
        (directory / "stderr.log").write_bytes(result.stderr)
        try:
            value = json.loads(result.stdout)
        except ValueError:
            (directory / "stdout.log").write_bytes(result.stdout)
            value = {"error": "NATIVE_PROCESS_FAILED", "exit_code": result.returncode}
        if candidate and not value.get("wire"):
            copied = subprocess.run(["docker", "cp", "tangerine-local-speech-1:" + remote_capture, str(directory / "native-capture.json")], env=ENV, capture_output=True)
            if copied.returncode == 0:
                value["model_visible_context"] = json.loads((directory / "native-capture.json").read_text())
        return value
    return saved_observation(response, perform)


def recordings(fixture):
    directory = OUT / "recordings" / fixture["taxonomy_id"]
    index = directory / "index.json"
    if index.exists():
        return json.loads(index.read_text())
    if fixture["render_kind"] != "text":
        if fixture["render_kind"] == "acoustic":
            from generate_acoustic import generate_case
            return generate_case(fixture["taxonomy_id"], directory, worker, ROOT)
        return None
    paths = {}
    for role, text in (("clean", fixture["clean_text"]), ("mutated", fixture["mutated_text"]),
                       ("acceptable", fixture["control_text"])):
        turn = dict(id="category-probe", utterance_id="category-probe", speaker_id="s1",
                    voice_id="af_heart", locale="en-US", operations=[dict(kind="text", text=text)], gap_after_ms=0)
        value = worker(dict(profile=PROFILE, turn=turn), directory / role)
        if value.get("error"):
            print(json.dumps(dict(category=fixture["taxonomy_id"], role=role, error=value["error"])), flush=True)
            return None
        raw = base64.b64decode(value["audio_base64"])
        path = directory / (role + ".wav"); path.write_bytes(raw)
        with wave.open(io.BytesIO(raw), "rb") as stream:
            if stream.getnframes() > 240000:
                save(directory / "capacity.json", {"role": role, "duration_seconds": stream.getnframes() / 24000,
                                                   "status": "exceeds_selected_10_second_clip_profile"})
                return None
        paths[role] = os.path.relpath(path, ROOT)
    paths["misleading_metadata"] = paths["clean"]
    result = dict(paths=paths, binding=dict(backend="local_kokoro", model="Kokoro-82M", voice="af_heart", locale="en-US"))
    save(index, result)
    return result


def listen(fixture, record, profile, variant="configured"):
    directory = OUT / ("observations-" + variant) / fixture["taxonomy_id"]
    result_path = directory / "comparison.json"
    if result_path.exists():
        return json.loads(result_path.read_text())
    fixture = {**fixture, **record.get("fixture_override", {})}
    probe = make_probe(fixture, record["paths"], {**record["binding"], "judge": profile}, fixture["taxonomy_id"])
    save(directory / "withheld.json", probe)
    prompt = (ROOT / "specification/v2/prompts/audio-category-probe-v1.txt").read_text()
    audios = [base64.b64encode((ROOT / b["audio_path"]).read_bytes()).decode() for b in probe["withheld"]]
    packet = dict(action="measure", method_id="gemini-audio-v1", profile=profile, prompt=prompt,
                  input=blind_input(probe), audio_base64=audios[0], additional_audio_base64=audios[1:])
    observation = worker(packet, directory, candidate=True)
    if record.get("physical"): observation["physical"] = record["physical"]
    # A native returned receipt is required. Failed dispatches remain failures,
    # with their full wire; no synthetic successful receipt is manufactured.
    result = compare_probe(probe, observation)
    result["error"] = observation.get("error")
    save(result_path, result)
    return result


def report(fixtures, variant="configured"):
    prior = ROOT / "audit/linguistic-fullness-20261023/CASES.json"
    native = json.loads(prior.read_text())["cases"]
    semantics = json.loads((ROOT / "audit/linguistic-fullness-20261023/MODEL-CASES.json").read_text())["cases"]
    implementations = {}
    for fixture in fixtures:
        category = fixture["taxonomy_id"]
        ids = [r["id"] for r in native if r["id"].endswith("." + category)]
        implementations[category] = {"status": "retained_valid" if ids else "not_run", "case_ids": ids,
                                    "receipt_index": "audit/linguistic-fullness-20261023/RECONCILIATION.json",
                                    "proof": "native_selection_context_recipe_scoring_not_heard_audio"}
        implementations[category]["semantic_case_ids"] = [r["id"] for r in semantics if r["category"] == category]
        if category == "discourse.turn_taking":
            implementations[category]["audio_rendering_gap"] = "No simultaneous/masking controller in the current sequential turn renderer; text captions do not implement overlap."
    observed = {}
    for p in (OUT / ("observations-" + variant)).glob("*/comparison.json"):
        value = json.loads(p.read_text()); observed[value["category_id"]] = value
    result = coverage(fixtures, observed, implementations)
    result["recording_categories"] = len(list((OUT / "recordings").glob("*/index.json")))
    result["attempted_categories"] = len(observed)
    save(OUT / "coverage.json", result)
    report_target = HERE if OUT == DEFAULT_OUT else OUT
    save(report_target / "COVERAGE.json", result)
    text = ["# Category implementation and audio evidence", "",
            "Constructed finite references. Existing implementation/grading receipts are retained; "
            "auditory agreement is not perceptual gold. A missing row is never a pass.", "",
            "| Category | Implementation | Audio | Controls |", "| --- | --- | --- | --- |"]
    for row in result["categories"]:
        sound = row["audio"]
        text.append("| " + " | ".join([row["category_id"], row["implementation"]["status"], sound["audio_confirmation"],
                                       str(sound.get("controls_passed", "not_run"))]) + " |")
    (report_target / "COVERAGE.md").write_text("\n".join(text) + "\n")
    print(json.dumps({"categories": result["category_count"], "confirmed": result["confirmed"],
                      "unconfirmed": len(result["unconfirmed"])}), flush=True)


def readmit(variant):
    """Repair admission of retained real output, making zero new model calls."""
    from diagnostic_models import decode_findings
    for path in (OUT / ("observations-" + variant)).glob("*/response.json"):
        value = json.loads(path.read_text())
        wire = value.get("wire", {})
        if value.get("error") != "DIAGNOSTIC_OUTPUT_INVALID" or wire.get("http_status") != 200: continue
        visible = "".join(c.get("text", "") for s in wire["response"].get("steps", []) if s.get("type") == "model_output"
                          for c in s.get("content", []) if c.get("type") == "text")
        try: output = decode_findings(visible)
        except ValueError: continue
        admitted = {**value, "output": output, "error": None,
                    "receipt": dict(model=wire["profile"]["model"], inference_calls=1,
                                    started_at_unix=value["started_at_unix"], finished_at_unix=value["finished_at_unix"]),
                    "readmission": "retained original wire; zero new inference"}
        record = saved_observation(OUT / "recordings" / path.parent.name / "index.json")
        if record and record.get("physical"): admitted["physical"] = record["physical"]
        save(path.with_name("readmitted-response.json"), admitted)
        probe = json.loads(path.with_name("withheld.json").read_text())
        prior = path.with_name("comparison.json")
        original = path.with_name("original-comparison.json")
        if prior.exists() and not original.exists(): original.write_bytes(prior.read_bytes())
        result = compare_probe(probe, admitted); result["error"] = None
        save(prior, result)


def reconcile(variant):
    """Recompute changed comparison logic/physical evidence, with no redispatch."""
    for directory in (OUT / ("observations-" + variant)).iterdir():
        if not directory.is_dir() or not (directory / "withheld.json").exists(): continue
        response = directory / "readmitted-response.json"
        if not response.exists(): response = directory / "response.json"
        if not response.exists(): continue
        observation = json.loads(response.read_text())
        record = saved_observation(OUT / "recordings" / directory.name / "index.json")
        if record and record.get("physical"): observation["physical"] = record["physical"]
        probe = json.loads((directory / "withheld.json").read_text())
        original = directory / "comparison-before-reconciliation.json"
        current = directory / "comparison.json"
        if current.exists() and not original.exists(): original.write_bytes(current.read_bytes())
        result = compare_probe(probe, observation); result["error"] = observation.get("error")
        save(current, result)


def main():
    global OUT
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["render", "listen", "report", "prepare-candidate", "readmit", "reconcile"])
    ap.add_argument("--categories", help="Comma-separated exact category IDs; omission selects the finite inventory")
    ap.add_argument("--variant", default="configured", help="Named explicit judge binding, never a runtime fallback")
    ap.add_argument("--judge-model", help="Explicit existing free-project experiment model; does not change Settings")
    ap.add_argument("--continue-503", action="store_true", help="Attempt other finite cases after a 503; never retry a failed case")
    ap.add_argument("--output", type=Path, help="Separate experiment directory for a changed fixture population")
    args = ap.parse_args()
    if args.output: OUT = args.output.resolve()
    frozen = OUT / "frozen-fixtures.json"
    if not frozen.exists(): save(frozen, json.loads((HERE / "FIXTURES.json").read_text()))
    fixtures = json.loads(frozen.read_text())["fixtures"]
    selected = set(args.categories.split(",")) if args.categories else {r["taxonomy_id"] for r in fixtures}
    if args.action == "report": report(fixtures, args.variant); return
    if args.action == "readmit": readmit(args.variant); report(fixtures, args.variant); return
    if args.action == "reconcile": reconcile(args.variant); report(fixtures, args.variant); return
    if args.action == "prepare-candidate":
        docker("exec", "tangerine-local-speech-1", "mkdir", "-p", REMOTE)
        docker("cp", str(ROOT / "services/speech") + "/.", "tangerine-local-speech-1:" + REMOTE)
        save(OUT / "candidate-binding.json", {"source": str(ROOT), "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
             "purpose": "candidate native diagnostic only; ordinary server and settings unchanged"})
        return
    profile = None
    if args.action == "listen":
        with urllib.request.urlopen("http://localhost:3000/api/v1/configuration", timeout=10) as stream:
            config = json.load(stream)["configuration"]
        profile = config["audio_diagnostic_profile"]
        if profile.get("provider") != "gemini_interactions" or profile.get("billing_mode") != "free_tier":
            raise SystemExit("Only the existing verified unbilled Gemini profile is selected; no fallback")
        profile = {**profile, "max_output_tokens": 2500,
                   "prompt_sha256": hashlib.sha256((ROOT / "specification/v2/prompts/audio-category-probe-v1.txt").read_bytes()).hexdigest(),
                   "prompt_asset_id": "development:audio-category-probe-v1"}
        if args.judge_model:
            if args.variant == "configured": raise SystemExit("A changed judge needs a separately named --variant")
            profile["model"] = args.judge_model
        binding_path = OUT / ("observations-" + args.variant) / "binding.json"
        if binding_path.exists() and json.loads(binding_path.read_text()) != profile:
            raise SystemExit("This saved experiment has a different binding; choose a new variant")
        save(binding_path, profile)
    for fixture in fixtures:
        if fixture["taxonomy_id"] not in selected: continue
        record = recordings(fixture) if args.action == "render" else saved_observation(OUT / "recordings" / fixture["taxonomy_id"] / "index.json")
        if not record: continue
        if args.action == "listen":
            value = listen(fixture, record, profile, args.variant)
            print(json.dumps(dict(category=fixture["taxonomy_id"], status=value["audio_confirmation"], error=value.get("error"))), flush=True)
            if value.get("error"):
                response_path = OUT / ("observations-" + args.variant) / fixture["taxonomy_id"] / "response.json"
                failed = json.loads(response_path.read_text())
                if args.continue_503 and failed.get("wire", {}).get("http_status") == 503:
                    continue
                report(fixtures, args.variant)
                raise SystemExit("Free auditory provider failed; retained failure, no retry or paid fallback")
        else:
            print(json.dumps(dict(category=fixture["taxonomy_id"], rendered=True)), flush=True)
    report(fixtures, args.variant)


if __name__ == "__main__":
    main()
