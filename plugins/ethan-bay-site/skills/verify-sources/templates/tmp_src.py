# 临时：打开要核对的网页或 PDF，找出关键句前后文，每份资料发成一条“检查结果”（check run，最多 6 万字）。查完删除。
# 用法：把本文件复制到 tools/q4/tmp_src.py，tmp-src.yml 复制到 .github/workflows/，改好 JOBS 后提交推送。
import io, os, re, html, requests
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
# (键, 网址, 关键词列表)。关键词为空时存全文开头 6 万字；PDF 会逐页标出 [[p页码]]。
JOBS = [
    ('example', 'https://ccel.org/ccel/white/desire.html', ['Desire of Ages']),
]


def get(url):
    r = requests.get(url, headers=UA, timeout=60)
    if r.status_code != 200:
        return r.status_code, ''
    if r.content[:4] == b'%PDF':
        from pypdf import PdfReader
        t = ' '.join(f'[[p{i + 1}]] ' + (p.extract_text() or '') for i, p in enumerate(PdfReader(io.BytesIO(r.content)).pages))
    else:
        t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', r.text)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
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
        parts.append(t[:59000])
    for p in pats:
        ms = list(re.finditer(re.escape(p), t, re.I))
        parts.append(f'[{p}] {len(ms)} 处')
        for m in ms[:3]:
            parts.append('>> ' + t[max(0, m.start() - 700):m.end() + 700])
    OUT[key] = '\n'.join(parts)

api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for key, t in OUT.items():
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                                            'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:60000]}})
    print('check', key, r.status_code)
