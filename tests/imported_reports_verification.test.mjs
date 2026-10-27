import assert from 'node:assert/strict';
import test from 'node:test';
import {reportRequest} from '../services/web/app/reports/request.js';
import {readableMetric} from '../services/web/app/reports/sourcePresentation.js';

test('Zero denominator guidance does not falsely claim missing sentence annotations',()=>{
  const shown=readableMetric({numerator:'0',denominator:'0',exact:null,missing_reason:'no_inspected_denominator'});
  assert.equal(shown.value,'Not measured');
  assert.equal(shown.basis,'No eligible observations were counted for this measurement.');
});

test('Rejected input and failed saves use different authored recovery, without replaying writes',async()=>{
  const original=globalThis.fetch;
  const calls=[];
  try {
    for(const status of [400,503]) {
      globalThis.fetch=async(path,options)=>{calls.push({path,method:options.method});return new Response('{"error":"PRIVATE_DATABASE_CANARY"}',{status});};
      const failure=await reportRequest('reports/empirical',{method:'POST',body:'{}'}).catch(error=>error);
      assert(failure instanceof Error);
      assert(!failure.message.includes('PRIVATE_DATABASE_CANARY'));
      if(status===400)assert.equal(failure.message,'Check your selections and try again. Your input and saved reports are retained.');
      else assert.equal(failure.message,'We couldn’t confirm that this report was saved. Your inputs and earlier reports are retained. Refresh saved reports to check whether it was saved before trying again.');
    }
    assert.equal(calls.length,2,'An ambiguous save must not be automatically replayed.');
    assert(calls.every(call=>call.method==='POST'));
  } finally {globalThis.fetch=original;}
});
