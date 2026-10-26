import {parseUserJSON,requestError} from '../requestError.js';

// Selected identities and delivery live here; native owners freeze and calculate.
export function createReportsSession({request,onChange,refreshReports,refreshExperiments,remember=()=>{}}) {
  let state={report:null,run:null,comparisons:[],reportError:'',runError:'',actionError:'',comparisonError:'',notice:'',busy:false,loadingReport:false,loadingRun:false,loadingComparisons:false};
  let reportID=null,runID=null,reportVersion=0,runVersion=0,comparisonVersion=0,lifetime=0,actionVersion=0;
  const writes=new Set();
  const publish=change=>{state={...state,...change};onChange(state);};
  async function loadReport(id) {
    const current=++reportVersion;
    reportID=id;
    publish({report:state.report?.id===id?state.report:null,reportError:'',loadingReport:true});
    try {const value=await request('reports/empirical/'+encodeURIComponent(id));if(current===reportVersion)publish({report:value});}
    catch(failure){if(current===reportVersion)publish({reportError:requestError(failure)});}
    finally{if(current===reportVersion)publish({loadingReport:false});}
  }
  async function loadComparisons(value,currentRun=runVersion) {
    const current=++comparisonVersion;
    publish({comparisonError:'',loadingComparisons:!!value.comparison_asset_id});
    if(!value.comparison_asset_id){publish({comparisons:[]});return;}
    try {
      const paired=await request('lab/assets/'+encodeURIComponent(value.comparison_asset_id));
      if(currentRun===runVersion&&current===comparisonVersion)publish({comparisons:paired});
    }catch(failure){
      requestError(failure);
      if(currentRun===runVersion&&current===comparisonVersion)publish({comparisonError:'Comparison details are temporarily unavailable. The saved experiment remains usable. Retry comparison details.'});
    }finally{if(currentRun===runVersion&&current===comparisonVersion)publish({loadingComparisons:false});}
  }
  async function loadRun(id) {
    const current=++runVersion;
    comparisonVersion++;
    runID=id;
    publish({run:state.run?.id===id?state.run:null,comparisons:state.run?.id===id?state.comparisons:[],runError:'',comparisonError:'',loadingRun:true,loadingComparisons:false});
    try {
      const value=await request('lab/experiments/'+encodeURIComponent(id));
      if(current!==runVersion)return;
      publish({run:value,comparisons:state.run?.comparison_asset_id===value.comparison_asset_id?state.comparisons:[],loadingRun:false});
      try{remember(id);}catch(failure){console.warn('Tangerine experiment restore preference',{kind:failure.name||'UnknownError'});}
      await loadComparisons(value,current);
    }catch(failure){if(current===runVersion)publish({runError:requestError(failure)});}
    finally{if(current===runVersion)publish({loadingRun:false});}
  }
  async function save(kind,definition) {
    const life=lifetime,action=++actionVersion,write=Symbol(kind);
    writes.add(write);publish({busy:true,actionError:'',notice:''});
    try {
      parseUserJSON(definition,kind==='report'?'Report definition':'Experiment definition');
      const current=kind==='report'?++reportVersion:++runVersion;
      publish(kind==='report'?{loadingReport:false}:{loadingRun:false,loadingComparisons:false});
      const value=await request(kind==='report'?'reports/empirical':'lab/experiments',{method:'POST',headers:{'Content-Type':'application/json'},body:definition});
      if(life!==lifetime)return;
      if(kind==='report'&&current===reportVersion){reportID=value.id;publish({report:value,reportError:'',loadingReport:false});}
      if(kind==='experiment'&&current===runVersion){
        runID=value.id;comparisonVersion++;
        publish({run:value,comparisons:[],runError:'',comparisonError:'',loadingRun:false,loadingComparisons:false});
        try{remember(value.id);}catch(failure){console.warn('Tangerine experiment restore preference',{kind:failure.name||'UnknownError'});}
      }
      if(action===actionVersion)publish({notice:kind==='report'?'Report saved.':'Experiment saved. Run it when you choose.'});
      // The saved-list owner observes this refresh; a slow list cannot hold Save.
      (kind==='report'?refreshReports:refreshExperiments)();
    }catch(failure){if(life===lifetime&&action===actionVersion)publish({actionError:requestError(failure)});}
    finally{writes.delete(write);if(life===lifetime)publish({busy:writes.size>0});}
  }
  async function runAction(kind) {
    if(!state.run)return;
    const id=state.run.id,selected=runVersion,life=lifetime,action=++actionVersion,write=Symbol(kind);
    writes.add(write);publish({busy:true,actionError:'',notice:''});
    try {
      await request('lab/experiments/'+id+':'+kind,{method:'POST',headers:{'Content-Type':'application/json'},body:'{}'});
      if(life===lifetime&&selected===runVersion)return loadRun(id);
    }catch(failure){if(life===lifetime&&action===actionVersion&&selected===runVersion)publish({actionError:requestError(failure)});}
    finally{writes.delete(write);if(life===lifetime)publish({busy:writes.size>0});}
  }
  return {
    loadReport,loadRun,runAction,
    createReport:definition=>save('report',definition),admit:definition=>save('experiment',definition),
    refresh:()=>Promise.all([refreshReports(),refreshExperiments(),reportID?loadReport(reportID):null,runID?loadRun(runID):null]),
    retryComparisons:()=>state.run?loadComparisons(state.run):Promise.resolve(),
    cancel(){lifetime++;reportVersion++;runVersion++;comparisonVersion++;actionVersion++;writes.clear();},
  };
}
