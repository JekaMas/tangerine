'use client';
import {useEffect, useRef, useState} from 'react';

// Own the listening session and HTTP transitions; rendering lives in page.js.
export default function useListening() {
  const [attempt, setAttempt] = useState(null);
  const [results,setResults]=useState(null);
  const answerHash=useRef(''),configurationHash=useRef('');
  const [answer, setAnswer] = useState('');
  const [language, setLanguage] = useState('en');
  const [recovered, setRecovered] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [busy, setBusy] = useState(false);
  const [audioRevision, setAudioRevision] = useState(0);
  const draft = useRef({answer: '', language: 'en', dirty: false});
  const revision = useRef('"0"');
  const audioHash = useRef('');
  const pending = useRef(null);
  const sequence = useRef(0);
  const page = useRef('');
  const attemptID = useRef('');

  function showDraft(text, locale) {
    draft.current = {answer: text, language: locale, dirty: false};
    setAnswer(text);
    setLanguage(locale);
  }
  async function load(preserve = false) {
    const response = await fetch('/api/v1/attempts/' + attemptID.current, {cache: 'no-store'});
    if (!response.ok) throw Error('Saved attempt is unavailable. Your text is retained. Refresh to retry.');
    const value = await response.json();
    revision.current = response.headers.get('etag');
    audioHash.current = response.headers.get('x-tangerine-audio-sha256');
    answerHash.current=response.headers.get('x-tangerine-answer-sha256');
    configurationHash.current=response.headers.get('x-tangerine-configuration-sha256');
    setAttempt(value);
    if (value.submitted_at != null) {
      const local = draft.current;
      if (local.dirty && (local.answer !== value.answer_text || local.language !== value.requested_language)) {
        setRecovered({answer: local.answer, language: local.language});
      }
      // The submitted display always comes from the durable record. Local intent
      // survives separately and can never masquerade as the immutable submission.
      showDraft(value.answer_text, value.requested_language);
      pending.current = null;
      const saved=await fetch(value.results_path,{cache:'no-store'});
      if(saved.ok){setResults(await saved.json());}else{setError('Your answer is saved. Findings are temporarily unavailable. Refresh to retry.');}
    } else if (!preserve || !draft.current.dirty) {
      showDraft(value.answer_text, value.requested_language);
    }
    return value;
  }
  useEffect(() => {
    page.current = crypto.randomUUID();
    let active = true;
    async function open() {
      setBusy(true);
      try {
        const q = new URLSearchParams(window.location.search);
        attemptID.current = q.get('attempt') || '';
        if (!attemptID.current) {
          const id = q.get('case'), sha = q.get('sha');
          if (!id || !sha) throw Error('Select a playable exercise from the Library.');
          const storageKey = 'tangerine-start:' + id;
          let key = sessionStorage.getItem(storageKey);
          if (!key) { key = crypto.randomUUID(); sessionStorage.setItem(storageKey, key); }
          const response = await fetch('/api/v1/attempts', {
            method: 'POST', headers: {'Content-Type': 'application/json', 'Idempotency-Key': key},
            body: JSON.stringify({case_version_id: id, case_sha256: sha, requested_language: 'en'}),
          });
          if (!response.ok) {
            const failure = await response.json();
            throw Error(failure.code === 'CAPABILITY_UNQUALIFIED'
              ? 'Select an available included, free or local evaluator model in Settings before starting an attempt.'
              : response.status === 409 ? 'This exercise is unavailable for a new attempt. Return to the Library.'
                : 'The attempt could not be started. Refresh to retry.');
          }
          const started = await response.json();
          attemptID.current = started.attempt_id;
          sessionStorage.removeItem(storageKey);
          history.replaceState(null, '', '/listen?attempt=' + attemptID.current);
        }
        if (active) await load();
      } catch (e) { if (active) setError(e.message); }
      finally { if (active) setBusy(false); }
    }
    open();
    return () => { active = false; };
  }, []);

  async function refresh() {
    setBusy(true); setError('');
    try {
      await load(true);
      setAudioRevision(n => n + 1);
      setNotice(draft.current.dirty ? 'Saved state refreshed. Your unsaved text is retained.' : 'Saved state refreshed.');
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  async function write(submit) {
    if (Array.from(answer).length > 20000) {
      setError('Answers can contain up to 20,000 characters. Your text is retained.'); return;
    }
    draft.current.dirty = true;
    setBusy(true); setError(''); setNotice('');
    const body = JSON.stringify({answer_text: answer, requested_language: language});
    const action = submit ? ':submit' : '/answer';
    const signature = action + '|' + revision.current + '|' + body;
    if (pending.current?.signature !== signature) pending.current = {signature, key: crypto.randomUUID()};
    try {
      const response = await fetch('/api/v1/attempts/' + attemptID.current + action, {
        method: submit ? 'POST' : 'PUT',
        headers: {'Content-Type': 'application/json', 'If-Match': revision.current, 'Idempotency-Key': pending.current.key},
        body, signal: AbortSignal.timeout(310000),
      });
      const outcome=await response.json();
      const committed=submit&&outcome.attempt_id===attemptID.current&&outcome.status==='evaluation_failed';
      if (!response.ok&&!committed) throw Error(response.status === 412
        ? 'The saved draft changed. Your text is retained. Refresh saved state, then save again.'
        : response.status === 409 ? 'This answer is already submitted or conflicts with a saved request. Your text is retained. Refresh saved state.'
          : 'Your answer could not be saved. Your text is retained. Retry the same action.');
      draft.current.dirty = false;
      pending.current = null;
      await load();
      setNotice(submit ? 'Answer submitted and saved.' : 'Draft saved.');
      if(committed)setError('Your answer is saved. Checking failed. Retry checking after the service is available.');
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  async function retryChecking(){
    setBusy(true);setError('');setNotice('');
    const body=JSON.stringify({answer_sha256:answerHash.current,configuration_sha256:configurationHash.current});
    const signature='retry|'+revision.current+'|'+body;
    if(pending.current?.signature!==signature)pending.current={signature,key:crypto.randomUUID()};
    try{
      const response=await fetch('/api/v1/attempts/'+attemptID.current+':retry',{method:'POST',headers:{'Content-Type':'application/json','If-Match':revision.current,'Idempotency-Key':pending.current.key},body,signal:AbortSignal.timeout(310000)});
      const value=await response.json();
      if(!response.ok&&value.attempt_id!==attemptID.current)throw Error(response.status===409?'Checking is already active or the saved state changed. Refresh saved state.':'Checking is unavailable. Your submitted answer is retained.');
      pending.current=null;await load();
      if(value.status==='evaluation_failed')setError('Your answer is saved. Checking failed. Retry checking after the service is available.');
      else setNotice('Saved findings refreshed.');
    }catch(e){setError(e.message)}finally{setBusy(false)}
  }
  function editAnswer(text) {
    draft.current.answer = text; draft.current.dirty = true;
    setAnswer(text); setNotice('');
  }
  function editLanguage(locale) {
    draft.current.language = locale; draft.current.dirty = true;
    setLanguage(locale);
  }
  function playback(kind, event) {
    if (!attempt || !audioHash.current) return;
    const value = {
      schema_version: '2.0.0', attempt_id: attemptID.current, audio_sha256: audioHash.current,
      kind, client_sequence: sequence.current++, page_instance_id: page.current,
      position_sample: Math.min(Math.round(event.currentTarget.currentTime * 24000), attempt.case.duration_ms * 24),
      client_time_ms: String(Date.now()),
    };
    fetch('/api/v1/attempts/' + attemptID.current + '/playback', {
      method: 'POST', headers: {'Content-Type': 'application/json', 'Idempotency-Key': crypto.randomUUID()},
      body: JSON.stringify(value),
    }).catch(() => {});
  }
  return {attempt, answer, language, recovered, results, error, notice, busy, audioRevision, retryChecking,
    canRefresh: !!attemptID.current, refresh, write, editAnswer, editLanguage, playback,
    audioError: () => setError('Saved audio is temporarily unavailable. Your answer is retained. Refresh saved state to retry playback.')};
}
