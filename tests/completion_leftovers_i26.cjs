const {chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE),assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
(async()=>{
 const out=process.env.I26_OUTPUT,browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:720},recordVideo:{dir:out,size:{width:1280,height:720}}}),page=await context.newPage();
 const facts={source_scope:'I26 selected saved clips',layouts:[],audio:[],interaction:{},pageErrors:[],claimed_all_122_confirmed:false,requested_benchmark_calls:0};
 page.on('pageerror',error=>facts.pageErrors.push(error.message));
 try{
  await page.goto(process.env.I26_URL);await page.locator('audio').first().waitFor();
  assert.equal(await page.locator('audio').count(),20);await page.waitForFunction(()=>[...document.querySelectorAll('audio')].every(a=>a.readyState===4&&!a.error));
  facts.audio=await page.locator('audio').evaluateAll(items=>items.map(a=>({case:a.getAttribute('src').split('/')[2],role:a.getAttribute('src').split('/')[3].replace('.wav',''),src:a.getAttribute('src'),readyState:a.readyState,error:a.error?.code??null,duration:a.duration})));
  const first=page.getByLabel('Linking · Clean reference',{exact:true}),second=page.getByLabel('Linking · Candidate recording',{exact:true});
  await first.click({position:{x:18,y:25}});await page.waitForFunction(()=>document.querySelector('audio').currentTime>.2);
  facts.interaction.advanced_time=await first.evaluate(a=>a.currentTime);
  await second.click({position:{x:18,y:25}});await page.waitForFunction(()=>document.querySelectorAll('audio')[1].currentTime>.1);
  facts.interaction.other_player_paused=await first.evaluate(a=>a.paused);assert(facts.interaction.other_player_paused);
  await second.focus();await page.keyboard.press('Space');assert(await second.evaluate(a=>a.paused));await first.focus();await page.keyboard.press('Space');await page.waitForFunction(()=>!document.querySelector('audio').paused);await page.keyboard.press('Space');
  facts.interaction.keyboard_observed=true;facts.interaction.activation_observed=true;
  const detail=page.locator('#linking .model-note').first();await detail.locator('summary').click();assert(await detail.evaluate(e=>e.open));await page.screenshot({path:path.join(out,'playing-and-notes.png')});
  for(const width of [1280,390,320]){
   await page.setViewportSize({width,height:width===1280?720:width===390?844:740});await page.locator('h1').scrollIntoViewIfNeeded();
   const row=await page.evaluate(()=>({width:innerWidth,pageWidth:document.documentElement.scrollWidth,size:getComputedStyle(document.body).fontSize,lineHeight:getComputedStyle(document.body).lineHeight,fontLoaded:document.fonts.check('17px "Source Sans 3"')}));assert.equal(row.width,row.pageWidth);assert.equal(row.size,'17px');assert(row.fontLoaded);facts.layouts.push(row);await page.screenshot({path:path.join(out,'layout-'+width+'.png')});
  }
  await page.setViewportSize({width:1280,height:720});const refresh=page.getByRole('button',{name:'Refresh saved observations',exact:true});await refresh.focus();await Promise.all([page.waitForNavigation(),page.keyboard.press('Enter')]);await page.waitForFunction(()=>[...document.querySelectorAll('audio')].length===20&&[...document.querySelectorAll('audio')].every(a=>a.readyState===4&&!a.error));
  facts.interaction.refresh_observed=true;facts.interaction.disclosure_observed=true;assert.equal(facts.pageErrors.length,0);facts.completed=true;await page.screenshot({path:path.join(out,'refreshed.png')});
 }finally{fs.writeFileSync(path.join(out,'browser-observations.json'),JSON.stringify(facts,null,2)+'\n');await context.close();await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1});
