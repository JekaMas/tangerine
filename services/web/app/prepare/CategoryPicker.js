'use client';
import {useState} from 'react';
import {mistakeFamilies,mistakeCount} from './request';
import Icon from '../Icon';

export default function CategoryPicker({form,update,categories,loading,error,retry}) {
  const [search,setSearch]=useState('');
  const selected=form.categories || [], families=form.families || [];
  let controlOnly=false;try{controlOnly=mistakeCount(form)===0;}catch{}
  const errors=categories.filter(x=>!x.control);
  const query=search.trim().toLowerCase();
  const visible=errors.filter(x=>!query || [x.label,x.description,x.id,mistakeFamilies.find(([id])=>id===x.family)?.[1]||'',x.id==='lexis.lexical_register'||x.id==='lexis.redundancy_pleonasm'?'style':''].some(v=>v.toLowerCase().includes(query)));
  function toggleCategory(id) {update('categories',selected.includes(id)?selected.filter(x=>x!==id):[...selected,id]);update('families',[]);}
  function toggleFamily(id) {update('families',families.includes(id)?families.filter(x=>x!==id):[...families,id]);update('categories',[]);}
  function clear(){update('categories',[]);update('families',[]);}
  return <fieldset className="control-section category-section"><legend>What would you like to practise?</legend>
    <p className="field-help">Choose broad families or pick individual mistake types. Leave both empty for automatic selection.</p>
    <div className="family-options" role="group" aria-label="Broad mistake families">{mistakeFamilies.map(([id,label])=><label className="choice-chip" key={id}><input type="checkbox" checked={families.includes(id)} aria-label={label} onChange={()=>toggleFamily(id)}/><span>{label}</span></label>)}</div>
    <div className="category-tools"><label className="search-field"><Icon name="search"/><input type="search" aria-label="Search mistake categories" placeholder="Find collocations, word stress, formality…" value={search} onChange={e=>setSearch(e.target.value)}/></label><button type="button" className="text-button" onClick={clear} disabled={!selected.length&&!families.length}>Clear selection</button></div>
    {selected.length>0&&<div className="selected-categories" aria-label="Selected categories">{selected.map(id=><button className="selected-chip" key={id} type="button" aria-label={'Remove '+(errors.find(x=>x.id===id)?.label||id)} onClick={()=>toggleCategory(id)}>{errors.find(x=>x.id===id)?.label||id}<Icon name="close" size={13}/></button>)}</div>}
    {loading&&<p role="status" className="field-help">Loading registered categories…</p>}
    {error&&<div className="error" role="alert"><p>{error}</p><button type="button" className="secondary" onClick={retry}>Retry categories</button></div>}
    {!loading&&!error&&<div className="category-tree" aria-label="Individual mistake categories">
      {mistakeFamilies.filter(([id])=>id!=='pronunciation').map(([family,label])=>{
        const rows=visible.filter(x=>x.family===family);if(!rows.length)return null;
        return <details key={family} open={Boolean(query)||rows.some(x=>selected.includes(x.id))}><summary>{label}<span>{rows.length} {rows.length===1?'type':'types'}</span></summary><div className="category-options">{rows.map(item=><label key={item.id} className="category-option"><input type="checkbox" checked={selected.includes(item.id)} aria-label={item.label} onChange={()=>toggleCategory(item.id)}/><span><strong>{item.label}</strong><small>{item.description}</small></span></label>)}</div></details>;
      })}
      {!visible.length&&<p className="search-empty">No matching categories. Try a different term; your selected categories are retained.</p>}
    </div>}
    <p className="selection-caption" aria-live="polite">{controlOnly?'No mistakes will be injected; your category selection is retained.':selected.length?`${selected.length} specific ${selected.length===1?'category':'categories'} selected. ${selected.length===1?'It':'Each'} receives at least one mistake.`:families.length?'The LLM chooses specific mistakes within your selected families.':'Automatic selection across the available mistake families.'}</p>
  </fieldset>;
}
