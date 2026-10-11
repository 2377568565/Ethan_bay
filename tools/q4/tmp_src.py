# 临时：读取怀著原版页面（egwwritings 的逐页文字），只存含关键句的段落和页码标记。查完删除。
import os, re, html, requests
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
GROUPS = [('gc5', 'en_GC', range(455, 482), ['begin to think', 'one minute', 'natural immortality', 'personate', 'Spiritualism', 'familiar spirit', 'rich man', 'Lazarus', 'the dead know not', 'sleep']),
          ('da3', 'en_DA', list(range(446, 462)), ['unborrowed', 'sleep', 'Lazarus, come forth', 'dead']),
          ('da4', 'en_DA', list(range(660, 697)), ['small matter', 'silence and darkness', 'sleep', 'thief', 'Paradise', 'To-day', 'today']),
          ('col3', 'en_COL', range(126, 150), ['own ground', 'Abraham', 'Lazarus', 'state of the dead', 'the dead'])]


def text(u):
    r = requests.get(u, headers=UA, timeout=60)
    if r.status_code != 200:
        return ''
    t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', r.text)
    t = re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))
    t = t.split('Nächste Seite »')[-1]
    return t.replace('ﬁ', 'fi').replace('ﬂ', 'fl')


OUT = {}
for key, b, ps, pats in GROUPS:
    full = ''.join(f' {{seo{p}}} ' + text(M.format(b=b, p=p)) for p in ps)
    parts = [key + ' marks: ' + ' '.join(re.findall(r'\{seo\d+\} \S+ \S+|\[\d{3}\]', full))]
    for pat in pats:
        ms = list(re.finditer(re.escape(pat), full, re.I))
        parts.append(f'[{pat}] {len(ms)}')
        for m in ms[:4]:
            parts.append('>> ' + full[max(0, m.start() - 1500):m.end() + 1000])
    OUT[key] = '\n'.join(parts)
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for key, t in OUT.items():
    print(key, len(t))
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                      'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:65000]}})
    print('check', key, r.status_code)
