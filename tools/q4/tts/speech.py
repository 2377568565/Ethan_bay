#!/usr/bin/env python3
"""朗读稿：从生成好的合集页里取出每个“朗读单位”（原文每天、解读每天、问答文章）的段落，
整理成适合语音合成的文字，写到 tts/script.json。

分段规则和网页里的朗读/继续阅读一致（app.js 的 BLK / SKIP），所以第 i 段的声音对应网页第 i 段，
播放时能逐段高亮。每段带一个“指纹”（开头几个字），网页核对后才高亮，防止对不上。

用法：python3 tools/q4/tts/speech.py        （先用 render.py 生成网页）
"""
import html, json, os, re, sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
Q4 = os.path.dirname(HERE)
ROOT = os.path.normpath(os.path.join(Q4, '..', '..'))
PAGE = os.path.join(ROOT, 'lessons', '2026-Q4', 'gift-of-prophecy-all.html')
OUT = os.path.join(HERE, 'script.json')
sys.path.insert(0, Q4)
import bible  # noqa: E402  书卷名表与经文出处的正则

BLK = {'h1', 'h2', 'h3', 'p', 'li', 'blockquote', 'td'}
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr'}


class Node:
    __slots__ = ('tag', 'attrs', 'kids', 'parent')

    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.kids, self.parent = tag, attrs, [], parent

    @property
    def cls(self):
        return (self.attrs.get('class') or '').split()

    def text(self):
        return ''.join(k if isinstance(k, str) else k.text() for k in self.kids)

    def walk(self):
        for k in self.kids:
            if isinstance(k, Node):
                yield k
                yield from k.walk()

    def up(self):
        n = self
        while n is not None:
            yield n
            n = n.parent


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node('#root', {}, None)
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        n = Node(tag, dict(attrs), self.cur)
        self.cur.kids.append(n)
        if tag not in VOID:
            self.cur = n

    def handle_startendtag(self, tag, attrs):
        self.cur.kids.append(Node(tag, dict(attrs), self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, d):
        self.cur.kids.append(d)


# 和 app.js 的 SKIP 一致：.lessonbar,.nav,.ckin,.dsc,.my,.btnrow,.qshare,nav,footer,.askpage,.vpool,.cover .from,.when,.yqlink,script,style
SKIP_CLS = {'lessonbar', 'nav', 'ckin', 'dsc', 'my', 'btnrow', 'qshare', 'askpage', 'vpool', 'when', 'yqlink'}
SKIP_TAG = {'nav', 'footer', 'script', 'style'}


def skipped(n):
    for a in n.up():
        if a.tag in SKIP_TAG or SKIP_CLS & set(a.cls):
            return True
        if 'from' in a.cls and any('cover' in b.cls for b in a.up()):
            return True
    return False


def blocks(root):
    out = []
    for n in root.walk():
        if n.tag not in BLK or skipped(n):
            continue
        if n.tag != 'p' and any(d.tag in ('p', 'li') for d in n.walk()):
            continue
        out.append(n)
    return out


def ws(s):
    return re.sub(r'\s+', ' ', s).strip()


# ---------- 读法 ----------
DIG = '零一二三四五六七八九'


def num(n):
    """普通数字读法：27 → 二十七，104 → 一百零四"""
    n = int(n)
    if n < 10:
        return DIG[n]
    if n < 20:
        return '十' + (DIG[n % 10] if n % 10 else '')
    if n < 100:
        return DIG[n // 10] + '十' + (DIG[n % 10] if n % 10 else '')
    if n < 1000:
        h, r = divmod(n, 100)
        if not r:
            return DIG[h] + '百'
        return DIG[h] + '百' + ('零' + DIG[r] if r < 10 else (DIG[r // 10] + '十' + (DIG[r % 10] if r % 10 else '')))
    if n < 10000:
        t, r = divmod(n, 1000)
        if not r:
            return DIG[t] + '千'
        return DIG[t] + '千' + ('零' + num(r) if r < 100 else num(r))
    return ''.join(DIG[int(c)] for c in str(n))


def dec(x):
    """99.5 → 九十九点五"""
    i, _, f = x.partition('.')
    return num(i) + ('点' + ''.join(DIG[int(c)] for c in f) if f else '')


def verses(rest):
    """'1、2' → 一、二节；'14-24' → 十四到二十四节；'26-2:3'（跨章）在 cv() 里处理"""
    parts = []
    for p in re.split(r'[、，,]', rest):
        m = re.fullmatch(r'(\d+)(?:[-–—~](\d+))?', p)
        if not m:
            return None
        parts.append(num(m[1]) + ('到' + num(m[2]) if m[2] else ''))
    return '、'.join(parts) + '节'


def cv(s):
    """'15：11-32' → 十五章十一到三十二节；'1：26-2：3' → 一章二十六节到二章三节；'23' → 二十三章"""
    s = re.sub(r'[ 　]', '', s).replace('：', ':')
    m = re.fullmatch(r'(\d+):(\d+)[-–—~](\d+):(\d+)', s)
    if m:
        return f'{num(m[1])}章{num(m[2])}节到{num(m[3])}章{num(m[4])}节'
    if ':' not in s:
        return num(s) + '章' if s.isdigit() else None
    c, rest = s.split(':', 1)
    v = verses(rest)
    return f'{num(c)}章{v}' if v and c.isdigit() else None


def chain(book, body):
    """'1：27、28；2：15-18' 这样同一卷书的几处 → 一章二十七、二十八节；二章十五到十八节"""
    out = []
    for piece in re.split(r'[；;]', body):
        piece = piece.strip(' ，,')
        if not piece:
            continue
        r = cv(piece)
        if r is None:
            return None
        out.append(r)
    return (book or '') + '，'.join(out) if out else None


BOOK_SAY = {name: bible.BOOKS[i][1] for name, i in bible.NAME2IDX.items()}
BOOK_SAY.update({'约一': '约翰一书', '约二': '约翰二书', '约三': '约翰三书'})
REF_RE = re.compile(r'(' + bible.BOOK_RE + r')?[ 　]*(\d+[ 　]*[:：][ 　]*[\d、，,\-–—~:：；; 　]*\d)')


def refs(t):
    def rep(m):
        book = BOOK_SAY.get(m[1], m[1]) if m[1] else ''
        r = chain(book, m[2])
        return r if r else m[0]
    return REF_RE.sub(rep, t)


def years(t):
    # 1844年 → 一八四四年；其余四位数照普通数字读
    t = re.sub(r'(\d{4})(?=年)', lambda m: ''.join(DIG[int(c)] for c in m[1]), t)
    t = re.sub(r'(\d{4})(?=[—–\-~至到])', lambda m: ''.join(DIG[int(c)] for c in m[1]), t)
    return t


def say(text):
    t = text
    t = re.sub(r'https?[:：]//[\w./\-]+', '怀爱伦著作网站', t)
    t = re.sub(r'看参考解答\s*→?', '', t)
    t = re.sub(r'(学课原题)?\s*↩\s*回到原文问题', '', t)
    t = re.sub(r'[\u0590-\u05FF\uFB1D-\uFB4F\u0370-\u03FF\u1F00-\u1FFF]+', '', t)   # 希伯来文、希腊文不读（括号里的拼音和中文意思照读）
    t = re.sub(r'(\d+(?:\.\d+)?)\s*[%％]', lambda m: '百分之' + dec(m[1]), t)
    t = re.sub(r'^(\d{1,2})[.、]\s*', lambda m: '第' + num(m[1]) + '，', t)
    t = refs(t)
    t = years(t)
    t = re.sub(r'第(\d+)', lambda m: '第' + num(m[1]), t)
    t = re.sub(r'(?<![\d.])(\d{1,4})(?![\d.])', lambda m: num(m[1]), t)
    t = t.replace('─', '，').replace('—', '，').replace('…', '……')
    t = re.sub(r'[→↔✦■❚▶◀]', ' ', t)
    t = re.sub(r'[❶➊①]', '第一，', t)
    t = re.sub(r'[❷➋②]', '第二，', t)
    t = re.sub(r'[❸➌③]', '第三，', t)
    t = re.sub(r'[❹➍④]', '第四，', t)
    t = re.sub(r'[❺➎⑤]', '第五，', t)
    t = re.sub(r'[❻➏⑥]', '第六，', t)
    t = re.sub(r'[❼➐⑦]', '第七，', t)
    t = t.replace('－', '—').replace('／', '/').replace('〔', '（').replace('〕', '）')
    t = t.replace('〈', '《').replace('〉', '》').replace('‧', '·')
    t = t.replace('↩', '')
    t = re.sub(r'（[\s，、；]*', '（', t)
    t = re.sub(r'[\s，、；]*）', '）', t)
    t = re.sub(r'（\s*）|\(\s*\)', '', t)
    if not re.search(r'[\u4e00-\u9fffA-Za-z]', t):
        return ''
    t = re.sub(r'\s+', ' ', t).strip(' ，')
    return t


def fingerprint(t):
    return re.sub(r'\s+', '', t)[:12]


def units(tree):
    for L in tree.root.walk():
        if 'lesson' not in L.cls or not L.attrs.get('id'):
            continue
        lid = L.attrs['id']
        if lid in ('ask', 'home', 'qa'):
            continue
        for s in L.walk():
            c = s.cls
            if s.tag == 'article' and 'ywday' in c and s.attrs.get('id'):
                yield s.attrs['id'], 'yw', s
            elif s.tag == 'section' and 'day' in c and s.attrs.get('id'):
                yield s.attrs['id'], 'jd', s
            elif s.tag == 'article' and 'qna' in c:
                yield s.attrs.get('id') or lid, 'qa', s


def main():
    tree = Tree()
    tree.feed(open(PAGE, encoding='utf-8').read())
    out = []
    for uid, kind, sec in units(tree):
        bl = []
        for b in blocks(sec):
            raw = ws(b.text())
            if not raw:
                bl.append({'fp': '', 'say': ''})
                continue
            bl.append({'fp': fingerprint(raw), 'say': say(raw)})
        out.append({'id': uid, 'kind': kind, 'blocks': bl})
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=0)
    n = {k: sum(1 for u in out if u['kind'] == k) for k in ('yw', 'jd', 'qa')}
    ch = {k: sum(len(b['say']) for u in out if u['kind'] == k for b in u['blocks']) for k in ('yw', 'jd', 'qa')}
    print(f'朗读稿：原文 {n["yw"]} 天（{ch["yw"]} 字），解读 {n["jd"]} 段（{ch["jd"]} 字），问答 {n["qa"]} 篇（{ch["qa"]} 字）→ {os.path.relpath(OUT, ROOT)}')


if __name__ == '__main__':
    main()
