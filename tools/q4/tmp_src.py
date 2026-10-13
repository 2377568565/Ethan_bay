# 临时：核对问题彩蛋26（启示录的兽、印记、666）要用的资料（网页关键句 + 怀著原版逐页文字）。查完删除。
import io, os, re, html, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
JOBS = [
    ('number_w', W + 'Number_of_the_beast', ['Nero', '616', 'Irenaeus', 'gematria', 'Papyrus 115', 'Vicarius', 'Solomon', 'Lateinos', 'triangular']),
    ('vfd_w', W + 'Vicarius_Filii_Dei', ['Adventist', 'Uriah Smith', 'tiara', 'Donation', 'official', 'Ellen', 'Vicarius Christi', '666']),
    ('p115_w', W + 'Papyrus_115', ['616', 'Oxyrhynchus', 'dated']),
    ('mark_w', W + 'Mark_of_the_beast', ['microchip', 'barcode', 'Adventist', 'Sunday', 'vaccin', 'forehead', 'charagma', 'Jehovah']),
    ('hist_w', W + 'Historicism_(Christianity)', ['Wycliffe', 'Luther', 'Calvin', 'Knox', 'Newton', 'year-day', 'Antichrist', 'Westminster', 'Adventist']),
    ('futur_w', W + 'Futurism_(Christianity)', ['Ribera', 'Jesuit', 'Darby', 'Lacunza', 'Counter']),
    ('pret_w', W + 'Preterism', ['Alcazar', 'Nero', 'Jesuit', 'AD 70']),
    ('dayyear_w', W + 'Day-year_principle', ['Numbers 14', 'Ezekiel 4', '1260', 'Joachim', 'Newton', 'seventy weeks']),
    ('pius6_w', W + 'Pope_Pius_VI', ['1798', 'Berthier', 'Valence', 'prisoner', 'Siena', '1799']),
    ('rr1798_w', W + 'Roman_Republic_(1798%E2%80%931799)', ['Berthier', 'February 1798', 'Pius VI']),
    ('sdaesch_w', W + 'Seventh-day_Adventist_eschatology', ['mark of the beast', 'Sunday', 'United States', 'papacy', 'image', 'seal of God', '1798']),
    ('antichrist_w', W + 'Antichrist', ['1 John', 'Smalcald', 'Westminster', 'Pope', 'Luther', 'Calvin']),
    ('unam_w', W + 'Unam_sanctam', ['1302', 'Roman Pontiff', 'necessary for salvation']),
    ('smalc_w', W + 'Smalcald_Articles', ['Antichrist', '1537']),
    ('wcf_w', W + 'Westminster_Confession_of_Faith', ['Antichrist', 'Pope', '1788', '1903']),
    ('siege538_w', W + 'Siege_of_Rome_(537%E2%80%93538)', ['538', 'Belisarius', 'Ostrogoth', 'March']),
    ('vandal_w', W + 'Vandalic_War', ['534', 'Belisarius', 'Gelimer']),
    ('odoacer_w', W + 'Odoacer', ['493', 'Heruli', 'Theodoric']),
    ('justin_w', W + 'Pope_John_II', ['Justinian', 'head of all', '533']),
    ('irenaeus', 'https://www.newadvent.org/fathers/0103530.htm', ['six hundred', 'Lateinos', 'Teitan', 'Evanthas', 'hazardous', 'ancient copies', 'surmises']),
    ('ccc882', 'https://www.scborromeo.org/ccc/para/882.htm', ['Roman Pontiff', 'Vicar of Christ', 'full, supreme']),
    ('ccc1461', 'https://www.scborromeo.org/ccc/para/1461.htm', ['forgive', 'bishops']),
    ('ccc_idx', 'https://www.vatican.va/archive/ENG0015/__P2A.HTM', ['882', 'Vicar of Christ']),
    ('wcf_opc', 'https://www.opc.org/wcf.html', ['Antichrist', 'Pope of Rome', 'head thereof']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = [
    ('gc', 'en_GC', range(1, 640), ['mark of the beast', 'seal of God', 'yet received', 'image to the beast', 'lamblike', 'two horns', 'made captive',
                                    'forty and two months', 'Catholic communion', 'true Christians', 'brought home to his mind', 'test of loyalty',
                                    'apostate Protestantism', 'buy or sell', 'number of his name', 'deadly wound', 'papal supremacy', 'twelve hundred and sixty']),
    ('lde', 'en_LDE', range(1, 330), ['yet received the mark', 'mark of the beast', 'seal of God', 'ignorance', 'Catholic', 'six hundred']),
    ('ev', 'en_Ev', range(200, 600), ['yet received the mark', 'mark of the beast', 'Catholics', 'denunciatory']),
    ('bc7', 'en_7BC', range(1, 160), ['mark of the beast', 'six hundred', 'seal of', 'number of']),
    ('tm', 'en_TM', range(90, 130), ['Daniel and the Revelation', 'Revelation are one']),
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
