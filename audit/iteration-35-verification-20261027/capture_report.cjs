// Additional framing only: prior interaction checks remain valid.
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.TANGERINE_TEST_PLAYWRIGHT_MODULE);
(async()=>{const out=path.join(process.cwd(),'data/iteration-35-verification-20261027/browser');
fs.writeFileSync(path.join(out,'control.json'),JSON.stringify({scenario:'report-heading-framing',mode:'normal'}));
const browser=await chromium.launchPersistentContext(path.join(out,'chrome-profile'),{executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true,viewport:{width:1280,height:720}});
try{const page=browser.pages()[0];await page.goto(JSON.parse(fs.readFileSync(path.join(out,'server.json'))).url+'/sources');const heading=page.getByRole('region',{name:'Import report'}).getByRole('heading',{name:'Import report',exact:true});await heading.waitFor();
for(const width of [390,320]){await page.setViewportSize({width,height:width===390?844:740});await heading.evaluate(e=>e.scrollIntoView({block:'start'}));await page.evaluate(()=>scrollBy(0,-100));await page.screenshot({path:path.join(out,'12-report-heading-'+width+'.png')});}
}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1});
