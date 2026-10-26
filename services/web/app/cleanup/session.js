import {requestError} from '../requestError.js';

// One selection owns its preview/confirmation. API owns dependency and erasure rules.
export function createCleanupSession({request,onChange}) {
  let state={ids:'',plan:null,confirmed:false,pending:null,error:'',scope:''},version=0;
  const publish=change=>{state={...state,...change};onChange(state);};
  async function execute(apply=false,orphans=false) {
    if(apply&&(!state.confirmed||state.plan?.state!=='preview'||state.plan.blocked.length))return;
    const current=++version,{ids,plan,scope}=state;
    publish({pending:apply?'apply':'preview',error:'',confirmed:false});
    try {
      const value=await request({apply,orphans,ids,plan});
      if(current===version)publish({plan:value,scope:apply?scope:orphans?'Old unlinked media':'Selected saved records'});
    } catch(failure) {
      const message=requestError(failure,'The cleanup outcome could not be confirmed. Your selection is retained. Refresh the preview before retrying.');
      if(current===version)publish({error:message});
    } finally {if(current===version)publish({pending:null});}
  }
  return {
    select(ids){version++;publish({ids,plan:null,confirmed:false,pending:null,error:'',scope:''});},
    confirm(confirmed){publish({confirmed});},
    preview:(orphans=false)=>execute(false,orphans),
    apply:()=>execute(true),
    cancel(){version++;},
  };
}
