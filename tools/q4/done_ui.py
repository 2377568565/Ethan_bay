"""“读完打卡”（2026-11-03 用户要的）：问题彩蛋（和健康文章）读到文末，有一个“我读完了”的按钮；
在这一篇上的阅读时间要超过预估时间的一半才能打卡（例如预估 60 分钟，要读满 30 分钟）。
打卡后：文末盖上金色的“已读完”印章；问题彩蛋 / 健康列表里这一篇换成金色印章编号、带“已读完”标记；列表顶上显示“已读完 N / 总数 篇”。
数据：localStorage q4:tdone = {页面: {s: 读了多少秒, d: 打卡时间, c: 'qa' 或 'health', m: 预估分钟}}；
登录账号后，打卡（d、c）随账号同步（app.js 的 td，两边合并，取较早的打卡时间）；阅读秒数只记在本机。
页面键：独立专题页用网页文件名（heaven.html → heaven），网站里的短文问答用 id（qa1）。
计时：页面看得见、并且 3 分钟内有过滑动、点按、按键（或正在听朗读），每秒加一秒；在网站里打开的短文，要那一篇正在显示才算。"""
import math


def _rosette(cx, cy, r, k=16, amp=2.6):
    pts = []
    for i in range(k * 8):
        a = 2 * math.pi * i / (k * 8)
        rr = r + amp * math.cos(k * a)
        pts.append(f'{cx + rr * math.cos(a):.2f},{cy + rr * math.sin(a):.2f}')
    return 'M' + 'L'.join(pts) + 'Z'


ROSETTE = _rosette(40, 40, 27)
SEAL_SVG = ('<svg class="rd-svg" viewBox="0 0 80 80" aria-hidden="true">'
            '<circle class="rd-trk" cx="40" cy="40" r="37"/>'
            '<circle class="rd-arc" cx="40" cy="40" r="37" pathLength="100" transform="rotate(-90 40 40)"/>'
            f'<path class="rd-ros" d="{ROSETTE}"/>'
            '<circle class="rd-in" cx="40" cy="40" r="20.5"/>'
            '<path class="rd-ck" d="M30.5 40.5l6.5 6.5 13-14" pathLength="1"/>'
            '<path class="rd-lk" d="M34 39v-3.2a6 6 0 0 1 12 0V39M32.5 39h15v10.5h-15z"/></svg>')
MINI_SEAL = (f'<svg viewBox="0 0 80 80" aria-hidden="true"><path d="{ROSETTE}"/>'
             '<path class="ck" d="M29 41l8 8 15-17"/></svg>')


def card(key='', mins=0, col='qa'):
    """文末的“读完打卡”卡片。key、mins 可以空着：专题页由脚本从网址和页面上的“细读约 N 分钟”取。"""
    fx = ''.join(f'<i style="--a:{i * 30}deg;--d:{38 + (i % 3) * 10}px"></i>' for i in range(12))
    return (f'<section class="rdone lock" data-rdone data-key="{key}" data-mins="{mins or ""}" data-col="{col}" aria-label="读完打卡">'
            f'<div class="rd-seal">{SEAL_SVG}<span class="rd-fx" aria-hidden="true">{fx}</span></div>'
            '<div class="rd-b"><p class="rd-k">读完打卡</p><h3 class="rd-h" data-rdh>读到这里，辛苦了</h3>'
            '<p class="rd-m" data-rdm>在这一篇读满预估时间的一半，就可以打卡</p>'
            '<button type="button" class="rd-btn" data-rdbtn disabled><span data-rdbt>再读一会儿</span></button></div></section>')


def donebar(col, total):
    """列表顶上的“已读完 N / 总数 篇”。"""
    return (f'<div class="qdonebar" data-donebar="{col}" data-total="{total}"><span class="qdb-seal">{MINI_SEAL}</span>'
            f'<span class="qdb-t"><span class="qdb-n"><b data-dbn>0</b> / {total} 篇已读完</span><small data-dbm>读完一篇，在文末点“我读完了”打卡</small></span>'
            '<span class="qdb-bar" aria-hidden="true"><i></i></span></div>')


CSS = r'''
.rdone{position:relative;display:flex;gap:18px;align-items:center;margin:40px 0 28px;padding:22px 20px;border:1px solid var(--rule);border-radius:22px;background:var(--surface);overflow:hidden}
.rdone::before{content:"";position:absolute;inset:0;border-radius:inherit;padding:1.5px;background:linear-gradient(135deg,var(--gold),#F0D9A0 35%,transparent 55%,#F0D9A0 80%,var(--gold));-webkit-mask:linear-gradient(#000 0 0) content-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude;opacity:.35;transition:opacity .5s;pointer-events:none}
.rdone.ready::before,.rdone.done::before{opacity:1}
.rdone.done{background:linear-gradient(160deg,var(--gold-soft),var(--surface) 65%)}
.rd-seal{position:relative;flex:0 0 auto;width:88px;height:88px}
.rd-svg{width:100%;height:100%;overflow:visible}
.rd-trk{fill:none;stroke:var(--rule);stroke-width:3}
.rd-arc{fill:none;stroke:var(--gold);stroke-width:3;stroke-linecap:round;stroke-dasharray:100;stroke-dashoffset:var(--off,100);transition:stroke-dashoffset .8s ease}
.rd-ros{fill:var(--gold-soft);stroke:var(--gold);stroke-width:1.2;transition:fill .5s}
.rd-in{fill:var(--surface);stroke:var(--gold);stroke-width:1;stroke-dasharray:2 2.4;transition:fill .5s}
.rd-ck{fill:none;stroke:#fff;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1;opacity:0}
.rd-lk{fill:none;stroke:var(--gold);stroke-width:1.8;stroke-linejoin:round;transition:opacity .3s}
.rdone.ready .rd-lk{opacity:0}
.rdone.ready .rd-in{fill:var(--gold-soft)}
.rdone.ready .rd-ck{opacity:.45;stroke:var(--gold);stroke-dashoffset:0;stroke-width:3.2}
@media print{.rdone{display:none}}
.rdone.done .rd-trk,.rdone.done .rd-arc{opacity:0}
.rdone.done .rd-ros{fill:var(--gold)}
.rdone.done .rd-in{fill:var(--gold);stroke:#F7E7BF;stroke-dasharray:none}
.rdone.done .rd-lk{opacity:0}
.rdone.done .rd-ck{opacity:1;stroke-dashoffset:0}
.rdone.done .rd-svg{transform:rotate(-8deg)}
.rdone.stamp .rd-svg{animation:rdstamp .7s cubic-bezier(.2,1.6,.4,1) both}
.rdone.stamp .rd-ck{transition:stroke-dashoffset .5s .35s ease}
@keyframes rdstamp{0%{transform:scale(1.6) rotate(-20deg);opacity:0}60%{transform:scale(.92) rotate(-6deg);opacity:1}100%{transform:scale(1) rotate(-8deg)}}
.rd-fx{position:absolute;left:50%;top:50%;width:0;height:0;pointer-events:none}
.rd-fx i{position:absolute;left:-3px;top:-3px;width:6px;height:6px;border-radius:50%;background:var(--gold);opacity:0}
.rd-fx i:nth-child(3n){background:#F0D9A0;width:5px;height:5px}
.rd-fx i:nth-child(4n){border-radius:1px;transform:rotate(45deg)}
.rdone.stamp .rd-fx i{animation:rdfx .9s .25s ease-out both}
@keyframes rdfx{0%{opacity:1;transform:rotate(var(--a)) translateY(0) scale(1)}100%{opacity:0;transform:rotate(var(--a)) translateY(calc(var(--d) * -1)) scale(.4)}}
.rd-b{min-width:0;flex:1}
.rd-k{margin:0 0 2px;font:700 .72rem/1.2 var(--sans);letter-spacing:.2em;color:var(--gold)}
.rd-h{margin:0 0 6px;font:800 1.12rem/1.4 var(--serif,serif);color:var(--ink)}
.rd-m{margin:0 0 12px;font-size:.84rem;line-height:1.6;color:var(--ink-2)}
.rd-btn{position:relative;display:inline-flex;align-items:center;justify-content:center;gap:6px;min-height:44px;padding:0 22px;border:1px solid var(--rule);border-radius:999px;background:var(--paper);color:var(--muted);font:700 .92rem/1 var(--sans);cursor:not-allowed;overflow:hidden;-webkit-tap-highlight-color:transparent}
.rdone.ready .rd-btn{border-color:transparent;background:linear-gradient(135deg,#C9A45C,#9A742C);color:#fff;cursor:pointer;box-shadow:0 6px 18px rgba(154,116,44,.35)}
.rdone.ready .rd-btn::after{content:"";position:absolute;top:0;left:0;width:40%;height:100%;background:linear-gradient(100deg,transparent,rgba(255,255,255,.45),transparent);transform:translateX(-120%);animation:rdshine 2.8s ease-in-out infinite}
@keyframes rdshine{0%,55%{transform:translateX(-120%)}100%{transform:translateX(320%)}}
.rdone.ready .rd-btn:active{transform:scale(.97)}
.rdone.done .rd-btn{border-color:transparent;background:none;color:var(--gold);cursor:default;padding:0;min-height:0}
@media (max-width:420px){.rdone{padding:18px 14px;gap:14px}.rd-seal{width:72px;height:72px}.rd-h{font-size:1.02rem}}
@media (prefers-reduced-motion:reduce){.rdone.stamp .rd-svg,.rdone.stamp .rd-fx i,.rdone.ready .rd-btn::after{animation:none}}
/* 列表：读完的一篇 */
.qdonebar{display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto auto;gap:4px 12px;align-items:center;margin:14px 0 6px;padding:12px 16px;border:1px solid var(--rule);border-radius:18px;background:linear-gradient(135deg,var(--gold-soft),transparent 75%)}
.qdb-seal{grid-row:1/3;width:38px;height:38px}
.qdb-seal svg,.qdn-seal svg{width:100%;height:100%;overflow:visible}
.qdb-seal path,.qdn-seal path{fill:var(--gold)}
.qdb-seal path.ck,.qdn-seal path.ck{fill:none;stroke:#fff;stroke-width:6;stroke-linecap:round;stroke-linejoin:round}
.qdonebar.zero .qdb-seal path{fill:none;stroke:var(--gold);stroke-width:2}
.qdonebar.zero .qdb-seal path.ck{stroke:var(--gold);opacity:.35}
.qdb-t{display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 10px;min-width:0}
.qdb-n{font:600 .92rem/1.3 var(--sans);color:var(--ink)}
.qdb-n b{font:800 1.3rem/1 var(--serif,serif);color:var(--gold);font-variant-numeric:tabular-nums}
.qdb-t small{font-size:.76rem;color:var(--muted)}
.qdb-bar{display:block;height:6px;border-radius:99px;background:var(--rule);overflow:hidden}
.qdb-bar i{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#C9A45C,var(--gold));transform-origin:left;transform:scaleX(var(--p,0));transition:transform .8s ease}
.qcard.qrow.qdone{background:linear-gradient(90deg,var(--gold-soft),transparent 80%);box-shadow:inset 3px 0 0 var(--gold);border-radius:0 14px 14px 0;padding-left:10px}
.qcard.qrow.qdone .qno{position:relative}
.qcard.qrow.qdone .qno b{color:var(--gold)}
.qdn-seal{position:absolute;right:-8px;bottom:-12px;width:22px;height:22px;transform:rotate(-12deg)}
.qcard.qrow.qdone.qfresh .qdn-seal{animation:qdnpop .7s .2s cubic-bezier(.2,1.6,.4,1) both}
@keyframes qdnpop{0%{transform:scale(0) rotate(-60deg)}100%{transform:scale(1) rotate(-12deg)}}
.qdn-tag{display:inline-flex;align-items:center;gap:3px;padding:1px 8px;border-radius:999px;background:var(--gold);color:#fff;font-style:normal;font-weight:700}
@media (prefers-reduced-motion:reduce){.qcard.qrow.qdone.qfresh .qdn-seal{animation:none}}
'''

JS = r'''
(function(){
  var K='q4:tdone',SEEN='q4:tdone-seen',IDLE=180000;
  function load(){try{var o=JSON.parse(localStorage.getItem(K)||'{}');return o&&typeof o==='object'?o:{};}catch(e){return {};}}
  function save(o){try{localStorage.setItem(K,JSON.stringify(o));}catch(e){}}
  function count(col){var o=load(),n=0;Object.keys(o).forEach(function(k){if(o[k]&&o[k].d&&(o[k].c||'qa')===col)n++;});return n;}
  function md(t){var d=new Date(t);return (d.getMonth()+1)+'月'+d.getDate()+'日';}
  function keyOfHref(h){if(!h)return '';var m=/^#(qa\d+)$/.exec(h);if(m)return m[1];m=/([\w-]+)\.html(?:[?#].*)?$/.exec(h);return m?m[1]:'';}
  var last=Date.now();
  ['scroll','pointerdown','touchstart','keydown','wheel','mousemove'].forEach(function(e){addEventListener(e,function(){last=Date.now();},{passive:true,capture:true});});
  function listening(){var a=document.querySelectorAll('audio');for(var i=0;i<a.length;i++)if(!a[i].paused)return true;return false;}
  var cards=[];
  function init(el){
    if(el.q4done)return;el.q4done=1;
    var key=el.getAttribute('data-key')||(location.pathname.split('/').pop()||'index').replace(/\.html?$/,'');
    var col=el.getAttribute('data-col')||document.documentElement.getAttribute('data-col')||'qa';if(col!=='health')col='qa';
    var mins=+el.getAttribute('data-mins');
    if(!mins){var mt=document.querySelector('.hero .meta'),mm=mt&&/细读约\s*(\d+)\s*分钟/.exec(mt.textContent);mins=mm?+mm[1]:(+(document.body.getAttribute('data-mins'))||10);}
    var need=Math.max(60,Math.round(mins*60/2)),r=load()[key]||{},secs=r.s||0,dirty=0,lastTxt='';
    var lesson=el.closest('.lesson');
    var h=el.querySelector('[data-rdh]'),m=el.querySelector('[data-rdm]'),bt=el.querySelector('[data-rdbt]'),btn=el.querySelector('[data-rdbtn]');
    function flush(){if(!dirty)return;dirty=0;var o=load(),x=o[key]||{};x.s=Math.max(x.s||0,secs);x.m=mins;o[key]=x;save(o);}
    function ui(force){
      var x=load()[key]||{},st=x.d?'done':(secs>=need?'ready':'lock'),txt;
      if(st==='done'){txt='d';
        if(lastTxt!==txt||force){h.textContent='已读完 · '+md(x.d);m.textContent='这是你读完的第 '+count(x.c||col)+' 篇'+(col==='health'?'健康文章':'问题彩蛋')+'。愿所读的成为你生命里的亮光。';bt.textContent='✓ 已打卡';btn.disabled=true;}}
      else if(st==='ready'){txt='r'+Math.floor(secs/60);
        if(lastTxt!==txt||force){h.textContent='读到这里，辛苦了';m.textContent='已经认真读了 '+Math.max(1,Math.floor(secs/60))+' 分钟，可以打卡了';bt.textContent='我读完了';btn.disabled=false;}}
      else{var left=Math.max(1,Math.ceil((need-secs)/60));txt='l'+left;
        if(lastTxt!==txt||force){h.textContent='读到这里，辛苦了';m.textContent='这一篇预估 '+mins+' 分钟，读满一半就能打卡。已读 '+Math.floor(secs/60)+' 分钟，再读约 '+left+' 分钟';bt.textContent='再读约 '+left+' 分钟';btn.disabled=true;}}
      if(lastTxt!==txt||force){el.classList.toggle('lock',st==='lock');el.classList.toggle('ready',st==='ready');el.classList.toggle('done',st==='done');
        el.style.setProperty('--off',String(100-Math.min(100,Math.round(secs/need*100))));lastTxt=txt;}
      return st;
    }
    function active(){if(document.visibilityState!=='visible')return false;if(lesson&&!lesson.classList.contains('show'))return false;return listening()||Date.now()-last<IDLE;}
    setInterval(function(){if(!active())return;var x=load()[key];if(x&&x.d)return;secs++;dirty++;if(dirty>=10)flush();if(secs===need||secs%60===0)ui();},1000);
    addEventListener('pagehide',flush);document.addEventListener('visibilitychange',function(){if(document.hidden)flush();});
    btn.addEventListener('click',function(){if(ui()!=='ready')return;var o=load(),x=o[key]||{};x.s=Math.max(x.s||0,secs);x.d=Date.now();x.c=col;x.m=mins;o[key]=x;save(o);
      el.classList.add('stamp');ui(true);try{window.q4lamb&&q4lamb.joy&&q4lamb.joy();}catch(e){}
      try{if(window.parent!==window)parent.postMessage({q4:'tdone',k:key},location.origin);}catch(e){}
      setTimeout(function(){el.classList.remove('stamp');},1800);paint();});
    cards.push(ui);ui(true);
  }
  function paint(){
    var o=load(),seen=[];try{seen=JSON.parse(localStorage.getItem(SEEN)||'[]')||[];}catch(e){}var ns=seen.slice();
    [].forEach.call(document.querySelectorAll('#qa .qcard,#health .qcard'),function(a){
      var k=keyOfHref(a.getAttribute('href')),x=o[k],on=!!(x&&x.d);a.classList.toggle('qdone',on);
      var s=a.querySelector('.qdn-seal'),t=a.querySelector('.qdn-tag');
      if(on){if(!s){s=document.createElement('span');s.className='qdn-seal';s.innerHTML=MS;var q=a.querySelector('.qno');if(q)q.appendChild(s);}
        if(!t){t=document.createElement('i');t.className='qdn-tag';var qm=a.querySelector('.qm');if(qm)qm.insertBefore(t,qm.firstChild);}
        t.textContent='✓ 已读完 · '+md(x.d);
        if(ns.indexOf(k)<0){a.classList.add('qfresh');ns.push(k);}}
      else{if(s)s.remove();if(t)t.remove();a.classList.remove('qfresh');}
    });
    if(ns.length!==seen.length)try{localStorage.setItem(SEEN,JSON.stringify(ns));}catch(e){}
    [].forEach.call(document.querySelectorAll('[data-donebar]'),function(b){
      var col=b.getAttribute('data-donebar'),tot=+b.getAttribute('data-total')||1,n=0;
      [].forEach.call(document.querySelectorAll('#'+(col==='health'?'health':'qa')+' .qshelves .qcard'),function(a){var x=o[keyOfHref(a.getAttribute('href'))];if(x&&x.d)n++;});
      b.querySelector('[data-dbn]').textContent=n;b.classList.toggle('zero',!n);
      b.querySelector('.qdb-bar i').style.setProperty('--p',String(Math.min(1,n/tot)));
      var w=col==='health'?'篇健康文章':'篇问题彩蛋';
      b.querySelector('[data-dbm]').textContent=!n?'读完一篇，在文末点“我读完了”打卡':n>=tot?'全部读完了！感谢你一路读下来':n<3?'好的开始，继续读下去':n<10?'已经读完 '+n+' '+w+'，一步一步来':'了不起，已经读完 '+n+' '+w;
    });
    cards.forEach(function(f){f(true);});
  }
  var MS='__MINI__';
  function boot(){[].forEach.call(document.querySelectorAll('[data-rdone]'),init);paint();}
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot);else boot();
  addEventListener('storage',function(e){if(!e.key||e.key===K)paint();});
  addEventListener('hashchange',function(){setTimeout(boot,60);});
  addEventListener('message',function(e){if(e.origin===location.origin&&e.data&&e.data.q4==='tdone')paint();});
  window.Q4Done={load:load,save:save,paint:paint,keyOfHref:keyOfHref};
})();
'''.replace('__MINI__', MINI_SEAL.replace("'", "\\'"))
