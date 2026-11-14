#!/usr/bin/env python3
"""生成《我的祖先从没听过耶稣，他们会怎样？》专题网页（仓库根目录 unheard.html，问题彩蛋 34）。版式、出处、经文都和《基督教两千年家谱》共用（history.py）。
正文在 unheard_text.py，图在 unheard_svg.py，资料在 history_sources.py（2026-10 用临时任务读取原文核对）。
用法：Q4_WORK=<含 bible/ 的目录> python3 tools/q4/unheard.py [输出路径] [--pdf]"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history as H
import topic_tools
import unheard_text as T, unheard_svg as G

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = ARGS[0] if ARGS else os.path.join(H.ROOT, 'unheard.html')
TITLE = '我的祖先从没听过耶稣，他们会怎样？'
PDF = '研经问答34-我的祖先从没听过耶稣他们会怎样.pdf'
NO = {cid: i + 1 for i, (_, cid, _, _) in enumerate(T.CHAPTERS)}
NAME = {cid: t for _, cid, t, _ in T.CHAPTERS}
FIGS = {'heart': G.heart, 'sleep': G.sleep, 'light': G.light, 'outside': G.outside, 'cross': G.cross, 'views': G.views, 'china': G.china, 'ditch': G.ditch}
EXTRA_CSS = r'''
.poem p[lang=it]{font-size:.92rem;line-height:1.75;font-style:italic;margin-top:.6em}
/* “深入一点”小框：正文读起来不被打断，想深挖的人点开看（2026-10-25 用户要文章更适合口述阅读） */
.deep{margin:1em 0 1.2em;border:1px solid var(--rule);border-radius:12px;background:var(--surface)}
.deep>summary{cursor:pointer;padding:10px 14px;font-size:.92rem;font-weight:650;color:var(--ink-2);list-style:none}
.deep>summary::-webkit-details-marker{display:none}
.deep>summary::before{content:"＋";display:inline-block;width:1.4em;color:var(--gold)}
.deep[open]>summary::before{content:"－"}
.deep>div{padding:0 14px 6px}
/* 名人诗文（2026-10-23 用户要的：选一些有名的诗文作补充） */
.poem{margin:1.2em 0;padding:16px 18px 10px;border-radius:14px;border:1px solid var(--rule);border-left:4px solid var(--gold,#B8862B);background:var(--surface)}
.poem figcaption{font-family:var(--serif);font-weight:700;font-size:1.05rem;margin:0 0 .6em;color:var(--ink)}
.poem p{font-family:var(--serif);line-height:1.95;margin:0 0 .9em}
.poem .pcite{font-family:inherit;font-size:.82rem;color:var(--muted);margin:.2em 0 .6em}
.poem details{margin:.4em 0 .4em;border-top:1px dashed var(--rule);padding-top:.5em}
.poem summary{cursor:pointer;font-size:.88rem;color:var(--ink-2)}
.poem details p[lang=en]{font-size:.92rem;line-height:1.75;overflow-wrap:anywhere;margin-top:.6em}
/* 本页表格：只给出处栏不换行（2026-10-25） */
.ch .ntbl td,.ch .ntbl th{width:50%}
.dg .dop{font-size:22px;font-weight:800;fill:var(--ink-2)}
.tblwrap.two-col .dtbl{min-width:0;width:100%}
.dtbl th,.dtbl td{width:50%}
.srcs .sb{overflow-wrap:anywhere;word-break:break-all}
.ch .mini{width:100%}
.ch .mini th{white-space:normal}
.ch .mini th,.ch .mini td{overflow-wrap:anywhere;word-break:break-word}
.ch .mini td small{display:block;font-size:.8em;line-height:1.4;color:var(--muted)}
.tblwrap.two-col .stbl{min-width:0;width:100%}
.stbl th,.stbl td{width:50%}
.hero h1 .h1s{display:block;margin-top:.3em;font-size:.5em;letter-spacing:.04em;color:var(--ink-2)}
.quote.big p{font-size:1.05em;line-height:1.85}
.obj .o{margin:0 0 14px;padding:12px 14px;border:1px solid var(--rule);border-radius:14px;background:var(--surface)}
.obj .o h4{display:flex;gap:10px;align-items:flex-start;margin:0 0 8px;font-size:1rem;line-height:1.5}
.obj .o h4 .ci{flex:none;width:24px;height:24px;border-radius:50%;background:var(--c6);color:#fff;font-size:.8rem;display:grid;place-items:center;margin-top:1px}
.obj .o p{margin:.4em 0}
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
.cause .neg1,.cause .pos1,.cause .step1,.cause .m1,.cause .m2{margin:.3em 0;font-size:.92rem}
.cause .m1{color:var(--c1);font-weight:600}
.cause .m2{color:var(--muted)}
.cause .neg1{color:var(--muted)}
.cause .pos1{color:var(--ink)}
.cause .step1{color:var(--c1);font-weight:600}
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
<p class="eyebrow">问题彩蛋 · 34 · 给慕道朋友</p>
<h1>{TITLE}<small class="h1s">爷爷奶奶走的时候没有信主，他们在哪里？上帝公平吗？我还能做什么？</small></h1>
<p class="hsub">在亲人的灵堂里，有人问你：“你们信耶稣的，是不是说奶奶要下地狱？”慕道的朋友也常问：“照你们说，我们祖宗十八代都完了？”这一篇先听听问这个问题的人心里在想什么，再用圣经一步一步回答：人死了以后在哪里，审判的是谁、按什么标准，从没听过福音的人会怎样；也谈谈历史上的基督徒怎样回答、我们中国人的祖先，以及亲人已经离世或还没信主时，我们可以怎样想、怎样做。</p>
<div class="answer"><p class="lab">先说结论</p>
<ol class="lineage">{steps}</ol>
<p>圣经没有给我们一份“谁得救、谁没有”的名单，但它清楚地告诉我们：审判的那一位是怎样的主。想多了解细节的地方，可以点开“深入一点”的小框。“编者的理解”只供参考。</p></div>
<p class="howto"><span>怎样读这一页：</span>点正文里<a class="cite demo" href="#sources">1</a>这样的小数字，可以看到出处；点{ref("sleep")}之类的蓝色字，可以跳到相关的章节；点经文出处可以看原文；右下角的“目录”按钮随时可以跳到任何一章。</p>
</header>
<nav class="toc-in" aria-label="目录"><h2>目录</h2>{toc_html}</nav>'''
    main = expand(hero) + ''.join(body)
    main = re.sub(r'\{\{c:(\w+)\}\}', lambda m: cites(m.group(1)), main)
    assert '{{' not in main, re.findall(r'\{\{[^}]*\}\}', main)[:5]
    srcs = f'''<section class="ch" id="sources"><h2><span class="no">✦</span>资料出处</h2>
<p>本页的依据是圣经，经文都用和合本原文。另有历史资料（沙勿略的书信、游斯丁《第一护教书》、奥古斯丁《忏悔录》、但丁《神曲》、《威斯敏斯德信条》、天主教会的文件、卫斯理讲章等）、中国古籍（《诗经》《尚书》《论语》，据维基文库）、百科资料、名人名书（路易斯《最后的战役》，惠蒂尔、费伯的诗），以及<b>怀爱伦著作</b>（《历代愿望》《先知与君王》，只作补充，按英文原著页码引用）。外文引文的中文，凡未注明译者的，都是编者所译。</p>
<p class="note2">网页资料和怀爱伦著作的引文都在 2026 年 10 月逐一读取原文核对过；部分外国网站在中国大陆可能打不开。点 ↑ 回到正文引用的位置。</p>
{cites.html()}
</section>'''
    words = len(re.sub(r'<[^>]+>|\s', '', main))
    mins = round(words / 450 / 5) * 5
    main = main.replace('</h1>', f'</h1><p class="meta">约 {words / 10000:.1f} 万字 · 细读约 {mins} 分钟 · {len(T.CHAPTERS)} 章 · {len(cites.order)} 条资料出处</p>', 1)
    css = H.CSS
    H.CSS = css + EXTRA_CSS
    try:
        tools = topic_tools.build(id='qa35', title=TITLE, page='unheard.html', pdf=PDF, quiz=T.QUIZ, ref=ref)
        return H.doc(TITLE, '我的祖先从没听过耶稣，他们会怎样？问这个问题的人心里在想什么（公平、孝道、内疚、害怕）；死了的人像睡了，现在没有受苦（传9:5、约11:11、约5:28-29）；父把审判交给子（约5:22）；亚伯拉罕为所多玛祈求（创18:25）；大自然、良心和照亮每个人的真光（罗1:20、罗2:14-16、约1:9）；按所领受的光审判（路12:48、约9:41、约15:22、徒17:30、约3:19）；圣经里的外人：麦基洗德、叶忒罗、约伯、喇合、路得、乃缦、尼尼微、哥尼流；只有一个名字却不一定先知道这个名字（徒4:12、约8:56、罗3:25）；罗10:14、约3:18、彼前3:19、为死人受洗；五种回答：威斯敏斯德信条10.3—4、梵二《教会宪章》16、天主教教理847—848、卫斯理《论信心》、拉纳、普救论；拉德博德国王、沙勿略与日本信徒的眼泪、游斯丁、但丁灵薄狱、路易斯《最后的战役》；怀爱伦《历代愿望》638、《先知与君王》188—189、371、376—378；《诗经》“皇矣上帝”、利玛窦、理雅各；赛49:12“秦国”；景教碑；孝道与信仰；为亲人哭、不知道的最后时刻、内疚、天上见不到怎么办；惠蒂尔《永恒的良善》；怎样向父母传福音；为什么还要传福音；两边的坑；费伯《上帝的怜悯，宽阔无边》', main, srcs, toc_html, cites, tools)
    finally:
        H.CSS = css


if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
    if '--pdf' in sys.argv:          # 同时重做 PDF 学习版（内容改了就要重做）
        topic_tools.make_pdf(OUT, PDF, TITLE)
