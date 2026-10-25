# 临时：核对问题彩蛋33（宗教这么多，为什么偏偏是耶稣）要用的资料（第二次）。每读到一份就发一条 check run。查完删除。
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
WS = 'https://zh.wikisource.org/w/index.php?action=raw&title='
CB = 'https://cbdata.dila.edu.tw/stable/juans?work={w}&juan={j}'
SC = 'https://suttacentral.net/api/bilarasuttas/{s}/sujato?lang=en'
JOBS = [
    ('ddj_api', 'https://api.ctext.org/gettext?urn=ctp:dao-de-jing', []),
    ('ddj_ws1', WS + '道德經_(王弼本)', ['道可道', '有物混成', '道生一', '天地不仁']),
    ('ddj_ws2', WS + '老子_(王弼本)', ['道可道', '有物混成', '道生一', '天地不仁']),
    ('ddj_ws3', WS + '道德經_(河上公章句)', ['道可道', '有物混成', '道生一', '天地不仁']),
    ('ddj_search', 'https://zh.wikisource.org/w/api.php?action=query&list=search&srsearch=%E9%81%93%E5%8F%AF%E9%81%93%20%E6%9C%89%E7%89%A9%E6%B7%B7%E6%88%90&format=json', []),
    ('ddj_zhw', ZW + '道德经', ['道可道', '有物混成', '道生一', '天地不仁', '郭店']),
    ('tanni_ja', 'https://ja.wikisource.org/w/index.php?action=raw&title=歎異抄', ['善人なほもて', '悪人をや']),
    ('tanni_jaw', 'https://ja.wikipedia.org/wiki/歎異抄', ['善人なほもて', '悪人をや', '悪人正機']),
    ('baima_zhw', ZW + '白马寺', ['永平', '东汉', '68']),
    ('hanbud_zhw', ZW + '汉传佛教', ['东汉', '传入']),
    ('hound_ws2', 'https://en.wikisource.org/wiki/The_Hound_of_Heaven', ['I fled Him', 'Halts by me', 'Rise, clasp My hand']),
    ('hound_pf', 'https://www.poetryfoundation.org/poems/45155/the-hound-of-heaven', ['I fled Him', 'Halts by me', 'Rise, clasp My hand']),
]


def job(j):
    key, url, pats = j
    try:
        c, t = get(url)
    except Exception as e:
        c, t = str(e)[:80], ''
    if c != 200:
        time.sleep(3)
        try:
            c, t = get(url)
        except Exception as e:
            c, t = str(e)[:80], ''
    return key, f'{c} {url}\n' + (ctx(t, pats) if pats else t[:60000])


with ThreadPoolExecutor(3) as ex:
    for key, txt in ex.map(job, JOBS):
        post(key, txt)

# ---------- 三、怀爱伦著作逐页原版 ----------
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


RAW = [('da', 'en_DA', range(545, 557)), ('pk', 'en_PK', range(243, 257))]
with ThreadPoolExecutor(2) as ex:
    for key, b, ps in RAW:
        ps = list(ps)
        texts = list(ex.map(page, [(b, p) for p in ps]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(ps, texts))
        post(f'raw_{key}{ps[0]}', full)
