'use client';
import {clientFetch as fetch} from '../clientRequest.js';
import {requestError,userError} from '../requestError.js';
import {useEffect, useRef, useState} from 'react';
import {watchChecking} from './checkingProgress';

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
  const [checking, setChecking] = useState(null);
  const observer = useRef(null), writeController = useRef(null), mounted = useRef(true);
  const [audioRevision, setAudioRevision] = useState(0);
  const draft = useRef({answer: '', language: 'en', dirty: false});
  const revision = useRef('"0"');
  const audioHash = useRef('');
  const pending = useRef(null);
  const sequence = useRef(0);
  const page = useRef('');
  const attemptID = useRef('');
  const readVersion = useRef(0);

  // Manual refresh, foreground readback and progress share one delivery owner.
  function beginRead() {
    const version = ++readVersion.current;
    return () => mounted.current && version === readVersion.current;
  }

  function showDraft(text, locale) {
    draft.current = {answer: text, language: locale, dirty: false};
    setAnswer(text);
    setLanguage(locale);
  }
  function showSubmitted(value) {
    const local = draft.current;
    if (local.dirty && (local.answer !== value.answer_text || local.language !== value.requested_language)) {
      setRecovered({answer: local.answer, language: local.language});
    }
    showDraft(value.answer_text, value.requested_language);
  }
  function observeChecking(stage) {
    observer.current?.();
    setChecking({startedAt: Date.now(), stage});
    observer.current = watchChecking(attemptID.current, (value, saved) => {
      setAttempt(value);
      showSubmitted(value);
      if (saved) setResults(saved);
      setChecking(old => old && ({...old, stage: saved?.checking_stage || (old.stage === 'saving' ? 'not_started' : old.stage)}));
    }, beginRead);
  }
  function stopChecking() {
    observer.current?.();
    observer.current = null;
  }
  async function load(preserve = false) {
    const current = beginRead();
    try {
      const response = await fetch('/api/v1/attempts/' + attemptID.current, {cache: 'no-store'});
      if (!response.ok) throw userError('Saved attempt is unavailable. Your text is retained. Refresh to retry.');
      const value = await response.json();
      if (!current()) return null;
      revision.current = response.headers.get('etag');
      audioHash.current = response.headers.get('x-tangerine-audio-sha256');
      answerHash.current=response.headers.get('x-tangerine-answer-sha256');
      configurationHash.current=response.headers.get('x-tangerine-configuration-sha256');
      setAttempt(value);
      if (value.submitted_at != null) {
        // The submitted display always comes from the durable record. Local intent
        // survives separately and can never masquerade as the immutable submission.
        showSubmitted(value);
        pending.current = null;
        const unavailable = 'Your answer is saved. Findings are temporarily unavailable. Refresh to retry.';
        try {
          const saved=await fetch(value.results_path,{cache:'no-store'});
          if(saved.ok){const result=await saved.json();if(current())setResults(result);}
          else if(current())setError(unavailable);
        } catch (failure) { if(current())setError(requestError(failure,unavailable)); }
      } else if (!preserve || !draft.current.dirty) {
        showDraft(value.answer_text, value.requested_language);
      }
      return current() ? value : null;
    } catch (failure) { if(current())throw failure; return null; }
  }
  useEffect(() => {
    mounted.current = true;
    page.current = crypto.randomUUID();
    let active = true;
    async function open() {
      setBusy(true);
      try {
        const q = new URLSearchParams(window.location.search);
        attemptID.current = q.get('attempt') || '';
        if (!attemptID.current) {
          const id = q.get('case'), sha = q.get('sha');
          if (!id || !sha) throw userError('Select a playable exercise from the Library.');
          const storageKey = 'tangerine-start:' + id;
          let key = sessionStorage.getItem(storageKey);
          if (!key) { key = crypto.randomUUID(); sessionStorage.setItem(storageKey, key); }
          const response = await fetch('/api/v1/attempts', {
            method: 'POST', headers: {'Content-Type': 'application/json', 'Idempotency-Key': key},
            body: JSON.stringify({case_version_id: id, case_sha256: sha, requested_language: 'en'}),
          });
          if (!response.ok) {
            const failure = await response.json();
            throw userError(failure.code === 'CAPABILITY_UNQUALIFIED'
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
      } catch (e) { if (active) setError(requestError(e)); }
      finally { if (active) setBusy(false); }
    }
    open();
    return () => { active = false; mounted.current = false; readVersion.current++; stopChecking(); writeController.current?.abort(); };
  }, []);

  async function refresh() {
    setError('');
    try {
      const value = await load(true);
      if (!value) return;
      setAudioRevision(n => n + 1);
      setNotice(draft.current.dirty ? 'Saved state refreshed. Your unsaved text is retained.' : 'Saved state refreshed.');
    } catch (e) { setError(requestError(e)); }
  }
  async function write(submit) {
    if (Array.from(answer).length > 20000) {
      setError('Answers can contain up to 20,000 characters. Your text is retained.'); return;
    }
    draft.current.dirty = true;
    readVersion.current++;
    setBusy(true); setError(''); setNotice('');
    const body = JSON.stringify({answer_text: answer, requested_language: language});
    const action = submit ? ':submit' : '/answer';
    const signature = action + '|' + revision.current + '|' + body;
    if (pending.current?.signature !== signature) pending.current = {signature, key: crypto.randomUUID()};
    writeController.current = new AbortController();
    if (submit) observeChecking('saving');
    try {
      const response = await fetch('/api/v1/attempts/' + attemptID.current + action, {
        method: submit ? 'POST' : 'PUT',
        headers: {'Content-Type': 'application/json', 'If-Match': revision.current, 'Idempotency-Key': pending.current.key},
        body, signal: AbortSignal.any([writeController.current.signal, AbortSignal.timeout(310000)]),
      });
      const outcome=await response.json();
      const committed=submit&&!response.ok&&outcome.attempt_id===attemptID.current&&(outcome.status==='evaluation_failed'||outcome.score!=null);
      if (!response.ok&&!committed) throw userError(response.status === 412
        ? 'The saved draft changed. Your text is retained. Refresh saved state, then save again.'
        : response.status === 409 ? 'This answer is already submitted or conflicts with a saved request. Your text is retained. Refresh saved state.'
          : 'Your answer could not be saved. Your text is retained. Retry the same action.');
      draft.current.dirty = false;
      pending.current = null;
      stopChecking();
      if (!mounted.current) return;
      await load();
      setNotice(submit ? 'Answer submitted and saved.' : 'Draft saved.');
      if(committed)setError(outcome.score!=null?'Your answer and score are saved. Comments are unavailable. Retry comments and recommendations.':'Your answer is saved. Checking failed. Retry checking after the service is available.');
    } catch (e) {
      stopChecking();
      if (!mounted.current) return;
      if (submit) {
        try {
          const saved = await load(true);
          if (!saved) return;
          if (saved.submitted_at != null) {
            setNotice('Answer submitted and saved.');
            setError('Checking was interrupted. Your saved answer and any completed findings are retained. Refresh saved state, then explicitly resume if needed.');
          } else setError(requestError(e));
        } catch { setError('Completion could not be confirmed. Your text is retained. Refresh saved state before retrying.'); }
      } else setError(requestError(e));
    }
    finally { stopChecking(); writeController.current = null; if (mounted.current) { setChecking(null); setBusy(false); } }
  }
  async function retryChecking(){
    readVersion.current++;
    setBusy(true);setError('');setNotice('');
    const body=JSON.stringify({answer_sha256:answerHash.current,configuration_sha256:configurationHash.current});
    const signature='retry|'+revision.current+'|'+body;
    if(pending.current?.signature!==signature)pending.current={signature,key:crypto.randomUUID()};
    writeController.current=new AbortController();observeChecking(results?.score?'feedback':'not_started');
    try{
      const action=results?.score?':retry-feedback':':retry';
      const response=await fetch('/api/v1/attempts/'+attemptID.current+action,{method:'POST',headers:{'Content-Type':'application/json','If-Match':revision.current,'Idempotency-Key':pending.current.key},body,signal:AbortSignal.any([writeController.current.signal,AbortSignal.timeout(310000)])});
      const value=await response.json();
      if(!response.ok&&value.attempt_id!==attemptID.current)throw userError(response.status===409?'Checking is already active or the saved state changed. Refresh saved state.':'Checking is unavailable. Your submitted answer is retained.');
      pending.current=null;stopChecking();if(!mounted.current)return;await load();
      if(value.status==='evaluation_failed')setError('Your answer is saved. Checking failed. Retry checking after the service is available.');
      else setNotice('Saved findings refreshed.');
    }catch(e){if(mounted.current)setError(requestError(e))}finally{stopChecking();writeController.current=null;if(mounted.current){setChecking(null);setBusy(false)}}
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
  return {attempt, answer, language, recovered, results, error, notice, busy, checking, audioRevision, retryChecking,
    canRefresh: !!attemptID.current, refresh, write, editAnswer, editLanguage, playback,
    audioError: failure => setError(requestError(failure,'Saved audio is temporarily unavailable. Your answer is retained. Refresh saved state to retry playback.'))};
}
