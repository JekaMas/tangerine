'use client';
import {useEffect,useRef,useState} from 'react';
import useSavedList from '../useSavedList';
import {requestError,parseUserJSON} from '../requestError.js';
import {reportRequest as request} from './request';

// Session transitions and delivery; native API owns freezing and calculation.
export default function useReports() {
  const reports=useSavedList('/api/v1/reports/empirical',{unavailable:'Saved reports are unavailable. Refresh to retry.'});
  const experiments=useSavedList('/api/v1/lab/experiments',{unavailable:'Saved experiments are unavailable. Refresh to retry.'});
  const [report,setReport]=useState(null),[run,setRun]=useState(null),[comparisons,setComparisons]=useState([]);
  const [error,setError]=useState(''),[notice,setNotice]=useState(''),[busy,setBusy]=useState(false);
  const reportVersion=useRef(0),runVersion=useRef(0);
  async function action(fn) {
    setError('');setNotice('');setBusy(true);
    try {await fn();}catch(failure){setError(requestError(failure));}finally{setBusy(false);}
  }
  async function loadReport(id) {
    const current=++reportVersion.current;
    try {const value=await request('reports/empirical/'+encodeURIComponent(id));if(current===reportVersion.current)setReport(value);}
    catch(failure){if(current===reportVersion.current)throw failure;}
  }
  async function loadRun(id) {
    const current=++runVersion.current;
    try {
      const value=await request('lab/experiments/'+encodeURIComponent(id));
      const paired=value.comparison_asset_id?await request('lab/assets/'+encodeURIComponent(value.comparison_asset_id)):[];
      if(current!==runVersion.current)return;
      setRun(value);setComparisons(paired);localStorage.setItem('tangerine-quality-experiment',id);
    }catch(failure){if(current===runVersion.current)throw failure;}
  }
  async function refresh() {
    setError('');await Promise.all([reports.refresh(),experiments.refresh()]);
    if(run)try{await loadRun(run.id);}catch(failure){setError(requestError(failure));}
  }
  useEffect(()=>{
    const id=localStorage.getItem('tangerine-quality-experiment');if(id)action(()=>loadRun(id));
    return()=>{reportVersion.current++;runVersion.current++;};
  },[]);
  async function createReport(definition) {
    await action(async()=>{
      const current=++reportVersion.current;
      parseUserJSON(definition,'Report definition');
      const value=await request('reports/empirical',{method:'POST',headers:{'Content-Type':'application/json'},body:definition});
      if(current===reportVersion.current)setReport(value);
      setNotice('Report saved.');await reports.refresh();
    });
  }
  async function admit(definition) {
    await action(async()=>{
      const current=++runVersion.current;
      parseUserJSON(definition,'Experiment definition');
      const value=await request('lab/experiments',{method:'POST',headers:{'Content-Type':'application/json'},body:definition});
      if(current===runVersion.current){setRun(value);setComparisons([]);localStorage.setItem('tangerine-quality-experiment',value.id);}
      setNotice('Experiment saved. Run it when you choose.');await experiments.refresh();
    });
  }
  async function runAction(kind) {
    await action(async()=>{await request('lab/experiments/'+run.id+':'+kind,{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});await loadRun(run.id);});
  }
  return {reports,experiments,report,run,comparisons,error,notice,busy,refresh,createReport,admit,runAction,
    selectReport:id=>action(()=>loadReport(id)),selectRun:id=>action(()=>loadRun(id))};
}
