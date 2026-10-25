"""Short concrete local contrasts through the existing plan/render/transform owners."""
import base64
import copy
import hashlib
import io
import json
import wave
from run import ROOT, OUT, PROFILE, worker, save, saved_observation


CASES = [
    dict(category="pronunciation.suprasegmental.pitch_range", text="We will meet at the station tomorrow.", scope="We will meet at the station tomorrow.",
         controller="pitch_duration", parameters={},
         context="A controlled comparison asks for the ordinary same-speaker pitch range rather than a doubled exaggerated range. This is a local practice target, not an accent-wide norm.",
         question="Is the pitch range audibly exaggerated beyond the ordinary range in this explicit comparison?"),
    dict(category="fluency.speech_rate", text="Please bring the parcel to the front desk.", scope="Please bring the parcel to the front desk.",
         controller="pitch_duration", parameters=dict(duration_ratio=.5),
         context="A matched-pace drill asks for the ordinary same-speaker pace rather than approximately double that pace. Fast clear speech remains permitted outside this drill.",
         question="Does this recording depart from the ordinary matched pace by speaking approximately twice as fast?"),
    dict(category="fluency.excessive_pausing", text="Please bring the package to the front desk.", scope="package",
         controller="pause_insert", parameters=dict(pause_ms=4000, phone_start=1),
         context="This controlled phrase permits at most 1.5 seconds of internal silence. A four-second unplanned pause violates that target.",
         question="Does this phrase contain an internal silence longer than 1.5 seconds?"),
    dict(category="fluency.pause_location", text="The teacher will meet us tomorrow.", scope="teacher",
         controller="pause_insert", parameters=dict(pause_ms=2000, phone_start=2),
         context="The lexical word teacher must remain uninterrupted; pauses between words or phrases are permitted.",
         question="Is the word teacher split by an intrusive internal silence?"),
    dict(category="acceptable_variant.pronunciation_variant", text="Either option is fine.", scope="Either",
         controller="phone_pair", parameters=dict(reference_ipa="ˈiðɚ", mutated_ipa="ˈaɪðɚ"),
         context="Both the eether and eye-ther pronunciations of either are permitted. There is no preference or narrow drill target.",
         question="Does the pronunciation of either contain an actual error under this policy allowing both standard variants?"),
]


def duration(raw):
    with wave.open(io.BytesIO(raw)) as w: return w.getnframes()


def main():
    for row in CASES:
        directory = OUT / "recordings" / row["category"]
        if (directory / "index.json").exists(): continue
        start = row["text"].index(row["scope"])
        edit = dict(unit_id="target", taxonomy_id=row["category"], utterance_id="short-probe",
                    scope=dict(start=start, end=start + len(row["scope"])), controller=row["controller"], parameters=row["parameters"])
        turn = dict(id="short-probe", utterance_id="short-probe", speaker_id="s1", voice_id="af_heart", locale="en-US",
                    operations=[dict(kind="text", text=row["text"])], acoustic_edits=[edit], gap_after_ms=0)
        profile = {**PROFILE, "id": "kokoro-controlled-v1", "adapter_version": "kokoro-controlled-v1"}
        plan = worker(dict(action="plan", profile=profile, plan=dict(turns=[turn])), directory / "plan")
        if plan.get("error"):
            print(row["category"], plan["error"], flush=True); continue
        piece = plan["pieces"][0]
        source = worker(dict(profile=profile, turn=piece), directory / "source")
        if source.get("error"):
            print(row["category"], source["error"], flush=True); continue
        resolved = worker(dict(action="resolve", audio_base64=source["audio_base64"], native=source["receipt"]["native"], turn=piece, piece_id="short-probe"), directory / "resolve")
        if resolved.get("error"):
            print(row["category"], resolved["error"], flush=True); continue
        audio, native = source["audio_base64"], source["receipt"]["native"]
        for i, step in enumerate(resolved["steps"]):
            changed = worker(dict(action="transform", audio_base64=audio, native=native, step=step), directory / ("transform-" + str(i)))
            if changed.get("error"): break
            audio, native = changed["audio_base64"], changed["native"]
        if changed.get("error"):
            print(row["category"], changed["error"], flush=True); continue
        clean, mutated = base64.b64decode(source["audio_base64"]), base64.b64decode(audio)
        (directory / "clean.wav").write_bytes(clean); (directory / "mutated.wav").write_bytes(mutated)
        paths = {"clean": str((directory / "clean.wav").relative_to(ROOT)), "mutated": str((directory / "mutated.wav").relative_to(ROOT))}
        paths.update(acceptable=paths["clean"], misleading_metadata=paths["clean"])
        # Actual file durations are independent of the controller's reported
        # requested values. Pitch shape is separately measured below, not inferred.
        physical = None
        if row["controller"] == "pause_insert":
            added = duration(mutated) - duration(clean)
            physical = dict(status="supported" if added == row["parameters"]["pause_ms"] * 24 else "uncertain",
                            observations=[dict(observed_added_samples=added, expected_added_samples=row["parameters"]["pause_ms"] * 24)],
                            basis="actual_final_and_source_WAV_sample_counts")
        elif row["category"] == "fluency.speech_rate":
            ratio = duration(mutated) / duration(clean)
            physical = dict(status="supported" if .4 < ratio < .7 else "uncertain", observations=[dict(observed_file_duration_ratio=ratio)],
                            basis="actual_final_and_source_WAV_sample_counts_in_this_matched_text_task")
        override = dict(context=row["context"], question=row["question"], control_context=row["context"], control_question=row["question"])
        if row["category"] == "fluency.speech_rate":
            override.update(control_context="Clear ordinary English, with no rate constraint. A clear fast or moderate speaker is allowed.", control_question="Is this speech defective merely because of its speaking pace in this unrestricted context?")
        save(directory / "index.json", dict(paths=paths, binding=dict(backend="local_kokoro_controlled", model="Kokoro-82M", voice="af_heart", locale="en-US"),
             fixture_override=override, physical=physical, native_evidence="source/resolve/transform packets in this directory"))
        print(row["category"], "rendered", flush=True)
    measure_pitch_range()


def measure_pitch_range():
    directory = OUT / "recordings/pronunciation.suprasegmental.pitch_range"
    record = saved_observation(directory / "index.json")
    if not record: return
    ranges = {}
    for role in ("clean", "mutated"):
        measured = saved_observation(directory / ("measured-" + role) / "response.json")
        if measured is None:
            raw = (ROOT / record["paths"][role]).read_bytes()
            measured = worker(dict(action="measure", method_id="praat-ac-v1", audio_base64=base64.b64encode(raw).decode(),
                                  audio_sha256=hashlib.sha256(raw).hexdigest()), directory / ("measured-" + role))
        ranges[role] = next((r["numeric_value"] for r in measured.get("measurements", []) if r["feature"] == "f0_range_semitones"), None)
    if all(value is not None for value in ranges.values()) and float(ranges["clean"]) > 0:
        ratio = float(ranges["mutated"]) / float(ranges["clean"])
        record["physical"] = dict(status="supported" if 1.6 < ratio < 2.5 else "uncertain",
                                  observations=[dict(actual_f0_range_semitones=ranges, ratio=ratio)],
                                  basis="native_Praat_on_actual_final_WAVs_not_requested_contour")
        save(directory / "index.json", record)


if __name__ == "__main__": main()
