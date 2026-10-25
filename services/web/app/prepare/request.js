import {userError,parseUserJSON} from '../requestError.js';
import {recurringRequests} from './recurringRequest.js';

export const mistakeFamilies = [
  ['grammar', 'Grammar'], ['lexis', 'Vocabulary'],
  ['pronunciation', 'Pronunciation (all)'],
  ['pronunciation.segmental', 'Pronunciation: individual sounds'],
  ['pronunciation.suprasegmental', 'Pronunciation: stress and intonation'],
  ['fluency', 'Fluency'], ['discourse', 'Discourse and coherence'],
  ['pragmatics_register', 'Style and register'],
];

export const severityOptions = [
  ['minor','Minor','A small slip; the meaning stays clear.'],
  ['moderate','Moderate','Noticeable, but the listener can recover the meaning.'],
  ['major','Major','Changes or seriously obscures the intended meaning.'],
  ['communication_breakdown','Communication breakdown','Prevents the intended message from getting through.'],
];

export function categoryFloor(form) {
  if (form.categories?.length) return new Set(form.categories).size;
  const families=new Set(form.families || []);
  const sounds=families.has('pronunciation.segmental'), stress=families.has('pronunciation.suprasegmental');
  return [...families].filter(x=>!x.startsWith('pronunciation')).length + Number(sounds)+Number(stress)+Number(families.has('pronunciation')&&!sounds&&!stress);
}

export function mistakeCount(form) {
  const mode=form.amount || (form.mutationCount===''?'auto':'exact');
  if (['low','medium','high'].includes(mode)) {
    const rate={low:1,medium:2,high:4}[mode];
    return Math.max(1,categoryFloor(form),recurringRequests(form).length,Math.round(Number(form.words)*rate/100));
  }
  if (mode==='auto') return null;
  const count=Number(form.mutationCount);
  if (form.mutationCount==='' || !Number.isSafeInteger(count) || count<0) throw userError('Enter a whole number of mistakes, zero or greater. Your other choices are retained.');
  return count;
}

export function blueprintRequest(form) {
  const advanced = form.advanced.trim() ? parseUserJSON(form.advanced,'Advanced blueprint') : {};
  if (!advanced || Array.isArray(advanced) || typeof advanced !== 'object') {
    throw userError('Advanced blueprint must be a JSON object. Your form values are retained.');
  }
  const count=mistakeCount(form);
  const recurring=recurringRequests(form);
  const request={
    topic: form.topic, speaker_count: Number(form.speakers), text_length_words: Number(form.words),
    english_level: form.level || null, category_families: form.families || [],
    mutation_count: count,
    ...(!advanced.speakers && form.voices?.slice(0,Number(form.speakers)).some(Boolean) ? {speaker_voice_ids:Array.from({length:Number(form.speakers)},(_,i)=>form.voices[i]||null)} : {}),
    ...(form.categories?.length ? {category_ids:form.categories} : {}),
    ...(form.severities?.length ? {severity_levels:form.severities} : {}),
    ...(recurring.length ? {recurring_errors:recurring} : {}),
    ...advanced.exercise_request,
  };
  const floor=Math.max(categoryFloor({categories:Array.isArray(request.category_ids)?request.category_ids:[],families:Array.isArray(request.category_families)?request.category_families:[]}),Array.isArray(request.recurring_errors)?request.recurring_errors.length:0);
  if (Number.isInteger(request.mutation_count) && request.mutation_count>0 && request.mutation_count<floor) throw userError(`Choose at least ${floor} mistakes to cover your selected categories and recurring speaker patterns, or zero for a control exercise. Your choices are retained.`);
  return {...advanced, exercise_request:request};
}
