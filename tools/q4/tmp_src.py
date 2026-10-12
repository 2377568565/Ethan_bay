# 临时：核对《安息日怎样守》要用的资料（网页全文 + 怀著原版逐页文字）。查完删除。
import io, os, re, html, requests
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
Z = 'https://zh.wikipedia.org/wiki/'
FULL = [('bri', 'https://adventistbiblicalresearch.org/articles/sabbath-observance-guidelines'),
        ('bri2', 'https://www.eldersdigest.org/en/2009/2/sabbath-observance-guidelines-part-1')]
JOBS = [
    ('fb20', 'https://www.adventist.org/the-sabbath/', ['sunset', 'delight', 'Creator']),
    ('gaokao', Z + '%E6%99%AE%E9%80%9A%E9%AB%98%E7%AD%89%E5%AD%A6%E6%A0%A1%E6%8B%9B%E7%94%9F%E5%85%A8%E5%9B%BD%E7%BB%9F%E4%B8%80%E8%80%83%E8%AF%95', ['6月7日', '2003']),
    ('cet', Z + '%E5%A4%A7%E5%AD%A6%E8%8B%B1%E8%AF%AD%E5%9B%9B%E5%85%AD%E7%BA%A7%E8%80%83%E8%AF%95', ['星期六', '周六', '6月', '12月']),
    ('ielts', W + 'International_English_Language_Testing_System', ['Saturday', 'computer', 'times a month', 'dates']),
    ('toefl', W + 'TOEFL', ['Home Edition', 'times a year', 'dates', 'Saturday']),
    ('korea', 'https://adventist.news/news/adventists-in-korea-await-groundbreaking-legal-ruling-on-sabbath-accommodation', ['Sabbath', 'exam']),
    ('kenya', 'https://www.standardmedia.co.ke/amp/article/2000084618/sda-students-now-get-their-sabbath-back', ['Sabbath', 'court']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = [('t6a', 'en_6T', range(298, 312), ['preparation', 'edges', 'sunset', 'Friday', 'cooking']),
       ('t6b', 'en_6T', range(312, 326), ['fields and groves', 'tedious', 'long', 'children', 'nature', 'Sabbath school']),
       ('da207', 'en_DA', range(150, 178), ['useless inactivity', 'holy deeds', 'healing the sick'])]


def get(url):
    r = requests.get(url, headers=UA, timeout=90)
    if r.status_code != 200:
        return r.status_code, ''
    if r.content[:4] == b'%PDF':
        from pypdf import PdfReader
        t = ' '.join(f'[[p{i + 1}]] ' + (p.extract_text() or '') for i, p in enumerate(PdfReader(io.BytesIO(r.content)).pages))
    else:
        t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', r.text)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    return 200, re.sub(r'\s+', ' ', t).replace('ﬁ', 'fi').replace('ﬂ', 'fl')


def ctx(key, full, pats, n=4, w=900):
    parts = [key]
    for pat in pats:
        ms = list(re.finditer(re.escape(pat), full, re.I))
        parts.append(f'[{pat}] {len(ms)}')
        for m in ms[:n]:
            parts.append('>> ' + full[max(0, m.start() - w):m.end() + w])
    return '\n'.join(parts)


OUT = {}
for key, url in FULL:
    try:
        c, t = get(url)
    except Exception as e:
        c, t = str(e)[:80], ''
    for i in range(0, max(1, len(t)), 60000):
        OUT[f'{key}_{i // 60000}'] = f'{c} {url}\n' + t[i:i + 60000]
for key, url, pats in JOBS:
    try:
        c, t = get(url)
    except Exception as e:
        c, t = str(e)[:80], ''
    OUT[key] = f'{c} {url}\n' + ctx(key, t, pats)
for key, b, ps, pats in EGW:
    full = ''
    for p in ps:
        try:
            c, t = get(M.format(b=b, p=p))
        except Exception:
            t = ''
        full += f' {{seo{p}}} ' + t.split('Nächste Seite »')[-1]
    for i in range(0, max(1, len(full)), 60000):
        OUT[f'{key}_{i // 60000}'] = key + ' marks: ' + ' '.join(re.findall(r'\[\d{2,3}\]', full[i:i + 60000])) + '\n' + full[i:i + 60000]
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for key, t in OUT.items():
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                      'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:65000]}})
    print('check', key, len(t), r.status_code)
