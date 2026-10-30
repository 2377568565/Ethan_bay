#!/usr/bin/env python3
"""生成《基督教两千年家谱》独立网页（仓库根目录 history.html）。
正文在 history_text.py，表格和名片在 history_data.py，三张图在 history_svg.py，资料出处在 history_sources.py。
用法：Q4_WORK=<含 bible/ 的目录> python3 tools/q4/history.py [输出路径]
文字里的记号：{{c:键}} 出处编号；{{v:徒2:42}} 整段经文（和合本）；{{ref:章id}} 跳到某一章；{{fig:名}} 图；其余见 BLOCKS。"""
import html, json, os, re, sys, urllib.parse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bible
import lamb, pixsky
import history_text as T, history_data as D, history_svg as G, history_sources as SR
try:
    from history_checked import CHECKED      # 核对通过的网址（由 GitHub 上的核对结果整理）
except ImportError:
    CHECKED = {}

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = ARGS[0] if ARGS else os.path.join(ROOT, 'history.html')
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
           'luther_pref', 'luther_worms', 'luther_name', 'irenaeus', 'mishnah_rh', 'talmud_rh', 'aquinas99', 'aquinas83', 'calvin420', 'wcf19'}


def src_kind(k, url):
    if url is None:
        if k in ('chaldef', 'gregnaz'):
            return '原始文献'
        return '怀爱伦著作' if k[:2] in ('gc', 'cm', 'ls', 'da', 'bc', 'sm') or k in getattr(SR, 'EGW_KEYS', ()) else '书籍'
    if k in PRIMARY or k in ('br1914', 'br1949', 'min1956', 'unruh77'):
        return '原始文献'
    if k in ('rh1896', 'yi1900') or k in getattr(SR, 'EGW_KEYS', ()):
        return '怀爱伦著作'
    if k in ('valentine', 'irving'):
        return '百科全书'
    if k in ('knight03', 'whidden03', 'douglass04', 'qod2007', 'tgc'):
        return '学术研究'
    if k in ('fraser', 'pew'):
        return '学术研究'
    if 'doi.org/' in url:
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
    import topic_tools
    tools = topic_tools.build(id='qa3', title='基督教两千年家谱', page='history.html', pdf='研经问答03-基督教两千年家谱.pdf', quiz=T.QUIZ, ref=ref)
    return doc('基督教两千年家谱', '从耶稣到今天：基督复临安息日会从哪里来？各大教派怎样分出来、核心教义有什么不同？有图有表，每个说法都附出处。', main, srcs, toc_html, cites, tools)


COL_QA = dict(name='问题彩蛋', hash='qa', foot='安息日学2026年第4季《预言的恩赐》问题彩蛋')


def doc(title, desc, main, srcs, toc_html, cites, tools=None, col=None):
    """专题网页的外壳（顶栏、目录、阅读设置、出处弹窗）：家谱和其他问题彩蛋专题共用。
    tools：topic_tools.build(...) 的结果（分享、答题后下载 PDF）。每个问题彩蛋都要有。
    col：属于哪个栏目（默认问题彩蛋；健康栏目 2026-10-26 起用 dict(name='健康', hash='health', foot=…)），决定返回链接、标题后缀和页尾。"""
    col = col or COL_QA
    if tools:
        main = main.replace('</header>', '</header>' + tools['row'], 1)
        srcs = (f'<div class="tend"><p>读完了？把这一篇分享给需要的人，或者答 3 道小题，下载 PDF 留着慢慢读。</p>{tools["row"]}</div>') + srcs
    else:
        print('  ! 这一页没有“分享”和“下载 PDF”按钮（tools）', file=sys.stderr)
    tb = tools['bar'] if tools else ''
    tail = tools['tail'] if tools else ''
    main = label_figs(main)
    main = main.replace('<header class="hero">', '<header class="hero">' + ORN, 1)
    words = len(re.sub(r'<[^>]+>|\s', '', main + srcs))
    mins = max(5, round(words / 450 / 5) * 5)
    pxw = f'<div class="pxw"><div class="px"><i></i></div><span class="pxn" data-pct>0%</span><p class="pxt">约 {mins} 分钟读完<span data-left></span></p></div>'
    rel = related(title) if col is COL_QA else (col.get('related') or '')
    au = col.get('audio')
    lp_btn = lp_bar = lp_css = lp_js = ''
    if au:   # 听朗读（健康栏目，2026-10-27）：录音在 GitHub 上合成好以后才显示，网页不用重新生成
        lp_btn = ('<div class="lsn" data-lsn hidden><button type="button" class="lsn-go" data-lsngo>' + I_HP +
                  '<span>听朗读</span><span class="lsn-d" data-lsnd></span></button><span class="lsn-note">温和的女声朗读全文（开源语音模型合成）。可以边听边做别的事。</span></div>')
        main = main.replace(tools['row'], tools['row'] + lp_btn, 1) if tools else main.replace('</header>', '</header>' + lp_btn, 1)
        lp_bar = LP_HTML
        lp_css = LP_CSS
        cfg = json.dumps(dict(id=au['id'], dir=au['dir'], heads=au['heads'], h=au['h'], n=au['n'], title=title), ensure_ascii=False)
        lp_js = '<script type="application/json" id="lpcfg">' + cfg + '</script><script>' + LP_JS + '</script>'
    return f'''<!doctype html>
<html lang="zh-CN" data-col="{col['hash']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title} · {col['name']}</title>
<meta name="description" content="{desc}">
<script>try{{var d=document.documentElement,f=localStorage.getItem('q4:fs'),t=localStorage.getItem('q4:theme');if(f)d.style.setProperty('--fs',f);if(t==='light'||t==='dark')d.setAttribute('data-theme',t);}}catch(e){{}}try{{if(window.top!==window&&top.location.host===location.host)document.documentElement.classList.add('emb');}}catch(e){{}}</script>
<style>{CSS}{lp_css}</style>
</head>
<body data-mins="{mins}">
<div class="prog" aria-hidden="true"><i></i></div>
<header class="bar"><a class="back" href="./#{col['hash']}">← {col['name']}</a><span class="bt">{title}</span>{tb}<button type="button" class="aa" data-aa aria-label="字号与夜间模式">Aa</button></header>
<div class="wrap">
<aside class="toc-side" aria-label="目录"><p class="tsh">目录</p>{toc_html}<p class="tsrc"><a href="#sources">✦ 资料出处</a></p>{pxw}</aside>
<main>
{main}
{srcs}
{rel}{SCENE}
<footer class="foot"><p>整理制作 · Ethan（HangZhou_XG）　·　{col['foot']}</p><p><a href="./#{col['hash']}">← 回到{col['name']}</a>　<a href="./#home">学课目录</a></p></footer>
</main>
</div>
<button type="button" class="fab-toc" data-tocopen aria-label="打开目录">☰ 目录<span class="fabp" data-pct>0%</span></button>
<div class="sheet" id="tocsheet" hidden><div class="sh-bg" data-close></div><div class="sh-card" role="dialog" aria-modal="true" aria-label="目录"><button type="button" class="sh-x" data-close aria-label="关闭">×</button><p class="tsh">目录</p>{toc_html}<p class="tsrc"><a href="#sources">✦ 资料出处</a></p>{pxw}</div></div>
<div class="sheet" id="aasheet" hidden><div class="sh-bg" data-close></div><div class="sh-card small" role="dialog" aria-modal="true" aria-label="阅读设置"><button type="button" class="sh-x" data-close aria-label="关闭">×</button>
<p class="tsh">字号</p><div class="seg" data-segfs><button type="button" data-fs="0.9">小</button><button type="button" data-fs="1">标准</button><button type="button" data-fs="1.12">大</button><button type="button" data-fs="1.25">特大</button><button type="button" data-fs="1.4">超大</button></div>
<p class="tsh">夜间模式</p><div class="seg" data-segth><button type="button" data-th="auto">跟随手机</button><button type="button" data-th="light">白天</button><button type="button" data-th="dark">夜间</button></div>
<p class="note2">和学课网站的设置是同一套。</p></div></div>
<div class="pop" id="pop" role="dialog" aria-label="资料出处" hidden></div>
<script type="application/json" id="srcdata">{cites.data()}</script>
<script>{JS}{LAMB_JS}{CARD_JS}{SEL_JS}</script>
{lp_bar}{lp_js}
{tail}
</body>
</html>
'''


def label_figs(main):
    """给没有图注的 figure.fig 加上“图 N · 标题”（标题取自 SVG 的 <title>）；已经有 <p class="cap">图 N 的保持原样。"""
    out, pos, n = [], 0, 0
    for m in re.finditer(r'<figure class="fig">(.*?)</figure>', main, re.S):
        n += 1
        out.append(main[pos:m.start()])
        body = m.group(1)
        has_cap = re.match(r'\s*<p class="cap">', main[m.end():m.end() + 40])
        tm = re.search(r'<title[^>]*>(.*?)</title>', body, re.S)
        if has_cap or not tm:
            out.append(m.group(0))
        else:
            out.append(f'<figure class="fig"><figcaption class="fgl"><b>图 {n}</b><span>{tm.group(1)}</span></figcaption>{body}</figure>')
        pos = m.end()
    out.append(main[pos:])
    return ''.join(out)


def related(title):
    """页面底部的“相关阅读”：按 qa_data.RELATED 取三篇。"""
    try:
        import qa_data
    except Exception:
        return ''
    by = {d['id']: d for d in qa_data.ITEMS if d.get('url')}
    me = next((d for d in by.values() if d['q'] == title), None)
    if not me:
        return ''
    cards = []
    for i in getattr(qa_data, 'RELATED', {}).get(me['id'], []):
        d = by.get(i)
        if d:
            cards.append(f'<a class="relc" href="{d["url"]}"><span class="reln">问题彩蛋 {d["no"]:02d}</span><b>{d["q"]}</b><small>{d.get("sub", "")}</small></a>')
    if not cards:
        return ''
    return f'<section class="rel" aria-label="相关阅读"><p class="relh">相关阅读</p><div class="relg">{"".join(cards)}</div></section>'


ORN = '<span class="orn">' + lamb.sprite(48, '小羊') + '</span>'   # 开头：小羊（第一次看到时左右看一下、眨眼）

# 页尾：点阵星空 + 站在地平线上的小羊（读到这里＝读完一篇，它欢喜跳三下；深夜它睡着）。经文放在星空上面，离会动的小羊远一些。
SCENE = ('<div class="scene"><p class="scv">“在你的光中，我们必得见光。”（诗36:9）</p><div class="stage">'
         + pixsky.svg() + lamb.sprite(48, '小羊', enter='joy') + '</div></div>')

# 星空每格的大小：手机 2px（360×112，小羊 48px），宽屏 3px（540×168，小羊 72px）。都是整数倍，点和小羊的像素一样清楚。
_LX, _LY, _ = pixsky.LAMB
SCENE_CSS = ''.join(
    (f'@media (min-width:600px){{' if k == 3 else '')
    + f'.scene .stage{{position:relative;flex:none;width:{pixsky.COLS * k}px;height:{pixsky.ROWS * k}px}}'
    + f'.scene .lamb{{position:absolute;left:{_LX * k}px;top:{_LY * k}px;width:{24 * k}px;height:{24 * k}px}}'
    + ('}' if k == 3 else '') for k in (2, 3)) + '.scene .sky{display:block;width:100%;height:100%}\n'



# ---------------- 听朗读（健康栏目，2026-10-27） ----------------
I_HP = '<svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><path d="M4 14v-2a8 8 0 0 1 16 0v2"/><rect x="3.5" y="13.5" width="4" height="6.5" rx="1.6"/><rect x="16.5" y="13.5" width="4" height="6.5" rx="1.6"/></svg>'
_I = lambda d: '<svg viewBox="0 0 24 24" aria-hidden="true">' + d + '</svg>'
LP_HTML = ('<div class="lp" id="lp" hidden role="region" aria-label="朗读播放器">'
           '<div class="lp-top"><span class="lp-ch" data-lpch>正在加载声音……</span><span class="lp-t" data-lpt>0:00</span><button type="button" class="lp-x" data-lpx aria-label="关闭朗读">×</button></div>'
           '<div class="lp-bar" data-lpbar role="slider" aria-label="播放进度" tabindex="0"><i></i></div>'
           '<div class="lp-row">'
           '<button type="button" data-lpprev aria-label="上一章">' + _I('<path d="M6 5v14"/><path d="M18 5 9 12l9 7z"/>') + '</button>'
           '<button type="button" data-lpback aria-label="后退 15 秒">' + _I('<path d="M4.5 12a7.5 7.5 0 1 0 2.2-5.3"/><path d="M4 4v4h4"/><text x="12" y="15.2" text-anchor="middle" font-size="7.5" stroke="none" fill="currentColor" font-family="system-ui,sans-serif">15</text>') + '</button>'
           '<button type="button" class="lp-pp" data-lppp aria-label="播放">' + _I('<path class="i-play" d="M8 5.5v13l11-6.5z"/><path class="i-pause" d="M8 5v14M16 5v14"/>') + '</button>'
           '<button type="button" data-lpfwd aria-label="前进 15 秒">' + _I('<path d="M19.5 12a7.5 7.5 0 1 1-2.2-5.3"/><path d="M20 4v4h-4"/><text x="12" y="15.2" text-anchor="middle" font-size="7.5" stroke="none" fill="currentColor" font-family="system-ui,sans-serif">15</text>') + '</button>'
           '<button type="button" data-lpnext aria-label="下一章">' + _I('<path d="M18 5v14"/><path d="M6 5l9 7-9 7z"/>') + '</button>'
           '<button type="button" class="lp-sp" data-lpsp aria-label="语速">1.0×</button>'
           '</div><p class="lp-msg" data-lpmsg hidden></p></div>')

LP_CSS = r"""
.lsn{display:flex;flex-wrap:wrap;align-items:center;gap:6px 12px;margin:14px 0 4px}
.lsn-go{display:inline-flex;align-items:center;gap:8px;font:inherit;font-size:1rem;font-weight:650;color:var(--surface);background:var(--accent);border:0;border-radius:999px;padding:9px 18px;cursor:pointer}
.lsn-go .ic{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
.lsn-d{font-weight:400;font-size:.86rem;opacity:.9}
.lsn-note{font-size:.84rem;color:var(--muted);flex:1 1 220px}
.lp-chgo{display:inline-flex;align-items:center;gap:4px;margin:4px 0 0;font:inherit;font-size:.82rem;color:var(--accent);background:var(--accent-soft);border:0;border-radius:999px;padding:3px 11px;cursor:pointer}
.lp-chgo svg{width:13px;height:13px;fill:currentColor}
.lp{position:fixed;left:0;right:0;bottom:0;z-index:28;background:var(--surface);border-top:1px solid var(--rule);box-shadow:0 -6px 20px rgba(0,0,0,.08);padding:8px 16px calc(8px + env(safe-area-inset-bottom))}
.lp>*{max-width:640px;margin-left:auto;margin-right:auto}
.lp-top{display:flex;align-items:center;gap:10px;font-size:.86rem}
.lp-ch{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-weight:650;color:var(--ink)}
.lp-t{color:var(--muted);font-variant-numeric:tabular-nums;white-space:nowrap}
.lp-x{font:inherit;font-size:1.3rem;line-height:1;color:var(--muted);background:none;border:0;padding:2px 4px;cursor:pointer}
.lp-bar{position:relative;height:22px;cursor:pointer;touch-action:none}
.lp-bar::before{content:"";position:absolute;left:0;right:0;top:9px;height:4px;border-radius:2px;background:var(--rule)}
.lp-bar i{position:absolute;left:0;right:0;top:9px;height:4px;border-radius:2px;background:var(--accent);transform-origin:0 50%;transform:scaleX(0)}
.lp-row{display:flex;align-items:center;justify-content:space-between;gap:4px}
.lp-row button{flex:0 0 auto;width:44px;height:44px;display:inline-flex;align-items:center;justify-content:center;font:inherit;color:var(--ink);background:none;border:0;border-radius:50%;cursor:pointer;padding:0}
.lp-row button:disabled{opacity:.3;cursor:default}
.lp-row svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.lp-row .lp-pp{width:54px;height:54px;color:var(--surface);background:var(--accent)}
.lp-row .lp-pp svg{width:26px;height:26px}
.lp-pp .i-play{fill:currentColor;stroke:none}.lp-pp .i-pause{display:none;stroke-width:2.6}
.lp.playing .lp-pp .i-play{display:none}.lp.playing .lp-pp .i-pause{display:inline}
.lp-row .lp-sp{width:auto;min-width:52px;padding:0 8px;border-radius:999px;border:1px solid var(--rule);height:34px;font-size:.86rem;font-variant-numeric:tabular-nums}
@media (max-width:360px){.lp-row button{width:40px;height:40px}.lp-row .lp-pp{width:50px;height:50px}.lp-row .lp-sp{min-width:46px;padding:0 6px;font-size:.8rem}}
.lp-msg{margin:4px 0 0;font-size:.84rem;color:var(--ink-2);text-align:center}
.lp-msg button{font:inherit;color:var(--accent);background:none;border:0;text-decoration:underline;cursor:pointer;padding:0 4px}
html.lpon body{padding-bottom:150px}
html.lpon .fab-toc{bottom:calc(150px + env(safe-area-inset-bottom))}
@media print{.lp,.lsn,.lp-chgo{display:none!important}}
"""

LP_JS = r"""
(function(){
  var C=JSON.parse(document.getElementById('lpcfg').textContent),de=document.documentElement;
  var P=document.getElementById('lp'),BTN=document.querySelector('[data-lsn]');if(!P||!BTN||!window.fetch)return;
  function q(s){return P.querySelector(s);}
  var A=null,M=null,ST=[],cur=-2,lastSave=0,userScroll=0,RATES=[0.8,0.9,1,1.15,1.3];
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);}catch(e){}}
  function fmt(t){t=Math.max(0,Math.floor(t||0));var h=Math.floor(t/3600),m=Math.floor(t%3600/60),s=t%60;return (h?h+':'+(m<10?'0':''):'')+m+':'+(s<10?'0':'')+s;}
  function name(i){var sec=document.getElementById(C.heads[i][1]),h=sec&&sec.querySelector('h2');return h?h.textContent.replace(/^0*(\d+)/,'第$1章 · '):'';}
  fetch(C.dir+'index.json',{cache:'no-cache'}).then(function(r){return r.ok?r.json():null;}).then(function(ix){
    M=ix&&ix[C.id];if(!M||!M.d)return;
    if(M.h===C.h&&M.t&&M.t.length===C.n)ST=C.heads.map(function(x){return M.t[x[0]];});   // 录音和文章对得上，才能按章跳转
    BTN.hidden=false;BTN.querySelector('[data-lsnd]').textContent='约 '+Math.max(1,Math.round(M.d/60))+' 分钟';
    if(ST.length)C.heads.forEach(function(x,i){var sec=document.getElementById(x[1]),h=sec&&sec.querySelector('h2');if(!h)return;
      var b=document.createElement('button');b.type='button';b.className='lp-chgo';b.innerHTML='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5v14l12-7z"/></svg>听这一章';
      b.addEventListener('click',function(){start(ST[i]);});h.insertAdjacentElement('afterend',b);});
    else{q('[data-lpprev]').hidden=true;q('[data-lpnext]').hidden=true;}
  }).catch(function(){});
  function rate(){var r=+(get('lprate')||1);return RATES.indexOf(r)>=0?r:1;}
  function msg(h,ms){var m=q('[data-lpmsg]');m.innerHTML=h;m.hidden=!h;clearTimeout(msg.t);if(h&&ms)msg.t=setTimeout(function(){m.hidden=true;},ms);}
  function save(){if(A&&A.currentTime>3)set('lpos:'+C.id,A.ended?'0':String(Math.floor(A.currentTime)));}
  function ensure(){
    if(A)return;
    A=new Audio();A.preload='auto';A.src=C.dir+C.id+'.mp3';
    A.addEventListener('timeupdate',paint);A.addEventListener('durationchange',paint);
    A.addEventListener('play',function(){P.classList.add('playing');q('[data-lppp]').setAttribute('aria-label','暂停');try{parent!==window&&parent.postMessage({q4:'tts'},location.origin);}catch(e){}});
    A.addEventListener('pause',function(){P.classList.remove('playing');q('[data-lppp]').setAttribute('aria-label','播放');save();});
    A.addEventListener('waiting',function(){q('[data-lpch]').textContent='正在加载声音……';cur=-2;});
    A.addEventListener('playing',function(){cur=-2;paint();});
    A.addEventListener('ended',function(){set('lpos:'+C.id,'0');msg('这一篇听完了。',6000);});
    A.addEventListener('error',function(){msg('声音没有加载成功，请检查网络后再点一次播放。');});
    if('mediaSession' in navigator)try{
      navigator.mediaSession.metadata=new MediaMetadata({title:C.title,artist:'健康 · 听朗读',album:'预言的恩赐 · 研读网站'});
      var MS=navigator.mediaSession;MS.setActionHandler('play',function(){A.play();});MS.setActionHandler('pause',function(){A.pause();});
      MS.setActionHandler('seekbackward',function(){seek(A.currentTime-15);});MS.setActionHandler('seekforward',function(){seek(A.currentTime+15);});
      if(ST.length){MS.setActionHandler('previoustrack',function(){chap(-1);});MS.setActionHandler('nexttrack',function(){chap(1);});}
    }catch(e){}
  }
  function open(){P.hidden=false;de.classList.add('lpon');var r=rate();q('[data-lpsp]').textContent=(r%1?String(r):r.toFixed(1))+'×';}
  function start(t,resume){ensure();open();A.playbackRate=rate();try{A.defaultPlaybackRate=rate();}catch(e){}
    var go=function(){try{A.currentTime=t||0;}catch(e){}};
    if(A.readyState>=1)go();else A.addEventListener('loadedmetadata',go,{once:true});
    var p=A.play();if(p&&p.catch)p.catch(function(){});
    if(resume)msg('已从上次听到的地方继续 <button type="button" data-lpfrom0>从头听</button>',9000);else msg('');}
  function seek(t){if(!A)return;var d=A.duration||M.d;try{A.currentTime=Math.max(0,Math.min(d-0.5,t));}catch(e){}paint();}
  function idx(t){var i=-1;for(var k=0;k<ST.length;k++){if(ST[k]<=t+0.3)i=k;else break;}return i;}
  function chap(dir){if(!A||!ST.length)return;var t=A.currentTime,i=idx(t);
    if(dir<0&&i>=0&&t-ST[i]>4)seek(ST[i]);else{var j=Math.max(0,Math.min(ST.length-1,i+dir));seek(ST[j]);}}
  function paint(){if(!A)return;var d=A.duration||M.d||1,t=A.currentTime||0;
    q('.lp-bar i').style.transform='scaleX('+Math.min(1,t/d).toFixed(4)+')';
    q('[data-lpt]').textContent=fmt(t)+' / '+fmt(d);
    var i=ST.length?idx(t):-1;
    if(i!==cur&&!A.paused){var first=cur===-2;cur=i;q('[data-lpch]').textContent=i>=0?name(i):C.title;
      if(i>=0&&!first&&Date.now()-userScroll>12000){var sec=document.getElementById(C.heads[i][1]);if(sec)sec.scrollIntoView({behavior:'smooth',block:'start'});}}   // 跟着声音翻到这一章（刚自己翻过页面就不打扰）
    else if(A.paused&&cur===-2){q('[data-lpch]').textContent=i>=0?name(i):C.title;}
    if(Date.now()-lastSave>5000){lastSave=Date.now();save();}
  }
  addEventListener('touchmove',function(){userScroll=Date.now();},{passive:true});addEventListener('wheel',function(){userScroll=Date.now();},{passive:true});
  BTN.querySelector('[data-lsngo]').addEventListener('click',function(){
    if(A&&!A.paused){open();return;}
    var s=+(get('lpos:'+C.id)||0);if(A&&A.currentTime>1){open();A.play();return;}
    start(s>10&&s<(M.d-15)?s:0,s>10&&s<(M.d-15));});
  q('[data-lppp]').addEventListener('click',function(){if(!A){start(0);return;}if(A.paused){A.playbackRate=rate();A.play();}else A.pause();});
  q('[data-lpback]').addEventListener('click',function(){seek((A?A.currentTime:0)-15);});
  q('[data-lpfwd]').addEventListener('click',function(){seek((A?A.currentTime:0)+15);});
  q('[data-lpprev]').addEventListener('click',function(){chap(-1);});
  q('[data-lpnext]').addEventListener('click',function(){chap(1);});
  q('[data-lpsp]').addEventListener('click',function(){var r=RATES[(RATES.indexOf(rate())+1)%RATES.length];set('lprate',String(r));if(A)A.playbackRate=r;this.textContent=(r%1?String(r):r.toFixed(1))+'×';});
  q('[data-lpx]').addEventListener('click',function(){if(A)A.pause();P.hidden=true;de.classList.remove('lpon');});
  P.addEventListener('click',function(e){if(e.target.closest('[data-lpfrom0]')){seek(0);msg('');}});
  var bar=q('[data-lpbar]');
  function barSeek(e){var r=bar.getBoundingClientRect(),x=(e.touches?e.touches[0].clientX:e.clientX)-r.left;seek(Math.max(0,Math.min(1,x/r.width))*((A&&A.duration)||M.d));}
  bar.addEventListener('pointerdown',function(e){if(!A)return;barSeek(e);bar.setPointerCapture&&bar.setPointerCapture(e.pointerId);bar.onpointermove=barSeek;});
  bar.addEventListener('pointerup',function(){bar.onpointermove=null;});bar.addEventListener('pointercancel',function(){bar.onpointermove=null;});
  bar.addEventListener('keydown',function(e){if(e.key==='ArrowLeft')seek(A.currentTime-15);if(e.key==='ArrowRight')seek(A.currentTime+15);});
  addEventListener('message',function(e){if(e.origin===location.origin&&e.data&&e.data.q4==='hidden'&&A)A.pause();});   // 网站把这一页收起来了
  addEventListener('pagehide',save);
})();
"""

CSS = r'''
*,*::before,*::after{box-sizing:border-box}
html{-webkit-text-size-adjust:100%;font-size:calc(100% * var(--fs,1))}
[hidden]{display:none!important}
:root{
  --paper:#F5F1E8;--surface:#FFFDF8;--ink:#1A2132;--ink-2:#454C5D;--muted:#767A86;--rule:#E3DCCD;
  --accent:#8A2E3E;--accent-soft:#F6EAE6;--link:#3D5672;--gold:#9A742C;--gold-soft:#F3E9D2;--band:#EFE9DD;
  --c0:#8A8F9C;--c1:#08968C;--c2:#B0631C;--c3:#3A5FC8;--c4:#B07F0E;--c5:#7B4FC4;--c6:#A8324A;
  --c6-soft:#F7E8EB;
  --sans:"PingFang SC","Hiragino Sans GB","Noto Sans SC","Microsoft YaHei",system-ui,sans-serif;
  --serif:"Songti SC","STSong","Noto Serif SC","Source Han Serif SC","SimSun",serif;
  color-scheme:light;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  color-scheme:dark;--paper:#0C111C;--surface:#141B2A;--ink:#ECE6DA;--ink-2:#C3C0B7;--muted:#8D93A2;--rule:#263042;
  --accent:#E08C9A;--accent-soft:#2B1B22;--link:#9DB4CC;--gold:#D3B06A;--gold-soft:#2A2518;--band:#1B2335;
  --c0:#7D8494;--c1:#1A9C93;--c2:#C9722E;--c3:#5F82E0;--c4:#B5871A;--c5:#946FE0;--c6:#DB5F78;--c6-soft:#33202A}}
:root[data-theme="dark"]{
  color-scheme:dark;--paper:#0C111C;--surface:#141B2A;--ink:#ECE6DA;--ink-2:#C3C0B7;--muted:#8D93A2;--rule:#263042;
  --accent:#E08C9A;--accent-soft:#2B1B22;--link:#9DB4CC;--gold:#D3B06A;--gold-soft:#2A2518;--band:#1B2335;
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
.mini th,.mini td{border-bottom:1px solid var(--rule);padding:7px 8px;text-align:left;vertical-align:top;min-width:4.5em}
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
/* ===== 2026-10-22 新版式：树形目录、像素进度条、图编号、表格、装饰、相关阅读 ===== */
:root{--mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,"Noto Sans Mono CJK SC",monospace}
.prog{height:4px}
.prog i{background:conic-gradient(var(--accent) 25%,transparent 0 50%,var(--accent) 0 75%,transparent 0) 0 0/4px 4px;transform:translateX(-100%);will-change:transform}
.toc-l .tp{position:relative;padding-left:1.35em;cursor:pointer;-webkit-user-select:none;user-select:none}
.toc-l .tp::before{content:"└";position:absolute;left:.15em;color:var(--muted);font-family:var(--mono)}
.toc-l>li.open>.tp{color:var(--ink)}
.toc-l ol{margin-left:.9em!important}
.toc-l ol a{position:relative;padding-left:1.55em}
.toc-l ol a::before{content:"└";position:absolute;left:.35em;top:4px;color:var(--rule);font-family:var(--mono)}
.toc-l ol a.on::before{color:var(--accent)}
.toc-side .toc-l>li>ol,.sheet .toc-l>li>ol{display:none}
.toc-side .toc-l>li.open>ol,.sheet .toc-l>li.open>ol{display:block;animation:tin .32s ease both}
.toc-side .toc-l a.on{background:none;color:var(--ink);font-weight:700}
@keyframes tin{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}
.pxw{display:grid;grid-template-columns:1fr auto;align-items:center;gap:4px 10px;margin:14px 0 4px;padding:12px 0 6px;border-top:1px solid var(--rule)}
.toc-side .pxw{position:sticky;bottom:0;background:var(--paper)}
.px{position:relative;height:14px;overflow:hidden;background-image:radial-gradient(var(--muted) .9px,transparent 1.2px);background-size:4px 4px;opacity:.95}
.px i{position:absolute;inset:0;background:conic-gradient(var(--ink) 25%,transparent 0 50%,var(--ink) 0 75%,transparent 0) 0 0/4px 4px;transform:translateX(-100%);will-change:transform}
.px i::after{content:"";position:absolute;right:0;top:0;bottom:0;width:4px;background:var(--ink)}
.pxn{font-family:var(--mono);font-size:.82rem;color:var(--ink-2);font-variant-numeric:tabular-nums;min-width:3.2em;text-align:right}
.pxt{grid-column:1/-1;margin:0;font-size:.76rem;letter-spacing:.04em;color:var(--muted);font-variant-numeric:tabular-nums}
.pxt span:not(:empty)::before{content:" · "}
.fabp{font-family:var(--mono);font-size:.76em;opacity:.8;margin-left:6px;font-variant-numeric:tabular-nums}
.fgl{display:flex;gap:8px;align-items:baseline;margin:0 4px 8px;font-size:.82rem;color:var(--ink-2);line-height:1.5}
.fgl b{flex:none;font-size:.74rem;letter-spacing:.08em;color:var(--accent);border:1px solid currentColor;border-radius:4px;padding:0 5px}
.mini th{color:var(--ink-2);letter-spacing:.03em}
.mini tr:nth-child(even) td{background:color-mix(in srgb,var(--band) 55%,var(--surface))}
.mini tr:hover td{background:var(--gold-soft)}
.mini td:first-child{font-weight:600}
.hero{position:relative;padding-top:58px}
.orn{position:absolute;left:0;top:6px;width:48px;height:48px}
.rel{margin:40px 0 0}
.relh{font-size:.8rem;font-weight:700;letter-spacing:.14em;color:var(--muted);margin:0 0 10px}
.relh::before{content:"└ ";font-family:var(--mono)}
.relg{display:grid;gap:10px}
@media (min-width:700px){.relg{grid-template-columns:repeat(3,1fr)}}
.relc{display:flex;flex-direction:column;gap:4px;padding:14px 14px 12px;background:var(--surface);border:1px solid var(--rule);border-radius:14px;text-decoration:none;color:var(--ink);transition:transform .2s ease,border-color .2s ease}
.relc:hover{transform:translateY(-2px);border-color:var(--gold)}
.reln{font-size:.74rem;letter-spacing:.08em;color:var(--accent);font-variant-numeric:tabular-nums}
.relc b{font-family:var(--serif);font-size:1.02rem;line-height:1.45}
.relc small{color:var(--muted);font-size:.8rem;line-height:1.55;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.scene{margin:40px -16px 0;overflow:hidden;display:flex;flex-direction:column;align-items:center}
.scene .scv{font-family:var(--serif);font-size:.9rem;color:var(--muted);margin:0 16px 14px;text-align:center}
/* 回到上次读到的地方：底部一条小提示（6 秒后收起） */
.rtip{position:fixed;z-index:60;left:50%;bottom:calc(20px + env(safe-area-inset-bottom,0px));display:flex;align-items:center;gap:12px;max-width:calc(100% - 32px);padding:9px 10px 9px 16px;border-radius:999px;background:var(--ink);color:var(--paper);font-size:.86rem;box-shadow:0 8px 24px rgba(0,0,0,.2);opacity:0;transform:translate(-50%,12px);transition:opacity .25s,transform .25s}
.rtip.on{opacity:1;transform:translate(-50%,0)}
.rtip span{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.rtip button{flex:none;border:0;border-radius:999px;padding:6px 12px;background:color-mix(in srgb,var(--paper) 18%,transparent);color:var(--paper);font:inherit;font-weight:700;cursor:pointer}
@media (prefers-reduced-motion:reduce){.rtip{transition:none}}

'''+SCENE_CSS+r'''@media (prefers-reduced-motion:reduce){.toc-side .toc-l>li.open>ol,.sheet .toc-l>li.open>ol{animation:none}}
@media print{.orn,.scene,.rel,.pxw{display:none!important}}
'''+lamb.sprite_css()+pixsky.CSS+r'''
@media print{.bar,.prog,.fab-toc,.toc-side,.dn-tools{display:none!important}details>*{display:block!important}.fig,.box,.dn,.spec{break-inside:avoid}}
'''

LAMB_JS = lamb.sprite_js()   # 小羊的动作（开头和页尾两只）
CARD_JS = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'card.js'), encoding='utf-8').read()   # 分享图片（和网站共用，2026-10-30）
# 选中文字：复制、分享成卡片图（2026-10-30 用户要的）。专题页没有划线功能，只放这两个按钮
SEL_JS = r"""
(function(){
  var de=document.documentElement,col=de.getAttribute('data-col')||'qa';
  var st=document.createElement('style');st.textContent='.tsel{position:fixed;z-index:90;left:0;top:0;display:flex;gap:2px;padding:5px 6px;border-radius:999px;background:var(--ink);color:var(--paper);'+
    'box-shadow:0 8px 24px rgba(0,0,0,.25);opacity:0;transition:opacity .15s}.tsel.on{opacity:1}.tsel[hidden]{display:none}'+
    '.tsel button{display:inline-flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;min-width:48px;height:40px;padding:0 6px;border:0;border-radius:12px;background:none;color:inherit;font:600 .68rem/1 var(--sans);cursor:pointer;-webkit-tap-highlight-color:transparent}'+
    '.tsel button:active{background:rgba(255,255,255,.12)}.tsel svg{width:18px;height:18px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}'+
    '.tsel-t{position:fixed;left:50%;bottom:calc(24px + env(safe-area-inset-bottom,0px));z-index:91;transform:translateX(-50%);padding:10px 16px;border-radius:999px;background:var(--ink);color:var(--paper);font-size:.86rem;opacity:0;transition:opacity .2s;pointer-events:none}.tsel-t.on{opacity:1}';
  document.head.appendChild(st);
  var bar=document.createElement('div');bar.className='tsel';bar.hidden=true;bar.setAttribute('role','toolbar');bar.setAttribute('aria-label','选中的文字');
  bar.innerHTML='<button type="button" data-a="copy"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="8.5" y="8.5" width="11" height="11" rx="2"/><path d="M15.5 8.5V6a1.5 1.5 0 0 0-1.5-1.5H6A1.5 1.5 0 0 0 4.5 6v8A1.5 1.5 0 0 0 6 15.5h2.5"/></svg>复制</button>'+
    '<button type="button" data-a="share"><svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="18" cy="5.5" r="2.6"/><circle cx="6" cy="12" r="2.6"/><circle cx="18" cy="18.5" r="2.6"/><path d="M8.3 10.8 15.7 6.7M8.3 13.2l7.4 4.1"/></svg>分享</button>';
  document.body.appendChild(bar);
  var tip=document.createElement('div');tip.className='tsel-t';tip.setAttribute('role','status');document.body.appendChild(tip);var tipT=null;
  function toast(m){tip.textContent=m;tip.classList.add('on');clearTimeout(tipT);tipT=setTimeout(function(){tip.classList.remove('on');},2200);}
  var cur=null,press=0;
  function title(){var h=document.querySelector('.hero h1');if(!h)return document.title;var c=h.cloneNode(true),x=c.querySelector('.h1s,small,.meta');if(x)x.remove();return c.textContent.trim();}
  function src(node){var ch=node&&node.closest&&node.closest('section.ch'),h=ch&&ch.querySelector('h2'),t='《'+title()+'》';
    if(h){var c=h.cloneNode(true),n=c.querySelector('.no');var no=n?n.textContent.trim():'';if(n)n.remove();if(/^\d+$/.test(no))t+=' · 第 '+(+no)+' 章 '+c.textContent.trim();}
    return (col==='health'?'健康':'问题彩蛋')+t;}
  function ok(r){var a=r.commonAncestorContainer;if(a.nodeType!==1)a=a.parentNode;
    return !!(a.closest&&a.closest('section.ch,header.hero')&&!a.closest('nav,.toc-in,#sources,.srcs,figure,svg,.tools,.trow,.tend,.faq summary,button,.pop,.sheet,.tsel,.lp'));}
  function hide(){bar.classList.remove('on');bar.hidden=true;cur=null;}
  function place(r){var rs=r.getClientRects(),f=rs[0]||r.getBoundingClientRect(),l=rs[rs.length-1]||f;
    var bw=bar.offsetWidth||120,bh=bar.offsetHeight||50,top=l.bottom+14;if(top+bh>innerHeight-8)top=Math.max(8,f.top-bh-14);
    var left=Math.min(innerWidth-bw-8,Math.max(8,(Math.min(f.left,l.left)+Math.max(f.right,l.right))/2-bw/2));bar.style.transform='translate3d('+Math.round(left)+'px,'+Math.round(top)+'px,0)';}
  function check(){if(Date.now()-press<700)return;var s=getSelection();
    if(!s||s.isCollapsed||!s.rangeCount){hide();return;}var r=s.getRangeAt(0),t=s.toString().replace(/\s+/g,' ').trim();
    if(t.length<2||!ok(r)){hide();return;}
    cur={t:t,node:r.startContainer.nodeType===1?r.startContainer:r.startContainer.parentNode};bar.hidden=false;place(r);requestAnimationFrame(function(){bar.classList.add('on');});}
  var T=null;document.addEventListener('selectionchange',function(){clearTimeout(T);T=setTimeout(check,260);});
  bar.addEventListener('pointerdown',function(e){press=Date.now();if(e.pointerType==='mouse')e.preventDefault();});
  bar.addEventListener('touchstart',function(){press=Date.now();},{passive:true});
  function copy(t){if(navigator.clipboard&&window.isSecureContext)return navigator.clipboard.writeText(t).then(function(){return true;},legacy);return Promise.resolve(legacy());
    function legacy(){var ta=document.createElement('textarea');ta.value=t;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();var k=false;try{k=document.execCommand('copy');}catch(e){}ta.remove();return k;}}
  bar.addEventListener('click',function(e){var b=e.target.closest('button');if(!b||!cur)return;var c=cur;
    try{getSelection().removeAllRanges();}catch(err){}hide();
    if(b.dataset.a==='copy')copy('“'+c.t+'”\n——'+src(c.node)).then(function(k){toast(k===false?'复制没有成功，请用手机自带的复制':'已复制，可以粘贴到微信');});
    else if(window.Q4Card)Q4Card({kind:'quote',text:c.t,src:src(c.node),col:col==='health'?'health':'qa',qrText:'阅读这一篇的全文',head:'分享这段文字'});
  });
  addEventListener('scroll',function(){if(!bar.hidden){var s=getSelection();if(s&&s.rangeCount&&!s.isCollapsed)place(s.getRangeAt(0));}},{passive:true});
})();
"""

JS = r'''
(function(){
  var de=document.documentElement;
  /* 在学课网站里用浮层打开时（iframe）：回到网站的链接交给网站处理，不重新加载整个网站 */
  if(de.classList.contains('emb'))document.addEventListener('click',function(e){
    var a=e.target.closest('a[href^="./#"],a[href="./"]');if(!a)return;
    e.preventDefault();var h=(a.getAttribute('href').split('#')[1])||'home';
    try{parent.postMessage({q4:'nav',hash:h},location.origin);}catch(err){top.location.href=a.href;}
  },true);
  function get(k){try{return localStorage.getItem('q4:'+k);}catch(e){return null;}}
  function set(k,v){try{localStorage.setItem('q4:'+k,v);}catch(e){}}
  /* 阅读进度 */
  var pb=document.querySelector('.prog i'),tick=false,pxs=document.querySelectorAll('.px i'),pcts=document.querySelectorAll('[data-pct]'),lefts=document.querySelectorAll('[data-left]'),MINS=+document.body.dataset.mins||0,lastP=-1;
  function prog(){tick=false;var h=de.scrollHeight-innerHeight,p=h>0?Math.min(1,Math.max(0,scrollY/h)):0,tx='translateX('+((p-1)*100).toFixed(2)+'%)';
    pb.style.transform=tx;for(var i=0;i<pxs.length;i++)pxs[i].style.transform=tx;
    var n=Math.round(p*100);if(n!==lastP){lastP=n;var s=n+'%';pcts.forEach(function(e){e.textContent=s;});
      var l=Math.ceil(MINS*(1-p));lefts.forEach(function(e){e.textContent=p>0.02&&l>0?'还剩约 '+l+' 分钟':(p>=0.99?'读完了':'');});}}
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
    document.querySelectorAll('.toc-l').forEach(function(l){var a=cur&&l.querySelector('a[href="#'+cur+'"]'),li=a?a.closest('.toc-l>li'):null;
      [].forEach.call(l.children,function(x){x.classList.toggle('open',x===li);});});
    var side=document.querySelector('.toc-side a.on');
    if(side){var box=side.closest('.toc-side'),r=side.getBoundingClientRect(),br=box.getBoundingClientRect();if(r.top<br.top+40||r.bottom>br.bottom-40)box.scrollTop+=r.top-br.top-br.height/2;}
  }
  var mt=false;addEventListener('scroll',function(){if(!mt){mt=true;setTimeout(function(){mt=false;mark();},120);}},{passive:true});mark();
  /* 树形目录：点“部分”展开或收起 */
  document.addEventListener('click',function(e){var tp=e.target.closest('.toc-l .tp');if(tp)tp.parentNode.classList.toggle('open');});
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
/* 上次读到哪里（2026-10-26 用户要的）：每篇记下“读到第几章、这一章读了多少”，下次打开回到那里。
   存在本机 q4:tpos（{网页: [章id, 这一章读到的比例, 时间]}）；网站登录账号后随“继续阅读”一起同步（app.js 的 tp）。
   网址带 #章 时（目录、分享的链接）不跳；读到最后（98% 以后）或回到开头时不记，下次从头读。 */
(function(){
  var de=document.documentElement,PG=(location.pathname.split('/').pop()||'').replace(/\?.*$/,'');if(!PG)return;
  function get(){try{return JSON.parse(localStorage.getItem('q4:tpos')||'{}')||{};}catch(e){return {};}}
  function put(a){try{var ks=Object.keys(a).sort(function(x,y){return a[y][2]-a[x][2];});ks.slice(60).forEach(function(k){delete a[k];});localStorage.setItem('q4:tpos',JSON.stringify(a));}catch(e){}}
  var secs=[].slice.call(document.querySelectorAll('section.ch'));if(!secs.length)return;
  function where(){var y=innerHeight*0.25,s=null;for(var i=0;i<secs.length;i++){if(secs[i].getBoundingClientRect().top<=y)s=secs[i];else break;}
    if(!s)return null;var r=s.getBoundingClientRect();return [s.id,Math.round(Math.min(1,Math.max(0,(y-r.top)/Math.max(1,r.height)))*1000)/1000];}
  var ready=false,t=null;
  function save(){if(!ready||!innerHeight)return;var h=de.scrollHeight-innerHeight;if(h<innerHeight)return;   // 在网站的浮层里被藏起来时，页面高度会塌下来：这时不记
    var p=scrollY/h,a=get(),w=where();
    if(p<0.02||p>0.98||!w){if(a[PG]&&a[PG][0]){a[PG]=['',0,Date.now()];put(a);}return;}   // 留一条空记录（带时间），别的设备同步过来的旧位置不会再“复活”
    a[PG]=[w[0],w[1],Date.now()];put(a);}
  addEventListener('scroll',function(){clearTimeout(t);t=setTimeout(save,700);},{passive:true});
  addEventListener('pagehide',save);
  document.addEventListener('visibilitychange',function(){if(document.hidden)save();});
  function tip(n,title){
    var d=document.createElement('div');d.className='rtip';d.setAttribute('role','status');
    d.innerHTML='<span>已回到上次读到的地方：第 '+n+' 章</span><button type="button">从头读</button>';
    document.body.appendChild(d);requestAnimationFrame(function(){d.classList.add('on');});
    var gone=setTimeout(hide,6000);
    function hide(){d.classList.remove('on');setTimeout(function(){d.remove();},400);}
    d.querySelector('button').addEventListener('click',function(){clearTimeout(gone);scrollTo(0,0);var a=get();a[PG]=['',0,Date.now()];put(a);hide();});
  }
  function restore(){
    var a=get(),r=a[PG];
    if(r&&r[0]&&!location.hash){var s=document.getElementById(r[0]);
      if(s){var y=s.getBoundingClientRect().top+scrollY+r[1]*s.offsetHeight-innerHeight*0.25;scrollTo(0,Math.max(0,y));
        tip(secs.indexOf(s)+1);}}
    setTimeout(function(){ready=true;},800);   // 刚跳过去时的滚动不算“读到”
  }
  if(document.readyState==='complete')setTimeout(restore,60);else addEventListener('load',function(){setTimeout(restore,60);});
  // 在网站里关掉浮层时，这一页被藏起来（高度变成 0，滚动位置也没了）；再打开同一篇时页面不重新载入：显示出来那一刻回到记下的位置
  function again(){if(scrollY>50)return;var old=document.querySelector('.rtip');if(old)old.remove();ready=false;restore();}   // 位置还在就不动
  var hid=false;addEventListener('resize',function(){if(!innerHeight){hid=true;ready=false;return;}if(hid){hid=false;again();}});
  addEventListener('message',function(e){if(e.origin===location.origin&&e.data&&e.data.q4==='shown')setTimeout(again,30);});   // 网站又把这一页显示出来（app.js）
})();

'''

if __name__ == '__main__':
    h = page()
    open(OUT, 'w', encoding='utf-8').write(h)
    print(OUT, len(h.encode()), 'bytes')
    if '--pdf' in sys.argv:          # 同时重做 PDF 学习版（内容改了就要重做）
        import topic_tools
        topic_tools.make_pdf(OUT, '研经问答03-基督教两千年家谱.pdf', '基督教两千年家谱')
