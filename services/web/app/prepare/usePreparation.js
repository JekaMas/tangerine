'use client';
import {useEffect, useRef, useState} from 'react';
import {blueprintRequest} from './request';

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
      const q = new URLSearchParams({limit:'50'}); if (append && cursor) q.set('cursor',cursor);
      const r = await fetch('/api/v1/preparations?'+q,{cache:'no-store'});
      if (!r.ok) throw Error('Saved preparations are unavailable. Your input is retained. Refresh to retry.');
      const data = await r.json(); setItems(old => append ? [...old,...data.items] : data.items); setCursor(data.next_cursor);
    } catch(e) { setError(e.message); }
  }
  async function retryCategories(){setCategoryLoading(true);setCategoryError('');try{const r=await fetch('/api/v1/preparation-options',{cache:'no-store'});if(!r.ok)throw Error('Catalogue unavailable');const data=await r.json();setCategories(data.categories);setVoices(data.voices||[]);}catch{setCategoryError('Category and voice choices are unavailable. Your choices are retained. Retry to load the list.');}finally{setCategoryLoading(false);}}
  useEffect(() => { refresh(); retryCategories(); return () => controller.current?.abort(); }, []);
  async function request(url, body, key) {
    const r = await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','Idempotency-Key':key},body:JSON.stringify(body),signal:controller.current.signal});
    const data = await r.json();
    if (!r.ok) {
      const messages = {
        PAID_USE_FORBIDDEN:'This profile has no confirmed free, local or included access. Choose an eligible profile in Settings. No paid fallback was used.',
        LOCAL_BUDGET_EXCEEDED:'Included allowance is unavailable. Check Settings or retry after reset.',
        MODEL_SETUP_REQUIRED:'Set up the selected local speech model, then Resume. For Australian or Indian voices, run scripts/tangerine model-setup local-english-accents-v1.',
        MISSING_CREDENTIAL:'Supply the selected credential in Settings, then Resume.',
        LEASE_ACTIVE:'This preparation is still running. Refresh after it finishes or its foreground deadline expires.',
        REVISION_STALE:'The saved state changed. Refresh before resuming.',
      };
      throw Error(messages[data.code] || data.message || 'The exercise is not complete. Refresh to see saved progress, then Resume.');
    }
    return data;
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
        if (!config.ok) throw Error('Configuration is unavailable. Your request is retained. Retry when Settings is available.');
        const c = await config.json();
        await request('/api/v1/candidates:generate',{blueprint_id:blueprint.id,effective_configuration_sha256:c.configuration.configuration_sha256,source_record_ids:[],generation_attempt:1,preparation_id:null},crypto.randomUUID());
      }
      setNotice('Exercise saved. Open the Library to listen and answer.');
    } catch(e) {
      setError(e.name==='AbortError' ? 'Generation stopped. Saved text, mutations and completed audio pieces are retained. Refresh, then Resume explicitly.' : e instanceof SyntaxError ? 'Advanced blueprint is not valid JSON. Your form values are retained.' : e instanceof TypeError && /fetch/i.test(e.message) ? 'Could not reach the local service. Your choices are retained. Check Recovery, then retry or resume a saved preparation.' : e.message);
      setNotice('');
    } finally { clearTimeout(timeout); controller.current=null; setBusy(false); await refresh(); }
  }
  return {form, update, items, cursor, busy, error, notice, generate, categories, voices, categoryLoading, categoryError, retryCategories, refresh: (append=false) => {setError(''); return refresh(append);}, stop: () => controller.current?.abort()};
}
