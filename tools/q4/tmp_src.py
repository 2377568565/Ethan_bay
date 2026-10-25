# 临时（第二次）：核对问题彩蛋34（没听过耶稣的祖先会怎样）要用的资料。每读到一份就发一条 check run。查完删除。
import os, re, html, json, time, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
API = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
HD = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}


def post(key, t):
    t = t or '(empty)'
    for i in range(0, len(t), 64000):
        k = key if i == 0 else f'{key}_{i // 64000}'
        r = requests.post(API, headers=HD, json={'name': f'chk:{k}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                          'conclusion': 'neutral', 'output': {'title': k, 'summary': k, 'text': t[i:i + 64000]}})
        print('check', k, len(t), r.status_code, flush=True)
        if i >= 64000 * 3:
            break


def get(url, raw=False):
    r = requests.get(url, headers=UA, timeout=40)
    if r.status_code != 200:
        return r.status_code, ''
    if raw:
        return 200, r.text
    t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', r.text)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    return 200, re.sub(r'\s+', ' ', t)


def ctx(full, pats, n=3, w=900):
    parts = []
    for pat in pats:
        ms = list(re.finditer(re.escape(pat), full, re.I))
        parts.append(f'[{pat}] {len(ms)}')
        last = -10**9
        k = 0
        for m in ms:
            if m.start() - last < w or k >= n:
                continue
            last = m.start(); k += 1
            parts.append('>> ' + full[max(0, m.start() - w):m.end() + w])
    return '\n'.join(parts)


# ---------- 二、网页资料 ----------
W = 'https://en.wikipedia.org/wiki/'
ZW = 'https://zh.wikipedia.org/wiki/'
WQ = 'https://en.wikiquote.org/wiki/'
WS = 'https://zh.wikisource.org/w/index.php?action=raw&title='
NA = 'https://www.newadvent.org/'
CC = 'https://www.scborromeo.org/ccc/para/{}.htm'
WA = 'https://web.archive.org/web/2024id_/'
JOBS = [
    ('whit_full', 'https://en.wikisource.org/w/index.php?action=raw&title=The_Complete_Poetical_Works_of_John_Greenleaf_Whittier/The_Eternal_Goodness', []),
    ('whit_rsb', 'https://en.wikisource.org/w/index.php?action=raw&title=The_Riverside_song_book/I_know_not_what_the_Future_hath', []),
    ('faber_s2', 'https://en.wikisource.org/w/api.php?action=query&list=search&srsearch=%22wideness+in+God%27s+mercy%22&format=json&srlimit=20', []),
    ('faber_uhb', 'https://en.wikisource.org/w/index.php?action=raw&title=The_University_Hymn_Book', []),
    ('faber_ia', 'https://archive.org/advancedsearch.php?q=title%3A%28hymns%29+AND+creator%3A%28Faber%2C+Frederick+William%29&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=year&rows=30&output=json', []),
    ('faber_ccel', 'https://www.ccel.org/ccel/faber/hymns.html', ['wideness', 'Souls of men']),
    ('faber_w2', W + 'Frederick_William_Faber', ['wideness', 'Souls of men', '1854', 'hymn']),
    ('lunyu_s', 'https://zh.wikisource.org/w/api.php?action=query&list=search&srsearch=%E6%9C%AA%E7%9F%A5%E7%94%9F%E7%84%89%E7%9F%A5%E6%AD%BB&format=json&srlimit=10', []),
    ('lunyu_ws', WS + '論語/先進第十一', []),
    ('tzsy_s2', 'https://zh.wikisource.org/w/api.php?action=query&list=search&srsearch=intitle%3A%E5%A4%A9%E4%B8%BB%E5%AF%A6%E7%BE%A9&format=json&srlimit=20', []),
    ('tzsy_s3', 'https://zh.wikisource.org/w/api.php?action=query&list=search&srsearch=%E5%90%BE%E5%A4%A9%E4%B8%BB%E4%B9%83%E5%8F%A4%E7%B6%93%E6%9B%B8%E6%89%80%E7%A8%B1%E4%B8%8A%E5%B8%9D&format=json&srlimit=10', []),
    ('tzsy_zw2', ZW + '天主实义', ['1603', '上帝', '古經', '古经']),
    ('tzsy_w', W + 'The_True_Meaning_of_the_Lord_of_Heaven', ['1603', 'Shangdi', 'classics', 'Lord of Heaven']),
    ('lewis_mc2', 'https://en.wikiquote.org/w/index.php?action=raw&title=C._S._Lewis', []),
]


def job(j):
    key, url, pats = j
    try:
        c, t = get(url, raw=('action=raw' in url or 'api.php' in url or 'advancedsearch' in url))
    except Exception as e:
        c, t = str(e)[:80], ''
    if c != 200:
        time.sleep(3)
        try:
            c, t = get(url, raw=('action=raw' in url or 'api.php' in url or 'advancedsearch' in url))
        except Exception as e:
            c, t = str(e)[:80], ''
    return key, f'{c} {url}\n' + (ctx(t, pats) if pats else t[:60000])


with ThreadPoolExecutor(3) as ex:
    for key, txt in ex.map(job, JOBS):
        post(key, txt)

# ---------- 怀爱伦著作逐页原版（PK 188—189：以利亚和七千人，“在中国……”） ----------
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'


def page(bp):
    b, p = bp
    for k in range(5):
        time.sleep(1.5 * (k + 1))
        try:
            c, t = get(M.format(b=b, p=p))
            if c == 200:
                return t.split('Nächste Seite »')[-1]
        except Exception:
            pass
    return ''


RAW = [('pk', 'en_PK', range(118, 142))]
with ThreadPoolExecutor(2) as ex:
    for key, b, ps in RAW:
        ps = list(ps)
        texts = list(ex.map(page, [(b, p) for p in ps]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(ps, texts))
        post(f'raw_{key}{ps[0]}', full)
