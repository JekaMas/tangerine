// Current browser + real saved source responses. Only the response order/delay
// below is controlled. No source, database, successful response or DOM is faked.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE);
const out=process.env.TANGERINE_JFLEG_EVIDENCE,base=process.env.TANGERINE_JFLEG_BROWSER_URL;
const fixture=JSON.parse(fs.readFileSync(process.env.TANGERINE_JFLEG_FIXTURE));
(async()=>{
 fs.mkdirSync(path.join(out,'video'),{recursive:true});
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:720},recordVideo:{dir:path.join(out,'video'),size:{width:1280,height:720}},acceptDownloads:true});
 const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
 const actual={fixture,scope:'Actual saved JFLEG; controlled response order only; zero model calls'};
 try {
  await page.goto(base+'/sources',{waitUntil:'networkidle'});
  await page.getByRole('button',{name:'Open saved release '+fixture.release_id,exact:true}).click();
  const region=page.getByRole('region',{name:'Written correction examples',exact:true});
  const examples=region.locator(':scope > details');await examples.last().waitFor();assert.equal(await examples.count(),20);
  let unblock,ready;const held=new Promise(r=>unblock=r),arrived=new Promise(r=>ready=r);
  await page.route('**/api/v1/imports/*/corrections?*',async route=>{
   if(new URL(route.request().url()).searchParams.has('cursor')){
    const response=await route.fetch();ready();await held;await route.fulfill({response});
   }else await route.continue();
  });
  await region.getByRole('button',{name:'More correction examples',exact:true}).click();await arrived;
  assert.equal(await region.getByRole('button',{name:'Refresh correction examples',exact:true}).isEnabled(),true);
  await Promise.all([page.waitForResponse(r=>r.url().includes('/corrections?limit=20')&&!new URL(r.url()).searchParams.has('cursor')&&r.status()===200),region.getByRole('button',{name:'Refresh correction examples',exact:true}).click()]);
  await region.getByText('Reading saved correction examples…',{exact:true}).waitFor({state:'hidden'});
  assert.equal(await examples.count(),20);
  const oldReply=page.waitForResponse(r=>r.url().includes('/corrections?limit=20')&&new URL(r.url()).searchParams.has('cursor'));unblock();await oldReply;
  await page.waitForTimeout(200);
  actual.after_superseded_more=await examples.count();actual.alerts=await region.getByRole('alert').allTextContents();actual.page_errors=errors;
  await region.getByRole('heading',{name:'Written correction examples',exact:true}).scrollIntoViewIfNeeded();
  await page.screenshot({path:path.join(out,'superseded-more.png')});
  fs.writeFileSync(path.join(out,'observations.json'),JSON.stringify(actual,null,2)+'\n');
  assert.equal(actual.after_superseded_more,20,'Refresh must supersede a pending More result');
  await page.unroute('**/api/v1/imports/*/corrections?*');
  await region.getByRole('button',{name:'More correction examples',exact:true}).click();
  await page.waitForFunction(()=>document.querySelectorAll('[aria-label="Written correction examples"] > details').length===40);
  actual.current_more_after_refresh=40;

  // A Refresh can finish before an explicitly requested download. It must not
  // falsely clear download progress or enable another simultaneous export.
  let releaseDownload,downloadReady;const delayed=new Promise(r=>releaseDownload=r),fetched=new Promise(r=>downloadReady=r);
  await page.route('**/api/v1/imports/*/corrections?format=dataset&partition=dev',async route=>{
   const response=await route.fetch();downloadReady();await delayed;await route.fulfill({response});
  });
  await region.getByRole('button',{name:'Download development dataset',exact:true}).click();await fetched;
  await Promise.all([page.waitForResponse(r=>r.url().includes('/corrections?limit=20')&&r.status()===200),region.getByRole('button',{name:'Refresh correction examples',exact:true}).click()]);
  await region.getByText('Reading saved correction examples…',{exact:true}).waitFor({state:'hidden'});
  await region.getByText('Preparing the saved reference dataset…',{exact:true}).waitFor();
  assert.equal(await region.getByRole('button',{name:'Download test dataset',exact:true}).isDisabled(),true);
  assert.equal(await region.getByRole('button',{name:'Refresh correction examples',exact:true}).isEnabled(),true);
  assert.equal(await examples.count(),20);actual.download_remains_pending_after_refresh=true;
  await region.getByRole('heading',{name:'Written correction examples',exact:true}).evaluate(e=>e.scrollIntoView({block:'start'}));await page.evaluate(()=>window.scrollBy(0,-100));
  await page.screenshot({path:path.join(out,'download-pending-after-refresh.png')});
  fs.mkdirSync(path.join(out,'downloads'),{recursive:true});
  const save=async download=>{const name=path.join(out,'downloads',download.suggestedFilename());await download.saveAs(name);return JSON.parse(fs.readFileSync(name))};
  const gotDownload=page.waitForEvent('download');releaseDownload();const dev=await save(await gotDownload);
  assert.equal(dev.examples.length,754);actual.development_download=754;await page.unroute('**/api/v1/imports/*/corrections?format=dataset&partition=dev');

  const mode=async name=>{const r=await fetch(base+'/__test/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:name,remaining:0})});assert.equal(r.status,200)};
  await mode('unavailable');await region.getByRole('button',{name:'Download test dataset',exact:true}).click();
  const failure=region.getByRole('alert');await failure.waitFor();
  assert.equal(await failure.textContent(),'The source service is temporarily unavailable. Your files and progress are retained. Refresh to continue.');
  assert.equal(await examples.count(),20);assert.equal(await region.getByRole('button',{name:'Download test dataset',exact:true}).isEnabled(),true);
  assert.doesNotMatch(await region.textContent(),/INTERNAL_CANARY|traceback/);actual.download_failure_retains_examples=20;
  await page.screenshot({path:path.join(out,'download-recovery.png')});
  await mode('normal');const nextDownload=page.waitForEvent('download');await region.getByRole('button',{name:'Download test dataset',exact:true}).click();const heldOut=await save(await nextDownload);
  assert.equal(heldOut.examples.length,747);assert.equal(await region.getByRole('alert').count(),0);actual.test_download_recovered=747;
  const baseline=JSON.parse(fs.readFileSync(process.env.TANGERINE_JFLEG_NATIVE_EXPECTED));
  for(const [part,dataset,count] of [['dev',dev,754],['test',heldOut,747]]){
   for(let i=0;i<count;i++){
    assert.equal(dataset.examples[i].original.text,baseline.lines[part+'/'+part+'.src'][i]);
    assert.equal(dataset.examples[i].references.length,4);
    for(let j=0;j<4;j++)assert.equal(dataset.examples[i].references[j].text,baseline.lines[part+'/'+part+'.ref'+j][i]);
   }
  }
  actual.downloaded_originals_checked=1501;actual.downloaded_references_checked=6004;

  const extra=JSON.parse(fs.readFileSync(process.env.TANGERINE_JFLEG_VERIFY_FIXTURES));actual.constructed_views={};
  for(const kind of ['partial','empty']){
   await page.getByRole('button',{name:'Open saved release '+extra[kind].release_id,exact:true}).click();
   if(kind==='partial'){
    await region.getByText('Development sentence 1 · 1 supplied reference',{exact:true}).waitFor();assert.equal(await examples.count(),2);
    const first=examples.first();await first.locator(':scope > summary').click();
    assert.equal(await first.locator(':scope > p').first().textContent(),'They goes . ');assert.equal(await first.locator('ol > li').count(),1);
    assert.equal(await first.locator('ol > li p').textContent(),'They go . ');assert.match(await region.textContent(),/partial import shows only the references it contains/);
   }else{
    await region.getByText('No converted written corrections are saved yet. Import or resume the selected release above.',{exact:true}).waitFor();assert.equal(await examples.count(),0);
   }
   assert.equal(await region.getByRole('button',{name:'Refresh correction examples',exact:true}).isEnabled(),true);
   actual.constructed_views[kind]={examples:await examples.count(),reference_count:kind==='partial'?1:0,refresh_enabled:true};
   for(const [width,height] of [[1280,720],[390,844],[320,740]]){
    await page.setViewportSize({width,height});await page.evaluate(()=>document.fonts.ready);
    await region.getByRole('heading',{name:'Written correction examples',exact:true}).evaluate(e=>e.scrollIntoView({block:'start'}));await page.evaluate(()=>window.scrollBy(0,-100));
    assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth),width);await page.screenshot({path:path.join(out,kind+'-'+width+'.png')});
   }
  }
  actual.page_errors=errors;
  fs.writeFileSync(path.join(out,'observations.json'),JSON.stringify(actual,null,2)+'\n');
  assert.deepEqual(errors,[]);
 }finally{await context.close();await browser.close()}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
