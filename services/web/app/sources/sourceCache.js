// This is only a convenience cache. Actual releases, imports and connectors
// remain in the database; unavailable browser storage must not report failure
// after the real operation succeeded.
export function createSourceCache({storage=()=>window.localStorage,log=value=>console.warn('Tangerine source selection cache',value)}={}) {
  return {
    read(key) {
      try { const value=storage().getItem(key);return value?JSON.parse(value):null; }
      catch (error) { log({kind:error.name});return null; }
    },
    write(key,value) {
      try { if(value===null)storage().removeItem(key);else storage().setItem(key,JSON.stringify(value)); }
      catch (error) { log({kind:error.name}); }
    },
  };
}

export const sourceCache=createSourceCache();
