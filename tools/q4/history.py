#!/usr/bin/env python3
"""生成《基督教两千年家谱》独立网页（仓库根目录 history.html）。
正文在 history_text.py，表格和名片在 history_data.py，三张图在 history_svg.py，资料出处在 history_sources.py。
用法：Q4_WORK=<含 bible/ 的目录> python3 tools/q4/history.py [输出路径]
文字里的记号：{{c:键}} 出处编号；{{v:徒2:42}} 整段经文（和合本）；{{ref:章id}} 跳到某一章；{{fig:名}} 图；其余见 BLOCKS。"""
import html, json, os, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bible
import history_text as T, history_data as D, history_svg as G, history_sources as SR
try:
    from history_checked import CHECKED      # 核对通过的网址（由 GitHub 上的核对结果整理）
except ImportError:
    CHECKED = {}

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'history.html')
esc = html.escape
FAMS = {'f1': '东方亚述', 'f2': '东方正统', 'f3': '东正教', 'f4': '天主教', 'f5': '新教', 'f6': '复临'}
ERA_YEARS = {'a': '约31—312', 'b': '313—589', 'c': '590—1516', 'd': '1517—1600', 'e': '1600—1830', 'f': '1831—1900', 'g': '1900—今天'}

# ---------- 章节编号 ----------
CH = [(part, cid, title) for part, cid, title, _ in T.CHAPTERS]
NO = {cid: i + 1 for i, (_, cid, _) in enumerate(CH)}
TITLE = {cid: t for _, cid, t in CH}
ANCHORS = {'sabbath': ('empire', '专题“安息日怎样变成了星期日”')}


def ref(cid):
    if cid in ANCHORS:
        c, lab = ANCHORS[cid]
        return f'<a class="xref" href="#{cid}">第 {NO[c]} 章的{lab}</a>'
    return f'<a class="xref" href="#{cid}">第 {NO[cid]} 章《{TITLE[cid]}》</a>'


# ---------- 经文 ----------
def verse(r):
    m = re.fullmatch(r'(\D+?)(\d.*)', r)
    b = bible.NAME2IDX[m.group(1)]
    cvs = bible.parse_cv(m.group(2))
    full = bible.BOOKS[b][1]
    texts = [re.sub(r'\s+', '', bible.cuv(b, c, v)).replace('－', '') for c, v in cvs]
    joined = ''.join(texts)
    if joined.count('“') != joined.count('”'):          # 引号跨出了引用的范围：去掉，免得只剩半边
        texts = [t.replace('“', '').replace('”', '') for t in texts]
    texts[-1] = re.sub(r'[，；、：]$', '……', texts[-1])     # 句子没完的，用省略号收尾
    parts = [(f'<sup>{v}</sup>' if len(cvs) > 1 else '') + esc(t) for (c, v), t in zip(cvs, texts)]
    cv = m.group(2).replace('-', '—')
    if len(bible._cuv[b]['chapters']) == 1:              # 只有一章的书（如犹大书）只写节数
        cv = cv.split(':', 1)[1]
    label = full + ' ' + cv
    return f'<blockquote class="verse"><p>{"".join(parts)}</p><cite>{label}</cite></blockquote>'


# ---------- 资料出处 ----------
def src_info(k):
    """(说明, 网址或 None, 网站名, 核对方式)"""
    d, urls, _ = SR.SRC[k]
    if urls is None:                       # 书籍
        return d, None, '', 'book'
    ok = CHECKED.get(k)
    if ok:
        url, how = ok
    else:
        url, how = (urls[0] if isinstance(urls, list) else urls), ''
        print('  ! 未核对的出处：', k, file=sys.stderr)
    host = urllib.parse.urlsplit(url).netloc.replace('www.', '')
    return d, url, host, how


def archive_url(url, how):
    return f'https://web.archive.org/web/{how.split()[1]}/{url}'


PRIMARY = {'justin', 'ignatius', 'pliny_txt', 'laodicea', 'socrates', 'sozomen', 'theses_txt', 'augsburg', 'lbc1689',
           'luther_pref', 'luther_worms', 'luther_name'}


def src_kind(k, url):
    if url is None:
        if k in ('chaldef', 'gregnaz'):
            return '原始文献'
        return '怀爱伦著作' if k[:2] in ('gc', 'cm', 'ls', 'da', 'bc', 'sm') else '书籍'
    if k in PRIMARY or k in ('br1914', 'br1949', 'min1956', 'unruh77'):
        return '原始文献'
    if k in ('rh1896', 'yi1900'):
        return '怀爱伦著作'
    if k in ('valentine',):
        return '百科全书'
    if k in ('knight03', 'whidden03', 'douglass04', 'qod2007'):
        return '学术研究'
    if k in ('fraser', 'pew'):
        return '学术研究'
    if any(h in url for h in ('britannica.com', 'wikipedia.org', 'newadvent.org/cathen', 'gameo.org')):
        return '百科全书'
    return '官方网站'


class Cites:
    def __init__(self):
        self.order = []          # 键，按第一次出现的顺序
        self.uses = {}           # 键 → 出现次数

    def __call__(self, k):
        assert k in SR.SRC, k
        if k not in self.uses:
            self.order.append(k); self.uses[k] = 0
        self.uses[k] += 1
        n = self.order.index(k) + 1
        return f'<a class="cite" id="r{n}-{self.uses[k]}" href="#s{n}" data-n="{n}">{n}</a>'

    def html(self):
        items = []
        for i, k in enumerate(self.order):
            n = i + 1
            d, url, host, how = src_info(k)
            kind = src_kind(k, url)
            back = ''.join(f'<a href="#r{n}-{j}" aria-label="回到正文第{j}处">↑</a>' for j in range(1, self.uses[k] + 1))
            link = f'<a class="su" href="{esc(url)}" target="_blank" rel="noopener">{esc(host)} ↗</a>' if url else ''
            if how.startswith('archive '):
                link += f'<a class="su2" href="{esc(archive_url(url, how))}" target="_blank" rel="noopener">网页存档</a>'
            items.append(f'<li id="s{n}" data-k="{k}"><span class="sk">{kind}</span><span class="sd">{esc(d)}</span>{link}<span class="sb">{back}</span></li>')
        return '<ol class="srcs">' + ''.join(items) + '</ol>'

    def data(self):
        out = {}
        for i, k in enumerate(self.order):
            d, url, host, how = src_info(k)
            out[i + 1] = [d, url or '', host, src_kind(k, url), archive_url(url, how) if how.startswith('archive ') else '']
        return json.dumps(out, ensure_ascii=False)


# ---------- 各种内容块 ----------
def timeline():
    out = ['<div class="tl">']
    cur = None
    for yr, era, txt, c in D.TIMELINE:
        if era != cur:
            if cur:
                out.append('</ol></div>')
            out.append(f'<div class="era era-{era}"><h4>{D.ERAS[era]}<small>{ERA_YEARS[era]}</small></h4><ol>')
            cur = era
        out.append(f'<li><b class="y">{yr}</b><span>{txt}{"{{c:" + c + "}}" if c else ""}</span></li>')
    out.append('</ol></div></div>')
    return ''.join(out)


def denoms():
    out = ['<p class="dn-tools"><button type="button" class="btn sm" data-allopen>全部展开</button></p><div class="dns">']
    for d in D.DENOMS:
        li = lambda xs: '<ul>' + ''.join(f'<li>{x}</li>' for x in xs) + '</ul>'
        out.append(f'''<details class="dn {d["fam"]}" id="d-{d["id"]}">
<summary><span class="dn-fam">{FAMS[d["fam"]]}</span><span class="dn-n">{d["name"]}</span><span class="dn-w">{d["when"]}</span></summary>
<div class="dn-b">
<p class="dn-m"><b>也叫</b>{d["names"]}</p><p class="dn-m"><b>代表人物</b>{d["who"]}</p>
<h5>核心特点</h5>{li(d["core"])}
<div class="dn-cmp"><div class="same"><h5>✓ 与复临信仰相同</h5>{li(d["same"])}</div><div class="diff"><h5>≠ 与复临信仰不同</h5>{li(d["diff"])}</div></div>
<p class="dn-src">资料{{{{c:{d["cite"]}}}}}</p>
</div></details>''')
    out.append('</div>')
    return ''.join(out)


def cmp_table():
    cols = D.CMP_COLS
    sda = len(cols) - 1
    data = {c: [r[1][i] for r in D.CMP_ROWS] for i, c in enumerate(cols)}
    default = '浸信会'
    opts = ''.join(f'<option{" selected" if c == default else ""}>{c}</option>' for c in cols[:-1])
    rows = ''.join(f'<tr><th>{r[0]}</th><td class="a">{r[1][cols.index(default)]}</td><td class="s">{r[1][sda]}</td></tr>' for r in D.CMP_ROWS)
    vs = f'''<div class="vs">
<label class="vs-pick"><span>选一个教派，和复临安息日会并排对比：</span><select data-vs>{opts}</select></label>
<table class="vs-t"><thead><tr><th></th><th class="a" data-vsname>{default}</th><th class="s">复临安息日会</th></tr></thead><tbody>{rows}</tbody></table>
<script type="application/json" id="vsdata">{json.dumps(data, ensure_ascii=False)}</script>
</div>'''
    head = '<tr><th class="c0">问题</th>' + ''.join(f'<th{" class=s" if i == sda else ""}>{c}</th>' for i, c in enumerate(cols)) + '</tr>'
    body = ''.join('<tr><th class="c0">' + r[0] + '</th>' + ''.join(f'<td{" class=s" if i == sda else ""}>{x}</td>' for i, x in enumerate(r[1])) + '</tr>' for r in D.CMP_ROWS)
    full = f'<h3>九个宗派的总表</h3><div class="tblwrap" tabindex="0" role="region" aria-label="九个宗派核心教义总表，可以左右滑动"><table class="cmp"><thead>{head}</thead><tbody>{body}</tbody></table></div>'
    return vs + full


def spectra():
    out = []
    for title, left, right, pts in D.SPECTRA:
        W, x0, x1 = 400, 22, 378
        ty = 52
        lanes = {-1: [], 1: [], -2: [], 2: []}
        ypos = {-1: ty - 12, 1: ty + 22, -2: ty - 28, 2: ty + 38}
        svg = []
        placed = []
        for name, pos in sorted(pts, key=lambda p: p[1]):
            cx = x0 + pos / 100 * (x1 - x0)
            w = sum(11 if ord(ch) > 255 else 6 for ch in name) + 4
            a, b = max(2, cx - w / 2), min(W - 2, cx + w / 2)
            if b - a < w:      # 贴边时整体挪进来
                a, b = (W - 2 - w, W - 2) if cx > W / 2 else (2, 2 + w)
            for lane in (-1, 1, -2, 2):
                if not lanes[lane] or lanes[lane][-1] + 4 <= a:
                    lanes[lane].append(b); break
            placed.append((name, cx, (a + b) / 2, lane))
        top = min(ypos[l] for *_, l in placed) - 14
        bot = max(ypos[l] for *_, l in placed) + 8
        svg.append(f'<line x1="{x0}" y1="{ty}" x2="{x1}" y2="{ty}" class="trk"/>')
        for name, cx, mx, lane in placed:
            sda = name == '复临'
            y = ypos[lane]
            if abs(lane) == 2:
                svg.append(f'<line x1="{cx:.1f}" y1="{ty + (6 if lane > 0 else -6)}" x2="{cx:.1f}" y2="{y - (11 if lane > 0 else -4)}" class="ldr"/>')
            svg.append(f'<circle cx="{cx:.1f}" cy="{ty}" r="{7 if sda else 5}" class="{"sp-s" if sda else "sp-d"}"/>')
            svg.append(f'<text x="{mx:.1f}" y="{y}" text-anchor="middle" class="{"sp-ts" if sda else "sp-t"}">{esc(name)}</text>')
        vb = f'0 {top} {W} {bot - top}'
        out.append(f'''<figure class="spec"><figcaption>{title}</figcaption>
<p class="sp-ends"><span>← {left}</span><span>{right} →</span></p>
<svg viewBox="{vb}" class="dg sp" role="img" aria-label="{esc(title)}：从“{esc(left)}”到“{esc(right)}”，{esc("、".join(n for n, _ in sorted(pts, key=lambda p: p[1])))}">{"".join(svg)}</svg></figure>''')
    return '<div class="specs">' + ''.join(out) + f'<p class="note2">{D.SPECTRA_NOTE}</p></div>'


def people():
    out = ['<div class="ppl">']
    for era_name, era, ps in D.PEOPLE:
        out.append(f'<section class="pe era-{era}"><h4>{era_name}</h4><ul>')
        for name, yrs, role in ps:
            out.append(f'<li><p class="pn"><b>{name}</b><span>{yrs}</span></p><p class="pr">{role}</p></li>')
        out.append('</ul></section>')
    out.append('</div>')
    return ''.join(out)


def faq():
    return '<div class="faq">' + ''.join(f'<details><summary>{q}</summary><div><p>{a}</p></div></details>' for q, a in D.FAQ) + '</div>'


def struct():
    lv = [('全球总会', '全世界教会的最高行政机构，总部在美国马里兰州'), ('分会', '全球总会在各大地区的分部，例如北亚太分会、南亚太分会'),
          ('联合会', '由一个地区的若干区会组成'), ('区会', '由若干地方教会组成，负责聘任和派遣牧师'), ('地方教会', '信徒每个安息日聚会的地方，信徒在这里受浸、入会')]
    li = ''.join(f'<li><b>{a}</b><small>{b}</small></li>' for a, b in lv)
    return f'''<div class="org"><p class="lab">今天的组织：代议制</p><ol>{li}</ol>
<p>每一级的负责人，都由下一级选出的代表开会选举；全球总会代表大会每五年开一次。这样，全世界的教会信仰一致、彼此相连，地方教会又有自己的选举和管理。</p></div>'''


def chart(which):
    if which == 'share':
        rows = D.CHART_SHARE
        title, sub, src = '全世界的基督徒：各大分支所占的比例', D.CHART_SHARE_NOTE, 'pew'
    else:
        rows = D.CHART_FAM
        title, sub, src = '几个宗派的世界性联会自己公布的人数（约数）', D.CHART_FAM_NOTE, None
        if not rows:
            return ''
    mx = max(r[1] for r in rows)
    bars = ''.join(f'<div class="br {fam}"><span class="bl">{name}</span><span class="bt"><i style="width:{v / mx * 100:.1f}%"></i><em>{lab}</em></span>'
                   f'{"{{c:" + c + "}}" if c else ""}</div>' for name, v, lab, fam, c in rows)
    s = f'资料{{{{c:{src}}}}}' if src else ''
    return f'<figure class="chart"><figcaption><b>{title}</b><small>{sub}{s}</small></figcaption><div class="bars">{bars}</div></figure>'


FIGS = {'overview': G.overview, 'protestant': G.protestant, 'streams': G.streams}


def expand(s):
    s = re.sub(r'\{\{fig:(\w+)\}\}', lambda m: f'<figure class="fig">{FIGS[m.group(1)]()}</figure>', s)
    s = s.replace('{{tl}}', timeline()).replace('{{denoms}}', denoms()).replace('{{cmp}}', cmp_table()) \
         .replace('{{spectra}}', spectra()).replace('{{people}}', people()).replace('{{faq}}', faq()).replace('{{struct}}', struct())
    s = re.sub(r'\{\{chart:(\w+)\}\}', lambda m: chart(m.group(1)), s)
    s = re.sub(r'\{\{v:([^}]+)\}\}', lambda m: verse(m.group(1)), s)
    s = re.sub(r'\{\{ref:(\w+)\}\}', lambda m: ref(m.group(1)), s)
    return s


# ---------- 页面 ----------
LINEAGE = [('约30', '耶稣与使徒', '五旬节，耶路撒冷教会', 'f0'), ('100—1054', '大公教会', '教父、信经、大公会议', 'f0'),
           ('1054', '西方的罗马天主教', '东西方教会大分裂', 'f4'), ('1517', '新教（更正教）', '路德发起宗教改革', 'f5'),
           ('1609—1784', '浸信会、卫理公会等', '信徒受浸、自由意志、成圣', 'f5'), ('1831—1844', '复临运动', '米勒耳研究但以理书8:14', 'f6'),
           ('1863', '基督复临安息日会', '安息日、圣所、预言之灵', 'f6')]


def page():
    cites = Cites()
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
    lineage = ''.join(f'<li class="{f}"><span class="ly">{y}</span><b>{n}</b><small>{s}</small></li>' for y, n, s, f in LINEAGE)
    hero = f'''<header class="hero">
<p class="eyebrow">问题彩蛋 · 第12课星期三《末时的余民》延伸阅读</p>
<h1>基督教两千年家谱</h1>
<p class="hsub">从耶稣到今天：基督复临安息日会从哪里来？天主教、东正教、浸信会、长老会……又是怎样分出来的？</p>
<div class="answer"><p class="lab">先说结论</p>
<p>基督复临安息日会不是凭空出现的新宗教，而是基督教这棵大树上的一根枝子。沿着家谱往回找，它的来路是这样的：</p>
<ol class="lineage">{lineage}</ol>
<p>它和天主教、东正教、新教各宗<b>共有</b>三位一体、基督的神性、因信称义、圣经的权威等核心信仰；<b>不同</b>的地方，主要在于第七日安息日、死人的状态、基督在天上圣所的工作、预言之灵和对末世的理解。下面一步一步讲清楚，每一个历史说法都标了出处，点小数字就能查看。</p></div>
<p class="howto"><span>怎样读这一页：</span>点正文里的<a class="cite demo" href="#sources">1</a>这样的小数字，可以看到这句话的出处，再点“打开网页”就能看原文；点{ref("timeline")}之类的蓝色字，可以跳到相关的章节；右下角的“目录”按钮随时可以跳到任何一章。</p>
</header>
<nav class="toc-in" aria-label="目录"><h2>目录</h2>{toc_html}</nav>'''
    main = expand(hero) + ''.join(body)
    # 出处编号按在页面中出现的顺序
    main = re.sub(r'\{\{c:(\w+)\}\}', lambda m: cites(m.group(1)), main)
    assert '{{' not in main, re.findall(r'\{\{[^}]*\}\}', main)[:5]
    srcs = f'''<section class="ch" id="sources"><h2><span class="no">✦</span>资料出处</h2>
<p>本页每一个重要的历史说法，都标了一个小数字，对应下面的资料。资料分四类：<b>原始文献</b>（当时的人亲笔写下的记录，最直接的证据）、<b>学术研究</b>、<b>百科全书</b>（大英百科全书、天主教百科全书等，由各领域学者编写），以及各教会的<b>官方网站</b>（它们对自己信仰的正式说明）。</p>
<p class="note2">这些网页都在 2026 年 10 月 2 日逐一核对过，确认网页里确实有正文所说的内容（年份、人数、原话等）：多数是用程序直接打开网页核对；大英百科等网站不允许程序读取，就用“网页时光机”（互联网档案馆）保存的副本核对，并附上“网页存档”链接；医学论文用 PubMed 数据库核对；个别网站（《复临评论》）用搜索引擎显示的原文核对。部分外国网站在中国大陆可能打不开，可以换个网络环境再看。点 ↑ 回到正文引用的位置。</p>
{cites.html()}
</section>'''
    words = len(re.sub(r'<[^>]+>|\s', '', main))
    mins = round(words / 450 / 5) * 5
    main = main.replace('</h1>', f'</h1><p class="meta">约 {words / 10000:.1f} 万字 · 细读约 {mins} 分钟 · {len(T.CHAPTERS)} 章 · {len(cites.order)} 条资料出处</p>', 1)
    return doc('基督教两千年家谱', '从耶稣到今天：基督复临安息日会从哪里来？各大教派怎样分出来、核心教义有什么不同？有图有表，每个说法都附出处。', main, srcs, toc_html, cites)


def doc(title, desc, main, srcs, toc_html, cites):
    """专题网页的外壳（顶栏、目录、阅读设置、出处弹窗）：家谱和其他问题彩蛋专题共用"""
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title} · 问题彩蛋</title>
<meta name="description" content="{desc}">
<script>try{{var d=document.documentElement,f=localStorage.getItem('q4:fs'),t=localStorage.getItem('q4:theme');if(f)d.style.setProperty('--fs',f);if(t==='light'||t==='dark')d.setAttribute('data-theme',t);}}catch(e){{}}</script>
<style>{CSS}</style>
</head>
<body>
<div class="prog" aria-hidden="true"><i></i></div>
<header class="bar"><a class="back" href="./#qa">← 问题彩蛋</a><span class="bt">{title}</span><button type="button" class="aa" data-aa aria-label="字号与夜间模式">Aa</button></header>
<div class="wrap">
<aside class="toc-side" aria-label="目录"><p class="tsh">目录</p>{toc_html}<p class="tsrc"><a href="#sources">✦ 资料出处</a></p></aside>
<main>
{main}
{srcs}
<footer class="foot"><p>整理制作 · Ethan（HangZhou_XG）　·　安息日学2026年第4季《预言的恩赐》问题彩蛋</p><p><a href="./#qa">← 回到问题彩蛋</a>　<a href="./#home">学课目录</a></p></footer>
</main>
</div>
<button type="button" class="fab-toc" data-tocopen aria-label="打开目录">☰ 目录</button>
<div class="sheet" id="tocsheet" hidden><div class="sh-bg" data-close></div><div class="sh-card" role="dialog" aria-modal="true" aria-label="目录"><button type="button" class="sh-x" data-close aria-label="关闭">×</button><p class="tsh">目录</p>{toc_html}<p class="tsrc"><a href="#sources">✦ 资料出处</a></p></div></div>
<div class="sheet" id="aasheet" hidden><div class="sh-bg" data-close></div><div class="sh-card small" role="dialog" aria-modal="true" aria-label="阅读设置"><button type="button" class="sh-x" data-close aria-label="关闭">×</button>
<p class="tsh">字号</p><div class="seg" data-segfs><button type="button" data-fs="0.9">小</button><button type="button" data-fs="1">标准</button><button type="button" data-fs="1.12">大</button><button type="button" data-fs="1.25">特大</button><button type="button" data-fs="1.4">超大</button></div>
<p class="tsh">夜间模式</p><div class="seg" data-segth><button type="button" data-th="auto">跟随手机</button><button type="button" data-th="light">白天</button><button type="button" data-th="dark">夜间</button></div>
<p class="note2">和学课网站的设置是同一套。</p></div></div>
<div class="pop" id="pop" role="dialog" aria-label="资料出处" hidden></div>
<script type="application/json" id="srcdata">{cites.data()}</script>
<script>{JS}</script>
</body>
</html>
'''


CSS = r'''
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;font-size:calc(100% * var(--fs,1))}
[hidden]{display:none!important}
:root{
  --paper:#F5F3EE;--surface:#FFFFFF;--ink:#1C212D;--ink-2:#3C4354;--muted:#697183;--rule:#DEDAD0;
  --accent:#7A2233;--accent-soft:#F5E9EC;--link:#2F58B8;--gold:#8A6A22;--gold-soft:#F6F0E1;--band:#F1EEE6;
  --c0:#8A8F9C;--c1:#08968C;--c2:#B0631C;--c3:#3A5FC8;--c4:#B07F0E;--c5:#7B4FC4;--c6:#A8324A;
  --c6-soft:#F7E8EB;
  --sans:"PingFang SC","Hiragino Sans GB","Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;
  --serif:"Songti SC","STSong","Noto Serif SC","Source Han Serif SC","SimSun",serif;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;--paper:#11141A;--surface:#181C24;--ink:#E8EAEF;--ink-2:#C4C9D3;--muted:#949BAA;--rule:#2C323E;
  --accent:#E08A9A;--accent-soft:#2E1C22;--link:#8FB0F5;--gold:#D8B46A;--gold-soft:#2A2518;--band:#1C2029;
  --c0:#7D8494;--c1:#1A9C93;--c2:#C9722E;--c3:#5F82E0;--c4:#B5871A;--c5:#946FE0;--c6:#DB5F78;--c6-soft:#33202A}}
:root[data-theme="dark"]{
  color-scheme:dark;--paper:#11141A;--surface:#181C24;--ink:#E8EAEF;--ink-2:#C4C9D3;--muted:#949BAA;--rule:#2C323E;
  --accent:#E08A9A;--accent-soft:#2E1C22;--link:#8FB0F5;--gold:#D8B46A;--gold-soft:#2A2518;--band:#1C2029;
  --c0:#7D8494;--c1:#1A9C93;--c2:#C9722E;--c3:#5F82E0;--c4:#B5871A;--c5:#946FE0;--c6:#DB5F78;--c6-soft:#33202A}
.f0{--c:var(--c0)}.f1{--c:var(--c1)}.f2{--c:var(--c2)}.f3{--c:var(--c3)}.f4{--c:var(--c4)}.f5{--c:var(--c5)}.f6{--c:var(--c6)}
body{margin:0;background:var(--paper);color:var(--ink);font:400 calc(16.5px * var(--fs,1))/1.85 var(--sans);-webkit-font-smoothing:antialiased}
p{margin:0 0 .9em}
a{color:var(--link)}
b,strong{font-weight:650}
h1,h2,h3,h4,h5{line-height:1.4;margin:0}
.prog{position:fixed;top:0;left:0;right:0;height:3px;z-index:30;pointer-events:none}
.prog i{display:block;height:100%;width:100%;background:var(--accent);transform-origin:0 50%;transform:scaleX(0)}
.bar{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:10px;padding:8px 16px;padding-top:max(8px,env(safe-area-inset-top));background:color-mix(in srgb,var(--paper) 92%,transparent);backdrop-filter:blur(8px);-webkit-backdrop-filter:blur(8px);border-bottom:1px solid var(--rule)}
.bar .back{color:var(--accent);text-decoration:none;font-size:.9rem;white-space:nowrap}
.bar .bt{flex:1;text-align:center;font-weight:650;font-size:.92rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.bar .aa,.btn{font:inherit;font-size:.86rem;color:var(--ink);background:var(--surface);border:1px solid var(--rule);border-radius:999px;padding:4px 12px;cursor:pointer}
.btn.sm{font-size:.82rem}
.wrap{max-width:1180px;margin:0 auto;padding:0 16px}
main{max-width:720px;margin:0 auto;min-width:0}
.toc-side{display:none}
@media (min-width:1080px){
  .wrap{display:grid;grid-template-columns:260px minmax(0,1fr);gap:40px}
  .toc-side{display:block;position:sticky;top:64px;align-self:start;max-height:calc(100vh - 80px);overflow:auto;padding:20px 0 40px;font-size:.86rem}
  .fab-toc,.toc-in{display:none}
}
/* 封面 */
.hero{padding:28px 0 8px}
.eyebrow{color:var(--accent);font-size:.82rem;letter-spacing:.06em;margin:0 0 6px}
.hero h1{font-family:var(--serif);font-size:2.1rem;letter-spacing:.04em;margin:0 0 6px}
.meta{color:var(--muted);font-size:.82rem;margin:0 0 12px}
.hsub{font-size:1.06rem;color:var(--ink-2);margin:0 0 18px}
.answer{background:var(--surface);border:1px solid var(--rule);border-radius:16px;padding:16px 16px 6px;margin:0 0 16px}
.lab{font-size:.78rem;font-weight:700;letter-spacing:.1em;color:var(--accent);margin:0 0 6px}
.lineage{list-style:none;margin:6px 0 14px;padding:0}
.lineage li{position:relative;padding:0 0 12px 26px}
.lineage li::before{content:"";position:absolute;left:6px;top:8px;width:11px;height:11px;border-radius:50%;background:var(--c);box-shadow:0 0 0 3px var(--surface)}
.lineage li::after{content:"";position:absolute;left:11px;top:20px;bottom:-6px;width:2px;background:var(--rule)}
.lineage li:last-child::after{display:none}
.lineage .ly{display:block;font-size:.76rem;line-height:1.3;color:var(--muted);font-variant-numeric:tabular-nums}
.lineage b{font-size:.98rem}
.lineage small{display:block;color:var(--muted);font-size:.82rem;line-height:1.5}
.lineage li.f6 b{color:var(--c6)}
.howto{font-size:.88rem;color:var(--ink-2);background:var(--gold-soft);border-radius:12px;padding:10px 14px}
.howto span{font-weight:650}
/* 目录 */
.toc-in{background:var(--surface);border:1px solid var(--rule);border-radius:16px;padding:14px 16px 8px;margin:8px 0 8px}
.toc-in h2{font-size:1rem;margin:0 0 6px}
.toc-l,.toc-l ol{list-style:none;margin:0;padding:0}
.toc-l>li{margin:0 0 8px}
.tp{display:block;font-size:.76rem;font-weight:700;color:var(--muted);letter-spacing:.08em;margin:6px 0 2px}
.toc-l a{display:flex;gap:8px;padding:4px 6px;border-radius:8px;color:var(--ink);text-decoration:none;line-height:1.5}
.toc-l a:hover{background:var(--band)}
.toc-l a.on{background:var(--accent-soft);color:var(--accent);font-weight:650}
.toc-l .tn{flex:none;color:var(--muted);font-variant-numeric:tabular-nums;font-size:.86em;padding-top:.08em}
.tsh{font-weight:700;font-size:.9rem;margin:0 0 8px}
.tsrc a{color:var(--accent);text-decoration:none;font-size:.9rem}
/* 部分、章 */
.part{margin:48px 0 0;padding:18px 0 0;border-top:2px solid var(--ink)}
.part span{display:block;font-size:.8rem;letter-spacing:.14em;color:var(--accent);font-weight:700}
.part b{font-family:var(--serif);font-size:1.5rem}
.ch{padding:26px 0 8px;scroll-margin-top:56px}
.ch h2{font-family:var(--serif);font-size:1.42rem;display:flex;gap:10px;align-items:baseline;margin:0 0 14px}
.ch h2 .no{flex:none;font-family:var(--sans);font-size:.8rem;font-weight:700;color:var(--surface);background:var(--accent);border-radius:6px;padding:1px 7px;transform:translateY(-3px)}
.ch h3{font-size:1.1rem;margin:22px 0 8px;scroll-margin-top:56px}
.ch ul,.ch ol{padding-left:1.3em;margin:0 0 1em}
.ch li{margin:0 0 .4em}
.xref{color:var(--link);text-decoration:none;border-bottom:1px dashed currentColor}
/* 出处小数字 */
.cite{display:inline-block;min-width:1.45em;height:1.45em;line-height:1.45em;margin:0 1px;padding:0 3px;border-radius:5px;font-size:.66em;font-weight:700;text-align:center;vertical-align:.45em;text-decoration:none;color:var(--accent);background:var(--accent-soft);font-variant-numeric:tabular-nums}
.cite:target,.cite.flash{outline:2px solid var(--accent)}
/* 经文 */
.verse{margin:12px 0 16px;padding:10px 14px 10px 16px;border-left:3px solid var(--gold);background:var(--gold-soft);border-radius:0 12px 12px 0}
.verse p{font-family:var(--serif);font-size:1.02rem;margin:0 0 2px}
.verse sup{font-family:var(--sans);font-size:.65em;color:var(--gold);margin:0 2px 0 4px}
.verse cite{display:block;text-align:right;font-style:normal;font-size:.8rem;color:var(--gold)}
/* 提示框 */
.box{background:var(--surface);border:1px solid var(--rule);border-radius:14px;padding:14px 16px 4px;margin:16px 0}
.box.sda{border-color:color-mix(in srgb,var(--c6) 45%,var(--rule));background:var(--c6-soft)}
.box.sda .lab{color:var(--c6)}
.keys{background:var(--surface);border:1px solid var(--rule);border-radius:14px;padding:14px 16px 4px;margin:14px 0}
.keys ol{padding-left:1.2em}
.note2{font-size:.82rem;color:var(--muted)}
.cap{font-size:.84rem;color:var(--muted);margin:-4px 0 18px}
/* 图 */
.fig{margin:14px -12px 10px;padding:12px 6px;background:var(--surface);border:1px solid var(--rule);border-radius:16px}
.fig svg{display:block;width:100%;max-width:560px;height:auto;margin:0 auto}
@media (min-width:600px){.fig{margin:16px 0 10px;padding:16px}}
.dg{font-family:var(--sans)}
.dg .band0{fill:var(--band)}.dg .band1{fill:none}
.dg .tb{font-size:9px;fill:var(--muted);letter-spacing:.04em}
.dg .ln{fill:none;stroke:var(--c);stroke-width:5;stroke-linecap:round}
.dg .dot{fill:var(--surface);stroke:var(--ink);stroke-width:1.8}
.dg .root{fill:var(--ink)}
.dg .ty{font-weight:800;fill:var(--ink-2)}
.dg .tn{font-size:11px;font-weight:650;fill:var(--ink)}
.dg .tn.hi{font-weight:800}
.dg .ts{font-size:9px;fill:var(--muted)}
.dg .tw{font-size:9px;fill:var(--ink-2)}
.dg .ax{stroke:var(--muted);stroke-width:1;fill:none}
.dg .ta{font-size:9px;fill:var(--muted)}
.dg .grid{stroke:var(--rule);stroke-width:1;stroke-dasharray:2 3}
.dg .cn{stroke:var(--c);stroke-width:1.6;fill:none}
.dg .bar{stroke:var(--c);stroke-width:7;stroke-linecap:round;fill:none}
.dg .bar.hi{stroke-width:10}
.dg .dash{stroke-dasharray:4 4}
.dg .bar.dash{stroke-dasharray:6 4;stroke-width:6;stroke-linecap:butt}
.dg .halo{paint-order:stroke;stroke:var(--surface);stroke-width:3px;stroke-linejoin:round}
.dg .flow{fill:none;stroke:var(--rule);stroke-width:1.6}
.dg .box{fill:var(--paper);stroke:var(--rule);stroke-width:1}
.dg .fillc{fill:var(--c);stroke:none}
.dg .tnode{font-size:13px;font-weight:800;fill:#fff}
.dg .tnode2{font-size:11px;font-weight:600;fill:#fff;opacity:.92}
/* 六个原因、三项发现、七个独特之处 */
.causes,.disc3{display:grid;gap:10px;margin:12px 0 16px}
@media (min-width:600px){.causes{grid-template-columns:1fr 1fr}}
.cause,.disc3>div,.dist .d{position:relative;background:var(--surface);border:1px solid var(--rule);border-radius:14px;padding:12px 14px 4px}
.cause h4,.disc3 h4,.dist h4{font-size:1rem;margin:0 0 6px;display:flex;gap:8px;align-items:center}
.cause p{font-size:.92rem}
.cause .eg{font-size:.8rem;color:var(--accent);margin:-4px 0 8px}
.ci{flex:none;display:inline-grid;place-items:center;width:1.6em;height:1.6em;border-radius:50%;background:var(--accent);color:var(--surface);font-size:.78rem;font-weight:700}
.cause .ci,.disc3 .ci{position:absolute;top:12px;right:12px}
.disc3>div{border-left:4px solid var(--c6)}
.disc3 .ci{background:var(--c6)}
.dist{display:grid;gap:12px;margin:12px 0}
.dist .d{border-top:4px solid var(--c6)}
.dist .ci{background:var(--c6)}
.dist .also{font-size:.84rem;color:var(--muted)}
/* 年份步骤 */
.steps{list-style:none;padding:0!important;margin:12px 0 16px!important;border-left:2px solid var(--rule)}
.steps li{position:relative;padding:0 0 4px 16px;margin:0 0 10px!important}
.steps li::before{content:"";position:absolute;left:-6px;top:.62em;width:10px;height:10px;border-radius:50%;background:var(--surface);border:2px solid var(--accent)}
.steps .yr{display:inline-block;font-weight:700;color:var(--accent);margin-right:8px;font-variant-numeric:tabular-nums}
.solas{background:var(--surface);border:1px solid var(--rule);border-radius:14px;padding:14px 16px 4px;margin:14px 0}
/* 小表格 */
.mini{width:100%;border-collapse:collapse;font-size:.88rem;margin:10px 0 16px;background:var(--surface);border-radius:12px;overflow:hidden}
.mini th,.mini td{border-bottom:1px solid var(--rule);padding:7px 8px;text-align:left;vertical-align:top}
.mini th{background:var(--band);font-size:.82rem;white-space:nowrap}
/* 年表 */
.tl{margin:10px 0}
.era{position:relative;padding:0 0 6px 18px;border-left:3px solid var(--rule)}
.era.era-f{border-left-color:var(--c6)}
.era h4{font-size:.98rem;margin:0 0 6px;padding-top:6px}
.era h4 small{font-weight:400;color:var(--muted);font-size:.8rem;margin-left:8px}
.era h4::before{content:"";position:absolute;left:-8px;margin-top:.45em;width:13px;height:13px;border-radius:50%;background:var(--ink)}
.era.era-f h4::before{background:var(--c6)}
.era ol{list-style:none;padding:0!important;margin:0 0 12px!important}
.era li{display:grid;grid-template-columns:4.2em 1fr;gap:8px;font-size:.92rem;line-height:1.7;padding:5px 0;border-bottom:1px dashed var(--rule)}
.era li:last-child{border-bottom:0}
.era .y{font-variant-numeric:tabular-nums;color:var(--accent)}
.era.era-f .y{color:var(--c6)}
/* 教派名片 */
.dn-tools{text-align:right;margin:0 0 8px}
.dns{display:grid;gap:10px}
.dn{background:var(--surface);border:1px solid var(--rule);border-left:5px solid var(--c);border-radius:14px}
.dn summary{list-style:none;cursor:pointer;padding:12px 40px 12px 14px;position:relative}
.dn summary::-webkit-details-marker{display:none}
.dn summary::after{content:"＋";position:absolute;right:14px;top:12px;color:var(--muted);font-weight:700}
.dn[open] summary::after{content:"－"}
.dn-fam{display:inline-block;font-size:.72rem;font-weight:700;color:var(--ink-2);border:1px solid var(--c);border-radius:999px;padding:0 8px;margin-right:8px;vertical-align:.12em}
.dn-n{font-weight:700;font-size:1.06rem}
.dn-w{display:block;color:var(--muted);font-size:.84rem;line-height:1.6;margin-top:2px}
.dn-b{padding:0 14px 10px;font-size:.93rem}
.dn-m{margin:0 0 4px}.dn-m b{display:inline-block;min-width:5em;color:var(--muted);font-weight:600}
.dn h5{font-size:.88rem;margin:12px 0 4px}
.dn ul{margin:0 0 6px;padding-left:1.2em}
.dn-cmp{display:grid;gap:8px;margin-top:8px}
@media (min-width:600px){.dn-cmp{grid-template-columns:1fr 1fr}}
.dn-cmp>div{border-radius:10px;padding:2px 12px 6px}
.dn-cmp .same{background:color-mix(in srgb,var(--c1) 10%,transparent)}
.dn-cmp .diff{background:var(--c6-soft)}
.dn-cmp .same h5{color:var(--c1)}.dn-cmp .diff h5{color:var(--c6)}
.dn-src{font-size:.8rem;color:var(--muted);margin:6px 0 0}
#d-sda{border-color:color-mix(in srgb,var(--c6) 50%,var(--rule));border-left-color:var(--c6)}
/* 对照 */
.vs{background:var(--surface);border:1px solid var(--rule);border-radius:16px;padding:12px 12px 4px;margin:12px 0 18px}
.vs-pick{display:block;font-size:.9rem;margin:0 0 10px}
.vs-pick span{display:block;color:var(--ink-2);margin-bottom:4px}
.vs-pick select{font:inherit;font-size:1rem;padding:6px 10px;border-radius:10px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);width:100%}
.vs-t{width:100%;border-collapse:collapse;font-size:.88rem;table-layout:fixed}
.vs-t th,.vs-t td{padding:8px 6px;border-bottom:1px solid var(--rule);vertical-align:top;text-align:left;line-height:1.6}
.vs-t tbody th{width:4.6em;color:var(--muted);font-weight:600;font-size:.82rem}
.vs-t thead th{font-size:.86rem}
.vs-t .s{background:var(--c6-soft)}
.vs-t thead .s{color:var(--c6)}
.tblwrap{overflow-x:auto;-webkit-overflow-scrolling:touch;border:1px solid var(--rule);border-radius:14px;background:var(--surface);margin:8px 0 6px}
.cmp{border-collapse:separate;border-spacing:0;font-size:.84rem;min-width:1060px}
.cmp th,.cmp td{padding:8px 8px;border-bottom:1px solid var(--rule);vertical-align:top;text-align:left;line-height:1.6;width:115px}
.cmp thead th{background:var(--band);font-size:.82rem;white-space:nowrap}
.cmp .c0{position:sticky;left:0;z-index:1;background:var(--surface);width:76px;min-width:76px;box-shadow:1px 0 0 var(--rule);font-weight:650}
.cmp thead .c0{background:var(--band)}
.cmp .s{background:var(--c6-soft)}
.cmp thead .s{color:var(--c6)}
/* 光谱 */
.specs{display:grid;gap:10px;margin:10px 0}
.spec{margin:0;background:var(--surface);border:1px solid var(--rule);border-radius:14px;padding:12px 10px 8px}
.spec figcaption{font-weight:700;font-size:.96rem;margin:0 4px 2px}
.sp-ends{display:flex;justify-content:space-between;gap:12px;font-size:.78rem;color:var(--muted);margin:0 4px 0}
.spec svg{display:block;width:100%;height:auto}
.dg .trk{stroke:var(--rule);stroke-width:4;stroke-linecap:round}
.dg .ldr{stroke:var(--muted);stroke-width:1}
.dg .sp-d{fill:var(--ink-2);stroke:var(--surface);stroke-width:2}
.dg .sp-s{fill:var(--c6);stroke:var(--surface);stroke-width:2}
.dg .sp-t{font-size:11px;fill:var(--ink-2)}
.dg .sp-ts{font-size:11.5px;font-weight:800;fill:var(--ink)}
/* 组织 */
.org{background:var(--surface);border:1px solid var(--rule);border-radius:14px;padding:14px 16px 4px;margin:16px 0}
.org ol{list-style:none;padding:0!important;margin:6px 0 12px!important;display:grid;gap:6px}
.org li{background:var(--c6-soft);border-radius:10px;padding:6px 12px;margin:0!important;position:relative}
.org li:nth-child(1){margin:0 0 0 0!important}.org li:nth-child(2){margin-left:10px!important}.org li:nth-child(3){margin-left:20px!important}.org li:nth-child(4){margin-left:30px!important}.org li:nth-child(5){margin-left:40px!important}
.org b{color:var(--c6)}.org small{display:block;color:var(--ink-2);font-size:.8rem;line-height:1.5}
/* 图表 */
.chart{margin:14px 0;background:var(--surface);border:1px solid var(--rule);border-radius:14px;padding:12px 14px 8px}
.chart figcaption b{display:block;font-size:.96rem}
.chart figcaption small{display:block;color:var(--muted);font-size:.78rem;line-height:1.55;margin:2px 0 10px}
.bars{display:grid;gap:9px}
.br{display:grid;grid-template-columns:6.4em 1fr auto;align-items:center;gap:8px;font-size:.86rem}
.bl{line-height:1.3}
.bt{display:flex;align-items:center;gap:6px;min-width:0}
.bt i{display:block;height:14px;min-width:4px;background:var(--c);border-radius:0 4px 4px 0}
.bt em{font-style:normal;font-size:.8rem;color:var(--ink-2);white-space:nowrap;font-variant-numeric:tabular-nums}
/* 人物 */
.ppl{display:grid;gap:12px}
.pe{background:var(--surface);border:1px solid var(--rule);border-radius:14px;padding:12px 14px 2px}
.pe.era-f{border-top:4px solid var(--c6)}
.pe h4{font-size:.98rem;margin:0 0 6px}
.pe ul{list-style:none;padding:0!important;margin:0!important}
.pe li{padding:7px 0;border-top:1px dashed var(--rule);margin:0!important}
.pe li:first-child{border-top:0}
.pn{display:flex;flex-wrap:wrap;gap:4px 10px;align-items:baseline;margin:0}
.pn span{font-size:.8rem;color:var(--muted);font-variant-numeric:tabular-nums}
.pr{font-size:.88rem;color:var(--ink-2);margin:0}
/* 常见问题 */
.faq{display:grid;gap:8px;margin:10px 0}
.faq details{background:var(--surface);border:1px solid var(--rule);border-radius:12px}
.faq summary{cursor:pointer;padding:10px 36px 10px 14px;font-weight:650;position:relative;list-style:none}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"＋";position:absolute;right:12px;top:10px;color:var(--muted)}
.faq details[open] summary::after{content:"－"}
.faq details>div{padding:0 14px 4px;font-size:.94rem}
/* 人物特写 */
.prof{background:var(--surface);border:1px solid var(--rule);border-top:5px solid var(--c);border-radius:16px;padding:14px 16px 4px;margin:0 0 18px}
.pf-n{font-family:var(--serif);font-size:1.45rem;font-weight:700;line-height:1.35;margin:0 0 2px}
.pf-n small{display:block;font-family:var(--sans);font-size:.8rem;font-weight:400;color:var(--muted)}
.pf-y{font-size:.84rem;color:var(--ink-2);font-variant-numeric:tabular-nums;margin:0 0 8px;padding-bottom:8px;border-bottom:1px dashed var(--rule)}
.pf-s{font-size:.96rem}
.quote{margin:12px 0 16px;padding:12px 16px;background:var(--surface);border:1px solid var(--rule);border-left:4px solid var(--accent);border-radius:0 12px 12px 0}
.quote p{font-family:var(--serif);font-size:1.03rem;margin:0 0 6px}
.quote cite{display:block;font-style:normal;font-size:.8rem;color:var(--muted)}
.box .quote{background:var(--paper)}
.mini.two td:first-child{white-space:nowrap;color:var(--muted);font-weight:600;font-size:.82rem}
.box .mini{background:var(--paper)}
/* 怀爱伦引文 */
.egw{margin:16px 0;padding:14px 16px;border-radius:14px;background:var(--surface);border:1px solid var(--rule)}
.egw p{font-family:var(--serif);font-size:1.04rem}
.egw cite{display:block;font-style:normal;font-size:.8rem;color:var(--muted)}
/* 资料 */
.srcs{padding-left:2.2em!important;font-size:.86rem}
.srcs li{margin:0 0 10px!important;line-height:1.6;scroll-margin-top:60px}
.srcs li:target{background:var(--accent-soft);border-radius:8px}
.sk{display:inline-block;font-size:.7rem;font-weight:700;border-radius:4px;padding:0 5px;margin-right:6px;background:var(--band);color:var(--ink-2)}
.su{display:inline-block;margin-left:6px;word-break:break-all}
.sb a{margin-left:6px;text-decoration:none;color:var(--muted)}
.su2{display:inline-block;margin-left:8px;font-size:.8rem;color:var(--muted)}
.foot{border-top:1px solid var(--rule);margin:40px 0 0;padding:16px 0 120px;font-size:.84rem;color:var(--muted)}
/* 浮动按钮、弹出层 */
.fab-toc{position:fixed;right:16px;bottom:calc(18px + env(safe-area-inset-bottom));z-index:25;font:inherit;font-size:.9rem;font-weight:650;color:var(--surface);background:var(--ink);border:0;border-radius:999px;padding:9px 16px;box-shadow:0 6px 18px rgba(0,0,0,.18);cursor:pointer}
.sheet{position:fixed;inset:0;z-index:40}
.sh-bg{position:absolute;inset:0;background:rgba(0,0,0,.4)}
.sh-card{position:absolute;left:0;right:0;bottom:0;max-height:82vh;overflow:auto;background:var(--surface);border-radius:18px 18px 0 0;padding:18px 16px calc(20px + env(safe-area-inset-bottom));font-size:.94rem}
.sh-card.small{max-height:60vh}
@media (min-width:700px){.sh-card{left:50%;right:auto;width:560px;transform:translateX(-50%);bottom:40px;border-radius:18px}}
.sh-x{position:absolute;right:10px;top:8px;font-size:1.5rem;line-height:1;border:0;background:none;color:var(--muted);cursor:pointer;padding:4px 8px}
.seg{display:flex;gap:6px;flex-wrap:wrap;margin:0 0 14px}
.seg button{font:inherit;font-size:.88rem;flex:1;min-width:4em;padding:7px 4px;border-radius:10px;border:1px solid var(--rule);background:var(--paper);color:var(--ink);cursor:pointer}
.seg button.on{border-color:var(--accent);color:var(--accent);background:var(--accent-soft);font-weight:700}
.pop{position:absolute;z-index:35;width:min(330px,calc(100vw - 24px));background:var(--surface);color:var(--ink);border:1px solid var(--rule);border-radius:14px;box-shadow:0 10px 30px rgba(0,0,0,.2);padding:12px 14px;font-size:.88rem;line-height:1.65}
.pop .pk{font-size:.72rem;font-weight:700;color:var(--muted);margin:0 0 4px}
.pop .pd{margin:0 0 8px}
.pop .pa{display:flex;gap:8px;flex-wrap:wrap}
.pop .pa a{font-size:.84rem;text-decoration:none;border:1px solid var(--rule);border-radius:999px;padding:3px 10px}
.pop .pa a.go{background:var(--accent);border-color:var(--accent);color:var(--surface)}
.pop .pbook{font-size:.8rem;color:var(--muted);align-self:center}
html.sheetopen{overflow:hidden}
@media print{.bar,.prog,.fab-toc,.toc-side,.dn-tools{display:none!important}details>*{display:block!important}.fig,.box,.dn,.spec{break-inside:avoid}}
'''

JS = r'''
(function(){
  var de=document.documentElement;
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);}catch(e){}}
  /* 阅读进度 */
  var pb=document.querySelector('.prog i'),tick=false;
  function prog(){tick=false;var h=de.scrollHeight-innerHeight;pb.style.transform='scaleX('+(h>0?Math.min(1,scrollY/h):0)+')';}
  addEventListener('scroll',function(){if(!tick){tick=true;requestAnimationFrame(prog);}},{passive:true});prog();
  /* 弹出层 */
  function open(s){s.hidden=false;de.classList.add('sheetopen');}
  function close(s){s.hidden=true;de.classList.remove('sheetopen');}
  document.querySelectorAll('.sheet').forEach(function(s){
    s.addEventListener('click',function(e){if(e.target.closest('[data-close]')||e.target.closest('a[href^="#"]'))close(s);});
  });
  var TS=document.getElementById('tocsheet'),AS=document.getElementById('aasheet');
  document.querySelector('[data-tocopen]').addEventListener('click',function(){open(TS);var a=TS.querySelector('a.on');if(a)a.scrollIntoView({block:'center'});});
  document.querySelector('[data-aa]').addEventListener('click',function(){paint();open(AS);});
  addEventListener('keydown',function(e){if(e.key==='Escape'){close(TS);close(AS);hidePop();}});
  /* 字号、夜间模式（与学课网站共用设置） */
  function paint(){
    var f=+(get('fs')||1),t=get('theme')||'auto';
    AS.querySelectorAll('[data-fs]').forEach(function(b){b.classList.toggle('on',+b.dataset.fs===f);});
    AS.querySelectorAll('[data-th]').forEach(function(b){b.classList.toggle('on',b.dataset.th===t);});
  }
  AS.addEventListener('click',function(e){
    var b=e.target.closest('button');if(!b)return;
    if(b.dataset.fs){set('fs',b.dataset.fs);if(+b.dataset.fs===1)de.style.removeProperty('--fs');else de.style.setProperty('--fs',b.dataset.fs);}
    if(b.dataset.th){set('theme',b.dataset.th);if(b.dataset.th==='auto')de.removeAttribute('data-theme');else de.setAttribute('data-theme',b.dataset.th);}
    paint();
  });
  /* 目录：标出正在读的章 */
  var secs=[].slice.call(document.querySelectorAll('section.ch'));
  var links={};document.querySelectorAll('.toc-l a').forEach(function(a){var id=a.getAttribute('href').slice(1);(links[id]=links[id]||[]).push(a);});
  var cur=null;
  function mark(){
    var y=innerHeight*0.3,id=null;
    for(var i=0;i<secs.length;i++){if(secs[i].getBoundingClientRect().top<y)id=secs[i].id;else break;}
    if(id===cur)return;
    if(cur&&links[cur])links[cur].forEach(function(a){a.classList.remove('on');});
    cur=id;
    if(cur&&links[cur])links[cur].forEach(function(a){a.classList.add('on');});
    var side=document.querySelector('.toc-side a.on');
    if(side){var box=side.closest('.toc-side'),r=side.getBoundingClientRect(),br=box.getBoundingClientRect();if(r.top<br.top+40||r.bottom>br.bottom-40)box.scrollTop+=r.top-br.top-br.height/2;}
  }
  var mt=false;addEventListener('scroll',function(){if(!mt){mt=true;setTimeout(function(){mt=false;mark();},120);}},{passive:true});mark();
  /* 教派名片：全部展开 */
  var ab=document.querySelector('[data-allopen]');
  if(ab)ab.addEventListener('click',function(){
    var ds=document.querySelectorAll('.dn'),all=[].every.call(ds,function(d){return d.open;});
    ds.forEach(function(d){d.open=!all;});ab.textContent=all?'全部展开':'全部收起';
  });
  /* 并排对比 */
  var sel=document.querySelector('[data-vs]');
  if(sel){
    var VD=JSON.parse(document.getElementById('vsdata').textContent);
    sel.addEventListener('change',function(){
      var v=VD[sel.value];document.querySelector('[data-vsname]').textContent=sel.value;
      document.querySelectorAll('.vs-t tbody td.a').forEach(function(td,i){td.textContent=v[i];});
    });
  }
  /* 出处小数字：点了先弹出说明，再决定打开网页还是看资料列表 */
  var SD=JSON.parse(document.getElementById('srcdata').textContent),P=document.getElementById('pop'),pfrom=null;
  function esc(s){return String(s).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
  function hidePop(){P.hidden=true;pfrom=null;}
  document.addEventListener('click',function(e){
    var c=e.target.closest('a.cite');
    if(c&&!c.classList.contains('demo')){
      e.preventDefault();
      if(pfrom===c){hidePop();return;}
      var n=c.dataset.n,s=SD[n];if(!s)return;
      P.innerHTML='<p class="pk">资料 '+n+' · '+esc(s[3])+'</p><p class="pd">'+esc(s[0])+'</p><p class="pa">'+(s[1]?'<a class="go" href="'+esc(s[1])+'" target="_blank" rel="noopener">打开网页 ↗</a>':'<span class="pbook">书籍，可查阅纸本或电子版</span>')+(s[4]?'<a href="'+esc(s[4])+'" target="_blank" rel="noopener">网页存档</a>':'')+'<a href="#s'+n+'" data-golist>在资料列表中看</a></p>';
      P.hidden=false;pfrom=c;
      var r=c.getBoundingClientRect(),w=P.offsetWidth,x=Math.max(12,Math.min(innerWidth-w-12,r.left+r.width/2-w/2)),y=r.bottom+8;
      if(y+P.offsetHeight>innerHeight-12)y=r.top-P.offsetHeight-8;
      P.style.left=(x+scrollX)+'px';P.style.top=(y+scrollY)+'px';
      return;
    }
    if(c&&c.classList.contains('demo')){return;}
    if(!e.target.closest('#pop'))hidePop();
    else if(e.target.closest('[data-golist]'))setTimeout(hidePop,0);
  });
  addEventListener('resize',hidePop);
  /* 从资料列表点 ↑ 回到正文时，闪一下那个数字 */
  addEventListener('hashchange',function(){var t=document.getElementById(location.hash.slice(1));if(t&&t.classList.contains('cite')){t.classList.add('flash');setTimeout(function(){t.classList.remove('flash');},1600);}});
})();
'''

if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
