#!/usr/bin/env python3
"""生成“问题彩蛋 · 经文索引”网页（仓库根目录 qa-index.html，2026-10-23）。
按圣经书卷、章排列；每一章后面是讲过这一章的问题彩蛋编号，点了就打开那一篇。
数据从已经生成好的各篇网页里读（qa_catalog.py），所以要在各专题页生成之后再运行。
用法：Q4_WORK=<含 bible/ 的目录> python3 tools/q4/qa_index.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import history as H
import qa_data, qa_catalog

OUT = os.path.join(H.ROOT, 'qa-index.html')
TITLE = '问题彩蛋 · 经文索引'
CATN = {k: n for k, n, _ in qa_data.CATS}
EXTRA_CSS = r'''
:root{--qc-god:#3A5FC8;--qc-sin:#A8324A;--qc-bible:#B0631C;--qc-law:#8A6A22;--qc-end:#7B4FC4;--qc-heart:#08857C;--qc-life:#546178}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--qc-god:#8FA8F0;--qc-sin:#E08C9A;--qc-bible:#E3A060;--qc-law:#D3B06A;--qc-end:#B79AF0;--qc-heart:#4FC9BE;--qc-life:#A9B4C8}}
:root[data-theme="dark"]{--qc-god:#8FA8F0;--qc-sin:#E08C9A;--qc-bible:#E3A060;--qc-law:#D3B06A;--qc-end:#B79AF0;--qc-heart:#4FC9BE;--qc-life:#A9B4C8}
.bkjump{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0 4px}
.bkjump a{padding:3px 9px;border:1px solid var(--rule);border-radius:999px;font-size:.82rem;color:var(--ink-2);text-decoration:none;background:var(--surface)}
.bk{margin:0 0 18px;scroll-margin-top:64px}
.bk h3{display:flex;align-items:baseline;gap:8px;margin:0 0 4px;padding-bottom:4px;border-bottom:1px solid var(--rule);font-family:var(--serif);font-size:1.1rem}
.bk h3 small{font:400 .76rem/1 var(--sans);color:var(--muted)}
.bkr{display:grid;grid-template-columns:3.6em 1fr;gap:8px;align-items:start;padding:5px 0;border-bottom:1px dashed color-mix(in srgb,var(--rule) 70%,transparent)}
.bkr .c{font:600 .8rem/26px ui-monospace,"SF Mono",Menlo,monospace;color:var(--muted);text-align:right;font-variant-numeric:tabular-nums}
.bkr .ns{display:flex;flex-wrap:wrap;gap:5px}
'''+''.join(f'.k{k}{{--qc:var(--qc-{k})}}' for k, _, _ in qa_data.CATS)+r'''
.bkr .n{display:inline-grid;place-items:center;min-width:30px;height:26px;padding:0 6px;border-radius:7px;border:1.5px solid var(--qc);color:var(--qc);font:700 .8rem/1 ui-monospace,"SF Mono",Menlo,monospace;text-decoration:none;font-variant-numeric:tabular-nums}
.legend{display:grid;gap:2px;margin:6px 0 0;padding:0;list-style:none}
.legend li{display:grid;grid-template-columns:2.6em 1fr;gap:8px;font-size:.88rem;line-height:1.55}
.legend li b{font:700 .82rem/1.55 ui-monospace,"SF Mono",Menlo,monospace;color:var(--qc);text-align:right}
.legend li a{color:var(--ink);text-decoration:none}
.legend li small{color:var(--muted)}
'''


def link(it):
    return it['url'] if it.get('url') else f'./#{it["id"]}'


def page():
    byid = {it['id']: it for it in qa_data.ITEMS}
    idx = qa_catalog.scripture_index()
    ot = [x for x in idx if x[0] < 39]
    nt = [x for x in idx if x[0] >= 39]
    nref = sum(len(c) for _, _, c in idx)

    def books(lst):
        out = []
        for b, name, chs in lst:
            rows = ''.join(
                f'<div class="bkr"><span class="c">{c} 章</span><span class="ns">'
                + ''.join(f'<a class="n k{byid[i]["cat"]}" href="{link(byid[i])}">{byid[i]["no"]:02d}</a>' for i in ids)
                + '</span></div>' for c, ids in chs)
            out.append(f'<section class="bk" id="bk{b}"><h3>{name}<small>{len(chs)} 章</small></h3>{rows}</section>')
        return ''.join(out)

    def jump(lst):
        return '<p class="bkjump">' + ''.join(f'<a href="#bk{b}">{name}</a>' for b, name, _ in lst) + '</p>'

    legend = ''.join(
        f'<li style="--qc:var(--qc-{it["cat"]})"><b>{it["no"]:02d}</b><span><a href="{link(it)}">{it["q"]}</a> <small>· {CATN[it["cat"]]}</small></span></li>'
        for it in sorted(qa_data.ITEMS, key=lambda d: d['no']))
    hero = f'''<header class="hero">
<p class="eyebrow">问题彩蛋 · 经文索引</p>
<h1>经文索引</h1>
<p class="hsub">想知道哪几篇问题彩蛋讲过某一段经文？按圣经书卷和章找到它，后面的数字就是问题彩蛋的编号，点一下就能打开那一篇。数字的颜色表示它属于哪一类。</p>
<p class="meta">{len(qa_data.ITEMS)} 篇问题彩蛋 · {len(idx)} 卷书 · {nref} 章</p>
</header>'''
    main = (hero
            + '<section class="ch" id="ot"><h2><span class="no">01</span>旧约</h2>' + jump(ot) + books(ot) + '</section>'
            + '<section class="ch" id="nt"><h2><span class="no">02</span>新约</h2>' + jump(nt) + books(nt) + '</section>'
            + f'<section class="ch" id="list"><h2><span class="no">03</span>编号对照</h2><ul class="legend">{legend}</ul></section>')
    toc_html = ('<ol class="toc-l"><li><span class="tp">旧约 · ' + str(len(ot)) + ' 卷</span><ol>'
                + ''.join(f'<li><a href="#bk{b}">{name}</a></li>' for b, name, _ in ot)
                + '</ol></li><li><span class="tp">新约 · ' + str(len(nt)) + ' 卷</span><ol>'
                + ''.join(f'<li><a href="#bk{b}">{name}</a></li>' for b, name, _ in nt)
                + '</ol></li><li><a href="#list">编号对照</a></li></ol>')
    srcs = ('<section class="ch" id="sources"><h2><span class="no">✦</span>说明</h2>'
            '<p>本页由程序从各篇问题彩蛋的正文里自动找出带出处的经文（例如“（罗3:25）”“（来9:22-28）”），按书卷和章整理；'
            '只算正文，不算资料出处。一篇文章在同一章引用多次，只列一次。问题彩蛋增加或修改以后，本页会一起重新生成。</p></section>')
    css = H.CSS
    H.CSS = css + EXTRA_CSS
    try:
        return H.doc(TITLE, '问题彩蛋经文索引：按圣经书卷和章查找哪几篇问题彩蛋讲过这段经文。', main, srcs, toc_html, H.Cites())
    finally:
        H.CSS = css


if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
