"""Literal ordered counterexamples through the production session/file owners."""
import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NODE = Path.home() / '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node'


class ReportsSession(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        script = """
import {createReportsSession} from './services/web/app/reports/session.js';
import {createDefinitionFile} from './services/web/app/reports/definitionFile.js';
import {metricDisplay} from './services/web/app/reports/metricDisplay.js';
import {reportRequest} from './services/web/app/reports/request.js';
const deferred=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject}};
function make(options={}){
 let state,events=0;const calls=[],pending=[],remembered=[],refreshes=[];
 const owner=createReportsSession({onChange:v=>{state=v;events++},request:(path,options)=>{const d=deferred();calls.push({path,options});pending.push(d);return d.promise},refreshReports:()=>{refreshes.push('report');return options.listPromise||Promise.resolve()},refreshExperiments:()=>{refreshes.push('experiment');return options.listPromise||Promise.resolve()},remember:id=>{if(options.rememberFailure)throw Error('private browser detail');remembered.push(id)}});
 return {owner,calls,pending,remembered,refreshes,get state(){return state},get events(){return events}};
}
const run=(id,comparison=null)=>({id,comparison_asset_id:comparison,status:'planned',rows:[]});
const out={};let f=make(),p=f.owner.loadReport('one');f.pending[0].reject(Error('private backend detail'));await p;
out.failedReport={...f.state};p=f.owner.refresh();out.retryPaths=f.calls.map(c=>c.path);f.pending[1].resolve({id:'one',title:'Saved report'});await p;out.recoveredReport={...f.state};
f=make({listPromise:deferred().promise});p=f.owner.loadRun('one');f.pending[0].resolve(run('one'));await p;
p=f.owner.refresh();let newer=f.owner.loadRun('two');f.pending[2].resolve(run('two'));await newer;f.pending[1].resolve(run('one'));await Promise.resolve();out.refreshRace={...f.state};
f=make();p=f.owner.loadRun('one','unused');f.pending[0].resolve(run('one','pairs'));await Promise.resolve();out.essentialBeforePairs={...f.state};f.pending[1].reject(Error('private backend detail'));await p;out.pairsFailure={...f.state};p=f.owner.retryComparisons();out.pairRetryPaths=f.calls.map(c=>c.path);f.pending[2].resolve([{variant:'baseline',value:'1/2'}]);await p;out.pairsRecovered={...f.state};
p=f.owner.loadRun('one');f.pending[3].resolve(run('one','pairs'));await Promise.resolve();f.pending[4].reject(Error('temporary'));await p;out.retainedPairs={...f.state};
f=make();p=f.owner.loadRun('one');f.pending[0].resolve(run('one','pairs'));await Promise.resolve();newer=f.owner.loadRun('two');f.pending[2].resolve(run('two'));await newer;f.pending[1].reject(Error('obsolete'));await p;out.oldPairs={...f.state};
f=make({listPromise:deferred().promise});p=f.owner.createReport('{"title":"One"}');f.pending[0].resolve({id:'saved',title:'One'});await p;out.savedWithoutList={...f.state,refreshes:f.refreshes};
f=make();p=f.owner.createReport('{"title":"One"}');newer=f.owner.createReport('{"title":"Two"}');f.pending[1].resolve({id:'two'});await newer;out.secondSavedBusy=f.state.busy;f.pending[0].resolve({id:'one'});await p;out.lastSave={...f.state,calls:f.calls};
f=make();p=f.owner.loadReport('one');await f.owner.createReport('{');f.pending[0].resolve({id:'one'});await p;out.invalidWhileReading={...f.state,calls:f.calls};
f=make();p=f.owner.loadReport('one');newer=f.owner.createReport('{}');f.pending[1].reject(Error('write unavailable'));await newer;f.pending[0].reject(Error('old read'));await p;out.failedWrite={...f.state};
f=make();p=f.owner.loadRun('one');f.pending[0].resolve(run('one'));await p;p=f.owner.loadRun('two');f.pending[1].reject(Error('not available'));await p;p=f.owner.refresh();out.failedSelectionRetry=f.calls.map(c=>c.path);f.pending[2].resolve(run('two'));await p;
f=make();p=f.owner.loadRun('one');f.pending[0].resolve(run('one'));await p;p=f.owner.runAction('cancel');newer=f.owner.loadRun('two');f.pending[2].resolve(run('two'));await newer;f.pending[1].resolve({});await p;out.lateAction={...f.state,calls:f.calls};
f=make();p=f.owner.loadReport('one');newer=f.owner.createReport('{}');f.owner.cancel();const before=f.events;f.pending[0].resolve({id:'one'});f.pending[1].resolve({id:'saved'});await Promise.all([p,newer]);out.disposedEvents=f.events-before;
f=make({rememberFailure:true});p=f.owner.loadRun('one');f.pending[0].resolve(run('one'));await p;out.browserPreference={...f.state};
let value='Retained definition',error='',fileEvents=0;
const files=createDefinitionFile({onValue:v=>{value=v;fileEvents++},onError:v=>{error=v;fileEvents++}});
let old=deferred();p=files.read({text:()=>old.promise});let next=deferred();newer=files.read({text:()=>next.promise});next.resolve('New file');await newer;old.resolve('Old file');await p;out.fileOrder=value;
old=deferred();p=files.read({text:()=>old.promise});files.edit('Typed definition');old.resolve('Late file');await p;out.typedWins=value;
await files.read({text:()=>Promise.reject(Error('private file path'))});out.fileFailure={value,error};
await files.read({text:()=>Promise.resolve('Retry file')});out.fileRecovery={value,error};
old=deferred();p=files.read({text:()=>old.promise});files.edit('Keep this');old.reject(Error('late private failure'));await p;out.fileOldFailure={value,error};
old=deferred();p=files.read({text:()=>old.promise});files.cancel();const fileBefore=fileEvents;old.resolve('Disposed');await p;out.fileDisposeEvents=fileEvents-fileBefore;
out.metricValues=[{missing_reason:'leaf_annotation_scope_not_declared'},{missing_reason:'correct_opportunity_annotations_absent'},{missing_reason:'private backend detail'},{exact:{numerator:'1',denominator:'2'}},{numerator:'125',denominator:'1'},null].map(metricDisplay);
globalThis.fetch=async()=>({ok:false,status:404,headers:new Headers()});
try{await reportRequest('lab/experiments/missing')}catch(e){out.missingItem=e.message}
console.log(JSON.stringify(out));
"""
        result = subprocess.run([str(NODE), '--input-type=module', '-e', script], cwd=ROOT,
                                capture_output=True, text=True, timeout=20)
        if result.returncode:
            raise AssertionError(result.stderr)
        cls.v = json.loads(result.stdout)

    def test_failed_report_retry_positive(self):
        self.assertEqual(['reports/empirical/one'] * 2, self.v['retryPaths'])
        self.assertEqual('one', self.v['recoveredReport']['report']['id'])
        self.assertEqual('', self.v['recoveredReport']['reportError'])
        self.assertFalse(self.v['failedReport']['busy'])
        self.assertNotIn('private', self.v['failedReport']['reportError'])

    def test_refresh_new_selection_negative(self):
        self.assertEqual('two', self.v['refreshRace']['run']['id'])
        self.assertFalse(self.v['refreshRace']['busy'])

    def test_comparison_isolation_positive(self):
        c = self.v['essentialBeforePairs']
        self.assertEqual('one', c['run']['id'])
        self.assertFalse(c['loadingRun'])
        self.assertFalse(c['busy'])
        self.assertTrue(c['loadingComparisons'])
        self.assertEqual('', self.v['pairsFailure']['runError'])
        self.assertIn('The saved experiment remains usable.', self.v['pairsFailure']['comparisonError'])

    def test_comparison_retry_positive(self):
        self.assertEqual(['lab/experiments/one', 'lab/assets/pairs', 'lab/assets/pairs'], self.v['pairRetryPaths'])
        self.assertEqual([{'variant': 'baseline', 'value': '1/2'}], self.v['pairsRecovered']['comparisons'])
        self.assertEqual('', self.v['pairsRecovered']['comparisonError'])
        self.assertEqual(self.v['pairsRecovered']['comparisons'], self.v['retainedPairs']['comparisons'])

    def test_old_comparison_negative(self):
        c = self.v['oldPairs']
        self.assertEqual('two', c['run']['id'])
        self.assertEqual([], c['comparisons'])
        self.assertEqual('', c['comparisonError'])

    def test_saved_before_list_positive(self):
        c = self.v['savedWithoutList']
        self.assertFalse(c['busy'])
        self.assertEqual('saved', c['report']['id'])
        self.assertEqual('Report saved.', c['notice'])
        self.assertEqual(['report'], c['refreshes'])

    def test_concurrent_save_delivery_negative(self):
        self.assertTrue(self.v['secondSavedBusy'])
        c = self.v['lastSave']
        self.assertFalse(c['busy'])
        self.assertEqual('two', c['report']['id'])
        self.assertEqual(['POST', 'POST'], [x['options']['method'] for x in c['calls']])

    def test_invalid_definition_keeps_read_negative(self):
        c = self.v['invalidWhileReading']
        self.assertEqual('one', c['report']['id'])
        self.assertFalse(c['loadingReport'])
        self.assertIn('not valid JSON', c['actionError'])
        self.assertEqual(1, len(c['calls']))

    def test_failed_write_ends_progress_negative(self):
        c = self.v['failedWrite']
        self.assertFalse(c['busy'])
        self.assertFalse(c['loadingReport'])
        self.assertEqual('', c['reportError'])
        self.assertNotIn('private', c['actionError'])

    def test_failed_selected_run_retry_positive(self):
        self.assertEqual(['lab/experiments/one', 'lab/experiments/two', 'lab/experiments/two'], self.v['failedSelectionRetry'])

    def test_old_action_readback_negative(self):
        c = self.v['lateAction']
        self.assertEqual('two', c['run']['id'])
        self.assertEqual(['lab/experiments/one', 'lab/experiments/one:cancel', 'lab/experiments/two'], [x['path'] for x in c['calls']])
        self.assertFalse(c['busy'])

    def test_disposal_negative(self):
        self.assertEqual(0, self.v['disposedEvents'])
        self.assertEqual(0, self.v['fileDisposeEvents'])

    def test_browser_preference_failure_negative(self):
        self.assertEqual('one', self.v['browserPreference']['run']['id'])
        self.assertEqual('', self.v['browserPreference']['runError'])

    def test_file_order_negative(self):
        self.assertEqual('New file', self.v['fileOrder'])
        self.assertEqual('Typed definition', self.v['typedWins'])
        self.assertEqual({'value': 'Keep this', 'error': ''}, self.v['fileOldFailure'])

    def test_file_recovery_positive(self):
        self.assertEqual('Typed definition', self.v['fileFailure']['value'])
        self.assertIn('Choose the file again or paste it below.', self.v['fileFailure']['error'])
        self.assertNotIn('private', self.v['fileFailure']['error'])
        self.assertEqual({'value': 'Retry file', 'error': ''}, self.v['fileRecovery'])

    def test_authored_metric_display_positive(self):
        self.assertEqual(['Not annotated', 'Correct-use observations needed', 'Not available', '1/2', '125/1', 'Not observed'], self.v['metricValues'])

    def test_missing_item_guidance_negative(self):
        self.assertEqual('This saved item is no longer available. Choose another saved item or create a new one.', self.v['missingItem'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
