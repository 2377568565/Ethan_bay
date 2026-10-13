# 临时：核对问题彩蛋28—29（律法、祷告）要用的资料（网页关键句 + 怀著原版逐页文字）。查完删除。
import io, os, re, html, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
JOBS = [
    ('biblaw_w', W + 'Biblical_law_in_Christianity', ['ceremonial', 'judicial', 'moral', 'Aquinas', 'Calvin', 'Westminster', 'tripartite', 'Luther', 'Sabbath']),
    ('council_w', W + 'Council_of_Jerusalem', ['circumcision', '50', 'James', 'Peter', 'Galatians', 'Leviticus']),
    ('decree_w', W + 'Apostolic_Decree', ['Leviticus 17', 'blood', 'strangled', 'Noahide', 'idols']),
    ('m613_w', W + '613_commandments', ['Maimonides', '613', '248', '365']),
    ('nct_w', W + 'New_Covenant_theology', ['tripartite', 'moral law', 'Mosaic', 'Ten Commandments']),
    ('tencom_w', W + 'Ten_Commandments', ['tablets', 'Catholic', 'Lutheran', 'Sabbath', 'two tablets']),
    ('oldcov_w', W + 'Christian_views_on_the_Old_Covenant', ['ceremonial', 'moral', 'Acts 15', 'dietary', 'circumcision']),
    ('thorn_w', W + 'Thorn_in_the_flesh', ['eye', 'epilepsy', 'Tertullian', 'Chrysostom', 'persecution', 'interpretations']),
    ('lordp_w', W + "Lord%27s_Prayer", ['temptation', 'Francis', 'abandon', '2019', 'peirasmos']),
    ('petit_w', W + 'Petitionary_prayer', ['unanswered', 'omniscien', 'Aquinas', 'change']),
    ('ipstudy_w', W + 'Studies_on_intercessory_prayer', ['STEP', 'Benson', '2006', 'complications', 'certain']),
    ('aquinas99', 'https://www.newadvent.org/summa/2099.htm', ['ceremonial', 'judicial', 'moral precepts', 'three kinds']),
    ('aquinas83', 'https://www.newadvent.org/summa/3083.htm', ['change the Divine disposition', 'obtain by asking', 'Gregory']),
    ('wcf19', 'https://www.opc.org/wcf.html', ['ceremonial laws', 'judicial laws', 'moral law doth forever']),
    ('ccc2072', 'https://www.scborromeo.org/ccc/para/2072.htm', ['Decalogue', 'grave obligations']),
    ('ccc2735', 'https://www.scborromeo.org/ccc/para/2735.htm', ['not been heard', 'filial']),
    ('ccc2737', 'https://www.scborromeo.org/ccc/para/2737.htm', ['You ask and do not receive', 'heart']),
    ('calvin420', 'https://www.ccel.org/ccel/calvin/institutes.vi.xxi.html', ['ceremonial', 'judicial', 'moral']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = [
    ('pp', 'en_PP', range(1, 700), ['ceremonial law', 'moral law', 'law of ten commandments', 'typical', 'civil', 'law of Moses', 'ordinances']),
    ('aa', 'en_AA', range(1, 600), ['ceremonial', 'circumcision', 'Gentile converts', 'council', 'strangled']),
    ('sm1', 'en_1SM', range(200, 260), ['law in Galatians', 'schoolmaster', 'both the ceremonial', 'moral and ceremonial']),
    ('da', 'en_DA', range(240, 700), ['destroy the law', 'ceremonial', 'Gethsemane', 'not My will', 'cup pass']),
    ('sc', 'en_SC', range(60, 115), ['opening of the heart', 'key in the hand', 'presumption', 'answer', 'not that it is necessary']),
    ('mh', 'en_MH', range(120, 280), ['know not what', 'prayer for the sick', 'His will', 'submission']),
    ('mb', 'en_MB', range(1, 180), ['lead us not', 'temptation', 'Thy will be done']),
    ('col', 'en_COL', range(1, 350), ['importunity', 'Ask, and it shall', 'delay', 'answer']),
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


with ThreadPoolExecutor(8) as ex:
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
