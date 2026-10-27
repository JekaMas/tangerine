// Actual installed Chrome against an owned Next/API/DB/MinIO source fixture.
// Only labelled HTTP failure/delay cases substitute transport responses.
const assert=require('node:assert/strict');
const fs=require('node:fs');const path=require('node:path');
const {chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE);
const base=process.env.TANGERINE_JFLEG_BROWSER_URL,out=process.env.TANGERINE_JFLEG_EVIDENCE;
const fixture=JSON.parse(fs.readFileSync(process.env.TANGERINE_JFLEG_FIXTURE));
const expected=JSON.parse(fs.readFileSync(process.env.TANGERINE_JFLEG_NATIVE_EXPECTED||path.join(out,'../native-expected.json')));
(async()=>{
 fs.mkdirSync(path.join(out,'video'),{recursive:true});fs.mkdirSync(path.join(out,'downloads'),{recursive:true});
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:720},recordVideo:{dir:path.join(out,'video'),size:{width:1280,height:720}},acceptDownloads:true});
 const page=await context.newPage();const errors=[],calls=[];page.on('pageerror',e=>errors.push(e.message));page.on('response',r=>{if(r.url().includes('/api/'))calls.push({url:r.url(),status:r.status(),method:r.request().method()});});
 const actual={fixture,driver:require(process.env.TANGERINE_PLAYWRIGHT_MODULE+'/package.json').version,rendering_substitution:false,transport_failure_cases:true};
 const mode=async name=>{const r=await fetch(base+'/__test/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:name,remaining:name==='transient'?1:0})});assert.equal(r.status,200)};
 const screenshot=async name=>{await page.screenshot({path:path.join(out,name+'.png')});fs.writeFileSync(path.join(out,name+'.html'),await page.content());};
 const refresh=async region=>{await Promise.all([page.waitForResponse(r=>r.url().includes('/corrections?limit=20')&&r.status()===200),region.getByRole('button',{name:'Refresh correction examples',exact:true}).click()]);};
 try {
  await page.goto(base+'/sources',{waitUntil:'networkidle'});
  assert.equal(await page.locator('[aria-label="Source status"] > li').count(),12);actual.source_cards=12;
  const card=page.locator('[aria-label="Source status"] > li').filter({has:page.getByRole('heading',{name:'JFLEG',exact:true})});
  if(process.env.TANGERINE_JFLEG_VERIFY_FIXTURES){assert.match(await card.textContent(),/Saved release is incomplete/);actual.status='latest_constructed_partial';}
  else{assert.match(await card.textContent(),/Complete source release retained/);actual.status='complete';}
  assert.equal(await page.getByRole('region',{name:'Written correction examples',exact:true}).count(),0);actual.no_example_before_selection=true;
  await card.getByRole('button',{name:'Open saved release '+fixture.release_id,exact:true}).click();
  assert.match(await page.getByRole('region',{name:'Import report',exact:true}).textContent(),/Raw complete: true · normalized complete: true/);actual.selected_full_import_complete=true;
  const region=page.getByRole('region',{name:'Written correction examples',exact:true});
  await region.locator(':scope > details').first().waitFor();await page.waitForFunction(()=>document.querySelectorAll('[aria-label="Written correction examples"] > details').length===20);
  actual.initial_examples=20;
  const first=region.locator(':scope > details').first();const summary=first.locator(':scope > summary');
  await summary.focus();await page.keyboard.press('Enter');assert.equal(await first.evaluate(e=>e.open),true);actual.keyboard_disclosure=true;
  const focused=await summary.evaluate(e=>{const s=getComputedStyle(e);return {focused:document.activeElement===e,outline:s.outlineStyle,width:s.outlineWidth}});assert.equal(focused.focused,true);assert.notEqual(focused.outline,'none');actual.focus=focused;
  assert.equal(await first.locator(':scope > p').first().textContent(),expected.lines['dev/dev.src'][0]);assert.equal(await first.locator('ol > li').count(),4);
  for(let i=0;i<4;i++)assert.equal(await first.locator('ol > li').nth(i).locator('p').textContent(),expected.lines['dev/dev.ref'+i][0]);
  actual.visible_original=expected.lines['dev/dev.src'][0];actual.visible_references=[0,1,2,3].map(i=>expected.lines['dev/dev.ref'+i][0]);
  await first.getByText('Separate source spellcheck',{exact:true}).click();assert.equal(await first.locator('details').first().locator('p').first().textContent(),expected.lines['dev/dev.spellchecked.src'][0]);actual.spellcheck_separate=true;
  await first.getByText('Derived text differences and provenance',{exact:true}).click();assert.match(await first.locator('pre').textContent(),/not_computed/);assert.match(await first.locator('pre').textContent(),/not_supplied/);actual.provenance_disclosed=true;
  await first.getByText('Derived text differences and provenance',{exact:true}).click();
  await region.getByRole('heading',{name:'Written correction examples',exact:true}).scrollIntoViewIfNeeded();await page.evaluate(()=>window.scrollBy(0,-100));await screenshot('desktop-examples');
  const downloads={};
  for(const [part,title,count] of [['dev','Download development dataset',754],['test','Download test dataset',747]]) {
   const [download]=await Promise.all([page.waitForEvent('download'),region.getByRole('button',{name:title,exact:true}).click()]);const filename=path.join(out,'downloads',download.suggestedFilename());await download.saveAs(filename);const dataset=JSON.parse(fs.readFileSync(filename));
   assert.equal(dataset.examples.length,count);assert.equal(dataset.source_version,'ee06ff806a208aba815ac45313f4e750a48330a5');assert.equal(dataset.licence,'CC-BY-NC-SA-4.0');
   for(let i=0;i<count;i++){assert.equal(dataset.examples[i].original.text,expected.lines[part+'/'+part+'.src'][i]);assert.equal(dataset.examples[i].references.length,4);for(let j=0;j<4;j++)assert.equal(dataset.examples[i].references[j].text,expected.lines[part+'/'+part+'.ref'+j][i]);}
   downloads[part]={examples:count,reference_positions:count*4,filename:path.basename(filename)};
  }
  actual.downloads=downloads;
  await region.getByRole('button',{name:'More correction examples',exact:true}).click();await page.waitForFunction(()=>document.querySelectorAll('[aria-label="Written correction examples"] > details').length===40);actual.paginated_examples=40;
  await mode('loading');const waiting=page.waitForResponse(r=>r.url().includes('/corrections?limit=20')&&r.status()===200);await region.getByRole('button',{name:'Refresh correction examples',exact:true}).click();await region.getByText('Reading saved correction examples…',{exact:true}).waitFor();assert.equal(await region.locator(':scope > details').count(),40);actual.loading_retains_examples=true;await waiting;await mode('normal');
  await page.waitForFunction(()=>document.querySelectorAll('[aria-label="Written correction examples"] > details').length===20);
  await mode('transient');const from=calls.length;await refresh(region);await page.waitForTimeout(100);const transient=calls.slice(from).filter(r=>r.url.includes('/corrections'));assert.deepEqual(transient.map(r=>r.status),[503,200]);assert.equal(await region.locator('[role="alert"]').count(),0);actual.transient_statuses=transient.map(r=>r.status);
  await mode('unavailable');const failureStart=calls.length;await region.getByRole('button',{name:'Refresh correction examples',exact:true}).click();await region.getByRole('alert').waitFor();assert.equal(await region.locator(':scope > details').count(),20);const error=await region.getByRole('alert').textContent();assert.equal(error,'The source service is temporarily unavailable. Your files and progress are retained. Refresh to continue.');assert.equal(await region.getByRole('button',{name:'Refresh correction examples',exact:true}).isEnabled(),true);assert.doesNotMatch(await page.locator('main').textContent(),/INTERNAL_CANARY|traceback/);assert.deepEqual(calls.slice(failureStart).filter(r=>r.url.includes('/corrections')).map(r=>r.status),[503,503,503]);actual.failure={message:error,retained_examples:20,refresh_enabled:true,raw_payload_absent:true};await region.getByRole('alert').scrollIntoViewIfNeeded();await screenshot('safe-recovery');
  await mode('normal');await refresh(region);await page.waitForFunction(()=>document.querySelectorAll('[aria-label="Written correction examples"] [role="alert"]').length===0);actual.recovered=true;
  await page.reload({waitUntil:'networkidle'});await page.waitForFunction(()=>document.querySelectorAll('[aria-label="Written correction examples"] > details').length===20);assert.equal(await page.getByLabel('Source',{exact:true}).inputValue(),'JFLEG');const locator=await page.evaluate(()=>JSON.parse(localStorage.getItem('tangerine-source-import')));assert.equal(locator.releaseId,fixture.release_id);assert.equal(locator.importId,fixture.import_id);assert.equal(locator.files,undefined);actual.reload_same_import=true;actual.compact_locator_bytes=JSON.stringify(locator).length;
  actual.layouts=[];
  for(const [width,height] of [[1280,720],[390,844],[320,740]]) {
   await page.setViewportSize({width,height});await page.evaluate(()=>document.fonts.ready);const open=region.locator(':scope > details').first();if(!await open.evaluate(e=>e.open))await open.locator(':scope > summary').click();
   await region.getByRole('heading',{name:'Written correction examples',exact:true}).scrollIntoViewIfNeeded();await page.evaluate(()=>window.scrollBy(0,-110));
   const layout=await region.evaluate(e=>{const p=e.querySelector('details > p'),style=getComputedStyle(p),button=e.querySelector('button'),b=getComputedStyle(button);return {viewport:innerWidth,document_width:document.documentElement.scrollWidth,font:style.fontFamily,font_size:style.fontSize,line_height:style.lineHeight,fonts_loaded:document.fonts.check('17px "Source Sans 3"'),button_font_size:b.fontSize,body_measure:p.getBoundingClientRect().width,button_height:button.getBoundingClientRect().height}});
   assert.equal(layout.document_width,width);assert.equal(layout.font_size,'17px');assert.equal(layout.line_height,'24.65px');assert.equal(layout.fonts_loaded,true);assert.ok(layout.button_height>=44);actual.layouts.push(layout);await screenshot('examples-'+width);
  }
  assert.deepEqual(errors,[]);actual.page_errors=errors;assert.ok(calls.length>10);assert.ok(calls.every(r=>r.method==='GET'));actual.application_methods=[...new Set(calls.map(r=>r.method))];actual.application_requests=calls.length;actual.no_model_or_write_requests=calls.every(r=>!/(generate|submit|:run|:render)/.test(r.url));assert.equal(actual.no_model_or_write_requests,true);
  fs.writeFileSync(path.join(out,'observations.json'),JSON.stringify(actual,null,2)+'\n');
 } finally {
  fs.writeFileSync(path.join(out,'final.html'),await page.content());await context.close();await browser.close();
 }
 console.log('Actual JFLEG browsing, both complete downloads, recovery, keyboard and three layouts passed.');
})().catch(error=>{console.error(error.stack||String(error));process.exitCode=1;});
