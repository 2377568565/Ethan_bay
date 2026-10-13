# 临时：核对问题彩蛋30（犹大）要用的资料（网页关键句 + 怀著原版逐页文字）。查完删除。
import io, os, re, html, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
JOBS = [
    ('judas_w', W + 'Judas_Iscariot', ['Iscariot', 'Kerioth', 'sicarius', 'Akeldama', 'hanged', 'headlong', 'predestin', 'Origen', 'Dante', 'Barth', 'Gospel of Judas', 'treasurer', 'thirty']),
    ('gjudas_w', W + 'Gospel_of_Judas', ['Cainites', 'Irenaeus', '2006', 'National Geographic', 'carbon', 'DeConick', 'Coptic']),
    ('silver_w', W + 'Thirty_pieces_of_silver', ['Zechariah', 'Jeremiah', 'shekel', 'Exodus 21', 'slave']),
    ('akel_w', W + 'Akeldama', ['potter', 'Acts', 'Matthew']),
    ('judas_ce', 'https://www.newadvent.org/cathen/08539a.htm', ['Iscariot', 'Kerioth', 'avarice', 'despair', 'foreknowledge', 'repent']),
    ('sonperd_w', W + 'Son_of_perdition', ['Judas', '2 Thessalonians', 'apoleia']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = [
    ('da', 'en_DA', range(1, 760), ['Judas', 'betray']),
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


RANGES = [(290, 300), (383, 395), (557, 570), (642, 664), (685, 700), (705, 725)]
with ThreadPoolExecutor(8) as ex:
    for key, b, ps, pats in EGW:
        ps = list(ps)
        texts = list(ex.map(page, [(b, p) for p in ps]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(ps, texts))
        OUT[key + '_ok'] = f'{key} pages ok {sum(1 for t in texts if t)}/{len(ps)}'
        seg = []
        for a, z in RANGES:
            i = full.find(f'[{a}]'); j = full.find(f'[{z + 1}]', i + 1)
            seg.append(f'\n#### {a}-{z} ({i},{j})\n' + (full[max(0, i - 3000):j] if i >= 0 and j > i else ''))
        r = ''.join(seg)
        for i in range(0, max(1, len(r)), 60000):
            OUT[f'{key}_{i // 60000}'] = r[i:i + 60000]
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for key, t in OUT.items():
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                      'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:65000]}})
    print('check', key, len(t), r.status_code)
