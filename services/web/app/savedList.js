import {requestError} from './requestError.js';

export const emptySavedList = () => ({items:[], cursor:null, loaded:false, loading:false, error:''});

// One owner for saved-list read ordering and retention. A late read cannot
// replace newer records, guidance or loading state. No write is retried here.
export function createSavedList({onChange, unavailable}) {
  let state=emptySavedList(), current=0;
  const publish=change => {state={...state,...change};onChange(state);};
  return {
    async read(load, append=false) {
	  // A button may pass its click event through a refresh callback. Only the
	  // explicit pagination flag appends; Refresh always replaces the page.
	  append=append===true;
      const request=++current, cursor=append?state.cursor:null;
      publish({loading:true,error:''});
      try {
        const page=await load(cursor);
        if (request!==current) return;
        publish({items:append?[...state.items,...page.items]:page.items,cursor:page.cursor||null,loaded:true});
      } catch(error) {
        const message=requestError(error,unavailable);
        if (request===current) publish({error:message});
      } finally {
        if (request===current) publish({loading:false});
      }
    },
    cancel() {current++;},
  };
}
