# 临时：下载怀爱伦著作原文（1929 年以前出版，公版），找出要引用的句子前后文，存进“检查结果”供核对。查完删除。
import io, os, re, html, requests
from pypdf import PdfReader
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
AD = 'https://documents.adventistarchives.org/Periodicals/'
C = 'https://ccel.org/ccel/white/'
PATS = ['nothing that responded', 'Not even by a thought', 'possibility of yielding', 'liabilities', 'hereditary and cultivated',
        'no sin in Him that Satan', 'condition in which those must be found', 'let this cup', 'shrunk', 'feared that in His human nature',
        'awful moment', 'bloody sweat', 'strengthen Him to drink', 'humanity of the Son of God', 'not cherished', 'repulsed as hateful',
        'I am sinless', 'vile body', 'refined sensibilities', 'hath nothing in Me', 'separation', 'Not My will', 'so it may be with us',
        'the cup', 'trembl', 'sinless', 'propensit', 'He was tempted', 'Father, save me', 'for this cause came I']
JOBS = [('da12', C + 'desire.xv.html'), ('da73', C + 'desire.lxxvi.html'), ('da74', C + 'desire.lxxvii.html'), ('da_toc', C + 'desire.html'),
        ('gc_toc', C + 'controversy.html')]
for n in range(10, 16):
    JOBS.append((f'rh1888_{n}', AD + f'RH/RH18880327-V65-{n}.pdf'))
    JOBS.append((f'st1888_{n}', AD + f'ST/ST18880323-V14-{n}.pdf'))
JOBS.append(('rh1887', AD + 'RH/RH18871108-V64-44.pdf'))
JOBS.append(('rh1887b', AD + 'RH/RH18871108-V64-45.pdf'))

def get(url):
    r = requests.get(url, headers=UA, timeout=90)
    if r.status_code != 200:
        return r.status_code, ''
    if r.content[:4] == b'%PDF':
        t = '\n'.join(p.extract_text() or '' for p in PdfReader(io.BytesIO(r.content)).pages)
    else:
        t = r.text
        links = re.findall(r'href="([^"]+)"[^>]*>([^<]{3,80})<', t)
        t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', t)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t)) + '\nLINKS: ' + ' | '.join(f'{a} {b}' for a, b in links if 'white/' in a)[:6000]
    return 200, re.sub(r'\s+', ' ', t)

OUT = {}
for key, url in JOBS:
    try:
        code, t = get(url)
    except Exception as e:
        code, t = str(e)[:100], ''
    print(key, code, len(t), flush=True)
    if not t:
        continue
    if key.endswith('_toc'):
        OUT[key] = t[-6000:]
        continue
    parts = []
    for p in PATS:
        for m in list(re.finditer(re.escape(p), t, re.I))[:4]:
            parts.append(f'[{p}] ' + t[max(0, m.start() - 900):m.end() + 900])
    if parts:
        OUT[key] = url + '\n' + '\n\n'.join(parts)

# 《善恶之争》“大艰难的时期”一章：从目录里找到网址再下载
toc = OUT.get('gc_toc', '')
m = re.search(r'(controversy\.[a-z]+\.html) +The Time of Trouble', toc)
if m:
    code, t = get(C + m.group(1))
    print('gc39', m.group(1), code, len(t))
    parts = [f'[{p}] ' + t[max(0, x.start() - 900):x.end() + 900] for p in PATS for x in list(re.finditer(re.escape(p), t, re.I))[:3]]
    OUT['gc39'] = C + m.group(1) + '\n' + '\n\n'.join(parts)

api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for key, t in OUT.items():
    chunks = [t[i:i + 60000] for i in range(0, len(t), 60000)][:4]
    for i, c in enumerate(chunks):
        name = f'egw:{key}:{i + 1}/{len(chunks)}'
        r = requests.post(api, headers=hd, json={'name': name, 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                                                'conclusion': 'neutral', 'output': {'title': name, 'summary': key, 'text': c}})
        print('check', name, r.status_code, flush=True)
