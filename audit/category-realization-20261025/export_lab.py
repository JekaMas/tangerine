"""Copy/read back this finite local experiment. Makes zero inference calls."""
import json
import argparse
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / "data/category-realization-20261025"
ENV = {**os.environ, "DOCKER_HOST": "unix:///Users/jekamas/Library/Containers/com.docker.docker/Data/docker.raw.sock",
       "DOCKER_CONFIG": str(ROOT / "data/local-preview/docker-config")}


def docker(*args):
    result = subprocess.run(["docker", *args], env=ENV, capture_output=True, timeout=240)
    if result.returncode:
        (OUT / "lab-failure.log").write_bytes(result.stdout + result.stderr)
        raise SystemExit("Local Lab export/readback failed; native evidence is retained")
    return result.stdout


def main():
    global OUT
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.output: OUT = args.output.resolve()
    receipt = OUT / "mlflow-readback.json"
    if receipt.exists(): print(receipt.read_text()); return
    stage = OUT / "lab-export"; stage.mkdir(exist_ok=True)
    for path in OUT.iterdir():
        if path == stage or path.name.startswith("mlflow"): continue
        if path.is_dir(): shutil.copytree(path, stage / path.name, dirs_exist_ok=True)
        elif path.is_file(): shutil.copyfile(path, stage / path.name)
    shutil.copytree(HERE, stage / "audit", dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
    sources = stage / "sources"; sources.mkdir(exist_ok=True)
    for name in ["category_validation.py", "diagnostic_runtime.py", "diagnostic_models.py"]:
        shutil.copyfile(ROOT / "services/speech" / name, sources / name)
    for name in ["test_category_validation.py", "test_category_evidence.py"]:
        shutil.copyfile(ROOT / "tests" / name, sources / name)
    shutil.copyfile(ROOT / "specification/v2/prompts/audio-category-probe-v1.txt", sources / "audio-category-probe-v1.txt")
    remote = "/tmp/tangerine-category-realization-20261025"
    docker("exec", "tangerine-local-llm-lab-1", "mkdir", "-p", remote)
    docker("cp", str(stage) + "/.", "tangerine-local-llm-lab-1:" + remote)
    code = '''import json,pathlib,mlflow
from mlflow import MlflowClient
root=pathlib.Path('/tmp/tangerine-category-realization-20261025');mlflow.set_tracking_uri('http://127.0.0.1:5000');c=MlflowClient();name='Tangerine category realization 20261025';e=c.get_experiment_by_name(name);eid=e.experiment_id if e else c.create_experiment(name)
r=c.create_run(eid,tags={'tangerine.scope':'122-category implementation versus blind actual-audio evidence','tangerine.billing':'existing local and verified unbilled free project only','tangerine.reference_origin':'authored; model opinion is not perceptual gold','tangerine.ordinary_settings_changed':'false'})
c.log_artifacts(r.info.run_id,str(root),artifact_path='experiment')
dest='/tmp/tangerine-category-realization-readback';p=c.download_artifacts(r.info.run_id,'experiment/coverage.json',dest);v=json.loads(pathlib.Path(p).read_text());assert v['category_count']==122 and len(v['categories'])==122
p=c.download_artifacts(r.info.run_id,'experiment/observations-gemini31/grammar.determiners.article_omission/readmitted-response.json',dest);a=json.loads(pathlib.Path(p).read_text());assert a['wire']['http_status']==200 and a['wire']['profile']['billing_mode']=='free_tier'
p=c.download_artifacts(r.info.run_id,'experiment/recordings/grammar.determiners.article_omission/mutated.wav',dest);assert pathlib.Path(p).stat().st_size>4800
p=c.download_artifacts(r.info.run_id,'experiment/observations-configured/grammar.determiners.article_omission/response.json',dest);assert json.loads(pathlib.Path(p).read_text())['wire']['http_status']==503
c.log_param(r.info.run_id,'taxonomy_categories',122);c.log_metric(r.info.run_id,'finite_confirmed',v['confirmed']);c.log_metric(r.info.run_id,'finite_unconfirmed',len(v['unconfirmed']))
c.set_terminated(r.info.run_id);print(json.dumps(dict(experiment_id=eid,run_id=r.info.run_id,coverage_categories=122,confirmed=v['confirmed'],unconfirmed=len(v['unconfirmed']),readback='category matrix, actual model wire, failed HTTP503 and actual WAV',export_inference_calls=0)))
'''
    raw = docker("exec", "tangerine-local-llm-lab-1", "python", "-c", code)
    (OUT / "mlflow-export.log").write_bytes(raw)
    result = json.loads(next(line for line in reversed(raw.decode().splitlines()) if line.startswith("{")))
    receipt.write_text(json.dumps(result, indent=2) + "\n")
    (HERE / "MLFLOW.json").write_text(receipt.read_text())
    print(json.dumps(result))


if __name__ == "__main__": main()
