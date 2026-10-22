export const mistakeFamilies = [
  ['grammar', 'Grammar'], ['lexis', 'Vocabulary'],
  ['pronunciation', 'Pronunciation (all)'],
  ['pronunciation.segmental', 'Pronunciation: individual sounds'],
  ['pronunciation.suprasegmental', 'Pronunciation: stress and intonation'],
  ['fluency', 'Fluency'], ['discourse', 'Discourse and coherence'],
  ['pragmatics_register', 'Pragmatics and register'],
];

export function blueprintRequest(form) {
  const advanced = form.advanced.trim() ? JSON.parse(form.advanced) : {};
  if (!advanced || Array.isArray(advanced) || typeof advanced !== 'object') {
    throw Error('Advanced blueprint must be a JSON object. Your form values are retained.');
  }
  return {...advanced, exercise_request: {
    topic: form.topic, speaker_count: Number(form.speakers), text_length_words: Number(form.words),
    english_level: form.level || null, category_families: form.families,
    mutation_count: form.mutationCount === '' ? null : Number(form.mutationCount),
    ...advanced.exercise_request,
  }};
}
