#!/usr/bin/env python3
"""“圣经”栏目的数据（2026-10-26 用户要的：整本和合本、KJV、原文，可以切换和对照，带搜索）。
输出到仓库根目录 site/bible/：
  cuv-NN-哈希.json   和合本（上帝版）第 NN 卷：[[第1章各节], [第2章各节], …]；和合本把几节印在一起时，后面的节是空字符串
  kjv-NN-哈希.json   KJV（公有领域）同样的格式
  org-NN-哈希.json   原文（STEPBible TAHOT/TAGNT，CC BY 4.0）：{"v": [[[原文, 音译, 英文直译, 词条], …每节], …每章], "x": {词条: [原形, 字义]}}
  words-哈希.json    搜索用的词语表：[[词, 拼音首字母, 全拼, 出现次数], …]（和合本分词得出，人名地名多在其中）
  index-哈希.json    文件清单（页面先读它，再按需下载各卷）
文件名带内容哈希：内容不变，文件名就不变，读者手机里存过的不用重新下载。同样的输入得到同样的输出。
用法：python3 tools/q4/biblesite.py   （需要 tools/q4/.work/bible 的数据，见 fetch_assets.py；分词用 jieba，拼音用 pypinyin）"""
import os, re, sys, json, gzip, glob, hashlib, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bible

ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
OUT = os.path.join(ROOT, 'site', 'bible')

# jieba 在部分环境装不上（要编译）；源码是纯 Python，可用 JIEBA_SRC 指到解压的源码目录
if os.environ.get('JIEBA_SRC'):
    sys.path.insert(0, os.environ['JIEBA_SRC'])
import jieba
from pypinyin import lazy_pinyin, Style
jieba.setLogLevel(60)
# 分词时会切错的几个常见人名（例如“希西家”被切成“希西 / 家”）
for w in ['希西家', '以利沙', '以利亚', '撒母耳', '约拿单', '米非波设', '尼布甲尼撒', '亚达薛西', '拿撒勒', '抹大拉', '亚利马太',
          '以马内利', '麦基洗德', '巴拿巴', '提摩太', '亚居拉', '百基拉', '亚波罗', '拉撒路', '撒该', '尼哥底母', '亚拿尼亚', '撒非喇',
          '以斯帖', '末底改', '哈曼', '波阿斯', '拿俄米', '俄巴底', '约沙法', '亚哈谢', '约阿施', '乌西雅', '约坦', '亚哈斯', '玛拿西']:
    jieba.add_word(w, 2000)


def h(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()[:10]


SZ = {}


def put(name, obj, files):
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    fn = f'{name}-{h(s)}.json'
    open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(s)
    files[name] = fn
    SZ[name] = len(s.encode())
    return SZ[name]


def clean_cuv(t):
    """和 bible.cuv() 一样整理：上帝、引号、多余空格；空的（和上一节印在一起的）保持空。"""
    t = t.strip().replace('\ue317', '讟')   # 原数据把“讟”（谤讟、怨讟，共 8 处）存成私用区字符，手机上显示成方框
    if not t:
        return ''
    if t.startswith('神') and not t.startswith('神人'):
        t = '上帝' + t[1:]
    t = re.sub('[ 　]+神', '上帝', t)
    t = t.replace('「', '“').replace('」', '”').replace('『', '‘').replace('』', '’')
    t = re.sub(r'\s+(?=[，。；：、！？”’）])', '', t)
    t = re.sub(r'\s+', '', t)          # 和合本数据里诗歌体的分行空格：阅读页按节排，不需要
    return t.replace('－', '·')         # “耶和华－你的上帝”里的连接号，排版上用间隔号


def para_ends():
    """原文里的分段记号：希腊文新约用“¶”，希伯来文旧约用“פ”（大段）、“ס”（小段），都标在一段最后一节的最后一个词上。
    返回 {卷: ["章.节", …]}，阅读页按它把和合本、KJV 分段。"""
    out = {}
    for f in bible.HEB_FILES + bible.GRK_FILES:
        for line in open(os.path.join(bible.BD, f), encoding='utf-8'):
            m = bible.LINE_RE.match(line)
            if not m:
                continue
            col = line.split('\t')
            if '¶' in col[1] or re.search(r'\\[ ]?\\?[פס]\s*$', col[1].strip()):
                b = bible.CODE2IDX.get(m.group(1))
                if b is not None:
                    out.setdefault(b, set()).add(f'{m.group(2)}.{m.group(3)}')
    return {b: sorted(v, key=lambda x: tuple(map(int, x.split('.')))) for b, v in out.items()}


def places():
    """这一节在哪里讲过：学课（合集页里的经文按钮）和问题彩蛋（专题页正文里的经文出处）。
    返回 (来源列表 [[说明, 网址]…], {"卷.章.节": [来源序号…]})。网址是网站里的地址（#l3-wed、heaven.html#city）。"""
    import html as H
    import qa_data
    src, idx, seen = [], {}, {}
    def add(key, label, href):
        k = (label, href)
        if k not in seen:
            seen[k] = len(src)
            src.append([label, href])
        lst = idx.setdefault(key, [])
        if seen[k] not in lst:
            lst.append(seen[k])
    # 学课
    DN = {'sab': '安息日', 'sun': '星期日', 'mon': '星期一', 'tue': '星期二', 'wed': '星期三', 'thu': '星期四', 'fri': '星期五', 'sum': '本课总结'}
    allp = os.path.join(ROOT, 'lessons', '2026-Q4', 'gift-of-prophecy-all.html')
    if os.path.exists(allp):
        h = open(allp, encoding='utf-8').read()
        marks = [(m.start(), m.group(1)) for m in re.finditer(r'id="(l\d+-(?:yw-)?(?:sab|sun|mon|tue|wed|thu|fri|sum|intro))"', h)]
        mi = 0
        cur = None
        for m in re.finditer(r'class="bref"[^>]*data-v="(\d+)\|([^"|]+)', h):
            while mi < len(marks) and marks[mi][0] < m.start():
                cur = marks[mi][1]
                mi += 1
            if not cur:
                continue
            n, rest = cur.split('-', 1)
            yw = rest.startswith('yw-')
            d = rest[3:] if yw else rest
            lab = ('本季导言' if n == 'l0' else f'第{n[1:]}课') + ('' if d == 'intro' else ' · ' + DN.get(d, d)) + (' · 学课原文' if yw else ' · 解读')
            b = int(m.group(1))
            for cv in m.group(2).split(';'):
                c, v = cv.split('.')
                add(f'{b}.{c}.{v}', lab, '#' + cur)
    # 问题彩蛋（独立专题页）
    for it in qa_data.ITEMS:
        if not it.get('url'):
            continue
        p = os.path.join(ROOT, it['url'])
        if not os.path.exists(p):
            continue
        h = open(p, encoding='utf-8').read()
        h = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', h).split('id="sources"')[0]
        secs = [(m.start(), m.group(1), H.unescape(re.sub(r'<[^>]+>', '', m.group(2))).strip())
                for m in re.finditer(r'<section class="ch" id="(\w+)"><h2><span class="no">\d+</span>(.*?)</h2>', h)]
        for k, (pos, sid, title) in enumerate(secs):
            end = secs[k + 1][0] if k + 1 < len(secs) else len(h)
            t = H.unescape(re.sub(r'<[^>]+>', '', h[pos:end]))
            for m in bible.CHAIN_RE.finditer(t):
                b = bible.NAME2IDX[m.group(1)]
                for part in re.split(r'[；;]', m.group(2)):
                    if not re.search(r'\d\s*[:：]', part):
                        continue
                    try:
                        cvs = bible.parse_cv(part)
                    except Exception:
                        continue
                    for c, v in cvs:
                        add(f'{b}.{c}.{v}', f'问题彩蛋 {it["no"]:02d}《{it["q"]}》· {title}', f'{it["url"]}#{sid}')
    return src, idx


# ---------- 第二期（2026-10-26）：小标题、诗行、串珠、原文中文 ----------
BD2 = os.path.join(HERE, 'bdata')        # 临时任务下载、整理过的公开数据（见 bdata_prep.py、tmp_src.py 的说明）
OB_CODES = ['Gen', 'Exod', 'Lev', 'Num', 'Deut', 'Josh', 'Judg', 'Ruth', '1Sam', '2Sam', '1Kgs', '2Kgs', '1Chr', '2Chr', 'Ezra', 'Neh', 'Esth',
            'Job', 'Ps', 'Prov', 'Eccl', 'Song', 'Isa', 'Jer', 'Lam', 'Ezek', 'Dan', 'Hos', 'Joel', 'Amos', 'Obad', 'Jonah', 'Mic', 'Nah',
            'Hab', 'Zeph', 'Hag', 'Zech', 'Mal', 'Matt', 'Mark', 'Luke', 'John', 'Acts', 'Rom', '1Cor', '2Cor', 'Gal', 'Eph', 'Phil', 'Col',
            '1Thess', '2Thess', '1Tim', '2Tim', 'Titus', 'Phlm', 'Heb', 'Jas', '1Pet', '2Pet', '1John', '2John', '3John', 'Jude', 'Rev']
HEB_LETTERS = {'ALEPH': 'א', 'BETH': 'ב', 'GIMEL': 'ג', 'DALETH': 'ד', 'HE': 'ה', 'WAW': 'ו', 'ZAYIN': 'ז', 'HETH': 'ח', 'TETH': 'ט',
               'YODH': 'י', 'KAPH': 'כ', 'LAMEDH': 'ל', 'MEM': 'מ', 'NUN': 'נ', 'SAMEKH': 'ס', 'AYIN': 'ע', 'PE': 'פ', 'TZADE': 'צ',
               'KOPH': 'ק', 'RESH': 'ר', 'SIN and SHIN': 'ש', 'TAW': 'ת'}
ROMAN = {'I': '一', 'II': '二', 'III': '三', 'IV': '四', 'V': '五'}


def en_book(name):
    n = name.strip().lower().replace('psalm ', 'psalms ').rstrip('.')
    for i, b in enumerate(bible.BOOKS):
        if b[2].lower() == n:
            return i
    return {'psalm': 18, 'song': 21, 'song of songs': 21, 'song of solomon': 21}.get(n)


def parse_refs(x):
    """BSB 小标题下的平行经文“(John 1:1–5; Hebrews 11:1–3)” → [[“约1:1-5”, 卷, 章, 节], …]"""
    out, bk = [], None
    for part in x.strip().strip('()').split(';'):
        part = part.strip().replace('—', '–')
        m = re.match(r'^((?:[1-3] )?[A-Za-z][A-Za-z ]*?)?\s*(\d+)(?::(\d+))?(?:\s*–\s*(\d+)(?::(\d+))?)?$', part)
        if not m:
            continue
        if m.group(1):
            bk = en_book(m.group(1))
        if bk is None:
            continue
        c, v = int(m.group(2)), int(m.group(3) or 0)
        lab = f'{bible.BOOKS[bk][3][0]}{c}' + (f':{v}' if v else '')
        if m.group(4):
            if m.group(5):
                lab += f'-{m.group(4)}:{m.group(5)}'
            elif v:
                lab += f'-{m.group(4)}'
            else:
                lab += f'-{m.group(4)}'
        out.append([lab, bk, c, v])
    return out


def headings():
    """小标题：位置和英文取自 BSB（Berean Standard Bible，CC0 公有领域）；中文由编者参照拟定（tools/q4/bheads/*.txt，人名地名按本站和合本的写法）。
    返回 {卷: {"章.节": [[级别, 中文, 英文, 平行经文], …]}}；级别 0＝诗篇的卷，1＝大标题，2＝小标题，3＝诗篇 119 篇的字母段。"""
    H = json.loads(gzip.open(os.path.join(BD2, 'bsbh.json.gz')).read())
    zh, order = {}, []
    for f in sorted(glob.glob(os.path.join(HERE, 'bheads', '*.txt'))):
        code = os.path.basename(f)[3:-4]
        order.append(code)
        zh[code] = [ln.rstrip('\n').split(' ', 1) for ln in open(f, encoding='utf-8') if ln.strip()]
    assert len(order) == 66
    BI = {c: i for i, c in enumerate(order)}
    out, pos, last = {}, collections.Counter(), None
    for code, c, v, t, x in H:
        b = BI[code]
        x = re.sub(r'\|strong="[^"]*"', '', x).replace('’', "'")
        x = re.sub(r'\s+', ' ', x).strip()
        key = f'{c}.{v}'
        lst = out.setdefault(b, {}).setdefault(key, [])
        if t in ('s1', 's2'):
            k, txt = zh[code][pos[code]]
            pos[code] += 1
            assert k == key + ('*' if t == 's2' else ''), (code, k, key, t)
            if txt == '-':
                last = None
                continue
            last = [1 if t == 's1' else 2, txt, x, []]
            lst.append(last)
        elif t == 'r' and last is not None and lst and lst[-1] is last:
            last[3] = parse_refs(x)
        elif t == 'ms1':
            lst.append([0, '诗篇卷' + ROMAN[x.split()[-1]], x.title(), []])
        elif t == 'mr' and lst and lst[-1][0] == 0:
            a, z = re.findall(r'\d+', x)
            lst[-1][1] += f'（第 {a}—{z} 篇）'
        elif t == 'qa':
            lst.append([3, HEB_LETTERS[x] + ' ' + x.title().replace(' And ', ' / '), x.title(), []])
    for code in order:
        assert pos[code] == len(zh[code]), code      # 中文和英文一行对一行
    return {b: {k: v for k, v in d.items() if v} for b, d in out.items()}


def poetry():
    """哪些节是诗歌（BSB 用 \\q 排成诗行的节）：{卷: {"章": [节…]}}"""
    Q = json.loads(gzip.open(os.path.join(BD2, 'bsbq.json.gz')).read())
    order = [os.path.basename(f)[3:-4] for f in sorted(glob.glob(os.path.join(HERE, 'bheads', '*.txt')))]
    BI = {c: i for i, c in enumerate(order)}
    out = {}
    for k, vs in Q.items():
        code, c = k.split('.')
        out.setdefault(BI[code], {})[c] = vs
    return out


def xrefs():
    """串珠：OpenBible.info 的公开串珠数据（CC BY，按读者投票的“相关程度”排序），只留票数 ≥ 3 的，每节最多 12 条。
    返回 {卷: {"章.节": [[卷, 章, 节, 末节或 0], …]}}"""
    OI = {c: i for i, c in enumerate(OB_CODES)}
    per = collections.defaultdict(list)
    for ln in open(os.path.join(HERE, '.work', 'b2', 'xref.txt'), encoding='utf-8'):
        a = ln.rstrip('\n').split('\t')
        if len(a) < 3 or not a[2].lstrip('-').isdigit() or int(a[2]) < 3:
            continue
        fb, fc, fv = a[0].split('.')
        to = a[1].split('-')
        tb, tc, tv = to[0].split('.')
        end = 0
        if len(to) > 1:
            eb, ec, ev = to[1].split('.')
            if eb == tb and ec == tc:
                end = int(ev)
        per[(OI[fb], int(fc), int(fv))].append((-int(a[2]), OI[tb], int(tc), int(tv), end))
    out = {}
    for (b, c, v), lst in per.items():
        lst.sort()
        out.setdefault(b, {})[f'{c}.{v}'] = [list(x[1:]) for x in lst[:12]]
    return out


def zh_fix(w):
    return w.replace('甚么', '什么').replace('彷彿', '仿佛').replace('反覆', '反复')
LEAD = ('我们的', '你们的', '他们的', '她们的', '我的', '你的', '他的', '她的', '的', '之', '就', '便', '也', '又', '都', '把', '被', '给', '在', '向', '叫', '必')
TRAIL = ('的', '了', '着', '之')


def zh_norm(w):
    """和合本里对应原文的那几个字，去掉前后的虚字（“的爱心”→“爱心”，“必得永”→“得永”），只留实义部分。"""
    w = zh_fix(w)
    for _ in range(3):
        for p in LEAD:
            if w.startswith(p) and len(w) > len(p):
                w = w[len(p):]
                break
        for p in TRAIL:
            if w.endswith(p) and len(w) > len(p):
                w = w[:-len(p)]
    return w


def sbase(s):
    m = re.match(r'([HG])0*(\d+)', s or '')
    return m.group(1) + m.group(2) if m else ''


def cuv_strong():
    """和合本带 Strong 编号的版本（ChiUns，信望爱 FHL 标注，CrossWire 发布，公有领域）：
    返回 ({"卷.章.节": {编号: [和合本字词, …按出现次序]}}, {编号: [[常见译法, 次数], …]})"""
    CU = json.loads(gzip.open(os.path.join(BD2, 'cuvs.json.gz')).read())
    per, cnt, tot = {}, collections.defaultdict(collections.Counter), collections.Counter()
    for k, toks in CU.items():
        q = {}
        for lm, w in toks:
            if not lm or not w:
                continue
            q.setdefault(lm[0], []).append(w)          # 一个字词标了几个编号时，只算第一个（后面多是前置词、宾语记号）
            n = zh_norm(w)
            if n and len(n) <= 4:
                cnt[lm[0]][n] += 1
            tot[lm[0]] += 1
        per[k] = q
    lex = {}
    for s, c in cnt.items():
        top = c.most_common(4)
        if s in NO_ZH:
            continue
        if top and top[0][1] >= max(2, 0.2 * tot[s]):       # 最常见的译法要占两成以上，才算这个词的“中文意思”
            lex[s] = [[w, n] for w, n in top if n >= 2 or n == top[0][1]]
    return per, lex
EXTRA = {'H430': '上帝', 'G2316': '上帝'}      # 本站用上帝版和合本
NO_ZH = {'H853', 'G3588'}                       # 宾语记号、冠词：中文没有对应的字


def plans(PE):
    """读经计划（按经文字数平均分配到每一天，同样的输入得到同样的计划）。
    每天是一串读经段落：[卷, 起章, 止章]（整章）或 [卷, 章, 章, 起节, 止节]（一章里的一段，按原文分段切开）。"""
    LEN = [[sum(len(clean_cuv(v)) for v in ch) for ch in bible._cuv[b]['chapters']] for b in range(66)]

    def by_chapter(books, days):
        seq = [(b, c, LEN[b][c - 1]) for b in books for c in range(1, len(LEN[b]) + 1)]
        tot, acc, out = sum(x[2] for x in seq), 0, [[] for _ in range(days)]
        for b, c, n in seq:
            d = min(days - 1, int((acc + n / 2) / tot * days))     # 按这一章的“中点”落在哪一天
            acc += n
            day = out[d]
            if day and day[-1][0] == b and len(day[-1]) == 3 and day[-1][2] == c - 1:
                day[-1][2] = c
            else:
                day.append([b, c, c])
        return out

    def by_paragraph(books, days):
        units = []
        for b in books:
            ends = set(PE.get(b, []))
            for c, ch in enumerate(bible._cuv[b]['chapters'], 1):
                v1 = 1
                for v in range(1, len(ch) + 1):
                    if f'{c}.{v}' in ends or v == len(ch):
                        units.append((b, c, v1, v, sum(len(clean_cuv(x)) for x in ch[v1 - 1:v])))
                        v1 = v + 1
        tot, acc, out = sum(u[4] for u in units), 0, [[] for _ in range(days)]
        for b, c, v1, v2, n in units:
            d = min(days - 1, int((acc + n / 2) / tot * days))
            acc += n
            day = out[d]
            if day and day[-1][0] == b and day[-1][1] == c and day[-1][4] == v1 - 1:
                day[-1][4] = v2
            else:
                day.append([b, c, c, v1, v2])
        for day in out:            # 一整章的就写成整章
            for it in day:
                if it[3] == 1 and it[4] == len(bible._cuv[it[0]]['chapters'][it[1] - 1]):
                    del it[3:]
        return out

    OT, NT = list(range(39)), list(range(39, 66))
    y2 = [a + b for a, b in zip(by_chapter(OT, 365), by_paragraph(NT, 365))]
    P = [['y1', '一年读完圣经', '按卷次序，每天约 3—4 章', by_chapter(range(66), 365)],
         ['y2', '一年读完圣经（旧约＋新约）', '每天读一段旧约、一段新约，两条线一起往前走', y2],
         ['nt90', '90 天读完新约', '每天约 3 章', by_chapter(NT, 90)],
         ['gs30', '30 天读完四福音', '马太、马可、路加、约翰，每天约 3 章', by_chapter(range(39, 43), 30)],
         ['ps30', '30 天读完诗篇', '每天约 5 篇（第 119 篇较长，单独一天）', by_chapter([18], 30)],
         ['pr31', '31 天读完箴言', '每天一章，正好一个月', [[[19, c, c]] for c in range(1, 32)]]]
    for k, n, d, days in P:
        assert all(days), k            # 每一天都要有经文
    return [{'id': k, 'n': n, 'd': d, 'days': days} for k, n, d, days in P]


def main():
    bible._load()
    os.makedirs(OUT, exist_ok=True)
    files, size = {}, collections.Counter()
    PE = para_ends()
    HD, PO, XR = headings(), poetry(), xrefs()
    CS, LEXZ = cuv_strong()
    nch = []
    for b in range(66):
        chs = bible._cuv[b]['chapters']
        nch.append(len(chs))
        size['cuv'] += put(f'cuv-{b:02d}', {'v': [[clean_cuv(v) for v in ch] for ch in chs], 'p': PE.get(b, []),
                                            'h': HD.get(b, {}), 'q': PO.get(b, {})}, files)
        size['xr'] += put(f'xr-{b:02d}', XR.get(b, {}), files)
        kj = []
        for c, ch in enumerate(chs, 1):
            row = []
            for v in range(1, len(ch) + 1):
                row.append(bible.en('K', b, c, v) or '')
            # KJV 偶尔比和合本多一节（分节不同）：补上
            extra = bible._kjv[b]['chapters'][c - 1][len(ch):] if c - 1 < len(bible._kjv[b]['chapters']) else []
            for t in extra:
                row.append(re.sub(r'\s+', ' ', re.sub(r'\{[^}]*\}', '', t)).strip())
            kj.append(row)
        size['kjv'] += put(f'kjv-{b:02d}', kj, files)
    # 原文：一次读完 STEPBible 文件，再按卷拆开
    need = {(b, c, v) for b in range(66) for c, ch in enumerate(bible._cuv[b]['chapters'], 1) for v in range(1, len(ch) + 1)}
    for b in range(66):          # KJV 多出来的节也要
        for c, ch in enumerate(bible._kjv[b]['chapters'], 1):
            for v in range(1, len(ch) + 1):
                need.add((b, c, v))
    for c in range(1, 151):        # 诗篇的标题：STEPBible 记作第 0 节（“大卫的诗”）；和合本、KJV 都印在第 1 节前面，这里接在第 1 节最前面
        need.add((18, c, 0))
    orig = bible.original(need)
    for c in range(1, 151):
        if (18, c, 0) in orig:
            orig[(18, c, 1)] = orig.pop((18, c, 0)) + orig.get((18, c, 1), [])
    for b in range(66):
        lx, chs = {}, []
        for c in range(1, nch[b] + 1):
            vs = []
            nv = max(len(bible._cuv[b]['chapters'][c - 1]), len(bible._kjv[b]['chapters'][c - 1]) if c - 1 < len(bible._kjv[b]['chapters']) else 0)
            for v in range(1, nv + 1):
                ws = []
                q = {k: list(x) for k, x in CS.get(f'{b}.{c}.{v}', {}).items()}
                cv = bible._cuv[b]['chapters'][c - 1]
                T = clean_cuv(cv[v - 1]) if v - 1 < len(cv) else ''
                for w, tr, gl, st, lem, mean in orig.get((b, c, v), []):
                    w = re.sub(r'\s+[פס]$', '', w.replace('¶', '')).strip()   # STEPBible 的分段记号（希腊文 ¶，希伯来文 פ / ס）
                    if not w:
                        continue
                    sb = sbase(st)
                    raw = q[sb].pop(0) if q.get(sb) else ''
                    if raw and raw not in T:                     # 旧版和合本的“神”，本站是“上帝”；个别字写法不同
                        for alt in (raw.replace('神', '上帝'), zh_fix(raw)):
                            if alt in T:
                                raw = alt
                                break
                    n = zh_norm(raw) if raw else ''
                    tops = [x[0] for x in LEXZ.get(sb) or []]
                    # 每个词下面写这个词的意思：这一节和合本的译法正是它常见的几种译法之一，就用这一节的（“灵”还是“风”、“上帝”还是“神”随上下文）；
                    # 否则用最常见的译法（这一节对不上、或和合本意译成长短语时）
                    if sb in NO_ZH:
                        n = ''
                    elif tops and n.replace('上帝', '神') not in [t.replace('上帝', '神') for t in tops]:
                        n = tops[0]
                    elif not tops and len(n) > 4:
                        n = ''
                    if n == '神' and sb in EXTRA and ('上帝' in raw or not raw):
                        n = '上帝'
                    ws.append([w, tr, gl, st, n] + ([raw] if raw != n else []))   # 第 6 项：这一节和合本的原样（空＝这一节没对上）
                    if st and st not in lx:
                        lx[st] = [lem, re.split('[»@]', mean)[0].strip().rstrip(':').strip(),
                                  '、'.join(EXTRA.get(sb, x[0]) if x[0] == '神' else x[0] for x in (LEXZ.get(sb) or [])[:3])]
                vs.append(ws)
            chs.append(vs)
        size['org'] += put(f'org-{b:02d}', {'v': chs, 'x': lx}, files)
    # 搜索用的词语表
    cnt = collections.Counter()
    for b in range(66):
        for ch in bible._cuv[b]['chapters']:
            for t in ch:
                for w in jieba.cut(clean_cuv(t)):
                    if 2 <= len(w) <= 6 and re.fullmatch(r'[一-鿿]+', w):
                        cnt[w] += 1
    words = []
    for w, n in cnt.items():
        # 去掉“希伯仑见”“希伯仑王”这类带了半截的：较短的前一部分本身是常见的词，而且多出来的不是“人、族”
        bad = any(w[:k] in cnt and cnt[w[:k]] >= 2 * n and w[k:] not in ('人', '族', '人的')
                  for k in range(2, len(w)))
        if bad:
            continue
        py = lazy_pinyin(w)
        words.append([w, ''.join(p[0] for p in py), ''.join(py), n])
    words.sort(key=lambda x: (-x[3], x[0]))
    size['words'] += put('words', words, files)
    size['plans'] += put('plans', plans(PE), files)
    ps, pi = places()
    size['places'] += put('places', {'s': ps, 'v': pi}, files)
    # 书卷：名称、简称、拼音
    books = []
    for i, (code, full, en, ab) in enumerate(bible.BOOKS):
        py = lazy_pinyin(full)
        books.append([full, ab, en, code, ''.join(p[0] for p in py), ''.join(py), nch[i]])
    idx = {'books': books, 'files': files, 'sz': SZ}     # sz：每个文件的大小（“下载到手机”显示用）
    s = json.dumps(idx, ensure_ascii=False, separators=(',', ':'))
    fn = f'index-{h(s)}.json'
    open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(s)
    # 旧文件留一代（微信会缓存旧网页，旧网页还会去找旧数据）：保留这次的和上一次 current.txt 指向的，其余旧的删掉
    keep = {fn, *files.values()}
    cur = os.path.join(OUT, 'current.txt')
    if os.path.exists(cur):
        prev = open(cur, encoding='utf-8').read().strip()
        if os.path.exists(os.path.join(OUT, prev)):
            keep |= {prev, *json.load(open(os.path.join(OUT, prev), encoding='utf-8'))['files'].values()}
    for f in glob.glob(os.path.join(OUT, '*.json')):
        if os.path.basename(f) not in keep:
            os.remove(f)
    open(cur, 'w', encoding='utf-8').write(fn + '\n')
    print('index', fn, {k: f'{v / 1e6:.1f} MB' for k, v in size.items()}, len(words), '个词')
    return fn


if __name__ == '__main__':
    main()
