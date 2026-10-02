/* 复制文字：优先用剪贴板接口，不行就退回老办法（微信等内置浏览器） */
function q4copy(t){
  function legacy(){var a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.cssText='position:fixed;top:0;left:0;width:1px;height:1px;opacity:0';
    document.body.appendChild(a);a.focus();a.select();try{a.setSelectionRange(0,t.length);}catch(e){}var ok=false;try{ok=document.execCommand('copy');}catch(e){}document.body.removeChild(a);return ok;}
  if(navigator.clipboard&&window.isSecureContext){return navigator.clipboard.writeText(t).then(function(){return true;},function(){return legacy();});}
  return Promise.resolve(legacy());
}
(function(){
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);return true;}catch(e){return false;}}
  document.querySelectorAll('.acts input[data-k]').forEach(function(el){
    if(get(el.dataset.k)==='1')el.checked=true;
    el.addEventListener('change',function(){set(el.dataset.k,el.checked?'1':'0');});
  });
  document.querySelectorAll('.my textarea[data-k]').forEach(function(el){
    var v=get(el.dataset.k); if(v){el.value=v;var d=el.closest('details');if(d)d.open=true;}
    var note=el.parentNode.querySelector('.saved'),t;
    el.addEventListener('input',function(){clearTimeout(t);t=setTimeout(function(){if(note)note.textContent=set(el.dataset.k,el.value)?'已保存在本机':'此浏览器无法保存';},400);});
  });

  /* ---------- 按设备日期：本周学课 / 今日 / 安息日课堂 ---------- */
  var KEYS=['sab','sun','mon','tue','wed','thu','fri'],DN=['安息日','星期日','星期一','星期二','星期三','星期四','星期五'],NL=13;
  var START=new Date(2026,8,26,12),now=new Date(),fake=/[?&]today=(\d{4})-(\d{1,2})-(\d{1,2})/.exec(location.search);
  if(fake)now=new Date(+fake[1],+fake[2]-1,+fake[3],12);
  var today=new Date(now.getFullYear(),now.getMonth(),now.getDate(),12),diff=Math.round((today-START)/864e5);
  // 第N课的学习周：从学课目录上的起始日（安息日下午）一直到下一个安息日（安息日学课堂那一天）
  var NO=(diff>=0&&diff<=7*NL)?(diff===0?1:Math.floor((diff-1)/7)+1):0,dd=NO?diff-7*(NO-1):-1;
  var D={no:NO,before:diff<0,after:diff>7*NL,sabbath:dd===7,next:(dd===7&&NO<NL)?NO+1:0,m:today.getMonth()+1,d:today.getDate()};
  D.key=NO?(dd===7?'sum':KEYS[dd]):null; D.dn=['星期日','星期一','星期二','星期三','星期四','星期五','安息日'][today.getDay()];
  window.Q4Today=D;
  if(D.no&&document.getElementById('l'+D.no)){
    var pre='l'+D.no+'-';
    document.querySelectorAll('a[href="#'+pre+D.key+'"],a[href="#'+pre+'yw-'+D.key+'"]').forEach(function(a){if(a.closest('.nav'))a.classList.add('today');});
    [pre+D.key,pre+'yw-'+D.key].forEach(function(id){
      var w=document.querySelector('#'+id+' .when');
      if(w){var s=document.createElement('span');s.className='todaytag';s.textContent='✦ 今天';w.appendChild(s);}
    });
  }
  document.querySelectorAll('.card[href]').forEach(function(c){
    var n=+c.getAttribute('href').slice(2);
    if(D.no&&n===D.no){c.classList.add('now');var w=c.querySelector('.wk');if(w)w.hidden=false;}
    if(D.next&&n===D.next){c.classList.add('class-today');var g=c.querySelector('.ctag');if(g)g.hidden=false;}
  });

  /* ---------- 本周研读时间（每台设备各记各的；登录账号后，欢迎页显示所有设备加起来的时间；每周从安息日算起） ---------- */
  var GOAL=3600;
  function ymd(x){return x.getFullYear()+'-'+('0'+(x.getMonth()+1)).slice(-2)+'-'+('0'+x.getDate()).slice(-2);}
  function wkKey(){var x=new Date();x=new Date(x.getFullYear(),x.getMonth(),x.getDate());x.setDate(x.getDate()-((x.getDay()+1)%7));return 'time:'+ymd(x);}
  var WK=wkKey(),secs=+(get(WK)||0),last=Date.now(),act=Date.now();
  function goals(){try{return JSON.parse(get('goals')||'[]');}catch(e){return [];}}
  function others(){var f=window.Q4Ext&&Q4Ext.weekSecs;return f?(+f(WK)||0):0;}   // 账号里其他设备本周读的秒数
  function total(){return secs+others();}
  window.Q4Week={key:function(){return WK;},secs:function(){return secs;},paint:function(){if(W&&!W.hidden)paintTime();}};
  function tick(){
    var n=Date.now(),dt=Math.min(n-last,20000);last=n;
    WK=wkKey(); secs=+(get(WK)||0);
    if(document.visibilityState==='hidden'||n-act>10*60e3)return;
    var before=total(); secs+=dt/1000; set(WK,Math.round(secs*10)/10);
    if(before<GOAL&&total()>=GOAL){
      var g=goals(); if(g.indexOf(WK)<0){g.push(WK);set('goals',JSON.stringify(g));}
      var t=document.getElementById('wtoast'); if(t){t.hidden=false;setTimeout(function(){t.hidden=true;},7000);}
    }
  }
  ['scroll','wheel','pointerdown','pointermove','keydown','touchstart','input'].forEach(function(e){window.addEventListener(e,function(){act=Date.now();},{passive:true});});
  document.addEventListener('visibilitychange',function(){if(document.visibilityState==='hidden'){tick();}else{last=Date.now();act=Date.now();}});
  window.addEventListener('pagehide',tick);
  setInterval(tick,15000);

  var linkFor={};
  function keepVisible(a){
    var row=a.parentNode; if(row.scrollWidth<=row.clientWidth)return;
    var rr=row.getBoundingClientRect(),ar=a.getBoundingClientRect(),lab=row.querySelector('.k'),lw=lab?lab.getBoundingClientRect().width+10:0;
    if(ar.left<rr.left+lw){row.scrollBy({left:ar.left-rr.left-lw,behavior:'smooth'});}
    else if(ar.right>rr.right){row.scrollBy({left:ar.right-rr.right+8,behavior:'smooth'});}
  }
  var io=('IntersectionObserver' in window)?new IntersectionObserver(function(es){es.forEach(function(e){
    if(!e.isIntersecting)return; var a=linkFor[e.target.id]; if(!a)return;
    var nav=a.closest('.nav'); nav.querySelectorAll('a.on').forEach(function(x){x.classList.remove('on');});
    a.classList.add('on'); keepVisible(a);
  });},{rootMargin:'-15% 0px -75% 0px'}):null;
  document.querySelectorAll('.nav a[href^="#"]').forEach(function(a){
    var id=a.getAttribute('href').slice(1),t=document.getElementById(id);
    if(t){linkFor[id]=a;if(io)io.observe(t);}
  });
  /* ---------- 原文 ⇄ 解读：远距离跳转用“翻页”，近距离平滑滚动 ---------- */
  var reduced=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches,page=document.querySelector('.page');
  function flash(t){
    var f=(t.matches('section,article')&&t.querySelector('header'))||t;
    f.classList.remove('flash');void f.offsetWidth;f.classList.add('flash');
    setTimeout(function(){f.classList.remove('flash');},1900);
  }
  function turnTo(t){
    var r=t.getBoundingClientRect(),de=document.documentElement;
    if(reduced||Math.abs(r.top)<innerHeight*1.2){t.scrollIntoView({behavior:reduced?'auto':'smooth'});flash(t);return;}
    var fwd=r.top>0,box=t.closest('main')||page,jump=function(){de.style.scrollBehavior='auto';t.scrollIntoView();de.style.scrollBehavior='';};
    // 只让正文区翻页；顶部/侧边两排导航不参与动画，始终固定不动
    box.style.setProperty('--tx',fwd?'-7%':'7%');box.style.setProperty('--tin',fwd?'7%':'-7%');
    box.style.setProperty('--ry',fwd?'5deg':'-5deg');box.style.setProperty('--ryin',fwd?'-5deg':'5deg');
    box.classList.remove('turn-in');box.classList.add('turn-out');
    setTimeout(function(){
      box.style.transition='none';box.classList.remove('turn-out');jump();void box.offsetWidth;box.style.transition='';box.classList.add('turn-in');
      setTimeout(function(){box.classList.remove('turn-in');},340);flash(t);
    },160);
  }
  document.addEventListener('click',function(e){
    if(e.defaultPrevented||e.button!==0||e.metaKey||e.ctrlKey||e.shiftKey||e.altKey)return;
    var a=e.target.closest('a[href^="#"]'); if(!a||a.closest('#welcome'))return;
    var id=decodeURIComponent(a.getAttribute('href').slice(1)),t=id&&document.getElementById(id);
    if(!t||!t.getClientRects().length)return;          // 目标在另一课（隐藏中），交给路由
    e.preventDefault();
    if(location.hash!=='#'+id){try{history.pushState(null,'','#'+id);}catch(err){}}
    turnTo(t);
  });

  if(!document.body.classList.contains('combined'))return;

  /* ---------- 全季合集：路由 ---------- */
  var home=document.getElementById('home'),cur=null,W=document.getElementById('welcome');
  var T0=document.title;
  function route(){
    var h=decodeURIComponent(location.hash.slice(1)),m=/^(l\d+|qa\d*|ask|music)(?:-|$)/.exec(h);
    var want=(m&&document.getElementById(m[1]))||home;
    if(cur===want)return;
    var first=!cur,t=(m&&h!==m[1])?document.getElementById(h):null;
    document.title=(want.dataset&&want.dataset.title)||T0;
    var de=document.documentElement,go=function(){ if(t){t.scrollIntoView();}else{window.scrollTo(0,0);} };
    var swap=function(){
      [home].concat([].slice.call(document.querySelectorAll('.lesson'))).forEach(function(x){x.classList.remove('show');});
      want.classList.add('show'); cur=want; de.style.scrollBehavior='auto'; go();
    };
    swap();
    if(!first&&!reduced){want.style.setProperty('--tin','4%');want.style.setProperty('--ryin','0deg');want.classList.remove('turn-in');void want.offsetWidth;want.classList.add('turn-in');setTimeout(function(){want.classList.remove('turn-in');},340);}
    if(window.requestAnimationFrame)requestAnimationFrame(go);
    if(want.id==='ask'&&window.q4ask)window.q4ask.open();
    maybeReward();
    setTimeout(function(){go();de.style.scrollBehavior='';},120);
  }
  window.addEventListener('hashchange',route);
  document.querySelectorAll('select[data-go]').forEach(function(s){s.addEventListener('change',function(){location.hash='l'+s.value;});});
  route();

  /* ---------- 欢迎页 ---------- */
  if(!W)return;
  var pool=[].slice.call(W.querySelectorAll('.vpool li')),vi=-1;
  function titleOf(n){var c=document.querySelector('.card[href="#l'+n+'"] .ct');return c?c.textContent:'';}
  function dayTitle(n,k){var a=document.querySelector('#l'+n+' .navrow[data-row="jd"] a[href="#l'+n+'-'+k+'"] .t');return a?a.textContent:'';}
  function verse(){
    if(!pool.length)return;
    var lastV=+(get('wv')||-1),i;
    do{i=Math.floor(Math.random()*pool.length);}while(pool.length>1&&(i===vi||i===lastV));
    vi=i;set('wv',i);var li=pool[i];
    W.querySelector('.wvt').textContent='“'+li.textContent+'”';
    W.querySelector('.wvr').innerHTML='';
    var r=W.querySelector('.wvr'),a=document.createElement('a');
    r.appendChild(document.createTextNode('—— '+li.dataset.r+' · 出自'));
    a.href='#l'+li.dataset.l;a.textContent='第'+li.dataset.l+'课《'+li.dataset.t+'》';r.appendChild(a);
  }
  function fill(){
    tick();
    var go=W.querySelector('#wgo'),dt=W.querySelector('.wdate'),cl=W.querySelector('.wclass');
    function btn(a,b){go.querySelector('.l1').textContent=a;go.querySelector('.l2').textContent=b;}
    var dstr='今天是 <b>'+D.m+'月'+D.d+'日 '+D.dn+'</b>';
    if(D.no){
      dt.innerHTML=dstr+' · 本周学课：第'+D.no+'课';
      go.href='#l'+D.no+'-'+(D.key==='sum'?'':'yw-')+D.key;   // 先读当天的学课原文；读完打卡后，需要时再看解读
      if(D.sabbath)btn('今日安息日学课堂 →','第'+D.no+'课《'+titleOf(D.no)+'》· 知信行与讨论');
      else btn('进入今日学课 →','第'+D.no+'课《'+titleOf(D.no)+'》· '+(D.key==='sab'?'导言':D.dn));
    }else if(D.before){
      dt.innerHTML=dstr+' · 本季学课将于 <b>9月26日</b> 开始';
      go.href='#l0'; btn('先读本季导言 →','《预言的恩赐》导言与全季总览');
    }else{
      dt.innerHTML=dstr+' · 本季学课已经学完';
      go.href='#home'; btn('本季已学完 →','回顾全季十三课');
    }
    if(D.next){cl.hidden=false;var ca=cl.querySelector('a');ca.href='#l'+D.next+'-yw-sab';ca.textContent='今天下午开始新课：第'+D.next+'课《'+titleOf(D.next)+'》';}
    paintTime();
    verse();
  }
  function paintTime(){
    var all=total(),mins=Math.floor(all/60),h=Math.floor(mins/60),mm=mins%60;
    W.querySelector('.wmin').textContent=(h?h+' 小时 ':'')+mm+' 分钟';
    var lit=Math.min(12,Math.floor(all/300));
    W.querySelectorAll('.wstars i').forEach(function(s,j){s.classList.toggle('on',j<lit);});
    W.style.setProperty('--p',Math.min(1,all/GOAL).toFixed(3));
    var glory=all>=GOAL; W.classList.toggle('glory',glory);
    W.querySelector('.m0').hidden=glory; W.querySelector('.m1').hidden=!glory;
    if(glory){var g=goals();if(g.indexOf(WK)<0){g.push(WK);set('goals',JSON.stringify(g));}W.querySelector('.wn').textContent=g.length;}
  }
  function open(){fill();W.hidden=false;W.classList.remove('leaving');document.documentElement.classList.add('wopen');W.scrollTop=0;setTimeout(function(){W.focus({preventScroll:true});},60);}
  function close(toHome){
    W.classList.add('leaving');document.documentElement.classList.remove('wopen');
    setTimeout(function(){W.hidden=true;},550);
    if(toHome){var c=document.querySelector('.card.now');if(c&&home.classList.contains('show'))setTimeout(function(){c.scrollIntoView({block:'center',behavior:'smooth'});},250);}
  }
  W.addEventListener('click',function(e){
    var a=e.target.closest('a[href^="#"]');
    if(a){var h=a.getAttribute('href');close(h==='#home');if(location.hash===h)e.preventDefault();return;}
    if(e.target.closest('[data-wclose]'))close(true);
    if(e.target.closest('.wshuf:not(.wimg)'))verse();
  });
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!W.hidden)close(true);});
  window.addEventListener('hashchange',function(){if(!W.hidden&&location.hash&&location.hash!=='#home')close(false);});
  document.querySelectorAll('[data-welcome]').forEach(function(b){b.addEventListener('click',function(e){e.preventDefault();open();});});

  /* ---------- 随时返回主页（欢迎页）：点一下直接打开；关掉欢迎页（或点“继续上次阅读”）就回到原来的位置 ---------- */
  var fab=document.querySelector('.fab');
  document.addEventListener('click',function(e){
    if(!e.target.closest('[data-gohome]'))return;
    e.preventDefault();e.stopPropagation();
    if(fab)fab.classList.remove('on');
    if(window.Q4Remember)window.Q4Remember();   // 先记下正在读的段落
    open();
  },true);
  if(fab){
    // 一直显示（老人家也找得到）：往下读时变成半透明的“玻璃”，不挡字；往上滑慢慢恢复全色；宽屏在正文右侧空白处，一直全色
    var wide=window.matchMedia?matchMedia('(min-width:1360px)'):{matches:false},lastY=window.scrollY;
    var glass=function(v){if(fab.classList.contains('glass')!==v)fab.classList.toggle('glass',v);};
    var hold=0;
    fab.classList.add('on');
    window.addEventListener('hashchange',function(){hold=Date.now()+1200;glass(false);});   // 刚跳到新的一段：先全色显示，开始往下读再变透明
    addEventListener('scroll',function(){
      var y=window.scrollY,dy=y-lastY;lastY=y;
      if(!W.hidden||Date.now()<hold)return;
      if(wide.matches||y<160||y+innerHeight>document.documentElement.scrollHeight-200){glass(false);return;}
      if(dy>4)glass(true);else if(dy<-4)glass(false);
    },{passive:true});
  }

  /* ---------- 分享：微信分享 / 复制链接 / 系统分享；电脑上显示二维码 ---------- */
  var SH=document.getElementById('shsheet'),WG=document.getElementById('wxguide'),GF=document.getElementById('gift'),GP=[],lastG=-1;
  try{GP=JSON.parse(document.getElementById('giftpool').textContent);}catch(err){}
  var UA=navigator.userAgent,inWx=/MicroMessenger/i.test(UA),mobile=/Android|iPhone|iPad|iPod|Mobile|HarmonyOS|OpenHarmony/i.test(UA);
  var shUrl='',shTitle='',shT=null;
  function markShared(){set('sharePending','1');}
  var shKind='';
  function shText(){return (shKind==='music'?'【音乐】':'【问题彩蛋】')+shTitle+'\n'+shUrl;}
  function shDone(html,sent){SH.querySelector('.sh-done').innerHTML=html;SH.querySelector('.sh-sent').hidden=!sent;}
  function shOpen(id){
    var pg=document.getElementById(id),isList=id==='qa';shKind=/^music/.test(id)?'music':'';
    shTitle=isList?'学课问题深度解答合集':(pg&&pg.dataset.title||document.title).replace(/ · 问题彩蛋$/,'').replace(/ · 音乐$/,'');
    shUrl=(SH.dataset.base||location.href.split('#')[0])+'#'+id;
    SH.querySelector('#sh-h').textContent=isList?'分享问题彩蛋':(id==='ask'?'分享提问区':'分享这篇问答');
    if(id==='ask')shTitle='提问区：读学课有问题，一起来问';
    if(shKind){SH.querySelector('#sh-h').textContent=id==='music'?'分享音乐栏目':'分享这首音乐';if(id==='music')shTitle='音乐：学课之余，听一首诗歌';}
    SH.querySelector('.sh-t').textContent='“'+shTitle+'”';SH.querySelector('.sh-url').textContent=shUrl;
    SH.querySelector('[data-shsys]').hidden=!(navigator.share&&!inWx);
    var qr=SH.querySelector('.sh-qr'),src=document.querySelector('.sh-qrs svg[data-for="'+id+'"]');
    qr.hidden=mobile||!src;if(src){var box=SH.querySelector('.sh-qrimg');box.innerHTML='';box.appendChild(src.cloneNode(true));}
    shDone('',false);
    clearTimeout(shT);SH.hidden=false;void SH.offsetWidth;SH.classList.add('open');
  }
  function shClose(then){SH.classList.remove('open');clearTimeout(shT);shT=setTimeout(function(){SH.hidden=true;if(then)then();else maybeReward();},280);}
  function wgClose(){if(WG)WG.hidden=true;}
  // 分享完成：关掉面板/提示，马上打开礼物（在哪一页都行）
  function shared(){markShared();wgClose();if(!SH.hidden)shClose(reward);else reward();}
  if(SH){
    document.addEventListener('click',function(e){
      var b=e.target.closest('[data-share]');
      if(b){e.preventDefault();shOpen(b.dataset.share);return;}
      if(WG&&!WG.hidden){
        if(e.target.closest('[data-wgdone]'))shared();
        else if(e.target.closest('[data-wgcancel]')){set('sharePending','0');wgClose();}
        return;
      }
      if(SH.hidden)return;
      if(e.target.closest('[data-shwx]')){
        if(inWx){markShared();shClose(function(){if(WG)WG.hidden=false;});return;}
        q4copy(shText()).then(function(ok){
          if(mobile){
            markShared();
            shDone(ok?'✓ 链接已复制，正在打开微信……<br>在聊天框里<b>长按 → 粘贴</b>，发送即可':'正在打开微信……请回来长按下面的链接复制',true);
            setTimeout(function(){location.href='weixin://';},450);
          }else{
            if(ok)markShared();
            shDone(ok?'✓ 链接已复制，粘贴到<b>电脑版微信</b>的聊天框发送即可；<br>也可以用手机微信扫上面的二维码':'复制没有成功，请用手机微信扫上面的二维码',ok);
          }
        });
        return;
      }
      if(e.target.closest('[data-shcopy]')){
        q4copy(shText()).then(function(ok){
          if(!ok){shDone('复制没有成功，请长按下面的链接手动复制',false);return;}
          markShared();shDone('✓ 已复制，可以粘贴到微信群里了',true);
        });
        return;
      }
      if(e.target.closest('[data-shsys]')){
        navigator.share({title:shTitle,text:'【问题彩蛋】'+shTitle,url:shUrl}).then(shared).catch(function(){});return;
      }
      if(e.target.closest('[data-shsent]')){shared();return;}
      if(e.target.closest('[data-shclose]'))shClose();
    });
    document.addEventListener('keydown',function(e){if(e.key==='Escape'){if(!SH.hidden)shClose();wgClose();}});
    // 去微信发完、切回来：自动打开礼物
    document.addEventListener('visibilitychange',function(){
      if(document.hidden||get('sharePending')!=='1')return;
      if(!SH.hidden||(WG&&!WG.hidden))setTimeout(shared,250);else reward();
    });
  }

  /* ---------- 分享之后的经文礼物 ---------- */
  function maybeReward(){          // 有没领的礼物，回到“问题彩蛋”页时补上
    if(!GF||get('sharePending')!=='1'||!cur||cur.id!=='qa'||document.hidden)return;
    reward();
  }
  function reward(){
    if(!GF||get('sharePending')!=='1')return;
    if(!W.hidden||(SH&&!SH.hidden)||(WG&&!WG.hidden)||(HC&&!HC.hidden)||!GF.hidden)return;
    set('sharePending','0');
    var n=(+get('shares')||0)+1;set('shares',String(n));
    setTimeout(function(){showGift(n);},300);
  }
  function giftMsg(n){
    if(n===1)return '一个小小的转发，也许正好是别人心里在找的答案。愿这份分享成为祝福。';
    if(n<4)return '这是你第 '+n+' 次分享。你把光传给了身边的人，谢谢你！';
    if(n<7)return '已经分享 '+n+' 次了！“报佳音的人，他们的脚踪何等佳美。”';
    return '已经分享 '+n+' 次！谢谢你一次又一次把好消息传出去，愿主记念你的每一次转发。';
  }
  function showGift(n){
    var i=0;if(GP.length){do{i=Math.floor(Math.random()*GP.length);}while(GP.length>1&&i===lastG);}lastG=i;
    var v=GP[i]||['',''],onList=cur&&cur.id==='qa';
    GF.querySelector('.gift-vt').textContent='“'+v[0]+'”';GF.querySelector('.gift-vr').textContent='—— '+v[1];
    GF.querySelector('h3').textContent=n===1?'你的第一次分享！':'你把好消息传出去了';
    GF.querySelector('.gift-msg').textContent=giftMsg(n);
    GF.querySelectorAll('.gift-stars i').forEach(function(s,j){s.classList.toggle('on',j<Math.min(n,7));s.style.animationDelay=(1+j*0.09)+'s';});
    GF.querySelector('.gift-q').hidden=onList;GF.querySelector('[data-giftstay]').hidden=onList;
    GF.querySelector('[data-giftgo]').innerHTML=onList?'收下礼物 ✦':'去问题彩蛋 ✦';
    GF.querySelector('.gift-btns').classList.toggle('one',onList);
    GF.querySelector('.gift-done').textContent='';
    GF.hidden=false;void GF.offsetWidth;GF.classList.add('open');
    if(!reduced){
      var f=GF.querySelector('.gift-fall');f.innerHTML='';
      for(var k=0;k<24;k++){var sp=document.createElement('span');sp.textContent='✦';
        sp.style.left=(Math.random()*100)+'%';sp.style.fontSize=(10+Math.random()*14)+'px';
        sp.style.animationDuration=(2.8+Math.random()*2.4)+'s';sp.style.animationDelay=(.3+Math.random()*1.4)+'s';
        sp.style.setProperty('--dx',(Math.random()*90-45)+'px');sp.style.setProperty('--rot',(Math.random()*360-180)+'deg');f.appendChild(sp);}
    }
    setTimeout(function(){var b=GF.querySelector('[data-giftgo]');if(b)b.focus({preventScroll:true});},80);
  }
  function hideGift(){GF.classList.remove('open');setTimeout(function(){GF.hidden=true;GF.querySelector('.gift-fall').innerHTML='';},340);}
  if(GF){
    document.addEventListener('click',function(e){
      if(GF.hidden)return;
      if(e.target.closest('[data-giftcopy]')){
        var t=GF.querySelector('.gift-vt').textContent+'（'+GF.querySelector('.gift-vr').textContent.replace(/^——\s*/,'')+'）';
        q4copy(t).then(function(ok){GF.querySelector('.gift-done').textContent=ok?'✓ 经文已复制，可以分享给需要的人':'请长按经文手动复制';});return;
      }
      if(e.target.closest('[data-giftgo]')){e.preventDefault();var go=!(cur&&cur.id==='qa');hideGift();if(go)location.hash='qa';return;}
      if(e.target.closest('[data-giftstay],[data-giftclose]'))hideGift();
    });
    document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!GF.hidden)hideGift();});
    maybeReward();
  }
  if(!location.hash||location.hash==='#home')open();
})();

/* ---------- 经文弹窗：和合本 / NKJV / 原文逐字直译 ---------- */
(function(){
  var src=document.getElementById('bdata'),pop=document.getElementById('bpop');
  if(!src||!pop)return;
  var DATA=null,card=pop.querySelector('.bpop-card'),body=pop.querySelector('.bpop-body'),ttl=pop.querySelector('#bpop-t'),
      tabs=[].slice.call(pop.querySelectorAll('.bpop-tabs button')),last=null,closing=null,de=document.documentElement;
  function data(){if(!DATA&&!src.dataset.src)DATA=JSON.parse(src.textContent);return DATA;}
  // 在线版：经文数据是单独的文件，页面显示后在空闲时预取，点经文时若未到就先显示“加载中”
  var waiting=null,fetching=null;
  function fetchData(){
    if(DATA||fetching||!src.dataset.src)return;
    fetching=fetch(src.dataset.src).then(function(r){if(!r.ok)throw 0;return r.json();}).then(function(j){
      DATA=j; if(waiting&&!pop.hidden)build(parse(waiting.dataset.v)); waiting=null;
    }).catch(function(){fetching=null; if(waiting&&!pop.hidden)body.innerHTML='<p class="bload">经文加载失败，请检查网络后再点一次。</p>'; waiting=null;});
  }
  if(src.dataset.src)setTimeout(fetchData,10000);   // 经文数据有 2.6 MB：网页打开 10 秒后再在后台下载，不和打开网页抢网速
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function parse(code){
    var p=code.split('|'),b=+p[0],vs=p[1].split(';').map(function(x){var q=x.split('.');return [+q[0],+q[1]];});
    return {b:b,vs:vs,more:p[2]==='+'};
  }
  function label(vs){           // [[c,v]...] → "1:27–28；2:16"
    var out=[],i=0;
    while(i<vs.length){
      var c=vs[i][0],a=vs[i][1],j=i;
      while(j+1<vs.length&&vs[j+1][0]===c&&vs[j+1][1]===vs[j][1]+1)j++;
      var s=(out.length&&out[out.length-1].c===c)?String(a):c+':'+a; if(j>i)s+='–'+vs[j][1];
      out.push({c:c,s:s});i=j+1;
    }
    return out.map(function(o){return o.s;}).join(', ').replace(/, (\d+:)/g,'；$1');
  }
  function vlab(vs,c,v){var multi=vs.some(function(x){return x[0]!==vs[0][0];});return multi?c+':'+v:String(v);}
  function build(r){
    var D=data(),bk=D.b[r.b],ot=bk[2]===1,rows=r.vs.map(function(x){return {c:x[0],v:x[1],d:D.v[r.b+'.'+x[0]+'.'+x[1]]};}).filter(function(x){return x.d;});
    ttl.textContent=bk[0]+' '+label(r.vs);
    var allN=rows.every(function(x){return x.d[2]==='N';}),allK=rows.every(function(x){return x.d[2]==='K';});
    tabs[1].textContent=allK?'KJV':(allN?'NKJV':'NKJV / KJV');
    var h='<section class="bs" data-sec="cuv"><h4>和合本<small>上帝版</small></h4>';
    rows.forEach(function(x){h+='<p class="bv"><sup>'+vlab(r.vs,x.c,x.v)+'</sup>'+esc(x.d[0])+'</p>';});
    h+='</section><section class="bs" data-sec="en" lang="en"><h4>'+(allK?'KJV':(allN?'NKJV':'NKJV / KJV'))+'<small>'+esc(bk[1])+' '+label(r.vs)+'</small></h4>';
    rows.forEach(function(x){h+='<p class="bv"><sup>'+vlab(r.vs,x.c,x.v)+'</sup>'+esc(x.d[1])+(x.d[2]==='K'&&!allK?' <em class="kjv">KJV</em>':'')+'</p>';});
    h+='</section><section class="bs" data-sec="og"><h4>'+(ot?'希伯来文':'希腊文')+' · 逐字直译<small>点单词看词典原形与字义</small></h4>';
    rows.forEach(function(x){
      var ws=x.d[3]||[];
      h+='<div class="og"><p class="og-n">'+vlab(r.vs,x.c,x.v)+'</p><div class="og-ws'+(ot?' heb':' grk')+'"'+(ot?' dir="rtl"':'')+'>';
      ws.forEach(function(w,i){h+='<button type="button" class="og-w" data-s="'+esc(w[3])+'" data-i="'+i+'"><span class="o"'+(ot?' lang="he"':' lang="grc"')+'>'+esc(w[0])+'</span><span class="t">'+esc(w[1])+'</span><span class="g" lang="en">'+esc(w[2])+'</span></button>';});
      h+='</div><p class="og-lit" lang="en"><b>英文直译</b>'+esc(ws.map(function(w){return w[2];}).join(' '))+'</p>'+(x.d[4]?'<p class="og-lit zh"><b>中文直译</b>'+esc(x.d[4])+'</p>':'')+'<p class="og-note" hidden></p></div>';
    });
    h+='</section>';
    if(r.more)h+='<p class="bmore">经文较长，此处只显示前16节。</p>';
    body.innerHTML=h; body.scrollTop=0; setTab('cuv');
  }
  function setTab(k){tabs.forEach(function(t){t.classList.toggle('on',t.dataset.sec===k);});}
  function open(el){
    if(closing){clearTimeout(closing);closing=null;}
    if(data())build(parse(el.dataset.v));
    else{ttl.textContent='经文';body.innerHTML='<p class="bload">经文加载中……</p>';waiting=el;fetchData();}
    last=el;
    pop.hidden=false; de.classList.add('bopen');
    var r=el.getBoundingClientRect();
    card.style.transformOrigin=Math.round(r.left+r.width/2-card.offsetLeft)+'px '+Math.round(r.top+r.height/2-card.offsetTop)+'px';
    void card.offsetWidth; pop.classList.add('open');
    setTimeout(function(){card.focus({preventScroll:true});},30);
  }
  function close(){
    if(pop.hidden)return;
    pop.classList.remove('open'); card.style.transform='';
    closing=setTimeout(function(){pop.hidden=true;de.classList.remove('bopen');closing=null;if(last)last.focus({preventScroll:true});},320);
  }
  document.addEventListener('click',function(e){
    var r=e.target.closest('.bref'); if(r&&!r.closest('#bpop')){e.preventDefault();e.stopPropagation();open(r);return;}
    if(e.target.closest('[data-bclose]')){close();return;}
    var t=e.target.closest('.bpop-tabs button');
    if(t){var s=body.querySelector('.bs[data-sec="'+t.dataset.sec+'"]');if(s)body.scrollTo({top:s.offsetTop-body.offsetTop-4,behavior:'smooth'});setTab(t.dataset.sec);return;}
    var w=e.target.closest('.og-w');
    if(w){
      var og=w.closest('.og'),n=og.querySelector('.og-note'),x=(data()||{x:{}}).x[w.dataset.s]||['',''],was=w.classList.contains('sel');
      og.querySelectorAll('.og-w.sel').forEach(function(y){y.classList.remove('sel');});
      if(was){n.hidden=true;return;}
      w.classList.add('sel');
      n.innerHTML='<span class="o">'+esc(x[0]||w.querySelector('.o').textContent)+'</span><span class="s">'+esc(w.dataset.s.replace(/_.*$/,'').replace(/^([HG])0*/,'$1'))+'</span><span lang="en">'+esc(x[1]||'')+'</span>';
      n.hidden=false;
    }
  },true);
  document.addEventListener('keydown',function(e){
    if(!pop.hidden&&e.key==='Escape'){close();return;}
    var r=e.target.closest&&e.target.closest('.bref');
    if(r&&(e.key==='Enter'||e.key===' ')){e.preventDefault();open(r);}
  });
  body.addEventListener('scroll',function(){
    var best='cuv',top=body.scrollTop+40;
    body.querySelectorAll('.bs').forEach(function(s){if(s.offsetTop-body.offsetTop<=top)best=s.dataset.sec;});
    if(body.scrollTop+body.clientHeight>=body.scrollHeight-4){var ss=body.querySelectorAll('.bs');if(ss.length)best=ss[ss.length-1].dataset.sec;}
    setTab(best);
  },{passive:true});
  // 手机：从顶部下拉关闭
  var y0=null,dy=0;
  card.addEventListener('touchstart',function(e){if(e.target.closest('.bpop-body')&&body.scrollTop>0){y0=null;return;}y0=e.touches[0].clientY;dy=0;card.style.transition='none';},{passive:true});
  card.addEventListener('touchmove',function(e){if(y0===null)return;dy=Math.max(0,e.touches[0].clientY-y0);if(dy>0)card.style.transform='translateY('+dy+'px)';},{passive:true});
  card.addEventListener('touchend',function(){if(y0===null)return;card.style.transition='';if(dy>90){close();}else{card.style.transform='';}y0=null;},{passive:true});
})();

/* ---------- 共享数据：提问、回复、讨论、打卡都存在 GitHub（data/ask.json），新消息先经中转站 ntfy 实时送达 ---------- */
window.Q4Hub=(function(){
  var A=window.Q4Ask,cfg=document.querySelector('.askpage');
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);}catch(e){}}
  var TOPIC=(cfg&&cfg.dataset.topic)||'',RELAY=((cfg&&cfg.dataset.relay)||'').replace(/\/+$/,''),DATA=(cfg&&cfg.dataset.data)||'';
  var H={S:null,uid:'',admin:false,relayOk:true,get:get,set:set,online:(cfg&&cfg.dataset.online)||'',
    ok:!!(A&&TOPIC&&RELAY&&DATA&&location.protocol!=='file:'&&window.crypto&&crypto.subtle&&window.TextEncoder&&window.fetch&&window.Promise)};
  var K=null,loading=null,loadedAt=0,subs=[];
  // 上次读到的共享数据（问题、打卡、访问人次等）存在手机里：打开网页先显示它，网上的最新数据到了再更新
  try{var C0=JSON.parse(get('askc')||'null');if(C0&&C0.v===1&&H.ok){H.S=A.norm(C0);H.cached=true;}}catch(e){}
  function saveCache(S){try{var c={};for(var k in S)if(k!=='vault')c[k]=S[k];set('askc',JSON.stringify(c));}catch(e){}}
  function net(p,ms){   // 超时与网络错误统一成 {code}
    return new Promise(function(ok,no){
      var t=setTimeout(function(){no({code:'TIMEOUT'});},ms||20000);
      p.then(function(r){clearTimeout(t);ok(r);},function(e){clearTimeout(t);no(e&&e.code?e:{code:'NETWORK',message:String((e&&e.message)||e)});});
    });
  }
  function lines(t){return String(t||'').split('\n').map(function(l){try{return JSON.parse(l);}catch(e){return null;}}).filter(Boolean);}
  function emit(){subs.forEach(function(f){try{f(H.S);}catch(e){}});}
  function mark(){H.admin=!!(H.uid&&H.S&&H.S.admins.indexOf(H.uid)>=0);}
  H.net=net;
  H.on=function(f){subs.push(f);if(H.S)try{f(H.S);}catch(e){}};
  H.rid=function(p){return A.rid(p);};
  H.why=function(e){return why(e);};
  // 这台设备已经有钥匙时算出身份码（不会新建钥匙）
  H.who=function(){
    if(H.uid||!get('sk')||!H.ok)return Promise.resolve(H.uid);
    return A.keys({get:get,set:set}).then(function(k){K=k;H.uid=k.uid;mark();return H.uid;},function(){return '';});
  };
  // 登录 / 退出账号后换了身份钥匙：清掉缓存，重新算身份码
  H.reset=function(){K=null;H.uid='';H.admin=false;return H.who().then(function(u){mark();emit();return u;});};
  // 要发东西时才生成钥匙（第一次发言、点“我也想知道”、打卡）
  H.ensure=function(){
    if(K)return Promise.resolve(K);
    if(!H.ok)return Promise.reject({code:location.protocol==='file:'?'FILE':(TOPIC&&A?'OLD':'CONFIG')});
    return A.keys({get:get,set:set}).then(function(k){K=k;H.uid=k.uid;mark();return k;});
  };
  // 最新数据 = GitHub 上的存档 + 中转站里还没存档的新消息（中转站只保留 12 小时，存档任务会定时把它们写进 GitHub）
  H.load=function(force){
    if(!H.ok)return Promise.reject({code:location.protocol==='file:'?'FILE':(TOPIC&&A?'OLD':'CONFIG')});
    if(loading)return loading;
    if(!force&&H.S&&Date.now()-loadedAt<20000)return Promise.resolve(H.S);
    loading=net(fetch(DATA+'?t='+Math.floor(Date.now()/30000),{cache:'no-store'}).then(function(r){
      if(r.status===404)return A.empty();if(!r.ok)throw {code:'HTTP_'+r.status};return r.json();
    })).then(function(d){
      var S=A.norm(d||A.empty()),since=S.last?Math.max(0,S.last-120):'12h';
      return net(fetch(RELAY+'/'+TOPIC+'/json?poll=1&since='+since,{cache:'no-store'}).then(function(r){if(!r.ok)throw {code:'HTTP_'+r.status};return r.text();}))
        .then(function(t){H.relayOk=true;return A.merge(S,lines(t));},function(){H.relayOk=false;}).then(function(){return S;});
    }).then(function(S){H.S=S;H.cached=false;loadedAt=Date.now();loading=null;saveCache(S);return H.who();})
      .then(function(){mark();emit();return H.S;},function(e){loading=null;throw e;});
    return loading;
  };
  // 访问计数：打开网页时投一条不带身份的 {h:1}；同一台设备 10 分钟内只算一次；自动测试的浏览器不算
  H.hit=function(){
    if(!H.ok||navigator.webdriver)return;
    var last=+get('hit')||0;if(Date.now()-last<6e5&&Date.now()>last)return;set('hit',String(Date.now()));
    net(fetch(RELAY+'/'+TOPIC,{method:'POST',body:JSON.stringify({h:1,id:A.rid('h')})}).then(function(r){if(!r.ok)throw {code:'HTTP_'+r.status};return r.json();}))
      .then(function(m){if(H.S)return A.merge(H.S,[m]).then(emit);},function(){});
  };
  // 签名后投进中转站，再马上用到本机数据上
  H.post=function(P){
    return H.ensure().then(function(k){return A.sign(k,P);}).then(function(body){
      return net(fetch(RELAY+'/'+TOPIC,{method:'POST',body:body}).then(function(r){if(!r.ok)throw {code:'HTTP_'+r.status};return r.json();}));
    }).then(function(m){
      H.relayOk=true;if(!H.S)H.S=A.empty();
      return A.merge(H.S,[m]).then(function(out){var w=out[0]&&out[0].why;mark();emit();if(w)throw {code:'REJECT',message:w};});
    });
  };
  function why(e){
    var c=String((e&&e.code)||''),m=String((e&&e.message)||'');
    if(c==='FILE')return '这个功能需要联网使用：请用在线版打开 '+H.online;
    if(c==='CONFIG')return '这个功能正在准备中，很快就能使用。';
    if(c==='OLD')return '这个浏览器版本太旧，用不了这个功能。请更新微信或换个浏览器打开。';
    if(c==='REJECT')return ({fast:'发得太快了，请稍等十几秒再发。',limit:'今天发得有点多了，明天再来吧。',spam:'内容里有联系方式、链接或广告词，请修改后再发。',
      closed:'提问者设置了“只要管理员回答”，这个问题不能回复。',gone:'这条内容已经被删除了，请点“刷新”。',notyours:'只能删除自己发的内容。',
      notadmin:'只有管理员能做这件事。',dup:'这条已经发过了。',taken:'这个账号已经有人用了，换一个吧。',noacct:'没有这个账号。',bad:'内容长度不符合要求：问题 4–500 字，回复 2–300 字，讨论回答 2–500 字，称呼 1–16 字。'})[m]||'没有发成功，请刷新后再试。（'+m+'）';
    if(c==='HTTP_429')return '这会儿用的人有点多，请过一分钟再试。';
    if(c==='TIMEOUT'||c==='NETWORK')return '连不上网络，请检查网络后再试。（'+c+'）';
    return '暂时连不上，请稍后再试。（'+(c||m||'未知错误')+'）';
  }
  return H;
})();

/* ---------- 提问区 ---------- */
(function(){
  var P=document.querySelector('.askpage');if(!P)return;
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);}catch(e){}}
  function $(s,r){return (r||P).querySelector(s);}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  var MOCK=/[?&]askmock/.test(location.search),H=window.Q4Hub,net=H.net;
  var ready=false,uid='',QS=[],RS={},filter='all',PAGE=40,more=false,started=false,busy=false;
  var card=$('.askcard'),msg=$('.ask-msg'),list=$('.ask-items');

  /* ---- 连接后台（或测试用的本机模拟） ---- */
  var mock={
    q:function(){try{return JSON.parse(localStorage.getItem('q4:mockdb')||'{"questions":[],"replies":[]}');}catch(e){return {questions:[],replies:[]};}},
    w:function(d){localStorage.setItem('q4:mockdb',JSON.stringify(d));}
  };
  var ME_ADMIN=false;
  function sync(){uid=H.uid;ME_ADMIN=H.admin;}
  function qrow(x){var vs=(H.S&&H.S.votes[x.id])||[];
    return {_id:x.id,name:x.name,loc:x.loc,text:x.text,uid:x.uid,ts:x.ts,allow:x.allow!==false,votes:vs.length,voted:!!uid&&vs.indexOf(uid)>=0,pin:x.pin||0,qa:x.qa||''};}
  function rrow(x){return {_id:x.id,qid:x.qid,name:x.name,loc:x.loc,text:x.text,uid:x.uid,ts:x.ts,admin:!!x.admin};}
  var store={
    init:function(){
      if(MOCK){uid=get('mockuid')||('u'+Math.random().toString(36).slice(2,10));set('mockuid',uid);ME_ADMIN=/[?&]askadmin/.test(location.search);ready=true;return Promise.resolve();}
      return H.ensure().then(function(){return H.load(true);}).then(function(){sync();ready=true;});
    },
    list:function(before){
      if(MOCK){var d=mock.q(),a=d.questions.slice().sort(function(x,y){return y.ts-x.ts;});if(before)a=a.filter(function(x){return x.ts<before;});return Promise.resolve(a.slice(0,PAGE));}
      return (before?Promise.resolve():H.load(true)).then(function(){
        sync();var a=H.S.questions.slice().sort(function(x,y){return y.ts-x.ts;});
        if(before)a=a.filter(function(x){return x.ts<before;});
        return a.slice(0,PAGE).map(qrow);
      });
    },
    replies:function(ids){
      if(!ids.length)return Promise.resolve([]);
      if(MOCK){var d=mock.q();return Promise.resolve(d.replies.filter(function(x){return ids.indexOf(x.qid)>=0;}));}
      return Promise.resolve(H.S.replies.filter(function(x){return ids.indexOf(x.qid)>=0;}).sort(function(x,y){return x.ts-y.ts;}).map(rrow));
    },
    add:function(coll,doc){
      if(MOCK){var d=mock.q();doc.uid=uid;doc.ts=Date.now();doc._id='m'+Date.now()+Math.random().toString(36).slice(2,6);if(coll==='replies')doc.admin=ME_ADMIN;d[coll].push(doc);mock.w(d);return Promise.resolve(doc);}
      var q=coll==='questions',x={op:q?'q':'r',id:H.rid(q?'q':'r'),name:doc.name,loc:doc.loc||'',text:doc.text};
      if(q)x.allow=doc.allow!==false;else{x.qid=doc.qid;x.admin=ME_ADMIN;}
      return H.post(x).then(function(){
        sync();var it=(q?H.S.questions:H.S.replies).filter(function(y){return y.id===x.id;})[0];
        if(!it)throw {code:'REJECT',message:'bad'};return q?qrow(it):rrow(it);
      });
    },
    remove:function(coll,id){
      if(MOCK){var d=mock.q();d[coll]=d[coll].filter(function(x){return x._id!==id;});if(coll==='questions')d.replies=d.replies.filter(function(x){return x.qid!==id;});mock.w(d);return Promise.resolve();}
      return H.post({op:'d',id:H.rid('d'),target:id});
    },
    vote:function(id,on){return H.post({op:'v',id:H.rid('v'),target:id,on:on}).then(sync);},
    pin:function(id,o){o.op='p';o.id=H.rid('p');o.target=id;return H.post(o);}
  };
  function why(e){var c=String((e&&e.code)||'');if(c==='FILE')return '提问区需要联网使用：请用在线版打开 '+P.dataset.online+'#ask';return H.why(e);}


  /* ---- 地区：按网络自动识别到“省 + 市”；开着 VPN 时不乱填；也可以手动选 ---- */
  var MAINLAND=/^(北京|天津|河北|山西|内蒙古|辽宁|吉林|黑龙江|上海|江苏|浙江|安徽|福建|江西|山东|河南|湖北|湖南|广东|广西|海南|重庆|四川|贵州|云南|西藏|陕西|甘肃|青海|宁夏|新疆)/;
  function chinaClock(){try{return /^Asia\/(Shanghai|Chongqing|Chungking|Harbin|Urumqi|Kashgar)$/.test(Intl.DateTimeFormat().resolvedOptions().timeZone||'');}catch(e){return false;}}
  function script(src,charset,ms,read){   // 用 <script> 取第三方的查询结果（JSONP），失败或超时都返回空
    return new Promise(function(ok){
      var s=document.createElement('script'),t=setTimeout(function(){fin('');},ms);
      function fin(v){clearTimeout(t);if(s.parentNode)s.parentNode.removeChild(s);ok(v||'');}
      read(fin,s);if(charset)s.charset=charset;s.onerror=function(){fin('');};s.src=src;document.head.appendChild(s);
    });
  }
  function pconline(){   // 太平洋网络：要用 callback=（JSONP），不要加 json=true，否则返回纯 JSON 会被浏览器拦截
    var cb='q4ip'+Date.now();
    return script('https://whois.pconline.com.cn/ipJson.jsp?callback='+cb,'gbk',6000,function(fin){
      window[cb]=function(d){try{delete window[cb];}catch(e){window[cb]=undefined;}
        var p=(d&&d.pro)||'',ci=(d&&d.city)||'';if(ci===p)ci='';var v=(p+ci).replace(/\s+/g,'');
        if(!v&&d&&d.addr)v=String(d.addr).trim().split(/\s+/)[0]||'';fin(v);};
    });
  }
  function sohu(){       // 搜狐：备用，结果放在全局变量 returnCitySN 里
    return script('https://pv.sohu.com/cityjson?ie=utf-8','',6000,function(fin,s){
      s.onload=function(){var d=window.returnCitySN,v=String((d&&d.cname)||'').replace(/\s+/g,'');fin(/^(CHINA|中国|)$/i.test(v)?'':v);};
    });
  }
  function afterLoad(f){if(document.readyState==='complete')setTimeout(f,0);else addEventListener('load',function(){setTimeout(f,0);});}
  /* 手机定位：浏览器先弹窗问“是否允许获取位置”；同意后把大概位置（约 1 公里）换成“省 + 市”，经纬度本身不保存 */
  var T2S={'臺':'台','灣':'湾','縣':'县','園':'园','東':'东','雲':'云','義':'义','蘭':'兰','蓮':'莲','門':'门','連':'连','區':'区','鄉':'乡','鎮':'镇','國':'国','華':'华','龍':'龙','興':'兴','寧':'宁','廣':'广','陽':'阳','島':'岛','頭':'头','關':'关','開':'开','澤':'泽','濱':'滨','亞':'亚','爾':'尔','聖':'圣','維':'维','納':'纳','約':'约','紐':'纽','倫':'伦','蘇':'苏','邊':'边','漢':'汉','韓':'韩','馬':'马','來':'来','禮':'礼','麗':'丽','歐':'欧','羅':'罗','愛':'爱','臘':'腊','奧':'奥','烏':'乌'};
  function simp(t){return String(t||'').replace(/[\u4e00-\u9fff]/g,function(ch){return T2S[ch]||ch;});}
  function place(cc,prov,city,country){
    cc=(cc||'').toUpperCase();prov=simp(prov);city=simp(city);
    if(cc==='CN'){if(/香港/.test(prov+city))return '香港';if(/澳门/.test(prov+city))return '澳门';return prov?prov+(city&&city!==prov?city:''):'';}
    if(cc==='TW')return '台湾'+(prov||city);
    if(cc==='HK')return '香港';if(cc==='MO')return '澳门';
    return simp(country)+(city||prov);
  }
  function bdc(la,lo){   // BigDataCloud：大陆能到“省 + 市”，台湾到县市
    return net(fetch('https://api.bigdatacloud.net/data/reverse-geocode-client?latitude='+la+'&longitude='+lo+'&localityLanguage=zh').then(function(r){if(!r.ok)throw {code:'HTTP_'+r.status};return r.json();}),10000)
      .then(function(d){var adm=((d&&d.localityInfo)||{}).administrative||[],lv5='';
        adm.forEach(function(x){if(x.adminLevel===5&&!lv5)lv5=x.name||'';});
        return place(d.countryCode,d.principalSubdivision,d.countryCode==='CN'?lv5:d.city,d.countryName);},function(){return '';});
  }
  function osm(la,lo){   // OpenStreetMap：备用
    return net(fetch('https://nominatim.openstreetmap.org/reverse?format=jsonv2&zoom=10&accept-language=zh-CN,zh&lat='+la+'&lon='+lo).then(function(r){if(!r.ok)throw {code:'HTTP_'+r.status};return r.json();}),10000)
      .then(function(d){var a=(d&&d.address)||{},f=function(x){return String(x||'').split(';')[0];},cc=String(a.country_code||'').toUpperCase(),ci=f(a.city||a.town||a.county);
        if(cc==='CN'&&!/市$/.test(ci))ci='';return place(cc,f(a.state||a.province)||(cc==='CN'?ci:''),ci,f(a.country));},function(){return '';});
  }
  function gpsLoc(){
    return new Promise(function(ok){
      if(!navigator.geolocation)return ok({err:'none'});
      setTimeout(function(){ok({err:'fail'});},20000);   // 没理会询问弹窗时，浏览器会一直等；最多等 20 秒
      navigator.geolocation.getCurrentPosition(function(p){ok({la:p.coords.latitude.toFixed(2),lo:p.coords.longitude.toFixed(2)});},
        function(e){ok({err:e&&e.code===1?'deny':'fail'});},{enableHighAccuracy:false,timeout:15000,maximumAge:6e5});
    }).then(function(r){
      if(r.err){if(r.err==='deny')set('asklocgps','no');return {err:r.err};}
      return bdc(r.la,r.lo).then(function(v){return v||osm(r.la,r.lo);}).then(function(v){return v?{v:v}:{err:'name'};});
    });
  }
  var LOC='',LOCSRC='',LOCVPN=false;
  function saveLoc(v,src){LOC=v;LOCSRC=src;set('askloc',v);set('asklocsrc',src);set('asklocat',String(Date.now()));set('asklocman',src==='man'?'1':'');}
  function ipLoc(){
    return pconline().then(function(v){return v||sohu();}).then(function(v){
      LOCVPN=false;v=v.replace(/^(台湾|香港|澳门)(省|特别行政区)/,'$1');
      if(v&&!MAINLAND.test(v)&&chinaClock()){LOCVPN=true;v='';}   // 手机是北京时间、网络却在境外：多半开着 VPN
      return v;
    });
  }
  // 先用手动选的；再用手机定位（30 天内有效，第一次会弹窗询问）；不允许定位就按网络识别
  function findLoc(mode){
    var c=get('askloc')||'',src=get('asklocsrc')||(get('asklocman')==='1'?'man':(c?'ip':'')),age=Date.now()-(+get('asklocat')||0);
    if(!get('asklocat')&&get('asklocday')===new Date().toDateString())age=0;
    if(!mode&&c&&(src==='man'||(src==='gps'&&age<30*864e5)||(src==='ip'&&age<864e5))){LOC=c;LOCSRC=src;return Promise.resolve(c);}
    if(MOCK){LOC=c||'浙江省杭州市';LOCSRC=src||'ip';return Promise.resolve(LOC);}
    var useGps=mode==='gps'||(mode!=='ip'&&get('asklocgps')!=='no');
    return (useGps?gpsLoc():Promise.resolve({err:'skip'})).then(function(g){
      if(g.v){saveLoc(g.v,'gps');return g;}
      if(mode==='gps')return g;   // 是用户点了“用手机定位”：失败就说明原因，不悄悄换成按网络识别
      return ipLoc().then(function(v){if(v)saveLoc(v,'ip');else if(mode){LOC='';LOCSRC='';}else{LOC=c;LOCSRC=src;}return {v:v,err:g.err};});
    });
  }
  function showLoc(){
    var tag={gps:'（手机定位）',ip:'（按网络识别）'}[LOCSRC]||'';
    $('.ask-locv').textContent=LOC?LOC+tag:(LOCVPN?'没认出地区（开着 VPN？）':'地区未识别');
  }
  var LS=null;
  function openLoc(){
    if(!LS){LS=document.querySelector('.locsheet');if(!LS)return;document.body.appendChild(LS);LS.addEventListener('click',locClick);
      LS.addEventListener('keydown',function(e){if(e.key==='Escape')closeLoc();});}
    var sel=LS.querySelector('.loc-pro'),city=LS.querySelector('.loc-city'),pro='';
    var L=LOC.replace(/^(台湾|香港|澳门)(省|特别行政区)/,'$1');
    [].slice.call(sel.options).forEach(function(o){if(o.value&&L.indexOf(o.value)===0&&o.value.length>pro.length)pro=o.value;});
    sel.value=pro;city.value=pro?L.slice(pro.length):'';LS.querySelector('.loc-msg').textContent='';
    LS.hidden=false;void LS.offsetWidth;LS.classList.add('open');setTimeout(function(){sel.focus({preventScroll:true});},60);
  }
  function closeLoc(){LS.classList.remove('open');setTimeout(function(){LS.hidden=true;},220);}
  function locClick(e){
    var t=e.target;
    if(t.closest('[data-locok]')){
      var pro=LS.querySelector('.loc-pro').value,ci=LS.querySelector('.loc-city').value.replace(/\s+/g,'').slice(0,12);
      if(!pro){LS.querySelector('.loc-pro').focus();return;}
      saveLoc(pro==='海外'?(ci||'海外'):pro+(ci&&ci!==pro?ci:''),'man');showLoc();closeLoc();return;
    }
    var mode=t.closest('[data-locgps]')?'gps':t.closest('[data-locauto]')?'ip':'';
    if(mode){
      var m=LS.querySelector('.loc-msg');m.textContent=mode==='gps'?'正在定位……（如果弹出询问，请点“允许”）':'正在按网络识别……';
      findLoc(mode).then(function(r){
        if(r&&r.v){showLoc();closeLoc();return;}
        m.textContent=mode==='gps'?({deny:'没有得到定位权限。可以在手机“设置 → 微信（或浏览器）→ 位置”里允许，或直接在上面选择。',none:'这个浏览器不支持定位，请在上面选择。'}[r&&r.err]||'定位没有成功，请在上面选择地区。'):'没识别出来，请在上面选择地区。';
        showLoc();
      });return;
    }
    if(t.closest('[data-locno]'))closeLoc();
  }

  /* ---- 本机这个身份的提问统计：界面随之变化 ---- */
  function weekStart(){var d=new Date();d.setHours(0,0,0,0);d.setDate(d.getDate()-((d.getDay()+1)%7));return d.getTime();}   // 每周从安息日算起
  function tier(){
    var mine=QS.filter(function(q){return isMine(q);}),ws=weekStart(),wk=mine.filter(function(q){return q.ts>=ws;}).length,n=mine.length;
    var t=n===0?0:(wk>=3?3:(wk>=1?2:1));
    card.className='askcard tier'+t;
    var hi=$('.ask-hi'),st=$('.ask-stats'),bd=$('.ask-badge');
    if(t===0){hi.textContent='第一次来提问？没有“傻问题”，只有愿意追问的心。';st.hidden=true;bd.hidden=true;return;}
    st.hidden=false;st.textContent='你一共提了 '+n+' 个问题 · 本周 '+wk+' 个';
    if(t===1){hi.textContent='欢迎回来！这周有什么新的疑问吗？';bd.hidden=true;}
    else if(t===2){hi.textContent='本周已经问了 '+wk+' 个问题 ✦ 好问题带来好学习，还可以接着问。';bd.hidden=false;bd.textContent='✦ 本周提问者';}
    else{hi.textContent='本周已经问了 '+wk+' 个问题！像庇哩亚人一样“天天考查圣经”（徒17:11）。';bd.hidden=false;bd.textContent='✦✦ 本周追问者';}
    if(n>=10){bd.hidden=false;bd.textContent='✦✦✦ 庇哩亚人 · 已提 '+n+' 问';}
  }
  function isMine(x){return !!uid&&x.uid===uid;}
  function isAdmin(x){return !!x.admin;}

  /* ---- 显示 ---- */
  function fmt(t){if(!t)return '';var d=new Date(t),z=function(n){return (n<10?'0':'')+n;};return d.getFullYear()+'-'+z(d.getMonth()+1)+'-'+z(d.getDate())+' '+z(d.getHours())+':'+z(d.getMinutes());}
  function ts(x){return x.ts||when(x.createdAt);}
  function articles(){return [].slice.call(document.querySelectorAll('.lesson[id^="qa"][data-title]')).filter(function(x){return /^qa\d+$/.test(x.id);})
    .map(function(x){return {id:x.id,t:x.dataset.title.replace(/ · 问题彩蛋$/,'')};});}
  function featLink(q){if(!q.qa)return '';var a=articles().filter(function(x){return x.id===q.qa;})[0];
    return a?'<a class="aq-feat" href="#'+a.id+'">✦ 已整理成问题彩蛋《'+esc(a.t)+'》→</a>':'';}
  function featSelect(q){return '<select data-featsel aria-label="标记已整理成问题彩蛋"><option value="">'+(q.qa?'取消“已整理”标记':'标记已整理成彩蛋…')+'</option>'+
    articles().map(function(a){return '<option value="'+a.id+'"'+(a.id===q.qa?' selected':'')+'>'+esc(a.t)+'</option>';}).join('')+'</select>';}
  function item(q){
    var rs=RS[q._id]||[],adm=rs.filter(isAdmin),mine=isMine(q);
    var h='<article class="aq'+(mine?' mine':'')+(adm.length?' answered':'')+(q.pin?' pinned':'')+'" data-id="'+esc(q._id)+'">'+(q.pin?'<p class="aq-pin">📌 置顶</p>':'')+
      '<header class="aq-h"><span class="aq-av" aria-hidden="true">'+esc((q.name||'友').slice(0,1))+'</span><span class="aq-who"><b>'+esc(q.name||'匿名')+'</b>'+(mine?'<i class="aq-me">我</i>':'')+
      '<span class="aq-meta">'+esc(q.loc||'地区未知')+' · '+esc(fmt(ts(q)))+'</span></span><button type="button" class="aq-copy" data-copyq>复制</button></header>'+
      '<p class="aq-t">'+esc(q.text)+'</p>'+featLink(q)+'<div class="aq-f">';
    if(!MOCK)h+='<button type="button" class="aq-vote'+(q.voted?' on':'')+'" data-vote aria-pressed="'+(q.voted?'true':'false')+'">🙋 我也想知道'+(q.votes?'<b>'+q.votes+'</b>':'')+'</button>';
    if(adm.length)h+='<span class="aq-tag gold">✦ 管理员已回答</span><button type="button" class="aq-img" data-qimg>🖼 生成图片</button>';
    if(q.allow===false)h+='<span class="aq-tag">只要管理员回答</span>';
    h+='<span class="sp"></span>';
    if(q.allow!==false||ME_ADMIN)h+='<button type="button" class="aq-rb" data-reply>回复'+(rs.length?' · '+rs.length:'')+'</button>';
    else if(rs.length)h+='<span class="aq-rc">'+rs.length+' 条回复</span>';
    if(mine||ME_ADMIN)h+='<button type="button" class="aq-del" data-delq>删除</button>';
    h+='</div>';
    if(ME_ADMIN&&!MOCK)h+='<div class="aq-admin"><span>管理：</span><button type="button" data-pin>'+(q.pin?'取消置顶':'📌 置顶')+'</button>'+featSelect(q)+'</div>';
    if(rs.length){h+='<div class="aq-rs">';rs.slice().sort(function(a,b){return isAdmin(b)-isAdmin(a)||ts(a)-ts(b);}).forEach(function(r){
      var ad=isAdmin(r);h+='<div class="aq-r'+(ad?' admin':'')+'" data-rid="'+esc(r._id)+'"><p class="aq-rh"><b>'+esc(ad?(r.name||'整理者'):(r.name||'匿名'))+'</b>'+(ad?'<i class="aq-adm">管理员回答</i>':'')+
        '<span>'+esc(r.loc||'')+' · '+esc(fmt(ts(r)))+'</span>'+((isMine(r)||ME_ADMIN)?'<button type="button" class="aq-rdel" data-delr>删除</button>':'')+'</p><p class="aq-rt">'+esc(r.text)+'</p></div>';});
      h+='</div>';}
    h+='<div class="aq-rf" hidden><textarea maxlength="300" rows="2" placeholder="写下你的回复（300 字以内）"></textarea><button type="button" class="btn solid" data-sendr>发送回复</button><p class="aq-rmsg"></p></div></article>';
    return h;
  }
  function render(){
    var a=QS.filter(function(q){return filter==='mine'?isMine(q):filter==='answered'?(RS[q._id]||[]).some(isAdmin):filter==='hot'?q.votes>0:true;});
    if(filter==='hot')a.sort(function(x,y){return (y.votes-x.votes)||(ts(y)-ts(x));});
    else if(filter==='all')a.sort(function(x,y){return ((y.pin||0)-(x.pin||0))||(ts(y)-ts(x));});   // 置顶的排在最前
    $('.ask-n').textContent=QS.length?'（'+QS.length+(more?'+':'')+'）':'';
    list.innerHTML=a.length?a.map(item).join(''):'<p class="ask-empty">'+(filter==='mine'?'你还没有提过问题。':filter==='answered'?'还没有管理员回答过的问题。':filter==='hot'?'还没有人点过“我也想知道”。看到想知道答案的问题，就点一下吧。':'还没有人提问，来做第一个提问的人吧！')+'</p>';
    $('.ask-more').hidden=!more||filter!=='all';
    var hot=P.querySelector('.chip[data-f="hot"]');if(hot)hot.hidden=MOCK;
    tier();
  }
  function load(append){
    if(busy)return;busy=true;
    var before=append&&QS.length?ts(QS[QS.length-1]):0;
    return store.list(before).then(function(a){
      more=a.length>=PAGE;QS=append?QS.concat(a):a;
      return store.replies(a.map(function(q){return q._id;}));
    }).then(function(rs){if(!append)RS={};rs.forEach(function(r){(RS[r.qid]=RS[r.qid]||[]).push(r);});busy=false;render();})
      .catch(function(e){busy=false;list.innerHTML='<p class="ask-empty err">'+esc(why(e))+'</p>';});
  }

  /* ---- 发问题 / 回复：基本防护 ---- */
  var BAD=/(加微|微信号|vx|v信|威信|QQ群|扣扣|代开|发票|贷款|网贷|博彩|彩票|棋牌|兼职|刷单|返利|https?:\/\/|www\.)/i;
  function check(t,kind){
    if(t.length<(kind==='q'?4:2))return kind==='q'?'问题太短了，再多写几个字吧。':'回复太短了。';
    if(BAD.test(t)||/1[3-9]\d{9}/.test(t))return '内容里有联系方式、链接或广告词，请修改后再发。';
    var day=new Date().toDateString(),k=kind+'day',c=(get(k)||'').split('|');var n=c[0]===day?+c[1]:0;
    if(n>=(kind==='q'?10:30))return '今天发得有点多了，明天再来吧。';
    var last=+(get(kind+'last')||0);if(Date.now()-last<20000)return '发得太快了，请稍等几秒再发。';
    return '';
  }
  function count(kind){var day=new Date().toDateString(),k=kind+'day',c=(get(k)||'').split('|');var n=c[0]===day?+c[1]:0;set(k,day+'|'+(n+1));set(kind+'last',String(Date.now()));}
  function name(){var n=$('.ask-name').value.trim();if(n)set('askname',n);return n;}
  function send(){
    var t=$('.ask-text').value.trim(),n=name(),err;
    if(!ready){msg.textContent='正在连接提问区，请稍等几秒再发。';return;}
    if(!n){msg.textContent='先给自己起个称呼吧（不用真名）。';$('.ask-name').focus();return;}
    if((err=check(t,'q'))){msg.textContent=err;return;}
    var b=$('.ask-send');b.disabled=true;msg.textContent='正在发送……';
    store.add('questions',{text:t,name:n,loc:LOC,allow:$('.ask-allow').checked}).then(function(d){
      count('q');$('.ask-text').value='';$('.ask-count').textContent='0 / 500';b.disabled=false;
      QS.unshift(d);RS[d._id]=[];filter='all';P.querySelectorAll('.ask-filter .chip[data-f]').forEach(function(c){c.classList.toggle('on',c.dataset.f==='all');});render();
      msg.textContent='✓ 已发出！大家都能看到了。';card.classList.add('sent');setTimeout(function(){card.classList.remove('sent');},1200);
      var el=list.querySelector('.aq');if(el)el.classList.add('fresh');
    }).catch(function(e){b.disabled=false;msg.textContent=why(e);});
  }
  function sendReply(art){
    var id=art.dataset.id,ta=art.querySelector('.aq-rf textarea'),m=art.querySelector('.aq-rmsg'),t=ta.value.trim(),n=name()||(ME_ADMIN?'整理者':''),err;
    if(!ready){m.textContent='正在连接提问区，请稍等几秒再发。';return;}
    if(!n){m.textContent='先在上面“你的称呼”里起个名字吧。';return;}
    if((err=check(t,'r'))){m.textContent=err;return;}
    m.textContent='正在发送……';
    store.add('replies',{qid:id,text:t,name:n,loc:LOC}).then(function(d){count('r');(RS[id]=RS[id]||[]).push(d);render();var a=list.querySelector('.aq[data-id="'+id+'"]');if(a){a.querySelector('.aq-rf').hidden=false;a.querySelector('.aq-rmsg').textContent='✓ 回复已发出';}})
      .catch(function(e){m.textContent=why(e);});
  }

  /* ---- 复制 ---- */
  function qText(q,i){
    var s=(i?i+'. ':'')+q.text.replace(/\s*\n\s*/g,' ')+'\n   —— '+(q.name||'匿名')+' · '+(q.loc||'地区未知')+' · '+fmt(ts(q));
    (RS[q._id]||[]).forEach(function(r){s+='\n   └ '+(isAdmin(r)?'【管理员回答】':(r.name||'匿名')+'：')+r.text.replace(/\s*\n\s*/g,' ');});
    return s;
  }
  function flash(el,t){var o=el.textContent;el.textContent=t;el.disabled=true;setTimeout(function(){el.textContent=o;el.disabled=false;},1400);}

  /* ---- 事件 ---- */
  P.addEventListener('click',function(e){
    var t=e.target,art=t.closest('.aq');
    if(t.closest('.ask-send'))return send();
    if(t.closest('.ask-locedit')){openLoc();return;}
    var chip=t.closest('.chip[data-f]');if(chip){filter=chip.dataset.f;P.querySelectorAll('.ask-filter .chip[data-f]').forEach(function(c){c.classList.toggle('on',c===chip);});render();return;}
    if(t.closest('.ask-refresh')){list.innerHTML='<p class="ask-empty">正在刷新……</p>';if(!started||!ready){started=false;open();}else load();return;}
    if(t.closest('.ask-more')){load(true);return;}
    if(t.closest('.ask-copyall')){
      var a=QS.filter(function(q){return filter==='mine'?isMine(q):filter==='answered'?(RS[q._id]||[]).some(isAdmin):filter==='hot'?q.votes>0:true;});
    if(filter==='hot')a.sort(function(x,y){return (y.votes-x.votes)||(ts(y)-ts(x));});
    else if(filter==='all')a.sort(function(x,y){return ((y.pin||0)-(x.pin||0))||(ts(y)-ts(x));});   // 置顶的排在最前
      if(!a.length)return;var b=t.closest('.ask-copyall');
      var s='【预言的恩赐 · 提问区】共 '+a.length+' 个问题（复制于 '+fmt(Date.now())+'）\n\n'+a.map(function(q,i){return qText(q,i+1);}).join('\n\n');
      q4copy(s).then(function(ok){flash(b,ok?'✓ 已复制 '+a.length+' 个问题':'复制失败，请重试');});return;
    }
    if(t.closest('.ask-adminbtn')){
      var s2=ME_ADMIN?('你已经是管理员 ✓\n身份码：'+uid+'\n\n你发的回复会显示为“管理员回答”，也可以删除任何一条问题或回复。'):('你的身份码：\n'+(uid||'（还没连上提问区）')+'\n\n把这串身份码发给网站制作者，绑定之后，你在这里发的回复会显示为“管理员回答”。');
      if(uid)q4copy(uid);window.alert(s2+(uid?'\n\n（身份码已复制）':''));return;
    }
    if(!art)return;
    var q=QS.filter(function(x){return x._id===art.dataset.id;})[0];if(!q)return;
    if(t.closest('[data-copyq]')){var cb=t.closest('[data-copyq]');q4copy(qText(q,0)).then(function(ok){flash(cb,ok?'✓ 已复制':'失败');});return;}
    if(t.closest('[data-vote]')){
      var vb=t.closest('[data-vote]'),on=!q.voted;if(vb.disabled)return;vb.disabled=true;
      store.vote(q._id,on).then(function(){var vs=H.S.votes[q._id]||[];q.votes=vs.length;q.voted=vs.indexOf(uid)>=0;render();},
        function(e){vb.disabled=false;window.alert(why(e));});return;
    }
    if(t.closest('[data-pin]')){
      store.pin(q._id,{pin:!q.pin}).then(function(){var x=H.S.questions.filter(function(y){return y.id===q._id;})[0];q.pin=(x&&x.pin)||0;render();},function(e){window.alert(why(e));});return;
    }
    if(t.closest('[data-reply]')){var f=art.querySelector('.aq-rf');f.hidden=!f.hidden;if(!f.hidden)f.querySelector('textarea').focus();return;}
    if(t.closest('[data-sendr]'))return sendReply(art);
    if(t.closest('[data-delq]')){if(!window.confirm('确定删除这个问题吗？删除后不能恢复。'))return;store.remove('questions',q._id).then(function(){QS=QS.filter(function(x){return x._id!==q._id;});render();}).catch(function(e){window.alert('删除没有成功：'+why(e));});return;}
    var rd=t.closest('[data-delr]');if(rd){var rid=rd.closest('.aq-r').dataset.rid;if(!window.confirm('确定删除这条回复吗？'))return;store.remove('replies',rid).then(function(){RS[q._id]=(RS[q._id]||[]).filter(function(x){return x._id!==rid;});render();}).catch(function(e){window.alert('删除没有成功：'+why(e));});}
  });
  P.addEventListener('change',function(e){
    var sel=e.target.closest('[data-featsel]');if(!sel)return;var art=sel.closest('.aq'),q=QS.filter(function(x){return x._id===art.dataset.id;})[0];if(!q)return;
    store.pin(q._id,{qa:sel.value}).then(function(){q.qa=sel.value;render();},function(e2){window.alert(why(e2));});
  });
  $('.ask-text').addEventListener('input',function(){$('.ask-count').textContent=this.value.length+' / 500';});

  function open(){
    if(started)return;started=true;
    $('.ask-name').value=get('askname')||'';
    afterLoad(function(){findLoc().then(showLoc);});   // 页面加载完再查地区，不拖慢页面（微信顶部进度条）
    store.init().then(function(){load();}).catch(function(e){list.innerHTML='<p class="ask-empty err">'+esc(why(e))+'</p>';started=false;});
  }
  window.q4ask={open:open};
  if(/^#ask(?:-|$)/.test(location.hash))open();
})();

/* ---------- 大家一起：新回答提醒 · 问题彩蛋新文章 · 读完打卡 · 讨论区 ---------- */
(function(){
  var H=window.Q4Hub;if(!H||!document.body.classList.contains('combined'))return;
  var get=H.get,set=H.set,D=window.Q4Today||{};
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
  function fmt(t){var d=new Date(t),z=function(n){return (n<10?'0':'')+n;};return (d.getMonth()+1)+'月'+d.getDate()+'日 '+z(d.getHours())+':'+z(d.getMinutes());}
  var DN={sab:'安息日下午',sun:'星期日',mon:'星期一',tue:'星期二',wed:'星期三',thu:'星期四',fri:'星期五',sum:'安息日课堂'};
  var AB={sab:'安',sun:'日',mon:'一',tue:'二',wed:'三',thu:'四',fri:'五',sum:'课'};

  /* ===== 1. 提醒 ===== */
  var arts=[].slice.call(document.querySelectorAll('.lesson[id^="qa"]')).map(function(x){return x.id;}).filter(function(id){return /^qa\d+$/.test(id);});
  var EXT={};   // 独立网页的问答（例如 history.html）：卡片上有 data-art
  document.querySelectorAll('.qcard[data-art]').forEach(function(c){var id=c.dataset.art;EXT[id]={href:c.getAttribute('href'),title:c.dataset.title||''};if(arts.indexOf(id)<0)arts.push(id);});
  var seenArts=null;try{seenArts=JSON.parse(get('qaseen')||'null');}catch(e){}
  if(!seenArts){seenArts=arts.slice();set('qaseen',JSON.stringify(seenArts));}   // 第一次来：现有的文章都不算“新”
  var unseen=[];
  function newArts(){return arts.filter(function(id){return seenArts.indexOf(id)<0;});}
  function artTitle(id){if(EXT[id])return EXT[id].title;var x=document.getElementById(id);return x&&x.dataset.title?x.dataset.title.replace(/ · 问题彩蛋$/,''):'';}
  function markArt(id){if(arts.indexOf(id)>=0&&seenArts.indexOf(id)<0){seenArts.push(id);set('qaseen',JSON.stringify(seenArts));paint();}}
  function compute(S){
    unseen=[];if(!H.uid||!S)return;
    var mine={},w=+get('rseen')||0;
    S.questions.forEach(function(q){if(q.uid===H.uid)mine[q.id]=1;});
    unseen=S.replies.filter(function(r){return mine[r.qid]&&r.uid!==H.uid&&r.ts>w;});
  }
  function markReplies(){
    if(!H.S)return;var mx=+get('rseen')||0;
    H.S.replies.forEach(function(r){if(r.ts>mx)mx=r.ts;});set('rseen',String(mx));unseen=[];paint();
  }
  function paint(){
    var na=newArts(),nr=unseen.length,adm=unseen.some(function(r){return r.admin;});
    document.querySelectorAll('a.btn.egg[href="#qa"],a.wbtn.egg').forEach(function(a){
      var b=a.querySelector('.nbadge');
      if(na.length||nr){if(!b){b=el('span','nbadge');a.appendChild(b);}b.textContent=nr?String(nr):'新';b.setAttribute('aria-label',nr?nr+' 条新回答':'有新文章');}
      else if(b)b.parentNode.removeChild(b);
    });
    document.querySelectorAll('.qcard[href]').forEach(function(c){c.classList.toggle('isnew',na.indexOf(c.dataset.art||c.getAttribute('href').slice(1))>=0);});
    var ae=document.querySelector('.askentry .ae-t');
    if(ae){var x=ae.querySelector('.ae-new');if(nr){if(!x){x=el('em','ae-new');ae.appendChild(x);}x.textContent='你的问题有 '+nr+' 条新回答'+(adm?'，管理员已回答':'');}else if(x)x.parentNode.removeChild(x);}
    var wn=document.querySelector('#welcome .wnews');
    if(wn){
      var h='';
      if(nr)h+='<a class="wnew" href="#ask"><span class="st">✦</span>你的问题有 <b>'+nr+'</b> 条新回答'+(adm?'，管理员已回答':'')+' →</a>';
      na.forEach(function(id){h+='<a class="wnew" href="'+(EXT[id]?esc(EXT[id].href)+'" data-art="'+id:'#'+id)+'"><span class="st">✦</span>问题彩蛋新文章《'+esc(artTitle(id))+'》→</a>';});
      wn.innerHTML=h;wn.hidden=!h;
    }
  }
  function onRoute(){
    var h=decodeURIComponent(location.hash.slice(1));
    if(/^qa\d+/.test(h))markArt(h.split('-')[0]);
    if(/^ask(-|$)/.test(h)&&H.S)markReplies();
  }
  window.addEventListener('hashchange',onRoute);onRoute();paint();
  document.addEventListener('click',function(e){var a=e.target.closest('a[data-art]');if(a)markArt(a.dataset.art);});

  /* ===== 2. 读完打卡 ===== */
  var CK=/^l\d+-yw-(sab|sun|mon|tue|wed|thu|fri)$/;   // 打卡放在“学课原文”每天的最后；记录仍按 l1-sun 这样的日子
  var cheers=['愿主的话成为你脚前的灯、路上的光。（诗119:105）','“你的言语一解开，就发出亮光。”（诗119:130）','“我将你的话藏在心里，免得我得罪你。”（诗119:11）',
    '“人活着不是单靠食物，乃是靠上帝口里所出的一切话。”（太4:4）','“你们要查考圣经。”（约5:39）','“这些人……天天考查圣经。”（徒17:11）'];
  var days=[].slice.call(document.querySelectorAll('.lesson article.ywday[id],.lesson .day[id]')).filter(function(s){return CK.test(s.id)||/^l\d+-sab$/.test(s.id);});   // 解读的“导言”也有打卡，和原文的安息日下午算同一天
  function ckKey(sec){return sec.id.replace('-yw-','-');}
  function mineCk(k){if(get('ck:'+k)==='1')return true;var u=H.uid&&H.uid.slice(0,12);return !!(u&&H.S&&(H.S.checks[k]||[]).indexOf(u)>=0);}
  function nCk(k){return (H.S&&H.S.checks[k]||[]).length;}
  var CK_SHOW=10;   // 一天的打卡人数达到这么多才显示出来
  days.forEach(function(sec){
    var box=el('div','ckin');box.dataset.ck=ckKey(sec);
    box.innerHTML='<p class="ck-q">这一天的学课读完了吗？</p><button type="button" class="btn solid ck-btn">✓ 读完了，打卡</button><p class="ck-n" aria-live="polite"></p><p class="ck-cheer" hidden></p>';
    var nav=[].slice.call(sec.children).filter(function(x){return x.classList.contains('btnrow');}).pop();   // 放在“查看本日解读 / 下一天原文”按钮的上面
    sec.insertBefore(box,nav||null);
  });
  function paintCk(){
    days.forEach(function(sec){
      var box=sec.querySelector('.ckin');if(!box)return;var k=ckKey(sec),me=mineCk(k),n=Math.max(nCk(k),me?1:0),b=box.querySelector('.ck-btn');
      box.classList.toggle('done',me);b.textContent=me?'✓ 你已打卡':'✓ 读完了，打卡';b.disabled=me;
      box.querySelector('.ck-q').textContent=me?'这一天你已经读完了，真好！':'这一天的学课读完了吗？';
      box.querySelector('.ck-n').innerHTML=H.S&&n>=CK_SHOW?'已有 <b>'+n+'</b> 人读完这一天':'';   // 人少时不显示人数
    });
    weekCard();
  }
  document.addEventListener('click',function(e){
    var b=e.target.closest('.ckin .ck-btn');if(!b||b.disabled)return;
    var box=b.closest('.ckin'),k=box.dataset.ck;
    set('ck:'+k,'1');b.disabled=true;paintCk();   // 先在本机记下，马上有反馈
    var c=box.querySelector('.ck-cheer');c.textContent=cheers[Math.floor(Math.random()*cheers.length)];c.hidden=false;box.classList.add('pop');
    setTimeout(function(){box.classList.remove('pop');},900);
    H.post({op:'c',id:H.rid('c'),k:k}).then(paintCk,function(){/* 没联网也没关系：本机已记下；下次联网再补 */set('ckpend',JSON.stringify(pend().concat([k])));});
  });
  function pend(){try{return JSON.parse(get('ckpend')||'[]');}catch(e){return [];}}
  function flush(){var p=pend();if(!p.length||!H.ok)return;set('ckpend','[]');p.forEach(function(k,i){setTimeout(function(){H.post({op:'c',id:H.rid('c'),k:k}).catch(function(){set('ckpend',JSON.stringify(pend().concat([k])));});},i*400);});}
  // 欢迎页“本周共读”
  function weekCard(){
    var card=document.querySelector('#welcome .wtogether');if(!card)return;
    var no=D.no;if(!no){card.hidden=true;return;}
    var keys=['sab','sun','mon','tue','wed','thu','fri'],mine=0,h='';   // 只显示自己读完了哪几天，不显示人数
    keys.forEach(function(x){var k='l'+no+'-'+x,me=mineCk(k);if(me)mine++;
      h+='<a class="wt-d'+(me?' me':'')+(D.key===x?' today':'')+'" href="#l'+no+'-yw-'+x+'" title="'+DN[x]+(me?' · 已读完':'')+'"><span class="wt-a">'+AB[x]+'</span><span class="wt-n">'+(me?'✓':'·')+'</span></a>';});
    card.querySelector('.wt-days').innerHTML=h;
    card.querySelector('.wt-msg').innerHTML=mine?('第'+no+'课本周你已读完 <b>'+mine+'</b>/7 天'+(mine===7?'，全部读完了，真好！':'，继续加油')):('读完当天的学课原文，记得在最后打卡；读完的日子会在这里打上 ✓');
    card.hidden=false;
  }

  /* ===== 3. 讨论区：把“写下我的回答”分享给大家 ===== */
  var notes=[].slice.call(document.querySelectorAll('.lesson .my textarea[data-k]')).filter(function(t){return /^l\d+-(sab|sun|mon|tue|wed|thu|fri)-[qe]\d+$/.test(t.dataset.k);});
  notes.forEach(function(ta){
    var box=el('div','dsc');box.dataset.dk=ta.dataset.k;
    box.innerHTML='<div class="dsc-bar"><button type="button" class="dsc-tg" aria-expanded="false">💬 大家的回答</button><button type="button" class="dsc-sh">分享我的回答</button></div>'+
      '<div class="dsc-form" hidden><label><span>你的称呼（大家看到的名字，不用真名）</span><input class="dsc-name" maxlength="16"></label>'+
      '<p class="dsc-tip">分享后所有人都能看到这条回答，以及你的称呼和地区（省市）。</p><p class="dsc-btns"><button type="button" class="btn ghost dsc-cancel">取消</button><button type="button" class="btn solid dsc-go">确认分享</button></p></div>'+
      '<p class="dsc-msg" role="status"></p><div class="dsc-list" hidden></div>';
    var my=ta.closest('.my');my.parentNode.insertBefore(box,my.nextSibling);
  });
  function answersOf(k){return H.S?H.S.answers.filter(function(a){return a.k===k;}):[];}
  function votesOf(id){return (H.S&&H.S.votes[id])||[];}
  function paintDsc(box){
    var k=box.dataset.dk,list=answersOf(k),tg=box.querySelector('.dsc-tg'),open=tg.getAttribute('aria-expanded')==='true';
    tg.innerHTML='💬 大家的回答'+(H.S?(list.length?' · <b>'+list.length+'</b>':' · 还没有'):'');
    var L=box.querySelector('.dsc-list');L.hidden=!open;if(!open)return;
    if(!H.S){L.innerHTML='<p class="dsc-empty">正在读取……</p>';return;}
    if(!list.length){L.innerHTML='<p class="dsc-empty">还没有人分享回答。写下你的回答后，点“分享我的回答”，帮助大家一起思考。</p>';return;}
    list=list.slice().sort(function(a,b){return votesOf(b.id).length-votesOf(a.id).length||a.ts-b.ts;});
    L.innerHTML=list.map(function(a){
      var vs=votesOf(a.id),mine=H.uid&&a.uid===H.uid,on=H.uid&&vs.indexOf(H.uid)>=0;
      return '<div class="dsc-a'+(mine?' mine':'')+'" data-aid="'+esc(a.id)+'"><p class="dsc-h"><b>'+esc(a.name)+'</b>'+(mine?'<i>我</i>':'')+'<span>'+esc(a.loc||'')+(a.loc?' · ':'')+esc(fmt(a.ts))+'</span></p>'+
        '<p class="dsc-t">'+esc(a.text)+'</p><p class="dsc-f"><button type="button" class="dsc-v'+(on?' on':'')+'" aria-pressed="'+(on?'true':'false')+'">👍 有帮助'+(vs.length?' <b>'+vs.length+'</b>':'')+'</button>'+
        ((mine||H.admin)?'<button type="button" class="dsc-del">删除</button>':'')+'</p></div>';
    }).join('');
  }
  function paintAll(){document.querySelectorAll('.dsc').forEach(paintDsc);}
  function say(box,t){box.querySelector('.dsc-msg').textContent=t||'';}
  function share(box){
    var ta=document.querySelector('.my textarea[data-k="'+box.dataset.dk+'"]'),text=(ta&&ta.value||'').trim(),name=(box.querySelector('.dsc-name').value||'').trim();
    if(text.length<2){say(box,'先在上面“写下我的回答”里写几句，再分享。');var d=ta&&ta.closest('details');if(d){d.open=true;ta.focus();}return;}
    if(text.length>500){say(box,'回答太长了，分享的部分请控制在 500 字以内。');return;}
    if(!name){box.querySelector('.dsc-name').focus();say(box,'先填一个称呼。');return;}
    set('askname',name);say(box,'正在分享……');
    var go=box.querySelector('.dsc-go');go.disabled=true;
    H.post({op:'a',id:H.rid('a'),k:box.dataset.dk,name:name,loc:get('askloc')||'',text:text}).then(function(){
      go.disabled=false;box.querySelector('.dsc-form').hidden=true;say(box,'✓ 已分享，大家都能看到了。');
      box.querySelector('.dsc-tg').setAttribute('aria-expanded','true');paintDsc(box);
    },function(e){go.disabled=false;say(box,H.why(e));});
  }
  document.addEventListener('click',function(e){
    var box=e.target.closest('.dsc');if(!box)return;var t=e.target;
    if(t.closest('.dsc-tg')){var tg=box.querySelector('.dsc-tg'),o=tg.getAttribute('aria-expanded')!=='true';tg.setAttribute('aria-expanded',o?'true':'false');paintDsc(box);if(o&&!H.S)start(true);return;}
    if(t.closest('.dsc-sh')){var f=box.querySelector('.dsc-form');f.hidden=!f.hidden;say(box,'');var ni=box.querySelector('.dsc-name');if(!ni.value)ni.value=get('askname')||'';if(!f.hidden)(ni.value?box.querySelector('.dsc-go'):ni).focus();return;}
    if(t.closest('.dsc-cancel')){box.querySelector('.dsc-form').hidden=true;say(box,'');return;}
    if(t.closest('.dsc-go')){share(box);return;}
    var a=t.closest('.dsc-a');if(!a)return;var id=a.dataset.aid;
    if(t.closest('.dsc-v')){var vb=t.closest('.dsc-v'),on=vb.getAttribute('aria-pressed')!=='true';vb.disabled=true;
      H.post({op:'v',id:H.rid('v'),target:id,on:on}).then(function(){paintDsc(box);},function(e2){vb.disabled=false;say(box,H.why(e2));});return;}
    if(t.closest('.dsc-del')){if(!window.confirm('确定删除这条回答吗？'))return;
      H.post({op:'d',id:H.rid('d'),target:id}).then(function(){paintDsc(box);},function(e2){say(box,H.why(e2));});}
  });

  /* ===== 读取数据：页面加载完以后再读，不拖慢页面 ===== */
  var started=false;
  function start(force){
    if(!H.ok)return;if(started&&!force)return;started=true;
    H.load(force).then(function(){flush();},function(){paintCk();});
  }
  H.on(function(S){compute(S);if(/^#ask(-|$)/.test(location.hash))markReplies();else paint();paintCk();paintAll();});
  window.Q4Comm={paint:paintCk};   // 账号同步来的打卡马上显示
  // 欢迎页“本站累计访问 N 人次” = 起点（以前不蒜子上的数字）+ 之后的访问
  var vis=document.querySelector('#welcome .wvisits');
  if(vis)H.on(function(S){var n=(S.hits0||+vis.dataset.base||0)+(S.hits||0),sp=vis.querySelector('span');if(n>0){sp.querySelector('b').textContent=n;sp.hidden=false;}});
  paintCk();
  // 脚本在网页最后，运行时页面已经出来了：不等字体、图片全部下载完（网速慢时要好久），马上去读数据
  setTimeout(function(){start(false);},200);setTimeout(H.hit,1500);
})();

/* ---------- 阅读工具：字号 · 夜间模式 · 全文搜索 · 朗读 · 继续上次阅读 ---------- */
(function(){
  if(!document.body.classList.contains('combined'))return;
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);}catch(e){}}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
  var de=document.documentElement,reduced=window.matchMedia&&matchMedia('(prefers-reduced-motion: reduce)').matches;
  function sheet(cls,label,inner){   // 统一样式的弹出面板（沿用“返回主页”确认框的外观）
    var s=el('div','hconf rsheet '+cls);s.setAttribute('role','dialog');s.setAttribute('aria-modal','true');s.setAttribute('aria-label',label);s.hidden=true;
    s.innerHTML='<div class="hconf-bg" data-close></div><div class="hconf-card"><button type="button" class="rs-x" data-close aria-label="关闭">×</button><div class="rs-body">'+inner+'</div></div>';document.body.appendChild(s);
    s.addEventListener('click',function(e){if(e.target.closest('[data-close]'))close(s);});
    s.addEventListener('keydown',function(e){if(e.key==='Escape')close(s);});
    return s;
  }
  function open(s){s.hidden=false;void s.offsetWidth;s.classList.add('open');de.classList.add('sheetopen');}
  function close(s){s.classList.remove('open');de.classList.remove('sheetopen');setTimeout(function(){s.hidden=true;},220);}

  /* ===== 字号与夜间模式 ===== */
  var FS=[[0.9,'小'],[1,'标准'],[1.12,'大'],[1.25,'特大'],[1.4,'超大']],THEMES=[['auto','跟随手机'],['light','白天'],['dark','夜间']],RATES=[['0.8','慢'],['1','正常'],['1.25','快']];
  var RS=sheet('rset','阅读设置','<h3>阅读设置</h3>'+
    '<p class="rs-k">字号</p><div class="rs-seg rs-fs">'+FS.map(function(f,i){return '<button type="button" data-fs="'+f[0]+'" style="font-size:'+(13+i*2)+'px">'+f[1]+'</button>';}).join('')+'</div>'+
    '<p class="rs-prev">“你的话是我脚前的灯，是我路上的光。”（诗119:105）</p>'+
    '<p class="rs-k">夜间模式</p><div class="rs-seg rs-th">'+THEMES.map(function(t){return '<button type="button" data-th="'+t[0]+'">'+t[1]+'</button>';}).join('')+'</div>'+
    '<p class="rs-k">朗读速度</p><div class="rs-seg rs-rate">'+RATES.map(function(r){return '<button type="button" data-rate="'+r[0]+'">'+r[1]+'</button>';}).join('')+'</div>'+
    '<p class="rs-note">这些设置只保存在这台设备上。</p><div class="hconf-btns one"><button type="button" class="ok" data-close>完成</button></div>');
  function fs(){return +(get('fs')||1);}
  function theme(){return get('theme')||'auto';}
  function rate(){return get('rate')||'1';}
  function applyFs(v){if(v===1)de.style.removeProperty('--fs');else de.style.setProperty('--fs',String(v));}
  function applyTh(t){if(t==='light'||t==='dark')de.setAttribute('data-theme',t);else de.removeAttribute('data-theme');}
  function paintRS(){
    RS.querySelectorAll('[data-fs]').forEach(function(b){b.classList.toggle('on',+b.dataset.fs===fs());});
    RS.querySelectorAll('[data-th]').forEach(function(b){b.classList.toggle('on',b.dataset.th===theme());});
    RS.querySelectorAll('[data-rate]').forEach(function(b){b.classList.toggle('on',b.dataset.rate===rate());});
  }
  RS.addEventListener('click',function(e){
    var b=e.target.closest('button');if(!b)return;
    if(b.dataset.fs){set('fs',b.dataset.fs);applyFs(+b.dataset.fs);}
    if(b.dataset.th){set('theme',b.dataset.th);applyTh(b.dataset.th);}
    if(b.dataset.rate){set('rate',b.dataset.rate);if(T.on&&T.u)T.rate=+b.dataset.rate;}
    paintRS();
  });
  applyFs(fs());applyTh(theme());

  /* ===== 工具按钮：和“主页”浮动按钮并排、一样一直显示（往下读时一起变成半透明）；欢迎页、学课目录里也有 ===== */
  var SVG={s:'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="11" cy="11" r="6.5" fill="none" stroke="currentColor" stroke-width="2.2"/><path d="M16 16l4.5 4.5" stroke="currentColor" stroke-width="2.4" stroke-linecap="round"/></svg>',
    a:'<span class="aa" aria-hidden="true">A<small>A</small></span>'};
  var tools=el('div','tools');tools.innerHTML='<button type="button" class="tbtn" data-rsearch aria-label="搜索">'+SVG.s+'</button><button type="button" class="tbtn" data-rsettings aria-label="阅读设置">'+SVG.a+'</button>';
  document.body.appendChild(tools);
  var fab=document.querySelector('.fab');
  function syncTools(){if(!fab)return;var g=fab.classList.contains('glass');tools.querySelectorAll('.tbtn').forEach(function(b){b.classList.toggle('glass',g);});tools.style.setProperty('--fabw',fab.offsetWidth+'px');}
  if(fab&&window.MutationObserver)new MutationObserver(syncTools).observe(fab,{attributes:true,attributeFilter:['class']});
  if(fab&&window.ResizeObserver)new ResizeObserver(syncTools).observe(fab);   // 字号变了，主页按钮变宽，工具按钮跟着让位
  syncTools();
  var wrec=document.querySelector('#welcome .wrec');
  if(wrec){var wt=el('p','wtools','<button type="button" data-rsearch>'+SVG.s+'搜索全季内容</button><button type="button" data-rsettings>'+SVG.a+'字号 · 夜间模式</button>');
    var wb=wrec.querySelector('.wbtns');wb.parentNode.insertBefore(wt,wb.nextSibling);}
  var home=document.getElementById('home');
  if(home){var ht=el('p','hometools','<button type="button" class="btn ghost" data-rsearch>'+SVG.s+'搜索</button><button type="button" class="btn ghost" data-rsettings>'+SVG.a+'字号 · 夜间</button><button type="button" class="btn ghost" data-rresume hidden>📖 继续上次阅读</button>');
    home.insertBefore(ht,home.firstChild);}
  document.addEventListener('click',function(e){
    if(e.target.closest('[data-rsettings]')){e.preventDefault();paintRS();open(RS);}
    else if(e.target.closest('[data-rsearch]')){e.preventDefault();openSearch();}
    else if(e.target.closest('[data-rresume]')){e.preventDefault();resume();}
  });

  /* ===== 在哪里：给搜索结果、继续阅读用的“第几课 · 星期几” ===== */
  var SEC='section.day,article.ywday,article.qna,section.ov';
  function lessonName(L){
    var m=/^l(\d+)$/.exec(L.id);if(m){if(m[1]==='0')return '本季导言';var c=document.querySelector('.card[href="#'+L.id+'"] .ct');return '第'+m[1]+'课'+(c?'《'+c.textContent.trim()+'》':'');}
    if(/^qa\d+$/.test(L.id)){var h=L.querySelector('.qna h1');return '问题彩蛋《'+(h?h.textContent.trim():'')+'》';}
    return L.dataset.title||'';
  }
  function where(x){
    var L=x.closest('.lesson');if(!L)return null;var sec=x.closest(SEC),label=lessonName(L);
    if(sec&&sec.matches('section.day,article.ywday')){var dn=sec.querySelector('.when .dn');label+=' · '+(dn?dn.textContent.trim():'')+(sec.matches('.ywday')?' · 学课原文':'');}
    return {a:(sec&&sec.id)||L.id,label:label,sec:sec||L};
  }
  var BLK='h1,h2,h3,p,li,blockquote,td';
  var SKIP='.lessonbar,.nav,.ckin,.dsc,.my,.btnrow,.qshare,nav,footer,.askpage,.vpool,.cover .from,.when,.yqlink,script,style';   // 和 tts/speech.py 的分段规则一致
  function blocks(root){
    return [].slice.call(root.querySelectorAll(BLK)).filter(function(b){
      if(b.closest(SKIP))return false;if(b.tagName!=='P'&&b.querySelector('p,li'))return false;return true;
    });
  }

  /* ===== 继续上次阅读 ===== */
  var lastSave=0,saveT=null;
  function cur(){var h=decodeURIComponent(location.hash.slice(1));return /^(l\d+|qa\d+)(-|$)/.test(h);}
  function remember(){
    if(!cur()||de.classList.contains('wopen'))return;
    var y=Math.round(innerHeight*0.35),x=document.elementFromPoint(innerWidth/2,y);if(!x)return;
    var w=where(x);if(!w)return;
    var list=blocks(w.sec),i=-1;   // 取屏幕这一高度上的第一段（引文框、列表等都算）
    for(var k=0;k<list.length;k++){var rc=list[k].getBoundingClientRect();if(rc.height&&rc.bottom>y){i=k;break;}}
    if(i<0)return;
    set('resume',JSON.stringify({a:w.a,i:i,label:w.label,ts:Date.now()}));paintResume();
  }
  addEventListener('scroll',function(){clearTimeout(saveT);saveT=setTimeout(remember,700);},{passive:true});
  window.Q4Remember=function(){clearTimeout(saveT);remember();};
  function saved(){try{var r=JSON.parse(get('resume')||'null');return r&&document.getElementById(r.a)?r:null;}catch(e){return null;}}
  function jump(a,target){
    var go=function(){if(target){target.scrollIntoView({block:'center'});target.classList.add('hit');setTimeout(function(){target.classList.remove('hit');},2400);}};
    if(decodeURIComponent(location.hash.slice(1))!==a){location.hash=a;setTimeout(go,420);}else go();
  }
  function resume(){
    var r=saved();if(!r)return;var sec=document.getElementById(r.a);
    var W=document.getElementById('welcome');if(W&&!W.hidden){var x=W.querySelector('[data-wclose]');if(x)x.click();}
    jump(r.a,blocks(sec)[r.i]||null);
  }
  function paintResume(){
    var r=saved(),w=document.querySelector('#welcome .wresume'),hb=document.querySelector('[data-rresume]');
    if(w){if(r){w.innerHTML='<a href="#'+esc(r.a)+'" data-rresume>📖 继续上次阅读：'+esc(r.label)+' →</a>';w.hidden=false;}else w.hidden=true;}
    if(hb)hb.hidden=!r;
  }
  paintResume();
  window.Q4Reader={fs:function(v){applyFs(+v||1);},th:applyTh,resume:paintResume};   // 账号同步来的设置、阅读位置马上生效

  /* ===== 全文搜索 ===== */
  var SS=sheet('rsearch','搜索全季内容','<h3>搜索全季内容</h3><p class="sr-tip">13 课解读、学课原文、问题彩蛋都能搜。多个词用空格分开。</p>'+
    '<form class="sr-f" role="search"><input type="search" class="sr-q" placeholder="例如：但以理 异象" enterkeyhint="search" autocomplete="off"><button type="submit" class="btn solid">搜索</button></form>'+
    '<p class="sr-n" role="status"></p><div class="sr-list"></div><div class="hconf-btns one"><button type="button" data-close>关闭</button></div>');
  var IDX=null;
  function index(){
    if(IDX)return IDX;IDX=[];
    document.querySelectorAll('.lesson').forEach(function(L){
      if(L.id==='ask')return;
      blocks(L).forEach(function(b){var t=b.textContent.replace(/\s+/g,' ').trim();if(t.length<2)return;IDX.push({el:b,t:t,low:t.toLowerCase()});});
    });
    return IDX;
  }
  function snip(t,terms){
    var low=t.toLowerCase(),i=low.indexOf(terms[0]),a=Math.max(0,i-24),s=(a?'…':'')+t.slice(a,a+90)+(a+90<t.length?'…':'');
    var h=esc(s);terms.forEach(function(w){if(!w)return;h=h.replace(new RegExp(esc(w).replace(/[.*+?^${}()|[\]\\]/g,'\\$&'),'gi'),function(m){return '<mark>'+m+'</mark>';});});return h;
  }
  var hits=[];
  function search(q){
    var terms=q.toLowerCase().split(/\s+/).filter(Boolean),n=SS.querySelector('.sr-n'),list=SS.querySelector('.sr-list');
    if(!terms.length){n.textContent='';list.innerHTML='';return;}
    hits=index().filter(function(x){return terms.every(function(w){return x.low.indexOf(w)>=0;});});
    n.textContent=hits.length?'找到 '+hits.length+' 处'+(hits.length>80?'，先显示前 80 处':''):'没有找到。换个说法，或少写几个字试试。';
    var groups=[],last=null;
    hits.slice(0,80).forEach(function(x,i){var w=where(x.el);if(!w)return;if(!last||last.label!==w.label){last={label:w.label,items:[]};groups.push(last);}last.items.push('<button type="button" class="sr-hit" data-i="'+i+'">'+snip(x.t,terms)+'</button>');});
    list.innerHTML=groups.map(function(g){return '<p class="sr-g">'+esc(g.label)+'</p>'+g.items.join('');}).join('');
  }
  SS.querySelector('.sr-f').addEventListener('submit',function(e){e.preventDefault();var q=SS.querySelector('.sr-q');search(q.value);q.blur();set('lastq',q.value);});
  var typing=null;SS.querySelector('.sr-q').addEventListener('input',function(){var v=this.value;clearTimeout(typing);typing=setTimeout(function(){if(v.trim().length>=2)search(v);},350);});
  SS.querySelector('.sr-list').addEventListener('click',function(e){
    var b=e.target.closest('.sr-hit');if(!b)return;var x=hits[+b.dataset.i];if(!x)return;var w=where(x.el);
    close(SS);var W=document.getElementById('welcome');if(W&&!W.hidden){var c=W.querySelector('[data-wclose]');if(c)c.click();}
    var d=x.el.closest('details');if(d)d.open=true;
    jump(w.a,x.el);
  });
  function openSearch(){open(SS);var q=SS.querySelector('.sr-q');if(!q.value&&get('lastq'))q.value=get('lastq');setTimeout(function(){q.focus();if(q.value)q.select();},80);}

  /* ===== 朗读：优先播放预先录好的自然人声（微信里也能听）；没有录音的部分用手机自带的语音 ===== */
  var SY=window.speechSynthesis,canSY=!!(SY&&window.SpeechSynthesisUtterance);
  var AC=document.querySelector('[data-audio]'),AUD=AC?AC.dataset.audio:'',AIDS={},AIDX=null;
  if(AC)(AC.dataset.audioIds||'').split(' ').forEach(function(x){if(x)AIDS[x]=1;});
  function unitId(root){return root.id||((root.closest('.lesson')||{}).id)||'';}
  function fpOf(b){return b.textContent.replace(/\s+/g,'').slice(0,12);}
  function fph(list){var s=list.join('|'),h=0x811c9dc5;for(var i=0;i<s.length;i++){var c=s.charCodeAt(i);h=Math.imul((h^(c&255))>>>0,0x01000193)>>>0;h=Math.imul((h^(c>>>8))>>>0,0x01000193)>>>0;}return ('0000000'+h.toString(16)).slice(-8);}
  if(canSY||AUD){
    var bar=el('div','ttsbar');bar.hidden=true;bar.setAttribute('role','region');bar.setAttribute('aria-label','朗读');
    bar.innerHTML='<i class="tt-pg" aria-hidden="true"><b></b></i><span class="tt-t">正在朗读</span><span class="tt-tm"></span><button type="button" class="tt-pp" aria-label="暂停">❚❚</button><button type="button" class="tt-rate" aria-label="朗读速度"></button><button type="button" class="tt-x" aria-label="停止朗读">✕</button>';
    document.body.appendChild(bar);
    var ppB=bar.querySelector('.tt-pp'),tmS=bar.querySelector('.tt-tm'),pgB=bar.querySelector('.tt-pg b'),ttS=bar.querySelector('.tt-t');
    var T={on:false,mode:'',root:null,title:'',rate:+rate()};
    function setPP(playing){ppB.textContent=playing?'❚❚':'▶';ppB.setAttribute('aria-label',playing?'暂停':'继续');}
    function setRateLabel(){var r=String(T.rate);bar.querySelector('.tt-rate').textContent=(RATES.filter(function(x){return x[0]===r;})[0]||['','正常'])[1]+'速';}
    function inView(b){var r=b.getBoundingClientRect();return r.top>60&&r.bottom<innerHeight-90;}
    function mark(b,scroll){document.querySelectorAll('.speaking').forEach(function(x){x.classList.remove('speaking');});if(b){b.classList.add('speaking');if(scroll!==false&&!inView(b))b.scrollIntoView({block:'center',behavior:reduced?'auto':'smooth'});}}
    function mmss(t){t=Math.max(0,Math.floor(t||0));return Math.floor(t/60)+':'+('0'+t%60).slice(-2);}
    function short(t){return t.replace(/《[^》]*》/,'').replace(/学课原文$/,'原文');}   // 底部条上放得下：第1课 · 星期四 · 原文
    function show(title){ttS.textContent=short(title);tmS.textContent='';pgB.style.width='0';setPP(true);setRateLabel();bar.hidden=false;de.classList.add('ttson');}

    /* --- 录好的声音 --- */
    var A=null,AT=null;   // AT：每段开始的秒数（和网页段落对得上时才有）
    function media(title){
      if(!('mediaSession' in navigator))return;
      try{navigator.mediaSession.metadata=new MediaMetadata({title:title,artist:'预言的恩赐 · 学课朗读',album:'2026年第4季安息日学'});
        navigator.mediaSession.setActionHandler('play',function(){if(A)A.play();});
        navigator.mediaSession.setActionHandler('pause',function(){if(A)A.pause();});
        navigator.mediaSession.setActionHandler('seekbackward',function(){if(A)A.currentTime=Math.max(0,A.currentTime-10);});
        navigator.mediaSession.setActionHandler('seekforward',function(){if(A)A.currentTime=Math.min(A.duration||1e9,A.currentTime+10);});
      }catch(e){}
    }
    function playAudio(root,title,id){
      var list=blocks(root),cur=-1;
      if(!A){A=new Audio();A.preload='auto';
        A.addEventListener('timeupdate',function(){
          if(T.mode!=='a')return;var t=A.currentTime,d=A.duration||0;
          tmS.textContent=mmss(t)+(d?' / '+mmss(d):'');pgB.style.width=(d?Math.min(100,t/d*100):0)+'%';
          if(!AT)return;var i=-1;for(var k=0;k<AT.length;k++){if(AT[k]>=0&&AT[k]<=t+0.15)i=k;}
          if(i!==T.cur){T.cur=i;mark(T.list[i]||null);}
        });
        A.addEventListener('playing',function(){if(T.mode==='a'){ttS.textContent=short(T.title);setPP(true);}});
        A.addEventListener('waiting',function(){if(T.mode==='a')ttS.textContent='正在加载声音……';});
        A.addEventListener('pause',function(){if(T.mode==='a')setPP(false);});
        A.addEventListener('ended',function(){if(T.mode!=='a')return;var r=T.root;stop();var ck=r&&r.querySelector('.ckin');
          if(ck&&!ck.classList.contains('done')){ck.scrollIntoView({block:'center',behavior:reduced?'auto':'smooth'});ck.classList.add('pop');setTimeout(function(){ck.classList.remove('pop');},1600);}});
        A.addEventListener('error',function(){if(T.mode!=='a')return;var r=T.root,ti=T.title;stop();
          if(canSY)speak(r,ti);else window.alert('朗读声音没有加载成功，请检查网络后再试一次。');});
      }
      AT=null;T={on:true,mode:'a',root:root,title:title,rate:+rate(),list:list,cur:-1};
      A.src=AUD+id+'.mp3';A.playbackRate=T.rate;try{A.defaultPlaybackRate=T.rate;}catch(e){}
      show(title);media(title);
      var pr=A.play();if(pr&&pr.catch)pr.catch(function(){if(T.mode==='a')setPP(false);});   // 被浏览器拦下时，点 ▶ 就能开始
      var useMeta=function(m){if(m&&T.mode==='a'&&T.root===root&&m.h===fph(list.map(fpOf))&&m.t&&m.t.length===list.length)AT=m.t;};
      if(AIDX&&AIDX[id])useMeta(AIDX[id]);
      else if(window.fetch)fetch(AUD+id+'.json').then(function(r){return r.ok?r.json():null;}).then(useMeta).catch(function(){});
    }

    /* --- 手机自带的语音（没有录音时） --- */
    var voice=null;
    function pickVoice(){if(!canSY)return;var vs=SY.getVoices()||[];voice=vs.filter(function(v){return /^zh[-_]CN/i.test(v.lang);})[0]||vs.filter(function(v){return /^zh/i.test(v.lang)&&!/HK|TW/i.test(v.lang);})[0]||vs.filter(function(v){return /^zh/i.test(v.lang);})[0]||null;}
    if(canSY){pickVoice();if(SY.addEventListener)SY.addEventListener('voiceschanged',pickVoice);}
    function speakable(t){return t.replace(/(\d+)\s*[:：]\s*(\d+)(?:\s*[-–]\s*(\d+))?/g,function(m,c,v,v2){return c+'章'+v+'节'+(v2?'到'+v2+'节':'');}).replace(/看参考解答|↩\s*回到原文问题|https?[:：]\/\/\S+/g,'').replace(/[→↔✦❚─]/g,'，').replace(/\s+/g,' ').trim();}
    function pieces(t){var out=[];t.replace(/([。！？；])/g,'$1\u0001').split('\u0001').forEach(function(s){if(out.length&&(out[out.length-1]+s).length<120)out[out.length-1]+=s;else out.push(s);});return out.filter(function(s){return s.trim();});}
    function next(){
      if(!T.on||T.mode!=='s')return;if(T.i>=T.q.length){stop();return;}
      var item=T.q[T.i++];mark(item.b);
      var u=new SpeechSynthesisUtterance(item.t);u.lang='zh-CN';try{if(voice)u.voice=voice;}catch(e){}u.rate=T.rate;T.u=u;
      u.onstart=function(){T.started=true;};
      u.onend=function(){if(T.u===u)next();};
      u.onerror=function(e){if(T.u===u&&e.error!=='interrupted'&&e.error!=='canceled')next();};
      SY.speak(u);
    }
    function speak(root,title){
      var q=[];
      blocks(root).forEach(function(b){if(!b.offsetParent)return;pieces(speakable(b.textContent)).forEach(function(t){q.push({b:b,t:t});});});
      if(!q.length)return;T={on:true,mode:'s',root:root,title:title,q:q,i:0,u:null,started:false,rate:+rate()};
      show(title);next();
      setTimeout(function(){if(T.on&&T.mode==='s'&&!T.started&&!SY.speaking){stop();window.alert('这个浏览器暂时不支持朗读。可以换手机自带的浏览器（如 Safari）打开试试。');}},4000);
    }

    function start(root,title){
      stop();var id=unitId(root);try{window.dispatchEvent(new Event('q4:tts'));}catch(e){}
      if(AUD&&AIDS[id])playAudio(root,title,id);else if(canSY)speak(root,title);
    }
    function stop(){
      if(T.mode==='a'&&A){try{A.pause();}catch(e){}}
      if(T.mode==='s'){try{SY.cancel();}catch(e){}}
      T={on:false,mode:'',root:null,title:'',rate:+rate()};AT=null;mark(null);bar.hidden=true;de.classList.remove('ttson');
    }
    bar.addEventListener('click',function(e){
      if(e.target.closest('.tt-x'))stop();
      else if(e.target.closest('.tt-pp')){
        if(T.mode==='a'){if(A.paused){A.play();}else A.pause();}
        else if(T.mode==='s'){if(SY.paused){SY.resume();setPP(true);}else{SY.pause();setPP(false);}}
      }
      else if(e.target.closest('.tt-rate')){var i=RATES.map(function(r){return r[0];}).indexOf(String(T.rate));T.rate=+RATES[(i+1)%RATES.length][0];set('rate',String(T.rate));setRateLabel();
        if(T.mode==='a'){A.playbackRate=T.rate;}
        else if(T.mode==='s'&&T.on){T.i=Math.max(0,T.i-1);T.u=null;SY.cancel();setTimeout(next,60);}}
    });
    // 进度条：点一下跳到那里
    bar.querySelector('.tt-pg').addEventListener('click',function(e){if(T.mode!=='a'||!A.duration)return;var r=this.getBoundingClientRect();A.currentTime=Math.max(0,Math.min(1,(e.clientX-r.left)/r.width))*A.duration;});
    window.addEventListener('hashchange',function(){if(T.on)stop();});
    window.addEventListener('q4:music',function(){if(T.on)stop();});   // 开始放音乐就停止朗读
    // 每一天的解读、每一天的学课原文、每篇问题彩蛋都加一个“朗读”按钮（只有录好声音、或手机支持朗读时才显示）
    var SLOTS=[];
    function addBtn(where,root,title){
      var rec=AUD&&AIDS[unitId(root)],b=root._tts;
      if(!rec&&!canSY)return;
      if(typeof where==='function')where=where();   // 标题下原本没有按钮行（全季总览、本课总结）时，需要时再加一行
      if(!b){b=el('button','btn ttsbtn');b.type='button';b.addEventListener('click',function(){start(root,title);});where.appendChild(b);root._tts=b;}
      b.classList.toggle('rec',!!rec);b.textContent=rec?'🎧 听朗读':'🔊 朗读';
    }
    document.querySelectorAll('section.day').forEach(function(s){
      var h=s.querySelector('.dayhead'),r=h&&h.querySelector('.btnrow'),w=where(s);if(!h||!w)return;
      if(!r)r=function(){var x=h.querySelector('.btnrow');if(!x){x=el('p','btnrow');h.appendChild(x);}return x;};
      SLOTS.push([r,s,w.label+(/^l0-|-sum$/.test(s.id)?'':' · 解读')]);
    });
    document.querySelectorAll('article.ywday').forEach(function(s){var r=s.querySelector('.ywhead .btnrow');var w=where(s);if(r&&w)SLOTS.push([r,s,w.label]);});
    document.querySelectorAll('article.qna').forEach(function(s){var r=s.parentNode.querySelector('.qshare');var w=where(s);var L=s.closest('.lesson');
      if(r&&w)SLOTS.push([r,s,(L&&L.dataset.title?L.dataset.title.replace(/ · 问题彩蛋$/,''):w.label)]);});
    function paintBtns(){SLOTS.forEach(function(x){addBtn(x[0],x[1],x[2]);});}
    paintBtns();
    // 录音是陆续合成上传的：页面打开后再查一次目录，新录好的部分马上出现“听朗读”（不用重新生成网页）
    if(AUD&&window.fetch){
      var loadIdx=function(){fetch(AUD+'index.json',{cache:'no-cache'}).then(function(r){return r.ok?r.json():null;}).then(function(ix){
        if(!ix)return;AIDX=ix;Object.keys(ix).forEach(function(k){AIDS[k]=1;});paintBtns();
      }).catch(function(){});};
      if(document.readyState==='complete')setTimeout(loadIdx,800);else addEventListener('load',function(){setTimeout(loadIdx,800);});
    }
  }
})();

/* ---------- 生成分享图片：经文 · 问题彩蛋文章 · 管理员回答（微信里长按图片即可保存或转发） ---------- */
(function(){
  if(!document.body.classList.contains('combined'))return;
  var cv=document.createElement('canvas');if(!cv.getContext||!cv.toDataURL)return;
  var W=1080,HH=1440,PAD=120;
  var SERIF='"LessonSerif","Noto Serif SC","Source Han Serif SC","Songti SC","STSong","SimSun",serif';
  var SANS=getComputedStyle(document.body).fontFamily||'sans-serif';
  var mobile=/Android|iPhone|iPad|iPod|Mobile|HarmonyOS|OpenHarmony/i.test(navigator.userAgent);
  function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
  function clean(t){return String(t||'').replace(/\s+/g,' ').replace(/\s*([，。、；：！？”’）》])\s*/g,'$1').trim();}

  /* ---- 面板 ---- */
  var SH=el('div','hconf rsheet imgsheet');SH.setAttribute('role','dialog');SH.setAttribute('aria-modal','true');SH.setAttribute('aria-label','分享图片');SH.hidden=true;
  SH.innerHTML='<div class="hconf-bg" data-close></div><div class="hconf-card"><button type="button" class="rs-x" data-close aria-label="关闭">×</button><div class="rs-body"><h3>分享图片</h3><p class="im-tip"></p><div class="im-box"><p class="im-wait">正在生成图片……</p><img class="im-img" alt="分享图片" hidden></div>'+
    '<div class="hconf-btns"><a class="btn im-dl" download="预言的恩赐.jpg" hidden>保存图片</a><button type="button" data-close>关闭</button></div></div></div>';
  document.body.appendChild(SH);
  SH.addEventListener('click',function(e){if(e.target.closest('[data-close]'))close();});
  SH.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
  function open(){SH.querySelector('.im-img').hidden=true;SH.querySelector('.im-wait').hidden=false;SH.querySelector('.im-dl').hidden=true;
    SH.querySelector('.im-tip').textContent=mobile?'图片生成后，长按图片就可以保存，或直接发送给朋友。':'图片生成后，点“保存图片”下载到电脑，再发到微信。';
    SH.hidden=false;void SH.offsetWidth;SH.classList.add('open');document.documentElement.classList.add('sheetopen');}
  function close(){SH.classList.remove('open');document.documentElement.classList.remove('sheetopen');setTimeout(function(){SH.hidden=true;},220);}

  /* ---- 画布工具 ---- */
  function qrImg(id){
    var svg=document.querySelector('.sh-qrs svg[data-for="'+id+'"]')||document.querySelector('.sh-qrs svg[data-for="home"]');
    if(!svg)return Promise.resolve(null);
    var s=new XMLSerializer().serializeToString(svg);if(!/xmlns=/.test(s))s=s.replace('<svg','<svg xmlns="http://www.w3.org/2000/svg"');
    return new Promise(function(ok){var im=new Image();im.onload=function(){ok(im);};im.onerror=function(){ok(null);};im.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(s);});
  }
  var NOHEAD=/[，。、；：！？”’）》〉」』…·]/,NOTAIL=/[（“‘《〈「『]$/;
  function wrap(ctx,text,maxW){
    var lines=[],line='';
    for(var i=0;i<text.length;i++){
      var ch=text[i];if(ch==='\n'){lines.push(line);line='';continue;}
      var t=line+ch;
      if(line&&ctx.measureText(t).width>maxW){
        if(NOHEAD.test(ch)){lines.push(t);line='';}
        else{var carry='';while(NOTAIL.test(line)&&line.length>1){carry=line.slice(-1)+carry;line=line.slice(0,-1);}lines.push(line);line=carry+ch;}   // 开括号、前引号不留在行尾
      }
      else line=t;
    }
    if(line)lines.push(line);return lines;
  }
  function balance(ctx,text,ls,maxW){   // 标题：让各行长短均匀，避免最后一行只剩一两个字
    if(ls.length<2||/\n/.test(text))return ls;var w=ctx.measureText(text).width/ls.length;
    for(var k=0;k<12;k++){var t=wrap(ctx,text,Math.min(maxW,w+k*ctx.measureText('字').width*0.5));if(t.length===ls.length)return t;}return ls;
  }
  function fit(ctx,text,font,size,min,maxW,maxLines,bal){   // 字太多就缩小字号；再放不下就截断加省略号
    for(var s=size;s>=min;s-=2){ctx.font=font(s);var ls=wrap(ctx,text,maxW);if(ls.length<=maxLines)return {s:s,lines:bal?balance(ctx,text,ls,maxW):ls};}
    ctx.font=font(min);var all=wrap(ctx,text,maxW),cut=all.slice(0,maxLines);
    cut[maxLines-1]=cut[maxLines-1].replace(/[，。、；：！？]?$/,'').slice(0,-1)+'……';return {s:min,lines:cut};
  }
  function rrect(ctx,x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
  function frame(ctx,eyebrow){
    var g=ctx.createLinearGradient(0,0,0,HH);g.addColorStop(0,'#FCF7EB');g.addColorStop(1,'#F2E3C3');ctx.fillStyle=g;ctx.fillRect(0,0,W,HH);
    var gl=ctx.createRadialGradient(W/2,180,20,W/2,180,620);gl.addColorStop(0,'rgba(255,236,170,.55)');gl.addColorStop(1,'rgba(255,236,170,0)');ctx.fillStyle=gl;ctx.fillRect(0,0,W,HH);
    ctx.strokeStyle='#C9A55A';ctx.lineWidth=3;rrect(ctx,44,44,W-88,HH-88,30);ctx.stroke();
    ctx.strokeStyle='rgba(201,165,90,.45)';ctx.lineWidth=1.5;rrect(ctx,58,58,W-116,HH-116,24);ctx.stroke();
    ctx.fillStyle='#B98E35';ctx.textAlign='center';ctx.textBaseline='alphabetic';ctx.font='600 30px '+SANS;ctx.fillText('✦  '+eyebrow+'  ✦',W/2,150);
  }
  function footer(ctx,qr,line1,line2){
    var y=1120;ctx.strokeStyle='rgba(122,34,51,.25)';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(PAD,y);ctx.lineTo(W-PAD,y);ctx.stroke();
    var q=200,qx=PAD,qy=y+44;ctx.fillStyle='#fff';rrect(ctx,qx-10,qy-10,q+20,q+20,16);ctx.fill();
    if(qr)ctx.drawImage(qr,qx,qy,q,q);
    ctx.textAlign='left';ctx.fillStyle='#7A2233';ctx.font='700 38px '+SANS;ctx.fillText(line1,qx+q+50,qy+60);
    ctx.fillStyle='#5A4A36';ctx.font='400 28px '+SANS;ctx.fillText(line2,qx+q+50,qy+112);
    ctx.fillStyle='#9A8A70';ctx.font='400 24px '+SANS;ctx.fillText('整理制作 · Ethan（HangZhou_XG）',qx+q+50,qy+170);
  }
  function block(ctx,lines,size,lh,x,y,align,color,font){ctx.textAlign=align;ctx.fillStyle=color;ctx.font=font;lines.forEach(function(l,i){ctx.fillText(l,x,y+i*size*lh);});return y+lines.length*size*lh;}

  /* ---- 三种图片 ---- */
  function drawVerse(ctx,c){
    frame(ctx,'预言的恩赐 · 经文');
    ctx.fillStyle='rgba(185,142,53,.3)';ctx.font='900 200px '+SERIF;ctx.textAlign='left';ctx.fillText('“',PAD-36,350);
    var txt=clean(c.text).replace(/^“|”$/g,''),lh=1.7,f=null;
    for(var s=66;s>=34;s-=2){ctx.font='600 '+s+'px '+SERIF;var ls=wrap(ctx,txt,W-2*PAD);if(ls.length*s*lh<=620){f={s:s,lines:ls};break;}}   // 经文区：360–980，下面留给出处
    if(!f)f=fit(ctx,txt,function(s){return '600 '+s+'px '+SERIF;},34,34,W-2*PAD,Math.floor(620/(34*lh)));
    var h=f.lines.length*f.s*lh,top=360+f.s+Math.max(0,(620-h)/2);
    var end=block(ctx,f.lines,f.s,lh,PAD,top,'left','#2B2118','600 '+f.s+'px '+SERIF);
    ctx.textAlign='right';ctx.fillStyle='#7A2233';ctx.font='600 36px '+SANS;ctx.fillText('—— '+c.ref,W-PAD,Math.min(end-f.s*lh+f.s+70,1070));
  }
  function drawArticle(ctx,c){
    frame(ctx,'问题彩蛋 · 研经问答');
    var t=fit(ctx,c.title.split('\n').map(clean).filter(Boolean).join('\n'),function(s){return '900 '+s+'px '+SERIF;},84,56,W-2*PAD,3,true);
    var y=block(ctx,t.lines,t.s,1.35,W/2,300,'center','#2B2118','900 '+t.s+'px '+SERIF);
    if(c.sub){ctx.font='500 32px '+SANS;var sl=wrap(ctx,clean(c.sub),W-2*PAD).slice(0,2);y=block(ctx,sl,32,1.6,W/2,y+30,'center','#7A2233','500 32px '+SANS);}
    ctx.strokeStyle='#C9A55A';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(W/2-60,y+30);ctx.lineTo(W/2+60,y+30);ctx.stroke();
    var b=fit(ctx,clean(c.text),function(s){return '400 '+s+'px '+SERIF;},42,34,W-2*PAD,Math.max(4,Math.floor((1060-(y+90))/(42*1.75))));
    block(ctx,b.lines,b.s,1.75,PAD,y+100,'left','#3A2E22','400 '+b.s+'px '+SERIF);
  }
  function drawAnswer(ctx,c){
    frame(ctx,'提问区 · 管理员回答');
    ctx.textAlign='left';ctx.fillStyle='#7A2233';ctx.font='900 44px '+SERIF;ctx.fillText('问',PAD,290);
    var q=fit(ctx,clean(c.q),function(s){return '700 '+s+'px '+SERIF;},50,38,W-2*PAD-80,5);
    var y=block(ctx,q.lines,q.s,1.6,PAD+80,290,'left','#2B2118','700 '+q.s+'px '+SERIF);
    y=Math.max(y+40,420);ctx.fillStyle='#B98E35';ctx.font='900 44px '+SERIF;ctx.fillText('答',PAD,y+20);
    var a=fit(ctx,clean(c.a),function(s){return '400 '+s+'px '+SERIF;},42,32,W-2*PAD-80,Math.max(4,Math.floor((1070-y)/(42*1.7))));
    block(ctx,a.lines,a.s,1.7,PAD+80,y+20,'left','#3A2E22','400 '+a.s+'px '+SERIF);
  }
  function make(card){
    open();
    var fonts=document.fonts&&document.fonts.load?Promise.all([document.fonts.load('600 48px LessonSerif'),document.fonts.load('900 48px LessonSerif')]).catch(function(){}):Promise.resolve();
    Promise.all([fonts,qrImg(card.qr)]).then(function(r){
      cv.width=W;cv.height=HH;var ctx=cv.getContext('2d');
      ({verse:drawVerse,article:drawArticle,answer:drawAnswer})[card.kind](ctx,card);
      footer(ctx,r[1],'长按识别二维码',card.qrText||'阅读本季安息日学研读');
      var url=cv.toDataURL('image/jpeg',0.92),img=SH.querySelector('.im-img');
      img.src=url;img.hidden=false;SH.querySelector('.im-wait').hidden=true;
      var dl=SH.querySelector('.im-dl');dl.href=url;dl.hidden=mobile;
    }).catch(function(){SH.querySelector('.im-wait').textContent='图片没有生成成功，请再试一次。';});
  }
  window.Q4Card=make;

  /* ---- 入口 ---- */
  document.addEventListener('click',function(e){
    var b=e.target.closest('[data-imgverse]');
    if(b){
      e.preventDefault();e.stopPropagation();var w=b.dataset.imgverse,text='',ref='';
      if(w==='welcome'){text=(document.querySelector('#welcome .wvt')||{}).textContent;ref=((document.querySelector('#welcome .wvr')||{}).textContent||'').replace(/^——\s*/,'').replace(/\s*·\s*出自.*$/,'');}
      else if(w==='gift'){text=(document.querySelector('#gift .gift-vt')||{}).textContent;ref=((document.querySelector('#gift .gift-vr')||{}).textContent||'').replace(/^——\s*/,'');}
      else if(w==='bpop'){var ps=document.querySelectorAll('#bpop .bs[data-sec="cuv"] .bv');text=[].map.call(ps,function(p){var c=p.cloneNode(true),s=c.querySelector('sup');if(s)s.remove();return c.textContent;}).join('');ref=(document.getElementById('bpop-t')||{}).textContent;}
      if(text)make({kind:'verse',text:text,ref:ref||'',qr:'home'});
      return;
    }
    b=e.target.closest('[data-imgqa]');
    if(b){var L=b.closest('.lesson'),art=L&&L.querySelector('article.qna');if(!art)return;
      var h1=art.querySelector('.cover h1'),sub=art.querySelector('.cover .sub'),paras=[].slice.call(art.querySelectorAll('p')).filter(function(p){
        var t=p.textContent.trim();return !p.closest('.cover,.qshare,.btnrow,blockquote,.hl,figure,aside,table')&&t.length>40&&!/[\u0590-\u05FF\u0370-\u03FF]/.test(t)&&!/（和合本）$/.test(t);});
      make({kind:'article',title:h1?(h1.innerText||h1.textContent):'',sub:sub?sub.textContent:'',text:paras.slice(0,2).map(function(p){return p.textContent;}).join(''),qr:L.id,qrText:'阅读这篇问答的全文'});return;}
    b=e.target.closest('[data-qimg]');
    if(b){var a=b.closest('.aq'),qt=a&&a.querySelector('.aq-t'),ad=a&&a.querySelector('.aq-r.admin .aq-rt');if(!qt||!ad)return;
      make({kind:'answer',q:qt.textContent,a:ad.textContent,qr:'ask',qrText:'来提问区一起讨论'});}
  },true);
  document.querySelectorAll('article.qna').forEach(function(art){var r=art.parentNode.querySelector('.qshare');if(!r)return;
    var b=el('button','btn','🖼 生成图片');b.type='button';b.setAttribute('data-imgqa','');r.appendChild(b);});
})();

/* ---------- 账号（可选）：登录后，设置、笔记、行动勾选、读到哪里、提问身份在不同设备之间同步 ----------
   不登录一切照旧。账号名的哈希 = 账号编号；密码在本机算出两把钥匙（PBKDF2）：一把加密数据（AES-GCM），一把给每项数据编格子号（HMAC）。
   网上（GitHub 公开仓库）只存密文，谁也看不到内容；忘记密码无法找回。
   注册 = 把这台设备的身份钥匙（发问题、打卡用的那把）加密后存到账号里；在别的设备登录就取回同一个身份。 */
(function(){
  var H=window.Q4Hub;if(!H||!document.body.classList.contains('combined'))return;
  var SUB=window.crypto&&crypto.subtle,get=H.get,set=H.set;
  function del(k){try{localStorage.removeItem('q4:'+k);}catch(e){}}
  function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function enc(s){return new TextEncoder().encode(s);}
  function b64u(buf){var s='',a=new Uint8Array(buf);for(var i=0;i<a.length;i++)s+=String.fromCharCode(a[i]);return btoa(s).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');}
  function unb64u(s){s=s.replace(/-/g,'+').replace(/_/g,'/');while(s.length%4)s+='=';var b=atob(s),a=new Uint8Array(b.length);for(var i=0;i<b.length;i++)a[i]=b.charCodeAt(i);return a;}
  function hex(buf){return Array.prototype.map.call(new Uint8Array(buf),function(b){return ('0'+b.toString(16)).slice(-2);}).join('');}
  function fnv(s){var h=0x811c9dc5;for(var i=0;i<s.length;i++){h=Math.imul(h^s.charCodeAt(i),0x01000193)>>>0;}return h.toString(36)+'.'+s.length;}
  var VURL=H.online+'data/vault.json';
  var NOTE=/^l\d+-(sab|sun|mon|tue|wed|thu|fri)-[qe]\d+$/,CHUNK=600;
  var DID=get('did');if(!DID){DID=Math.random().toString(36).slice(2,10)+Date.now().toString(36).slice(-4);set('did',DID);}   // 这台设备的编号（研读时间按设备分开记，再加起来）
  var OTHERS={};   // 账号里其他设备本周的研读时间
  window.Q4Ext={weekSecs:function(wk){var n=0;Object.keys(OTHERS).forEach(function(k){var o=OTHERS[k];if(o&&o.w===wk)n+=+o.s||0;});return n;}};
  function lsKeys(prefix){var out=[];try{for(var i=0;i<localStorage.length;i++){var k=localStorage.key(i);if(k&&k.indexOf('q4:'+prefix)===0)out.push(k.slice(3+prefix.length));}}catch(e){}return out.sort();}
  function list(v){try{var a=JSON.parse(v||'[]');return Array.isArray(a)?a:[];}catch(e){return [];}}
  function union(a,b){var o={};a.concat(b).forEach(function(x){if(typeof x==='string')o[x]=1;});return Object.keys(o).sort();}

  /* ===== 钥匙 ===== */
  function uname(s){s=String(s||'');if(s.normalize)s=s.normalize('NFKC');return s.trim().toLowerCase();}
  function okName(u){return /^[一-鿿A-Za-z0-9_.\-]{2,20}$/.test(u);}
  function aidOf(u){return SUB.digest('SHA-256',enc('q4acct|'+u)).then(function(h){return hex(h).slice(0,32);});}
  function derive(u,pw){
    return SUB.importKey('raw',enc(pw),'PBKDF2',false,['deriveBits'])
      .then(function(k){return SUB.deriveBits({name:'PBKDF2',salt:enc('q4acct|'+u),iterations:120000,hash:'SHA-256'},k,512);});
  }
  var KE=null,KM=null;   // 加密钥匙、格子号钥匙
  function useRaw(raw){
    var a=new Uint8Array(raw);
    return Promise.all([SUB.importKey('raw',a.slice(0,32),{name:'AES-GCM'},false,['encrypt','decrypt']),
                        SUB.importKey('raw',a.slice(32,64),{name:'HMAC',hash:'SHA-256'},false,['sign'])])
      .then(function(ks){KE=ks[0];KM=ks[1];});
  }
  function seal(obj){var iv=crypto.getRandomValues(new Uint8Array(12));
    return SUB.encrypt({name:'AES-GCM',iv:iv},KE,enc(JSON.stringify(obj))).then(function(ct){var o=new Uint8Array(12+ct.byteLength);o.set(iv);o.set(new Uint8Array(ct),12);return b64u(o);});}
  function unseal(s){
    try{var a=unb64u(s);}catch(e){return Promise.resolve(null);}
    return SUB.decrypt({name:'AES-GCM',iv:a.slice(0,12)},KE,a.slice(12)).then(function(pt){return JSON.parse(new TextDecoder().decode(pt));},function(){return null;});
  }
  function slotOf(k,i){return SUB.sign('HMAC',KM,enc(k+'#'+i)).then(function(h){return hex(h).slice(0,16);});}

  /* ===== 本机状态 ===== */
  var ACC=null;try{ACC=JSON.parse(get('acct')||'null');}catch(e){}
  var VS={};try{VS=JSON.parse(get('vstate')||'{}')||{};}catch(e){}
  function saveVS(){set('vstate',JSON.stringify(VS));}
  var status={t:0,msg:'',err:''};

  /* ===== 本机数据 ⇄ 同步项 ===== */
  function noteKeys(){return [].slice.call(document.querySelectorAll('.my textarea[data-k]')).map(function(t){return t.dataset.k;}).filter(function(k){return NOTE.test(k);});}
  var ACTS={};[].slice.call(document.querySelectorAll('.acts input[data-k]')).forEach(function(c){var m=/^(l\d+)-/.exec(c.dataset.k);if(m)(ACTS[m[1]]=ACTS[m[1]]||[]).push(c.dataset.k);});
  function settingsVal(){
    var o={},keys={fs:'fs',th:'theme',rate:'rate',name:'askname'};
    Object.keys(keys).forEach(function(x){var v=get(keys[x]);if(v)o[x]=v;});
    if(get('asklocman')==='1'&&get('askloc'))o.loc=get('askloc');
    return Object.keys(o).length?JSON.stringify(o):'';
  }
  function snapshot(withResume){
    var m={set:settingsVal()};
    noteKeys().forEach(function(k){m['n:'+k]=get(k)||'';});
    Object.keys(ACTS).forEach(function(l){var on=ACTS[l].filter(function(k){return get(k)==='1';});m['a:'+l]=on.length?JSON.stringify(on):'';});
    if(withResume)m.r=get('resume')||'';
    var ck=lsKeys('ck:').filter(function(k){return get('ck:'+k)==='1';});m.c=ck.length?JSON.stringify(ck):'';   // 读完打卡
    var g=list(get('goals')).sort();m.g=g.length?JSON.stringify(g):'';   // 达到研读目标的周
    if(window.Q4Week){var s=Math.floor(Q4Week.secs()/300)*300;m['tm:'+DID]=s?JSON.stringify({w:Q4Week.key(),s:s}):'';}   // 本设备本周研读时间（按 5 分钟取整，免得传得太勤）
    return m;
  }
  function applyItem(k,v){
    if(k==='set'){
      var o={};try{o=JSON.parse(v||'{}')||{};}catch(e){}
      var keys={fs:'fs',th:'theme',rate:'rate',name:'askname'};
      Object.keys(keys).forEach(function(x){if(o[x])set(keys[x],String(o[x]));});
      if(o.loc){set('askloc',o.loc);set('asklocsrc','man');set('asklocman','1');set('asklocat',String(Date.now()));}
      if(window.Q4Reader){Q4Reader.fs(get('fs'));Q4Reader.th(get('theme')||'auto');}
      var an=document.querySelector('#ask .ask-name');if(an&&o.name&&!an.value)an.value=o.name;
    }else if(k.indexOf('n:')===0){
      var nk=k.slice(2);if(v)set(nk,v);else del(nk);
      var ta=document.querySelector('.my textarea[data-k="'+nk+'"]');
      if(ta&&document.activeElement!==ta){ta.value=v||'';if(v){var d=ta.closest('details');if(d)d.open=true;}var sv=ta.parentNode.querySelector('.saved');if(sv)sv.textContent=v?'已从账号同步':'';}
    }else if(k.indexOf('a:')===0){
      var on=[];try{on=JSON.parse(v||'[]')||[];}catch(e){}
      (ACTS[k.slice(2)]||[]).forEach(function(ck){var y=on.indexOf(ck)>=0;set(ck,y?'1':'0');var c=document.querySelector('.acts input[data-k="'+ck+'"]');if(c)c.checked=y;});
    }else if(k==='r'){
      if(v)set('resume',v);if(window.Q4Reader)Q4Reader.resume();
    }else if(k==='c'){   // 打卡：两边合起来
      list(v).forEach(function(x){if(/^l\d+-(sab|sun|mon|tue|wed|thu|fri|sum)$/.test(x))set('ck:'+x,'1');});
      if(window.Q4Comm)Q4Comm.paint();
    }else if(k==='g'){
      set('goals',JSON.stringify(union(list(get('goals')),list(v))));
      if(window.Q4Week)Q4Week.paint();
    }
  }

  /* ===== 网上的数据（存档 vault.json + 中转站里的新消息） ===== */
  var VJ=null,vjFor=-1,DEC={};   // DEC：格子 → 解开后的内容（按格子+时间缓存）
  function loadVJ(){
    var up=(H.S&&H.S.updated)||0;if(VJ&&vjFor===up)return Promise.resolve(VJ);
    return fetch(VURL+'?t='+Math.floor(Date.now()/30000),{cache:'no-store'}).then(function(r){return r.ok?r.json():{};},function(){return {};})
      .then(function(j){VJ=((j&&j.vault)||{})[ACC.aid]||{};vjFor=up;return VJ;});
  }
  function remoteSlots(){
    var o={},live=(H.S&&H.S.vault&&H.S.vault[ACC.aid])||{},base=VJ||{};
    Object.keys(base).forEach(function(s){o[s]=base[s];});
    Object.keys(live).forEach(function(s){if(!o[s]||live[s].ts>=o[s].ts)o[s]=live[s];});
    return o;
  }
  function remoteItems(){
    var sl=remoteSlots();
    return Promise.all(Object.keys(sl).map(function(s){
      var x=sl[s],c=DEC[s];if(c&&c.ts===x.ts)return c.v;
      return unseal(x.d).then(function(v){DEC[s]={ts:x.ts,v:v};return v;});
    })).then(function(list){
      var g={};
      list.forEach(function(p){if(!p||typeof p.k!=='string')return;var it=g[p.k];if(!it||p.t>it.t)g[p.k]=it={t:p.t,n:p.n,parts:{}};if(p.t===it.t)it.parts[p.i]=p.v;});
      var out={};
      Object.keys(g).forEach(function(k){var it=g[k],v='';for(var i=0;i<it.n;i++){if(typeof it.parts[i]!=='string')return;v+=it.parts[i];}out[k]={v:v,t:it.t,n:it.n};});
      return out;
    });
  }

  /* ===== 同步 ===== */
  var running=null,queue=[],lastR=0;
  function pull(R,first){
    var cur=snapshot(true),changed=0;
    Object.keys(R).forEach(function(k){
      var r=R[k],st=VS[k],lv=cur[k]!=null?cur[k]:'';
      if(k.indexOf('tm:')===0){   // 别的设备的研读时间：只记下来加到总数里，不改本机
        if(k!=='tm:'+DID){try{OTHERS[k]=JSON.parse(r.v||'null');}catch(e){}}
        if(!st||r.t>st.t)VS[k]={h:fnv(r.v),t:r.t,n:r.n};return;
      }
      if(k==='c'||k==='g'){if(!st||r.t>st.t){applyItem(k,r.v);VS[k]={h:fnv(r.v),t:r.t,n:r.n};}return;}   // 打卡、达标周：两边合并（合并后的结果稍后再传上去）
      if(st&&r.t<=st.t)return;   // 已经是最新
      var localEdited=st?fnv(lv)!==st.h:(!first&&lv!=='');
      if(localEdited&&st&&st.lt&&st.lt>r.t)return;   // 两边都改了：本机的更新，稍后上传
      if(lv!==r.v){applyItem(k,r.v);changed++;}
      VS[k]={h:fnv(r.v),t:r.t,n:r.n};
    });
    saveVS();if(window.Q4Week)Q4Week.paint();return changed;
  }
  function pushChanged(withResume){
    var cur=snapshot(withResume),now=Date.now(),jobs=[];
    Object.keys(cur).forEach(function(k){
      var v=cur[k],h=fnv(v),st=VS[k];
      if(!st&&!v)return;if(st&&st.h===h)return;
      if(k==='r'&&!withResume)return;
      jobs.push({k:k,v:v,t:now,old:(st&&st.n)||0});
      VS[k]={h:h,t:now,n:Math.max(1,Math.ceil(v.length/CHUNK)),lt:now,pending:1};
    });
    saveVS();
    jobs.forEach(function(j){queue.push(j);});
    return drain();
  }
  var draining=null;
  function drain(){
    if(draining)return draining;
    draining=(function step(){
      var j=queue.shift();if(!j){draining=null;return Promise.resolve();}
      var n=Math.max(1,Math.ceil(j.v.length/CHUNK)),parts=[];
      for(var i=0;i<n;i++)parts.push(j.v.slice(i*CHUNK,(i+1)*CHUNK));
      var seq=Promise.resolve();
      parts.forEach(function(pv,i){seq=seq.then(function(){return Promise.all([slotOf(j.k,i),seal({k:j.k,v:pv,i:i,n:n,t:j.t})]);})
        .then(function(a){return send({op:'w',id:H.rid('w'),aid:ACC.aid,slot:a[0],d:a[1]});});});
      for(var x=n;x<j.old;x++)(function(x){seq=seq.then(function(){return slotOf(j.k,x);}).then(function(s){return send({op:'w',id:H.rid('w'),aid:ACC.aid,slot:s,d:''});});})(x);
      return seq.then(function(){if(VS[j.k]&&VS[j.k].t===j.t){delete VS[j.k].pending;saveVS();}status.t=Date.now();status.err='';paint();return step();},
        function(e){queue.unshift(j);draining=null;status.err=H.why(e);paint();throw e;});
    })();
    return draining;
  }
  function send(P){   // 每条之间稍隔一会儿，免得中转站嫌太快
    var go=function(n){return H.post(P).catch(function(e){if(e&&e.code==='HTTP_429'&&n<3)return new Promise(function(ok){setTimeout(ok,8000*(n+1));}).then(function(){return go(n+1);});throw e;});};
    return new Promise(function(ok){setTimeout(ok,700);}).then(function(){return go(0);});
  }
  function sync(opts){
    opts=opts||{};if(!ACC||!KE)return Promise.resolve();
    if(running)return running;
    status.msg='正在同步……';paint();
    running=(opts.fresh||H.cached?H.load(true):(H.S?Promise.resolve(H.S):H.load()))   /* 手机里存的旧数据不拿来同步账号 */
      .then(loadVJ).then(remoteItems).then(function(R){
        var ch=pull(R,opts.first);
        if(opts.first&&ACC){delete ACC.first;set('acct',JSON.stringify(ACC));}
        return pushChanged(opts.resume||Date.now()-lastR>120000).then(function(){if(opts.resume||Date.now()-lastR>120000)lastR=Date.now();return ch;});
      })
      .then(function(ch){status.msg='';status.t=Date.now();status.err='';running=null;paint();return ch;},
            function(e){status.msg='';status.err=H.why(e);running=null;paint();});
    return running;
  }

  /* ===== 登录 / 注册 / 退出 ===== */
  function register(u,pw){
    var aid;
    return aidOf(u).then(function(a){aid=a;return H.load(true);}).then(function(S){
      if(S.accounts&&S.accounts[aid])throw {msg:'这个账号已经有人用了，换一个吧。如果是你自己的账号，请点上面的“登录”。'};
      return Promise.all([H.ensure(),derive(u,pw)]);
    }).then(function(a){
      var raw=a[1],sk=null;try{sk=JSON.parse(get('sk'));}catch(e){}
      if(!sk)throw {msg:'没能准备好这台设备的身份，请刷新后再试。'};
      return useRaw(raw).then(function(){return seal({sk:sk,u:u});}).then(function(ek){
        return H.post({op:'u',id:H.rid('u'),aid:aid,ek:ek});
      }).then(function(){return login2(u,aid,raw,true);});
    });
  }
  function login(u,pw){
    var aid,raw;
    return aidOf(u).then(function(a){aid=a;return Promise.all([H.load(true),derive(u,pw)]);}).then(function(r){
      var S=r[0];raw=r[1];var ac=S.accounts&&S.accounts[aid];
      if(!ac)throw {msg:'没有这个账号。新用户请点上面的“注册”。'};
      return useRaw(raw).then(function(){return unseal(ac.ek);}).then(function(box){
        if(!box||!box.sk||!box.sk.d)throw {msg:'密码不对，请再试一次。'};
        var cur=get('sk');
        if(cur&&cur!==JSON.stringify(box.sk)&&!get('sk_prev'))set('sk_prev',cur);   // 这台设备原来的身份留着，退出时换回来
        set('sk',JSON.stringify(box.sk));
        return H.reset();
      }).then(function(){return login2(u,aid,raw,false);});
    });
  }
  function login2(u,aid,raw,fresh){
    ACC={u:u,aid:aid,r:b64u(raw),first:fresh?0:1};set('acct',JSON.stringify(ACC));
    VS={};saveVS();VJ=null;DEC={};
    return sync({fresh:false,first:!fresh,resume:true});
  }
  function logout(){
    ACC=null;KE=KM=null;del('acct');del('vstate');VS={};VJ=null;DEC={};queue=[];
    var prev=get('sk_prev');if(prev){set('sk',prev);del('sk_prev');}else del('sk');
    return H.reset();
  }

  /* ===== 界面：欢迎页左上角“账号” ===== */
  var SH=el('div','hconf rsheet acctsheet');SH.setAttribute('role','dialog');SH.setAttribute('aria-modal','true');SH.setAttribute('aria-label','账号');SH.hidden=true;
  SH.innerHTML='<div class="hconf-bg" data-close></div><div class="hconf-card"><button type="button" class="rs-x" data-close aria-label="关闭">×</button><div class="rs-body"></div></div>';
  document.body.appendChild(SH);
  var BODY=SH.querySelector('.rs-body'),tab='in';
  function openSheet(){paint(true);SH.hidden=false;void SH.offsetWidth;SH.classList.add('open');document.documentElement.classList.add('sheetopen');
  }
  function closeSheet(){SH.classList.remove('open');document.documentElement.classList.remove('sheetopen');setTimeout(function(){SH.hidden=true;},220);}
  function when(t){if(!t)return '';var s=Math.round((Date.now()-t)/1000);return s<60?'刚刚':s<3600?Math.floor(s/60)+' 分钟前':new Date(t).toLocaleString('zh-CN',{month:'numeric',day:'numeric',hour:'2-digit',minute:'2-digit'});}
  function paint(force){
    document.querySelectorAll('[data-acct]').forEach(function(b){var n=b.querySelector('.ac-n');if(n)n.textContent=ACC?ACC.u:'账号';b.classList.toggle('in',!!ACC);});
    if(!force&&(SH.hidden||!ACC))return;   // 面板关着不用画；没登录时不打断正在填的表单
    if(ACC){
      var st=status.err?'<span class="ac-bad">同步没有成功：'+esc(status.err)+'</span>':status.msg?esc(status.msg):status.t?'✓ 已同步 · '+when(status.t):'';
      BODY.innerHTML='<h3>账号</h3><p class="ac-me">已登录：<b>'+esc(ACC.u)+'</b></p><p class="ac-st" role="status">'+st+'</p>'+
        '<p class="ac-k">在别的手机、电脑或微信里登录这个账号，下面这些都会同步过去：</p>'+
        '<ul class="ac-list"><li>字号、夜间模式、朗读速度、称呼</li><li>你发过的问题和回复（同一个身份）</li><li>读完打卡、本周研读时间（各设备加起来）</li><li>“写下我的回答”里写的内容</li><li>“我们的行动”的勾选</li><li>读到哪里（继续上次阅读）</li></ul>'+
        '<div class="hconf-btns"><button type="button" data-acsync>立即同步</button><button type="button" data-acout>退出登录</button></div>';
      return;
    }
    if(!H.ok||!SUB){BODY.innerHTML='<h3>账号</h3><p class="ac-lead">'+esc(H.why({code:location.protocol==='file:'?'FILE':'OLD'}))+'</p>';return;}
    var up=tab==='up';
    BODY.innerHTML='<h3>账号</h3><p class="ac-lead">不登录也能正常使用。登录后，换手机、用电脑或在微信里打开，你的设置、发过的问题和写下的回答都会同步过来。</p>'+
      '<div class="rs-seg ac-tabs" role="tablist"><button type="button" role="tab" data-actab="in" class="'+(up?'':'on')+'">登录</button><button type="button" role="tab" data-actab="up" class="'+(up?'on':'')+'">注册新账号</button></div>'+
      '<form class="ac-f" autocomplete="on">'+
      '<label><span>账号</span><input class="ac-u" name="username" autocomplete="username" maxlength="20" placeholder="例如：杭州小羊" autocapitalize="off" spellcheck="false"></label>'+
      '<label><span>密码</span><input class="ac-p" name="password" type="password" autocomplete="'+(up?'new':'current')+'-password" maxlength="64" placeholder="'+(up?'至少 6 位，不要太简单':'输入密码')+'"></label>'+
      (up?'<label><span>确认密码</span><input class="ac-p2" type="password" autocomplete="new-password" maxlength="64" placeholder="再输入一次密码"></label>':'')+
      '<label class="ac-show"><input type="checkbox" class="ac-sh"> 显示密码</label>'+
      '<p class="ac-msg" role="status"></p>'+
      '<button type="submit" class="btn solid ac-go">'+(up?'注册并登录':'登录')+'</button>'+
      (up?'<p class="ac-tip">请记住密码。你的笔记先用密码加密，再保存到网上，谁也看不到；也因此<b>忘记密码就无法找回</b>。</p>':'<p class="ac-tip">还没有账号？点上面的“注册新账号”。</p>')+
      '</form>';
  }
  var WEAK=/^(123456|1234567|12345678|123456789|111111|000000|666666|888888|abc123|password|qwerty|654321|123123)$/i;
  SH.addEventListener('click',function(e){
    var t=e.target;
    if(t.closest('[data-close]')){closeSheet();return;}
    var tb=t.closest('[data-actab]');if(tb){var u=SH.querySelector('.ac-u');var keep=u&&u.value;tab=tb.dataset.actab;paint(true);if(keep)SH.querySelector('.ac-u').value=keep;return;}
    if(t.closest('.ac-sh')){SH.querySelectorAll('.ac-p,.ac-p2').forEach(function(i){i.type=t.checked?'text':'password';});return;}
    if(t.closest('[data-acsync]')){sync({fresh:true,resume:true});return;}
    if(t.closest('[data-acout]')){
      if(!window.confirm('退出登录后，这台设备不再同步。已经在这台设备上的笔记会保留。确定退出吗？'))return;
      logout().then(function(){tab='in';paint(true);});return;
    }
  });
  SH.addEventListener('keydown',function(e){if(e.key==='Escape')closeSheet();});
  SH.addEventListener('submit',function(e){
    e.preventDefault();
    var msg=SH.querySelector('.ac-msg'),go=SH.querySelector('.ac-go');
    var u=uname(SH.querySelector('.ac-u').value),pw=SH.querySelector('.ac-p').value,p2=SH.querySelector('.ac-p2');
    function say(s,bad){msg.textContent=s;msg.classList.toggle('ac-bad',!!bad);}
    if(!okName(u))return say('账号要 2–20 个字，只能用中文、字母、数字（以及 _ . -）。',true);
    if(tab==='up'){
      if(pw.length<6)return say('密码至少 6 位。',true);
      if(WEAK.test(pw))return say('这个密码太常见了，容易被猜到，换一个吧。',true);
      if(p2&&p2.value!==pw)return say('两次输入的密码不一样。',true);
    }else if(!pw)return say('请输入密码。',true);
    go.disabled=true;say(tab==='up'?'正在注册……':'正在登录……');
    (tab==='up'?register(u,pw):login(u,pw)).then(function(){
      go.disabled=false;paint(true);
      var st=SH.querySelector('.ac-st');if(st)st.textContent=tab==='up'?'✓ 注册成功，已登录。以后在别的设备登录这个账号即可同步。':'✓ 登录成功，已同步。';
    },function(err){go.disabled=false;say(err&&err.msg?err.msg:H.why(err),true);});
  });
  document.addEventListener('click',function(e){if(e.target.closest('[data-acct]')){e.preventDefault();openSheet();}});

  /* ===== 自动同步 ===== */
  function changedSinceSync(){if(!ACC||!KE)return false;var cur=snapshot(false);return Object.keys(cur).some(function(k){var st=VS[k];return st?st.h!==fnv(cur[k]):!!cur[k];});}
  setInterval(function(){if(!document.hidden&&(queue.length||changedSinceSync()))sync();},8000);   // 写完笔记、改了设置，几秒后自动上传；上次没传成功的也会再传
  document.addEventListener('visibilitychange',function(){if(!ACC||!KE)return;if(document.hidden)sync({resume:true});else sync({fresh:true});});
  H.on(function(){if(ACC&&KE&&!running&&!draining)loadVJ().then(remoteItems).then(function(R){pull(R,false);}).catch(function(){});});   // 别处刷新了数据，顺便看看账号里有没有新内容
  function boot(){
    paint(true);
    if(!ACC)return;
    if(!SUB){return;}
    useRaw(unb64u(ACC.r)).then(function(){return sync({fresh:true,first:!!ACC.first,resume:false});});
  }
  if(document.readyState==='complete')setTimeout(boot,1500);else addEventListener('load',function(){setTimeout(boot,1500);});
  paint();
})();

/* ---------- 音乐：一首接一首播放；离开音乐页去读学课或问答时，缩成左下角的小窗继续播放 ----------
   曲目清单在 music/list.json：网页先用生成时放进来的一份，打开后再读最新的（收了新歌不用重新生成网页）。
   歌分放在文件夹里：#music 是文件夹列表，#music-f-<文件夹> 是一个文件夹里的歌，#music-<歌> 打开那首歌所在的文件夹并滚到它。 */
(function(){
  var page=document.getElementById('music');if(!page||!document.body.classList.contains('combined'))return;
  var box=page.querySelector('.mhome'),LIST=box.dataset.list,BASE=box.dataset.base,wrap=page.querySelector('.msongs');
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);}catch(e){}}
  function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function mmss(t){t=Math.max(0,Math.floor(t||0));return Math.floor(t/60)+':'+('0'+t%60).slice(-2);}
  var SHARE='<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5.5" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="6" cy="12" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="18" cy="18.5" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M8.3 10.8 15.7 6.7M8.3 13.2l7.4 4.1" fill="none" stroke="currentColor" stroke-width="2"/></svg>';
  var DL='<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 19.5h14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
  var inWx=/MicroMessenger/i.test(navigator.userAgent),de=document.documentElement;
  var SONGS=[],FOLDERS=[],folder='';   // folder：现在打开的文件夹（'' 表示文件夹列表）
  function take(j){if(Array.isArray(j)){SONGS=j;FOLDERS=[];}else if(j){SONGS=j.songs||[];FOLDERS=(j.folders||[]).filter(function(f){return f&&f.id&&f.name;});}}
  try{take(JSON.parse(page.querySelector('.mdata').textContent));}catch(e){}
  var byId={},FMAP={};function index(){byId={};FMAP={};SONGS.forEach(function(x){byId[x.id]=x;});FOLDERS.forEach(function(f){FMAP[f.id]=f;});}index();
  function folderOf(x){return x&&x.folder&&FMAP[x.folder]?x.folder:'other';}   // 没写文件夹的歌放进“其他诗歌”
  function flist(){var l=FOLDERS.slice();if(SONGS.some(function(x){return folderOf(x)==='other';}))l.push({id:'other',name:'其他诗歌',sub:''});return l;}
  function inFolder(fid){return SONGS.filter(function(x){return folderOf(x)===fid;});}
  function ordered(){if(!FOLDERS.length)return SONGS;var o=[];flist().forEach(function(f){o=o.concat(inFolder(f.id));});return o;}
  var A=new Audio();A.preload='auto';
  var cur='',queue=[],loop=get('mloop')==='1',shuf=get('mshuf')==='1',q='';
  var want=false,buf=null,bufPct=-1,waitT=null,pre={},rate=[],rateT=null,tapAt=0,MAXWAIT=7000;   // 缓冲最多等 7 秒就先播起来   // want：想让它播着；buf：网速跟不上时先停下来缓冲；pre：提前下载好的下一首
  var mini=el('div','mplayer');mini.hidden=true;mini.setAttribute('role','region');mini.setAttribute('aria-label','正在播放的音乐');
  mini.innerHTML='<a class="mp-go" href="#music" aria-label="回到音乐"><span class="mp-ic" aria-hidden="true">♪</span><span class="mp-tt"><span class="mp-t"></span><span class="mp-s"></span></span></a>'+
    '<button type="button" class="mp-prev" aria-label="上一首"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path fill="currentColor" d="M5 5h2.4v14H5zM20 5v14L8.6 12z"/></svg></button>'+
    '<button type="button" class="mp-pp" aria-label="暂停">❚❚</button>'+
    '<button type="button" class="mp-next" aria-label="下一首"><svg viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path fill="currentColor" d="M16.6 5H19v14h-2.4zM4 5v14l11.4-7z"/></svg></button>'+
    '<button type="button" class="mp-x" aria-label="停止播放">✕</button><i class="mp-pg" aria-hidden="true"><b></b></i>';
  document.body.appendChild(mini);
  var toastEl=el('p','mtoast');toastEl.hidden=true;toastEl.setAttribute('role','status');document.body.appendChild(toastEl);var toastT=null;
  function toast(s){toastEl.textContent=s;toastEl.hidden=false;clearTimeout(toastT);toastT=setTimeout(function(){toastEl.hidden=true;},6000);}
  function onMusic(){return /^#music(-|$)/.test(location.hash);}
  function shown(){   // 现在列出来的歌（搜索结果 / 这个文件夹的 / 文件夹列表时是全部）；“全部播放”就按这个顺序
    var k=q.trim().toLowerCase();
    if(k)return ordered().filter(function(x){return (x.title+' '+(x.sub||'')).toLowerCase().indexOf(k)>=0;});
    return folder&&FOLDERS.length?inFolder(folder):ordered();
  }
  function mins(list){var t=0;list.forEach(function(x){t+=x.dur||0;});t=Math.round(t/60);return t>=60?'约 '+Math.floor(t/60)+' 小时'+(t%60?' '+t%60+' 分钟':''):'约 '+Math.max(1,t)+' 分钟';}
  function isNew(f){   // 只给最新的那个文件夹标“新”（30 天内建的）
    var d=Date.parse(f.date||''),top=0;FOLDERS.forEach(function(x){top=Math.max(top,Date.parse(x.date||'')||0);});
    return d&&d===top&&Date.now()-d<30*864e5;
  }
  function fcard(f){var l=inFolder(f.id);return '<a class="mfold" href="#music-f-'+esc(f.id)+'" data-f="'+esc(f.id)+'">'+
    '<span class="mf-ic" aria-hidden="true"><svg viewBox="0 0 24 24" width="22" height="22"><path fill="currentColor" d="M3 6.5A2.5 2.5 0 0 1 5.5 4h4l2 2.2h7A2.5 2.5 0 0 1 21 8.7v8.8a2.5 2.5 0 0 1-2.5 2.5h-13A2.5 2.5 0 0 1 3 17.5z"/></svg></span>'+
    '<span class="mf-main"><b class="mf-n">'+esc(f.name)+(isNew(f)?'<i class="mf-new">新</i>':'')+'</b>'+(f.sub?'<span class="mf-s">'+esc(f.sub)+'</span>':'')+
    '<span class="mf-c">'+l.length+' 首 · '+mins(l)+'<span class="mf-on"> · 正在播放</span></span></span><span class="mf-go" aria-hidden="true">›</span></a>';}
  function card(x,withF){var fn=withF&&FOLDERS.length?(FMAP[x.folder]||{name:'其他诗歌'}).name:'';
    return '<article class="msong" id="music-'+esc(x.id)+'" data-id="'+esc(x.id)+'" data-title="'+esc(x.title+(x.sub?'（'+x.sub+'）':''))+' · 音乐">'+
    '<button class="ms-play" type="button" data-mplay aria-label="播放《'+esc(x.title)+'》"><span class="ms-ic" aria-hidden="true"></span></button>'+
    '<div class="ms-main"><h3 class="ms-t">'+esc(x.title)+'</h3>'+(x.sub||fn?'<p class="ms-s">'+esc(x.sub||'')+(fn?'<span class="ms-f">'+(x.sub?' · ':'')+esc(fn)+'</span>':'')+'</p>':'')+'</div>'+
    '<span class="ms-tm">'+(x.dur?mmss(x.dur):'')+'</span>'+
    '<span class="ms-acts"><a class="ms-ib ms-dl" href="'+esc(BASE+encodeURIComponent(fileOf(x)))+'" download="'+esc(x.title+(/\.\w+$/.exec(fileOf(x))||['.mp3'])[0])+'" aria-label="下载《'+esc(x.title)+'》">'+DL+'</a>'+
    '<button class="ms-ib share" type="button" data-share="music-'+esc(x.id)+'" aria-label="分享《'+esc(x.title)+'》">'+SHARE+'</button></span>'+
    '<div class="ms-bar"><i class="ms-pg" aria-hidden="true"><b></b></i></div></article>';}
  function render(){
    if(folder&&!FMAP[folder]&&folder!=='other')folder='';   // 文件夹已经没有了
    var list=shown(),k=q.trim(),n=page.querySelector('.ms-n'),h;
    if(!SONGS.length)h='<p class="mnone">音乐正在整理中，敬请期待。</p>';
    else if(k){h=list.length?list.map(function(x){return card(x,true);}).join(''):'<p class="mnone">没有找到这首歌，换个字试试。</p>';n.textContent='找到 '+list.length+' 首';}
    else if(!FOLDERS.length){h=list.map(function(x){return card(x);}).join('');n.textContent='共 '+SONGS.length+' 首';}
    else if(folder){
      var f=FMAP[folder]||{name:'其他诗歌',sub:''};
      h='<div class="mf-head"><a class="mf-back" href="#music">‹ 全部文件夹</a><h2 class="mf-title">'+esc(f.name)+'</h2>'+(f.sub?'<p class="mf-sub">'+esc(f.sub)+'</p>':'')+'</div>'+
        list.map(function(x){return card(x);}).join('');
      n.textContent='共 '+list.length+' 首';
    }
    else{h=flist().map(fcard).join('');n.textContent=flist().length+' 个文件夹 · 共 '+SONGS.length+' 首';}
    if(SONGS.length&&!SONGS.some(playable))h='<p class="mwarn">'+NOPLAY+'</p>'+h;
    wrap.innerHTML=h;wrap.classList.toggle('folders',!k&&!folder&&!!FOLDERS.length);
    paint();prog();marks();
  }
  function cardOf(id){return document.getElementById('music-'+id);}
  function makeQueue(startId){
    var ids=shown().map(function(x){return x.id;});if(!ids.length)ids=SONGS.map(function(x){return x.id;});
    if(shuf){for(var i=ids.length-1;i>0;i--){var j=Math.floor(Math.random()*(i+1)),t=ids[i];ids[i]=ids[j];ids[j]=t;}
      if(startId){ids.splice(ids.indexOf(startId),1);ids.unshift(startId);}}
    queue=ids;
  }
  var BASEA=(function(){var l=document.createElement('a');l.href=BASE;return l.href;})();   // 写成完整网址，和存在手机里的一致
  // OGG（Opus / Vorbis）较旧的苹果手机放不出来：放不了时改用备用的 AAC（list.json 里的 alt）
  var PROBE=document.createElement('audio');
  function total(){var d=A.duration;return isFinite(d)&&d>0?d:((cur&&byId[cur]||{}).dur||0);}   // 有的手机读不出 OGG 的总长（Infinity），用清单里记的
  function canType(t){return !t||!!(PROBE.canPlayType&&PROBE.canPlayType(t));}
  function fileOf(x){return x.alt&&!canType(x.type)?x.alt:x.file;}
  function playable(x){return canType(x.type)||!!x.alt;}
  var NOPLAY='这台手机暂时放不了这里的音乐（音乐是 OGG 格式，较旧的苹果手机放不了）。请把手机系统更新到最新，或换用安卓手机、电脑打开。';
  function urlOf(x){return BASEA+encodeURIComponent(fileOf(x));}
  /* 听过的歌存在这台设备上（浏览器的 Cache Storage），下次直接从手机里播，不用再等网络。
     最多存 40 首，再多就先删已经不在清单里的、再删最久没听的 */
  var BOX='q4-music',MAXSAVE=40,saved={},tried={},saving='',unlocked=false;
  var boxOk=!!(window.caches&&window.fetch&&window.Response&&window.URL&&URL.createObjectURL);
  function lru(){try{return JSON.parse(get('mlru')||'{}')||{};}catch(e){return {};}}
  function touch(u){var m=lru();m[u]=Date.now();set('mlru',JSON.stringify(m));}
  function store(){return caches.open(BOX);}
  function keep(u,b){   // 存进手机
    if(!boxOk||saved[u]||!b||b.size<1000)return;
    store().then(function(c){return c.put(u,new Response(b,{headers:{'Content-Type':b.type||'audio/mp4'}}));})
      .then(function(){saved[u]=1;touch(u);trim();marks();},function(){});
  }
  function trim(){
    var ks=Object.keys(saved),live={};if(ks.length<=MAXSAVE)return;var m=lru();
    SONGS.forEach(function(x){live[urlOf(x)]=1;});
    ks.sort(function(a,b){return (live[a]?1:0)-(live[b]?1:0)||(m[a]||0)-(m[b]||0);});
    ks.slice(0,ks.length-MAXSAVE).forEach(function(u){delete saved[u];delete m[u];store().then(function(c){return c.delete(u);}).catch(function(){});});
    set('mlru',JSON.stringify(m));
  }
  function fromBox(id,u){   // 从手机里取出来，换成本机地址
    return store().then(function(c){return c.match(u);}).then(function(r){return r?r.blob():null;}).then(function(b){
      if(!b){delete saved[u];marks();return '';}
      var o=pre[id]||(pre[id]={});if(!o.url)o.url=URL.createObjectURL(b);return o.url;
    });
  }
  function marks(){[].forEach.call(wrap.querySelectorAll('.msong'),function(it){var x=byId[it.dataset.id];it.classList.toggle('saved',!!(x&&saved[urlOf(x)]));});}
  if(boxOk)try{store().then(function(c){return c.keys();}).then(function(ks){ks.forEach(function(r){saved[r.url]=1;});marks();}).catch(function(){boxOk=false;});}catch(e){boxOk=false;}
  function tidy(){   // 读到最新清单后：清单里已经没有的（比如换了格式的旧文件）从手机里删掉
    if(!boxOk)return;var live={};SONGS.forEach(function(x){live[urlOf(x)]=1;});
    Object.keys(saved).forEach(function(u){if(!live[u]){delete saved[u];store().then(function(c){return c.delete(u);}).catch(function(){});}});
  }
  function play(id){
    var x=byId[id];if(!x)return;
    if(!playable(x)){toast(NOPLAY);return;}
    if(id!==cur){
      cur=id;stopBuf();rate=[];tapAt=Date.now();
      Object.keys(pre).forEach(function(k){var o=pre[k];if(!o.url){if(o.ctl)o.ctl.abort();delete pre[k];}});   // 后台还没下载完的先停掉，网速全给选中的这首
      var u=urlOf(x);if(saved[u])touch(u);
      if(pre[id]&&pre[id].url)A.src=pre[id].url;   // 提前下载好的：直接从手机里播
      else if(saved[u]){   // 以前听过、存在手机里的
        if(unlocked)A.removeAttribute('src');else A.src=u;   // 这次打开网页还没播过：手机要求点下去马上开始播，先用网址，取出来后马上换过去
        fromBox(id,u).then(function(bu){
          if(cur!==id)return;
          if(!bu){if(!A.getAttribute('src')){A.src=u;if(want)go();}return;}
          if(A.getAttribute('src')===bu||(A.currentTime>0.3&&!A.paused))return;
          stopBuf();rate=[];A.src=bu;if(want)go();
        }).catch(function(){if(cur===id&&!A.getAttribute('src')){A.src=u;if(want)go();}});
      }
      else A.src=u;
    }
    if(queue.indexOf(id)<0)makeQueue(id);
    want=true;if(!rateT)rateT=setInterval(sample,500);
    try{window.dispatchEvent(new Event('q4:music'));}catch(e){}
    if(!buf&&A.getAttribute('src'))go();
    media();paint();
  }
  function go(){var p=A.play();if(p&&p.catch)p.catch(function(e){if(e&&e.name==='NotAllowedError'){want=false;stopBuf();}paint();});}
  function hold(){want=false;stopBuf();A.pause();paint();}   // 使用者按了暂停
  /* 网速跟不上时：与其一卡一卡，不如先停下来多缓冲一些。
     按最近几秒的下载速度估算：已缓冲的部分够撑到整首下载完，就接着播，之后不会再卡；
     但最多只等 7 秒（刚点播放时从点的那一刻算起），到时间就先播起来 */
  function ahead(){var b=A.buffered,t=A.currentTime;for(var i=0;i<b.length;i++)if(b.start(i)<=t+0.5&&b.end(i)>t)return b.end(i)-t;return 0;}
  function sample(){   // 一直记着最近 8 秒下载到了第几秒，用来估网速
    if(!cur)return;var e=A.currentTime+ahead(),now=Date.now(),l=rate[rate.length-1];
    if(l&&e<l[1]-0.5)rate=[];rate.push([now,e]);while(rate.length>2&&now-rate[0][0]>8000)rate.shift();
  }
  function slope(a,z){var dt=(z[0]-a[0])/1000;return dt>0?(z[1]-a[1])/dt:0;}
  function speed(){   // 每秒能下载几秒的歌；取整段和后半段里慢的那个，免得被开头一下子来的一批数据骗了
    var n=rate.length;if(n<2||rate[n-1][0]-rate[0][0]<2500)return -1;
    return Math.min(slope(rate[0],rate[n-1]),slope(rate[Math.floor(n/2)],rate[n-1]));
  }
  function startBuf(){
    if(buf||!want||!cur)return;
    var t0=A.currentTime<0.5&&Date.now()-tapAt<3000?tapAt:Date.now();bufPct=0;
    buf=setInterval(function(){
      var d=total(),h=ahead(),e=A.currentTime+h,now=Date.now(),g=speed(),waited=now-t0;
      var rest=isFinite(d)&&d>0?Math.max(0,d-e):1e9;
      var ge=0.85*g,need=g<0?1e9:ge>=1?4:ge>0.02?Math.min(rest+h,(1/ge-1)*rest+3):1e9;   // 下载比播放慢时：缓冲要够撑到整首下载完
      if(rest<=0.5||(h>=4&&h>=need)||(waited>=MAXWAIT&&h>=1)){stopBuf();go();paint();return;}
      bufPct=Math.max(bufPct,Math.min(99,Math.round(Math.max(need<1e9?h/Math.max(4,need):0,waited/MAXWAIT)*100)));prog();
    },400);
    A.pause();paint();
  }
  function stopBuf(){if(buf){clearInterval(buf);buf=null;}clearTimeout(waitT);bufPct=-1;}
  function prefetch(){   // 这一首已经全部下载好了：先把它存进手机，再趁空把下一首也下载好，换歌时不用等
    if(!cur||!want||!window.fetch||!window.URL||!URL.createObjectURL)return;
    var d=total();if(!(d&&A.currentTime+ahead()>=d-1))return;   // 这一首还没下载完时不抢网速
    var u=byId[cur]?urlOf(byId[cur]):'';
    if(u&&boxOk&&!saved[u]&&!tried[u]&&A.getAttribute('src')===u){   // 刚从网上下载完的这首（一般直接从浏览器缓存里拿，不用再下载）
      if(saving)return;saving=u;tried[u]=1;
      fetch(u,{cache:'force-cache'}).then(function(r){if(!r.ok)throw 0;return r.blob();}).then(function(b){keep(u,b);},function(){})
        .then(function(){saving='';prefetch();});
      return;
    }
    if(saving)return;
    var i=queue.indexOf(cur),nid=queue[i+1]||(loop?queue[0]:'');if(!nid||nid===cur||pre[nid]||!byId[nid])return;
    var nu=urlOf(byId[nid]),o=pre[nid]={ctl:window.AbortController?new AbortController():null};
    if(saved[nu])fromBox(nid,nu).catch(function(){if(pre[nid]===o)delete pre[nid];});
    else fetch(nu,o.ctl?{signal:o.ctl.signal}:{}).then(function(r){if(!r.ok)throw 0;return r.blob();})
      .then(function(b){if(pre[nid]===o)o.url=URL.createObjectURL(b);keep(nu,b);}).catch(function(){if(pre[nid]===o)delete pre[nid];});
    var ks=Object.keys(pre);   // 内存里最多留 3 首
    for(var k=0;k<ks.length&&Object.keys(pre).length>3;k++){var id=ks[k];if(id===cur||id===nid)continue;if(pre[id].url&&A.getAttribute('src')!==pre[id].url)URL.revokeObjectURL(pre[id].url);delete pre[id];}
  }
  function next(step,manual){
    if(!queue.length)makeQueue(cur);var i=queue.indexOf(cur)+step;
    if(i>=queue.length){if(!loop&&!manual){paint();return false;}if(shuf)makeQueue();i=0;}
    if(i<0)i=queue.length-1;
    play(queue[i]);return true;
  }
  function stop(){want=false;stopBuf();A.pause();cur='';A.removeAttribute('src');try{A.load();}catch(e){}paint();prog();}
  function paint(){
    [].forEach.call(wrap.querySelectorAll('.msong'),function(it){
      var on=it.dataset.id===cur,pl=on&&want,x=byId[it.dataset.id]||{};it.classList.toggle('cur',on);it.classList.toggle('playing',pl);it.classList.toggle('buffering',on&&!!buf);
      it.querySelector('[data-mplay]').setAttribute('aria-label',(pl?'暂停':'播放')+'《'+(x.title||'')+'》');
    });
    var show=!!cur,cf=cur&&byId[cur]?folderOf(byId[cur]):'';
    [].forEach.call(wrap.querySelectorAll('.mfold'),function(f){f.classList.toggle('on',!!cf&&f.dataset.f===cf&&want);});
    if(cur)mini.querySelector('.mp-go').setAttribute('href','#music-'+cur);
    mini.hidden=!show;de.classList.toggle('mplay',show);
    if(cur){
      var cx=byId[cur]||{};mini.querySelector('.mp-t').textContent=cx.title||'';var ms=mini.querySelector('.mp-s');ms.textContent=buf?'网络慢，正在缓冲'+(bufPct>0?' '+bufPct+'%':'')+'…':(cx.sub||'');ms.hidden=!buf&&!cx.sub;
      var pp=mini.querySelector('.mp-pp');pp.textContent=want?'❚❚':'▶';pp.setAttribute('aria-label',want?'暂停':'继续播放');
      mini.classList.toggle('paused',!want);mini.classList.toggle('buffering',!!buf);
    }
    var all=page.querySelector('[data-mall]');all.textContent=(cur&&want)?'❚❚ 暂停':(cur?'▶ 继续播放':'▶ 全部播放');
    var lp=page.querySelector('[data-mloop]');lp.setAttribute('aria-pressed',loop?'true':'false');lp.classList.toggle('on',loop);
    var sh=page.querySelector('[data-mshuf]');sh.setAttribute('aria-pressed',shuf?'true':'false');sh.classList.toggle('on',shuf);
  }
  function prog(){
    var t=A.currentTime,d=total(),w=(cur&&d?Math.min(100,t/d*100):0)+'%';
    var it=cur&&cardOf(cur);
    if(it){it.querySelector('.ms-pg b').style.width=w;it.querySelector('.ms-tm').textContent=buf?'缓冲'+(bufPct>0?' '+bufPct+'%':'…'):mmss(t)+(d?' / '+mmss(d):'');}
    mini.querySelector('.mp-pg b').style.width=w;
    if(buf){var ms=mini.querySelector('.mp-s');ms.textContent='网络慢，正在缓冲'+(bufPct>0?' '+bufPct+'%':'')+'…';ms.hidden=false;}
  }
  function media(){
    if(!('mediaSession' in navigator)||!cur)return;
    try{navigator.mediaSession.metadata=new MediaMetadata({title:(byId[cur]||{}).title||'',artist:(byId[cur]||{}).sub||'预言的恩赐 · 音乐',album:'预言的恩赐 · 音乐'});
      navigator.mediaSession.setActionHandler('play',function(){play(cur);});
      navigator.mediaSession.setActionHandler('pause',hold);
      navigator.mediaSession.setActionHandler('previoustrack',function(){next(-1,true);});
      navigator.mediaSession.setActionHandler('nexttrack',function(){next(1,true);});
    }catch(e){}
  }
  A.addEventListener('play',paint);A.addEventListener('timeupdate',prog);
  A.addEventListener('pause',function(){if(A.paused&&!buf&&want&&!A.ended&&A.getAttribute('src')){want=false;}paint();});   // 被系统暂停（来电、别的声音）也算暂停
  A.addEventListener('waiting',function(){   // 播到一半卡住：马上停下来缓冲；刚开始播：给它一秒钟
    clearTimeout(waitT);if(!want||buf)return;
    if(A.currentTime>0.5&&!A.seeking)startBuf();
    else waitT=setTimeout(function(){if(want&&!buf&&A.readyState<3&&!A.seeking)startBuf();},900);
  });
  A.addEventListener('playing',function(){clearTimeout(waitT);unlocked=true;});
  A.addEventListener('progress',prefetch);A.addEventListener('canplaythrough',prefetch);
  A.addEventListener('ended',function(){if(!next(1)){var it=cur&&cardOf(cur);if(it)it.querySelector('.ms-pg b').style.width='0';}});
  A.addEventListener('error',function(){if(cur&&A.getAttribute('src'))toast('《'+((byId[cur]||{}).title||'')+'》没有加载成功，请检查网络后再试。');});
  page.addEventListener('click',function(e){
    var t=e.target,it=t.closest('.msong'),id=it&&it.dataset.id;
    var fl=t.closest('.mfold,.mf-back');   // 文件夹和“全部文件夹”：自己换网址（不让翻页动画接手，它不触发 hashchange）
    if(fl){e.preventDefault();var hh=fl.getAttribute('href');if(location.hash!==hh)location.hash=hh;else sync();return;}
    if(t.closest('[data-mplay]')&&id){if(id===cur&&want)hold();else{makeQueue(id);play(id);}return;}
    var bar=t.closest('.ms-pg');
    if(bar&&id){if(id!==cur){makeQueue(id);play(id);return;}var tt=total();if(tt){var r=bar.getBoundingClientRect();A.currentTime=Math.max(0,Math.min(1,(e.clientX-r.left)/r.width))*tt;}return;}
    if(t.closest('.ms-dl')&&inWx){e.preventDefault();toast('微信里不能直接下载：请点右上角「···」，选「在浏览器打开」，再点“⬇”。');return;}
    if(t.closest('[data-mall]')){if(cur&&want)hold();else if(cur)play(cur);else{makeQueue();if(queue.length)play(queue[0]);}
      var ci=cur&&cardOf(cur);if(ci){var r=ci.getBoundingClientRect();if(r.top<0||r.bottom>innerHeight-80)ci.scrollIntoView({block:'center',behavior:'smooth'});}return;}
    if(t.closest('[data-mloop]')){loop=!loop;set('mloop',loop?'1':'');paint();return;}
    if(t.closest('[data-mshuf]')){shuf=!shuf;set('mshuf',shuf?'1':'');makeQueue(cur);paint();toast(shuf?'已开启随机播放':'已改回按顺序播放');return;}
  });
  var qT=null;page.querySelector('.ms-q').addEventListener('input',function(){var v=this.value;clearTimeout(qT);qT=setTimeout(function(){q=v;render();},150);});
  mini.addEventListener('click',function(e){
    if(e.target.closest('.mp-pp')){e.preventDefault();if(want)hold();else play(cur);}
    else if(e.target.closest('.mp-prev')){e.preventDefault();if(A.currentTime>4){A.currentTime=0;if(!want)play(cur);}else next(-1,true);}   // 播了几秒后按“上一首”先回到这首开头
    else if(e.target.closest('.mp-next')){e.preventDefault();next(1,true);}
    else if(e.target.closest('.mp-go')&&cur){e.preventDefault();var h='#music-'+cur;if(location.hash!==h)location.hash=h;else{sync();hit();}}   // 回到音乐页这首歌所在的文件夹
    else if(e.target.closest('.mp-x')){e.preventDefault();stop();}
  });
  window.addEventListener('hashchange',paint);
  window.addEventListener('q4:tts',function(){if(want)hold();});   // 开始听朗读时音乐先停下
  var fab=document.querySelector('.fab');   // 小窗跟着主页按钮：往下读时一起变成半透明
  if(fab&&window.MutationObserver)new MutationObserver(function(){mini.classList.toggle('glass',fab.classList.contains('glass'));}).observe(fab,{attributes:true,attributeFilter:['class']});
  function top(){var s=page.querySelector('.msearch');if(s)window.scrollTo(0,Math.max(0,s.getBoundingClientRect().top+window.pageYOffset-12));}
  function sync(){   // 按网址打开文件夹：#music → 文件夹列表；#music-f-x → 文件夹 x；#music-<歌> → 那首歌所在的文件夹
    if(!onMusic())return;
    var h=decodeURIComponent(location.hash),m,nf=folder,song=null;
    if(h==='#music')nf='';
    else if((m=/^#music-f-(.+)$/.exec(h)))nf=m[1];
    else if((m=/^#music-(.+)$/.exec(h))&&byId[m[1]]){song=m[1];nf=FOLDERS.length?folderOf(byId[song]):'';}
    var changed=nf!==folder;folder=nf;
    if(q&&(changed||(song&&!shown().some(function(x){return x.id===song;})))){q='';page.querySelector('.ms-q').value='';changed=true;}   // 换文件夹时清掉搜索
    if(changed){render();if(!song)setTimeout(top,0);}
  }
  function hit(){   // 分享出去的单曲链接：打开后滚到那一首，亮一下（等页面切换的滚动做完再滚）
    var m=/^#music-(.+)$/.exec(decodeURIComponent(location.hash));if(!m||/^f-/.test(m[1]))return;
    setTimeout(function(){var it=cardOf(m[1]);if(it){it.scrollIntoView({block:'center'});it.classList.add('hit');setTimeout(function(){it.classList.remove('hit');},2600);}},200);
  }
  window.addEventListener('hashchange',function(){sync();hit();});
  sync();render();hit();
  // 读最新的曲目清单（收了新歌马上出现）
  var fetched=false;
  function refresh(){
    if(fetched||!window.fetch)return;fetched=true;
    fetch(LIST+'?t='+Math.floor(Date.now()/60000),{cache:'no-cache'}).then(function(r){return r.ok?r.json():null;}).then(function(j){
      var s=j&&Array.isArray(j.songs)?j.songs.filter(function(x){return x&&x.id&&x.file&&x.title;}):null;if(!s)return;
      var sig=function(ss,ff){return JSON.stringify([ss.map(function(x){return [x.id,x.title,x.sub,x.folder,x.file];}),(ff||[]).map(function(f){return [f.id,f.name,f.sub];})]);};
      if(sig(s,j.folders)===sig(SONGS,FOLDERS))return;
      take({songs:s,folders:j.folders||[]});index();
      if(/^#music-[^f]|^#music-f[^-]/.test(location.hash)){folder='\u0000';sync();}   // 分享的单曲链接：新清单里才有的歌也能打开
      render();hit();
    }).then(tidy,function(){});
  }
  if(onMusic())refresh();
  window.addEventListener('hashchange',function(){if(onMusic())refresh();});
})();

/* ---------- 网页就绪：开场画面淡出；稍后再换上正文字体（在线版首屏先用手机自带的字体，省下约 800 KB） ---------- */
(function(){
  var d=document.documentElement;d.classList.add('ready');
  setTimeout(function(){var b=document.getElementById('boot');if(b&&b.parentNode)b.parentNode.removeChild(b);},900);
  setTimeout(function(){d.classList.add('wf');},2500);
})();
