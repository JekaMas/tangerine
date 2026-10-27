import {requestError} from '../requestError.js';

// This view owns its read order and its exports separately. Refresh supersedes
// an older page read; it never cancels an explicitly requested dataset download.
export const emptyCorrections=()=>({items:[],cursor:'',loading:false,downloading:false,readError:'',downloadError:'',notice:''});
export function createCorrectionSession({importId,request,publish,saveDownload}) {
 let state=emptyCorrections(),read=0,download=0,active=true;
 const update=value=>{state={...state,...value};publish(value)};
 return {
  async load(more=false){
   const ticket=++read,cursor=more?state.cursor:'',previous=state.items;
   update({loading:true,readError:''});
   try {
    const {body}=await request('imports/'+importId+'/corrections?limit=20'+(more?'&cursor='+encodeURIComponent(cursor):''));
    if(active&&ticket===read)update({items:more?[...previous,...body.items]:body.items,cursor:body.next_cursor||''});
   }catch(error){if(active&&ticket===read)update({readError:requestError(error)})}
   finally{if(active&&ticket===read)update({loading:false})}
  },
  async download(partition){
   const ticket=++download;
   update({downloading:true,downloadError:'',notice:''});
   try {
    const {body}=await request('imports/'+importId+'/corrections?format=dataset&partition='+partition);
    if(active&&ticket===download){
     saveDownload(body,partition);
     update({notice:body.examples.length+' '+(partition==='dev'?'development':'test')+' examples downloaded with their supplied references.'});
    }
   }catch(error){if(active&&ticket===download)update({downloadError:requestError(error)})}
   finally{if(active&&ticket===download)update({downloading:false})}
  },
  dispose(){active=false;read++;download++},
 };
}
