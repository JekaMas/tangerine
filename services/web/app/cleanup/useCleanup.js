'use client';
import {useEffect,useRef,useState} from 'react';
import {clientFetch} from '../clientRequest.js';
import {userError} from '../requestError.js';
import {createCleanupSession} from './session';

export default function useCleanup() {
  const [state,setState]=useState({ids:'',plan:null,confirmed:false,pending:null,error:'',scope:''});
  const owner=useRef(null);
  if(!owner.current)owner.current=createCleanupSession({onChange:setState,request:async({apply,orphans,ids,plan})=>{
    const response=await clientFetch(apply?'/api/v1/deletions/'+plan.id+':apply':'/api/v1/deletions',{
      method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify(apply?{confirmed_plan_sha256:plan.confirmation_sha256}:{subject_ids:orphans?[]:ids.split(/[,\s]+/).filter(Boolean),orphan_cleanup:orphans}),
    });
    if(!response.ok)throw userError('The cleanup outcome could not be confirmed. Your selection is retained. Refresh the preview before retrying.');
    return response.json();
  }});
  useEffect(()=>{const id=new URLSearchParams(window.location.search).get('subject');if(id)owner.current.select(id);return()=>owner.current.cancel();},[]);
  return {...state,select:owner.current.select,confirm:owner.current.confirm,preview:owner.current.preview,apply:owner.current.apply};
}
