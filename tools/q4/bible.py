"""经文识别与经文数据：把正文里的经文出处变成可点击的按钮，并生成和合本 / NKJV / 原文逐字数据。"""
import re, json, os, html, unicodedata

import os
S = os.environ.get('Q4_WORK') or os.path.join(os.path.dirname(os.path.abspath(__file__)), '.work')   # 字体与圣经数据：python3 tools/q4/fetch_assets.py 会下载到这里
BD = os.path.join(S, 'bible')
Q4 = os.path.dirname(os.path.abspath(__file__))

# (STEP 代码, 中文全名, 英文名, [中文简称...])
BOOKS = [
 ('Gen','创世记','Genesis',['创']),('Exo','出埃及记','Exodus',['出']),('Lev','利未记','Leviticus',['利']),
 ('Num','民数记','Numbers',['民']),('Deu','申命记','Deuteronomy',['申']),('Jos','约书亚记','Joshua',['书']),
 ('Jdg','士师记','Judges',['士']),('Rut','路得记','Ruth',['得']),('1Sa','撒母耳记上','1 Samuel',['撒上']),
 ('2Sa','撒母耳记下','2 Samuel',['撒下']),('1Ki','列王纪上','1 Kings',['王上']),('2Ki','列王纪下','2 Kings',['王下']),
 ('1Ch','历代志上','1 Chronicles',['代上']),('2Ch','历代志下','2 Chronicles',['代下']),('Ezr','以斯拉记','Ezra',['拉']),
 ('Neh','尼希米记','Nehemiah',['尼']),('Est','以斯帖记','Esther',['斯']),('Job','约伯记','Job',['伯']),
 ('Psa','诗篇','Psalms',['诗']),('Pro','箴言','Proverbs',['箴']),('Ecc','传道书','Ecclesiastes',['传']),
 ('Sng','雅歌','Song of Solomon',['歌']),('Isa','以赛亚书','Isaiah',['赛']),('Jer','耶利米书','Jeremiah',['耶']),
 ('Lam','耶利米哀歌','Lamentations',['哀']),('Ezk','以西结书','Ezekiel',['结']),('Dan','但以理书','Daniel',['但']),
 ('Hos','何西阿书','Hosea',['何']),('Jol','约珥书','Joel',['珥']),('Amo','阿摩司书','Amos',['摩']),
 ('Oba','俄巴底亚书','Obadiah',['俄']),('Jon','约拿书','Jonah',['拿']),('Mic','弥迦书','Micah',['弥']),
 ('Nam','那鸿书','Nahum',['鸿']),('Hab','哈巴谷书','Habakkuk',['哈']),('Zep','西番雅书','Zephaniah',['番']),
 ('Hag','哈该书','Haggai',['该']),('Zec','撒迦利亚书','Zechariah',['亚']),('Mal','玛拉基书','Malachi',['玛']),
 ('Mat','马太福音','Matthew',['太']),('Mrk','马可福音','Mark',['可']),('Luk','路加福音','Luke',['路']),
 ('Jhn','约翰福音','John',['约']),('Act','使徒行传','Acts',['徒']),('Rom','罗马书','Romans',['罗']),
 ('1Co','哥林多前书','1 Corinthians',['林前']),('2Co','哥林多后书','2 Corinthians',['林后']),
 ('Gal','加拉太书','Galatians',['加']),('Eph','以弗所书','Ephesians',['弗']),('Php','腓立比书','Philippians',['腓']),
 ('Col','歌罗西书','Colossians',['西']),('1Th','帖撒罗尼迦前书','1 Thessalonians',['帖前']),
 ('2Th','帖撒罗尼迦后书','2 Thessalonians',['帖后']),('1Ti','提摩太前书','1 Timothy',['提前']),
 ('2Ti','提摩太后书','2 Timothy',['提后']),('Tit','提多书','Titus',['多']),('Phm','腓利门书','Philemon',['门']),
 ('Heb','希伯来书','Hebrews',['来']),('Jas','雅各书','James',['雅']),('1Pe','彼得前书','1 Peter',['彼前']),
 ('2Pe','彼得后书','2 Peter',['彼后']),('1Jn','约翰一书','1 John',['约一','约壹']),('2Jn','约翰二书','2 John',['约二','约贰']),
 ('3Jn','约翰三书','3 John',['约三','约叁']),('Jud','犹大书','Jude',['犹']),('Rev','启示录','Revelation',['启']),
]
NAME2IDX = {}
for i, (_, full, _, ab) in enumerate(BOOKS):
    NAME2IDX[full] = i
    for a in ab: NAME2IDX[a] = i
NAME2IDX['诗'] = 18
_names = sorted(NAME2IDX, key=len, reverse=True)
BOOK_RE = '(?:' + '|'.join(map(re.escape, _names)) + ')'
SP = r'[ 　]*'
COLON = r'[:：]'
V = r'\d+(?:' + SP + r'[-–—~]' + SP + r'\d+(?:' + COLON + r'\d+)?)?'
VLIST = V + r'(?:' + SP + r'[、，,]' + SP + r'(?=\d)(?!\d+' + SP + COLON + r')' + V + r')*'
CV = r'\d+' + SP + COLON + SP + VLIST
SEP = SP + r'[；;，,]' + SP + r'(?=\d+' + SP + COLON + r')'
CHAIN_RE = re.compile(r'(' + BOOK_RE + r')' + SP + r'(' + CV + r'(?:' + SEP + CV + r')*)')
BARE_RE = re.compile(r'(?<![\d:：])(' + CV + r'(?:' + SEP + CV + r')*)')
CV_RE = re.compile(CV)
MAXV = 16

def parse_cv(s):
    """'2:15-17' / '18:21，38、39' / '24:29-25:2' → [(章, 节), ...]（最多 MAXV 节）"""
    s = re.sub(SP, '', s).replace('：', ':')
    ch, rest = s.split(':', 1)
    ch = int(ch); out = []
    for part in re.split(r'[、，,]', rest):
        m = re.fullmatch(r'(\d+)(?:[-–—~](\d+)(?::(\d+))?)?', part)
        if not m: continue
        a = int(m.group(1))
        if m.group(3):                     # 跨章：24:29-25:2
            b_ch, b_v = int(m.group(2)), int(m.group(3))
            for c in range(ch, b_ch + 1):
                lo = a if c == ch else 1
                hi = b_v if c == b_ch else 200
                for v in range(lo, hi + 1): out.append((c, v))
        elif m.group(2):
            for v in range(a, int(m.group(2)) + 1): out.append((ch, v))
        else:
            out.append((ch, a))
    return out

class Linker:
    """在 HTML 文本节点里找经文出处，包成 <span class="bref">；记住上一次出现的书卷，以便处理“（2:16、17）”这类省略书名的出处。"""
    def __init__(self):
        self.last = None
        self.refs = []          # [(book, [(c,v)...])]

    def _wrap(self, book, text, cvs):
        verses = []
        for c, v in cvs:
            if (c, v) not in verses: verses.append((c, v))
        verses = [x for x in verses if exists(book, *x)]
        if not verses: return html.escape(text, quote=False) if False else text
        full = len(verses) > MAXV
        verses = verses[:MAXV]
        self.refs.append((book, verses))
        code = f'{book}|' + ';'.join(f'{c}.{v}' for c, v in verses) + ('|+' if full else '')
        return f'<span class="bref" role="button" tabindex="0" data-v="{code}">{text}</span>'

    def _chain(self, book, body, prefix=''):
        out = prefix; pos = 0
        for m in CV_RE.finditer(body):
            out += body[pos:m.start()]
            seg = m.group(0)
            out += self._wrap(book, (prefix and '') + seg, parse_cv(seg))
            pos = m.end()
        return out + body[pos:]

    def text(self, t, in_ref):
        res = []; pos = 0
        for m in CHAIN_RE.finditer(t):
            res.append(self._bare(t[pos:m.start()], in_ref))
            book = NAME2IDX[m.group(1)]; self.last = book
            body = m.group(2)
            cvs = list(CV_RE.finditer(body))
            first = cvs[0]
            # 书名和第一个“章:节”一起作为一个按钮
            chunk = self._wrap(book, m.group(0)[:len(m.group(0)) - len(body)] + body[:first.end()], parse_cv(first.group(0)))
            rest = body[first.end():]
            chunk += self._chain(book, rest)
            res.append(chunk); pos = m.end()
        res.append(self._bare(t[pos:], in_ref))
        return ''.join(res)

    def _bare(self, t, in_ref):
        if not in_ref or self.last is None or not t: return t
        out = []; pos = 0
        for m in BARE_RE.finditer(t):
            out.append(t[pos:m.start()]); out.append(self._chain(self.last, m.group(1))); pos = m.end()
        out.append(t[pos:])
        return ''.join(out)

    def html(self, h):
        parts = re.split(r'(<[^>]+>)', h)
        out = []; stack = []
        for p in parts:
            if p.startswith('<'):
                tag = re.match(r'</?([a-zA-Z0-9]+)', p)
                if tag:
                    name = tag.group(1).lower()
                    if p.startswith('</'):
                        if stack and stack[-1][0] == name: stack.pop()
                    elif not p.endswith('/>') and name not in ('br', 'img', 'input', 'meta', 'link', 'hr'):
                        stack.append((name, 'class="ref"' in p or 'class="r"' in p))
                out.append(p); continue
            skip = any(n in ('a', 'script', 'style', 'textarea', 'button', 'title', 'h1') for n, _ in stack) or \
                   any(n == 'span' and 'bref' in n for n, _ in stack)
            if skip or not p.strip():
                out.append(p); continue
            in_ref = any(r for _, r in stack)
            out.append(self.text(p, in_ref))
        return ''.join(out)

# ---------- 数据 ----------
_cuv = _kjv = _nkjv = None
def _load():
    global _cuv, _kjv, _nkjv
    if _cuv is None:
        _cuv = json.load(open(os.path.join(BD, 'zh_cun.json'), encoding='utf-8-sig'))
        _kjv = json.load(open(os.path.join(BD, 'en_kjv.json'), encoding='utf-8-sig'))
        _nkjv = json.load(open(os.path.join(BD, 'en_nkjv.json'), encoding='utf-8-sig'))

def exists(b, c, v):
    _load()
    ch = _cuv[b]['chapters']
    return 1 <= c <= len(ch) and 1 <= v <= len(ch[c - 1])

def cuv(b, c, v):
    _load()
    t = _cuv[b]['chapters'][c - 1][v - 1]
    t = t.strip()
    if t.startswith('神') and not t.startswith('神人'): t = '上帝' + t[1:]   # 句首空格在抓取时丢失
    t = re.sub('[ \u3000]+神', '上帝', t)
    t = t.replace('「', '“').replace('」', '”').replace('『', '‘').replace('』', '’')
    return t.strip()

def en(which, b, c, v):
    _load()
    d = _nkjv if which == 'N' else _kjv
    try:
        t = d[b]['chapters'][c - 1][v - 1]
    except IndexError:
        return None
    t = re.sub(r'\{[^}]*\}', '', t)
    return re.sub(r'\s+', ' ', t).strip()

# ---------- 原文（STEPBible TAHOT / TAGNT，CC BY 4.0） ----------
HEB_FILES = ['TAHOT_Gen-Deu.txt', 'TAHOT_Jos-Est.txt', 'TAHOT_Job-Sng.txt', 'TAHOT_Isa-Mal.txt']
GRK_FILES = ['TAGNT_Mat-Jhn.txt', 'TAGNT_Act-Rev.txt']
LINE_RE = re.compile(r'^(\w+)\.(\d+)\.(\d+)(?:\([\d.]+\))?#(\d+)=(\S+)\t')
CODE2IDX = {b[0]: i for i, b in enumerate(BOOKS)}

def _heb_clean(w):
    w = unicodedata.normalize('NFC', w)
    w = ''.join(ch for ch in w if not ('\u0591' <= ch <= '\u05AF' or ch in '\u05BD\u05C0'))
    return w.replace('/', '').replace('\\', '')

def _tr(t):
    return t.replace('/', '').replace('\\', '').replace('.', '').lower()

def _gloss(g):
    g = re.sub(r'/\s*', ' ', g).replace('<obj.>', '[obj]').replace('\\', ' ')
    return re.sub(r'\s+', ' ', g).strip()

def original(needed):
    """needed: set of (book, c, v) → {(b,c,v): [(原文, 音译, 英文直译, 词条编号, 词条原形, 词条义)]}"""
    want = {}
    for b, c, v in needed: want[(BOOKS[b][0], c, v)] = (b, c, v)
    res = {}; seen = set()
    for f in HEB_FILES + GRK_FILES:
        grk = f.startswith('TAGNT')
        for line in open(os.path.join(BD, f), encoding='utf-8'):
            m = LINE_RE.match(line)
            if not m: continue
            key = (m.group(1), int(m.group(2)), int(m.group(3)))
            if key not in want: continue
            typ = m.group(5); col = line.rstrip('\n').split('\t')
            wid = (key, m.group(4))
            if grk:
                if 'K' not in typ.upper(): continue
                if wid in seen: continue
                gm = re.match(r'(.*?)\s*\((.*)\)', col[1])
                word, tr = (gm.group(1), gm.group(2)) if gm else (col[1], '')
                strong = col[3].split('=')[0]
                lem, _, mean = col[4].partition('=')
                ent = (unicodedata.normalize('NFC', word), tr, _gloss(col[2]), strong, lem, mean)
            else:
                if typ.startswith('K') and not typ.startswith('KQ'): continue
                if wid in seen: continue
                root = col[8].strip() if len(col) > 8 else ''
                exp = col[-1] if col[-1].strip() else (col[-2] if len(col) > 1 else '')
                mm = re.search(r'\{(H\d+\w?)=([^=]*)=([^}]*)\}', line)
                strong = root or (mm.group(1) if mm else '')
                lem = mm.group(2) if mm else ''; mean = mm.group(3) if mm else ''
                ent = (_heb_clean(col[1]), _tr(col[2]), _gloss(col[3]), strong, _heb_clean(lem), mean)
            seen.add(wid)
            res.setdefault(want[key], []).append(ent)
    return res

# ---------- 打包给页面 ----------
NKJV_LIMIT = 1000     # Thomas Nelson 允许在不另行申请许可的情况下引用至多 1000 节 NKJV
def nkjv_choice(refs):
    """按“被引用的分量”挑出最多 1000 节用 NKJV，其余用 KJV（公有领域）。"""
    score = {}
    for b, vs in refs:
        for c, v in vs: score[(b, c, v)] = score.get((b, c, v), 0) + 1 / len(vs)
    ranked = sorted(score, key=lambda k: (-score[k], k))
    return set(ranked[:NKJV_LIMIT])

ZHLIT = json.load(open(os.path.join(Q4, 'zhlit', 'zhlit.json'), encoding='utf-8'))   # 中文直译（按原文逐字释义译出）
_orig_cache = None
def payload(refs, nkjv_ok):
    global _orig_cache
    need = sorted({(b, c, v) for b, vs in refs for c, v in vs})
    if _orig_cache is None: _orig_cache = {}
    miss = [k for k in need if k not in _orig_cache]
    if miss: _orig_cache.update(original(set(miss)))
    V = {}; LX = {}
    for b, c, v in need:
        use_n = (b, c, v) in nkjv_ok
        e = en('N' if use_n else 'K', b, c, v) or en('K', b, c, v) or ''
        words = []
        for w, tr, gl, st, lem, mean in _orig_cache.get((b, c, v), []):
            words.append([w, tr, gl, st])
            if st and st not in LX: LX[st] = [lem, re.split('[»@]', mean)[0].strip().rstrip(':').strip()]
        V[f'{b}.{c}.{v}'] = [cuv(b, c, v), e, 'N' if use_n else 'K', words, ZHLIT.get(f'{b}.{c}.{v}', '')]
    books = [[b[1], b[2], 1 if i < 39 else 0] for i, b in enumerate(BOOKS)]
    return json.dumps({'b': books, 'v': V, 'x': LX}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
