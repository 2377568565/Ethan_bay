#!/usr/bin/env python3
"""“圣经”栏目的阅读页（仓库根目录 bible.html）。数据由 biblesite.py 生成在 site/bible/（按卷下载，存在手机里）。
2026-10-26 用户要的：整本和合本、KJV、原文（旧约希伯来文、新约希腊文），可以切换、对照；搜索可以搜书卷（拼音首字母 xbl → 希伯来书）、
人名地名和词语（xbl → 希伯仑、希伯来人）、经文出处（来11:1、xbl11:1、Heb 11:1）和全文。
用法：python3 tools/q4/biblesite.py && python3 tools/q4/biblepage.py"""
import os, re, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
THEME = open(os.path.join(HERE, 'theme.css'), encoding='utf-8').read()
TOKENS = THEME[THEME.index(':root{'):THEME.index('@media (min-width:600px)')]   # 网站的颜色（白天、夜间）

CSS = TOKENS + r'''
:root{--c1:#08968C;--c2:#B0631C;--c3:#3A5FC8;--c4:#B07F0E;--c5:#7B4FC4;--c6:#A8324A}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--c1:#1A9C93;--c2:#C9722E;--c3:#5F82E0;--c4:#B5871A;--c5:#946FE0;--c6:#DB5F78}}
:root[data-theme="dark"]{--c1:#1A9C93;--c2:#C9722E;--c3:#5F82E0;--c4:#B5871A;--c5:#946FE0;--c6:#DB5F78}
:root{--serif:"LessonSerif","Noto Serif SC","Source Han Serif SC","Songti SC","STSong","SimSun",serif;--fs:1.06rem;--hdr:96px}
*{box-sizing:border-box}
html,body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--sans);-webkit-text-size-adjust:100%}
button{font:inherit;color:inherit}
.ic{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round;flex:none}
/* 顶栏：返回、书卷章（点开选）、搜索、字号；下面一排版本开关 */
.top{position:sticky;top:0;z-index:20;background:var(--paper);background:color-mix(in srgb,var(--paper) 92%,transparent);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);border-bottom:1px solid var(--rule);padding-top:env(safe-area-inset-top,0px)}
.bar{display:flex;align-items:center;gap:4px;max-width:1100px;margin:0 auto;padding:6px 8px 4px}
.ib{display:grid;place-items:center;width:42px;height:42px;border:0;border-radius:12px;background:none;color:var(--ink-2);cursor:pointer;flex:none;text-decoration:none}
.ib:active{background:var(--surface-2)}
.where{flex:1;min-width:0;display:flex;align-items:center;justify-content:center;gap:4px;height:42px;border:0;background:none;cursor:pointer;font-family:var(--serif);font-weight:800;font-size:1.12rem;color:var(--ink)}
.where span{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.where .ic{width:18px;height:18px;color:var(--gold)}
.modes{display:flex;gap:6px;max-width:1100px;margin:0 auto;padding:2px 12px 8px;overflow-x:auto;scrollbar-width:none}
.modes::-webkit-scrollbar{display:none}
.modes button{flex:1 0 auto;min-width:64px;height:34px;padding:0 12px;border:1px solid var(--rule);border-radius:999px;background:var(--surface);font-size:.88rem;font-weight:600;color:var(--ink-2);cursor:pointer;white-space:nowrap}
.modes button[aria-pressed="true"]{background:var(--ink);border-color:var(--ink);color:var(--paper)}
.cmpopt{display:none;max-width:1100px;margin:0 auto;padding:0 12px 8px;gap:14px;font-size:.84rem;color:var(--ink-2)}
body[data-mode="cmp"] .cmpopt{display:flex}
.cmpopt label{display:flex;align-items:center;gap:5px;cursor:pointer}
/* 正文 */
main{max-width:760px;margin:0 auto;padding:18px 18px calc(110px + env(safe-area-inset-bottom,0px))}
body[data-mode="cmp"] main{max-width:1100px}
.chead{margin:4px 0 18px;text-align:center}
.chead h1{margin:0;font-family:var(--serif);font-weight:900;font-size:1.5rem;letter-spacing:.06em}
.chead p{margin:4px 0 0;font-size:.8rem;color:var(--muted);letter-spacing:.12em}
.vs{font-family:var(--serif);font-size:var(--fs);line-height:1.95}
.v{position:relative;padding:3px 6px;margin:0 -6px;border-radius:8px;cursor:pointer;-webkit-tap-highlight-color:transparent}
.v.sel{background:var(--gold-soft)}
.v.flash{animation:fl 1.6s ease-out}
@keyframes fl{0%,40%{background:color-mix(in srgb,var(--gold-2) 45%,transparent)}100%{background:transparent}}
.n{font-family:var(--sans);font-size:.62em;font-weight:700;color:var(--gold);vertical-align:.45em;margin-right:3px}
body[data-mode="cuv"] .v,body[data-mode="kjv"] .v{display:inline;padding:2px 2px;margin:0}
body[data-mode="kjv"] .vs{font-family:Georgia,"Times New Roman",var(--serif);line-height:1.8}
.en{font-family:Georgia,"Times New Roman",serif}
/* 原文逐字：一个词一格，原文在上，读音、英文意思在下；旧约从右往左排 */
.ol{display:flex;flex-wrap:wrap;gap:2px 4px;padding:4px 0 6px}
.ol[dir=rtl]{direction:rtl}
.w{display:flex;flex-direction:column;align-items:center;padding:3px 4px;border-radius:8px;cursor:pointer;min-width:2.2em}
.w:active,.w.on{background:var(--slate-soft)}
.w .o{font-family:"SBL Hebrew","Ezra SIL","Times New Roman",serif;font-size:1.32em;line-height:1.5;color:var(--ink)}
.ol:not([dir=rtl]) .w .o{font-family:"SBL Greek","Gentium Plus","Times New Roman",serif;font-size:1.15em}
.w .t{font-family:var(--sans);font-size:.62em;line-height:1.3;color:var(--muted);direction:ltr}
.w .g{font-family:var(--sans);font-size:.66em;line-height:1.3;color:var(--slate);direction:ltr;max-width:9em;text-align:center}
body[data-mode="org"] .v{display:block;margin:0 -6px 6px}
.vn{display:block;font-family:var(--sans);font-size:.72rem;font-weight:700;color:var(--gold);margin-top:6px}
/* 对照：手机上一节竖着排；电脑上并排 */
.cmp .v{display:block;margin:0 -6px 10px;padding:8px 6px;border-bottom:1px solid var(--rule)}
.row{display:flex;gap:10px}
.lb{flex:none;width:2.6em;font-family:var(--sans);font-size:.68rem;font-weight:700;color:var(--muted);padding-top:.55em}
.row>div{flex:1;min-width:0}
.row+.row{margin-top:4px}
.row.k>div{font-family:Georgia,"Times New Roman",serif;font-size:.95em;line-height:1.7;color:var(--ink-2)}
@media (min-width:900px){
  .cmp .v{display:grid;grid-template-columns:var(--cols);gap:18px}
  .cmp .row{display:block}.cmp .row+.row{margin-top:0}
  .cmp .lb{display:none}
  .cmphead{display:grid;grid-template-columns:var(--cols);gap:18px;font-size:.8rem;font-weight:700;color:var(--muted);padding:0 6px 8px;border-bottom:1px solid var(--rule);margin-bottom:8px}
}
@media (max-width:899.98px){.cmphead{display:none}}
.note{margin:24px 0 0;font-size:.75rem;line-height:1.6;color:var(--muted)}
/* 上一章、下一章 */
.pn{display:flex;gap:10px;margin-top:28px}
.pn button{flex:1;min-height:52px;border:1px solid var(--rule);border-radius:14px;background:var(--surface);cursor:pointer;font-size:.9rem;font-weight:600;color:var(--ink-2)}
.pn button:disabled{opacity:.35}
.load{padding:40px 0;text-align:center;color:var(--muted);font-size:.9rem}
/* 弹出的面板（选书卷、搜索、经文菜单） */
.sh{position:fixed;inset:0;z-index:50;display:flex;align-items:flex-end;justify-content:center}
.sh[hidden]{display:none}
.sh .bg{position:absolute;inset:0;background:rgba(8,12,20,.45)}
.sh .card{position:relative;width:100%;max-width:720px;max-height:88vh;max-height:88dvh;display:flex;flex-direction:column;background:var(--surface);border-radius:22px 22px 0 0;box-shadow:var(--shadow-2);padding-bottom:env(safe-area-inset-bottom,0px)}
@media (min-width:760px){.sh{align-items:center}.sh .card{border-radius:22px;max-height:82vh}}
.sh .hd{display:flex;align-items:center;gap:8px;padding:12px 12px 8px 16px;border-bottom:1px solid var(--rule)}
.sh .hd h2{flex:1;margin:0;font-size:1.02rem}
.sh .bd{overflow-y:auto;overscroll-behavior:contain;-webkit-overflow-scrolling:touch;padding:10px 14px 18px}
.tabs2{display:flex;gap:6px}
.tabs2 button{height:32px;padding:0 14px;border:1px solid var(--rule);border-radius:999px;background:none;font-size:.86rem;font-weight:600;color:var(--ink-2);cursor:pointer}
.tabs2 button[aria-pressed="true"]{background:var(--gold-soft);border-color:color-mix(in srgb,var(--gold) 40%,var(--rule));color:var(--gold)}
.grp{margin:12px 0 4px;font-size:.74rem;font-weight:700;letter-spacing:.12em;color:var(--muted)}
.bks{display:grid;grid-template-columns:repeat(auto-fill,minmax(64px,1fr));gap:6px}
.bk{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-height:56px;padding:4px 2px;border:0;border-radius:12px;cursor:pointer;background:color-mix(in srgb,var(--c) 14%,var(--surface));color:var(--ink)}
.bk b{font-family:var(--serif);font-size:1.02rem;color:color-mix(in srgb,var(--c) 70%,var(--ink))}
.bk small{font-size:.62rem;color:var(--ink-2);line-height:1.2;text-align:center}
.bk.on{outline:2px solid var(--gold-2)}
.chs{display:grid;grid-template-columns:repeat(auto-fill,minmax(48px,1fr));gap:6px;margin-top:8px}
.chs button{height:46px;border:1px solid var(--rule);border-radius:12px;background:var(--paper);cursor:pointer;font-weight:600}
.chs button.on{background:var(--ink);color:var(--paper);border-color:var(--ink)}
.back2{border:0;background:none;color:var(--gold);font-weight:600;cursor:pointer;padding:6px 0}
/* 搜索 */
.sbox{display:flex;align-items:center;gap:8px;flex:1;height:42px;padding:0 12px;border:1px solid var(--rule);border-radius:12px;background:var(--paper)}
.sbox input{flex:1;min-width:0;border:0;outline:0;background:none;font-size:16px;color:var(--ink)}
.sbox .ic{color:var(--muted);width:19px;height:19px}
.rs{display:block;width:100%;text-align:left;padding:11px 12px;margin:0 0 6px;border:1px solid var(--rule);border-radius:12px;background:var(--paper);cursor:pointer;color:var(--ink)}
.rs:active{background:var(--surface-2)}
.rs b{font-family:var(--serif)}
.rs small{display:block;margin-top:2px;font-size:.76rem;color:var(--muted)}
.rs.go{background:var(--gold-soft);border-color:color-mix(in srgb,var(--gold) 35%,var(--rule))}
.rs.go b{color:var(--gold)}
.chips{display:flex;flex-wrap:wrap;gap:6px}
.chip{display:inline-flex;align-items:baseline;gap:4px;padding:7px 12px;border:1px solid var(--rule);border-radius:999px;background:var(--paper);cursor:pointer;font-size:.92rem;color:var(--ink)}
.chip i{font-style:normal;font-size:.7rem;color:var(--muted)}
.hit{display:block;width:100%;text-align:left;padding:9px 4px;border:0;border-bottom:1px solid var(--rule);background:none;cursor:pointer;font-family:var(--serif);font-size:.95rem;line-height:1.75;color:var(--ink)}
.hit em{font-style:normal;font-family:var(--sans);font-size:.74rem;font-weight:700;color:var(--gold);margin-right:6px}
.hit mark{background:color-mix(in srgb,var(--gold-2) 45%,transparent);color:inherit;border-radius:3px;padding:0 1px}
.more{display:block;margin:12px auto 0;padding:9px 18px;border:1px solid var(--rule);border-radius:999px;background:none;cursor:pointer;color:var(--ink-2)}
.tip{font-size:.8rem;color:var(--muted);line-height:1.7}
.recent{margin-top:6px}
/* 经文菜单 */
.acts{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:10px}
.acts button{min-height:52px;border:1px solid var(--rule);border-radius:12px;background:var(--paper);cursor:pointer;font-size:.88rem;font-weight:600;color:var(--ink-2)}
.vq{font-family:var(--serif);line-height:1.85;margin:0}
.lex{margin-top:10px;padding:10px 12px;border-radius:12px;background:var(--slate-soft);font-size:.86rem;line-height:1.6}
.lex b{font-family:"SBL Hebrew","Times New Roman",serif;font-size:1.15rem}
.toast{position:fixed;left:50%;bottom:calc(90px + env(safe-area-inset-bottom,0px));transform:translate(-50%,10px);opacity:0;transition:opacity .2s,transform .2s;z-index:60;padding:8px 16px;border-radius:999px;background:var(--ink);color:var(--paper);font-size:.86rem;pointer-events:none}
.toast.on{opacity:1;transform:translate(-50%,0)}
@media (prefers-reduced-motion:reduce){.v.flash{animation:none}.toast{transition:none}}
'''

I = {'back': '<path d="m15 18-6-6 6-6"/>', 'down': '<path d="m6 9 6 6 6-6"/>', 'search': '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>',
     'aa': '<path d="M4 18 9 6l5 12M5.8 14h6.4M15 18l3-7 3 7M15.9 16h4.2"/>', 'x': '<path d="M6 6l12 12M18 6 6 18"/>'}


def ic(k):
    return f'<svg class="ic" viewBox="0 0 24 24" aria-hidden="true">{I[k]}</svg>'


JS = open(os.path.join(HERE, 'bible.js'), encoding='utf-8').read()


def page():
    idx = sorted(glob.glob(os.path.join(ROOT, 'site', 'bible', 'index-*.json')))
    assert len(idx) == 1, '先运行 biblesite.py（site/bible 里应当只有一个 index 文件）'
    index = 'site/bible/' + os.path.basename(idx[0])
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>圣经 · 预言的恩赐</title>
<meta name="description" content="和合本、KJV 和原文（希伯来文、希腊文）圣经，可以切换、对照，搜书卷、人名地名、词语和经文。">
<script>try{{var t=localStorage.getItem('q4:theme');if(t)document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}</script>
<style>{CSS}</style></head>
<body data-mode="cuv">
<header class="top"><div class="bar">
<a class="ib" href="./#home" data-home aria-label="回首页">{ic('back')}</a>
<button class="where" type="button" data-pick aria-label="选择书卷和章"><span id="where">圣经</span>{ic('down')}</button>
<button class="ib" type="button" data-search aria-label="搜索">{ic('search')}</button>
<button class="ib" type="button" data-font aria-label="字号">{ic('aa')}</button>
</div>
<div class="modes" role="group" aria-label="版本">
<button type="button" data-mode="cuv" aria-pressed="true">和合本</button><button type="button" data-mode="kjv" aria-pressed="false">KJV</button><button type="button" data-mode="org" aria-pressed="false">原文</button><button type="button" data-mode="cmp" aria-pressed="false">对照</button>
</div>
<div class="cmpopt"><span>对照显示：</span><label><input type="checkbox" data-cmp="cuv" checked>和合本</label><label><input type="checkbox" data-cmp="kjv" checked>KJV</label><label><input type="checkbox" data-cmp="org">原文</label></div>
</header>
<main id="main"><p class="load">正在打开……</p></main>
<div class="sh" id="pick" hidden><div class="bg" data-close></div><div class="card" role="dialog" aria-modal="true" aria-label="选择书卷和章">
<div class="hd"><h2>选择书卷</h2><div class="tabs2"><button type="button" data-t="ot" aria-pressed="true">旧约</button><button type="button" data-t="nt" aria-pressed="false">新约</button></div><button class="ib" type="button" data-close aria-label="关闭">{ic('x')}</button></div>
<div class="bd" id="pickbd"></div></div></div>
<div class="sh" id="find" hidden><div class="bg" data-close></div><div class="card" role="dialog" aria-modal="true" aria-label="搜索圣经">
<div class="hd"><label class="sbox">{ic('search')}<input id="q" type="search" enterkeyhint="search" autocomplete="off" placeholder="书卷、经文、人名或词语，如 xbl、来11:1、信心"></label><button class="ib" type="button" data-close aria-label="关闭">{ic('x')}</button></div>
<div class="bd" id="res"></div></div></div>
<div class="sh" id="vm" hidden><div class="bg" data-close></div><div class="card" role="dialog" aria-modal="true" aria-label="这一节经文">
<div class="hd"><h2 id="vmt"></h2><button class="ib" type="button" data-close aria-label="关闭">{ic('x')}</button></div>
<div class="bd" id="vmb"></div></div></div>
<div class="toast" id="toast" role="status"></div>
<script>var BIBLE_INDEX={json.dumps(index)};</script>
<script>{JS}</script>
</body></html>'''


if __name__ == '__main__':
    h = page()
    out = os.path.join(ROOT, 'bible.html')
    open(out, 'w', encoding='utf-8').write(h)
    print(out, len(h.encode()), 'bytes')
