import assert from 'node:assert/strict';
import test from 'node:test';
import {createSavedList} from '../services/web/app/savedList.js';
import {readableMetric,nativeName,categoryName} from '../services/web/app/reports/sourcePresentation.js';
import {reportFromPopulation} from '../services/web/app/reports/starters.js';

test('Refresh click replaces old records even with an event argument',async()=>{
 let state;const seen=[];const list=createSavedList({onChange:s=>state=s});
 await list.read(async cursor=>{seen.push(cursor);return {items:['old'],cursor:'next'}});
 await list.read(async cursor=>{seen.push(cursor);return {items:[],cursor:null}},{type:'click'});
 assert.deepEqual(state.items,[]);assert.deepEqual(seen,[null,null]);assert.equal(state.error,'');
});
test('Explicit pagination appends, while failed reads retain saved records',async()=>{
 let state;const seen=[];const list=createSavedList({onChange:s=>state=s,unavailable:'Please retry.'});
 await list.read(async()=>({items:['first'],cursor:'page2'}));
 await list.read(async cursor=>{seen.push(cursor);return {items:['second'],cursor:null}},true);
 assert.deepEqual(seen,['page2']);assert.deepEqual(state.items,['first','second']);
 await list.read(async()=>{throw new TypeError('private database error')},{type:'click'});
 assert.deepEqual(state.items,['first','second']);assert(!state.error.includes('private'));
});
test('Measurements remain readable, distinguish zero and unknown, and retain rare positives',()=>{
 assert.deepEqual(readableMetric({numerator:'1',denominator:'4',exact:{numerator:'1',denominator:'4'}}),{value:'25%',basis:'1 out of 4'});
 assert.equal(readableMetric({numerator:'0',denominator:'4',exact:{numerator:'0',denominator:'1'}}).value,'0%');
 assert.equal(readableMetric({missing_reason:'correct_opportunity_annotations_absent'}).value,'Not measured');
 assert.equal(readableMetric({numerator:'1',denominator:'1000000',exact:{numerator:'1',denominator:'1000000'}}).value,'0.0001%');
 assert.equal(nativeName('R:VERB:SVA'),'Verb agreement — changed');assert.equal(nativeName('s'),'Phone substitution');
 assert.equal(categoryName('grammar.verbs.subject_verb_agreement',{'grammar.verbs.subject_verb_agreement':'Subject–verb agreement'}),'Subject–verb agreement');
});
test('Reuse sends a saved input identity instead of selecting current source rows',()=>{
 assert.deepEqual(reportFromPopulation(' Frozen observations ',null,'saved-input'),{title:'Frozen observations',reuse_input_asset_id:'saved-input'});
 const old={source:null,input:{population:{release:'constructed'}}};const clone=reportFromPopulation('Copy',old);clone.input.population.release='changed';assert.equal(old.input.population.release,'constructed');
});
