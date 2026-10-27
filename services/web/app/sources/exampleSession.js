import {requestError} from '../requestError.js';

export const emptyExamples=()=>({items:[],cursor:'',loading:false,error:''});
// One owner for saved-example read ordering. Refresh remains available; an old
// response cannot replace the selected import or a newer page.
export function createExampleSession({importId,view='',request,publish}) {
 let state=emptyExamples(),ticket=0,active=true;
 const update=value=>{state={...state,...value};publish(value)};
 return {
  async load(more=false){
   const current=++ticket,previous=state.items,cursor=more?state.cursor:'';
   update({loading:true,error:''});
   try{
    const {body}=await request('imports/'+importId+'/examples?limit=20'+(view?'&view='+encodeURIComponent(view):'')+(cursor?'&cursor='+encodeURIComponent(cursor):''));
    if(active&&current===ticket)update({items:more?[...previous,...body.items]:body.items,cursor:body.next_cursor||''});
   }catch(error){if(active&&current===ticket)update({error:requestError(error)})}
   finally{if(active&&current===ticket)update({loading:false})}
  },
  dispose(){active=false;ticket++},
 };
}
