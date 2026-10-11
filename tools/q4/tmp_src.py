# 临时：读取怀著原版页面（egwwritings 的逐页文字），按书合并成“检查结果”。查完删除。
import os, re, html, requests
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
GROUPS = [('gc_a', 'en_GC', range(544, 554)), ('gc_b', 'en_GC', range(554, 564)),
          ('da', 'en_DA', list(range(527, 533)) + list(range(783, 791))),
          ('col', 'en_COL', range(259, 268))]
EXTRA = [('sda26', 'https://www.adventist.org/death-and-resurrection/')]


def text(u):
    r = requests.get(u, headers=UA, timeout=60)
    if r.status_code != 200:
        return f'[{r.status_code}]'
    t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', r.text)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t)))


OUT = {}
for key, b, ps in GROUPS:
    OUT[key] = '\n'.join(f'##### {b} seo page{p}\n' + text(M.format(b=b, p=p))[:6500] for p in ps)
for key, u in EXTRA:
    t = text(u); i = t.find('Death and Resurrection')
    OUT[key] = u + '\n' + t[max(0, i - 200):i + 6000]
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for key, t in OUT.items():
    print(key, len(t))
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                      'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:65000]}})
    print('check', key, r.status_code)
