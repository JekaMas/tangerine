// Pixel evidence only; native and interaction greens are retained separately.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE);
const base=process.env.TANGERINE_SUPPLEMENT_BROWSER_URL,out=process.env.TANGERINE_SUPPLEMENT_EVIDENCE,data=process.env.TANGERINE_SUPPLEMENT_DATA;
(async()=>{
 fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});const page=await browser.newPage({viewport:{width:1280,height:720}}),observed={views:[],scope:'Additional actual body/answer pixels; no repeated model, import or grading behavior.'};
 const region=page.getByRole('region',{name:'Speech and dialogue examples',exact:true});
 async function shot(name,locator){await locator.evaluate(e=>e.scrollIntoView({block:'start',behavior:'instant'}));await page.evaluate(()=>window.scrollBy(0,-100));await page.waitForTimeout(100);await page.screenshot({path:path.join(out,name+'.png')});fs.writeFileSync(path.join(out,name+'.html'),await page.content())}
 const mode=async name=>{await fetch(base+'/__test/mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode:name,remaining:0})})};
 try{
  await page.goto(base+'/sources',{waitUntil:'networkidle'});
  for(const name of ['edacc','elrd','diplomat','dral-base','dral-8']){
   const fixture=JSON.parse(fs.readFileSync(path.join(data,name+'-fixture.json')));await page.locator('[aria-label="Source status"] > li').filter({has:page.getByRole('heading',{name:fixture.source_id,exact:true})}).getByRole('button',{name:'Open saved release '+fixture.release_id,exact:true}).click();
   await page.waitForFunction(({source,version})=>{const p=document.querySelector('[aria-label="Speech and dialogue examples"] details pre');if(!p)return false;const e=JSON.parse(p.textContent);return e.source_id===source&&e.source_version===version},{source:fixture.source_id,version:fixture.source_version});
   if(name==='diplomat'){await page.getByLabel('Example view',{exact:true}).selectOption('PIR_second_subtask_dataset');await page.waitForFunction(()=>document.querySelector('[aria-label="Speech and dialogue examples"] details summary')?.textContent.includes('PIR_second_subtask_dataset'))}
   if(name==='dral-8'){await page.getByLabel('Example view',{exact:true}).selectOption('fragments-short');await page.waitForFunction(()=>document.querySelector('[aria-label="Speech and dialogue examples"] details summary')?.textContent.includes('ES_001_2'))}
   const first=region.locator(':scope > details').first();await first.locator(':scope > summary').click();
   for(const [width,height] of [[1280,720],[390,844],[320,740]]){
    await page.setViewportSize({width,height});await page.evaluate(()=>document.fonts.ready);await shot(name+'-'+width+'-controls',region.getByRole('heading',{name:'Speech and dialogue examples',exact:true}));await shot(name+'-'+width+'-body',first.locator(':scope > summary'));
    if(name==='diplomat')await shot(name+'-'+width+'-answer',first.getByRole('heading',{name:'Source answer choice',exact:true}));
    const rect=await first.locator(':scope > summary').boundingBox(),size=await first.locator(':scope > p').first().evaluate(e=>({font:getComputedStyle(e).fontSize,line:getComputedStyle(e).lineHeight,width:document.documentElement.scrollWidth}));assert.equal(size.width,width);assert.equal(size.font,'17px');observed.views.push({source:name,width,summary:rect,style:size});
   }
  }
  await mode('recording_window');await page.getByLabel('Example view',{exact:true}).selectOption('fragments-long');await page.waitForFunction(()=>document.querySelector('[aria-label="Speech and dialogue examples"] details summary')?.textContent.includes('EN_049_#1'));const window=region.locator(':scope > details').first();await window.locator(':scope > summary').click();await shot('recording-window-320',window.locator(':scope > summary'));await mode('normal');
  fs.writeFileSync(path.join(out,'observations.json'),JSON.stringify(observed,null,2)+'\n');
 }finally{await browser.close()}
 console.log('Actual source bodies, controls, native answers and recording-window pixels saved at all three widths.');
})().catch(error=>{console.error(error.stack||String(error));process.exitCode=1});
