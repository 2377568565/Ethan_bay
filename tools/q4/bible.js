/* “圣经”栏目（2026-10-26）：和合本、KJV、原文，切换和对照；书卷、出处、人名地名和词语、全文搜索。
   数据按卷放在 site/bible/（文件名带内容哈希），下载一次就存在手机里（IndexedDB “q4bible”，和网站其他缓存分开，免得被清理掉）。 */
(function(){
  'use strict';
  var $=function(s,r){return (r||document).querySelector(s);};
  function esc(s){return String(s==null?'':s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);}catch(e){}}
  var toastT;function toast(m){var t=$('#toast');t.textContent=m;t.classList.add('on');clearTimeout(toastT);toastT=setTimeout(function(){t.classList.remove('on');},1600);}

  /* ---------- 存在手机里的数据 ---------- */
  var DB=null;
  function db(){if(!DB)DB=new Promise(function(ok){try{var r=indexedDB.open('q4bible',1);r.onupgradeneeded=function(){r.result.createObjectStore('f');};
    r.onsuccess=function(){ok(r.result);};r.onerror=r.onblocked=function(){ok(null);};}catch(e){ok(null);}});return DB;}
  function idb(mode,fn){return db().then(function(d){if(!d)return null;return new Promise(function(ok){
    try{var t=d.transaction('f',mode),q=fn(t.objectStore('f'));t.oncomplete=function(){ok(q?q.result:null);};t.onerror=t.onabort=function(){ok(null);};}catch(e){ok(null);}});});}
  var MEM={};
  function load(fn){
    if(MEM[fn])return MEM[fn];
    var url='site/bible/'+fn;
    return MEM[fn]=idb('readonly',function(s){return s.get(fn);}).then(function(v){
      if(v!=null)return JSON.parse(v);
      return fetch(url).then(function(r){if(!r.ok)throw new Error(r.status);return r.text();}).then(function(t){idb('readwrite',function(s){return s.put(t,fn);});return JSON.parse(t);});
    }).catch(function(e){delete MEM[fn];throw e;});
  }
  function prune(keep){idb('readwrite',function(s){if(!s.getAllKeys)return null;var q=s.getAllKeys();q.onsuccess=function(){(q.result||[]).forEach(function(k){if(keep.indexOf(k)<0)s.delete(k);});};return q;});}

  /* ---------- 书卷 ---------- */
  var IX,BK=[];   // BK[i] = {n:全名, ab:[简称], en:英文, code, ini:拼音首字母, py:全拼, nc:章数}
  var CAT=[[0,4,'律法书','--c4'],[5,16,'历史书','--c1'],[17,21,'诗歌智慧书','--c5'],[22,26,'大先知书','--c3'],[27,38,'小先知书','--c3'],
           [39,42,'福音书','--c6'],[43,43,'历史书','--c1'],[44,56,'保罗书信','--c2'],[57,64,'其他书信','--c2'],[65,65,'预言书','--c5']];
  function cat(i){for(var k=0;k<CAT.length;k++)if(i>=CAT[k][0]&&i<=CAT[k][1])return CAT[k];return CAT[0];}
  function ab(i){return BK[i].ab[0];}

  /* ---------- 状态 ---------- */
  var S={b:0,c:1,mode:'cuv',cmp:{cuv:1,kjv:1,org:0},fs:1};
  try{var sv=JSON.parse(get('bible')||'{}');for(var k in sv)S[k]=sv[k];}catch(e){}
  function save(){set('bible',JSON.stringify({b:S.b,c:S.c,mode:S.mode,cmp:S.cmp,fs:S.fs}));}
  var FS=[.92,1,1.1,1.22,1.36];

  /* ---------- 地址：#58.11 或 #58.11.1（卷从 1 数起，和常见的书卷编号一致） ---------- */
  function readHash(){var m=/^#(\d+)\.(\d+)(?:\.(\d+))?/.exec(location.hash);if(!m)return null;return {b:+m[1]-1,c:+m[2],v:m[3]?+m[3]:0};}
  function go(b,c,v,push){
    b=Math.max(0,Math.min(65,b));c=Math.max(1,Math.min(BK[b].nc,c));
    var h='#'+(b+1)+'.'+c+(v?'.'+v:'');
    if(location.hash!==h){if(push===false)history.replaceState(null,'',h);else location.hash=h;}else render(b,c,v);
  }
  window.addEventListener('hashchange',function(){var r=readHash();if(r)render(r.b,r.c,r.v);});

  /* ---------- 显示一章 ---------- */
  var cur={};
  function files(b){var f=IX.files,p=('0'+b).slice(-2);return {cuv:f['cuv-'+p],kjv:f['kjv-'+p],org:f['org-'+p]};}
  function need(){var m=S.mode;return {cuv:m==='cuv'||(m==='cmp'&&S.cmp.cuv),kjv:m==='kjv'||(m==='cmp'&&S.cmp.kjv),org:m==='org'||(m==='cmp'&&S.cmp.org)};}
  function render(b,c,v){
    S.b=b;S.c=c;save();
    var N=need(),F=files(b),main=$('#main'),tok={};cur=tok;
    $('#where').textContent=BK[b].n+' '+c;
    document.title=BK[b].n+' '+c+' · 圣经';
    var ps=[load(F.cuv),N.kjv?load(F.kjv):Promise.resolve(null),N.org?load(F.org):Promise.resolve(null)];   // 和合本总是要（标题、经文菜单都用到）
    var slow=setTimeout(function(){if(cur===tok)main.innerHTML='<p class="load">正在下载这一卷（下载一次以后就存在手机里）……</p>';},250);
    Promise.all(ps).then(function(r){
      clearTimeout(slow);if(cur!==tok)return;
      draw(b,c,r[0],r[1],r[2]);
      if(v){var el=document.getElementById('v'+v);if(el){el.scrollIntoView({block:'center'});el.classList.remove('flash');void el.offsetWidth;el.classList.add('flash');}}
      else window.scrollTo(0,0);
    },function(){clearTimeout(slow);if(cur===tok)main.innerHTML='<p class="load">下载失败，请检查网络后<a href="javascript:location.reload()">重新打开</a>。</p>';});
  }
  function numLabel(arr,v){   // 和合本把几节印在一起：这一节的号码写成“6-7”
    var e=v;while(e<arr.length&&!arr[e])e++;
    return e>v?v+'-'+e:String(v);
  }
  function orgLine(words,ot){
    return '<div class="ol"'+(ot?' dir="rtl"':'')+'>'+words.map(function(w,i){
      return '<span class="w" data-w="'+i+'"><span class="o">'+esc(w[0])+'</span><span class="t">'+esc(w[1])+'</span><span class="g">'+esc(w[2])+'</span></span>';}).join('')+'</div>';
  }
  var DATA={};
  function draw(b,c,cuv,kjv,org){
    var ch=cuv[c-1]||[],kc=kjv?kjv[c-1]||[]:[],oc=org?org.v[c-1]||[]:[],ot=b<39,m=S.mode,h=[];
    DATA={b:b,c:c,cuv:ch,kjv:kc,org:oc,lx:org?org.x:null};
    var nv=Math.max(ch.length,m==='kjv'||m==='cmp'&&S.cmp.kjv?kc.length:0,m==='org'?oc.length:0);
    h.push('<div class="chead"><h1>'+esc(BK[b].n)+'</h1><p>第 '+c+' 章'+(BK[b].nc>1?' / 共 '+BK[b].nc+' 章':'')+'</p></div>');
    if(m==='cmp'){
      var cols=[];if(S.cmp.cuv)cols.push('和合本');if(S.cmp.kjv)cols.push('KJV');if(S.cmp.org)cols.push(ot?'希伯来文':'希腊文');
      if(!cols.length){cols=['和合本'];S.cmp.cuv=1;}
      h.push('<div class="cmphead" style="--cols:repeat('+cols.length+',1fr)">'+cols.map(function(x){return '<span>'+x+'</span>';}).join('')+'</div>');
      h.push('<div class="vs cmp" style="--cols:repeat('+cols.length+',1fr)">');
    }else h.push('<div class="vs">');
    for(var v=1;v<=nv;v++){
      var t=ch[v-1],k=kc[v-1],o=oc[v-1];
      if(m==='cuv'){if(!t)continue;h.push('<span class="v" id="v'+v+'" data-v="'+v+'"><sup class="n">'+numLabel(ch,v)+'</sup>'+esc(t)+'</span>');}
      else if(m==='kjv'){if(!k)continue;h.push('<span class="v" id="v'+v+'" data-v="'+v+'"><sup class="n">'+v+'</sup>'+esc(k)+'</span>');}
      else if(m==='org'){if(!o||!o.length)continue;h.push('<div class="v" id="v'+v+'" data-v="'+v+'"><span class="vn">'+v+'</span>'+orgLine(o,ot)+'</div>');}
      else{
        var rows='';
        if(S.cmp.cuv)rows+='<div class="row"><span class="lb">和合</span><div>'+(t?'<sup class="n">'+numLabel(ch,v)+'</sup>'+esc(t):'<span class="tip">（和上一节合在一起）</span>')+'</div></div>';
        if(S.cmp.kjv)rows+='<div class="row k"><span class="lb">KJV</span><div><sup class="n">'+v+'</sup>'+esc(k||'')+'</div></div>';
        if(S.cmp.org)rows+='<div class="row"><span class="lb">原文</span><div>'+(o&&o.length?orgLine(o,ot):'')+'</div></div>';
        h.push('<div class="v" id="v'+v+'" data-v="'+v+'">'+rows+'</div>');
      }
    }
    h.push('</div>');
    if(m==='org'||m==='cmp'&&S.cmp.org)h.push('<p class="note">原文据 STEPBible 的 TAHOT（希伯来文旧约）和 TAGNT（希腊文新约），CC BY 4.0；每个词下面是读音和英文直译，点一个词可以看词典里的原形和字义。</p>');
    if(m==='kjv'||m==='cmp'&&S.cmp.kjv)h.push('<p class="note">英文是英王钦定本（KJV，公有领域）。分节偶尔和和合本不同。</p>');
    var pv=prev(b,c),nx=next(b,c);
    h.push('<div class="pn"><button type="button" data-go="'+(pv?pv.join('.'):'')+'"'+(pv?'':' disabled')+'>‹ '+(pv?esc(BK[pv[0]].n)+' '+pv[1]:'')+'</button>'+
           '<button type="button" data-go="'+(nx?nx.join('.'):'')+'"'+(nx?'':' disabled')+'>'+(nx?esc(BK[nx[0]].n)+' '+nx[1]:'')+' ›</button></div>');
    $('#main').innerHTML=h.join('');
  }
  function prev(b,c){return c>1?[b,c-1]:b>0?[b-1,BK[b-1].nc]:null;}
  function next(b,c){return c<BK[b].nc?[b,c+1]:b<65?[b+1,1]:null;}

  /* ---------- 点经文、点原文的词 ---------- */
  document.addEventListener('click',function(e){
    var g=e.target.closest('[data-go]');if(g&&g.dataset.go){var p=g.dataset.go.split('.');go(+p[0],+p[1]);return;}
    var w=e.target.closest('.w');
    if(w&&DATA.lx&&!e.target.closest('#vm')){
      var v=w.closest('.v');showVerse(+v.dataset.v,+w.dataset.w);return;}
    var v2=e.target.closest('#main .v');if(v2)showVerse(+v2.dataset.v,-1);
  });
  function refText(v){return ab(DATA.b)+DATA.c+':'+v;}
  function showVerse(v,wi){
    var t=DATA.cuv[v-1],k=DATA.kjv[v-1],o=DATA.org[v-1];
    $('#vmt').textContent=BK[DATA.b].n+' '+DATA.c+':'+v;
    var h='';
    if(t)h+='<p class="vq">'+esc(t)+'</p>';
    if(k&&S.mode!=='cuv')h+='<p class="vq en" style="margin-top:8px;color:var(--ink-2)">'+esc(k)+'</p>';
    if(wi>=0&&o&&o[wi]){var w=o[wi],lx=DATA.lx[w[3]]||[];h+='<div class="lex"><b>'+esc(w[0])+'</b> '+esc(w[1])+' · '+esc(w[2])+(lx[0]?'<br>词典原形：<b>'+esc(lx[0])+'</b>（'+esc(w[3])+'）'+(lx[1]?' · '+esc(lx[1]):''):'')+'</div>';}
    h+='<div class="acts"><button type="button" data-a="copy">复制</button><button type="button" data-a="org">原文逐字</button><button type="button" data-a="cmp">三版对照</button></div>';
    $('#vmb').innerHTML=h;$('#vmb').dataset.v=v;
    document.querySelectorAll('#main .v.sel').forEach(function(x){x.classList.remove('sel');});
    var el=document.getElementById('v'+v);if(el)el.classList.add('sel');
    open('#vm');
  }
  $('#vm').addEventListener('click',function(e){
    var a=e.target.closest('[data-a]');if(!a)return;var v=+$('#vmb').dataset.v;
    if(a.dataset.a==='copy'){
      var t=DATA.cuv[v-1]||'',s='“'+t+'”（'+refText(v)+' 和合本）';
      (navigator.clipboard&&window.isSecureContext?navigator.clipboard.writeText(s):Promise.reject()).then(function(){toast('已复制');},function(){
        var ta=document.createElement('textarea');ta.value=s;document.body.appendChild(ta);ta.select();try{document.execCommand('copy');toast('已复制');}catch(e){}ta.remove();});
      close();
    }else{
      var want=a.dataset.a==='org'?{org:1}:{cuv:1,kjv:1,org:1},b=DATA.b,c=DATA.c;
      Promise.all([load(files(b).cuv),load(files(b).kjv),load(files(b).org)]).then(function(r){
        var ot=b<39,h='',k=(r[1][c-1]||[])[v-1],o=(r[2].v[c-1]||[])[v-1]||[],t=(r[0][c-1]||[])[v-1];
        if(want.cuv&&t)h+='<p class="vq">'+esc(t)+'</p>';
        if(want.kjv&&k)h+='<p class="vq en" style="margin-top:8px;color:var(--ink-2)">'+esc(k)+'</p>';
        h+=orgLine(o,ot);
        h+='<p class="note" style="margin-top:8px">每个词下面是读音和英文直译（STEPBible，CC BY 4.0）。</p>';
        DATA.lx=DATA.lx||r[2].x;if(!DATA.org.length)DATA.org=r[2].v[c-1]||[];
        $('#vmb').innerHTML=h;$('#vmb').dataset.v=v;
      });
    }
  });
  $('#vmb').addEventListener('click',function(e){   // 弹窗里的原文词：显示词典
    var w=e.target.closest('.w');if(!w)return;
    var v=+$('#vmb').dataset.v,o=DATA.org[v-1],x=o&&o[+w.dataset.w],lx=x&&DATA.lx&&DATA.lx[x[3]];if(!x)return;
    var old=$('#vmb .lex');if(old)old.remove();
    $('#vmb').insertAdjacentHTML('beforeend','<div class="lex"><b>'+esc(x[0])+'</b> '+esc(x[1])+' · '+esc(x[2])+(lx&&lx[0]?'<br>词典原形：<b>'+esc(lx[0])+'</b>（'+esc(x[3])+'）'+(lx[1]?' · '+esc(lx[1]):''):'')+'</div>');
  });

  /* ---------- 面板 ---------- */
  var opened=null;
  function open(s){close();opened=$(s);opened.hidden=false;document.body.style.overflow='hidden';}
  function close(){if(opened){opened.hidden=true;opened=null;document.body.style.overflow='';document.querySelectorAll('#main .v.sel').forEach(function(x){x.classList.remove('sel');});}}
  document.addEventListener('click',function(e){if(e.target.closest('[data-close]'))close();});
  document.addEventListener('keydown',function(e){
    if(e.key==='Escape')close();
    if(opened||/INPUT|TEXTAREA/.test((e.target||{}).tagName||''))return;
    if(e.key==='ArrowLeft'){var p=prev(S.b,S.c);if(p)go(p[0],p[1]);}
    if(e.key==='ArrowRight'){var n=next(S.b,S.c);if(n)go(n[0],n[1]);}
    if(e.key==='/'||(e.key==='k'&&(e.ctrlKey||e.metaKey))){e.preventDefault();openFind();}
  });

  /* ---------- 版本开关 ---------- */
  function setMode(m){S.mode=m;document.body.dataset.mode=m;
    document.querySelectorAll('.modes [data-mode]').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.mode===m?'true':'false');});save();}
  document.querySelector('.modes').addEventListener('click',function(e){var b=e.target.closest('[data-mode]');if(!b)return;setMode(b.dataset.mode);render(S.b,S.c,0);});
  document.querySelectorAll('[data-cmp]').forEach(function(x){x.checked=!!S.cmp[x.dataset.cmp];x.addEventListener('change',function(){S.cmp[x.dataset.cmp]=x.checked?1:0;save();render(S.b,S.c,0);});});
  function setFs(){document.documentElement.style.setProperty('--fs',(1.06*FS[S.fs])+'rem');}
  $('[data-font]').addEventListener('click',function(){S.fs=(S.fs+1)%FS.length;setFs();save();toast('字号 '+(S.fs+1)+' / '+FS.length);});

  /* ---------- 选书卷、选章 ---------- */
  var pickT='ot',pickB=-1;
  function drawPick(){
    var h='';
    if(pickB<0){
      var lo=pickT==='ot'?0:39,hi=pickT==='ot'?38:65,last='';
      for(var i=lo;i<=hi;i++){var ct=cat(i);if(ct[2]!==last){if(last)h+='</div>';h+='<p class="grp">'+ct[2]+'</p><div class="bks">';last=ct[2];}
        h+='<button type="button" class="bk'+(i===S.b?' on':'')+'" data-bk="'+i+'" style="--c:var('+ct[3]+')"><b>'+esc(ab(i))+'</b><small>'+esc(BK[i].n)+'</small></button>';}
      h+='</div>';
    }else{
      h+='<button type="button" class="back2" data-bk="-1">‹ 全部书卷</button><p class="grp">'+esc(BK[pickB].n)+' · 共 '+BK[pickB].nc+' 章</p><div class="chs">';
      for(var c=1;c<=BK[pickB].nc;c++)h+='<button type="button" data-ch="'+c+'"'+(pickB===S.b&&c===S.c?' class="on"':'')+'>'+c+'</button>';
      h+='</div>';
    }
    $('#pickbd').innerHTML=h;
    document.querySelectorAll('#pick [data-t]').forEach(function(b){b.setAttribute('aria-pressed',b.dataset.t===pickT?'true':'false');});
  }
  $('[data-pick]').addEventListener('click',function(){pickT=S.b<39?'ot':'nt';pickB=-1;drawPick();open('#pick');var on=$('#pick .bk.on');if(on)on.scrollIntoView({block:'center'});});
  $('#pick').addEventListener('click',function(e){
    var t=e.target.closest('[data-t]');if(t){pickT=t.dataset.t;pickB=-1;drawPick();return;}
    var b=e.target.closest('[data-bk]');if(b){pickB=+b.dataset.bk;if(pickB>=0&&BK[pickB].nc===1){close();go(pickB,1);return;}drawPick();$('#pickbd').scrollTop=0;return;}
    var c=e.target.closest('[data-ch]');if(c){close();go(pickB,+c.dataset.ch);}
  });

  /* ---------- 搜索 ---------- */
  var WORDS=null,ALL=null,KALL=null;
  function openFind(){open('#find');var q=$('#q');q.value='';showRes('');setTimeout(function(){q.focus();},60);}
  $('[data-search]').addEventListener('click',openFind);
  var qt;
  $('#q').addEventListener('input',function(){clearTimeout(qt);var v=this.value;qt=setTimeout(function(){showRes(v);},120);});
  $('#q').addEventListener('keydown',function(e){if(e.key==='Enter'){var f=$('#res .rs');if(f)f.click();}});
  var HAN=/[一-鿿]/;
  // 常见的异体字、不同写法：搜“借”也能找到和合本的“藉”，搜“祂”也能找到“他”
  var VAR={'借':'藉','祂':'他','妳':'你','著':'着','於':'于','裏':'里','裡':'里'};
  function norm(s){return s.replace(/[借祂妳著於裏裡]/g,function(c){return VAR[c];});}
  function bookScore(q,i){
    var b=BK[i],ql=q.toLowerCase().replace(/\s+/g,'');
    if(!ql)return 0;
    if(b.n===q||b.ab.indexOf(q)>=0)return 100;
    if(HAN.test(q))return b.n.indexOf(q)===0?90:b.n.indexOf(q)>0?60:0;
    var en=b.en.toLowerCase().replace(/\s+/g,''),code=b.code.toLowerCase();
    if(ql===code||ql===en)return 98;
    if(b.ini.indexOf(ql)===0)return 85+Math.min(ql.length,4);
    if(b.py.indexOf(ql)===0)return 84;
    if(ql.length>=2&&en.indexOf(ql)===0)return 80;
    if(ql.length>=2&&code.indexOf(ql)===0)return 79;
    return 0;
  }
  function books(q){var r=[];for(var i=0;i<66;i++){var s=bookScore(q,i);if(s)r.push([s,i]);}r.sort(function(a,b){return b[0]-a[0]||a[1]-b[1];});return r.map(function(x){return x[1];});}
  function parseRef(q){   // 来11:1、来 11 1、希伯来书11章1节、xbl11:1、Heb 11:1、1co13
    var m=/^\s*((?:[1-3]\s*)?[A-Za-z]+|[一-鿿]+?)\s*(\d+)(?:\s*(?:章|[:：.,，\s])\s*(\d+)?)?\s*节?\s*(?:[-–—~]\s*\d+)?\s*$/.exec(q);
    if(!m)return null;
    var bs=books(m[1].replace(/\s+/g,''));if(!bs.length)return null;
    var b=bs[0],c=+m[2],v=m[3]?+m[3]:0;
    if(BK[b].nc===1&&!m[3]&&c>1){v=c;c=1;}   // 犹大书 5 → 1:5
    if(c<1||c>BK[b].nc)return null;
    return {b:b,c:c,v:v};
  }
  function wordsFor(q){
    if(!WORDS)return [];
    var r=[],ql=q.toLowerCase(),han=HAN.test(q),nq=norm(q);
    for(var i=0;i<WORDS.length&&r.length<24;i++){var w=WORDS[i];
      if(han?(w[0].indexOf(nq)>=0&&w[0]!==nq):(w[1].indexOf(ql)===0||ql.length>=3&&w[2].indexOf(ql)===0))r.push(w);}
    if(han){r.sort(function(a,b){return (b[0].indexOf(nq)===0)-(a[0].indexOf(nq)===0)||b[3]-a[3];});}
    else r.sort(function(a,b){return (b[1]===ql)-(a[1]===ql)||b[3]-a[3];});
    return r.slice(0,16);
  }
  function recent(){try{return JSON.parse(get('bsrch')||'[]');}catch(e){return [];}}
  function remember(q){q=q.trim();if(!q)return;var r=recent().filter(function(x){return x!==q;});r.unshift(q);set('bsrch',JSON.stringify(r.slice(0,8)));}
  var lastQ='';
  function showRes(q){
    lastQ=q;q=q.trim();var h='',R=$('#res');
    if(!q){
      var rc=recent();
      h='<p class="tip">可以搜：书卷（<b>xbl</b>、希伯、heb）· 经文出处（<b>来11:1</b>、希伯来书11章、Heb 11:1）· 人名地名和词语（<b>xbl</b> → 希伯仑、希伯来人）· 经文里的字句（<b>信心</b>、<b>恩典</b>）· 英文（<b>faith</b>）</p>';
      if(rc.length)h+='<p class="grp">最近搜过</p><div class="chips recent">'+rc.map(function(x){return '<button type="button" class="chip" data-q="'+esc(x)+'">'+esc(x)+'</button>';}).join('')+'</div>';
      R.innerHTML=h;return;
    }
    var ref=parseRef(q);
    if(ref)h+='<button type="button" class="rs go" data-ref="'+ref.b+'.'+ref.c+'.'+ref.v+'"><b>'+esc(BK[ref.b].n)+' '+ref.c+(ref.v?':'+ref.v:'')+'</b><small>直接打开</small></button>';
    var bs=books(q);
    if(bs.length&&!ref){h+='<p class="grp">书卷</p>';bs.slice(0,6).forEach(function(i){h+='<button type="button" class="rs" data-ref="'+i+'.1.0"><b>'+esc(BK[i].n)+'</b><small>'+esc(ab(i))+' · '+esc(BK[i].en)+' · 共 '+BK[i].nc+' 章</small></button>';});}
    if(!ref){
      var ws=wordsFor(q);
      if(ws.length)h+='<p class="grp">人名、地名和词语</p><div class="chips">'+ws.map(function(w){return '<button type="button" class="chip" data-q="'+esc(w[0])+'">'+esc(w[0])+'<i>'+w[3]+'</i></button>';}).join('')+'</div>';
      if(HAN.test(q))h+='<div id="full"><p class="grp">经文</p><p class="tip">正在查找……</p></div>';
      else if(q.length>=3&&/[aeiouy]/i.test(q)&&!bs.length&&!ws.length)h+='<button type="button" class="more" data-kjv="'+esc(q)+'">在 KJV 英文经文里搜“'+esc(q)+'”</button>';
    }
    if(!h)h='<p class="tip">没有找到。可以换个写法，例如书卷的拼音首字母（xbl）、简称（来）或经文里的字词。</p>';
    R.innerHTML=h;
    if(!ref&&HAN.test(q))fullText(q,'cuv');
  }
  function loadAll(kind){
    var fs=[];for(var b=0;b<66;b++)fs.push(load(files(b)[kind]));
    return Promise.all(fs);
  }
  var LIMIT=120;
  function fullText(q,kind,lim){
    var box=$('#full');if(!box)return;
    var have=kind==='cuv'?ALL:KALL;
    if(!have){box.querySelector('.tip').textContent='第一次搜索全文，要下载整本'+(kind==='cuv'?'和合本（约 1.2 MB）':' KJV（约 1.4 MB）')+'，以后就存在手机里……';
      loadAll(kind).then(function(a){if(kind==='cuv')ALL=a;else KALL=a;if(lastQ.trim()===q||kind==='kjv')fullText(q,kind,lim);});return;}
    var nq=kind==='cuv'?norm(q):q.toLowerCase(),hits=[],per={},re;
    for(var b=0;b<66;b++){var bk=have[b];for(var c=0;c<bk.length;c++){var ch=bk[c];for(var v=0;v<ch.length;v++){var t=ch[v];if(!t)continue;
      var tt=kind==='cuv'?norm(t):t.toLowerCase();if(tt.indexOf(nq)>=0){hits.push([b,c+1,v+1,t]);per[b]=(per[b]||0)+1;}}}}
    var h='<p class="grp">经文 · 共 '+hits.length+' 节</p>';
    if(!hits.length)h+='<p class="tip">经文里没有这个词。</p>';
    var bsum=Object.keys(per).map(Number).sort(function(a,b){return a-b;});
    if(bsum.length>1)h+='<div class="chips" style="margin-bottom:8px">'+bsum.map(function(b){return '<button type="button" class="chip" data-jb="'+b+'">'+esc(ab(b))+'<i>'+per[b]+'</i></button>';}).join('')+'</div>';
    var reS=q.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
    try{re=new RegExp(kind==='cuv'?reS.replace(/./g,function(ch){var k=Object.keys(VAR).filter(function(x){return VAR[x]===ch||x===ch;});return k.length?'['+ch+k.join('')+']':ch;}):reS,'gi');}catch(e){re=null;}
    hits.slice(0,lim||LIMIT).forEach(function(x){
      var s=esc(x[3]);if(re)s=s.replace(re,function(m){return '<mark>'+m+'</mark>';});
      h+='<button type="button" class="hit" data-ref="'+x[0]+'.'+x[1]+'.'+x[2]+'" data-b="'+x[0]+'"><em>'+esc(ab(x[0]))+x[1]+':'+x[2]+'</em>'+s+'</button>';});
    if(hits.length>(lim||LIMIT))h+='<button type="button" class="more" data-moreq="'+esc(q)+'" data-kind="'+kind+'" data-lim="'+((lim||LIMIT)+300)+'">再显示 300 节（还有 '+(hits.length-(lim||LIMIT))+' 节）</button>';
    box.innerHTML=h;
  }
  $('#res').addEventListener('click',function(e){
    var r=e.target.closest('[data-ref]');if(r){remember($('#q').value);var p=r.dataset.ref.split('.');close();go(+p[0],+p[1],+p[2]);return;}
    var q=e.target.closest('[data-q]');if(q){$('#q').value=q.dataset.q;showRes(q.dataset.q);return;}
    var k=e.target.closest('[data-kjv]');if(k){remember(k.dataset.kjv);$('#res').innerHTML='<div id="full"><p class="grp">KJV 经文</p><p class="tip">正在查找……</p></div>';fullText(k.dataset.kjv,'kjv');return;}
    var m=e.target.closest('[data-moreq]');if(m){fullText(m.dataset.moreq,m.dataset.kind,+m.dataset.lim);return;}
    var jb=e.target.closest('[data-jb]');if(jb){var el=$('#res .hit[data-b="'+jb.dataset.jb+'"]');if(el)el.scrollIntoView({block:'start'});else toast('这一卷的结果在后面，请点“再显示”');}
  });

  /* ---------- 手机上左右滑动换章 ---------- */
  var tx0=0,ty0=0,tt0=0;
  $('#main').addEventListener('touchstart',function(e){var t=e.touches[0];tx0=t.clientX;ty0=t.clientY;tt0=Date.now();},{passive:true});
  $('#main').addEventListener('touchend',function(e){var t=e.changedTouches[0],dx=t.clientX-tx0,dy=t.clientY-ty0;
    if(Date.now()-tt0<600&&Math.abs(dx)>80&&Math.abs(dy)<45&&!window.getSelection().toString()){var p=dx>0?prev(S.b,S.c):next(S.b,S.c);if(p)go(p[0],p[1]);}},{passive:true});

  /* ---------- 开始 ---------- */
  setFs();setMode(S.mode);
  fetch(BIBLE_INDEX).then(function(r){return r.json();}).then(function(ix){
    IX=ix;BK=ix.books.map(function(x){return {n:x[0],ab:x[1],en:x[2],code:x[3],ini:x[4],py:x[5],nc:x[6]};});
    var keep=Object.keys(ix.files).map(function(k){return ix.files[k];});setTimeout(function(){prune(keep);},8000);
    load(ix.files.words).then(function(w){WORDS=w;if(lastQ)showRes(lastQ);});
    var r=readHash();if(r)render(r.b,r.c,r.v);else go(S.b,S.c,0,false);
  },function(){$('#main').innerHTML='<p class="load">打开失败，请检查网络后重试。</p>';});
})();
