const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE);
(async()=>{
 const out=process.env.I30_OUTPUT,browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
 const context=await browser.newContext({viewport:{width:1280,height:720},recordVideo:{dir:out,size:{width:1280,height:720}}}),page=await context.newPage();
 let mode='normal',remaining=0;const calls=[],facts={layouts:[],states:[],pageErrors:[],console:[],raw_errors:false};
 page.on('pageerror',error=>facts.pageErrors.push(error.message));page.on('console',entry=>facts.console.push({type:entry.type(),text:entry.text()}));
 await context.route('**/api/v1/**',async route=>{
  const req=route.request(),pathname=new URL(req.url()).pathname,row={method:req.method(),path:pathname,mode};calls.push(row);
  if(req.method()!=='GET'&&!(req.method()==='PUT'&&pathname==='/api/v1/configuration')){row.forbidden=true;await route.fulfill({status:403,body:'Blocked test action'});return;}
  if(mode==='provider-unavailable'&&pathname==='/api/v1/provider-connections'||mode==='configuration-unavailable'&&pathname==='/api/v1/configuration'||mode==='transient'&&remaining>0&&pathname==='/api/v1/configuration'){
   if(mode==='transient')remaining--;row.status=503;await route.fulfill({status:503,contentType:'application/json',body:'{"error":"PRIVATE_SETTINGS_CANARY"}'});return;
  }
  const response=await route.fetch();row.status=response.status();await route.fulfill({response});
 });
 const speech=()=>page.getByLabel('Speech profile',{exact:true});
 async function loaded(){await page.waitForFunction(()=>{const s=document.querySelector('select[aria-label="Speech profile"]');return s&&!s.disabled});}
 async function clean(){const body=await page.locator('main').innerText();assert(!body.includes('PRIVATE_SETTINGS_CANARY'));}
 try{
  await page.goto(process.env.I30_URL);await page.locator('h1').waitFor();facts.empty_library=!(await page.locator('main').innerText()).includes('Generated exercise');await page.screenshot({path:path.join(out,'library.png')});
  const prepare=page.locator('a[href="/prepare"]').first();await prepare.focus();await page.keyboard.press('Enter');await page.waitForURL('**/prepare');facts.prepare_navigation=true;facts.keyboard_navigation=true;await page.screenshot({path:path.join(out,'prepare.png')});
  await page.goto(process.env.I30_URL+'/settings');await loaded();const original=await speech().inputValue();
  const alternate=original==='kokoro-local-en-v1'?'kokoro-controlled-v1':'kokoro-local-en-v1';await speech().selectOption(alternate);await page.getByRole('status').filter({hasText:'Settings saved.'}).waitFor();await page.reload();await loaded();assert.equal(await speech().inputValue(),alternate);facts.settings_saved=true;facts.settings_reopened=true;
  await speech().selectOption(original);await page.getByRole('status').filter({hasText:'Settings saved.'}).waitFor();facts.original_profile_restored=true;
  mode='transient';remaining=1;await page.reload();await loaded();await clean();facts.states.push('Transient configuration read recovered automatically');
  mode='provider-unavailable';await page.reload();await loaded();await page.getByRole('alert').filter({hasText:'ChatGPT connection settings are temporarily unavailable.'}).waitFor();assert(await speech().isEnabled());await clean();facts.states.push('Unavailable connection list leaves local settings usable');await page.screenshot({path:path.join(out,'independent-settings.png')});
  mode='normal';await page.getByRole('button',{name:'Refresh',exact:true}).first().click();await page.getByRole('alert').filter({hasText:'ChatGPT connection settings are temporarily unavailable.'}).waitFor({state:'hidden'});await loaded();
  mode='configuration-unavailable';await page.getByRole('button',{name:'Refresh',exact:true}).first().click();await page.getByRole('alert').filter({hasText:'Saved configuration is unavailable.'}).waitFor();assert.equal(await speech().inputValue(),original);assert(await speech().isEnabled());await clean();facts.states.push('Failed refresh retains accepted configuration');await page.screenshot({path:path.join(out,'retained-configuration.png')});
  mode='normal';const refresh=page.getByRole('button',{name:'Refresh',exact:true}).first();await refresh.focus();await page.keyboard.press('Enter');await page.getByRole('alert').filter({hasText:'Saved configuration is unavailable.'}).waitFor({state:'hidden'});await loaded();facts.states.push('Keyboard Refresh recovered settings');
  for(const size of [{width:1280,height:720},{width:390,height:844},{width:320,height:740}]){
   await page.setViewportSize(size);await page.locator('h1').scrollIntoViewIfNeeded();const row=await page.evaluate(()=>({width:innerWidth,height:innerHeight,pageWidth:document.documentElement.scrollWidth,bodySize:getComputedStyle(document.body).fontSize,bodyLine:getComputedStyle(document.body).lineHeight,fontLoaded:document.fonts.check('17px "Source Sans 3"'),heading:document.querySelector('h1').textContent}));assert.equal(row.width,row.pageWidth);assert.equal(row.bodySize,'17px');assert(row.fontLoaded);facts.layouts.push(row);await page.screenshot({path:path.join(out,'settings-'+size.width+'.png')});
  }
  const menu=page.getByRole('button',{name:/navigation|menu/i}).first();await menu.click();await page.locator('a[href="/"]').filter({hasText:'Library'}).first().click();await page.waitForURL(process.env.I30_URL+'/');facts.mobile_navigation=true;facts.completed=true;assert.equal(facts.pageErrors.length,0);assert(!calls.some(c=>c.forbidden));
 }finally{fs.writeFileSync(path.join(out,'ui-observations.json'),JSON.stringify(facts,null,2)+'\n');fs.writeFileSync(path.join(out,'requests.json'),JSON.stringify(calls,null,2)+'\n');await context.close();await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1});
