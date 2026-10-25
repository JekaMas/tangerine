'use client';
import {clientFetch as fetch} from '../clientRequest.js';
import {requestError,userError} from '../requestError.js';
import {useEffect, useRef, useState} from 'react';
import {blueprintRequest} from './request';
import {preparationResponse} from './response.js';

// Own foreground requests and retained form state; Controls owns presentation.
export default function usePreparation() {
  const [form, setForm] = useState({topic:'', speakers:1, words:150, level:'', families:[], categories:[], severities:[], amount:'auto', mutationCount:'', voices:[], recurring:[], advanced:''});
  const [voices,setVoices]=useState([]);
  const [categories,setCategories]=useState([]),[categoryLoading,setCategoryLoading]=useState(true),[categoryError,setCategoryError]=useState('');
  const [items, setItems] = useState([]), [cursor, setCursor] = useState(null);
  const [busy, setBusy] = useState(false), [error, setError] = useState(''), [notice, setNotice] = useState('');
  const controller = useRef(null);
  const update = (field, value) => setForm(old => ({...old, [field]:value}));
  async function refresh(append=false) {
    try {
      const q = new URLSearchParams({limit:'50',view:'public'}); if (append && cursor) q.set('cursor',cursor);
      const r = await fetch('/api/v1/preparations?'+q,{cache:'no-store'});
      if (!r.ok) throw userError('Saved preparations are unavailable. Your input is retained. Refresh to retry.');
      const data = await r.json(); setItems(old => append ? [...old,...data.items] : data.items); setCursor(data.next_cursor);
    } catch(e) { const message=requestError(e);setError(old=>old||message); }
  }
  async function retryCategories(){setCategoryLoading(true);setCategoryError('');try{const r=await fetch('/api/v1/preparation-options',{cache:'no-store'});if(!r.ok)throw userError('Catalogue unavailable');const data=await r.json();setCategories(data.categories);setVoices(data.voices||[]);}catch{setCategoryError('Category and voice choices are unavailable. Your choices are retained. Retry to load the list.');}finally{setCategoryLoading(false);}}
  useEffect(() => { refresh(); retryCategories(); return () => controller.current?.abort(); }, []);
  async function request(url, body, key) {
    const r = await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':key},body:JSON.stringify(body),signal:controller.current.signal});
    return preparationResponse(r);
  }
  async function generate(id=null) {
    setBusy(true); setError(''); setNotice(id ? 'Resuming saved preparation…' : 'Generating clean text, mutations and audio…');
    controller.current = new AbortController();
    const timeout = setTimeout(() => controller.current?.abort(),270000);
    try {
      if (id) await request('/api/v1/preparations/'+id+':resume',{},crypto.randomUUID());
      else {
        const blueprint = await request('/api/v1/blueprints',blueprintRequest(form),crypto.randomUUID());
        const config = await fetch('/api/v1/configuration',{cache:'no-store',signal:controller.current.signal});
        if (!config.ok) throw userError('Configuration is unavailable. Your request is retained. Retry when Settings is available.');
        const c = await preparationResponse(config);
        await request('/api/v1/candidates:generate',{blueprint_id:blueprint.id,effective_configuration_sha256:c.configuration.configuration_sha256,source_record_ids:[],generation_attempt:1,preparation_id:null},crypto.randomUUID());
      }
      setNotice('Exercise saved. Open the Library to listen and answer.');
    } catch(e) {
      setError(e.name==='AbortError' ? 'Generation stopped. Saved text, mutations and completed audio pieces are retained. Refresh, then Resume explicitly.' : e instanceof TypeError && /fetch/i.test(e.message) ? 'Could not reach the local service. Your choices are retained. Check Recovery, then retry or resume a saved preparation.' : requestError(e));
      setNotice('');
    } finally { clearTimeout(timeout); controller.current=null; setBusy(false); await refresh(); }
  }
  return {form, update, items, cursor, busy, error, notice, generate, categories, voices, categoryLoading, categoryError, retryCategories, refresh: (append=false) => {setError(''); return refresh(append);}, stop: () => controller.current?.abort()};
}
