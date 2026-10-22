'use client';
import {useEffect, useState} from 'react';

const stages = {
  saving: 'Saving your answer…',
  not_started: 'Answer saved. Starting the LLM check…',
  extraction: 'Answer saved. Reading your findings…',
  matching: 'Answer saved. Checking findings, corrections and optional explanations…',
  audit: 'Answer saved. Running the configured optional mapping audit…',
  scoring: 'Answer saved. Calculating your score…',
  feedback: 'Answer and score saved. Writing comments and practice recommendations…',
  complete: 'Checking complete. Loading saved results…',
  failed: 'Checking stopped. Loading saved work…',
};

export default function CheckingStatus({checking}) {
  const [seconds, setSeconds] = useState(0);
  useEffect(() => {
    if (!checking) return;
    const tick = () => setSeconds(Math.floor((Date.now() - checking.startedAt) / 1000));
    tick();
    const timer = setInterval(tick, 1000);
    return () => clearInterval(timer);
  }, [checking?.startedAt]);
  if (!checking) return null;
  return <p role="status" aria-label="Checking progress">{stages[checking.stage] || stages.not_started} <span>Elapsed: {seconds}s.</span></p>;
}
