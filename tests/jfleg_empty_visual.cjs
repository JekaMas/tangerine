// Focused follow-up capture: empty/partial result text was below the first
// screenshot's controls at narrow widths. Read real saved data, then frame it.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE);
(async()=>{
 const out=process.env.TANGERINE_JFLEG_EVIDENCE,base=process.env.TANGERINE_JFLEG_BROWSER_URL;
 const fixture=JSON.parse(fs.readFileSync(process.env.TANGERINE_JFLEG_VERIFY_FIXTURES));
 fs.mkdirSync(path.join(out,'video'),{recursive:true});
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:720},recordVideo:{dir:path.join(out,'video'),size:{width:1280,height:720}}});const page=await context.newPage(),views=[];
 try{
  await page.goto(base+'/sources',{waitUntil:'networkidle'});
  for(const kind of ['partial','empty']){
   await page.getByRole('button',{name:'Open saved release '+fixture[kind].release_id,exact:true}).click();
   const region=page.getByRole('region',{name:'Written correction examples',exact:true});
   const target=kind==='empty'?region.getByText('No converted written corrections are saved yet. Import or resume the selected release above.',{exact:true}):region.locator(':scope > details').first();await target.waitFor();
   if(kind==='partial')await target.locator(':scope > summary').click();
   for(const [width,height] of [[1280,720],[390,844],[320,740]]){
    await page.setViewportSize({width,height});await page.evaluate(()=>document.fonts.ready);
    await target.evaluate(e=>e.scrollIntoView({block:'center'}));
    await page.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
    const layout=await target.evaluate(e=>({document_width:document.documentElement.scrollWidth,sidebar_count:document.querySelectorAll('aside.sidebar').length,font_size:getComputedStyle(e).fontSize,top:e.getBoundingClientRect().top,bottom:e.getBoundingClientRect().bottom,viewport:innerHeight}));
    assert.equal(layout.document_width,width);assert.equal(layout.sidebar_count,1);assert.ok(layout.bottom>75&&layout.top<height);
    await page.screenshot({path:path.join(out,kind+'-result-'+width+'.png')});views.push({kind,width,height,...layout});
   }
   await page.waitForTimeout(800); // Retain a readable uncut observation.
  }
  const toggle=page.getByRole('button',{name:'Toggle navigation',exact:true});await toggle.click();assert.equal(await toggle.getAttribute('aria-expanded'),'true');await toggle.click();assert.equal(await toggle.getAttribute('aria-expanded'),'false');
  fs.writeFileSync(path.join(out,'observations.json'),JSON.stringify({views,mobile_navigation_works:true,fixture,scope:'Actual same retained partial/empty imports, focused result framing; no response or DOM substitute.'},null,2)+'\n');
 }finally{await context.close();await browser.close()}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
