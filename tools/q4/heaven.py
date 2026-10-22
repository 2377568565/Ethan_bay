#!/usr/bin/env python3
"""生成《永远住在天上，会不会很无聊？》专题网页（仓库根目录 heaven.html，问题彩蛋 32）。版式、出处、经文都和《基督教两千年家谱》共用（history.py）。
正文在 heaven_text.py，图在 heaven_svg.py，怀著引文在 heaven_egw.py，资料在 history_sources.py（2026-10 用临时任务读取原文核对）。
用法：Q4_WORK=<含 bible/ 的目录> python3 tools/q4/heaven.py [输出路径] [--pdf]"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history as H
import topic_tools
import heaven_text as T, heaven_svg as G

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = ARGS[0] if ARGS else os.path.join(H.ROOT, 'heaven.html')
TITLE = '永远住在天上，会不会很无聊？'
PDF = '研经问答32-永远住在天上会不会很无聊.pdf'
NO = {cid: i + 1 for i, (_, cid, _, _) in enumerate(T.CHAPTERS)}
NAME = {cid: t for _, cid, t, _ in T.CHAPTERS}
FIGS = {'road': G.road, 'bookend': G.bookend, 'near': G.near, 'cube': G.cube, 'know': G.know, 'keep': G.keep, 'bored': G.bored}
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
<p class="eyebrow">问题彩蛋 · 32 · 永远的家</p>
<h1>{TITLE}<small class="h1s">天堂是什么样子？在那里还认得家人吗？一直唱诗弹琴，不会腻吗？</small></h1>
<p class="hsub">说到天堂，很多人脑子里是云彩、白袍、竖琴和永远的礼拜，心里却有三个不太敢问的问题：那到底是个什么样的地方？先走一步的父母、夭折的孩子、相伴一生的配偶，到时候还认得吗？一万年、十万年地住下去，再好也会腻吧？这一页以经解经，从创世记读到启示录，看圣经怎样描写那个家，看耶稣复活的身体告诉我们什么，看保罗怎样安慰失去亲人的人，再一个一个回答“会不会无聊”。</p>
<div class="answer"><p class="lab">先说结论</p>
<ol class="lineage">{steps}</ol>
<p>下面先看我们心里的天堂图是从哪里来的；再弄清圣经说的天堂在哪里、什么时候；然后读圣经怎样描写那个地方；接着回答会不会认得家人、婚姻和不在那里的亲人；再回答会不会无聊；最后看这和今天的生活有什么关系。“编者的理解”只供参考。</p></div>
<p class="howto"><span>怎样读这一页：</span>点正文里<a class="cite demo" href="#sources">1</a>这样的小数字，可以看到出处；点{ref("reunion")}之类的蓝色字，可以跳到相关的章节；点经文出处可以看原文；右下角的“目录”按钮随时可以跳到任何一章。</p>
</header>
<nav class="toc-in" aria-label="目录"><h2>目录</h2>{toc_html}</nav>'''
    main = expand(hero) + ''.join(body)
    main = re.sub(r'\{\{c:(\w+)\}\}', lambda m: cites(m.group(1)), main)
    assert '{{' not in main, re.findall(r'\{\{[^}]*\}\}', main)[:5]
    srcs = f'''<section class="ch" id="sources"><h2><span class="no">✦</span>资料出处</h2>
<p>本页的依据是圣经，经文都用和合本原文，原文据希伯来文、希腊文核对。其他资料有：<b>原始文献</b>（奥古斯丁《上帝之城》、爱任纽《驳异端》、《天主教教理》、犹太教《塔木德》）、<b>名人名书</b>（路易斯《返璞归真》、切斯特顿《回到正统》、马克·吐温《地球来信》、赖特《惊人的盼望》）、<b>心理学研究</b>（在 PubMed 核对）、<b>百科资料</b>、<b>怀爱伦著作</b>（《善恶之争》第40—42章、《教育论》第27章、《先祖与先知》第2章、《信息选粹》第1卷，只作补充，按英文原著页码引用）。外文引文的中文都是编者所译。</p>
<p class="note2">网页资料和怀爱伦著作的引文都在 2026 年 10 月逐一读取原文核对过；部分外国网站在中国大陆可能打不开。点 ↑ 回到正文引用的位置。</p>
{cites.html()}
</section>'''
    words = len(re.sub(r'<[^>]+>|\s', '', main))
    mins = round(words / 450 / 5) * 5
    main = main.replace('</h1>', f'</h1><p class="meta">约 {words / 10000:.1f} 万字 · 细读约 {mins} 分钟 · {len(T.CHAPTERS)} 章 · {len(cites.order)} 条资料出处</p>', 1)
    css = H.CSS
    H.CSS = css + EXTRA_CSS
    try:
        tools = topic_tools.build(id='qa33', title=TITLE, page='heaven.html', pdf=PDF, quiz=T.QUIZ, ref=ref)
        return H.doc(TITLE, '天堂是什么样子？在那里会认得家人吗？永远会不会无聊？“天”的三种意思与乐园 paradeisos；死了像睡了，主再来时复活；一千年与新天新地的次序；赛65章、罗8章、启21—22章；伊甸与新耶路撒冷的首尾对照；上帝的帐幕在人间 skēnē；圣城像至圣所（王上6:20）、一万二千斯他迪亚；不再有的十一样；父家的住处 monai；林前2:9-10；复活的身体 sōma pneumatikon；门徒怎样认出复活的耶稣；名字长存、林前13:12 epignōsomai；帖前4:13-18“一同被提”；不娶不嫁（太22章）；所爱的人不在那里怎么办；无聊的心理学定义；无限的上帝、弗2:7、赛9:7“加增无穷”；新天新地的工作、人和成长；永远的敬拜与安息日；路易斯、切斯特顿、奥古斯丁；谁能进城；怎样安慰失去亲人的人', main, srcs, toc_html, cites, tools)
    finally:
        H.CSS = css


if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
    if '--pdf' in sys.argv:          # 同时重做 PDF 学习版（内容改了就要重做）
        topic_tools.make_pdf(OUT, PDF, TITLE)
