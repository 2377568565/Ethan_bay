#!/usr/bin/env python3
"""生成健康栏目 10《肺结节与肺癌》（仓库根目录 lung.html）。版式、出处、经文和问题彩蛋专题页共用（history.py），栏目设为“健康”。
正文在 lung_text.py，图在 lung_svg.py，资料在 history_sources.py 的 LC（医学文献都在 PubMed 核对过摘要和 DOI）。
用法：python3 tools/q4/lung.py [输出路径] [--pdf]"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history as H
import topic_tools
import health_data
import lung_text as T, lung_svg as G

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = ARGS[0] if ARGS else os.path.join(H.ROOT, 'lung.html')
IT = next(x for x in health_data.ITEMS if x['url'] == 'lung.html')
TITLE = IT['q']
PDF = '健康10-肺结节与肺癌.pdf'
NO = {cid: i + 1 for i, (_, cid, _, _) in enumerate(T.CHAPTERS)}
NAME = {cid: t for _, cid, t, _ in T.CHAPTERS}
FIGS = {k: getattr(G, k) for k in ('china', 'types', 'egfr', 'seed', 'nodules', 'overdx', 'quitage', 'survivor', 'betacar', 'kitchen', 'lines', 'screen', 'ages')}
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
                    for u in ('stomach.html', 'mi.html', 'stroke.html') if u in hb)
    cards += ''.join(f'<a class="relc" href="{u}"><span class="reln">问题彩蛋 {by[u]["no"]:02d}</span><b>{by[u]["q"]}</b><small>{by[u].get("sub", "")}</small></a>'
                     for u in ('health.html', 'joy.html') if u in by)
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
<p class="eyebrow">健康 · 10 · {IT["cat"]}</p>
<h1>{TITLE}<small class="h1s">{IT["sub"]}</small></h1>
<p class="hsub">很多人体检查出“肺结节”，心里七上八下：是不是肺癌？要不要开刀？很多不吸烟的女性也得了肺癌，这是为什么？吸烟的人得的肺癌和不吸烟的人得的，是不是一种病？九十多岁还抽烟的老人，说明抽烟不要紧吗？这一篇先摆中国的数据，再讲原理——肺癌不是一种病，吸烟“弄坏基因”，空气污染“唤醒坏细胞”；然后讲肺结节怎样看、怎样随访；最后用大部分篇幅，分<b>吸烟</b>和<b>不吸烟</b>两条线讲<b>一级预防</b>，再讲谁该做低剂量 CT。</p>
<div class="answer"><p class="lab">先说结论</p>
<ol class="lineage">{steps}</ol>
<p>下面先讲数据和原理，再讲肺结节，然后用大部分篇幅分两条线讲一级预防，最后讲筛查和确诊以后。医学研究都在 PubMed 上核对过摘要；“编者的理解”只供参考。<b>本篇不能代替医生的诊断和处方，换药、停药一定先问医生。</b></p></div>
<p class="howto"><span>怎样读这一页：</span>点正文里<a class="cite demo" href="#sources">1</a>这样的小数字，可以看到出处；点{ref("ggo")}之类的蓝色字，可以跳到相关的章节；右下角的“目录”按钮随时可以跳到任何一章。</p>
</header>
<nav class="toc-in" aria-label="目录"><h2>目录</h2>{toc_html}</nav>'''
    main = expand(hero) + ''.join(body)
    main = re.sub(r'\{\{c:(\w+)\}\}', lambda m: cites(m.group(1)), main)
    assert '{{' not in main, re.findall(r'\{\{[^}]*\}\}', main)[:5]
    srcs = f'''<section class="ch" id="sources"><h2><span class="no">✦</span>资料出处</h2>
<p>本页引用的医学研究和指南，都在 PubMed（美国国家医学图书馆的文献库）上核对过摘要，附 DOI 或 PubMed 链接；本页只转述摘要和指南里的结论，数字以原文为准。外文引文的中文都是编者所译。经文用和合本。</p>
<p class="note2">资料在 2026 年 11 月逐一核对过；部分外国网站在中国大陆可能打不开。点 ↑ 回到正文引用的位置。</p>
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
        return H.doc(TITLE, '肺结节与肺癌：中国的数据、男女来路不同、鳞癌小细胞癌腺癌、不吸烟者肺癌的基因、EGFR、PM2.5 唤醒突变细胞、磨玻璃结节怎样随访、过度诊断、戒烟的年数和心情体重、戒烟药、电子烟、水烟、幸存者偏差、β-胡萝卜素、二手烟和口罩、厨房油烟和通风、宣威改炉、氡、空气净化器、家族史、低剂量 CT 筛查（都在 PubMed 核对过）', main, srcs, toc_html, cites, tools, col)
    finally:
        H.CSS = css


if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
    if '--pdf' in sys.argv:
        topic_tools.make_pdf(OUT, PDF, TITLE, '健康')
