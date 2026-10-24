# 问题彩蛋的“目录”数据：每篇的阅读时间、章数、图数，以及经文索引（2026-10-23 分类改版）。
# 都从已经生成好的网页里读出来（同样的网页得到同样的结果），所以要先生成各专题页，再生成首页。
import os, re, html
import bible, qa_data

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
Q4 = os.path.dirname(os.path.abspath(__file__))


def _page(it):
    if it.get('url'):
        p = os.path.join(ROOT, it['url'])
    else:
        p = os.path.join(Q4, 'qa', it['src'])
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''


def _main_text(h):
    """只取正文（不含资料出处、页脚、脚本），去掉标签。"""
    h = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', h)
    h = h.split('id="sources"')[0]
    return html.unescape(re.sub(r'<[^>]+>', '', h))


def meta(it):
    """{'mins': 分钟, 'chs': 章数, 'figs': 图数}；短文没有“章”。"""
    h = _page(it)
    m = re.search(r'细读约 (\d+) 分钟 · (\d+) 章', h)
    figs = len(re.findall(r'<svg[^>]*class="dg"', h))
    if m:
        return {'mins': int(m.group(1)), 'chs': int(m.group(2)), 'figs': figs}
    words = len(re.sub(r'\s', '', _main_text(h)))
    return {'mins': max(5, round(words / 450 / 5) * 5), 'chs': 0, 'figs': figs}


# ---------- 经文索引 ----------
_ALIAS = {}
for i, (code, full, en, al) in enumerate(bible.BOOKS):
    _ALIAS[full] = i
    for a in al:
        _ALIAS[a] = i
_NAMES = sorted(_ALIAS, key=len, reverse=True)
_BOOK = re.compile('(' + '|'.join(map(re.escape, _NAMES)) + r')\s*(\d+)\s*[:：]\s*\d')
_CONT = re.compile(r'[；;]\s*(\d+)\s*[:：]\s*\d')


def refs(it):
    """这一篇正文里引用过的 (书卷序号, 章)。括号里“罗3:25；5:8”这种续写的章也算。"""
    t = _main_text(_page(it))
    out = set()
    for m in _BOOK.finditer(t):
        b = _ALIAS[m.group(1)]
        c = int(m.group(2))
        if c <= len(bible._cuv[b]['chapters']) if bible._cuv else True:
            out.add((b, c))
        # 同一个括号里接着写的“；12:13”
        tail = t[m.end():m.end() + 80]
        stop = re.search(r'[）)」”]', tail)
        seg = tail[:stop.start()] if stop else tail
        for n in _CONT.finditer(seg):
            if not re.search('(' + '|'.join(map(re.escape, _NAMES)) + r')', seg[:n.start()]):
                out.add((b, int(n.group(1))))
    return out


def scripture_index():
    """[(书卷序号, 书名, [(章, [彩蛋 id…])…])…]，按圣经书卷顺序。"""
    bible._load()
    idx = {}
    for it in qa_data.ITEMS:
        for b, c in refs(it):
            if 1 <= c <= len(bible._cuv[b]['chapters']):
                idx.setdefault(b, {}).setdefault(c, []).append(it['id'])
    order = {it['id']: k for k, it in enumerate(qa_data.ITEMS)}
    res = []
    for b in sorted(idx):
        chs = [(c, sorted(set(ids), key=lambda x: order[x])) for c, ids in sorted(idx[b].items())]
        res.append((b, bible.BOOKS[b][1], chs))
    return res


if __name__ == '__main__':
    for it in qa_data.ITEMS:
        print(it['no'], it['id'], meta(it), len(refs(it)))
    si = scripture_index()
    print(len(si), '卷', sum(len(c) for _, _, c in si), '章')
