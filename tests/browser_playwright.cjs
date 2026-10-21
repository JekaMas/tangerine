// Native browser transport only; application DOM and requests are never substituted.
const readline = require('node:readline');
const fs = require('node:fs');
const {chromium} = require(process.env.TANGERINE_TEST_PLAYWRIGHT_MODULE);
(async()=>{
 const recording=process.env.TANGERINE_TEST_VIDEO_DIR;
 if(recording)fs.mkdirSync(recording,{recursive:true});
 const context=await chromium.launchPersistentContext(process.argv[2],{...(recording?{recordVideo:{dir:recording,size:{width:1280,height:720}}}:{}),executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,timeout:30000});
 const page=context.pages()[0]||await context.newPage();
 const session=await context.newCDPSession(page);
 const lines=readline.createInterface({input:process.stdin});
 const send=x=>process.stdout.write(JSON.stringify(x)+'\n');
 try{
  if(process.argv[3])await page.goto(process.argv[3],{waitUntil:'load',timeout:30000});
  send({ready:true,driver_version:require(process.env.TANGERINE_TEST_PLAYWRIGHT_MODULE+'/package.json').version});
  for await(const line of lines){
   const request=JSON.parse(line);
   try{
    let result;
    if(request.method==='close'){const videos=[];for(const p of context.pages())if(p.video())videos.push(await p.video().path());await context.close();for(const path of videos)if(!fs.statSync(path).size)throw Error('VIDEO_EVIDENCE_EMPTY');send({id:request.id,result:{videos}});break;}
    if(request.method==='UI.click')result=await page.locator(request.params.selector).click();
    else if(request.method==='UI.fill')result=await page.locator(request.params.selector).fill(request.params.value);
    else if(request.method==='UI.select')result=await page.locator(request.params.selector).selectOption(request.params.value);
    else if(request.method==='UI.files')result=await page.locator(request.params.selector).setInputFiles(request.params.paths);
    else if(request.method==='evaluate')result=await page.evaluate(request.expression);
    else if(request.method==='Page.navigate'){await page.goto(request.params.url,{waitUntil:'load',timeout:30000});result={};}
    else if(request.method==='Page.reload'){await page.reload({waitUntil:'load',timeout:30000});result={};}
    else if(request.method==='Page.captureScreenshot')result={data:(await page.screenshot({type:'png',fullPage:request.params?.captureBeyondViewport===true,timeout:30000})).toString('base64')};
    else result=await session.send(request.method,request.params||{});
    send({id:request.id,result:result===undefined?null:result});
   }catch(error){send({id:request.id,error:String(error.stack||error)});}
  }
 }finally{await context.close();}
})().catch(error=>{process.stdout.write(JSON.stringify({error:String(error.stack||error)})+'\n');process.exitCode=1;});
