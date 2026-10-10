// Native browser transport only; application DOM and requests are never substituted.
const readline = require('node:readline');
const {chromium} = require(process.env.TANGERINE_TEST_PLAYWRIGHT_MODULE);
(async()=>{
 const context=await chromium.launchPersistentContext(process.argv[2],{executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,timeout:30000});
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
    if(request.method==='close'){await context.close();send({id:request.id,result:{}});break;}
    if(request.method==='evaluate')result=await page.evaluate(request.expression);
    else if(request.method==='Page.navigate'){await page.goto(request.params.url,{waitUntil:'load',timeout:30000});result={};}
    else if(request.method==='Page.captureScreenshot')result={data:(await page.screenshot({type:'png',timeout:30000})).toString('base64')};
    else result=await session.send(request.method,request.params||{});
    send({id:request.id,result:result===undefined?null:result});
   }catch(error){send({id:request.id,error:String(error.stack||error)});}
  }
 }finally{await context.close();}
})().catch(error=>{process.stdout.write(JSON.stringify({error:String(error.stack||error)})+'\n');process.exitCode=1;});
