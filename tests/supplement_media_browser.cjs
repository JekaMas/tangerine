// Actual retained ELRD recording, with one controlled HTTP failure at the byte boundary.
// No import, synthesis, model, provider or financial operation is performed.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE);
const base=process.env.TANGERINE_SUPPLEMENT_BROWSER_URL,out=process.env.TANGERINE_SUPPLEMENT_EVIDENCE,data=process.env.TANGERINE_SUPPLEMENT_DATA;
(async()=>{
 fs.mkdirSync(out,{recursive:true});
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:720},recordVideo:{dir:path.join(out,'video'),size:{width:1280,height:720}}});
 const page=await context.newPage(),observed={media_requests:[],diagnostics:[],page_errors:[],layouts:[],application_methods:[]};
 let remaining=1;
 page.on('console',message=>{if(message.type()==='warning')observed.diagnostics.push(message.text())});
 page.on('pageerror',error=>observed.page_errors.push(error.message));
 page.on('response',response=>{if(response.url().includes('/sources/assets/'))observed.media_requests.push(response.status())});
 page.on('request',request=>{if(request.url().includes('/api/'))observed.application_methods.push(request.method())});
 const region=page.getByRole('region',{name:'Speech and dialogue examples',exact:true});
 async function open(name){
  const fixture=JSON.parse(fs.readFileSync(path.join(data,name+'-fixture.json')));
  await page.goto(base+'/sources',{waitUntil:'networkidle'});
  await page.locator('[aria-label="Source status"] > li').filter({has:page.getByRole('heading',{name:fixture.source_id,exact:true})}).getByRole('button',{name:'Open saved release '+fixture.release_id,exact:true}).click();
  await page.waitForFunction(({source,version})=>{const raw=document.querySelector('[aria-label="Speech and dialogue examples"] details pre')?.textContent;return raw&&JSON.parse(raw).source_id===source&&JSON.parse(raw).source_version===version},{source:fixture.source_id,version:fixture.source_version});
  const first=region.locator(':scope > details').first();await first.locator(':scope > summary').click();return first;
 }
 const playing=()=>page.waitForFunction(()=>{const a=document.querySelector('[aria-label="Speech and dialogue examples"] audio');return a&&!a.paused&&a.currentTime>.1},{},{timeout:4500});
 const picture=async(name,first)=>{await first.locator(':scope > summary').evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));await page.evaluate(()=>window.scrollBy(0,-100));await page.screenshot({path:path.join(out,name+'.png')})};
 try{
  await page.route('**/api/v1/sources/assets/*/bytes',async route=>{
   if(remaining-->0)await route.fulfill({status:503,contentType:'application/json',body:'{"error":"PRIVATE_MEDIA_CANARY_DO_NOT_SHOW"}'});
   else await route.continue();
  });
  let first=await open('elrd');
  await first.getByRole('button',{name:'Play this source interval',exact:true}).click();
  // Bounded observation records the red counterexample without making a second user action.
  await playing().catch(()=>{});
  observed.audio=await first.locator('audio').evaluate(a=>({paused:a.paused,time:a.currentTime,error:a.error?.code??null}));
  observed.visible_error=await first.getByRole('alert').allTextContents();
  await picture('transient-source-audio',first);
  assert.ok(observed.media_requests.length>=2,'Transient byte failure must retry without another user action');
  assert.equal(observed.audio.paused,false,'The same source interval must resume after transient recovery');
  assert.deepEqual(observed.visible_error,[],'A recovered read must not leave a terminal error');
  assert.equal(observed.media_requests[0],503);assert.ok([200,206].includes(observed.media_requests[1]));
  observed.transient_statuses=observed.media_requests.slice();
  await page.waitForFunction(()=>{const a=document.querySelector('[aria-label="Speech and dialogue examples"] audio');return a?.paused&&a.currentTime>=13.703&&a.currentTime<14.5},{},{timeout:20000});
  observed.finite_playback=await first.locator('audio').evaluate(a=>({time:a.currentTime,paused:a.paused}));

  remaining=Infinity;first=await open('elrd');const from=observed.media_requests.length;
  await first.getByRole('button',{name:'Play this source interval',exact:true}).click();await first.getByRole('button',{name:'Retry recording',exact:true}).waitFor();
  observed.exhausted_statuses=observed.media_requests.slice(from);assert.deepEqual(observed.exhausted_statuses,[503,503,503]);
  observed.exhausted_message=await first.getByRole('alert').textContent();assert.equal(observed.exhausted_message,'This recording is unavailable right now. Retry playback; your source files are retained.');
  assert.doesNotMatch(await page.locator('main').textContent(),/PRIVATE_MEDIA|CANARY|traceback/);
  assert.equal(await region.locator(':scope > details').count(),20);assert.equal(await region.getByRole('button',{name:'Refresh source examples',exact:true}).isEnabled(),true);
  for(const [width,height] of [[1280,720],[390,844],[320,740]]){
   await page.setViewportSize({width,height});const retry=first.getByRole('button',{name:'Retry recording',exact:true});await retry.focus();
   observed.layouts.push(await first.evaluate(e=>({width:innerWidth,document_width:document.documentElement.scrollWidth,font:getComputedStyle(e.querySelector('p')).fontFamily,font_size:getComputedStyle(e.querySelector('p')).fontSize,line_height:getComputedStyle(e.querySelector('p')).lineHeight,focus:getComputedStyle(document.activeElement).outlineStyle,button_height:document.activeElement.getBoundingClientRect().height})));
   await picture('recording-retry-'+width,first);
  }
  remaining=0;await first.getByRole('button',{name:'Retry recording',exact:true}).click();await playing();assert.equal(await first.getByRole('alert').count(),0);observed.explicit_retry_recovered=true;
  await first.locator('audio').evaluate(a=>a.pause());

  await page.setViewportSize({width:1280,height:720});first=await open('dral-8');
  await fetch(base+'/__test/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:'recording_window',remaining:0})});
  await page.getByLabel('Example view',{exact:true}).selectOption('fragments-long');await page.waitForFunction(()=>document.querySelector('[aria-label="Speech and dialogue examples"] details summary')?.textContent.includes('EN_049_#1'));
  first=region.locator(':scope > details').first();await first.locator(':scope > summary').click();remaining=1;
  await first.getByRole('button',{name:'Play this source interval',exact:true}).click();await page.waitForFunction(()=>{const a=document.querySelector('[aria-label="Speech and dialogue examples"] audio');return a&&!a.paused&&a.currentTime>=5.66&&a.currentTime<8},{},{timeout:4500});
  observed.window_started=await first.locator('audio').evaluate(a=>({time:a.currentTime,paused:a.paused}));await picture('recovered-native-window',first);
  await page.waitForFunction(()=>{const a=document.querySelector('[aria-label="Speech and dialogue examples"] audio');return a?.paused&&a.currentTime>=9.81&&a.currentTime<10.5},{},{timeout:8000});
  observed.window_ended=await first.locator('audio').evaluate(a=>({time:a.currentTime,paused:a.paused}));
  await fetch(base+'/__test/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:'{"mode":"normal","remaining":0}'});

  first=await open('edacc');remaining=1;const audio=first.locator('audio');assert.equal(await audio.getAttribute('preload'),'none');assert.equal(await audio.evaluate(a=>a.paused),true);
  await audio.click({position:{x:20,y:25}});await playing();assert.equal(await first.getByRole('alert').count(),0);observed.native_controls_recovered=true;
  const removed=await audio.elementHandle();const diplomat=JSON.parse(fs.readFileSync(path.join(data,'diplomat-fixture.json')));
  await page.locator('[aria-label="Source status"] > li').filter({has:page.getByRole('heading',{name:'DIPLOMAT',exact:true})}).getByRole('button',{name:'Open saved release '+diplomat.release_id,exact:true}).click();
  await page.waitForFunction(()=>{const raw=document.querySelector('[aria-label="Speech and dialogue examples"] details pre')?.textContent;return raw&&JSON.parse(raw).source_id==='DIPLOMAT'});
  observed.disposed_player=await removed.evaluate(a=>({paused:a.paused,connected:a.isConnected}));assert.deepEqual(observed.disposed_player,{paused:true,connected:false});
  assert.ok(observed.diagnostics.some(value=>value.includes('Tangerine source playback')));
  assert.ok(observed.application_methods.every(method=>method==='GET'));
  assert.deepEqual(observed.page_errors,[]);
 }finally{
  fs.writeFileSync(path.join(out,'observations.json'),JSON.stringify(observed,null,2)+'\n');
  fs.writeFileSync(path.join(out,'final.html'),await page.content());
  await context.close();await browser.close();
 }
})().catch(error=>{console.error(error.stack||String(error));process.exitCode=1});
