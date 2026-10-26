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
import os, re, sys, json, glob, hashlib, collections
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


def put(name, obj, files):
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    fn = f'{name}-{h(s)}.json'
    open(os.path.join(OUT, fn), 'w', encoding='utf-8').write(s)
    files[name] = fn
    return len(s.encode())


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


def main():
    bible._load()
    os.makedirs(OUT, exist_ok=True)
    files, size = {}, collections.Counter()
    PE = para_ends()
    nch = []
    for b in range(66):
        chs = bible._cuv[b]['chapters']
        nch.append(len(chs))
        size['cuv'] += put(f'cuv-{b:02d}', {'v': [[clean_cuv(v) for v in ch] for ch in chs], 'p': PE.get(b, [])}, files)
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
                for w, tr, gl, st, lem, mean in orig.get((b, c, v), []):
                    w = re.sub(r'\s+[פס]$', '', w.replace('¶', '')).strip()   # STEPBible 的分段记号（希腊文 ¶，希伯来文 פ / ס）
                    if not w:
                        continue
                    ws.append([w, tr, gl, st])
                    if st and st not in lx:
                        lx[st] = [lem, re.split('[»@]', mean)[0].strip().rstrip(':').strip()]
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
    ps, pi = places()
    size['places'] += put('places', {'s': ps, 'v': pi}, files)
    # 书卷：名称、简称、拼音
    books = []
    for i, (code, full, en, ab) in enumerate(bible.BOOKS):
        py = lazy_pinyin(full)
        books.append([full, ab, en, code, ''.join(p[0] for p in py), ''.join(py), nch[i]])
    idx = {'books': books, 'files': files}
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
