#!/usr/bin/env python3
"""生成健康栏目 07《白内障》（仓库根目录 cataract.html）。版式、出处、经文和问题彩蛋专题页共用（history.py），栏目设为“健康”。
正文在 cataract_text.py，图在 cataract_svg.py，资料在 history_sources.py 的 CT（医学文献都在 PubMed 核对过摘要和 DOI）。
用法：python3 tools/q4/cataract.py [输出路径] [--pdf]"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history as H
import topic_tools
import health_data
import cataract_text as T, cataract_svg as G

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = ARGS[0] if ARGS else os.path.join(H.ROOT, 'cataract.html')
IT = next(x for x in health_data.ITEMS if x['url'] == 'cataract.html')
TITLE = IT['q']
PDF = '健康07-白内障.pdf'
NO = {cid: i + 1 for i, (_, cid, _, _) in enumerate(T.CHAPTERS)}
NAME = {cid: t for _, cid, t, _ in T.CHAPTERS}
FIGS = {k: getattr(G, k) for k in ('eye', 'trend', 'age', 'chinasvc', 'risk', 'levels', 'benefit', 'surgery', 'lens', 'ages')}
FIGS['global'] = G.global_
EXTRA_CSS = r'''
.deep{margin:1em 0 1.2em;border:1px solid var(--rule);border-radius:12px;background:var(--surface)}
.deep>summary{cursor:pointer;padding:10px 14px;font-size:.92rem;font-weight:650;color:var(--ink-2);list-style:none}
.deep>summary::-webkit-details-marker{display:none}
.deep>summary::before{content:"＋";display:inline-block;width:1.4em;color:var(--gold)}
.deep[open]>summary::before{content:"－"}
.deep>div{padding:0 14px 6px}
.box.warn{border-color:color-mix(in srgb,var(--c6) 45%,var(--rule));background:var(--c6-soft)}
.box.warn .lab{color:var(--c6)}
.hero h1 .h1s{display:block;margin-top:.3em;font-size:.5em;letter-spacing:.04em;color:var(--ink-2)}
.dg .ahd{fill:var(--muted)}
.dg .flow{stroke:var(--muted)}
.dg .tnode2.b{font-size:11px;font-weight:700;opacity:1}
.dg .tnode2.s{font-size:9px;font-weight:600}
.dg .cn{stroke-width:1.8}
.ch .ctbl{width:100%}
.ch .ctbl td small{display:block;font-size:.8em;line-height:1.4;color:var(--muted)}
.ch .ctbl td:first-child{width:34%}
.ch .ptbl{width:100%}
.ch .ptbl td:first-child{width:28%;font-weight:650}
.srcs .sb{overflow-wrap:anywhere;word-break:break-all}
.dg .tbig{font-size:34px;font-weight:800;fill:#fff}
.ch .stbl{width:100%}
.ch .stbl td:first-child{width:30%;font-weight:650;min-width:6.5em}
.ch .pull{margin:1.1em 0;padding:.7em 1em;border-left:4px solid var(--gold);background:var(--surface);border-radius:0 10px 10px 0;font-size:1.06rem;font-weight:650;line-height:1.7}
'''


def page_audio(uid):
    """听朗读：录音的位置和每章从第几段开始（tools/q4/tts/health_speech.py）"""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tts'))
    import health_speech
    return health_speech.page_audio(uid)


def ref(cid):
    return f'<a class="xref" href="#{cid}">第 {NO[cid]} 章《{NAME[cid]}》</a>'


def faq():
    return '<div class="faq">' + ''.join(f'<details><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in T.FAQ) + '</div>'


def expand(s):
    s = re.sub(r'\{\{deep:(.*?)\|(.*?</p>)\}\}', lambda m: T.deep(m.group(1), m.group(2)), s, flags=re.S)
    s = re.sub(r'\{\{fig:(\w+)\}\}', lambda m: f'<figure class="fig">{FIGS[m.group(1)]()}</figure>', s)
    s = s.replace('{{faq}}', faq())
    s = re.sub(r'\{\{v:([^}]+)\}\}', lambda m: H.verse(m.group(1)), s)
    s = re.sub(r'\{\{ref:(\w+)\}\}', lambda m: ref(m.group(1)), s)
    return s


def related():
    """页尾“相关阅读”：健康栏目的姊妹篇，和本站讲过身体与心情的问题彩蛋。"""
    import qa_data
    by = {d['url']: d for d in qa_data.ITEMS if d.get('url')}
    hb = {d['url']: d for d in health_data.ITEMS}
    cards = ''.join(f'<a class="relc" href="{u}"><span class="reln">健康 {hb[u]["no"]:02d}</span><b>{hb[u]["q"]}</b><small>{hb[u].get("sub", "")}</small></a>'
                    for u in ('diabetes.html', 'osteo.html') if u in hb)
    cards += ''.join(f'<a class="relc" href="{u}"><span class="reln">问题彩蛋 {by[u]["no"]:02d}</span><b>{by[u]["q"]}</b><small>{by[u].get("sub", "")}</small></a>'
                     for u in ('health.html', 'heaven.html') if u in by)
    return f'<section class="rel" aria-label="相关阅读"><p class="relh">相关阅读</p><div class="relg">{cards}</div></section>' if cards else ''


def page():
    cites = H.Cites()
    toc, body, last = [], [], None
    for part, cid, title, txt in T.CHAPTERS:
        if part != last:
            if last:
                toc.append('</ol></li>')
            pn, pt = T.PARTS[part].split('　')
            toc.append(f'<li><span class="tp">{pn} · {pt}</span><ol>')
            body.append(f'<div class="part" id="part{part}"><span>{pn}</span><b>{pt}</b></div>')
            last = part
        toc.append(f'<li><a href="#{cid}"><span class="tn">{NO[cid]:02d}</span>{title}</a></li>')
        body.append(f'<section class="ch" id="{cid}"><h2><span class="no">{NO[cid]:02d}</span>{title}</h2>{expand(txt)}</section>')
    toc.append('</ol></li>')
    toc_html = '<ol class="toc-l">' + ''.join(toc) + '</ol>'
    steps = ''.join(f'<li class="f1"><span class="ly">{a}</span><b>{b}</b><small>{c}</small></li>' for a, b, c in T.HERO)
    hero = f'''<header class="hero">
<p class="eyebrow">健康 · 07 · {IT["cat"]}</p>
<h1>{TITLE}<small class="h1s">{IT["sub"]}</small></h1>
<p class="hsub">到了七十多岁，眼睛像隔着一层雾，看电视不清楚，晚上看车灯一片白光。这是白内障吗？全世界、全中国有多少人得？能不能预防？眼药水和营养品能不能把它“化掉”？真的要“等熟了”才能做手术吗？手术怎样做、晶体怎样选？这一篇先用照相机的“镜头”讲清楚白内障是什么，再像综述一样把全球和中国的数据画成图，然后把重点放在一级预防、二级预防和治疗上。</p>
<div class="answer"><p class="lab">先说结论</p>
<ol class="lineage">{steps}</ol>
<p>下面先讲白内障是什么、有多常见，再讲为什么会得，然后是一级预防、二级预防和手术治疗。医学研究都在 PubMed 上核对过摘要；“编者的理解”只供参考。<b>本篇不能代替医生的诊断和处方，换药、停药一定先问医生。</b></p></div>
<p class="howto"><span>怎样读这一页：</span>点正文里<a class="cite demo" href="#sources">1</a>这样的小数字，可以看到出处；点{ref("levels")}之类的蓝色字，可以跳到相关的章节；右下角的“目录”按钮随时可以跳到任何一章。</p>
</header>
<nav class="toc-in" aria-label="目录"><h2>目录</h2>{toc_html}</nav>'''
    main = expand(hero) + ''.join(body)
    main = re.sub(r'\{\{c:(\w+)\}\}', lambda m: cites(m.group(1)), main)
    assert '{{' not in main, re.findall(r'\{\{[^}]*\}\}', main)[:5]
    srcs = f'''<section class="ch" id="sources"><h2><span class="no">✦</span>资料出处</h2>
<p>本页引用的医学研究和指南，都在 PubMed（美国国家医学图书馆的文献库）上核对过摘要，附 DOI 或 PubMed 链接；本页只转述摘要和指南里的结论，数字以原文为准。外文引文的中文都是编者所译。经文用和合本。</p>
<p class="note2">资料在 2026 年 10 月逐一核对过；部分外国网站在中国大陆可能打不开。点 ↑ 回到正文引用的位置。</p>
{cites.html()}
</section>'''
    words = len(re.sub(r'<[^>]+>|\s', '', main))
    mins = round(words / 450 / 5) * 5
    main = main.replace('</h1>', f'</h1><p class="meta">约 {words / 10000:.1f} 万字 · 细读约 {mins} 分钟 · {len(T.CHAPTERS)} 章 · {len(cites.order)} 条资料出处</p>', 1)
    css = H.CSS
    H.CSS = css + EXTRA_CSS
    try:
        tools = topic_tools.build(id=IT['id'], title=TITLE, page=IT['url'], pdf=PDF, quiz=T.QUIZ, ref=ref, col='健康')
        col = dict(name='健康', hash='health', foot='健康栏目 · 健康科普，不能代替医生的诊断和处方', related=related(), audio=page_audio(IT['id']))
        return H.doc(TITLE, '白内障：眼睛的镜头为什么变混、全球和中国的数据图、吸烟糖尿病激素紫外线和烧柴煤的烟、一级预防和二级预防、补充剂和眼药水的证据、不必等熟、手术怎样做、飞秒激光和人工晶体怎样选、术后并发症和后发障（都在 PubMed 核对过）', main, srcs, toc_html, cites, tools, col)
    finally:
        H.CSS = css


if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
    if '--pdf' in sys.argv:
        topic_tools.make_pdf(OUT, PDF, TITLE, '健康')
