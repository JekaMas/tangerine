'use client';
import {useEffect,useRef,useState} from 'react';
import useSavedList from '../useSavedList';
import {reportRequest as request} from './request';
import {createReportsSession} from './session';

// Session transitions and delivery; native API owns freezing and calculation.
export default function useReports() {
  const reports=useSavedList('/api/v1/reports/empirical',{unavailable:'Saved reports are unavailable. Refresh to retry.'});
  const experiments=useSavedList('/api/v1/lab/experiments',{unavailable:'Saved experiments are unavailable. Refresh to retry.'});
  const [state,setState]=useState({report:null,run:null,comparisons:[],reportError:'',runError:'',actionError:'',comparisonError:'',notice:'',busy:false,loadingReport:false,loadingRun:false,loadingComparisons:false});
  const owner=useRef(null);
  if(!owner.current)owner.current=createReportsSession({request,onChange:setState,refreshReports:reports.refresh,refreshExperiments:experiments.refresh,
    remember:id=>localStorage.setItem('tangerine-quality-experiment',id)});
  useEffect(()=>{
    const reportID=new URLSearchParams(window.location.search).get('report');
    if(reportID)owner.current.loadReport(reportID);
    try{const id=localStorage.getItem('tangerine-quality-experiment');if(id)owner.current.loadRun(id);}
    catch(failure){console.warn('Tangerine experiment restore preference',{kind:failure.name||'UnknownError'});}
    return()=>owner.current.cancel();
  },[]);
  useEffect(()=>{
    if(!state.report)return;
    const url=new URL(window.location.href);
    url.searchParams.set('report',state.report.id);
    window.history.replaceState(window.history.state,'',url);
  },[state.report?.id]);
  return {...state,error:state.actionError,reports,experiments,...owner.current,selectReport:owner.current.loadReport,selectRun:owner.current.loadRun};
}
