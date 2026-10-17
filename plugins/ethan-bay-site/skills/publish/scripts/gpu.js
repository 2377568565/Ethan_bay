// 120Hz 检查：每个常用操作里，动画是不是都交给显卡（合成层）完成。只动 transform / opacity 的动画由显卡跑，能跟上 120Hz；
// 动宽高、位置、颜色、阴影的动画要主线程每帧重新排版或重画，只能 60Hz 甚至掉帧。
// 用法（仓库根目录，先启动 site-data 的 mock_ntfy.js）：NODE_PATH=/opt/node22/lib/node_modules node plugins/ethan-bay-site/skills/publish/scripts/gpu.js
// 结果“✓”= 全部交给显卡；“△”后面列出没交出去的（color / background-color 多半是测试里鼠标悬停造成的，手机上没有悬停，可以忽略；
// 64、131104 之类是屏幕外或互相重叠的小动画，也可以忽略）。DBG=1 打印细节。测完 git checkout data/。
const L=require('/home/user/Ethan_bay/plugins/ethan-bay-site/skills/site-data/scripts/lib_dev.js');
(async()=>{const b=await L.launch();const errs=[];
 const p=await L.device(b,'A',errs,{userAgent:'Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 Chrome/124.0 Mobile Safari/537.36'});
 const U=L.GH+'?today=2026-10-06';
 async function sc(name,act,ms){
  await b.startTracing(p,{categories:['devtools.timeline','blink.animations','devtools.timeline.animation']});
  await act();await p.waitForTimeout(ms||1300);
  const tr=JSON.parse((await b.stopTracing()).toString());let ok=0;const bad={};
  tr.traceEvents.forEach(e=>{if(e.name==='Animation'&&e.args&&e.args.data&&e.args.data.compositeFailed!==undefined){const d=e.args.data;if(!d.compositeFailed)ok++;else if(d.compositeFailed!==131072){const k=d.compositeFailed+':'+(d.unsupportedProperties||[]).join('/');bad[k]=(bad[k]||0)+1;if(process.env.DBG)console.log('   ',JSON.stringify(e.args.data).slice(0,300));}}});
  console.log((Object.keys(bad).length?'△':'✓'),name.padEnd(16),'显卡完成',ok,Object.keys(bad).length?'没交出去 '+JSON.stringify(bad):'');
 }
 await p.goto(U,{waitUntil:'domcontentloaded'});await p.waitForTimeout(3000);
 await sc('首页换经文',async()=>{await p.click('.wverse');});
 await sc('今日学课→学课',async()=>{await p.click('#wgo');},1600);
 await sc('打卡',async()=>{await p.evaluate(()=>document.querySelector('#l2-yw-tue .ckin').scrollIntoView({block:'center'}));await p.waitForTimeout(800);await p.click('#l2-yw-tue .ck-btn');});
 await sc('标签→学课目录',async()=>{await p.evaluate(()=>scrollTo(0,0));await p.waitForTimeout(400);await p.click('.tabbar [data-t="home"]');},1600);
 await sc('目录→第4课',async()=>{await p.click('.tl .card[data-l="4"]');},1600);
 await sc('打开选择课次',async()=>{await p.click('.lbar .nb-t >> visible=true');});
 await p.keyboard.press('Escape');await p.waitForTimeout(500);
 await sc('经文弹窗',async()=>{await p.click('#l4 .bref >> visible=true');});
 await p.keyboard.press('Escape');await p.waitForTimeout(500);
 await sc('标签→音乐',async()=>{await p.click('.tabbar [data-t="music"]');},1600);
 await sc('打开“我的”',async()=>{await p.click('.tabbar [data-me]');});
 await p.keyboard.press('Escape');await p.waitForTimeout(500);
 await sc('标签→首页',async()=>{await p.click('.tabbar [data-t="welcome"]');},1600);
 console.log('errors',errs.filter(e=>!/ERR_FAILED/.test(e)));await b.close();})();
