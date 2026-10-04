# 临时：打开补充问答页要引用的网页，找出关键句，存进“检查结果”供核对。查完删除。
import os, re, html, requests
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
JOBS = [
    ('irving_enc', 'https://www.encyclopedia.com/people/philosophy-and-religion/protestant-christianity-biographies/edward-irving', ['Annan', 'deposed', 'human nature', 'sinful']),
    ('irving_bt', 'https://www.biblicaltraining.org/library/edward-irving', ['Annan', 'deposed', 'human nature', 'sinful']),
    ('tgc', 'https://www.thegospelcoalition.org/article/you-asked-did-jesus-assume-a-fallen-human-nature/', ['Barth', 'Torrance', 'Irving', 'fallen']),
    ('jets', 'https://etsjets.org/wp-content/uploads/2021/10/files_JETS-PDFs_64_64-2_JETS_64.2_327-340_Van_Kuiken.pdf', ['Barth', 'Torrance', 'Irving']),
    ('sc_toc', 'https://ccel.org/ccel/white/steps.html', []),
    ('sc2', 'https://ccel.org/ccel/white/steps.v.html', ['selfishness took the place', 'power working from within', 'joy in holiness']),
]
def get(url):
    r = requests.get(url, headers=UA, timeout=60)
    if r.status_code != 200:
        return r.status_code, ''
    if r.content[:4] == b'%PDF':
        import io; from pypdf import PdfReader
        t = ' '.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(r.content)).pages)
    else:
        t = r.text
        links = re.findall(r'href="([^"]*steps[^"]*)"[^>]*>([^<]{3,80})<', t)
        t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', t)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t)) + '\nLINKS: ' + ' | '.join(f'{a} {b}' for a, b in links)[:4000]
    return 200, re.sub(r'\s+', ' ', t)
OUT = {}
for key, url, pats in JOBS:
    try:
        code, t = get(url)
    except Exception as e:
        code, t = str(e)[:80], ''
    print(key, code, len(t), flush=True)
    parts = [f'{key} {code} {url}']
    if t and not pats:
        parts.append(t[-4000:])
    for p in pats:
        ms = list(re.finditer(re.escape(p), t, re.I))
        parts.append(f'[{p}] {len(ms)}')
        for m in ms[:2]:
            parts.append('>> ' + t[max(0, m.start() - 500):m.end() + 500])
    OUT[key] = '\n'.join(parts)
toc = OUT.get('sc_toc', '')
for name, pat in (('sc5', 'Consecration'), ('sc7', 'Test of Discipleship')):
    m = re.search(r'(steps\.[a-z]+\.html) +' + pat, toc)
    if m:
        code, t = get('https://ccel.org/ccel/white/' + m.group(1))
        pats = ['warfare against self', 'takes possession of the heart']
        OUT[name] = m.group(1) + '\n' + '\n'.join('>> ' + t[max(0, x.start() - 400):x.end() + 600] for p in pats for x in list(re.finditer(re.escape(p), t, re.I))[:1])
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for key, t in OUT.items():
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                                            'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:60000]}})
    print('check', key, r.status_code)
