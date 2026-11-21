#!/usr/bin/env python3
"""生成《“我原谅你”，为什么要用血来写？》专题网页（仓库根目录 blood.html，问题彩蛋 31）。版式、出处、经文都和《基督教两千年家谱》共用（history.py）。
正文在 blood_text.py，图在 blood_svg.py，资料在 history_sources.py（2026-10 用临时任务读取原文核对）。
用法：Q4_WORK=<含 bible/ 的目录> python3 tools/q4/blood.py [输出路径] [--pdf]"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history as H
import topic_tools
import blood_text as T, blood_svg as G

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = ARGS[0] if ARGS else os.path.join(H.ROOT, 'blood.html')
TITLE = '“我原谅你”，为什么要用血来写？'
PDF = '研经问答31-我原谅你为什么要用血来写.pdf'
NO = {cid: i + 1 for i, (_, cid, _, _) in enumerate(T.CHAPTERS)}
NAME = {cid: t for _, cid, t, _ in T.CHAPTERS}
FIGS = {'life': G.life, 'source': G.source, 'three': G.three, 'meet': G.meet, 'charge': G.charge, 'who': G.who, 'five': G.five}
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
<p class="eyebrow">问题彩蛋 · 31 · 十字架</p>
<h1>{TITLE}<small class="h1s">为什么非要流血才能赦罪？上帝不能直接原谅吗？十字架是残忍，还是爱？</small></h1>
<p class="hsub">“若不流血，罪就不得赦免了。”信了十几年的人也常常讲不清为什么；不信的朋友听了，觉得残忍：上帝说一句“我原谅你”不就好了？为什么要一个无辜的人死？父亲让儿子被钉死，算什么爱？这一页以经解经，从那句经文的上下文和原文读起，看圣经怎样讲罪、律法、原谅、公义和慈爱，看旧约的献祭、十字架上发生的事，再把各教会的解释和不同的看法摆出来，一个一个回答。</p>
<div class="answer"><p class="lab">先说结论</p>
<ol class="lineage">{steps}</ol>
<p>下面先把问题摆上桌，再把那句经文读准；然后看罪有多重、律法能不能改、上帝能不能“装作没看见”；再看原谅为什么总有代价、付代价的是谁、十字架是不是“残忍”；接着看公义与慈爱怎样在十字架相遇；再读旧约的献祭这本“画出来的书”；然后看十字架上到底发生了什么；最后回到开头的疑问，以及这对今天的我们有什么意义。“编者的理解”只供参考。</p></div>
<p class="howto"><span>怎样读这一页：</span>点正文里<a class="cite demo" href="#sources">1</a>这样的小数字，可以看到出处；点{ref("answer")}之类的蓝色字，可以跳到相关的章节；点经文出处可以看原文；右下角的“目录”按钮随时可以跳到任何一章。</p>
</header>
<nav class="toc-in" aria-label="目录"><h2>目录</h2>{toc_html}</nav>'''
    main = expand(hero) + ''.join(body)
    main = re.sub(r'\{\{c:(\w+)\}\}', lambda m: cites(m.group(1)), main)
    assert '{{' not in main, re.findall(r'\{\{[^}]*\}\}', main)[:5]
    srcs = f'''<section class="ch" id="sources"><h2><span class="no">✦</span>资料出处</h2>
<p>本页的依据是圣经，经文都用和合本原文，原文据希伯来文、希腊文核对。其他资料有：<b>原始文献</b>（安瑟伦《上帝为何成为人》、加尔文《基督教要义》、《天主教教理》、犹太教《密释纳》和《拉比拿单论先贤》）、<b>百科资料</b>（各种赎罪论、查尔克引起的争论、圣殿被毁后的犹太传统）、<b>怀爱伦著作</b>（《历代愿望》第1、78、79章，《拾级就主》第1、3章，《先祖与先知》第4、5章，只作补充，按英文原著页码引用）。外文引文的中文都是编者所译。</p>
<p class="note2">网页资料和怀爱伦著作的引文都在 2026 年 10 月逐一读取原文核对过；部分外国网站在中国大陆可能打不开。点 ↑ 回到正文引用的位置。</p>
{cites.html()}
</section>'''
    words = len(re.sub(r'<[^>]+>|\s', '', main))
    mins = round(words / 450 / 5) * 5
    main = main.replace('</h1>', f'</h1><p class="meta">约 {words / 10000:.1f} 万字 · 细读约 {mins} 分钟 · {len(T.CHAPTERS)} 章 · {len(cites.order)} 条资料出处</p>', 1)
    css = H.CSS
    H.CSS = css + EXTRA_CSS
    try:
        tools = topic_tools.build(id='qa32', title=TITLE, page='blood.html', pdf=PDF, quiz=T.QUIZ, ref=ref)
        return H.doc(TITLE, '为什么非要流血才能赦罪？上帝不能直接原谅吗？来9:22“差不多”与 haimatekchysia；利17:11 血就是生命；不用血的赎罪（利5:11-13）；罪是离开生命的源头；律法能不能改；出34:6-7 赦免与“万不以有罪的为无罪”；太18章免债与原谅的代价；林后5:19 上帝在基督里；约壹4:10 挽回祭；约10:18 自愿舍命；“宇宙级的虐待儿童”的批评与回应；罗3:21-26 hilastērion 施恩座；撒但的控告；献祭的方向与申12:31、耶7:31；赎罪日与逾越节；十字架的五幅画面；赎价、满足、道德感化、刑罚代替、政府说；《天主教教理》613—616；犹太传统；浪子的比喻；十字架以前的赦免', main, srcs, toc_html, cites, tools)
    finally:
        H.CSS = css


if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
    if '--pdf' in sys.argv:          # 同时重做 PDF 学习版（内容改了就要重做）
        topic_tools.make_pdf(OUT, PDF, TITLE)
