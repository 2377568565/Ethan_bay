# 临时：核对问题彩蛋31（为什么非要流血才能赦罪）要用的资料（网页关键句 + 怀著原版逐页文字）。查完删除。
import io, os, re, html, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
JOBS = [
    ('atone_w', W + 'Atonement_in_Christianity', ['ransom', 'Christus Victor', 'satisfaction', 'moral influence', 'penal substitution', 'governmental', 'Anselm', 'Abelard', 'Grotius', 'Aul']),
    ('satis_w', W + 'Satisfaction_theory_of_atonement', ['Cur Deus Homo', '1098', 'honor', 'Anselm', 'debt']),
    ('cv_w', W + 'Christus_Victor', ['Aul', '1931', 'ransom', 'Irenaeus', 'classic']),
    ('moral_w', W + 'Moral_influence_theory_of_atonement', ['Abelard', 'Romans', 'love', 'example']),
    ('penal_w', W + 'Penal_substitution', ['Calvin', 'Chalke', 'cosmic child abuse', '2003', 'Reformation', 'Hodge']),
    ('gov_w', W + 'Governmental_theory_of_atonement', ['Grotius', '1617', 'moral government', 'Arminian']),
    ('ransom_w', W + 'Ransom_theory_of_atonement', ['Origen', 'Gregory of Nyssa', 'fishhook', 'devil']),
    ('chalke_w', W + 'Steve_Chalke', ['cosmic child abuse', 'Lost Message', '2003', 'Evangelical Alliance']),
    ('korban_w', W + 'Korban', ['sin offering', 'Temple', 'flour', 'destruction', 'prayer', 'Hosea']),
    ('yk_w', W + 'Yom_Kippur', ['atonement', 'scapegoat', 'Temple', 'repentance']),
    ('ben_w', W + 'Yohanan_ben_Zakkai', ['Hosea', 'lovingkindness', 'acts of', 'atonement', 'Temple']),
    ('ccc613', 'https://www.scborromeo.org/ccc/para/613.htm', ['sacrifice', 'Passover', 'reconcil']),
    ('ccc614', 'https://www.scborromeo.org/ccc/para/614.htm', ['unique', 'completes', 'surpasses']),
    ('ccc615', 'https://www.scborromeo.org/ccc/para/615.htm', ['obedience', 'disobedience', 'satisf', 'Suffering Servant']),
    ('ccc616', 'https://www.scborromeo.org/ccc/para/616.htm', ['love', 'end', 'infinite']),
    ('calvin216', 'https://www.ccel.org/ccel/calvin/institutes.iv.xvii.html', ['substitut', 'curse', 'judge', 'wrath', 'love', 'Augustine']),
    ('anselm', 'https://sourcebooks.fordham.edu/basis/anselm-curdeus.asp', ['satisfaction', 'none but God', 'man ought', 'honor', 'merely by compassion', 'mercy alone']),
    ('sdafb9', 'https://www.adventist.org/beliefs/fundamental-beliefs/salvation/life-death-and-resurrection-of-christ/', ['atone', 'perfect', 'reconcil', 'substitut', 'Resurrection']),
    ('sdafb_w', W + '28_Fundamental_Beliefs', ['Life, Death', 'atonement', 'substitut']),
    ('ardn4', "https://www.sefaria.org/api/texts/Avot_D'Rabbi_Natan.4?context=0&commentary=0", ['Hosea', 'kindness', 'atonement', 'Joshua', 'desolate']),
    ('yoma8', 'https://www.sefaria.org/api/texts/Mishnah_Yoma.8?context=0&commentary=0', ['Day of Atonement', 'repentance', 'between man', 'fellow', 'death']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = [
    ('da', 'en_DA', list(range(15, 32)) + list(range(735, 780)), ['treated as we deserve', 'mercy destroyed justice', 'divorce mercy', 'Mercy and truth', 'fountain of life', 'executioner',
                                   'Satan had claimed', 'could not see through the portals', 'separation', 'reconcile', 'not to make the Father willing', 'propitiation', 'It is finished', 'universe']),
    ('sc', 'en_SC', range(5, 30), ['propitiation', 'not because of', 'great sacrifice', 'reconcile', 'Calvary']),
    ('pp', 'en_PP', range(55, 80), ['law of God is as sacred', 'sacrificial offering', 'perpetual reminder', 'could not be changed', 'repeal', 'painful ceremony', 'Abel', 'shed blood', 'Cain']),
]
RAW = [('da', 'en_DA', range(19, 29)), ('da', 'en_DA', range(745, 768)), ('sc', 'en_SC', range(9, 22)), ('pp', 'en_PP', range(60, 76))]


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
OFF = {'en_DA': 4, 'en_SC': 4, 'en_PP': 6}
with ThreadPoolExecutor(8) as ex:
    for key, b, ps in RAW:
        seo = [p + OFF[b] for p in ps]
        texts = list(ex.map(page, [(b, p) for p in seo]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(seo, texts))
        for i in range(0, max(1, len(full)), 60000):
            OUT[f'raw_{key}{ps[0]}_{i // 60000}'] = full[i:i + 60000]
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for key, t in OUT.items():
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                      'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:65000]}})
    print('check', key, len(t), r.status_code)
