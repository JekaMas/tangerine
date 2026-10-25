'use client';
import {useCallback,useEffect,useRef,useState} from 'react';
import {clientFetch} from './clientRequest.js';
import {userError} from './requestError.js';
import {createSavedList,emptySavedList} from './savedList.js';

// Adapt existing list envelopes once; accepted record fields remain trusted.
export default function useSavedList(url,{limit=null,publicView=false,wrapped=false,unavailable}) {
  const [state,setState]=useState(emptySavedList);
  const owner=useRef(null),options=useRef(null);
  options.current={url,limit,publicView,wrapped,unavailable};
  if (!owner.current) owner.current=createSavedList({onChange:setState,unavailable});
  const refresh=useCallback((append=false)=>owner.current.read(async cursor=>{
    const o=options.current,query=new URLSearchParams();
    if(o.limit)query.set('limit',String(o.limit));
    if(o.publicView)query.set('view','public');
    if(cursor)query.set('cursor',cursor);
    const response=await clientFetch(o.url+(query.size?'?'+query:''),{cache:'no-store'});
    if(!response.ok)throw userError(o.unavailable);
    const data=await response.json();
    return {items:o.wrapped?data.items:data,cursor:o.wrapped?data.next_cursor:response.headers.get('x-tangerine-next-cursor')};
  },append),[]);
  useEffect(()=>{refresh();return()=>owner.current.cancel();},[refresh,url,limit,publicView,wrapped]);
  return {...state,refresh};
}
