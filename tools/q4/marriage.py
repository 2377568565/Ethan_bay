#!/usr/bin/env python3
"""生成《婚姻是爱情的坟墓吗？》专题网页（仓库根目录 marriage.html，问题彩蛋 24）。版式、出处、经文都和《基督教两千年家谱》共用（history.py）。
正文在 marriage_text.py，图在 marriage_svg.py，资料在 history_sources.py（医学文献都在 PubMed 核对过摘要和 DOI）。
用法：Q4_WORK=<含 bible/ 的目录> python3 tools/q4/marriage.py [输出路径] [--pdf]"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history as H
import topic_tools
import marriage_text as T, marriage_svg as G

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = ARGS[0] if ARGS else os.path.join(H.ROOT, 'marriage.html')
TITLE = '婚姻是爱情的坟墓吗？'
PDF = '研经问答24-婚姻是爱情的坟墓吗.pdf'
NO = {cid: i + 1 for i, (_, cid, _, _) in enumerate(T.CHAPTERS)}
NAME = {cid: t for _, cid, t, _ in T.CHAPTERS}
FIGS = {'rope': G.rope}
EXTRA_CSS = r'''
.dg .dop{font-size:22px;font-weight:800;fill:var(--ink-2)}
.tblwrap.two-col .dtbl{min-width:0;width:100%}
.dtbl th,.dtbl td{width:50%}
.srcs .sb{overflow-wrap:anywhere;word-break:break-all}
.ch .mini{width:100%}
.ch .mini th{white-space:normal}
.ch .mini th,.ch .mini td{overflow-wrap:anywhere;word-break:break-word}
.ch .mini td small{display:block;font-size:.8em;line-height:1.4;color:var(--muted)}
.ch .ftbl td:first-child{width:22%;white-space:nowrap}
.ch .atbl td:nth-child(2){white-space:nowrap}
.ch .atbl td:first-child{width:30%}
.tblwrap.two-col .stbl{min-width:0;width:100%}
.stbl th,.stbl td{width:50%}
.hero h1 .h1s{display:block;margin-top:.3em;font-size:.5em;letter-spacing:.04em;color:var(--ink-2)}
.quote.big p{font-size:1.05em;line-height:1.85}
.obj .o{margin:0 0 14px;padding:12px 14px;border:1px solid var(--rule);border-radius:14px;background:var(--surface)}
.obj .o h4{display:flex;gap:10px;align-items:flex-start;margin:0 0 8px;font-size:1rem;line-height:1.5}
.obj .o h4 .ci{flex:none;width:24px;height:24px;border-radius:50%;background:var(--c6);color:#fff;font-size:.8rem;display:grid;place-items:center;margin-top:1px}
.obj .o p{margin:.4em 0}
.ch .wtbl td:first-child small{overflow-wrap:normal;word-break:keep-all}
.ch .wtbl td:first-child{white-space:nowrap}
.ch .wtbl td:first-child i{overflow-wrap:normal;word-break:normal}
.ch .wtbl td i{font-style:normal;font-weight:650}
.vlist{padding-left:1.2em}
.vlist li{margin:.35em 0}
.egw{margin:1.2em 0;padding:10px 14px 4px;border-radius:12px;border:1px dashed var(--rule);background:color-mix(in srgb,var(--c4) 6%,transparent)}
.egw .egwn{margin:0 0 6px;font-size:.82rem;color:var(--muted)}
.egw .quote{margin:6px 0 8px}
.sum7{counter-reset:s;list-style:none;padding:0!important}
.sum7 li{counter-increment:s;position:relative;padding:10px 12px 10px 46px!important;margin:0 0 8px!important;background:var(--surface);border:1px solid var(--rule);border-radius:12px}
.sum7 li::before{content:counter(s);position:absolute;left:12px;top:10px;width:24px;height:24px;border-radius:50%;background:var(--c6);color:#fff;font-size:.8rem;font-weight:700;display:grid;place-items:center}

.tblwrap.two-col .ktbl2{min-width:0;width:100%}
.ktbl2 th,.ktbl2 td{width:50%}
.ktbl2 thead th{white-space:normal}
.ch .ktbl td:first-child{width:24%;white-space:nowrap}
.ch .ptbl td:first-child{white-space:nowrap}
.cause .neg1,.cause .pos1,.cause .step1,.cause .m1,.cause .m2{margin:.3em 0;font-size:.92rem}
.cause .m1{color:var(--c1);font-weight:600}
.cause .m2{color:var(--muted)}
.cause .neg1{color:var(--muted)}
.cause .pos1{color:var(--ink)}
.cause .step1{color:var(--c1);font-weight:600}
.ch .ltbl td:first-child{width:32%}
.causes .cause h4{padding-right:30px}
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
<p class="eyebrow">问题彩蛋 · 24 · 婚姻与家庭</p>
<h1>{TITLE}<small class="h1s">上帝设立婚姻的心意，吵架、不信的配偶、离婚、受伤害和单身</small></h1>
<p class="hsub">恋爱时什么都好，结婚后柴米油盐、孩子、老人、房贷，慢慢只剩下吵架和沉默。婚姻只是两个人搭伙过日子吗？吵架怎么办？和不信主的人结婚可以吗？离婚可以吗？在婚姻里受到伤害怎么办？一直单身是不是不完整？我们把经文、研究和各方的看法摆出来。</p>
<div class="answer"><p class="lab">先说结论</p>
<ol class="lineage">{steps}</ol>
<p>下面先看上帝在伊甸园设立婚姻的心意和婚姻的盟约，再看丈夫和妻子怎样彼此顺服、吵架怎么办，然后谈不信的配偶、离婚、受到伤害，最后写给还没结婚和一直单身的人。“编者的理解”只供参考。</p></div>
<p class="howto"><span>怎样读这一页：</span>点正文里<a class="cite demo" href="#sources">1</a>这样的小数字，可以看到出处；点{ref("fight")}之类的蓝色字，可以跳到相关的章节；右下角的“目录”按钮随时可以跳到任何一章。</p>
</header>
<nav class="toc-in" aria-label="目录"><h2>目录</h2>{toc_html}</nav>'''
    main = expand(hero) + ''.join(body)
    main = re.sub(r'\{\{c:(\w+)\}\}', lambda m: cites(m.group(1)), main)
    assert '{{' not in main, re.findall(r'\{\{[^}]*\}\}', main)[:5]
    srcs = f'''<section class="ch" id="sources"><h2><span class="no">✦</span>资料出处</h2>
<p>本页的依据是圣经，经文都用和合本原文。其他资料有两类：<b>研究</b>（婚姻质量与健康、社会关系与寿命、夫妻争吵与伤口愈合，在 PubMed 上核对过摘要，附 DOI 链接）、<b>怀爱伦著作</b>（只作补充，按英文原著页码引用）。外文引文的中文都是编者所译。</p>
<p class="note2">医学文献、网页资料和怀爱伦著作的引文都在 2026 年 10 月逐一核对过；部分外国网站在中国大陆可能打不开。点 ↑ 回到正文引用的位置。</p>
{cites.html()}
</section>'''
    words = len(re.sub(r'<[^>]+>|\s', '', main))
    mins = round(words / 450 / 5) * 5
    main = main.replace('</h1>', f'</h1><p class="meta">约 {words / 10000:.1f} 万字 · 细读约 {mins} 分钟 · {len(T.CHAPTERS)} 章 · {len(cites.order)} 条资料出处</p>', 1)
    css = H.CSS
    H.CSS = css + EXTRA_CSS
    try:
        tools = topic_tools.build(id='qa25', title=TITLE, page='marriage.html', pdf=PDF, quiz=T.QUIZ, ref=ref)
        return H.doc(TITLE, '婚姻是爱情的坟墓吗？创2:18、24 离开连合成为一体、玛2:14-16 盟约、弗5:21-33 彼此顺服、吵架怎么办（夫妻争吵与伤口愈合研究、婚姻质量与健康）、三股合成的绳子、不要同负一轭、离婚的几种看法、受到伤害时安全第一、单身也是恩赐', main, srcs, toc_html, cites, tools)
    finally:
        H.CSS = css


if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
    if '--pdf' in sys.argv:          # 同时重做 PDF 学习版（内容改了就要重做）
        topic_tools.make_pdf(OUT, PDF, TITLE)
