"""Actual sequential interruption fixture; simultaneous masking stays unqualified.

This is another legitimate member of the same category, not evidence that the
original symbolic masked-overlap example is implemented by the renderer.
"""
import base64
import io
import json
import wave
from run import ROOT, OUT, PROFILE, worker, save

TURNS = {
    "clean": [("a", "Let me finish. Do not touch the wire."), ("b", "Okay.")],
    "mutated": [("a", "Let me finish. Do not..."), ("b", "I want to speak now."), ("a", "Wait, I haven't finished.")],
    "acceptable": [("a", "Can you finish this for me?"), ("b", "Do not touch the wire."), ("a", "Exactly.")],
}


def main():
    directory = OUT / "recordings/discourse.turn_taking"
    if (directory / "index.json").exists(): return
    voices = {"a": "af_heart", "b": "am_adam"}
    profile = {**PROFILE, "voices": [dict(id=v, locale="en-US") for v in voices.values()]}
    paths = {}
    for role, turns in TURNS.items():
        pcm = bytearray(); timings = []
        for i, (speaker, text) in enumerate(turns):
            turn = dict(id="turn-" + str(i), utterance_id="turn-" + str(i), speaker_id=speaker,
                        voice_id=voices[speaker], locale="en-US", operations=[dict(kind="text", text=text)], gap_after_ms=0)
            result = worker(dict(profile=profile, turn=turn), directory / role / ("turn-" + str(i)))
            if result.get("error"): raise SystemExit(result["error"])
            raw = base64.b64decode(result["audio_base64"])
            with wave.open(io.BytesIO(raw)) as w:
                start = len(pcm) // 2; pcm.extend(w.readframes(w.getnframes())); end = len(pcm) // 2
            timings.append(dict(speaker=speaker, voice=voices[speaker], start=start, end=end))
            pcm.extend(b"\0\0" * 2400)
        path = directory / (role + ".wav")
        with wave.open(str(path), "wb") as w:
            w.setparams((1, 2, 24000, 0, "NONE", "not compressed")); w.writeframes(pcm)
        paths[role] = str(path.relative_to(ROOT)); save(directory / (role + "-timing.json"), timings)
    paths["misleading_metadata"] = paths["clean"]
    context = "Speaker A asks to finish a safety instruction. Speaker B must wait until A finishes before taking the floor. An explicit invitation to finish the sentence permits a cooperative handoff."
    question = "Does B take the floor before A has finished, contrary to the request? Assess the actual audible cutoff/response; do not assume simultaneous overlap."
    save(directory / "index.json", dict(paths=paths, binding=dict(backend="local_kokoro", model="Kokoro-82M", voice=voices, locale="en-US"),
         fixture_override=dict(context=context, question=question, control_context=context, control_question=question),
         assembly="Authored finite scene from actual native TTS turns, sequential PCM with100ms gaps; no overlap synthesis.",
         unimplemented_variant="The earlier complete-masking overlap fixture is not rendered or qualified. This actual cutoff fixture does not close that gap."))
    print("discourse.turn_taking: actual cutoff/allowed handoff recordings retained; overlap remains unavailable")


if __name__ == "__main__": main()
