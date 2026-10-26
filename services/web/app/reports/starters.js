import {userError} from '../requestError.js';
// Constructed starters are development examples, never empirical observations.
const ordered = value => Array.isArray(value) ? value.map(ordered) : value && typeof value==='object'
  ? Object.fromEntries(Object.keys(value).sort().map(key=>[key,ordered(value[key])])) : value;
const canonical = value => JSON.stringify(ordered(value));
async function digest(value) {
  const bytes = await crypto.subtle.digest('SHA-256',new TextEncoder().encode(canonical(value)));
  return Array.from(new Uint8Array(bytes),x=>x.toString(16).padStart(2,'0')).join('');
}

export function reportStarter(title, category) {
  if (!title.trim() || !category) throw userError('Give the report a title and choose a category.');
  return {title:title.trim(), input:{population:{release:'constructed-starter-v1',view:'two-authored-sentences',split:'development',annotator:'authored-reference',window:'sentence',modality:'text',taxonomy_version:'v1',crosswalk_version:'identity',label_origin:'constructed',l1:null,cefr:null,task:null},annotated_leaf_ids:[category],leaves:[category],windows:[
    {id:category==='lexis.collocation'?'We did a decision.':'The café open tomorrow.',fully_annotated:true,native_tokens:4,events:[{id:'authored-error',native_label:category,leaf_id:category,secondary_ids:[],control:false,excluded_reason:''}],opportunities:{[category]:1}},
    {id:category==='lexis.collocation'?'We made a decision.':'The café opens tomorrow.',fully_annotated:true,native_tokens:4,events:[],opportunities:{[category]:1}},
  ],decisions:[]},attempts:[]};
}

export function reportFromPopulation(title, submission) {
  if (!title.trim()) throw userError('Give the report a title.');
  return {...structuredClone(submission),title:title.trim()};
}

export async function experimentStarter(defaults,{topic,level,words,profile,dataset:savedDataset}) {
  if (!savedDataset && (!topic.trim() || !Number.isSafeInteger(Number(words)) || Number(words)<1)) throw userError('Enter a topic and a positive whole word count.');
  if (!defaults?.configuration?.llm_profiles.some(p=>p.id===profile&&p.roles.includes('case_generation'))) throw userError('Choose a configured LLM profile with the generation role.');
  if (savedDataset && (savedDataset.scope!=='generation_pipeline' || savedDataset.judge_policy_asset_id)) throw userError('Use the advanced experiment definition for this dataset.');
  const config=structuredClone(defaults.configuration);
  config.llm_profile=profile;
  config.stage_profiles={...config.stage_profiles,case_generation:profile};
  delete config.configuration_sha256;
  config.configuration_sha256=await digest(config);
  if (savedDataset) return ordered({experiment:{scope:'generation_pipeline',dataset_asset_id:savedDataset.dataset_asset_id,dataset_sha256:savedDataset.dataset_sha256,scorer_version:'quality-v1',variants:[{id:'configured-baseline',bundle_id:'bundle',bundle_sha256:defaults.bundle.bundle_sha256,profile_id:profile,configuration_asset_id:'config',configuration_sha256:await digest(config)}],repetitions:1},assets:{config,bundle:defaults.bundle}});
  const input={topic:topic.trim(),speaker_count:1,text_length_words:Number(words),english_level:level||null,category_families:['grammar'],category_ids:['grammar.verbs.subject_verb_agreement'],mutation_count:1};
  const expected={schema_version:'1.0.0',expected_mapping:null,expected_metric_values:[],expected_canonical_sha256:null,semantic_propositions:[]};
  const dataset={schema_version:'2.0.0',scope:'generation_pipeline',stage:null,phase:null,cases:[{schema_version:'2.0.0',id:'authored-request',stage:'case_generation',phase:null,polarity:'positive',origin:'constructed',expectation_basis:'authored_assertion',group_id:'starter-request',split:'development',taxonomy_ids:['grammar.verbs.subject_verb_agreement'],input_asset_id:'input',input_sha256:await digest(input),expectations_asset_id:'expected',expectations_sha256:await digest(expected),reference_receipt_ids:[]}]};
  dataset.dataset_sha256=await digest(dataset);
  return ordered({experiment:{scope:'generation_pipeline',dataset_asset_id:'dataset',dataset_sha256:dataset.dataset_sha256,scorer_version:'quality-v1',variants:[{id:'configured-baseline',bundle_id:'bundle',bundle_sha256:defaults.bundle.bundle_sha256,profile_id:profile,configuration_asset_id:'config',configuration_sha256:await digest(config)}],repetitions:1},assets:{dataset,input,expected,config,bundle:defaults.bundle}});
}
