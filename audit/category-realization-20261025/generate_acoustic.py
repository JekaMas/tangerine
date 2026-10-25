"""Regenerate owned acoustic fixtures through native owners, without old data/."""
import base64
import io
import json
import os
from pathlib import Path
import wave

HERE = Path(__file__).resolve().parent


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(path)


def clip(raw, scope, path):
    with wave.open(io.BytesIO(raw)) as audio:
        a, b = max(0, scope["start"] - 24000), min(audio.getnframes(), scope["end"] + 24000)
        if b - a > 240000: return None
        audio.setpos(a); pcm = audio.readframes(b - a)
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as audio:
        audio.setparams((1, 2, 24000, 0, "NONE", "not compressed")); audio.writeframes(pcm)
    return dict(source_start=a, source_end=b, sample_rate_hz=24000,
                target_scope_basis="actual_native_decoder_scope_proposal_not_independent_perception")


def generate_case(category, directory, dispatch, root):
    plan = next((r for r in json.loads((HERE / "RENDER-PLANS.json").read_text())["cases"] if r["taxonomy_id"] == category), None)
    if plan is None: return None
    directory = Path(directory); index = directory / "index.json"
    if index.exists(): return json.loads(index.read_text())
    planned = dispatch(dict(action="plan", profile=plan["profile"], plan=dict(turns=[plan["turn"]])), directory / "plan")
    if planned.get("error"):
        save(directory / "unavailable.json", planned); return None
    if len(planned["pieces"]) != 1:
        save(directory / "unavailable.json", dict(error="ONE_COMPLETE_CARRIER_REQUIRED", pieces=len(planned["pieces"]))); return None
    piece = planned["pieces"][0]
    source = dispatch(dict(profile=plan["profile"], turn=piece), directory / "source")
    if source.get("error"):
        save(directory / "unavailable.json", source); return None
    original = source["receipt"]["native"]
    resolved = dispatch(dict(action="resolve", audio_base64=source["audio_base64"], native=original, turn=piece, piece_id="carrier"), directory / "resolve")
    if resolved.get("error"):
        save(directory / "unavailable.json", resolved); return None
    value = dict(audio_base64=source["audio_base64"], native=original)
    for i, step in enumerate(resolved["steps"]):
        value = dispatch(dict(action="transform", audio_base64=value["audio_base64"], native=value["native"], step=step), directory / ("transform-" + str(i)))
        if value.get("error"):
            save(directory / "unavailable.json", value); return None
    paths, derivatives = {}, {}
    for role, encoded, native in (("clean", source["audio_base64"], original), ("mutated", value["audio_base64"], value["native"])):
        scope = next((r for r in native.get("acoustic_scopes", []) if r["unit_id"] == "target"), None)
        if scope is None:
            save(directory / "unavailable.json", dict(error="NO_ACTUAL_TARGET_SCOPE")); return None
        path = directory / (role + ".wav")
        derivative = clip(base64.b64decode(encoded), scope, path)
        if derivative is None:
            save(directory / "unavailable.json", dict(error="TARGET_EXCEEDS_SELECTED_CLIP_PROFILE")); return None
        paths[role], derivatives[role] = os.path.relpath(path, root), derivative
    paths.update(acceptable=paths["clean"], misleading_metadata=paths["clean"])
    result = dict(paths=paths, derivatives=derivatives, fixture_override=plan["fixture_override"],
                  binding=dict(backend="local_kokoro_controlled", model="Kokoro-82M", voice=plan["turn"]["voice_id"], locale=plan["turn"]["locale"]),
                  origin="fresh_native_generation_from_committed_authored_plan",
                  limitation="Newly generated sound needs its own explicit auditory/physical qualification; no old judgment is copied.")
    save(index, result)
    return result
