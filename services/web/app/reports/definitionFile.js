import {requestError} from '../requestError.js';

// Each editable definition owns its pending file read. Typed text wins immediately.
export function createDefinitionFile({onValue,onError}) {
  let version=0;
  return {
    async read(file) {
      const current=++version;
      if(!file)return;
      onError('');
      try{const text=await file.text();if(current===version)onValue(text);}
      catch(failure){if(current===version)onError(requestError(failure,'This file could not be read. Your definition is retained. Choose the file again or paste it below.'));}
    },
    edit(text){version++;onError('');onValue(text);},
    cancel(){version++;},
  };
}
