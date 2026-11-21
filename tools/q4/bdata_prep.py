#!/usr/bin/env python3
"""圣经第二期：把临时任务下载的 ChiUns（和合本简体，带 Strong 编号，CrossWire / 信望爱 FHL，公有领域）整理成
tools/q4/bdata/cuvs.json.gz：{"卷序.章.节": [[编号列表, 和合本的字词], ...]}（卷序从 0 算，NRSV 分节≈英文分节）。
只需运行一次（要 pysword 源码：pip download --no-binary :all: pysword，解压后用 PYSWORD=解压目录 运行）。"""
import os, re, sys, json, gzip, zipfile, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.environ.get('PYSWORD', ''))
from pysword.modules import SwordModules

d = tempfile.mkdtemp()
zipfile.ZipFile(os.path.join(HERE, 'bdata', 'ChiUns.zip')).extractall(d)
mods = SwordModules(d)
mods.parse_modules()
bible = mods.get_bible_from_module('ChiUns')
st = bible.get_structure().get_books()
books = st['ot'] + st['nt']
assert len(books) == 66
out = {}
for bi, bk in enumerate(books):
    for ci, nv in enumerate(bk.chapter_lengths):
        for vi in range(nv):
            raw = bible.get(books=[bk.name], chapters=[ci + 1], verses=[vi + 1], clean=False)
            toks = []
            for m in re.finditer(r'<w\b([^>]*)>(.*?)</w>|([^<]+)|<[^>]+>', raw):
                if m.group(3) is not None:
                    t = re.sub(r'\s+', '', m.group(3))
                    if t: toks.append([[], t])
                    continue
                if m.group(1) is None:
                    continue
                lm = [s[0] + str(int(s[1:])) for s in re.findall(r'strong:([HG]\d+)', m.group(1))]
                lm = [s for s in lm if not (s[0] == 'H' and int(s[1:]) > 8674)]   # H8xxx 词形码、H9xxx 前缀不算词条
                toks.append([lm, re.sub(r'<[^>]+>|\s+', '', m.group(2))])
            out[f'{bi}.{ci + 1}.{vi + 1}'] = toks
s = json.dumps(out, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode()
open(os.path.join(HERE, 'bdata', 'cuvs.json.gz'), 'wb').write(gzip.compress(s, 9, mtime=0))
print(len(out), 'verses', len(s), 'bytes')
