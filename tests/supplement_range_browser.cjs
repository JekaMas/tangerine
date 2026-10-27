// Original byte-range metadata must survive the ordinary Next proxy.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE);
const base=process.env.TANGERINE_SUPPLEMENT_BROWSER_URL,out=process.env.TANGERINE_SUPPLEMENT_EVIDENCE,data=process.env.TANGERINE_SUPPLEMENT_DATA;
(async()=>{
 fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true}),context=await browser.newContext(),page=await context.newPage(),observed={};
 try{
  const fixture=JSON.parse(fs.readFileSync(path.join(data,'elrd-fixture.json')));await page.goto(base+'/sources',{waitUntil:'networkidle'});
  await page.locator('[aria-label="Source status"] > li').filter({has:page.getByRole('heading',{name:'ELRD',exact:true})}).getByRole('button',{name:'Open saved release '+fixture.release_id,exact:true}).click();
  await page.waitForFunction(()=>{const text=document.querySelector('[aria-label="Speech and dialogue examples"] details pre')?.textContent;return text&&JSON.parse(text).source_id==='ELRD'});
  const audio=page.getByRole('region',{name:'Speech and dialogue examples',exact:true}).locator('audio').first(),src=await audio.getAttribute('src');
  const response=await page.request.get(base+src,{headers:{Range:'bytes=0-43'}}),body=await response.body();
  Object.assign(observed,{status:response.status(),headers:response.headers(),byte_count:body.length,riff:body.subarray(0,4).toString()});
  await audio.evaluate(a=>{a.preload='metadata';a.load()});
  await page.waitForFunction(()=>document.querySelector('[aria-label="Speech and dialogue examples"] audio')?.readyState>=1);
  observed.metadata=await audio.evaluate(a=>({duration:Number.isFinite(a.duration)?a.duration:String(a.duration),ready_state:a.readyState}));
  assert.equal(observed.status,206);assert.equal(observed.byte_count,44);assert.equal(observed.riff,'RIFF');assert.match(observed.headers['content-range'],/^bytes 0-43\//);
  assert.ok(Number.isFinite(observed.metadata.duration),'The ordinary recording controls must know the actual duration after loading metadata');
  assert.equal(observed.headers['content-length'],'44','The original byte length must survive the proxy for normal browser recording controls');
 }finally{fs.writeFileSync(path.join(out,'observations.json'),JSON.stringify(observed,null,2)+'\n');await context.close();await browser.close()}
})().catch(error=>{console.error(error.stack||String(error));process.exitCode=1});
