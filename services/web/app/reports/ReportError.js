'use client';
import {useEffect,useRef} from 'react';

// Reveal the submitting form's authored feedback without losing its inputs.
export default function ReportError({message}) {
  const box=useRef(null);
  useEffect(()=>{
    if(!message)return;
    const node=box.current;
    const disclosure=node?.closest('details');
    if(disclosure)disclosure.open=true;
    node?.focus({preventScroll:true});
    node?.scrollIntoView({block:'center'});
  },[message]);
  return message?<p ref={box} tabIndex={-1} role="alert" className="error">{message}</p>:null;
}
