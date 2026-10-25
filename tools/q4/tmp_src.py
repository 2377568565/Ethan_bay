# 临时（第三次）：核对问题彩蛋34（没听过耶稣的祖先会怎样）要用的资料。每读到一份就发一条 check run。查完删除。
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
    ('whit_html', 'https://en.wikisource.org/wiki/The_Complete_Poetical_Works_of_John_Greenleaf_Whittier/The_Eternal_Goodness', []),
    ('faber_anh', "https://en.wikisource.org/wiki/The_Army_and_Navy_Hymnal/Hymns/There%27s_a_Wideness_in_God%27s_Mercy", []),
    ('faber_uhb136', 'https://en.wikisource.org/wiki/The_University_Hymn_Book', ['Souls of men', 'wideness']),
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


RAW = []
with ThreadPoolExecutor(2) as ex:
    for key, b, ps in RAW:
        ps = list(ps)
        texts = list(ex.map(page, [(b, p) for p in ps]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(ps, texts))
        post(f'raw_{key}{ps[0]}', full)
