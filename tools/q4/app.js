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

  /* ---------- 本周研读时间（只存在本机浏览器；每周从安息日算起） ---------- */
  var GOAL=3600;
  function ymd(x){return x.getFullYear()+'-'+('0'+(x.getMonth()+1)).slice(-2)+'-'+('0'+x.getDate()).slice(-2);}
  function wkKey(){var x=new Date();x=new Date(x.getFullYear(),x.getMonth(),x.getDate());x.setDate(x.getDate()-((x.getDay()+1)%7));return 'time:'+ymd(x);}
  var WK=wkKey(),secs=+(get(WK)||0),last=Date.now(),act=Date.now();
  function goals(){try{return JSON.parse(get('goals')||'[]');}catch(e){return [];}}
  function tick(){
    var n=Date.now(),dt=Math.min(n-last,20000);last=n;
    WK=wkKey(); secs=+(get(WK)||0);
    if(document.visibilityState==='hidden'||n-act>10*60e3)return;
    var before=secs; secs+=dt/1000; set(WK,Math.round(secs*10)/10);
    if(before<GOAL&&secs>=GOAL){
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
    var h=decodeURIComponent(location.hash.slice(1)),m=/^(l\d+|qa\d*|ask)(?:-|$)/.exec(h);
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
      go.href='#l'+D.no+'-'+D.key;
      if(D.sabbath)btn('今日安息日学课堂 →','第'+D.no+'课《'+titleOf(D.no)+'》· 知信行与讨论');
      else btn('进入今日学课 →','第'+D.no+'课《'+titleOf(D.no)+'》· '+(D.key==='sab'?'导言':D.dn));
    }else if(D.before){
      dt.innerHTML=dstr+' · 本季学课将于 <b>9月26日</b> 开始';
      go.href='#l0'; btn('先读本季导言 →','《预言的恩赐》导言与全季总览');
    }else{
      dt.innerHTML=dstr+' · 本季学课已经学完';
      go.href='#home'; btn('本季已学完 →','回顾全季十三课');
    }
    if(D.next){cl.hidden=false;var ca=cl.querySelector('a');ca.href='#l'+D.next+'-sab';ca.textContent='今天下午开始新课：第'+D.next+'课《'+titleOf(D.next)+'》';}
    var mins=Math.floor(secs/60),h=Math.floor(mins/60),mm=mins%60;
    W.querySelector('.wmin').textContent=(h?h+' 小时 ':'')+mm+' 分钟';
    var lit=Math.min(12,Math.floor(secs/300));
    W.querySelectorAll('.wstars i').forEach(function(s,j){s.classList.toggle('on',j<lit);});
    W.style.setProperty('--p',Math.min(1,secs/GOAL).toFixed(3));
    var glory=secs>=GOAL; W.classList.toggle('glory',glory);
    W.querySelector('.m0').hidden=glory; W.querySelector('.m1').hidden=!glory;
    if(glory){var g=goals();if(g.indexOf(WK)<0){g.push(WK);set('goals',JSON.stringify(g));}W.querySelector('.wn').textContent=g.length;}
    verse();
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
    if(e.target.closest('.wshuf'))verse();
  });
  document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!W.hidden)close(true);});
  window.addEventListener('hashchange',function(){if(!W.hidden&&location.hash&&location.hash!=='#home')close(false);});
  document.querySelectorAll('[data-welcome]').forEach(function(b){b.addEventListener('click',function(e){e.preventDefault();open();});});

  /* ---------- 随时返回主页（欢迎页）：先确认，再打开欢迎页；关掉欢迎页就回到原来的位置 ---------- */
  var HC=document.getElementById('hconf'),fab=document.querySelector('.fab');
  if(HC){
    var hcT=null,back=null;
    var ask=function(){clearTimeout(hcT);back=document.activeElement;if(fab)fab.classList.remove('on');HC.hidden=false;void HC.offsetWidth;HC.classList.add('open');setTimeout(function(){HC.querySelector('[data-hok]').focus({preventScroll:true});},40);};
    var shut=function(){HC.classList.remove('open');hcT=setTimeout(function(){HC.hidden=true;},240);};
    document.addEventListener('click',function(e){
      if(e.target.closest('[data-gohome]')){e.preventDefault();e.stopPropagation();ask();return;}
      if(HC.hidden)return;
      if(e.target.closest('[data-hok]')){e.preventDefault();shut();open();return;}
      if(e.target.closest('[data-hno]')){e.preventDefault();shut();if(back&&back.focus)back.focus({preventScroll:true});}
    },true);
    document.addEventListener('keydown',function(e){if(!HC.hidden&&e.key==='Escape'){e.stopPropagation();shut();}},true);
  }
  if(fab){
    // 往下读时藏起来，不挡字；往回滑一下就出现，3 秒不动又自动收起；宽屏放在正文右侧空白处，一直显示
    var wide=window.matchMedia?matchMedia('(min-width:1360px)'):{matches:false},lastY=window.scrollY,fT=null;
    var show=function(v){fab.classList.toggle('on',v);};
    addEventListener('scroll',function(){
      var y=window.scrollY,dy=y-lastY;lastY=y;
      if(!W.hidden||!HC||!HC.hidden)return;
      if(wide.matches){show(y>240);return;}
      var end=y+innerHeight>document.documentElement.scrollHeight-260;
      if(y<240||end||dy>3){clearTimeout(fT);show(false);}
      else if(dy<-3){show(true);clearTimeout(fT);fT=setTimeout(function(){show(false);},3000);}
    },{passive:true});
    window.addEventListener('hashchange',function(){clearTimeout(fT);show(false);});
  }

  /* ---------- 分享：微信分享 / 复制链接 / 系统分享；电脑上显示二维码 ---------- */
  var SH=document.getElementById('shsheet'),WG=document.getElementById('wxguide'),GF=document.getElementById('gift'),GP=[],lastG=-1;
  try{GP=JSON.parse(document.getElementById('giftpool').textContent);}catch(err){}
  var UA=navigator.userAgent,inWx=/MicroMessenger/i.test(UA),mobile=/Android|iPhone|iPad|iPod|Mobile|HarmonyOS|OpenHarmony/i.test(UA);
  var shUrl='',shTitle='',shT=null;
  function markShared(){set('sharePending','1');}
  function shText(){return '【问题彩蛋】'+shTitle+'\n'+shUrl;}
  function shDone(html,sent){SH.querySelector('.sh-done').innerHTML=html;SH.querySelector('.sh-sent').hidden=!sent;}
  function shOpen(id){
    var pg=document.getElementById(id),isList=id==='qa';
    shTitle=isList?'学课问题深度解答合集':(pg&&pg.dataset.title||document.title).replace(/ · 问题彩蛋$/,'');
    shUrl=(SH.dataset.base||location.href.split('#')[0])+'#'+id;
    SH.querySelector('#sh-h').textContent=isList?'分享问题彩蛋':(id==='ask'?'分享提问区':'分享这篇问答');
    if(id==='ask')shTitle='提问区：读学课有问题，一起来问';
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
  if(src.dataset.src){var pre=function(){setTimeout(fetchData,1500);};if(document.readyState==='complete')pre();else addEventListener('load',pre);}
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

/* ---------- 提问区：腾讯云开发（匿名身份）存问题与回复 ---------- */
(function(){
  var P=document.querySelector('.askpage');if(!P)return;
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);}catch(e){}}
  function $(s,r){return (r||P).querySelector(s);}
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  var ENV=P.dataset.env,SDK=P.dataset.sdk,MOCK=/[?&]askmock/.test(location.search);
  var app=null,db=null,uid='',QS=[],RS={},filter='all',PAGE=40,more=false,started=false,busy=false;
  var card=$('.askcard'),msg=$('.ask-msg'),list=$('.ask-items');

  /* ---- 连接后台（或测试用的本机模拟） ---- */
  function loadSDK(){return new Promise(function(ok,no){if(window.cloudbase)return ok();var s=document.createElement('script');s.src=SDK;s.onload=function(){window.cloudbase?ok():no({code:'SDK_LOAD'});};s.onerror=function(){no({code:'SDK_LOAD'});};document.head.appendChild(s);});}
  var mock={
    q:function(){try{return JSON.parse(localStorage.getItem('q4:mockdb')||'{"questions":[],"replies":[]}');}catch(e){return {questions:[],replies:[]};}},
    w:function(d){localStorage.setItem('q4:mockdb',JSON.stringify(d));}
  };
  function when(d){if(!d)return 0;if(d.$date)d=d.$date;var t=new Date(d).getTime();return isNaN(t)?0:t;}
  var ME_ADMIN=false;
  function row(t,x){   // 数据库的一行 → 页面里用的格式
    var o={_id:x.id,name:x.name,loc:x.loc,text:x.body,uid:x.user_id,ts:when(x.created_at)};
    if(t==='questions')o.allow=x.allow_reply!==false;else{o.qid=x.question_id;o.admin=!!x.is_admin;}
    return o;
  }
  function chk(r){if(r&&r.error)throw r.error;return (r&&r.data)||[];}
  var store={
    init:function(){
      if(MOCK){uid=get('mockuid')||('u'+Math.random().toString(36).slice(2,10));set('mockuid',uid);ME_ADMIN=/[?&]askadmin/.test(location.search);return Promise.resolve();}
      if(location.protocol==='file:')return Promise.reject({code:'FILE'});
      return loadSDK().then(function(){
        app=window.cloudbase.init({env:ENV,timeout:15000});
        var auth=app.auth();
        return auth.getLoginState().then(function(st){
          if(st&&st.user)return st;
          return auth.signInAnonymously().then(function(r){if(r&&r.error)throw r.error;});
        }).then(function(){return auth.getCurrentUser();}).then(function(u){
          uid=(u&&(u.uid||u.id))||'';db=app.rdb();
          return db.rpc('q4_whoami').then(function(r){if(r&&!r.error&&r.data){if(r.data.uid)uid=r.data.uid;ME_ADMIN=!!r.data.admin;}}).catch(function(){});
        });
      });
    },
    list:function(before){
      if(MOCK){var d=mock.q(),a=d.questions.slice().sort(function(x,y){return y.ts-x.ts;});if(before)a=a.filter(function(x){return x.ts<before;});return Promise.resolve(a.slice(0,PAGE));}
      var q=db.from('questions').select('*').order('created_at',{ascending:false}).limit(PAGE);
      if(before)q=q.lt('created_at',new Date(before).toISOString());
      return q.then(chk).then(function(a){return a.map(function(x){return row('questions',x);});});
    },
    replies:function(ids){
      if(!ids.length)return Promise.resolve([]);
      if(MOCK){var d=mock.q();return Promise.resolve(d.replies.filter(function(x){return ids.indexOf(x.qid)>=0;}));}
      return db.from('replies').select('*').in('question_id',ids).order('created_at',{ascending:true}).limit(1000)
        .then(chk).then(function(a){return a.map(function(x){return row('replies',x);});});
    },
    add:function(coll,doc){
      if(MOCK){var d=mock.q();doc.uid=uid;doc.ts=Date.now();doc._id='m'+Date.now()+Math.random().toString(36).slice(2,6);if(coll==='replies')doc.admin=ME_ADMIN;d[coll].push(doc);mock.w(d);return Promise.resolve(doc);}
      var x={name:doc.name,loc:doc.loc||'',body:doc.text};
      if(coll==='questions')x.allow_reply=doc.allow!==false;else{x.question_id=doc.qid;x.is_admin=ME_ADMIN;}
      return db.from(coll).insert(x).select().then(chk).then(function(a){if(!a[0])throw {code:'PERMISSION'};return row(coll,a[0]);});
    },
    remove:function(coll,id){
      if(MOCK){var d=mock.q();d[coll]=d[coll].filter(function(x){return x._id!==id;});if(coll==='questions')d.replies=d.replies.filter(function(x){return x.qid!==id;});mock.w(d);return Promise.resolve();}
      return db.from(coll).delete().eq('id',id).select().then(chk).then(function(a){if(!a.length)throw {code:'PERMISSION'};});
    }
  };
  function why(e){
    var c=(e&&(e.code||e.errCode||e.error))||'',m=(e&&(e.message||e.msg))||'';c=String(c);var s=c+' '+m;
    if(c==='FILE')return '提问区需要联网使用：请用在线版打开 '+P.dataset.online+'#ask';
    if(c==='SDK_LOAD')return '提问区工具没能加载，请检查网络后点“刷新”。';
    if(/PGRST204|42703|column/i.test(s))return '数据表还没设置好：请在云开发数据库里运行“提问区设置脚本”。（'+c+'）';
    if(/42501|PERMISSION|permission denied|row-level security|violates/i.test(s))return '没有权限：请确认已运行“提问区设置脚本”，或刷新后再试。（'+c+'）';
    if(/Failed to fetch|NetworkError|SERVICE_ERROR|Load failed/i.test(s)&&location.hostname==='2377568565.github.io')return '连不上提问区：请确认云开发“安全域名”里已添加 2377568565.github.io，或检查网络后点“刷新”。（'+c+'）';
    if(/INVALID_REQUEST_SOURCE|domain|origin|cors/i.test(s))return '连接被拒绝：请在云开发控制台把 2377568565.github.io 加入“安全域名”。（'+c+'）';
    if(/anonymous|ANONYMOUS|DISABLED|provider/i.test(s))return '登录失败：请在云开发控制台打开“匿名登录”。（'+c+'）';
    if(/COLLECTION|NOT_EXIST|not exist/i.test(s))return '数据表还没建好：请在云开发“数据库”里新建 questions 和 replies 两个集合。（'+c+'）';
    if(/PERMISSION|permission|denied/i.test(s))return '没有权限：请把 questions、replies 两个集合的权限设为“读取全部数据，修改本人数据”。（'+c+'）';
    return '暂时连不上提问区，请稍后点“刷新”再试。（'+(c||m||'未知错误')+'）';
  }

  /* ---- 地区：按网络自动识别到“省 + 市” ---- */
  function ipLoc(){
    var c=get('askloc'),day=new Date().toDateString();
    if(c&&get('asklocday')===day)return Promise.resolve(c);
    if(MOCK)return Promise.resolve(get('askloc')||'浙江省杭州市');
    return new Promise(function(ok){
      var cb='q4ip'+Date.now(),s=document.createElement('script'),t=setTimeout(function(){fin('');},8000);
      function fin(v){clearTimeout(t);try{delete window[cb];}catch(e){window[cb]=undefined;}if(s.parentNode)s.parentNode.removeChild(s);if(v){set('askloc',v);set('asklocday',day);}ok(v||c||'');}
      window[cb]=function(d){var p=(d&&d.pro)||'',ci=(d&&d.city)||'';if(ci===p)ci='';var v=(p+ci).replace(/\s+/g,'');if(!v&&d&&d.addr)v=String(d.addr).trim().split(/\s+/)[0]||'';fin(v);};
      s.charset='gbk';s.src='https://whois.pconline.com.cn/ipJson.jsp?callback='+cb;   // 用 JSONP 形式（不要 json=true，否则返回纯 JSON 会被浏览器拦截）s.onerror=function(){fin('');};document.head.appendChild(s);
    });
  }
  var LOC='';
  function showLoc(){$('.ask-locv').textContent=LOC?LOC+(get('asklocman')?'':'（自动识别）'):'地区未识别';}

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
    else if(t===2){hi.textContent='这是你本周的第 '+(wk+1)+' 个问题 ✦ 好问题带来好学习。';bd.hidden=false;bd.textContent='✦ 本周提问者';}
    else{hi.textContent='本周已经问了 '+wk+' 个问题！像庇哩亚人一样“天天考查圣经”（徒17:11）。';bd.hidden=false;bd.textContent='✦✦ 本周追问者';}
    if(n>=10){bd.hidden=false;bd.textContent='✦✦✦ 庇哩亚人 · 已提 '+n+' 问';}
  }
  function isMine(x){return !!uid&&x.uid===uid;}
  function isAdmin(x){return !!x.admin;}

  /* ---- 显示 ---- */
  function fmt(t){if(!t)return '';var d=new Date(t),z=function(n){return (n<10?'0':'')+n;};return d.getFullYear()+'-'+z(d.getMonth()+1)+'-'+z(d.getDate())+' '+z(d.getHours())+':'+z(d.getMinutes());}
  function ts(x){return x.ts||when(x.createdAt);}
  function item(q){
    var rs=RS[q._id]||[],adm=rs.filter(isAdmin),mine=isMine(q);
    var h='<article class="aq'+(mine?' mine':'')+(adm.length?' answered':'')+'" data-id="'+esc(q._id)+'">'+
      '<header class="aq-h"><span class="aq-av" aria-hidden="true">'+esc((q.name||'友').slice(0,1))+'</span><span class="aq-who"><b>'+esc(q.name||'匿名')+'</b>'+(mine?'<i class="aq-me">我</i>':'')+
      '<span class="aq-meta">'+esc(q.loc||'地区未知')+' · '+esc(fmt(ts(q)))+'</span></span><button type="button" class="aq-copy" data-copyq>复制</button></header>'+
      '<p class="aq-t">'+esc(q.text)+'</p><div class="aq-f">';
    if(adm.length)h+='<span class="aq-tag gold">✦ 管理员已回答</span>';
    if(q.allow===false)h+='<span class="aq-tag">只要管理员回答</span>';
    h+='<span class="sp"></span>';
    if(q.allow!==false||ME_ADMIN)h+='<button type="button" class="aq-rb" data-reply>回复'+(rs.length?' · '+rs.length:'')+'</button>';
    else if(rs.length)h+='<span class="aq-rc">'+rs.length+' 条回复</span>';
    if(mine||ME_ADMIN)h+='<button type="button" class="aq-del" data-delq>删除</button>';
    h+='</div>';
    if(rs.length){h+='<div class="aq-rs">';rs.slice().sort(function(a,b){return isAdmin(b)-isAdmin(a)||ts(a)-ts(b);}).forEach(function(r){
      var ad=isAdmin(r);h+='<div class="aq-r'+(ad?' admin':'')+'" data-rid="'+esc(r._id)+'"><p class="aq-rh"><b>'+esc(ad?(r.name||'整理者'):(r.name||'匿名'))+'</b>'+(ad?'<i class="aq-adm">管理员回答</i>':'')+
        '<span>'+esc(r.loc||'')+' · '+esc(fmt(ts(r)))+'</span>'+((isMine(r)||ME_ADMIN)?'<button type="button" class="aq-rdel" data-delr>删除</button>':'')+'</p><p class="aq-rt">'+esc(r.text)+'</p></div>';});
      h+='</div>';}
    h+='<div class="aq-rf" hidden><textarea maxlength="300" rows="2" placeholder="写下你的回复（300 字以内）"></textarea><button type="button" class="btn solid" data-sendr>发送回复</button><p class="aq-rmsg"></p></div></article>';
    return h;
  }
  function render(){
    var a=QS.filter(function(q){return filter==='mine'?isMine(q):filter==='answered'?(RS[q._id]||[]).some(isAdmin):true;});
    $('.ask-n').textContent=QS.length?'（'+QS.length+(more?'+':'')+'）':'';
    list.innerHTML=a.length?a.map(item).join(''):'<p class="ask-empty">'+(filter==='mine'?'你还没有提过问题。':filter==='answered'?'还没有管理员回答过的问题。':'还没有人提问，来做第一个提问的人吧！')+'</p>';
    $('.ask-more').hidden=!more||filter!=='all';
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
    if(!MOCK&&!db){msg.textContent='正在连接提问区，请稍等几秒再发。';return;}
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
    if(!MOCK&&!db){m.textContent='正在连接提问区，请稍等几秒再发。';return;}
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
    if(t.closest('.ask-locedit')){var v=window.prompt('请输入你的地区（例如：浙江省杭州市）',LOC);if(v!=null){v=v.trim().slice(0,20);if(v){LOC=v;set('askloc',v);set('asklocday',new Date().toDateString());set('asklocman','1');showLoc();}}return;}
    var chip=t.closest('.chip[data-f]');if(chip){filter=chip.dataset.f;P.querySelectorAll('.ask-filter .chip[data-f]').forEach(function(c){c.classList.toggle('on',c===chip);});render();return;}
    if(t.closest('.ask-refresh')){list.innerHTML='<p class="ask-empty">正在刷新……</p>';if(!started||!(db||MOCK)){started=false;open();}else load();return;}
    if(t.closest('.ask-more')){load(true);return;}
    if(t.closest('.ask-copyall')){
      var a=QS.filter(function(q){return filter==='mine'?isMine(q):filter==='answered'?(RS[q._id]||[]).some(isAdmin):true;});
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
    if(t.closest('[data-reply]')){var f=art.querySelector('.aq-rf');f.hidden=!f.hidden;if(!f.hidden)f.querySelector('textarea').focus();return;}
    if(t.closest('[data-sendr]'))return sendReply(art);
    if(t.closest('[data-delq]')){if(!window.confirm('确定删除这个问题吗？删除后不能恢复。'))return;store.remove('questions',q._id).then(function(){QS=QS.filter(function(x){return x._id!==q._id;});render();}).catch(function(e){window.alert('删除没有成功：'+why(e));});return;}
    var rd=t.closest('[data-delr]');if(rd){var rid=rd.closest('.aq-r').dataset.rid;if(!window.confirm('确定删除这条回复吗？'))return;store.remove('replies',rid).then(function(){RS[q._id]=(RS[q._id]||[]).filter(function(x){return x._id!==rid;});render();}).catch(function(e){window.alert('删除没有成功：'+why(e));});}
  });
  $('.ask-text').addEventListener('input',function(){$('.ask-count').textContent=this.value.length+' / 500';});

  function open(){
    if(started)return;started=true;
    $('.ask-name').value=get('askname')||'';
    ipLoc().then(function(v){LOC=v;showLoc();});
    store.init().then(function(){load();}).catch(function(e){list.innerHTML='<p class="ask-empty err">'+esc(why(e))+'</p>';started=false;});
  }
  window.q4ask={open:open};
  if(/^#ask(?:-|$)/.test(location.hash))open();
})();
