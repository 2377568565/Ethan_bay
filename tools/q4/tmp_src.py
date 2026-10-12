# 临时：核对《罗马书7章与得救》专题要用的资料（网页关键句 + 怀著原版逐页文字）。查完删除。
import io, os, re, html, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
JOBS = [
    ('ussher', W + 'Ussher_chronology', ['4004', 'Ussher', '1650']),
    ('annomundi', W + 'Anno_Mundi', ['3761', '5509', 'Septuagint', 'Hebrew calendar']),
    ('dating', W + 'Dating_creation', ['4004', '3761', '5500', 'Septuagint', 'Bede']),
    ('temple', W + "Solomon's_Temple", ['966', '967', '957', '1 Kings 6:1', '480']),
    ('heb_year', W + 'Hebrew_calendar', ['5786', '5787', '3761', 'Rosh Hashanah']),
    ('wycliffe', 'https://www.wycliffe.net/resources/statistics/', ['full Bible', 'New Testament', 'languages', 'no Scripture', '2025', '2024']),
    ('wycliffe_w', W + 'Wycliffe_Global_Alliance', ['languages', 'Bible']),
    ('gutenberg_w', W + 'Printing_press', ['Luther', 'Reformation', 'Bible']),
    ('chatgpt_w', W + 'ChatGPT', ['100 million', 'fastest-growing', 'two months', 'users']),
    ('millerite_w', W + 'Great_Disappointment', ['October 22, 1844', 'Miller', 'Snow']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = [
    ('gc_a', 'en_GC', list(range(285, 300)) + list(range(380, 400)), ['knowledge shall be increased', 'delayed', 'not the will of God', 'forty years', 'modern Israel']),
    ('gc_b', 'en_GC', range(430, 615), ['six thousand years', '6000 years', 'nearly six thousand']),
    ('da', 'en_DA', range(530, 560), ['hasten', 'Had the purpose of God', 'before this, have come']),
    ('col', 'en_COL', range(1, 30), ['perfectly reproduced', 'claim them as His own', 'hasten', 'waiting with longing desire']),
    ('sm1', 'en_1SM', range(150, 235), ['based on time', 'definite time', 'time-setting', 'set a time', 'not to know']),
    ('t2', 'en_2T', range(170, 230), ['deferred in mercy', 'long night of gloom', 'morning is deferred']),
    ('ev', 'en_Ev', range(640, 720), ['delayed', 'deferred', 'long night of gloom', 'not the will of God']),
]


def get(url):
    r = requests.get(url, headers=UA, timeout=90)
    if r.status_code != 200:
        return r.status_code, ''
    t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', r.text)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    return 200, re.sub(r'\s+', ' ', t)


def ctx(key, full, pats, n=3, w=1100):
    parts = [key]
    for pat in pats:
        ms = list(re.finditer(re.escape(pat), full, re.I))
        parts.append(f'[{pat}] {len(ms)}')
        for m in ms[:n]:
            before = full[max(0, m.start() - 6000):m.start()]
            mk = re.findall(r'\[\d{1,3}\]|\{seo\d+\}', before)
            parts.append(f'>> (marks before: {" ".join(mk[-3:])}) ' + full[max(0, m.start() - w):m.end() + w])
    return '\n'.join(parts)


OUT = {}
for key, url, pats in JOBS:
    try:
        c, t = get(url)
    except Exception as e:
        c, t = str(e)[:80], ''
    OUT[key] = f'{c} {url}\n' + ctx(key, t, pats)


def page(bp):
    b, p = bp
    for _ in range(3):
        try:
            c, t = get(M.format(b=b, p=p))
            if c == 200:
                return t.split('Nächste Seite »')[-1]
        except Exception:
            pass
    return ''


with ThreadPoolExecutor(4) as ex:
    for key, b, ps, pats in EGW:
        ps = list(ps)
        texts = list(ex.map(page, [(b, p) for p in ps]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(ps, texts))
        r = ctx(key, full, pats, n=4)
        for i in range(0, max(1, len(r)), 60000):
            OUT[f'{key}_{i // 60000}'] = f'{key} pages ok {sum(1 for t in texts if t)}/{len(ps)}\n' + r[i:i + 60000]
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for key, t in OUT.items():
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                      'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:65000]}})
    print('check', key, len(t), r.status_code)
