// 量换页卡不卡（模拟安卓微信）：CPU 降速 4 倍，量“点下去 → 新页面画出来”的时间、长任务，以及脚本 / 样式 / 排版各花了多少毫秒。
// 用法（在仓库根目录，先启动 site-data 的 mock_ntfy.js）：NODE_PATH=/opt/node22/lib/node_modules node plugins/ethan-bay-site/skills/publish/scripts/speed.js
//   NOVT=1 模拟不支持“视图过渡”的旧手机；RATE=6 降速更多；CV='css' 临时加一段样式做对比。
// 参考（2026-10-06 优化后，降速 4 倍）：进一课约 200 ms，标签切换约 130–300 ms；优化前进一课约 1000 ms。
const L=require('/home/user/Ethan_bay/plugins/ethan-bay-site/skills/site-data/scripts/lib_dev.js');
const NOVT=process.env.NOVT==='1',RATE=+(process.env.RATE||4);
(async()=>{const b=await L.launch();const errs=[];
 const p=await L.device(b,'A',errs,{userAgent:'Mozilla/5.0 (Linux; Android 14; V2405A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0 Mobile Safari/537.36 MicroMessenger/8.0.50'});
 if(NOVT)await p.addInitScript(()=>{try{delete Document.prototype.startViewTransition;}catch(e){}});
 await p.addInitScript(()=>{window.__lt=[];try{new PerformanceObserver(l=>l.getEntries().forEach(e=>window.__lt.push(e.duration))).observe({entryTypes:['longtask']});}catch(e){}});
 if(process.env.CV)await p.addInitScript(css=>{document.addEventListener('DOMContentLoaded',()=>{var st=document.createElement('style');st.textContent=css;document.head.appendChild(st);});},process.env.CV);
 const U=L.GH+'?today=2026-10-05';
 await p.goto(U+'#l2-yw-mon',{waitUntil:'domcontentloaded'});await p.waitForTimeout(4000);
 const cdp=await p.context().newCDPSession(p);await cdp.send('Emulation.setCPUThrottlingRate',{rate:RATE});
 await cdp.send('Performance.enable');
 const met=async()=>{const m=(await cdp.send('Performance.getMetrics')).metrics;const o={};m.forEach(x=>o[x.name]=x.value);return o;};
 async function step(name,sel){
  await p.evaluate(()=>{window.__lt=[];scrollTo(0,scrollY-200);});await p.waitForTimeout(600);const m0=await met();
  const t=await p.evaluate(sel=>new Promise(res=>{var el=document.querySelector(sel);var t0=performance.now();
    var done=false;window.addEventListener('hashchange',function h(){window.removeEventListener('hashchange',h);requestAnimationFrame(()=>requestAnimationFrame(()=>{if(!done){done=true;res(Math.round(performance.now()-t0));}}));});
    el.click();setTimeout(()=>{if(!done){done=true;res(-1);}},8000);}),sel);
  await p.waitForTimeout(1500);
  const lt=await p.evaluate(()=>window.__lt.slice());
  const m1=await met();const d=k=>Math.round((m1[k]-m0[k])*1000);
  console.log(name.padEnd(14),'点到画出',String(t).padStart(5),'ms  长任务',lt.length,'个 共',Math.round(lt.reduce((a,b)=>a+b,0)),'ms 最长',Math.round(Math.max(0,...lt)),'| 脚本',d('ScriptDuration'),'样式',d('RecalcStyleDuration'),'排版',d('LayoutDuration'),'节点',m1.Nodes);
 }
 await step('学课(目录)','.tabbar [data-t="home"]');
 await step('彩蛋','.tabbar [data-t="qa"]');
 await step('音乐','.tabbar [data-t="music"]');
 await step('学课(目录)','.tabbar [data-t="home"]');
 await step('第3课','.tl .card[data-l="3"]');
 await step('彩蛋','.tabbar [data-t="qa"]');
 await step('第2课(返回)','.tabbar [data-t="home"]');
 console.log('VT',NOVT?'关':'开','CPU 降速',RATE,'倍',errs.filter(e=>!/ERR_FAILED/.test(e)));
 await b.close();})();
