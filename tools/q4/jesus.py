#!/usr/bin/env python3
"""生成《耶稣是人还是神？》专题网页（仓库根目录 jesus.html）。版式、出处、经文都和《基督教两千年家谱》共用（history.py）。
正文在 jesus_text.py，三张图在 jesus_svg.py，资料在 history_sources.py。
用法：Q4_WORK=<含 bible/ 的目录> python3 tools/q4/jesus.py [输出路径]"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history as H
import topic_tools
import jesus_text as T, jesus_svg as G

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = ARGS[0] if ARGS else os.path.join(H.ROOT, 'jesus.html')
TITLE = '耶稣是人还是神？'
NO = {cid: i + 1 for i, (_, cid, _, _) in enumerate(T.CHAPTERS)}
NAME = {cid: t for _, cid, t, _ in T.CHAPTERS}
FIGS = {'chalcedon': G.chalcedon, 'power': G.power, 'qod': G.qod}
EXTRA_CSS = r'''
.dg .jsep{stroke:#fff;stroke-width:1.5;stroke-dasharray:3 4;opacity:.7}
.dg .jone{fill:var(--surface);stroke:var(--ink);stroke-width:1.4}
.dg .jx{font-size:12px;font-weight:800;fill:var(--c6)}
.dg .jdash{fill:none;stroke:var(--muted);stroke-width:1.4;stroke-dasharray:5 4}
.tblwrap.two-col .jtbl{min-width:0;width:100%}
.srcs .sb{overflow-wrap:anywhere;word-break:break-all}
.ch .mini td small{display:block;font-size:.76em;line-height:1.35;color:var(--muted);overflow-wrap:normal;word-break:normal;white-space:normal}
.ch .mini{width:100%}
.ch .mini th{white-space:normal}
.ch .mini th,.ch .mini td{overflow-wrap:anywhere;word-break:break-word}
.jtbl th,.jtbl td{width:50%}
.sum7{counter-reset:s;list-style:none;padding:0!important}
.sum7 li{counter-increment:s;position:relative;padding:10px 12px 10px 46px!important;margin:0 0 8px!important;background:var(--surface);border:1px solid var(--rule);border-radius:12px}
.sum7 li::before{content:counter(s);position:absolute;left:12px;top:10px;width:24px;height:24px;border-radius:50%;background:var(--c6);color:#fff;font-size:.8rem;font-weight:700;display:grid;place-items:center}
'''


def ref(cid):
    return f'<a class="xref" href="#{cid}">第 {NO[cid]} 章《{NAME[cid]}》</a>'


def faq():
    return '<div class="faq">' + ''.join(f'<details><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in T.FAQ) + '</div>'


def expand(s):
    s = re.sub(r'\{\{fig:(\w+)\}\}', lambda m: f'<figure class="fig">{FIGS[m.group(1)]()}</figure>', s)
    s = s.replace('{{faq}}', faq())
    s = re.sub(r'\{\{v:([^}]+)\}\}', lambda m: H.verse(m.group(1)), s)
    s = re.sub(r'\{\{ref:(\w+)\}\}', lambda m: ref(m.group(1)), s)
    return s


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
    steps = ''.join(f'<li class="f6"><span class="ly">{a}</span><b>{b}</b><small>{c}</small></li>' for a, b, c in T.HERO)
    hero = f'''<header class="hero">
<p class="eyebrow">问题彩蛋 · 第4课星期日《作为先知的耶稣》延伸阅读</p>
<h1>{TITLE}</h1>
<p class="hsub">耶稣既有神性，又有人性——那祂对抗试探的能力岂不是比我们强？祂还能作我们的榜样吗？</p>
<div class="answer"><p class="lab">先说结论</p>
<ol class="lineage">{steps}</ol>
<p>下面按“祂是谁 → 神性有没有帮祂 → 这对我们意味着什么”的顺序，一步一步用圣经讲清楚。怀爱伦著作的引文都注明了英文原著页码，点小数字就能看到出处。</p></div>
<p class="howto"><span>怎样读这一页：</span>点正文里<a class="cite demo" href="#sources">1</a>这样的小数字，可以看到出处；点{ref("empty")}之类的蓝色字，可以跳到相关的章节；右下角的“目录”按钮随时可以跳到任何一章。</p>
</header>
<nav class="toc-in" aria-label="目录"><h2>目录</h2>{toc_html}</nav>'''
    main = expand(hero) + ''.join(body)
    main = re.sub(r'\{\{c:(\w+)\}\}', lambda m: cites(m.group(1)), main)
    assert '{{' not in main, re.findall(r'\{\{[^}]*\}\}', main)[:5]
    srcs = f'''<section class="ch" id="sources"><h2><span class="no">✦</span>资料出处</h2>
<p>本页的核心依据是圣经，经文都用和合本原文。其他资料分三类：<b>原始文献</b>（早期教会的原话）、<b>怀爱伦著作</b>（按英文原著页码引用，中文为编者所译，可以对照各种中译本）、<b>百科全书与官方网站</b>（历史事实和复临教会的正式信仰）。</p>
<p class="note2">网页资料都在 2026 年 10 月逐一核对过网页内容；部分外国网站在中国大陆可能打不开。点 ↑ 回到正文引用的位置。</p>
{cites.html()}
</section>'''
    words = len(re.sub(r'<[^>]+>|\s', '', main))
    mins = round(words / 450 / 5) * 5
    main = main.replace('</h1>', f'</h1><p class="meta">约 {words / 10000:.1f} 万字 · 细读约 {mins} 分钟 · {len(T.CHAPTERS)} 章 · {len(cites.order)} 条资料出处</p>', 1)
    css = H.CSS
    H.CSS = css + EXTRA_CSS
    try:
        tools = topic_tools.build(id='qa4', title=TITLE, page='jesus.html', pdf='研经问答04-耶稣是人还是神.pdf', quiz=T.QUIZ, ref=ref)
        return H.doc(TITLE, '耶稣既是神又是人，祂对抗试探岂不是比我们容易？用圣经一步一步讲清楚：一位两性、虚己、旷野的试探、神迹的来源，以及祂为什么既是榜样又是救主；并讲述复临教会 1955—1957 年《教义问答》的历史。', main, srcs, toc_html, cites, tools)
    finally:
        H.CSS = css


if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
    if '--pdf' in sys.argv:          # 同时重做 PDF 学习版（内容改了就要重做）
        import topic_tools
        topic_tools.make_pdf(OUT, '研经问答04-耶稣是人还是神.pdf', TITLE)
