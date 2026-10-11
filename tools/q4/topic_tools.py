# 问题彩蛋专题网页的“分享”和“下载 PDF”（答题后下载）：history.py 的 doc(tools=...) 使用。
# 每个问题彩蛋都要有这两个按钮（整理者 2026-10-05 定下的规矩）。
# 用法：tools = topic_tools.build(id='qa3', title='基督教两千年家谱', page='history.html', pdf='研经问答03-基督教两千年家谱.pdf', quiz=QUIZ, ref=ref)
#   QUIZ = [dict(q='题目', o=['选项A', '选项B', '选项C'], a=正确选项序号, why='一句解释', ch='章id'), ...]   至少 5 题，每次随机抽 3 题，答对 2 题就能下载。
import html, json, os, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bible

ONLINE = 'https://2377568565.github.io/Ethan_bay/'
PDF_DIR = 'lessons/2026-Q4/qa/'
esc = html.escape

# 分享之后送的经文（和合本原文，生成时从圣经数据取）
GIFT = ['赛52:7', '箴11:25', '加6:9', '来10:24', '帖前5:11', '太5:16', '诗96:3', '箴15:23', '诗119:105', '林前15:58']

WXIC = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M9.2 4C5.2 4 2 6.7 2 10c0 1.9 1 3.6 2.7 4.7L4 17l2.6-1.4c.8.2 1.7.4 2.6.4h.5a5.6 5.6 0 0 1-.2-1.5C9.5 11.4 12.6 9 16.4 9h.4C16 6.1 12.9 4 9.2 4Zm-2.4 3.3a.9.9 0 1 1 0 1.8.9.9 0 0 1 0-1.8Zm4.8 0a.9.9 0 1 1 0 1.8.9.9 0 0 1 0-1.8ZM22 14.4c0-2.8-2.7-5-6-5s-6 2.2-6 5 2.7 5 6 5c.7 0 1.4-.1 2-.3l2.1 1.1-.6-1.9c1.5-.9 2.5-2.3 2.5-3.9Zm-8-.8a.8.8 0 1 1 0-1.6.8.8 0 0 1 0 1.6Zm4 0a.8.8 0 1 1 0-1.6.8.8 0 0 1 0 1.6Z" fill="currentColor"/></svg>'
LINKIC = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1 1M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1-1" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>'
SHAREIC = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5.5" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/>'
           '<circle cx="6" cy="12" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="18" cy="18.5" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/>'
           '<path d="M8.3 10.8 15.7 6.7M8.3 13.2l7.4 4.1" fill="none" stroke="currentColor" stroke-width="2"/></svg>')
DLIC = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11m0 0-4.5-4.5M12 15l4.5-4.5M5 19.5h14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def qr_svg(url):
    try:
        import qrcode
    except ImportError:            # 没装 qrcode（pip install qrcode）时，电脑上只给链接
        return ''
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2); q.add_data(url); q.make()
    m = q.get_matrix(); n = len(m)
    d = ''.join(f'M{x},{y}h1v1h-1z' for y in range(n) for x in range(n) if m[y][x])
    return f'<svg viewBox="0 0 {n} {n}" shape-rendering="crispEdges" role="img" aria-label="二维码"><rect width="{n}" height="{n}" fill="#fff"/><path d="{d}" fill="#111"/></svg>'


def gifts():
    out = []
    for r in GIFT:
        m = re.fullmatch(r'(\D+?)(\d+):(\d+)', r)
        b = bible.NAME2IDX[m.group(1)]
        t = bible.cuv(b, int(m.group(2)), int(m.group(3)))
        if t.count('“') != t.count('”'):        # 经文是一段话的开头或结尾时，引号不成对，去掉
            t = t.replace('“', '').replace('”', '')
        out.append([t, bible.BOOKS[b][1] + ' ' + m.group(2) + ':' + m.group(3)])
    return out


def pdf_url(pdf):
    return PDF_DIR + urllib.parse.quote(pdf)


def build(id, title, page, pdf, quiz, ref):
    """返回 doc() 要放进页面的几段 HTML：顶栏按钮、正文里的按钮行、弹出层和脚本。ref(章id) 给出“第 N 章”的链接文字。"""
    assert len(quiz) >= 5, '至少 5 题（每次随机抽 3 题）'
    for x in quiz:
        assert 0 <= x['a'] < len(x['o']) and x['ch'], x
    url = ONLINE + page
    qz = [dict(q=x['q'], o=x['o'], a=x['a'], why=x['why'], go=ref(x['ch'])) for x in quiz]
    cfg = dict(id=id, title=title, url=url, pdf=pdf_url(pdf), name=pdf)
    bar = (f'<button type="button" class="ib" data-tshare aria-label="分享">{SHAREIC}</button>'
           f'<button type="button" class="ib" data-tdl aria-label="下载 PDF">{DLIC}</button>')
    row = (f'<div class="tacts"><button type="button" class="tbtn" data-tshare>{SHAREIC}<span>分享这一篇</span></button>'
           f'<button type="button" class="tbtn solid" data-tdl>{DLIC}<span>下载 PDF</span></button></div>')
    qr = qr_svg(url)
    tail = f'''<div class="sheet" id="tshsheet" hidden><div class="sh-bg" data-close></div><div class="sh-card small" role="dialog" aria-modal="true" aria-labelledby="tsh-h">
<button type="button" class="sh-x" data-close aria-label="关闭">×</button><p class="tsh" id="tsh-h">分享这一篇</p><p class="tsh-t">“{esc(title)}”</p>
<div class="tsh-main"><button type="button" class="tile" data-twx>{WXIC}<span>微信分享</span></button><button type="button" class="tile" data-tcopy>{LINKIC}<span>复制链接</span></button><button type="button" class="tile" data-tsys hidden>{SHAREIC}<span>更多方式</span></button></div>
{f'<div class="tsh-qr" hidden>{qr}<p><b>用手机微信扫一扫</b>打开后点右上角 ··· 就能转发；也可以复制链接，粘贴到电脑版微信的聊天框。</p></div>' if qr else ''}
<p class="tsh-done" aria-live="polite"></p><button type="button" class="tsh-sent" data-tsent hidden>✓ 我已经分享好了</button><p class="tsh-url">{esc(url)}</p></div></div>
<div class="twg" id="twg" role="dialog" aria-modal="true" aria-label="微信转发提示" hidden><p class="twg-t">点右上角 <span>···</span><br>选择“转发给朋友”</p>
<div class="twg-box"><p>选好群或朋友、发送之后，回到这里点一下：</p><div class="twg-btns"><button type="button" class="ok" data-twdone>✓ 我已转发</button><button type="button" data-twno>先不转发</button></div></div></div>
<div class="sheet" id="tdlsheet" hidden><div class="sh-bg" data-close></div><div class="sh-card quiz" role="dialog" aria-modal="true" aria-labelledby="tdl-h">
<button type="button" class="sh-x" data-close aria-label="关闭">×</button><p class="tsh" id="tdl-h">下载 PDF 学习版</p>
<p class="qz-intro">先答 3 道小题，答对 2 道就可以下载。题目都来自这一页的内容。</p><ol class="qz"></ol>
<div class="qz-res" aria-live="polite"></div>
<div class="qz-btns"><button type="button" class="tbtn" data-qretry hidden>换 3 道题再答一次</button><a class="tbtn solid" data-qdl hidden href="{esc(cfg['pdf'])}" download="{esc(pdf)}">{DLIC}<span>下载 PDF</span></a></div>
<p class="qz-wx note2" hidden>微信里会先打开 PDF 预览：点右上角 ··· 选“用其他应用打开”或“在浏览器打开”，就能保存到手机。</p></div></div>
<div class="tgift" id="tgift" hidden><div class="sh-bg" data-gclose></div><div class="tg-card" role="dialog" aria-modal="true" aria-label="谢谢分享"><p class="tg-k">谢谢你的分享</p>
<p class="tg-m">一个小小的转发，也许正好是别人心里在找的答案。</p><blockquote class="tg-v"></blockquote><button type="button" class="tbtn solid" data-gclose>阿们，收下</button></div></div>
<script type="application/json" id="tcfg">{json.dumps(cfg, ensure_ascii=False)}</script>
<script type="application/json" id="tquiz">{json.dumps(qz, ensure_ascii=False)}</script>
<script type="application/json" id="tgifts">{json.dumps(gifts(), ensure_ascii=False)}</script>
<style>{CSS}</style>
<script>{JS}</script>'''
    return dict(bar=bar, row=row, tail=tail)


CSS = r'''
.tend{border-top:1px solid var(--rule);margin:36px 0 8px;padding:18px 0 0}
.tend p{color:var(--ink-2);font-size:.95rem;margin:0}
.ib{display:inline-grid;place-items:center;width:32px;height:32px;padding:0;border:1px solid var(--rule);border-radius:50%;background:var(--surface);color:var(--ink);cursor:pointer;flex:none}
.ib .ic{width:17px;height:17px}
.ic{width:18px;height:18px;flex:none}
.tacts{display:flex;gap:10px;flex-wrap:wrap;margin:14px 0 18px}
.tbtn{white-space:nowrap;display:inline-flex;align-items:center;justify-content:center;gap:6px;font:inherit;font-size:.92rem;font-weight:650;color:var(--ink);background:var(--surface);border:1px solid var(--rule);border-radius:999px;padding:9px 16px;cursor:pointer;text-decoration:none;flex:1 1 9em}
.tbtn.solid{background:var(--accent);border-color:var(--accent);color:#fff}
.tsh-t{color:var(--ink-2);margin:0 0 12px;font-weight:600}
.tsh-main{display:flex;gap:10px;margin:0 0 10px}
.tile{flex:1;display:flex;flex-direction:column;align-items:center;gap:6px;font:inherit;font-size:.86rem;color:var(--ink);background:var(--paper);border:1px solid var(--rule);border-radius:14px;padding:12px 4px;cursor:pointer}
.tile .ic{width:26px;height:26px}
.tile[data-twx] .ic{color:#07C160}
.tsh-qr{display:flex;gap:12px;align-items:center;margin:6px 0 8px;font-size:.84rem;color:var(--ink-2)}
.tsh-qr svg{width:120px;height:120px;flex:none;border-radius:8px}
.tsh-done{font-size:.9rem;color:var(--ink-2);margin:6px 0}
.tsh-sent{font:inherit;font-size:.9rem;width:100%;padding:9px;border-radius:12px;border:1px solid var(--accent);color:var(--accent);background:var(--accent-soft);cursor:pointer;margin:0 0 8px}
.tsh-url{font-size:.78rem;color:var(--muted);word-break:break-all;margin:4px 0 0;user-select:all;-webkit-user-select:all}
.twg{position:fixed;inset:0;z-index:60;background:rgba(10,12,18,.86);color:#fff;padding:calc(70px + env(safe-area-inset-top)) 24px 24px;text-align:center}
.twg-t{font-size:1.25rem;font-weight:700;line-height:1.6;margin:0 0 24px;text-align:right;padding-right:6px}
.twg-t span{letter-spacing:.1em}
.twg-t::before{content:"↗";display:block;font-size:2.6rem;line-height:1;color:#FCE7B0}
.twg-box{background:rgba(255,255,255,.1);border-radius:16px;padding:14px}
.twg-btns{display:flex;gap:10px;margin-top:10px}
.twg-btns button{flex:1;font:inherit;padding:10px;border-radius:12px;border:1px solid rgba(255,255,255,.4);background:none;color:#fff;cursor:pointer}
.twg-btns .ok{background:#07C160;border-color:#07C160;font-weight:700}
.sh-card.quiz{max-height:88vh}
.qz-intro{font-size:.9rem;color:var(--ink-2);margin:0 0 10px}
.qz{list-style:none;margin:0;padding:0;counter-reset:q}
.qz>li{counter-increment:q;border:1px solid var(--rule);border-radius:14px;padding:12px 12px 6px;margin:0 0 10px;background:var(--paper)}
.qq{font-weight:650;margin:0 0 8px}
.qq::before{content:counter(q) ". ";color:var(--accent)}
.qo{display:grid;gap:7px;margin:0 0 8px}
.qo button{font:inherit;font-size:.92rem;text-align:left;padding:9px 12px;border-radius:10px;border:1px solid var(--rule);background:var(--surface);color:var(--ink);cursor:pointer;line-height:1.5}
.qo button:disabled{cursor:default;opacity:1}
.qo button.ok{border-color:#2f8f57;background:color-mix(in srgb,#2f8f57 12%,var(--surface));color:var(--ink);font-weight:650}
.qo button.no{border-color:#cf4a43;background:color-mix(in srgb,#cf4a43 12%,var(--surface))}
.qo button.ok::after{content:" ✓";color:#2f8f57;font-weight:800}
.qo button.no::after{content:" ✗";color:#cf4a43;font-weight:800}
.qw{font-size:.86rem;color:var(--ink-2);margin:0 0 6px}
.qw b.y{color:#2f8f57}.qw b.n{color:#cf4a43}
.qz-res{font-weight:650;margin:4px 0 10px}
.qz-res.pass{color:#2f8f57}.qz-res.fail{color:#cf4a43}
.qz-btns{display:flex;gap:10px;flex-wrap:wrap}
.tgift{position:fixed;inset:0;z-index:55;display:grid;place-items:center;padding:20px}
.tg-card{position:relative;max-width:420px;width:100%;background:var(--surface);border-radius:20px;padding:22px 20px 18px;text-align:center;box-shadow:0 18px 50px rgba(0,0,0,.3)}
.tg-k{font-weight:800;font-size:1.15rem;color:var(--gold);margin:0 0 6px}
.tg-m{font-size:.92rem;color:var(--ink-2)}
.tg-v{margin:12px 0 16px;padding:12px 14px;background:var(--gold-soft);border-radius:14px;font-family:var(--serif);font-size:1.02rem;line-height:1.8}
.tg-v cite{display:block;font-family:var(--sans);font-style:normal;font-size:.82rem;color:var(--muted);margin-top:4px}
html.emb .bar{padding-top:8px}
/* 2026-10 新设计：和学课网站一致（米白纸色、墨蓝字、金色点缀；面板从底部升起） */
.prog i{background:linear-gradient(90deg,#C9A45C,var(--gold))}
.bar{background:color-mix(in srgb,var(--paper) 84%,transparent);-webkit-backdrop-filter:saturate(1.4) blur(14px);backdrop-filter:saturate(1.4) blur(14px)}
.bar .back{color:var(--ink);font-weight:500}
.bar .aa{font-family:var(--serif);font-weight:900}
.tbtn{transition:transform .18s cubic-bezier(.2,.8,.2,1),border-color .2s;box-shadow:0 1px 2px rgba(26,33,50,.04)}
.tbtn:active{transform:scale(.97)}
.tbtn .ic{color:var(--gold)}
.tbtn.solid{border-color:transparent;color:#1A2132;background:linear-gradient(180deg,#F0D9A0,#D3B06A);box-shadow:0 6px 18px -8px rgba(164,124,51,.65)}
.tbtn.solid .ic{color:inherit}
.tile{border-color:transparent;background:var(--band);border-radius:16px;font-weight:650}
.tile[data-twx]{background:#07C160;border-color:#07A355;color:#fff;box-shadow:0 8px 20px -10px rgba(7,160,85,.7)}
.tile[data-twx] .ic{color:#fff}
.tsh{font-family:var(--serif);font-weight:900}
.tsh-sent{border-color:color-mix(in srgb,var(--gold) 40%,transparent);color:var(--gold);background:var(--gold-soft)}
.sh-bg{background:rgba(8,12,20,.45)}
.sh-card{border-radius:24px 24px 0 0;border:1px solid var(--rule);border-bottom:0;padding-top:26px}
.sh-card::before{content:"";position:absolute;left:50%;top:8px;width:40px;height:5px;border-radius:3px;background:var(--muted);opacity:.3;transform:translateX(-50%)}
.sheet:not([hidden]) .sh-card{animation:shup .38s cubic-bezier(.2,.8,.2,1)}
@keyframes shup{from{transform:translateY(100%)}to{transform:none}}
@media (min-width:700px){.sh-card{border-radius:24px;border-bottom:1px solid var(--rule)}.sh-card::before{content:none}.sheet:not([hidden]) .sh-card{animation:shpop .3s cubic-bezier(.2,.8,.2,1)}}
@keyframes shpop{from{opacity:0;transform:translate(-50%,12px) scale(.97)}to{opacity:1;transform:translateX(-50%)}}
.sh-x{top:10px;right:12px;width:34px;height:34px;padding:0;border-radius:50%;background:var(--band);font-size:1.2rem}
.qq::before{color:var(--gold)}
.tg-card{border:1px solid var(--rule);border-radius:24px}
.fab-toc{background:#141B2A;color:#F3EBDA;border:1px solid rgba(233,214,163,.3)}
@media (prefers-reduced-motion:reduce){.sheet:not([hidden]) .sh-card{animation:none}}
@media print{.ib,.tacts,.sheet,.twg,.tgift,.howto,.toc-in .tsrc{display:none!important}
  :root{color-scheme:light}body{background:#fff}.bar,.fab-toc{display:none!important}
  .part{break-before:page;break-after:avoid}.ch h2{break-after:avoid}table,figure,.answer,blockquote{break-inside:avoid}
  a{color:inherit;text-decoration:none}.foot{padding-bottom:0}}
'''

JS = r'''
(function(){
  var de=document.documentElement,C=JSON.parse(document.getElementById('tcfg').textContent),Q=JSON.parse(document.getElementById('tquiz').textContent),
      G=JSON.parse(document.getElementById('tgifts').textContent);
  var SH=document.getElementById('tshsheet'),WG=document.getElementById('twg'),DL=document.getElementById('tdlsheet'),GF=document.getElementById('tgift');
  var UA=navigator.userAgent,inWx=/MicroMessenger/i.test(UA),mobile=/Android|iPhone|iPad|iPod|Mobile|HarmonyOS|OpenHarmony/i.test(UA);
  var emb=de.classList.contains('emb'),TOP=emb?window.top:window;
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);}catch(e){}}
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function open(s){s.hidden=false;de.classList.add('sheetopen');}
  function close(s){s.hidden=true;if(![SH,DL].some(function(x){return !x.hidden;}))de.classList.remove('sheetopen');}
  function copy(t){
    function legacy(){var a=document.createElement('textarea');a.value=t;a.setAttribute('readonly','');a.style.cssText='position:fixed;top:0;left:0;width:1px;height:1px;opacity:0';
      document.body.appendChild(a);a.focus();a.select();try{a.setSelectionRange(0,t.length);}catch(e){}var ok=false;try{ok=document.execCommand('copy');}catch(e){}document.body.removeChild(a);return ok;}
    if(navigator.clipboard&&window.isSecureContext)return navigator.clipboard.writeText(t).then(function(){return true;},function(){return legacy();});
    return Promise.resolve(legacy());
  }
  /* ---------- 分享 ---------- */
  var text='【问题彩蛋】'+C.title+'\n'+C.url,pending=false;
  function done(h,sent){SH.querySelector('.tsh-done').innerHTML=h;SH.querySelector('.tsh-sent').hidden=!sent;}
  function shOpen(){
    SH.querySelector('[data-tsys]').hidden=!(navigator.share&&!inWx);
    var qr=SH.querySelector('.tsh-qr');if(qr)qr.hidden=mobile;
    done('',false);open(SH);
  }
  function gift(){
    pending=false;close(SH);WG.hidden=true;
    var n=(+get('shares')||0)+1;set('shares',String(n));
    var v=G[Math.floor(Math.random()*G.length)];
    GF.querySelector('.tg-v').innerHTML=esc(v[0])+'<cite>'+esc(v[1])+'</cite>';
    setTimeout(function(){GF.hidden=false;},250);
  }
  document.addEventListener('click',function(e){
    var t=e.target;
    if(t.closest('[data-tshare]')){shOpen();return;}
    if(t.closest('[data-tdl]')){qOpen();return;}
    if(t.closest('[data-gclose]')){GF.hidden=true;return;}
    if(t.closest('[data-twdone]')){gift();return;}
    if(t.closest('[data-twno]')){pending=false;WG.hidden=true;return;}
    if(t.closest('[data-twx]')){
      if(inWx){pending=true;close(SH);WG.hidden=false;return;}
      copy(text).then(function(ok){
        if(mobile){pending=true;done(ok?'✓ 链接已复制，正在打开微信……<br>在聊天框里<b>长按 → 粘贴</b>，发送即可':'正在打开微信……请回来长按下面的链接复制',true);
          setTimeout(function(){try{TOP.location.href='weixin://';}catch(err){location.href='weixin://';}},450);}
        else done(ok?'✓ 链接已复制，粘贴到<b>电脑版微信</b>的聊天框发送即可；也可以用手机微信扫上面的二维码':'复制没有成功，请用手机微信扫上面的二维码',ok);
      });return;
    }
    if(t.closest('[data-tcopy]')){copy(text).then(function(ok){done(ok?'✓ 已复制，可以粘贴到微信群里了':'复制没有成功，请长按下面的链接手动复制',ok);});return;}
    if(t.closest('[data-tsys]')){navigator.share({title:C.title,text:'【问题彩蛋】'+C.title,url:C.url}).then(gift).catch(function(){});return;}
    if(t.closest('[data-tsent]')){gift();return;}
  });
  document.addEventListener('visibilitychange',function(){if(!document.hidden&&pending&&!SH.hidden)setTimeout(function(){done(SH.querySelector('.tsh-done').innerHTML,true);},200);});
  [SH,DL].forEach(function(s){s.addEventListener('click',function(e){if(e.target.closest('[data-close]'))close(s);});});
  /* ---------- 下载：先答 3 题，答对 2 题就能下载 ---------- */
  var OL=DL.querySelector('.qz'),RES=DL.querySelector('.qz-res'),RT=DL.querySelector('[data-qretry]'),DB=DL.querySelector('[data-qdl]'),WXN=DL.querySelector('.qz-wx'),
      KEY='quiz:'+C.id,cur=[],got=0,left=0,last=[];
  if(inWx){DB.removeAttribute('download');DB.target=emb?'_top':'_self';}
  function pick(){   // 随机抽 3 题，尽量不和上一次重复
    var idx=Q.map(function(_,i){return i;}).sort(function(){return Math.random()-.5;});
    idx.sort(function(a,b){return (last.indexOf(a)>=0)-(last.indexOf(b)>=0);});
    return idx.slice(0,3);
  }
  function ready(msg){RES.className='qz-res pass';RES.innerHTML=msg;DB.hidden=false;WXN.hidden=!inWx;}
  function qOpen(){
    if(get(KEY)==='1'&&!cur.length){OL.innerHTML='';RT.hidden=false;RT.textContent='再答一次题';ready('你已经答对过题目，可以直接下载。');open(DL);return;}
    if(!cur.length||!left)build();
    open(DL);
  }
  function build(){
    cur=pick();last=cur.slice();got=0;left=3;RES.className='qz-res';RES.textContent='';DB.hidden=true;RT.hidden=true;WXN.hidden=true;
    OL.innerHTML=cur.map(function(i,n){var x=Q[i];return '<li data-i="'+i+'"><p class="qq">'+esc(x.q)+'</p><div class="qo">'+
      x.o.map(function(o,j){return '<button type="button" data-o="'+j+'">'+'ABCD'[j]+'. '+esc(o)+'</button>';}).join('')+'</div><p class="qw" hidden></p></li>';}).join('');
    DL.querySelector('.sh-card').scrollTop=0;
  }
  OL.addEventListener('click',function(e){
    var b=e.target.closest('.qo button');if(!b)return;
    var li=b.closest('li'),x=Q[+li.dataset.i],j=+b.dataset.o,bs=li.querySelectorAll('.qo button');
    if(li.dataset.done)return;li.dataset.done='1';left--;
    bs.forEach(function(y){y.disabled=true;});
    bs[x.a].classList.add('ok');
    var ok=j===x.a,w=li.querySelector('.qw');
    if(ok)got++;else b.classList.add('no');
    w.innerHTML=(ok?'<b class="y">答对了！</b>':'<b class="n">答错了。</b>正确答案是 '+'ABCD'[x.a]+'。')+esc(x.why)+' '+x.go;
    w.hidden=false;
    if(!left){
      if(got>=2){set(KEY,'1');ready('答对 '+got+' 题，可以下载了！');RT.hidden=false;RT.textContent='再答一次题';}
      else{RES.className='qz-res fail';RES.textContent='答对 '+got+' 题，还差一点。可以回到正文再读一读，然后换 3 道题再试一次。';RT.hidden=false;RT.textContent='换 3 道题再答一次';}
      setTimeout(function(){RES.scrollIntoView({block:'nearest',behavior:'smooth'});},50);
    }
  });
  OL.addEventListener('click',function(e){var a=e.target.closest('.qw a');if(a)close(DL);});
  RT.addEventListener('click',function(){build();});
})();
'''


def make_pdf(html_path, pdf, title):
    """把生成好的专题网页打印成 PDF 学习版（lessons/2026-Q4/qa/<pdf>）。需要 node + Playwright 和 .work/fonts。"""
    import subprocess
    root = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
    out = os.path.join(root, PDF_DIR, pdf)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    subprocess.run(['node', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'topic_pdf.js'), html_path, out, title], check=True)
