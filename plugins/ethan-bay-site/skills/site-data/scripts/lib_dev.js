// 测试用：本机模拟的“手机”。打开线上网址，但网页文件改由本机仓库提供，中转站换成本机模拟（mock_ntfy.js，端口 8090）。
// 用法：先 node mock_ntfy.js &，再在自己的测试脚本里 const L=require('./lib_dev.js'); const b=await L.launch(); const p=await L.device(b,'A',errs);
// 测完要 git checkout data/ 恢复，测试数据不能推到线上。停止模拟中转站用 kill <进程号>（不要 pkill -f，会把当前 shell 一起关掉）。
let pw;try{pw=require('playwright');}catch(e){pw=require('/opt/node22/lib/node_modules/playwright');}const {chromium}=pw;const fs=require('fs'),path=require('path'),{execSync}=require('child_process');
const ROOT=process.env.REPO||process.cwd(),GH='https://2377568565.github.io/Ethan_bay/';
exports.ROOT=ROOT;exports.GH=GH;
exports.sync=()=>execSync('node tools/q4/ask_sync.js',{cwd:ROOT,env:Object.assign({Q4_TOPIC:'q4ask-c656a4ca18696d0b'},process.env,{Q4_RELAY:'http://127.0.0.1:8090'})}).toString().trim().replace(/\n/g,' | ');
exports.launch=()=>chromium.launch();
exports.device=async(b,name,errs,opt={})=>{
  const c=await b.newContext(Object.assign({viewport:{width:390,height:844},isMobile:true,hasTouch:true,timezoneId:'Asia/Shanghai',permissions:['clipboard-read','clipboard-write']},opt));
  await c.route(GH+'**',async r=>{let p=decodeURIComponent(new URL(r.request().url()).pathname.replace('/Ethan_bay/',''))||'index.html';const f=path.join(ROOT,p);
    if(fs.existsSync(f)&&fs.statSync(f).isFile())await r.fulfill({body:fs.readFileSync(f),contentType:{'.html':'text/html; charset=utf-8','.json':'application/json','.woff2':'font/woff2','.js':'application/javascript'}[path.extname(f)]||'application/octet-stream',headers:{'access-control-allow-origin':'*'}});else await r.fulfill({status:404,body:'nf'});});
  await c.route('https://ntfy.sh/**',async r=>{const resp=await r.fetch({url:r.request().url().replace('https://ntfy.sh','http://127.0.0.1:8090')});await r.fulfill({response:resp});});
  await c.route(/pconline|busuanzi|sohu|bigdatacloud|nominatim/,r=>r.abort());
  const p=await c.newPage();p.on('pageerror',e=>errs.push(name+': '+e.message));p.on('dialog',d=>{errs.push(name+' dialog: '+d.message().slice(0,80));d.accept();});
  p.ctx=c;return p;};
exports.openAsk=async p=>{if(p.url().startsWith(GH))await p.reload({waitUntil:'domcontentloaded'});await p.goto(GH+'#ask',{waitUntil:'domcontentloaded'});for(let i=0;i<60;i++){await p.waitForTimeout(250);if(!/正在连接/.test(await p.textContent('#ask .ask-items')))break;}};
exports.items=async p=>(await p.locator('#ask .aq').allTextContents()).map(t=>t.replace(/\s+/g,' ').slice(0,60));
