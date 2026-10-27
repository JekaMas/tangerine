// Actual installed Chrome + production Next/API and retained full official data.
// Only gateway failure responses are controlled; no UI or successful data mocks.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.TANGERINE_TEST_PLAYWRIGHT_MODULE);
const root=process.cwd(),out=path.join(root,'data/iteration-35-verification-20261027/browser');
const server=JSON.parse(fs.readFileSync(path.join(out,'server.json'))),base=server.url;
const release='8c5cda52-e8aa-4baf-8495-d4a2efb3918e',run='8cd233c7-1999-44c9-9ed7-e0519f375f4d';
const continuing=process.argv.includes('--recovery-only');
const observations=continuing?JSON.parse(fs.readFileSync(path.join(out,'before-request-log-repair/observations.json'))):{},logs=[],errors=[];let browser,page;
delete observations.status;delete observations.error;
const mode=(scenario,value)=>fs.writeFileSync(path.join(out,'control.json'),JSON.stringify({scenario,mode:value}));
const wait=async(fn)=>{for(let i=0;i<150;i++){if(await fn())return;await new Promise(r=>setTimeout(r,100))}throw Error('Expected browser state not reached')};
async function capture(label){await page.screenshot({path:path.join(out,label+'.png')});fs.writeFileSync(path.join(out,label+'.html'),await page.content());}
(async()=>{
 fs.mkdirSync(path.join(out,'videos'),{recursive:true});
 browser=await chromium.launchPersistentContext(path.join(out,'chrome-profile'),{executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,viewport:{width:1280,height:720},recordVideo:{dir:path.join(out,'videos'),size:{width:1280,height:720}},acceptDownloads:true});
 page=browser.pages()[0]||await browser.newPage();page.on('console',m=>logs.push({type:m.type(),text:m.text()}));page.on('pageerror',e=>errors.push(String(e)));
 if(!continuing){
 mode('normal-initial','normal');await page.goto(base+'/sources');await page.getByRole('heading',{name:'L2-ARCTIC',exact:true}).waitFor();
 const item=page.getByRole('heading',{name:'L2-ARCTIC',exact:true}).locator('..');
 await wait(async()=> (await item.innerText()).includes('Complete source release retained'));
 assert.match(await item.innerText(),/original files: retained · converted records: ready · unconverted records:\s*0/);
 observations.sourceStatus={source:'L2-ARCTIC',text:await item.innerText()};
 await item.scrollIntoViewIfNeeded();await capture('01-full-source-status');
 mode('loading-release','loading');const click=page.getByRole('button',{name:'Open saved release '+release}).click();
 await page.getByRole('status').filter({hasText:'Working on the selected source'}).waitFor();await capture('02-loading');await click;
 const report=page.getByRole('region',{name:'Import report'});await report.getByRole('heading',{name:'Import report',exact:true}).waitFor({timeout:60000});
 await wait(async()=> (await report.innerText()).includes('accepted: 1574840'));
 observations.report=await report.innerText();assert.match(observations.report,/Observed: 1574840 · accepted: 1574840 · quarantined: 0 · rejected: 0 · raw only: 0/);assert.match(observations.report,/Raw complete: true · normalized complete: true/);
 await report.scrollIntoViewIfNeeded();await capture('03-full-import-report');
 mode('normal-rows','normal');let rows=report.locator(':scope > details');await wait(async()=>await rows.count()===20);
 observations.initialRows=await rows.locator('summary').allInnerTexts();
 await rows.first().locator('summary').click();await rows.first().scrollIntoViewIfNeeded();await capture('04-native-row');
 const downloadEvent=page.waitForEvent('download');await rows.first().getByRole('link',{name:'Download original bytes'}).click();const download=await downloadEvent;await download.saveAs(path.join(out,'downloaded-original.TextGrid'));
 const original=fs.readFileSync(path.join(out,'downloaded-original.TextGrid'),'utf8');assert.match(original,/ooTextFile/);assert.match(original,/TextGrid/);observations.originalDownload={name:download.suggestedFilename(),bytes:Buffer.byteLength(original),textGrid:true};
 await report.getByRole('button',{name:'More source rows',exact:true}).click();await wait(async()=>await rows.count()===40);observations.afterMore=await rows.locator('summary').allInnerTexts();assert.equal(new Set(observations.afterMore).size,40);assert.deepEqual(observations.afterMore.slice(0,20),observations.initialRows);
 await report.getByRole('button',{name:'Read saved issue history'}).click();await report.getByRole('heading',{name:'Saved issue history'}).waitFor();await report.getByRole('heading',{name:'Saved issue history'}).scrollIntoViewIfNeeded();await capture('05-history');
 observations.cache=await page.evaluate(()=>({size:(localStorage.getItem('tangerine-source-import')||'').length,value:JSON.parse(localStorage.getItem('tangerine-source-import')||'null')}));
 assert.ok(observations.cache.size<300);assert.deepEqual(observations.cache.value,{source:'L2-ARCTIC',releaseId:release,binding:'native',importId:run});
 mode('reload-retained','normal');await page.reload();await page.getByRole('heading',{name:'L2-ARCTIC',exact:true}).waitFor();
 for(let i=0;i<50&&await page.getByRole('region',{name:'Import report'}).count()===0;i++)await page.waitForTimeout(100);
 observations.reportRestored=await page.getByRole('region',{name:'Import report'}).count()===1;await capture('06-after-reload');
 if(!observations.reportRestored){observations.finding='Full official release selection is not restored after reload';throw Error(observations.finding)}
 }else{mode('resume-recovery','normal');await page.goto(base+'/sources');await page.getByRole('region',{name:'Import report'}).waitFor();await wait(async()=>await page.getByRole('region',{name:'Import report'}).locator(':scope > details').count()===20);}
 mode('transient-verified','transient');const recoveredRead=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/v1/sources'&&r.status()===200);await page.getByRole('button',{name:'Refresh sources',exact:true}).click();await recoveredRead;await wait(async()=>await page.locator('main [role="alert"]').count()===0);observations.transientRecovered=true;
 mode('unavailable-verified','unavailable');await page.getByRole('button',{name:'Refresh sources',exact:true}).click();await page.locator('main [role="alert"]').waitFor();assert.match(await page.locator('main [role="alert"]').innerText(),/Your files and progress are retained. Refresh to continue/);assert.doesNotMatch(await page.locator('body').innerText(),/PRIVATE_BACKEND_CANARY|SQL\/private|password trace/);assert.equal(await page.getByRole('region',{name:'Import report'}).count(),1);observations.failureText=await page.locator('main [role="alert"]').innerText();await page.getByRole('heading',{name:'Sources',exact:true}).scrollIntoViewIfNeeded();await capture('07-safe-error');
 mode('recovery-verified','normal');await page.getByRole('button',{name:'Refresh sources',exact:true}).focus();await page.keyboard.press('Enter');await wait(async()=>await page.locator('main [role="alert"]').count()===0);observations.keyboardRefresh=true;await capture('08-recovered');
 if(!continuing||!observations.typography){
 observations.typography=await page.locator('main p').first().evaluate(e=>{const s=getComputedStyle(e);return {font:s.fontFamily,size:s.fontSize,lineHeight:s.lineHeight,loaded:document.fonts.check('17px "Source Sans 3"')}});assert.equal(observations.typography.size,'17px');assert.equal(observations.typography.loaded,true);
 observations.layouts=[];for(const width of [390,320]){await page.setViewportSize({width,height:width===390?844:740});await page.evaluate(()=>scrollTo(0,0));await page.getByRole('button',{name:'Toggle navigation'}).click();assert.equal(await page.getByRole('button',{name:'Toggle navigation'}).getAttribute('aria-expanded'),'true');await capture('09-navigation-'+width);await page.getByRole('button',{name:'Toggle navigation'}).click();await page.getByRole('heading',{name:'L2-ARCTIC',exact:true}).scrollIntoViewIfNeeded();await capture('10-source-'+width);await page.getByRole('region',{name:'Import report'}).scrollIntoViewIfNeeded();await capture('11-report-'+width);const layout=await page.evaluate(()=>({width:innerWidth,scroll:document.documentElement.scrollWidth}));observations.layouts.push(layout);assert.ok(layout.scroll<=layout.width,JSON.stringify(layout));}
 }
 observations.noPageErrors=errors.length===0;assert.deepEqual(errors,[]);observations.status='passed';
})().catch(e=>{observations.status='failed';observations.error=String(e.stack||e);process.exitCode=1}).finally(async()=>{if(browser)await browser.close();fs.writeFileSync(path.join(out,'observations.json'),JSON.stringify({...observations,logs,errors,driver:require(process.env.TANGERINE_TEST_PLAYWRIGHT_MODULE+'/package.json').version,origin:'Actual Chrome on retained full official import, controlled transient/unavailable GET failures only; no import, synthesis or inference.'},null,2)+'\n');console.log(JSON.stringify({status:observations.status,error:observations.error,reportRestored:observations.reportRestored}));});
