// Additional visual observations only. Behavioral browser evidence is retained.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE);
(async()=>{
 const out=process.env.TANGERINE_JFLEG_EVIDENCE,base=process.env.TANGERINE_JFLEG_BROWSER_URL,fixture=JSON.parse(fs.readFileSync(process.env.TANGERINE_JFLEG_FIXTURE));
 fs.mkdirSync(path.join(out,'video'),{recursive:true});
 const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:720},recordVideo:{dir:path.join(out,'video'),size:{width:1280,height:720}}});const page=await context.newPage();
 try {
  await page.goto(base+'/sources',{waitUntil:'networkidle'});await page.getByRole('button',{name:'Open saved release '+fixture.release_id,exact:true}).click();
  const region=page.getByRole('region',{name:'Written correction examples',exact:true}),first=region.locator(':scope > details').first();await first.waitFor();await first.locator(':scope > summary').click();
  const views=[];
  for(const [width,height] of [[1280,720],[390,844],[320,740]]) {
   await page.setViewportSize({width,height});await page.evaluate(()=>document.fonts.ready);
   await region.getByRole('heading',{name:'Written correction examples',exact:true}).evaluate(e=>e.scrollIntoView({block:'start'}));await page.evaluate(()=>window.scrollBy(0,-100));
   await page.screenshot({path:path.join(out,'controls-'+width+'.png')});await first.screenshot({path:path.join(out,'all-references-'+width+'.png')});
   assert.equal(await first.locator('ol > li').count(),4);views.push({width,height,reference_blocks:4,original_and_all_references_captured:true});
  }
  const buttons=region.getByRole('button');assert.equal(await buttons.count(),4);await buttons.first().focus();await page.keyboard.press('Tab');assert.equal(await buttons.nth(1).evaluate(e=>document.activeElement===e),true);
  fs.writeFileSync(path.join(out,'observations.json'),JSON.stringify({views,keyboard_download_focus:true,fixture,scope:'Additional visual capture and keyboard focus only; reuse full functional browser receipt.'},null,2)+'\n');
 }finally{await context.close();await browser.close()}
})().catch(e=>{console.error(e.stack);process.exitCode=1});
