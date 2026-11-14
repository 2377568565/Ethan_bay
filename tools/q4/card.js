/* ---------- 分享图片（卡片）：网站和问题彩蛋、健康的专题页共用（2026-10-30 从 app.js 搬出来） ----------
   window.Q4Card(card) 画一张图，放在弹出的面板里：手机上长按图片保存或发送，电脑上点“保存图片”。
   card.kind：
     verse   经文（文字 text、出处 ref）
     article 问题彩蛋文章（title、sub、text）
     answer  提问区管理员回答（q、a）
     quote   选中的一段文字（text、出处 src、栏目 col：lesson / bible / qa / health）——按字数自动选字号、对齐和图片高度
     column  栏目海报（col：health / qa；items：最新几篇 [{no,q,sub}]；total 共几篇）
   card.qr：二维码（网页里 .sh-qrs svg[data-for=…] 的 id；专题页用 .tsh-qr 里的那个）；card.qrText：二维码旁边的话。
   card.copy：附带一段可以复制的文字（栏目分享：介绍 + 最新 3 篇 + 单独一段链接）；card.onCopy：复制成功后调用。 */
(function(){
  if(window.Q4Card)return;
  var cv=document.createElement('canvas');if(!cv.getContext||!cv.toDataURL)return;
  var W=1080,PAD=120;
  var root=getComputedStyle(document.documentElement);
  var SERIF='"LessonSerif",'+((root.getPropertyValue('--serif')||'').trim()||'')+',"Noto Serif SC","Source Han Serif SC","Songti SC","STSong","SimSun",serif';
  SERIF=SERIF.replace(/,,+/g,',');
  var SANS=getComputedStyle(document.body).fontFamily||'sans-serif';
  var mobile=/Android|iPhone|iPad|iPod|Mobile|HarmonyOS|OpenHarmony/i.test(navigator.userAgent);
  function el(tag,cls,html){var e=document.createElement(tag);if(cls)e.className=cls;if(html!=null)e.innerHTML=html;return e;}
  function clean(t){return String(t||'').replace(/[ \t\r\f\v]+/g,' ').replace(/\s*\n\s*/g,'\n').replace(/\s*([，。、；：！？”’）》])\s*/g,'$1').trim();}
  function copy(t){
    if(window.q4copy)return q4copy(t);
    if(navigator.clipboard&&window.isSecureContext)return navigator.clipboard.writeText(t).then(function(){return true;},legacy);
    return Promise.resolve(legacy());
    function legacy(){var ta=document.createElement('textarea');ta.value=t;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();
      var ok=false;try{ok=document.execCommand('copy');}catch(e){}ta.remove();return ok;}
  }

  /* ---- 面板（自带样式：网站和专题页都能用；颜色用页面的变量，夜间模式跟着变） ---- */
  var st=el('style');st.textContent=
    '.q4c{position:fixed;inset:0;z-index:2147483000;display:flex;align-items:flex-end;justify-content:center}.q4c[hidden]{display:none}'+
    '.q4c-bg{position:absolute;inset:0;background:rgba(8,12,20,.5);opacity:0;transition:opacity .25s}.q4c.open .q4c-bg{opacity:1}'+
    '.q4c-card{position:relative;width:100%;max-width:460px;max-height:92vh;max-height:92dvh;overflow-y:auto;overscroll-behavior:contain;box-sizing:border-box;'+
      'padding:18px 18px 16px;padding-bottom:calc(16px + env(safe-area-inset-bottom,0px));border-radius:22px 22px 0 0;background:var(--surface,#fff);color:var(--ink,#222);'+
      'border:1px solid var(--rule,#ddd);border-bottom:0;transform:translateY(100%);transition:transform .32s cubic-bezier(.2,.8,.2,1);font-family:'+SANS+'}'+
    '.q4c.open .q4c-card{transform:none}'+
    '@media (min-width:640px){.q4c{align-items:center}.q4c-card{border-radius:22px;border-bottom:1px solid var(--rule,#ddd);transform:translateY(24px);opacity:0;transition:transform .3s,opacity .25s}.q4c.open .q4c-card{opacity:1}}'+
    '.q4c-x{position:absolute;top:10px;right:10px;width:36px;height:36px;border:0;border-radius:50%;background:transparent;color:var(--muted,#888);font:400 26px/1 sans-serif;cursor:pointer}'+
    '.q4c h3{margin:2px 40px 4px 2px;font-family:'+SERIF+';font-weight:900;font-size:1.15rem}'+
    '.q4c-step{margin:10px 2px 6px;font-size:.84rem;font-weight:700;color:var(--ink,#222)}.q4c-step i{display:inline-grid;place-items:center;width:20px;height:20px;margin-right:6px;border-radius:50%;background:var(--gold,#9A742C);color:#fff;font-style:normal;font-size:.72rem}'+
    '.q4c-tip{margin:0 2px 8px;font-size:.8rem;line-height:1.6;color:var(--muted,#888)}'+
    '.q4c-box{display:grid;place-items:center;min-height:200px;border-radius:14px;background:var(--paper,#f6f1e6);overflow:hidden}'+
    '.q4c-box img{display:block;max-width:100%;width:auto;height:auto;max-height:min(560px,52vh);max-height:min(560px,52dvh);-webkit-touch-callout:default;user-select:auto}.q4c-box img[hidden],.q4c [hidden]{display:none!important}'+
    '.q4c-wait{margin:0;font-size:.86rem;color:var(--muted,#888)}'+
    '.q4c-txt{margin:0 0 10px;padding:12px 14px;max-height:220px;overflow:auto;white-space:pre-wrap;word-break:break-word;border-radius:12px;border:1px dashed var(--rule,#ddd);background:var(--paper,#f6f1e6);font:400 .84rem/1.7 '+SANS+';color:var(--ink-2,#444)}'+
    '.q4c-btns{position:sticky;bottom:calc(-16px - env(safe-area-inset-bottom,0px));display:flex;gap:10px;margin:12px -18px 0;padding:10px 18px calc(16px + env(safe-area-inset-bottom,0px));background:var(--surface,#fff)}.q4c-btns>*{flex:1;display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:0 14px;border-radius:14px;border:1px solid var(--rule,#ddd);'+
      'background:var(--paper,#f6f1e6);color:var(--ink,#222);font:600 .92rem/1 '+SANS+';text-decoration:none;cursor:pointer;box-sizing:border-box}'+
    '.q4c-btns .ok{border-color:transparent;color:#1A2132;background:linear-gradient(180deg,#F0D9A0,#D3B06A)}'+
    '.q4c-done{min-height:1.2em;margin:8px 2px 0;font-size:.82rem;color:var(--ok,#2F7D5B)}';
  document.head.appendChild(st);
  var SH=el('div','q4c');SH.setAttribute('role','dialog');SH.setAttribute('aria-modal','true');SH.setAttribute('aria-label','分享图片');SH.hidden=true;
  SH.innerHTML='<div class="q4c-bg" data-close></div><div class="q4c-card"><button type="button" class="q4c-x" data-close aria-label="关闭">×</button>'+
    '<h3>分享图片</h3><p class="q4c-step q4c-s1" hidden><i>1</i>发图片</p><p class="q4c-tip"></p>'+
    '<div class="q4c-box"><p class="q4c-wait">正在生成图片……</p><img alt="分享图片" hidden></div>'+
    '<div class="q4c-cp" hidden><p class="q4c-step"><i>2</i>再发一段文字（点链接就能打开）</p><pre class="q4c-txt"></pre></div>'+
    '<p class="q4c-done" aria-live="polite"></p>'+
    '<div class="q4c-btns"><button type="button" class="ok q4c-cb" hidden>复制文字</button><a class="q4c-dl" download="预言的恩赐.jpg" hidden>保存图片</a><button type="button" data-close>关闭</button></div></div>';
  function mount(){if(!SH.parentNode)document.body.appendChild(SH);}
  if(document.body)mount();else document.addEventListener('DOMContentLoaded',mount);
  var cur=null;
  SH.addEventListener('click',function(e){
    if(e.target.closest('[data-close]')){close();return;}
    if(e.target.closest('.q4c-cb')&&cur&&cur.copy){var c=cur;copy(c.copy).then(function(ok){
      SH.querySelector('.q4c-done').textContent=ok===false?'复制没有成功，请长按上面的文字手动复制':'✓ 文字已复制，粘贴到微信群里，和图片一起发';if(ok!==false&&c.onCopy)c.onCopy();});}
  });
  SH.addEventListener('keydown',function(e){if(e.key==='Escape')close();});
  function open(card){
    mount();cur=card;var hasCp=!!card.copy;
    SH.querySelector('h3').textContent=card.head||'分享图片';
    SH.querySelector('img').hidden=true;SH.querySelector('.q4c-wait').hidden=false;SH.querySelector('.q4c-wait').textContent='正在生成图片……';SH.querySelector('.q4c-dl').hidden=true;
    SH.querySelector('.q4c-s1').hidden=!hasCp;SH.querySelector('.q4c-cp').hidden=!hasCp;SH.querySelector('.q4c-cb').hidden=!hasCp;
    SH.querySelector('.q4c-txt').textContent=card.copy||'';SH.querySelector('.q4c-done').textContent='';
    SH.querySelector('.q4c-tip').textContent=mobile?'图片生成后，长按图片就可以保存，或直接发送给朋友、发到群里。':'图片生成后，点“保存图片”下载到电脑，再发到微信。';
    SH.hidden=false;void SH.offsetWidth;SH.classList.add('open');document.documentElement.classList.add('sheetopen');
  }
  function close(){SH.classList.remove('open');document.documentElement.classList.remove('sheetopen');setTimeout(function(){SH.hidden=true;},260);}

  /* ---- 画布工具 ---- */
  function qrImg(id){
    var svg=(id&&document.querySelector('.sh-qrs svg[data-for="'+id+'"]'))||document.querySelector('.tsh-qr svg')||document.querySelector('.sh-qrs svg[data-for="home"]');
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
  function cut(lines,n,ctx,maxW){var c=lines.slice(0,n),t=c[n-1].replace(/[，。、；：！？]?$/,'').slice(0,-1);while(ctx&&t.length>1&&ctx.measureText(t+'……').width>maxW)t=t.slice(0,-1);c[n-1]=t+'……';return c;}
  function fit(ctx,text,font,size,min,maxW,maxLines,bal){   // 字太多就缩小字号；再放不下就截断加省略号
    for(var s=size;s>=min;s-=2){ctx.font=font(s);var ls=wrap(ctx,text,maxW);if(ls.length<=maxLines)return {s:s,lines:bal?balance(ctx,text,ls,maxW):ls};}
    ctx.font=font(min);return {s:min,lines:cut(wrap(ctx,text,maxW),maxLines,ctx,maxW)};
  }
  function rrect(ctx,x,y,w,h,r){ctx.beginPath();ctx.moveTo(x+r,y);ctx.arcTo(x+w,y,x+w,y+h,r);ctx.arcTo(x+w,y+h,x,y+h,r);ctx.arcTo(x,y+h,x,y,r);ctx.arcTo(x,y,x+w,y,r);ctx.closePath();}
  function block(ctx,lines,size,lh,x,y,align,color,font){ctx.textAlign=align;ctx.fillStyle=color;ctx.font=font;lines.forEach(function(l,i){ctx.fillText(l,x,y+i*size*lh);});return y+lines.length*size*lh;}
  // 每个栏目一种主色：学课、圣经、问题彩蛋用金和酒红；健康用绿
  var PAL={lesson:{a:'#7A2233',g:'#B98E35',name:'安息日学 · 学课'},bible:{a:'#7A2233',g:'#B98E35',name:'圣经 · 和合本'},
    qa:{a:'#7A2233',g:'#B98E35',name:'问题彩蛋 · 研经问答'},health:{a:'#1E7A5F',g:'#3E9C7C',name:'健康栏目'}};
  function frame(ctx,H,eyebrow,p){
    p=p||PAL.lesson;
    var g=ctx.createLinearGradient(0,0,0,H);g.addColorStop(0,'#FCF7EB');g.addColorStop(1,'#F2E3C3');ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
    var gl=ctx.createRadialGradient(W/2,180,20,W/2,180,620);gl.addColorStop(0,'rgba(255,236,170,.55)');gl.addColorStop(1,'rgba(255,236,170,0)');ctx.fillStyle=gl;ctx.fillRect(0,0,W,H);
    ctx.strokeStyle='#C9A55A';ctx.lineWidth=3;rrect(ctx,44,44,W-88,H-88,30);ctx.stroke();
    ctx.strokeStyle='rgba(201,165,90,.45)';ctx.lineWidth=1.5;rrect(ctx,58,58,W-116,H-116,24);ctx.stroke();
    ctx.fillStyle=p.g;ctx.textAlign='center';ctx.textBaseline='alphabetic';ctx.font='600 30px '+SANS;ctx.fillText('✦  '+eyebrow+'  ✦',W/2,150);
  }
  function footer(ctx,y,qr,line1,line2,p){
    p=p||PAL.lesson;
    ctx.strokeStyle='rgba(122,34,51,.22)';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(PAD,y);ctx.lineTo(W-PAD,y);ctx.stroke();
    var q=200,qx=PAD,qy=y+44;ctx.fillStyle='#fff';rrect(ctx,qx-10,qy-10,q+20,q+20,16);ctx.fill();
    if(qr)ctx.drawImage(qr,qx,qy,q,q);
    ctx.textAlign='left';ctx.fillStyle=p.a;ctx.font='700 38px '+SANS;ctx.fillText(line1,qx+q+50,qy+60);
    ctx.fillStyle='#5A4A36';ctx.font='400 28px '+SANS;ctx.fillText(line2,qx+q+50,qy+112);
    ctx.fillStyle='#9A8A70';ctx.font='400 24px '+SANS;ctx.fillText('整理制作 · Ethan（HangZhou_XG）',qx+q+50,qy+170);
  }

  /* ---- 原来的三种图（1080×1440） ---- */
  function drawVerse(ctx,c){
    frame(ctx,1440,'预言的恩赐 · 经文');
    ctx.fillStyle='rgba(185,142,53,.3)';ctx.font='900 200px '+SERIF;ctx.textAlign='left';ctx.fillText('“',PAD-36,350);
    var txt=clean(c.text).replace(/\n/g,'').replace(/^“|”$/g,''),lh=1.7,f=null;
    for(var s=66;s>=34;s-=2){ctx.font='600 '+s+'px '+SERIF;var ls=wrap(ctx,txt,W-2*PAD);if(ls.length*s*lh<=620){f={s:s,lines:ls};break;}}   // 经文区：360–980，下面留给出处
    if(!f)f=fit(ctx,txt,function(s){return '600 '+s+'px '+SERIF;},34,34,W-2*PAD,Math.floor(620/(34*lh)));
    var h=f.lines.length*f.s*lh,top=360+f.s+Math.max(0,(620-h)/2);
    var end=block(ctx,f.lines,f.s,lh,PAD,top,'left','#2B2118','600 '+f.s+'px '+SERIF);
    ctx.textAlign='right';ctx.fillStyle='#7A2233';ctx.font='600 36px '+SANS;ctx.fillText('—— '+c.ref,W-PAD,Math.min(end-f.s*lh+f.s+70,1070));
    return 1120;
  }
  function drawArticle(ctx,c){
    frame(ctx,1440,'问题彩蛋 · 研经问答');
    var t=fit(ctx,c.title.split('\n').map(clean).filter(Boolean).join('\n'),function(s){return '900 '+s+'px '+SERIF;},84,56,W-2*PAD,3,true);
    var y=block(ctx,t.lines,t.s,1.35,W/2,300,'center','#2B2118','900 '+t.s+'px '+SERIF);
    if(c.sub){ctx.font='500 32px '+SANS;var sl=wrap(ctx,clean(c.sub),W-2*PAD).slice(0,2);y=block(ctx,sl,32,1.6,W/2,y+30,'center','#7A2233','500 32px '+SANS);}
    ctx.strokeStyle='#C9A55A';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(W/2-60,y+30);ctx.lineTo(W/2+60,y+30);ctx.stroke();
    var b=fit(ctx,clean(c.text).replace(/\n/g,''),function(s){return '400 '+s+'px '+SERIF;},42,34,W-2*PAD,Math.max(4,Math.floor((1060-(y+90))/(42*1.75))));
    block(ctx,b.lines,b.s,1.75,PAD,y+100,'left','#3A2E22','400 '+b.s+'px '+SERIF);
    return 1120;
  }
  function drawAnswer(ctx,c){
    frame(ctx,1440,'提问区 · 管理员回答');
    ctx.textAlign='left';ctx.fillStyle='#7A2233';ctx.font='900 44px '+SERIF;ctx.fillText('问',PAD,290);
    var q=fit(ctx,clean(c.q),function(s){return '700 '+s+'px '+SERIF;},50,38,W-2*PAD-80,5);
    var y=block(ctx,q.lines,q.s,1.6,PAD+80,290,'left','#2B2118','700 '+q.s+'px '+SERIF);
    y=Math.max(y+40,420);ctx.fillStyle='#B98E35';ctx.font='900 44px '+SERIF;ctx.fillText('答',PAD,y+20);
    var a=fit(ctx,clean(c.a),function(s){return '400 '+s+'px '+SERIF;},42,32,W-2*PAD-80,Math.max(4,Math.floor((1070-y)/(42*1.7))));
    block(ctx,a.lines,a.s,1.7,PAD+80,y+20,'left','#3A2E22','400 '+a.s+'px '+SERIF);
    return 1120;
  }

  /* ---- 选中的一段文字（2026-10-30 用户要的）：按字数自动排版 ----
     很短（一句话）：大字居中，像一句金句；中等：大字靠左；长：字号逐步变小、图片变高；太长截断加省略号。 */
  function quoteLayout(ctx,txt){
    var n=txt.replace(/\s/g,'').length,maxW=W-2*PAD;
    var plan=n<=26?{s:76,min:64,lh:1.55,al:'center',w:'700'}:n<=70?{s:60,min:50,lh:1.62,al:'left',w:'600'}:n<=160?{s:48,min:42,lh:1.7,al:'left',w:'500'}:{s:42,min:34,lh:1.75,al:'left',w:'400'};
    var maxH=1920-220-40-330-40-120-150;   // 图最高 1920：上面题头和引号、下面出处和二维码
    for(var s=plan.s;s>=plan.min-8;s-=2){ctx.font=plan.w+' '+s+'px '+SERIF;var ls=wrap(ctx,txt,maxW);
      if(plan.al==='center')ls=balance(ctx,txt,ls,maxW);
      if(ls.length*s*plan.lh<=maxH)return {s:s,lines:ls,lh:plan.lh,al:plan.al,w:plan.w};}
    var s2=plan.min-8;ctx.font=plan.w+' '+s2+'px '+SERIF;
    return {s:s2,lines:cut(wrap(ctx,txt,maxW),Math.floor(maxH/(s2*plan.lh)),ctx,maxW),lh:plan.lh,al:plan.al,w:plan.w};
  }
  // 内容块从上到下：引号（120）、正文、分隔线和出处；整块在题头和二维码之间上下居中
  function quoteBlock(ctx,c,L){
    var sl=[];if(c.src){ctx.font='600 32px '+SANS;sl=wrap(ctx,'—— '+clean(c.src).replace(/\n/g,' '),W-2*PAD).slice(0,2);}
    var body=L.lines.length*L.s*L.lh;return {sl:sl,body:body,h:120+body+(sl.length?40+50+(sl.length-1)*48+16:20)};
  }
  function drawQuote(ctx,c,H,L,B){
    var p=PAL[c.col]||PAL.lesson,cx=L.al==='center'?W/2:PAD;
    frame(ctx,H,'预言的恩赐 · '+p.name,p);
    var top0=220,avail=H-330-40-top0,y0=top0+Math.max(0,(avail-B.h)/2);
    ctx.fillStyle=p.g;ctx.globalAlpha=.28;ctx.font='900 200px '+SERIF;ctx.textAlign=L.al==='center'?'center':'left';ctx.fillText('“',L.al==='center'?W/2:PAD-24,y0+150);ctx.globalAlpha=1;
    var end=block(ctx,L.lines,L.s,L.lh,cx,y0+120+L.s*0.95,L.al,'#2B2118',L.w+' '+L.s+'px '+SERIF);
    var ty=y0+120+B.body;
    if(B.sl.length){
      ctx.strokeStyle=p.g;ctx.lineWidth=3;ctx.beginPath();
      if(L.al==='center'){ctx.moveTo(W/2-50,ty+40);ctx.lineTo(W/2+50,ty+40);}else{ctx.moveTo(PAD,ty+40);ctx.lineTo(PAD+90,ty+40);}ctx.stroke();
      block(ctx,B.sl,32,1.5,cx,ty+40+60,L.al,p.a,'600 32px '+SANS);
    }
    return H-330;
  }

  /* ---- 栏目海报（2026-10-30 用户要的，健康和问题彩蛋）：1080×1920，适合手机全屏看 ----
     上：黎明的天空和栏目名；中：最新 7 篇（编号 + 题目，放得下就加一行副题）；下：二维码。 */
  var COLS={health:{name:'健康',k:'HEALTH · 健康栏目',tag:['常见健康问题，一篇讲透','原理讲清楚 · 研究都核对过 · 落到每天能做的事'],a:'#1E7A5F',g:'#3E9C7C',soft:'rgba(62,156,124,.12)',
      qr1:'长按识别二维码',qr2:'打开健康栏目，读全部文章'},
    qa:{name:'问题彩蛋',k:'Q & A · 研经问答',tag:['信徒和慕道朋友常问的问题','以经解经 · 资料详实 · 各方说法客观摆出来'],a:'#7A2233',g:'#B98E35',soft:'rgba(185,142,53,.14)',
      qr1:'长按识别二维码',qr2:'打开问题彩蛋，读全部文章'}};
  function stars(ctx,n,h,seed){var s=seed||7;function r(){s=(s*9301+49297)%233280;return s/233280;}
    for(var i=0;i<n;i++){var x=r()*W,y=r()*h*.72,a=.25+r()*.6,z=r()<.12?3:1.6;ctx.fillStyle='rgba(255,246,220,'+a.toFixed(2)+')';ctx.fillRect(x,y,z,z);}}
  // 两行的标题：尽量在“：”“，”“？”后面换行（不在词中间断开）
  function punctSplit(ctx,t,ls,maxW){if(ls.length!==2||/……$/.test(ls[1]))return ls;var best=null;
    for(var i=1;i<t.length-1;i++){if(!/[：，？！；]/.test(t[i]))continue;var a=t.slice(0,i+1),b=t.slice(i+1);if(ctx.measureText(a).width<=maxW&&ctx.measureText(b).width<=maxW)best=[a,b];}
    return best||ls;}
  function drawColumn(ctx,c){
    var C=COLS[c.col]||COLS.qa,H=1920,HB=600;
    // 天空
    var g=ctx.createLinearGradient(0,0,0,HB);g.addColorStop(0,'#111A2E');g.addColorStop(.55,'#2B3354');g.addColorStop(.86,'#8C6A55');g.addColorStop(1,'#E8BE7C');
    ctx.fillStyle=g;ctx.fillRect(0,0,W,HB);stars(ctx,90,HB,c.col==='health'?11:5);
    var gl=ctx.createRadialGradient(W/2,HB+40,10,W/2,HB+40,560);gl.addColorStop(0,'rgba(255,226,160,.85)');gl.addColorStop(.4,'rgba(255,214,140,.25)');gl.addColorStop(1,'rgba(255,214,140,0)');ctx.fillStyle=gl;ctx.fillRect(0,0,W,HB);
    ctx.textAlign='center';ctx.fillStyle='#E6C98B';ctx.font='700 28px '+SANS;ctx.fillText('预言的恩赐 · 安息日学研读',W/2,120);
    ctx.fillStyle='rgba(230,201,139,.75)';ctx.font='600 24px '+SANS;ctx.fillText(C.k,W/2,166);
    ctx.fillStyle='#FFF8E8';ctx.font='900 '+(C.name.length>2?132:168)+'px '+SERIF;ctx.fillText(C.name,W/2,350);
    ctx.fillStyle='#FFF1D6';ctx.font='700 40px '+SERIF;ctx.fillText(C.tag[0],W/2,440);
    ctx.fillStyle='rgba(255,241,214,.85)';ctx.font='400 28px '+SANS;ctx.fillText(C.tag[1],W/2,494);
    // 纸
    var pg=ctx.createLinearGradient(0,HB,0,H);pg.addColorStop(0,'#FCF7EB');pg.addColorStop(1,'#F3E6CA');ctx.fillStyle=pg;ctx.fillRect(0,HB,W,H-HB);
    ctx.fillStyle='rgba(255,236,190,.9)';ctx.fillRect(0,HB,W,3);
    // 最新几篇
    var y0=HB+90,x0=88,xr=W-88;
    ctx.textAlign='left';ctx.fillStyle=C.a;ctx.font='800 40px '+SERIF;ctx.fillText('最新上架',x0,y0);
    ctx.textAlign='right';ctx.fillStyle='#8A7A60';ctx.font='500 28px '+SANS;ctx.fillText('共 '+c.total+' 篇 · 持续更新',xr,y0);
    var items=(c.items||[]).slice(0,7),top=y0+36,bottom=H-330-30,avail=bottom-top,n=items.length||1;
    var rowH=avail/n,tx=x0+104,tw=xr-tx;
    items.forEach(function(it,i){
      var ry=top+i*rowH;
      if(i){ctx.strokeStyle='rgba(122,90,40,.16)';ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(tx,ry);ctx.lineTo(xr,ry);ctx.stroke();}
      var tf=fit(ctx,clean(it.q),function(s){return '700 '+s+'px '+SERIF;},40,34,tw,2),lh=1.32;tf.lines=punctSplit(ctx,clean(it.q),tf.lines,tw);
      var th=tf.lines.length*tf.s*lh,showSub=it.sub&&tf.lines.length===1&&rowH>=th+52;
      var bodyH=th+(showSub?44:0),by=ry+(rowH-bodyH)/2;
      // 编号
      var cy=ry+rowH/2;ctx.fillStyle=C.soft;rrect(ctx,x0,cy-38,80,76,18);ctx.fill();
      ctx.textAlign='center';ctx.fillStyle=C.a;ctx.font='800 38px '+SERIF;ctx.fillText(String(it.no).length<2?'0'+it.no:String(it.no),x0+40,cy+13);
      if(i===0){ctx.fillStyle=C.g;rrect(ctx,x0+44,cy-50,52,28,14);ctx.fill();ctx.fillStyle='#fff';ctx.font='700 18px '+SANS;ctx.fillText('最新',x0+70,cy-30);}
      block(ctx,tf.lines,tf.s,lh,tx,by+tf.s*.95,'left','#2B2118','700 '+tf.s+'px '+SERIF);
      if(showSub){ctx.font='400 26px '+SANS;var sl=fit(ctx,clean(it.sub),function(s){return '400 '+s+'px '+SANS;},26,24,tw,1);block(ctx,sl.lines,sl.s,1.4,tx,by+th+34,'left','#7A6A52','400 '+sl.s+'px '+SANS);}
    });
    return H-330;
  }

  function make(card){
    open(card);
    var fonts=document.fonts&&document.fonts.load?Promise.all([document.fonts.load('600 48px LessonSerif'),document.fonts.load('900 48px LessonSerif')]).catch(function(){}):Promise.resolve();
    Promise.all([fonts,qrImg(card.qr)]).then(function(r){
      var H=1440,L=null,ctx=cv.getContext('2d');
      if(card.kind==='column')H=1920;
      var B=null;
      if(card.kind==='quote'){cv.width=W;cv.height=10;L=quoteLayout(ctx,clean(card.text));B=quoteBlock(ctx,card,L);
        H=Math.round(Math.min(1920,Math.max(1350,220+B.h+40+330+40)));}
      cv.width=W;cv.height=H;ctx=cv.getContext('2d');
      var fy=({verse:drawVerse,article:drawArticle,answer:drawAnswer,quote:function(x,c){return drawQuote(x,c,H,L,B);},column:drawColumn})[card.kind](ctx,card);
      var p=card.kind==='column'?COLS[card.col]||COLS.qa:PAL[card.col]||PAL.lesson;
      footer(ctx,fy,r[1],card.qr1||(card.kind==='column'?p.qr1:'长按识别二维码'),card.qrText||(card.kind==='column'?p.qr2:'阅读本季安息日学研读'),p);
      var url=cv.toDataURL('image/jpeg',0.92),img=SH.querySelector('img');
      img.src=url;img.hidden=false;SH.querySelector('.q4c-wait').hidden=true;
      var dl=SH.querySelector('.q4c-dl');dl.href=url;dl.hidden=mobile;
    }).catch(function(){SH.querySelector('.q4c-wait').textContent='图片没有生成成功，请再试一次。';});
  }
  window.Q4Card=make;
})();
