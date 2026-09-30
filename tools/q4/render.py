"""生成《预言的恩赐》逐课研读网页：单课文件 + 全季合集文件。

用法：python3 render.py [课号...]      只生成指定课的单课文件
      python3 render.py all            生成全部单课文件 + 全季合集
"""
import welcome, intro, bible, qa_data
import urllib.parse
import re, sys, os, html, datetime, importlib, subprocess, json
Q4 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, Q4); sys.path.insert(0, os.path.join(Q4, 'data'))
from gen_yw import build as build_yw, merged, DAYS

OUT = '/home/user/Ethan_bay/lessons/2026-Q4'
Q_START = datetime.date(2026, 9, 26)          # 第1课安息日下午
DAYNAMES = dict(DAYS)
CN_WEEK = ['安息日下午', '星期日', '星期一', '星期二', '星期三', '星期四', '星期五']

# ---------- 文本小工具 ----------
REF_RE = re.compile(r'（([^（）<>]*?(?:\d+[:：]\d|原文第|\d+章|\d+篇)[^（）<>]*?)）')
def fmt(s):
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    return REF_RE.sub(r'<span class="ref">（\1）</span>', s)

def md(d):
    return f'{d.month}月{d.day}日'

def dates_for(no):
    s = Q_START + datetime.timedelta(days=7 * (no - 1))
    return [s + datetime.timedelta(days=i) for i in range(7)]

def blocks(items):
    out = []
    for it in items:
        if isinstance(it, str):
            out.append(f'<p>{fmt(it)}</p>')
        elif it[0] in ('ul', 'ol'):
            lis = ''.join(f'<li>{fmt(x)}</li>' for x in it[1])
            out.append(f'<{it[0]}>{lis}</{it[0]}>')
        elif it[0] == 'table':
            th = ''.join(f'<th>{h}</th>' for h in it[1])
            rows = ''.join('<tr>' + ''.join(f'<td>{fmt(c)}</td>' for c in r) + '</tr>' for r in it[2])
            out.append(f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{rows}</tbody></table></div>')
        elif it[0] == 'egw':
            out.append(egw(it[1], it[2]))
        else:
            raise ValueError(it)
    return '\n'.join(out)

def egw(q, cite):
    return (f'<div class="egw"><span class="k">怀著亮光</span><blockquote>“{fmt(q)}”</blockquote>'
            f'<cite>{cite}</cite></div>')

def lens(title, inner):
    return f'<div class="lens">\n<h3>{title}</h3>\n{inner}\n</div>'

# ---------- 单日解读 ----------
def render_day(no, i, d, ywtitle):
    key = d['key']; dt = md(dates_for(no)[i])
    parts = []
    parts.append(lens('核心概述', f'<div class="prose">{blocks(d["core"])}</div>'))
    X = '<span class="x">↔</span>'
    pairs = ''.join(
        f'<li><span class="link">{X.join(fmt(x.strip()) for x in a.split("↔"))}</span>'
        f'<span class="why">{fmt(b)}</span></li>' for a, b in d['pairs'])
    eg = ''.join(egw(q, c) for q, c in d.get('egw', []))
    parts.append(lens('以经解经', f'<ul class="pairs">{pairs}</ul>{eg}'))
    qas = []; qn = 0; en = 0
    for qa in d['qa']:
        if qa['t'] == 'q':
            qn += 1; qid = f' id="{key}-q{qn}"'; tag = '<span class="tag">学课原题</span>'; mk = f'{key}-q{qn}'
        else:
            en += 1; qid = ''; tag = '<span class="tag ext">延伸思考</span>'; mk = f'{key}-e{en}'
        my = (f'<details class="my"><summary>写下我的回答</summary><textarea data-k="{mk}" aria-label="我的回答">'
              f'</textarea><span class="saved"></span></details>') if qa.get('my') else ''
        qas.append(f'<div class="qa"{qid}>{tag}<p class="q">{fmt(qa["q"])}</p><div class="lines" aria-hidden="true"></div>'
                   f'<div class="ans">{blocks(qa["a"])}{my}</div></div>')
    parts.append(lens('思考问答', '\n'.join(qas)))
    sh = ''.join(f'<li><span class="from">{fmt(a)}</span><span class="arrow">→</span><span class="to">{fmt(b)}</span></li>'
                 for a, b in d['shift'])
    parts.append(lens('需要提升的认知', f'<ul class="shift">{sh}</ul>'))
    parts.append(lens('上帝的心意', f'<p class="heart">{fmt(d["heart"])}</p>'))
    acts = ''.join(f'<li><label><input type="checkbox" data-k="{key}-{j}"><span>{fmt(a)}</span></label></li>'
                   for j, a in enumerate(d['acts'], 1))
    parts.append(lens('我们的行动', f'<ul class="acts">{acts}</ul>'))
    dn = DAYNAMES[key]
    return f'''<section class="day" id="{key}">
  <header class="dayhead">
    <p class="when"><span class="dn">{dn}</span><span class="dt">{dt}</span></p>
    <h2>{fmt(d["title"])}</h2>
    <p class="btnrow"><a class="btn" href="#yw-{key}">阅读本日学课原文 →</a></p>
    <p class="texts">{d["texts"]}</p>
  </header>
{chr(10).join(parts)}
</section>''', qn

def nav_html(titles):
    abbr = ['导言', '日', '一', '二', '三', '四', '五']
    r1 = ''.join(f'<a href="#{k}"><span class="d">{a}</span><span class="t">{t}</span></a>'
                 for (k, _), a, t in zip(DAYS, abbr, titles))
    r2 = ''.join(f'<a href="#yw-{k}"><span class="d">{a}</span><span class="t">{t}</span></a>'
                 for (k, _), a, t in zip(DAYS, abbr, titles))
    return f'''<nav class="nav" aria-label="本课目录">
  <div class="navrow" data-row="jd"><span class="k">解读</span>{r1}<a href="#sum"><span class="d">总结</span><span class="t">知 · 信 · 行</span></a></div>
  <div class="navrow" data-row="yw"><span class="k">原文</span>{r2}</div>
</nav>'''

def yw_titles(no):
    fp = 5 + 7 * (no - 1)
    t = ['安息日下午']
    for i in range(1, 7):
        ts = [b['text'] for b in merged(fp + i) if b['kind'] == 'title']
        t.append(ts[0] if ts else DAYNAMES[DAYS[i][0]])
    return t

def yw_section(no, title, overrides, qids, intro_pages=None):
    ds = [md(x) for x in dates_for(no)]
    frag = build_yw(no, 5 + 7 * (no - 1), ds, title, overrides, qids, intro_pages=intro_pages)
    return f'''<section class="yw" id="yuanwen">
  <header class="parthead">
    <p class="k">第二部分</p>
    <h2>学课原文</h2>
    <p>以下是《安息日学研经指引》第{no}课的原文，按日排列。每一天的标题下都有“查看本日解读”按钮，可随时在原文与解读之间切换；原文中的思考题旁边有“看参考解答”链接。</p>
  </header>
{frag}
</section>'''

def orig_qcount(no, key, overrides):
    if key in overrides:
        return sum(1 for k, _ in overrides[key][1] if k == 'q')
    i = [k for k, _ in DAYS].index(key)
    return sum(1 for b in merged(5 + 7 * (no - 1) + i) if b['kind'] == 'q' and not b['text'].startswith('■'))

def render_lesson(mod):
    no = mod.NO
    if getattr(mod, 'RAW', None):          # 第1课：手写片段
        frag = open(os.path.join(Q4, 'data', mod.RAW), encoding='utf-8').read()
        qids = {f'{k}-{n}': f'{k}-q{n}' for k, _ in DAYS for n in range(1, 6)}
        yw = yw_section(no, mod.TITLE, mod.OVERRIDES, qids)
        yw = yw[yw.index('<article'):yw.rindex('</section>')]
        return reorder(frag.replace('<!--YUANWEN-->', yw))
    L = mod.L; ov = getattr(mod, 'OVERRIDES', {})
    ds = dates_for(no)
    titles = yw_titles(no)
    days = []; qids = {}
    for i, d in enumerate(L['days']):
        h, qn = render_day(no, i, d, titles[i])
        want = orig_qcount(no, d['key'], ov)
        if qn != want:
            raise SystemExit(f'第{no}课 {d["key"]}：解读里有 {qn} 道学课原题，原文有 {want} 道')
        for n in range(1, qn + 1): qids[f'{d["key"]}-{n}'] = f'{d["key"]}-q{n}'
        days.append(h)
    HI = ' class="hi"'
    arc = ''.join(f'<li{HI if hi else ""}><span class="w">{w}</span><span class="v">{v}</span><span class="r">{r}</span></li>'
                  for w, v, r, hi in L['arc'])
    ess = ''.join(f'<p>{fmt(p)}</p>' for p in L['essence'])
    k = L['kxx']
    kxx = ''.join(f'<section><h4>{h}<small>{s}</small></h4><ul>{"".join(f"<li>{fmt(x)}</li>" for x in k[key])}</ul></section>'
                  for h, s, key in (('知', '要明白的', 'know'), ('信', '要持守的', 'believe'), ('行', '要去做的', 'do')))
    disc = ''.join(f'<li>{fmt(x)}</li>' for x in L['discuss'])
    summary = f'''<section class="day" id="sum">
  <header class="dayhead">
    <p class="when"><span class="dn">本课总结</span><span class="dt">{md(ds[0] + datetime.timedelta(days=7))}安息日</span></p>
    <h2>知 · 信 · 行</h2>
  </header>
  <div class="kxx">{kxx}</div>
  {lens('安息日班讨论建议', f'<ol>{disc}</ol>')}
  {lens('本周背诵', f'<p class="heart">{fmt(L["recite"])}</p>')}
</section>'''
    yw = yw_section(no, L['title'], ov, qids)
    rng = f'{md(ds[0])}—{md(ds[6])}'
    return reorder(f'''<header class="masthead">
  <p class="eyebrow">安息日学研经指引 · 2026年第4季 ·《预言的恩赐》</p>
  <p class="meta"><b>第{no}课</b><span>{rng}</span><span>为{md(ds[0] + datetime.timedelta(days=7))}安息日预备</span></p>
  <h1>{L["title"]}</h1>
  <div class="memory">
    <span class="k">存心节 · {L["mem_ref"]}</span>
    <blockquote>“{L["mem"]}”</blockquote>
  </div>
  <p class="readings"><b>本周经文</b>{L["readings"]}</p>
  <p class="btnrow top"><a class="btn solid" href="#yuanwen">学课原文</a><a class="btn" href="#sab">开始研读</a></p>
</header>

<section class="essence" aria-label="本课精要">
  <span class="k">本课精要</span>
  {ess}
  <ol class="arc" style="--n:{len(L["arc"])}" aria-label="本课一条线">{arc}</ol>
  <p class="arc-cap">{fmt(L["arc_cap"])}</p>
</section>

<div class="layout">
{nav_html(titles)}
<main>
{chr(10).join(days)}
{summary}
{yw}
</main>
</div>''')

def reorder(h):
    """原文在前、解读在后；两排导航也把“原文”放上面；学课原题加“回到原文问题”。"""
    m = re.search(r'<section class="yw" id="yuanwen">.*?</section>\n?', h, re.S)
    yw = h[m.start():m.end()]; h = h[:m.start()] + h[m.end():]
    yw = yw.replace('<p class="k">第二部分</p>', '<p class="k">第一部分</p>', 1)
    yw = re.sub(r'(<h2>学课原文</h2>\s*<p>)[^<]*(</p>)',
                r'\1先读原文。每天标题下的“查看本日解读”可直接翻到当天的解读；原文里的思考题下有“看参考解答”。\2', yw, 1)
    jd = ('<header class="parthead jdhead" id="yandu">\n  <p class="k">第二部分</p>\n  <h2>逐日解读</h2>\n'
          '  <p>读完原文，再逐日深入：核心概述、以经解经、思考问答、需要提升的认知、上帝的心意、我们的行动。'
          '标着“学课原题”的问答，可点“回到原文问题”翻回原文。</p>\n</header>\n')
    h = h.replace('<main>\n', '<main>\n' + yw + jd, 1)
    h = re.sub(r'(<div class="navrow" data-row="jd">.*?</div>)(\s*)(<div class="navrow" data-row="yw">.*?</div>)',
               r'\3\2\1', h, count=1, flags=re.S)
    h = h.replace('<a class="btn" href="#sab">开始研读</a>', '<a class="btn" href="#yandu">逐日解读</a>')
    ids = set(re.findall(r'id="yw-(\w+-q\d+)"', h))
    def back(mm):
        q = mm.group(1)
        if q not in ids: return mm.group(0)
        return (f'<div class="qa" id="{q}">{mm.group(2)}<p class="qtop"><span class="tag">学课原题</span>'
                f'<a class="toyw" href="#yw-{q}">↩ 回到原文问题</a></p>')
    h = re.sub(r'<div class="qa" id="(\w+-q\d+)">(\s*)<span class="tag">学课原题</span>', back, h)
    missing = ids - set(re.findall(r'href="#yw-(\w+-q\d+)"', h))
    if missing: raise SystemExit(f'原文问题缺少返回链接：{sorted(missing)}')
    return h

def intro_frag():
    l1 = load(1)
    full = build_yw(1, 5, [md(x) for x in dates_for(1)], l1.TITLE, l1.OVERRIDES, {}, intro_pages=l1.INTRO_PAGES)
    art = full[:full.index('</article>') + len('</article>')]
    return intro.render_intro(art, fmt)

INTRO_GIST = '上帝从来没有停止说话；问题从来不在祂是否说话，而在我们是否在听。先读导言原文，再看全季总览。'

_NKJV = None
def nkjv_ok():
    """全季统一挑选 NKJV 经节（上限 1000 节），单课文件与合集保持一致。"""
    global _NKJV
    if _NKJV is None:
        L = bible.Linker(); L.html(intro_frag())
        for n in range(1, 14): L.html(render_lesson(load(n)))
        _NKJV = bible.nkjv_choice(L.refs)
    return _NKJV

POPUP = '''<div id="bpop" class="bpop" hidden>
  <div class="bpop-bg" data-bclose></div>
  <div class="bpop-card" role="dialog" aria-modal="true" aria-labelledby="bpop-t" tabindex="-1">
    <div class="bpop-grip" aria-hidden="true"></div>
    <header class="bpop-head">
      <div><p class="bpop-k">经文 · 三版本对照</p><h3 id="bpop-t"></h3></div>
      <button class="bpop-x" type="button" data-bclose aria-label="关闭">×</button>
    </header>
    <nav class="bpop-tabs" aria-label="版本">
      <button type="button" data-sec="cuv" class="on">和合本</button><button type="button" data-sec="en">NKJV</button><button type="button" data-sec="og">原文 · 直译</button>
    </nav>
    <div class="bpop-body"></div>
    <details class="bpop-foot"><summary>版本与版权说明</summary>和合本（上帝版，公有领域）。英文：Scripture taken from the New King James Version®. Copyright © 1982 by Thomas Nelson. Used by permission. All rights reserved.（全书 NKJV 引用以 1000 节为限，其余经节以 KJV 补足并标注。）原文与英文逐字直译：STEPBible.org TAHOT / TAGNT，CC BY 4.0。中文直译为本页编者依据原文逐字释义译出，保留原文语序与习语（以“直译：”标注），仅供研读参考。点原文单词可看词典原形与字义。</details>
  </div>
</div>'''

def with_bible(body_html):
    L = bible.Linker(); h = L.html(body_html)
    data = bible.payload(L.refs, nkjv_ok())
    return h + '\n' + POPUP + f'\n<script type="application/json" id="bdata">{data}</script>'

def lab(n):
    return '导言' if n == 0 else f'第{n}课'

# ---------- 组装 ----------
def prefix(frag, no):
    p = f'l{no}-'
    frag = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{p}{m.group(1)}"', frag)
    frag = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{p}{m.group(1)}"', frag)
    frag = re.sub(r'data-k="([^"]+)"', lambda m: f'data-k="{p}{m.group(1)}"', frag)
    return frag

EXTRA_CSS = open(os.path.join(Q4, 'extra.css'), encoding='utf-8').read()
BASE_CSS = open(os.path.join(Q4, 'base.css'), encoding='utf-8').read()
JS = open(os.path.join(Q4, 'app.js'), encoding='utf-8').read()
FOOT = '''<footer>
  <p class="credit">整理制作：Ethan（HangZhou_XG） · © 2026　转发分享请保留出处，请勿修改后另行发布，或用于商业用途。</p>
  <p>本页为安息日学研读辅助材料，依据《安息日学研经指引》2026年第4季整理。“学课原文”部分版权归原出版机构所有，仅供教会安息日学学习使用，请勿用于商业用途。</p>
  <p>经文引自和合本（上帝版）。怀爱伦著作引文依英文原著译出，页码为英文原文页码；学课中已有译文的，沿用学课译文。</p>
  <p>“写下我的回答”和行动勾选只保存在你自己的浏览器里，不会上传。</p>
</footer>'''

def shell(title, desc, body, combined):
    early = ("<script>document.documentElement.classList.add('jsok'" + (",'js'" if combined else '') + ");</script>")
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{desc}">
<title>{title}</title>
{early}
<style>
/*FONTS*/
{BASE_CSS}
{EXTRA_CSS}
</style>
</head>
<body{' class="combined"' if combined else ''}>
<div class="page">
{NOJS}
{body}
{FOOT}
</div>
<script>
{JS}
</script>
</body>
</html>
'''

ONLINE = 'https://2377568565.github.io/Ethan_bay/'
NOJS = f'''<div class="nojs-note" role="note">
  <p><b>你现在是在“预览模式”里阅读</b>（苹果手机在微信里直接点开 HTML 文件时就是这样）。这种模式不运行网页脚本，所以<b>欢迎页、按日期推荐、经文弹窗、翻页动画</b>都不会出现，但所有文字内容仍可阅读。</p>
  <p>完整体验请打开在线版（在微信里点链接即可，会用微信内置浏览器打开）：<br><a href="{ONLINE}">{ONLINE}</a></p>
</div>'''

def load(no):
    return importlib.import_module(f'l{no:02d}')

def lesson_title(mod):
    return mod.TITLE if getattr(mod, 'RAW', None) else mod.L['title']

def lesson_gist(mod):
    return mod.GIST if getattr(mod, 'RAW', None) else mod.L['gist']

def build_single_intro():
    frag = prefix(intro_frag(), 0).replace('#l0-NEXTLESSON', 'lesson-01.html')
    bar = '<div class="lessonbar single"><span>2026年第4季《预言的恩赐》逐课研读 · 本季导言</span></div>'
    out = shell('预言的恩赐 · 本季导言', '安息日学2026年第4季《预言的恩赐》导言原文与全季总览。',
                with_bible(f'<div class="lesson" id="l0">{bar}\n{frag}\n</div>'), False)
    tmp = os.path.join(Q4, '_l00.html'); open(tmp, 'w', encoding='utf-8').write(out)
    dst = os.path.join(OUT, 'lesson-00-intro.html')
    subprocess.run(['python3', os.path.join(Q4, 'build.py'), tmp, dst], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return dst

def build_single(no):
    mod = load(no)
    frag = prefix(render_lesson(mod), no)
    bar = f'<div class="lessonbar single"><span>2026年第4季《预言的恩赐》逐课研读 · 第{no}课</span></div>'
    body = f'<div class="lesson" id="l{no}">{bar}\n{frag}\n</div>'
    t = lesson_title(mod)
    out = shell(f'{t} · 第{no}课研读', f'安息日学2026年第4季《预言的恩赐》第{no}课《{t}》逐日研读与学课原文。', with_bible(body), False)
    tmp = os.path.join(Q4, f'_l{no:02d}.html')
    open(tmp, 'w', encoding='utf-8').write(out)
    dst = os.path.join(OUT, f'lesson-{no:02d}.html')
    subprocess.run(['python3', os.path.join(Q4, 'build.py'), tmp, dst], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return dst, frag, mod

HOUSE = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M3.5 11.2 12 4l8.5 7.2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'
         '<path d="M6 9.8v9.7h4.4v-5.6h3.2v5.6H18V9.8" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/></svg>')
GOHOME = f'<a class="btn gohome" href="#home" data-gohome>{HOUSE}主页</a>'
WXIC = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M9.3 4C5.2 4 2 6.7 2 10.1c0 1.9 1 3.5 2.6 4.6L4 17.2l2.9-1.5c.8.2 1.6.4 2.4.4h.5a5.4 5.4 0 0 1-.2-1.5c0-3.3 3.1-6 7-6h.5C16.3 5.9 13.1 4 9.3 4z" fill="currentColor"/>'
        '<path d="M22 14.6c0-2.8-2.8-5-6.2-5s-6.2 2.2-6.2 5 2.8 5 6.2 5c.7 0 1.4-.1 2-.3l2.3 1.3-.6-2.1c1.5-.9 2.5-2.3 2.5-3.9z" fill="currentColor" opacity=".82"/></svg>')
LINKIC = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3-3a4.5 4.5 0 0 0-6.4-6.4l-1.2 1.2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>'
          '<path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3 3a4.5 4.5 0 0 0 6.4 6.4l1.2-1.2" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>')

def qr_svg(url):
    import qrcode
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, border=2); q.add_data(url); q.make()
    m = q.get_matrix(); n = len(m)
    d = ''.join(f'M{x},{y}h1v1h-1z' for y in range(n) for x in range(n) if m[y][x])
    return f'<svg viewBox="0 0 {n} {n}" shape-rendering="crispEdges" role="img" aria-label="二维码"><rect width="{n}" height="{n}" fill="#fff"/><path d="{d}" fill="#111"/></svg>'

def qr_all():
    ids = ['qa', 'ask'] + [it['id'] for it in qa_data.ITEMS]
    return ''.join(qr_svg(ONLINE + '#' + i).replace('<svg ', f'<svg data-for="{i}" ', 1) for i in ids)

SHAREIC = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5.5" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/>'
           '<circle cx="6" cy="12" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/><circle cx="18" cy="18.5" r="2.6" fill="none" stroke="currentColor" stroke-width="2"/>'
           '<path d="M8.3 10.8 15.7 6.7M8.3 13.2l7.4 4.1" fill="none" stroke="currentColor" stroke-width="2"/></svg>')
def homeui():
    return f'''<button class="fab" type="button" data-gohome aria-label="返回主页">{HOUSE}<span>主页</span></button>
<div class="hconf" id="hconf" role="alertdialog" aria-modal="true" aria-labelledby="hconf-t" aria-describedby="hconf-d" hidden>
  <div class="hconf-bg" data-hno></div>
  <div class="hconf-card">
    <div class="hconf-ic">{HOUSE}</div>
    <h3 id="hconf-t">是否确定返回主页？</h3>
    <p id="hconf-d">将打开欢迎页。之后点欢迎页右上角的 ×，就能回到现在的阅读位置。</p>
    <div class="hconf-btns"><button type="button" data-hno>取消</button><button type="button" class="ok" data-hok>确定</button></div>
  </div>
</div>
<div class="shsheet" id="shsheet" role="dialog" aria-modal="true" aria-labelledby="sh-h" data-base="{ONLINE}" hidden>
  <div class="sh-bg" data-shclose></div>
  <div class="sh-card">
    <button class="sh-x" type="button" data-shclose aria-label="关闭">×</button>
    <h3 id="sh-h">分享这篇问答</h3>
    <p class="sh-t"></p>
    <div class="sh-main">
      <button type="button" class="sh-tile sh-wxbtn" data-shwx>{WXIC}<span>微信分享</span></button>
      <button type="button" class="sh-tile" data-shcopy>{LINKIC}<span>复制链接</span></button>
      <button type="button" class="sh-tile" data-shsys hidden>{SHAREIC}<span>更多方式</span></button>
    </div>
    <div class="sh-qr" hidden><div class="sh-qrimg"></div><p><b>用手机微信扫一扫</b>打开后点右上角 ··· 就能转发给朋友或群；也可以复制链接，粘贴到电脑版微信的聊天框。</p></div>
    <p class="sh-done" aria-live="polite"></p>
    <button type="button" class="sh-sent" data-shsent hidden>✓ 我已经分享好了</button>
    <span class="sh-url"></span>
  </div>
</div>
<div class="wxguide" id="wxguide" role="dialog" aria-modal="true" aria-label="微信转发提示" hidden>
  <svg viewBox="0 0 100 100" aria-hidden="true"><path d="M18 88 C30 50 52 30 84 16" fill="none" stroke="#FCE7B0" stroke-width="5" stroke-linecap="round" stroke-dasharray="2 10"/><path d="M68 12 86 15 80 32" fill="none" stroke="#FCE7B0" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>
  <p class="wg-t">点右上角 <span style="letter-spacing:.1em">···</span><br>选择“转发给朋友”</p>
  <div class="wg-box">
    <p>选好群或朋友、发送之后，回到这里点一下：</p>
    <div class="wg-btns"><button type="button" class="ok" data-wgdone>✓ 我已转发</button><button type="button" data-wgcancel>先不转发</button></div>
  </div>
</div>
<div class="sh-qrs" hidden>{qr_all()}</div>'''

GIFT_REFS = [('以赛亚书 52:7', 22, 52, 7), ('箴言 11:25', 19, 11, 25), ('加拉太书 6:9', 47, 6, 9), ('希伯来书 10:24', 57, 10, 24),
             ('帖撒罗尼迦前书 5:11', 51, 5, 11), ('马太福音 5:14', 39, 5, 14), ('马太福音 5:16', 39, 5, 16), ('但以理书 12:3', 26, 12, 3),
             ('歌罗西书 3:16', 50, 3, 16), ('诗篇 96:3', 18, 96, 3), ('哥林多前书 15:58', 45, 15, 58), ('箴言 25:25', 19, 25, 25),
             ('箴言 15:23', 19, 15, 23), ('腓立比书 1:6', 49, 1, 6), ('约翰福音 13:35', 42, 13, 35), ('彼得前书 3:15', 59, 3, 15),
             ('提摩太后书 2:15', 54, 2, 15), ('耶利米书 15:16', 23, 15, 16), ('诗篇 119:105', 18, 119, 105)]

def gift_html():
    """分享之后的鼓励弹窗：礼盒打开，附一节随机的经文礼物"""
    pool = []
    for r, b, c, v in GIFT_REFS:
        t = re.sub(r'\s+', '', bible.cuv(b, c, v)).replace('－', '')
        if t.count('“') != t.count('”'): t = t.replace('”', '').replace('“', '')
        t = re.sub(r'[；，、]$', '。', t)
        pool.append([t, r])
    stars = ''.join('<i>✦</i>' for _ in range(7))
    box = ('<svg viewBox="0 0 120 112" aria-hidden="true"><defs>'
           '<linearGradient id="gbx" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FBE6A6"/><stop offset="1" stop-color="#D5A23A"/></linearGradient>'
           '<radialGradient id="ggl"><stop offset="0" stop-color="#FFF4CC" stop-opacity=".95"/><stop offset="1" stop-color="#FFF4CC" stop-opacity="0"/></radialGradient></defs>'
           '<circle class="glow" cx="60" cy="50" r="54" fill="url(#ggl)"/>'
           '<g class="base"><rect x="22" y="52" width="76" height="52" rx="6" fill="url(#gbx)"/><rect x="54" y="52" width="12" height="52" fill="#8E2F40"/>'
           '<rect x="22" y="52" width="76" height="7" fill="#000" opacity=".08"/></g>'
           '<g class="lid"><rect x="16" y="38" width="88" height="17" rx="5" fill="url(#gbx)"/><rect x="54" y="38" width="12" height="17" fill="#8E2F40"/>'
           '<path d="M60 38C47 19 29 23 37 33c4 5 14 5 23 5zM60 38c13-19 31-15 23-5-4 5-14 5-23 5z" fill="#A83A4D"/></g></svg>')
    return f'''<div class="gift" id="gift" role="dialog" aria-modal="true" aria-labelledby="gift-h" hidden>
  <div class="gift-bg" data-giftclose></div>
  <div class="gift-card">
    <div class="gift-box">{box}</div>
    <p class="gift-k">✦ 谢谢你的分享 ✦</p>
    <h3 id="gift-h">你把好消息传出去了</h3>
    <p class="gift-msg"></p>
    <p class="gift-stars" aria-hidden="true">{stars}</p>
    <div class="gift-verse">
      <p class="gift-vk">送你一节经文礼物</p>
      <button type="button" class="gift-vcopy" data-giftcopy>复制</button>
      <blockquote class="gift-vt"></blockquote>
      <p class="gift-vr"></p>
    </div>
    <p class="gift-done" aria-live="polite"></p>
    <p class="gift-q">接下来想去哪里？</p>
    <div class="gift-btns"><button type="button" data-giftstay>回到刚才的页面</button><button type="button" class="ok" data-giftgo>去问题彩蛋 ✦</button></div>
  </div>
  <div class="gift-fall" aria-hidden="true"></div>
</div>
<script type="application/json" id="giftpool">{json.dumps(pool, ensure_ascii=False)}</script>'''

def qa_heb(key):
    b, c, v = map(int, key.split('.'))
    out = ''
    for w in bible.original([(b, c, v)])[(b, c, v)]: out += w[0] + ('' if w[0].endswith('־') else ' ')
    return out.strip()

def qa_article(it, tail):
    frag = open(os.path.join(qa_data.SRC, it['src']), encoding='utf-8').read()
    frag = re.sub(r'<!--title:.*?-->\n?', '', frag)
    frag = re.sub(r' data-ref="[^"]*"', '', frag)
    frag = re.sub(r'\{\{HEB ([\d.]+)\}\}', lambda m: qa_heb(m.group(1)), frag)
    assert '<footer class="colophon">' in frag
    frag = frag.replace('<footer class="colophon">', tail + '\n<footer class="colophon">', 1)
    frag = frag.replace('</header>', f'</header>\n<p class="qshare"><button class="btn share" type="button" data-share="{it["id"]}">{SHAREIC}分享这篇</button></p>', 1)
    return f'<article class="qna">\n{frag}\n</article>'

# ---------- 提问区（腾讯云开发） ----------
ASK_ENV = 'wenda-d8gqka1o3902489eb'
ASK_ADMINS = []            # 管理员身份码（在提问区点“我是整理者”可看到），绑定后回答带“管理员回答”标记
PINIC = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-6.5-6.2-6.5-11A6.5 6.5 0 0 1 18.5 10c0 4.8-6.5 11-6.5 11z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/>'
         '<circle cx="12" cy="10" r="2.4" fill="currentColor"/></svg>')
COPYIC = ('<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><rect x="8.5" y="8.5" width="11" height="11" rx="2" fill="none" stroke="currentColor" stroke-width="2"/>'
          '<path d="M15.5 5.5v-.5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v8.5a2 2 0 0 0 2 2h.5" fill="none" stroke="currentColor" stroke-width="2"/></svg>')

def ask_sdk():
    """把 CloudBase 网页工具包放到 site/ 下（文件名带内容哈希），返回在线地址"""
    import hashlib, shutil
    src = os.path.join(Q4, 'tcb_sdk.js')
    h = hashlib.sha1(open(src, 'rb').read()).hexdigest()[:10]
    site = os.path.join(OUT, '..', '..', 'site'); os.makedirs(site, exist_ok=True)
    shutil.copyfile(src, os.path.join(site, h + '.js'))
    return ONLINE + 'site/' + h + '.js'

def ask_page():
    top = (f'<nav class="lessonbar" aria-label="提问区"><a class="btn ghost" href="#home">全季目录</a>{GOHOME}<a class="btn egg" href="#qa">✦ 问题彩蛋</a>'
           f'<span class="pn"><button class="btn share" type="button" data-share="ask">{SHAREIC}分享提问区</button></span></nav>')
    bottom = f'<nav class="lessonbar bottom"><a class="btn ghost" href="#home">全季目录</a>{GOHOME}<a class="btn egg" href="#qa">✦ 问题彩蛋</a></nav>'
    return f'''<div class="lesson" id="ask" data-title="提问区 · 问题彩蛋">
{top}
<section class="askpage" data-env="{ASK_ENV}" data-sdk="{ask_sdk()}" data-admins="{",".join(ASK_ADMINS)}" data-online="{ONLINE}">
  <header class="askhead">
    <p class="eyebrow">问题彩蛋 · 提问区</p>
    <h1>提问区</h1>
    <p class="lead">读学课时有什么疑问，都可以写在这里。所有人都能看到，也可以一起讨论；整理者会挑选问题，做成完整的解答放进“问题彩蛋”。</p>
  </header>
  <div class="askcard tier0">
    <div class="ask-top"><span class="ask-badge" hidden></span><p class="ask-hi">第一次来提问？没有“傻问题”，只有愿意追问的心。</p><p class="ask-stats" hidden></p></div>
    <label class="ask-f"><span>你的称呼</span><input class="ask-name" maxlength="16" autocomplete="nickname" placeholder="随便起个名字，比如：杭州的小羊"></label>
    <label class="ask-f"><span>你的问题</span><textarea class="ask-text" maxlength="500" rows="4" placeholder="比如：为什么说罪使人与上帝隔绝？"></textarea><em class="ask-count">0 / 500</em></label>
    <div class="ask-opts">
      <label class="ask-sw"><input type="checkbox" class="ask-allow" checked><span class="sw" aria-hidden="true"></span><span>允许大家回复</span></label>
      <p class="ask-loc">{PINIC}<span class="ask-locv">正在识别地区…</span><button type="button" class="ask-locedit">修改</button></p>
    </div>
    <p class="ask-note">发出后所有人都能看到。请不要写电话、住址等个人信息。</p>
    <button class="btn solid ask-send" type="button">提交问题</button>
    <p class="ask-msg" aria-live="polite"></p>
  </div>
  <div class="asklist">
    <div class="ask-bar">
      <h2>大家的问题 <small class="ask-n"></small></h2>
      <button class="btn ask-copyall" type="button">{COPYIC}一键复制全部</button>
    </div>
    <p class="ask-filter"><button class="chip on" type="button" data-f="all">全部</button><button class="chip" type="button" data-f="mine">我的提问</button><button class="chip" type="button" data-f="answered">有管理员回答</button><button class="chip ask-refresh" type="button">↻ 刷新</button></p>
    <div class="ask-items"><p class="ask-empty">正在连接提问区…</p></div>
    <p class="ask-morep"><button class="btn ask-more" type="button" hidden>加载更多</button></p>
  </div>
  <p class="ask-admin"><button type="button" class="ask-adminbtn">我是整理者</button></p>
</section>
{bottom}
</div>'''

def qa_pages():
    items = qa_data.ITEMS
    cards = ''.join(f'''<a class="qcard" href="#{it['id']}">
  <span class="spark" aria-hidden="true">✦</span>
  <span class="qt"><span class="qno">问答 {it['no']:02d}</span><span class="qday">第{it['lesson']}课 · {it['dayname']}</span></span>
  <span class="qq">{it['q']}</span>
  <span class="qs">{it['sub']}</span>
  <span class="qx">{it['teaser']}</span>
  <span class="qgo">阅读解答 →</span>
</a>''' for it in items)
    out = [f'''<div class="lesson" id="qa" data-title="问题彩蛋 · 预言的恩赐">
<nav class="lessonbar" aria-label="问题彩蛋"><a class="btn ghost" href="#home">全季目录</a>{GOHOME}</nav>
<section class="qahome">
  <p class="eyebrow">研经问答 · 陆续更新</p>
  <h1>问题彩蛋</h1>
  <p class="lead">学课中常遇到的问题，结合全本圣经和怀爱伦著作逐一深入解答。点开任意一题即可阅读；每篇都有 PDF 版，方便转发。</p>
  <p class="qshare qshare-l"><button class="btn share" type="button" data-share="qa">{SHAREIC}分享问题彩蛋</button></p>
  <div class="qcards">{cards}<div class="qsoon"><span>✦</span>更多问题陆续加入</div></div>
  <a class="askentry" href="#ask"><span class="ae-ic" aria-hidden="true">?</span><span class="ae-t"><b>我也有问题想问</b><small>进入提问区：写下你的问题，大家一起讨论；整理者会挑选问题做成完整解答</small></span><span class="ae-go">去提问 →</span></a>
</section>
<nav class="lessonbar bottom"><a class="btn ghost" href="#home">全季目录</a>{GOHOME}</nav>
</div>''']
    for i, it in enumerate(items):
        prev = f'<a class="btn ghost" href="#{items[i-1]["id"]}">← 上一题</a>' if i > 0 else ''
        nxt = f'<a class="btn ghost" href="#{items[i+1]["id"]}">下一题 →</a>' if i + 1 < len(items) else ''
        pdf = ONLINE + 'lessons/2026-Q4/qa/' + urllib.parse.quote(it['pdf'])
        tail = (f'<p class="btnrow qaend"><button class="btn share" type="button" data-share="{it["id"]}">{SHAREIC}分享这篇</button><a class="btn solid" href="{pdf}" target="_blank" rel="noopener">下载 PDF 版（方便转发）</a>'
                f'<a class="btn" href="#l{it["lesson"]}-{it["day"]}">回到第{it["lesson"]}课 · {it["dayname"]}</a>'
                f'<a class="btn egg" href="#qa">✦ 更多问题彩蛋</a></p>')
        top = f'<nav class="lessonbar" aria-label="问题彩蛋"><a class="btn ghost" href="#home">全季目录</a>{GOHOME}<a class="btn egg" href="#qa">✦ 问题彩蛋</a><span class="pn">{prev}{nxt}</span></nav>'
        bottom = f'<nav class="lessonbar bottom"><a class="btn ghost" href="#home">全季目录</a>{GOHOME}<a class="btn egg" href="#qa">✦ 问题彩蛋</a><span class="pn">{prev}{nxt}</span></nav>'
        out.append(f'<div class="lesson" id="{it["id"]}" data-title="{it["q"]} · 问题彩蛋">\n{top}\n{qa_article(it, tail)}\n{bottom}\n</div>')
    return '\n'.join(out)

def build_combined(nos):
    mods = {}; frags = {}
    for no in nos:
        mod = load(no); mods[no] = mod; frags[no] = prefix(render_lesson(mod), no)
    titles = {0: '本季导言', **{n: lesson_title(mods[n]) for n in nos}}
    frags[0] = prefix(intro_frag(), 0).replace('#l0-NEXTLESSON', '#l1')
    for it in qa_data.ITEMS:          # 在对应那一天的标题区放一个“问题彩蛋”入口
        n = it['lesson']
        if n in frags:
            i = frags[n].find(f'id="l{n}-{it["day"]}"'); j = frags[n].find('</header>', i)
            assert i >= 0 and j > i, it['id']
            frags[n] = frags[n][:j] + f'  <p class="qchip"><a href="#{it["id"]}">✦ 问题彩蛋：{it["q"]}</a></p>\n  ' + frags[n][j:]
    nos = [0] + list(nos)
    opts = ''.join(f'<option value="{n}">{lab(n)} {titles[n]}</option>' for n in nos)
    cards = ['''<a class="card intro" href="#l0">
  <span class="top"><span class="no">导言</span></span>
  <span class="ct">预言的恩赐</span>
  <span class="cd">本季开篇 · 导言原文与全季总览</span>
  <span class="cg">''' + INTRO_GIST + '''</span>
</a>''']
    for n in nos[1:]:
        ds = dates_for(n)
        cards.append(f'''<a class="card" href="#l{n}" data-start="{ds[0].isoformat()}">
  <span class="top"><span class="no">第{n}课</span><span class="wk" hidden>✦ 本周学课</span><span class="ctag" hidden>今天下午开始新课</span></span>
  <i class="spk s1" aria-hidden="true">✦</i><i class="spk s2" aria-hidden="true">✦</i><i class="spk s3" aria-hidden="true">✦</i><i class="spk s4" aria-hidden="true">✦</i>
  <span class="ct">{lesson_title(mods[n])}</span>
  <span class="cd">{md(ds[0])}—{md(ds[6])} · {md(ds[0] + datetime.timedelta(days=7))}安息日</span>
  <span class="cg">{lesson_gist(mods[n])}</span>
</a>''')
    home = f'''<section id="home" class="home">
  <p class="eyebrow">安息日学研经指引 · 2026年第4季（10—12月）</p>
  <h1>预言的恩赐</h1>
  <p class="hsub">全季逐课研读 · 每课含逐日解读与学课原文</p>
  <p class="credit">整理制作 · Ethan（HangZhou_XG）</p>
  <div class="hlead">
    <p>罪关上了伊甸园的门，却没有让上帝就此沉默。祂在园中呼唤“你在哪里？”<span class="ref">（创3:9）</span>，先知们一个接一个回答“我在这里，请差遣我！”<span class="ref">（赛6:8）</span>。本季十三课，讲的就是这位不肯沉默的上帝：祂借着先知说话，借着圣经存话，借着儿子亲自来说，又借着圣灵一直说到末时。</p>
    <p>点下面任意一课，页面就只显示那一课：先读“解读”，再对照“学课原文”，两排按钮可以随时切换。</p>
  </div>
  <p class="btnrow hbtns"><a class="btn solid" href="#welcome" data-welcome>✦ 回到欢迎页</a><a class="btn" href="#l0">阅读本季导言</a><a class="btn egg" href="#qa">✦ 问题彩蛋</a></p>
  <div class="cards">{"".join(cards)}</div>
  <p class="homeend">{GOHOME.replace('主页', '返回主页（欢迎页）')}</p>
</section>'''
    lessons = []
    for n in nos:
        prev = f'<a class="btn ghost" href="#l{n-1}">← {lab(n-1)}</a>' if n - 1 in nos else ''
        nxt = f'<a class="btn ghost" href="#l{n+1}">{lab(n+1)} →</a>' if n + 1 in nos else ''
        bar = f'''<nav class="lessonbar" aria-label="课程切换">
  <a class="btn ghost" href="#home">全季目录</a>{GOHOME}
  <label class="sel"><span class="vh">切换课次</span><select data-go>{opts.replace(f'value="{n}"', f'value="{n}" selected')}</select></label>
  <span class="pn">{prev}{nxt}</span>
</nav>'''
        bottom = f'<nav class="lessonbar bottom" aria-label="上一课下一课"><a class="btn ghost" href="#home">全季目录</a>{GOHOME}<span class="pn">{prev}{nxt}</span></nav>'
        ptitle = '本季导言' if n == 0 else f'第{n}课《{titles[n]}》'
        lessons.append(f'<div class="lesson" id="l{n}" data-title="{ptitle} · 预言的恩赐">\n{bar}\n{frags[n]}\n{bottom}\n</div>')
    body = welcome.welcome_html(titles) + '\n' + homeui() + '\n' + gift_html() + '\n' + with_bible(home + '\n' + '\n'.join(lessons) + '\n' + qa_pages() + '\n' + ask_page())
    out = shell('预言的恩赐 · 全季研读', '安息日学2026年第4季《预言的恩赐》全季十三课逐日研读与学课原文合集。', body, True)
    tmp = os.path.join(Q4, '_all.html')
    open(tmp, 'w', encoding='utf-8').write(out)
    dst = os.path.join(OUT, 'gift-of-prophecy-all.html')
    subprocess.run(['python3', os.path.join(Q4, 'build.py'), tmp, dst], check=True,
                   stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    return dst

if __name__ == '__main__':
    args = sys.argv[1:]
    avail = sorted(int(f[1:3]) for f in os.listdir(os.path.join(Q4, 'data')) if re.fullmatch(r'l\d\d\.py', f))
    if args == ['all']:
        print(build_single_intro())
        for n in avail: print(build_single(n)[0])
        print(build_combined(avail))
        subprocess.run(['python3', os.path.join(Q4, 'online.py'), os.path.join(OUT, 'gift-of-prophecy-all.html'), os.path.join(OUT, '..', '..')], check=True)
    else:
        for a in args: print(build_single(int(a))[0])
