#!/usr/bin/env python3
"""生成问题彩蛋《为什么基督徒不吃“不洁净的食物”，比如猪肉、虾？》（仓库根目录 cleanfood.html）。
面向慕道友，结合圣经全线脉络、新约难解经文客观并列对照、PubMed 医学/生态文献与怀爱伦著作，讲清“谁不吃、为什么、得救靠什么、生活怎么办”。
用法：Q4_WORK=<含 bible/ 的目录> python tools/q4/cleanfood.py [--pdf]"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history as H
import cleanfood_text as T
import cleanfood_svg as G
import topic_tools

OUT = os.path.join(H.ROOT, 'cleanfood.html')
TITLE = '为什么基督徒不吃“不洁净的食物”，比如猪肉、虾？'
PDF = '研经问答35-为什么基督徒不吃不洁净的食物.pdf'

FIGS = {
    'diet_map': G.diet_map,
    'bib_arc': G.bib_arc,
    'eco_risk': G.eco_risk,
    'table_wisdom': G.table_wisdom,
}

NO = {cid: i + 1 for i, (_, cid, _, _) in enumerate(T.CHAPTERS)}
NAMES = {cid: title for _, cid, title, _ in T.CHAPTERS}

EXTRA_CSS = r'''
.h1s{display:block;font-size:.66em;font-weight:700;margin-top:4px;color:var(--ink-2)}
.deep{margin:1em 0 1.2em;border:1px solid var(--rule);border-radius:12px;background:var(--surface)}
.deep>summary{cursor:pointer;padding:10px 14px;font-size:.92rem;font-weight:650;color:var(--ink-2);list-style:none}
.deep>summary::-webkit-details-marker{display:none}
.deep>summary::before{content:"＋";display:inline-block;width:1.4em;color:var(--gold)}
.deep[open]>summary::before{content:"－"}
.deep>div{padding:0 14px 6px}
.tblwrap.two-col .dtbl,.tblwrap .dtbl{min-width:0;width:100%}
.dtbl th,.dtbl td{width:50%;overflow-wrap:anywhere;word-break:break-word}
.kxy3{display:grid;gap:10px;margin:12px 0 16px}
@media (min-width:640px){.kxy3{grid-template-columns:repeat(3,1fr)}}
@media print{.kxy3{grid-template-columns:repeat(3,1fr)}}
'''


def ref(cid):
    return f'<a class="xref" href="#{cid}">第{NO[cid]}章《{NAMES[cid]}》</a>'


def faq():
    out = ['<div class="faq">']
    for q, a in T.FAQ:
        out.append(f'<details><summary>{q}</summary><div><p>{a}</p></div></details>')
    out.append('</div>')
    return ''.join(out)


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
        n = NO[cid]
        toc.append(f'<li><a href="#{cid}"><span class="tn">{n:02d}</span>{title}</a></li>')
        body.append(f'<section class="ch" id="{cid}"><h2><span class="no">{n:02d}</span>{title}</h2>{expand(txt)}</section>')
    toc.append('</ol></li>')
    toc_html = '<ol class="toc-l">' + ''.join(toc) + '</ol>'
    main = expand(T.HERO) + f'<nav class="toc-in" aria-label="目录"><h2>目录</h2>{toc_html}</nav>' + ''.join(body)
    main = re.sub(r'\{\{c:(\w+)\}\}', lambda m: cites(m.group(1)), main)
    assert '{{' not in main, re.findall(r'\{\{[^}]*\}\}', main)[:5]
    srcs = (f'<section class="ch" id="sources"><h2><span class="no">✦</span>资料出处</h2>'
            f'<p>正文里医学与流行病学数据均经 PubMed 逐条核对原始论文摘要与 DOI（不含任何网络流言）；'
            f'《古兰经》引文经 AlQuran Cloud 所载马坚中译本逐节核对；圣经中文均用《和合本》（上帝版）；'
            f'怀爱伦英文原著按标准英文版页码标示并由编者直译。点出处后“↑”即可回到正文阅读处。</p>'
            f'{cites.html()}</section>')
    words = len(re.sub(r'<[^>]+>|\s', '', main))
    mins = max(5, round(words / 450 / 5) * 5)
    main = main.replace('</h1>', f'</h1><p class="meta">约 {words / 10000:.1f} 万字 · 细读约 {mins} 分钟 · {len(T.CHAPTERS)} 章 · {len(cites.order)} 条资料出处</p>', 1)
    css = H.CSS
    H.CSS = css + EXTRA_CSS
    try:
        tools = topic_tools.build(id='qa36', title=TITLE, page='cleanfood.html', pdf=PDF, quiz=T.QUIZ, ref=ref)
        return H.doc(TITLE, '为什么基督徒不吃“不洁净的食物”，比如猪肉、虾？分清犹太教、伊斯兰教与复临健康原则；从挪亚创7:2、利未记11章到新约可7:19、徒10:28与罗马书14章；结合PubMed实证医学拆解伪科学并阐明生态、寄生虫、生物毒素、慢病与餐桌相处之道。', main, srcs, toc_html, cites, tools)
    finally:
        H.CSS = css


if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
    if '--pdf' in sys.argv:
        topic_tools.make_pdf(OUT, PDF, TITLE)
