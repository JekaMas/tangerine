const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict'),{chromium}=require(process.env.TANGERINE_PLAYWRIGHT_MODULE);
(async()=>{
 const out=process.env.LEFTOVER_OUTPUT,stack=JSON.parse(fs.readFileSync('data/iteration-30-release-20261027/stack.json')),browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true}),context=await browser.newContext({viewport:{width:1280,height:720}}),page=await context.newPage();
 let mode='normal',remaining=0;const calls=[],facts={source_revision:stack.archive_revision,checks:[]};
 await context.route('**/api/v1/**',async route=>{
  const req=route.request(),pathname=new URL(req.url()).pathname;
  if(req.method()!=='GET'){await route.fulfill({status:403,body:'No writes in read-dependency discriminator'});return;}
  if(mode==='provider-unavailable'&&pathname==='/api/v1/provider-connections'||mode==='transient'&&remaining>0&&pathname==='/api/v1/configuration'){
   if(mode==='transient')remaining--;calls.push({path:pathname,status:503,mode});await route.fulfill({status:503,contentType:'application/json',body:'{"error":"PRIVATE_SETTINGS_CANARY"}'});return;
  }
  calls.push({path:pathname,mode,status:'forwarded'});await route.continue();
 });
 try{
  mode='transient';remaining=1;await page.goto(stack.origin_url+'/settings');
  await page.waitForTimeout(1500);const selector=page.getByLabel('Speech profile',{exact:true});
  facts.checks.push({case:'transient read',enabled:await selector.isEnabled(),alerts:await page.getByRole('alert').allTextContents()});await page.screenshot({path:path.join(out,'settings-transient-baseline.png')});
  mode='provider-unavailable';await page.reload();await page.waitForTimeout(1500);
  facts.checks.push({case:'optional provider unavailable',enabled:await selector.isEnabled(),alerts:await page.getByRole('alert').allTextContents()});await page.screenshot({path:path.join(out,'settings-provider-baseline.png')});
  facts.calls=calls;assert(facts.checks.every(row=>row.enabled),'An optional connection failure blocks independent local speech settings.');
 }finally{fs.writeFileSync(path.join(out,'settings-baseline.json'),JSON.stringify(facts,null,2)+'\n');await context.close();await browser.close();}
})().catch(error=>{console.error(error);process.exitCode=1});
