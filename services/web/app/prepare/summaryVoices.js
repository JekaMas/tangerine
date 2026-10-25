// Presentation follows the same explicit speaker precedence as the blueprint.
// Configured defaults are named honestly; this view does not resolve providers.
export function summaryVoices(blueprint, voices=[]) {
  const selected=Array.isArray(blueprint.speakers)
    ? blueprint.speakers.map(s=>({id:s.voice_profile_id,accent:s.requested_accent}))
    : (Array.isArray(blueprint.exercise_request.speaker_voice_ids)
      ? blueprint.exercise_request.speaker_voice_ids.map(id=>({id})) : []);
  return selected.map(({id,accent},i)=>{
    const voice=voices.find(v=>v.id===id);
    const label=voice?`${voice.accent_label} · ${voice.label}`:id||'Configured default';
    return `Speaker ${i+1}: ${label}${accent?` · Requested accent: ${accent}`:''}`;
  });
}
