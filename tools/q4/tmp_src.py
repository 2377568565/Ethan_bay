# 临时：核对问题彩蛋32（天堂）要用的资料（第二次）（网页关键句 + 怀著原版逐页文字）。查完删除。
import io, os, re, html, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
W = 'https://en.wikipedia.org/wiki/'
JOBS = [
    ('twain1', 'https://www.sacred-texts.com/aor/twain/letearth.htm', ['harp', 'sings', 'everybody']),
    ('twain2', 'http://www.online-literature.com/twain/letters-from-the-earth/2/', ['harp', 'sings', 'everybody']),
    ('twain3', 'https://en.wikiquote.org/wiki/Letters_from_the_Earth', ['harp', 'sing']),
    ('lewis_wq', 'https://en.wikiquote.org/wiki/Mere_Christianity', ['another world', 'Aim at Heaven', 'thrown in']),
    ('lewis_wq2', 'https://en.wikiquote.org/wiki/C._S._Lewis', ['another world', 'Aim at Heaven', 'thrown in']),
    ('wright_wq', 'https://en.wikiquote.org/wiki/N._T._Wright', ['end of the world', 'Heaven is important']),
    ('wright_w2', W + 'N._T._Wright', ['Surprised by Hope', 'end of the world']),
    ('plato_g', 'https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0178%3Atext%3DGorg.%3Apage%3D493', ['tomb']),
    ('plato_c', 'https://www.perseus.tufts.edu/hopper/text?doc=Perseus%3Atext%3A1999.01.0172%3Atext%3DCrat.%3Apage%3D400', ['tomb']),
    ('orph_w', W + 'Orphism_(religion)', ['tomb', 'soma']),
    ('mortal_w', W + 'Christian_mortalism', ['Tyndale', 'Adventist', 'soul sleep', 'Luther']),
    ('wcf32', 'https://www.opc.org/wcf.html', ['highest heavens', 'XXXII', 'Of the State of Men after Death']),
    ('sdafb27', 'https://web.archive.org/web/2024id_/https://www.adventist.org/the-millennium-and-the-end-of-sin/', ['thousand', 'heaven', 'earth']),
    ('sdafb28', 'https://web.archive.org/web/2024id_/https://www.adventist.org/the-new-earth/', ['new earth', 'home', 'eternal']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = []
RAW = [('gcc', 'en_GC', range(538, 577))]


def get(url):
    r = requests.get(url, headers=UA, timeout=40)
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
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}


def post(key, t):
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                      'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:65000]}})
    print('check', key, len(t), r.status_code, flush=True)


for key, url, pats in JOBS:
    try:
        c, t = get(url)
    except Exception as e:
        c, t = str(e)[:80], ''
    post(key, f'{c} {url}\n' + (ctx(key, t, pats) if pats else t[:60000]))


def page(bp):
    b, p = bp
    import time
    for k in range(5):
        time.sleep(1.5 * (k + 1))
        try:
            c, t = get(M.format(b=b, p=p))
            if c == 200:
                return t.split('Nächste Seite »')[-1]
        except Exception:
            pass
    return ''


with ThreadPoolExecutor(2) as ex:
    for key, b, ps, pats in EGW:
        ps = list(ps)
        texts = list(ex.map(page, [(b, p) for p in ps]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(ps, texts))
        r = ctx(key, full, pats, n=4)
        for i in range(0, max(1, len(r)), 60000):
            OUT[f'{key}_{i // 60000}'] = f'{key} pages ok {sum(1 for t in texts if t)}/{len(ps)}\n' + r[i:i + 60000]
OFF = {'en_GC': 0, 'en_Ed': 0, 'en_PP': 0, 'en_1SM': 0}   # 这次直接用 seo 页号
with ThreadPoolExecutor(2) as ex:
    for key, b, ps in RAW:
        seo = [p + OFF[b] for p in ps]
        texts = list(ex.map(page, [(b, p) for p in seo]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(seo, texts))
        for i in range(0, max(1, len(full)), 60000):
            post(f'raw_{key}{ps[0]}_{i // 60000}', full[i:i + 60000])
