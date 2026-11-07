#!/usr/bin/env python3
"""生成《耶稣是人还是神？》补充问答网页（仓库根目录 jesus-qa.html）。版式、出处、经文和原文页（jesus.py）、家谱页共用 history.py。
正文在 jesus2_text.py，两张图在 jesus2_svg.py，资料在 history_sources.py。原文页 jesus.html 不受影响。
用法：Q4_WORK=<含 bible/ 的目录> python3 tools/q4/jesus2.py [输出路径]"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history as H
import jesus as J
import jesus2_text as T, jesus2_svg as G

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H.ROOT, 'jesus-qa.html')
TITLE = '耶稣是人还是神？补充问答'
QS = [(p, cid, q) for p, cid, q, _, _ in T.Q] + [(6, 'end', '结语：七句话串起来')]
NO = {cid: i + 1 for i, (_, cid, _) in enumerate(QS)}
FIGS = {'scale': G.scale, 'path': G.path}
EXTRA_CSS = r'''
.qa-short{border-left:4px solid var(--c6)}
.qa-short .lab{color:var(--c6)}
.qa-short p:last-child{font-weight:600}
.views{display:grid;gap:12px;margin:12px 0 16px}
.vw{background:var(--surface);border:1px solid var(--rule);border-left:5px solid var(--c);border-radius:14px;padding:12px 14px 4px}
.vw p{font-size:.95rem}
.vh{font-weight:700;font-size:1rem!important;line-height:1.45}
.vh span{display:inline-block;font-size:.72rem;font-weight:700;color:#fff;background:var(--c);border-radius:999px;padding:1px 8px;margin-right:6px;vertical-align:2px}
.score td:not(:first-child),.score th:not(:first-child){text-align:center}
.mini td.sy{color:#2f8f57;font-weight:800}
.mini td.sm{color:var(--gold);font-weight:800}
.mini td.sn{color:#cf4a43;font-weight:800}
.score tr.tot td{font-weight:700;font-size:.85em;background:var(--paper)}
.dg .sbeam{fill:none;stroke:var(--ink);stroke-width:2.4;stroke-linecap:round}
.dg .sbeam.f3,.dg .sbeam.f5,.dg .sbeam.f6{stroke:var(--c);stroke-width:3.2}
.dg .spiv{fill:var(--surface);stroke:var(--ink);stroke-width:1.6}
.dg .sline{stroke:var(--muted);stroke-width:1.2}
.dg .span{fill:var(--surface);stroke:var(--ink);stroke-width:1.4}
.dg .sw{fill:var(--c3)}
.dg .sarr{fill:none;stroke:var(--c3);stroke-width:1.8;stroke-dasharray:4 3}
.dg .sarr.up{stroke:var(--c5);stroke-dasharray:none}
.dg .jdash2{fill:none;stroke:var(--c6);stroke-width:1.6;stroke-dasharray:5 4}
.endlink{margin-top:14px}
'''


def ref(cid):
    return f'<a class="xref" href="#{cid}">第 {NO[cid]} 问</a>'


def expand(s):
    s = re.sub(r'\{\{fig:(\w+)\}\}', lambda m: f'<figure class="fig">{FIGS[m.group(1)]()}</figure>', s)
    s = re.sub(r'\{\{v:([^}]+)\}\}', lambda m: H.verse(m.group(1)), s)
    s = re.sub(r'\{\{ref:(\w+)\}\}', lambda m: ref(m.group(1)), s)
    for sym, cls in (('✓', 'sy'), ('△', 'sm'), ('✗', 'sn')):
        s = s.replace(f'<td>{sym}</td>', f'<td class="{cls}">{sym}</td>')
    return s


def page():
    cites = H.Cites()
    toc, body, last = [], [], None
    items = [(p, cid, q, short, txt) for p, cid, q, short, txt in T.Q] + [(6, 'end', '结语：七句话串起来', '', T.END)]
    for part, cid, q, short, txt in items:
        if part != last:
            if last:
                toc.append('</ol></li>')
            pn, pt = T.PARTS[part].split('　')
            toc.append(f'<li><span class="tp">{pn} · {pt}</span><ol>')
            body.append(f'<div class="part" id="part{part}"><span>{pn}</span><b>{pt}</b></div>')
            last = part
        toc.append(f'<li><a href="#{cid}"><span class="tn">{NO[cid]:02d}</span>{q}</a></li>')
        sa = f'<div class="answer qa-short"><p class="lab">简短回答</p><p>{short}</p></div>' if short else ''
        body.append(f'<section class="ch" id="{cid}"><h2><span class="no">{NO[cid]:02d}</span>{q}</h2>{sa}{expand(txt)}</section>')
    toc.append('</ol></li>')
    toc_html = '<ol class="toc-l">' + ''.join(toc) + '</ol>'
    steps = ''.join(f'<li class="f6"><span class="ly">{a}</span><b>{b}</b><small>{c}</small></li>' for a, b, c in T.HERO)
    hero = f'''<header class="hero">
<p class="eyebrow">问题彩蛋 · 《耶稣是人还是神？》补充问答</p>
<h1>{TITLE}</h1>
<p class="hsub">读完《耶稣是人还是神？》以后提出的追问：“犯罪的倾向”到底是什么？耶稣为什么没有？这公平吗？我们重生以后呢？客西马尼园的祷告又说明了什么？</p>
<div class="answer"><p class="lab">先说结论</p>
<ol class="lineage">{steps}</ol>
<p>每一题先给“简短回答”，再用圣经和怀爱伦原文详细解答。有不同理解的地方，把各种说法和依据客观摆出来，判断留给读者；{ref("eval")}另附编者的评估。</p></div>
<p class="howto"><span>怎样读这一页：</span>建议先读原文<a class="xref" href="jesus.html">《耶稣是人还是神？》</a>。点正文里<a class="cite demo" href="#sources">1</a>这样的小数字可以看到出处；右下角的“目录”按钮随时可以跳到任何一题。</p>
</header>
<nav class="toc-in" aria-label="目录"><h2>目录</h2>{toc_html}</nav>'''
    main = expand(hero) + ''.join(body)
    main = re.sub(r'\{\{c:(\w+)\}\}', lambda m: cites(m.group(1)), main)
    assert '{{' not in main, re.findall(r'\{\{[^}]*\}\}', main)[:5]
    srcs = f'''<section class="ch" id="sources"><h2><span class="no">✦</span>资料出处</h2>
<p>本页的核心依据是圣经，经文都用和合本原文。怀爱伦著作按英文原著页码或原刊日期引用，中文为编者所译；凡是标了网址的，都在 2026 年 10 月打开原文或原刊扫描本核对过，其余的据书中原文或可靠的原文汇编核对。</p>
<p class="note2">部分外国网站在中国大陆可能打不开。点 ↑ 回到正文引用的位置。</p>
{cites.html()}
</section>'''
    words = len(re.sub(r'<[^>]+>|\s', '', main))
    mins = round(words / 450 / 5) * 5
    main = main.replace('</h1>', f'</h1><p class="meta">约 {words / 10000:.1f} 万字 · 细读约 {mins} 分钟 · {len(T.Q)} 问 · {len(cites.order)} 条资料出处</p>', 1)
    css = H.CSS
    H.CSS = css + J.EXTRA_CSS + EXTRA_CSS
    try:
        return H.doc(TITLE, '读完《耶稣是人还是神？》以后的追问：犯罪的倾向是什么、耶稣为什么没有、公平吗、重生以后倾向会不会被移开、客西马尼园的祷告；各种说法客观对照，并附编者评估。', main, srcs, toc_html, cites)
    finally:
        H.CSS = css


if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
