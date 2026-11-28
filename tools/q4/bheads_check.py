#!/usr/bin/env python3
"""核对小标题（tools/q4/bheads/*.txt）：每行的“章.节”要和 BSB 原表一致；标题里出现、但整本和合本里从来没有的两个字连在一起，列出来人工看（多半是人名地名写错）。"""
import os, re, sys, json, gzip, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bible
bible._load()
ALL = ''.join(v for bk in bible._cuv for ch in bk['chapters'] for v in ch).replace('神', '上帝')
# 旧版和合本（ChiUns）里的人名地名写法和网站用的这一版有些不同（推罗→泰尔、大马色→大马士革、古列→塞鲁士）：
# 标题里出现、旧版有而这一版没有的字串，都要改成这一版的写法
OLD = ''.join(w for toks in json.loads(gzip.open(os.path.join(HERE, 'bdata', 'cuvs.json.gz')).read()).values() for _, w in toks)
def oldnames(zh):
    out = set()
    for seg in re.findall(r'[一-鿿]+', zh):
        for n in range(2, 6):
            for i in range(len(seg) - n + 1):
                w = seg[i:i + n]
                if w in OLD and w not in ALL and w.replace('神', '上帝') not in ALL:
                    out.add(w)
    return [w for w in out if not any(w != x and w in x for x in out)]
OK = set(sys.argv[2:])
FUNC = set('的和与在为被从到向对把给将了着过中之一二三四五六七八九十百千第次个论再又也都') if len(sys.argv) > 2 else set()
sys.path.insert(0, os.environ.get('JIEBA_SRC', ''))
import jieba, logging
jieba.setLogLevel(logging.ERROR)
W = json.load(open(sorted(glob.glob(os.path.join(HERE, '..', '..', 'site', 'bible', 'words-*.json')))[-1], encoding='utf-8'))
for w in W:
    if len(w[0]) >= 2:
        jieba.add_word(w[0], freq=max(w[3], 5) * 50)
bad = 0
for f in sorted(glob.glob(os.path.join(HERE, 'bheads', '*.txt'))):
    if len(sys.argv) > 1 and sys.argv[1] not in os.path.basename(f):
        continue
    for ln in open(f, encoding='utf-8'):
        k, _, zh = ln.rstrip('\n').partition(' ')
        miss = []
        toks = list(jieba.cut(zh))
        for w in toks:
            if len(w) >= 2 and re.match(r'^[一-鿿]+$', w) and w not in ALL and w not in OK:
                miss.append(w)
        run = ''   # 连着几个单字：多半是分词认不出的人名地名（如“推罗”），整串要在经文里出现过
        for w in toks + ['。']:
            if len(w) == 1 and re.match(r'[一-鿿]', w) and w not in '的和与在为被从到向对把给将了着过中之一二三四五六七八九十第次个论':
                run += w
                continue
            if len(run) >= 2 and run not in ALL and run not in OK:
                miss.append('串:' + run)
            run = ''
        miss += ['旧:' + w for w in oldnames(zh)]
        for seg in re.findall(r'[一-鿿]+', zh):   # 每个字都要落在经文里出现过的两字以上字串中（虚字除外）
            cov = [False] * len(seg)
            for n in range(2, 7):
                for i in range(len(seg) - n + 1):
                    if seg[i:i + n] in ALL:
                        for j in range(i, i + n): cov[j] = True
            un = ''.join(ch if not c and ch not in FUNC else ' ' for ch, c in zip(seg, cov)).split()
            miss += ['孤:' + u for u in un if u not in OK]
        if miss:
            bad += 1
            print(os.path.basename(f)[:6], k, zh, '  ?', ' '.join(miss))
print('flagged', bad)
