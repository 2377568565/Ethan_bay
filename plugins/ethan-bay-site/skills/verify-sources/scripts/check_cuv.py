#!/usr/bin/env python3
"""核对网页或源文件里引用的和合本经文是否逐字正确。

找出 “……”（书卷 章:节） 这样的引用，把引号里的话和 tools/q4/bible.py 的和合本比对
（忽略标点、空格；引文里的“……”当作省略，各段按顺序出现即可）。
本站惯例：称上帝、耶稣用“祂”，所以 祂/他 视为相同；象/像 是和合本版本间的异体，也视为相同。

用法（在仓库根目录）：
  Q4_WORK=<含 bible/ 的目录> python3 plugins/ethan-bay-site/skills/verify-sources/scripts/check_cuv.py jesus.html tools/q4/jesus_text.py
没有下载过圣经数据时先运行：python3 tools/q4/fetch_assets.py
"""
import html, os, re, sys

ROOT = os.getcwd()
sys.path.insert(0, os.path.join(ROOT, 'tools', 'q4'))
import bible  # noqa: E402

QUOTE = re.compile(r'“([^“”]{4,400})”\s*[（(]([^（）()]{2,40})[）)]')
PUNCT = re.compile(r'[\s，。、；：？！“”‘’（）()《》〈〉「」『』…—－\-·,.;:?!\'"]')
SAME = str.maketrans('祂她牠象', '他他他像')


def norm(s):
    return PUNCT.sub('', s).translate(SAME)


def verses(ref):
    """'约14:30' / '罗7:22-23' / '彼前1:19' → 和合本原文（连在一起）。认不出时返回 None。"""
    m = re.fullmatch(r'\s*(' + bible.BOOK_RE + r')\s*(\d.*)', ref)
    if not m:
        return None
    b = bible.NAME2IDX[m.group(1)]
    try:
        cvs = bible.parse_cv(m.group(2))
        return ''.join(bible.cuv(b, c, v) for c, v in cvs)
    except Exception:
        return None


def check(path):
    s = open(path, encoding='utf-8').read()
    if path.endswith('.html'):
        s = html.unescape(re.sub(r'<[^>]+>', '', s))
    bad = ok = skip = 0
    for m in QUOTE.finditer(s):
        q, ref = m.group(1), m.group(2)
        text = verses(ref)
        if text is None:
            skip += 1
            continue
        t, pos, good = norm(text), 0, True
        for part in filter(None, (norm(x) for x in re.split(r'……|…', q))):
            i = t.find(part, pos)
            if i < 0:
                good = False
                break
            pos = i + len(part)
        if good:
            ok += 1
        else:
            bad += 1
            print(f'✗ {path}: “{q}”（{ref}）\n    和合本：{text}')
    print(f'{path}: 正确 {ok}，不符 {bad}，不是经文出处或认不出 {skip}')
    return bad


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(1 if sum(check(p) for p in sys.argv[1:]) else 0)
