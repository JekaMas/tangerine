'use client';
import {useEffect,useRef,useState} from 'react';
import RefreshButton from '../RefreshButton.js';
import {requestError,userError} from '../requestError.js';
import {recordDate} from '../savedRecord';
import {reportStarter,reportFromPopulation,experimentStarter,generationProfiles} from './starters';
import {reportRequest} from './request';

export default function StarterForms({kind,busy,onSave,list,onRefresh}) {
  const [title,setTitle]=useState('Constructed example: one error in two sentences');
  const [category,setCategory]=useState('lexis.collocation'),[selected,setSelected]=useState('');
  const [topic,setTopic]=useState('A café opening tomorrow'),[level,setLevel]=useState('B1');
  const [words,setWords]=useState(50),[profile,setProfile]=useState('');
  const [defaults,setDefaults]=useState(null),[error,setError]=useState('');
  const [loading,setLoading]=useState(false),[saving,setSaving]=useState(false);
  const version=useRef(0);
  async function load() {
    const current=++version.current;
    setLoading(true);setError('');
    try {
      const value=await reportRequest('lab/defaults');
      if(current!==version.current)return;
      setDefaults(value);
      setProfile(old=>old||value.configuration.stage_profiles?.case_generation||value.configuration.llm_profile);
    } catch(failure) {
      if(current===version.current)setError(requestError(failure,'Configured experiment choices are unavailable. Retry or open Settings. Your input is retained.'));
    } finally {if(current===version.current)setLoading(false);}
  }
  useEffect(()=>{if(kind==='experiment')load();return()=>{version.current++;};},[kind]);
  const choices=(list?.items||[]).filter(item=>kind==='report'||(item.scope==='generation_pipeline'&&!item.judge_policy_asset_id));
  const profiles=generationProfiles(defaults);
  async function save(event) {
    event.preventDefault();setError('');setSaving(true);
    try {
      let value;
      if(kind==='report') {
        if(selected) {
          const saved=await reportRequest('reports/empirical/'+encodeURIComponent(selected));
          value=reportFromPopulation(title,null,saved.source_input_asset_id);
        } else value=reportStarter(title,category);
      } else {
        const dataset=choices.find(item=>item.id===selected);
        if(selected&&!dataset)throw userError('The selected saved dataset is unavailable. Refresh choices or select a new request. Your input is retained.');
        value=await experimentStarter(defaults,{topic,level,words,profile,dataset});
      }
      await onSave(JSON.stringify(value));
    } catch(failure) {setError(requestError(failure,'This starter could not be saved. Your fields are retained. Refresh choices and retry.'));}
    finally {setSaving(false);}
  }
  return <form className="card" onSubmit={save}>
    <h3>{kind==='report'?'Create a report':'Create a generation experiment'}</h3>
    <label>{kind==='report'?'Report data':'Experiment dataset'}<select aria-label={kind==='report'?'Report data':'Experiment dataset'} value={selected} onChange={e=>setSelected(e.target.value)}>
      <option value="">{kind==='report'?'Constructed example · two authored sentences':'New request · subject–verb agreement'}</option>
      {selected&&!choices.some(item=>item.id===selected)&&<option value={selected}>Previously selected data · unavailable</option>}
      {choices.map(item=><option key={item.id} value={item.id}>{kind==='report'?item.title:'Saved generation dataset'} · {recordDate(item.created_at)}</option>)}
    </select></label>
    {selected&&<p className="field-help">Uses the saved {kind==='report'?'population, source selection and observation origins':'dataset and its original inputs and expectations'} unchanged. </p>}
    {list?.loaded&&!list.error&&!choices.length&&<p className="field-help">{kind==='report'?<>No saved populations yet. Use the labelled example, or <a href="/sources">import source data</a> and choose it above.</>:<>No saved generation datasets yet. Start with the request below. Advanced supports other experiment workflows.</>}</p>}
    {kind==='report'?<>
      {!selected&&<><p>This constructed example has one mistake and one correct use. It demonstrates arithmetic, not real learner frequencies.</p><p className="field-help">{category==='lexis.collocation'?'Error: “We did a decision.” Correct control: “We made a decision.”':'Error: “The café open tomorrow.” Correct control: “The café opens tomorrow.”'}</p></>}
      <div className="guided-fields"><label>Report title<input required aria-label="Report title" value={title} onChange={e=>setTitle(e.target.value)}/></label>
        {!selected&&<label>Example category<select aria-label="Example category" value={category} onChange={e=>setCategory(e.target.value)}><option value="lexis.collocation">Collocation</option><option value="grammar.verbs.subject_verb_agreement">Subject–verb agreement</option></select></label>}
      </div>
    </>:<>
      <p>Save a frozen experiment with your selected LLM configuration and current prompt bundle. Saving makes no model call. Run remains a separate action. This starter has no semantic judge; use Advanced for judged or answer-checking experiments.</p>
      <div className="guided-fields">
        {!selected&&<><label>Experiment topic<input required aria-label="Experiment topic" value={topic} onChange={e=>setTopic(e.target.value)}/></label><label>Experiment word count<input required aria-label="Experiment word count" type="number" min="1" step="1" value={words} onChange={e=>setWords(e.target.value)}/></label><label>Experiment English level<select aria-label="Experiment English level" value={level} onChange={e=>setLevel(e.target.value)}>{['A1','A2','B1','B2','C1','C2'].map(value=><option key={value}>{value}</option>)}</select></label></>}
        <label>Configured LLM<select required aria-label="Experiment LLM profile" value={profile} onChange={e=>setProfile(e.target.value)}><option value="">Choose a configured profile</option>{profile&&!profiles.some(p=>p.id===profile)&&<option value={profile}>Previously selected profile · setup needed</option>}{profiles.map(p=><option key={p.id} value={p.id}>{p.model} · {({local:'Local',subscription_included:'Included plan',free_tier:'Free allowance'})[p.billing_mode]||p.billing_mode.replaceAll('_',' ')}</option>)}</select></label>
      </div>
      <p className="field-help">Prompt bundle: {defaults?'Current saved prompts':loading?'Loading current prompts…':'Unavailable'}. <a href="/settings">Manage configured providers</a>.</p>
      {defaults&&!profiles.length&&<p>No generation model is configured. <a href="/settings">Choose an included, free or local model in Settings</a>, then refresh choices. Your request is retained.</p>}
      {loading&&<p role="status">Loading current configuration…</p>}
      <RefreshButton onClick={()=>{load();onRefresh?.();}}>{defaults?'Refresh experiment choices':'Retry experiment choices'}</RefreshButton>
    </>}
    {error&&<p role="alert">{error}</p>}
    <button disabled={busy||saving||(kind==='experiment'&&(!defaults||!profiles.length))}>{kind==='report'?'Calculate report from selection':'Save starter experiment'}</button>
  </form>;
}
