// Targeted keyboard and visible error/retry typography, on the real source UI.
const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE);
const base=process.env.TANGERINE_SUPPLEMENT_BROWSER_URL,out=process.env.TANGERINE_SUPPLEMENT_EVIDENCE,data=process.env.TANGERINE_SUPPLEMENT_DATA;
(async()=>{
 fs.mkdirSync(out,{recursive:true});const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:720},recordVideo:{dir:path.join(out,'video'),size:{width:1280,height:720}}}),page=await context.newPage();
 const fixture=JSON.parse(fs.readFileSync(path.join(data,'elrd-fixture.json'))),observed={layouts:[],page_errors:[]};page.on('pageerror',e=>observed.page_errors.push(e.message));
 try{
  await page.goto(base+'/sources',{waitUntil:'networkidle'});
  await page.locator('[aria-label="Source status"] > li').filter({has:page.getByRole('heading',{name:'ELRD',exact:true})}).getByRole('button',{name:'Open saved release '+fixture.release_id,exact:true}).click();
  await page.waitForFunction(()=>{const text=document.querySelector('[aria-label="Speech and dialogue examples"] details pre')?.textContent;return text&&JSON.parse(text).source_id==='ELRD'});
  const first=page.getByRole('region',{name:'Speech and dialogue examples',exact:true}).locator(':scope > details').first();await first.locator(':scope > summary').click();
  await page.route('**/api/v1/sources/assets/*/bytes',route=>route.fulfill({status:503,contentType:'application/json',body:'{"error":"PRIVATE_CANARY"}'}));
  await first.getByRole('button',{name:'Play this source interval',exact:true}).click();const retry=first.getByRole('button',{name:'Retry recording',exact:true});await retry.waitFor();
  for(const [width,height] of [[1280,720],[390,844],[320,740]]){
   await page.setViewportSize({width,height});await page.evaluate(()=>document.fonts.ready);
   await retry.focus();await page.keyboard.press('Shift+Tab');await page.keyboard.press('Tab');
   const layout=await retry.evaluate(button=>{const p=button.previousElementSibling,style=getComputedStyle(p),rect=p.getBoundingClientRect();return {width:innerWidth,document_width:document.documentElement.scrollWidth,font_size:style.fontSize,line_height:style.lineHeight,font_family:style.fontFamily,font_loaded:document.fonts.check('17px "Source Sans 3"'),focused:document.activeElement===button,outline:getComputedStyle(button).outlineStyle,button_height:button.getBoundingClientRect().height,alert_width:rect.width,error_text:p.textContent}});
   observed.layouts.push(layout);
   assert.equal(layout.focused,true);assert.notEqual(layout.outline,'none');assert.equal(layout.width,layout.document_width);assert.ok(parseFloat(layout.font_size)>=15);assert.equal(layout.font_loaded,true);assert.ok(layout.button_height>=44);
   await retry.evaluate(button=>button.scrollIntoView({block:'center',behavior:'instant'}));
   await page.screenshot({path:path.join(out,'recovery-keyboard-'+width+'.png')});
  }
  // Keyboard recovery is an ordinary same-record action, after the failure is removed.
  await page.unroute('**/api/v1/sources/assets/*/bytes');await page.keyboard.press('Enter');
  await page.waitForFunction(()=>{const a=document.querySelector('[aria-label="Speech and dialogue examples"] audio');return a&&!a.paused&&a.currentTime>.1});observed.keyboard_retry_recovered=true;
  assert.equal(await first.getByRole('alert').count(),0);await first.locator('audio').evaluate(a=>a.pause());
  assert.deepEqual(observed.page_errors,[]);
 }finally{fs.writeFileSync(path.join(out,'observations.json'),JSON.stringify(observed,null,2)+'\n');await context.close();await browser.close()}
})().catch(error=>{console.error(error.stack||String(error));process.exitCode=1});
