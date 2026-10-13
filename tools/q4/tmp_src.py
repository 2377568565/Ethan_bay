# 临时：核对问题彩蛋27（圣所、1844 与查案审判）要用的资料（网页关键句 + 怀著原版逐页文字）。查完删除。
import io, os, re, html, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
JOBS = [
    ('ij_w', W + 'Investigative_judgment', ['1857', 'Everts', 'James White', 'Barnhouse', 'face-saving', 'Ford', 'Glacier View', 'Hebrews', 'Daniel 7', 'assurance', 'Fundamental']),
    ('gd_w', W + 'Great_Disappointment', ['October 22', 'Edson', 'Snow', 'Crosier', 'cornfield', 'wept', 'Karaite']),
    ('edson_w', W + 'Hiram_Edson', ['cornfield', 'October 23', 'Crosier', 'sanctuary']),
    ('miller_w', W + 'William_Miller_(preacher)', ['2300', '1843', '1844', 'Daniel 8:14', 'Baptist']),
    ('millerism_w', W + 'Millerism', ['seventh-month', 'Samuel S. Snow', '50,000', 'October 22', '1843']),
    ('ford_w', W + 'Desmond_Ford', ['Glacier View', '1980', 'investigative judgment', 'Hebrews', 'apotelesmatic']),
    ('qod_w', W + 'Questions_on_Doctrine', ['Barnhouse', 'Martin', 'investigative', 'Eternity']),
    ('seventy_w', W + 'Prophecy_of_Seventy_Weeks', ['457', 'Artaxerxes', 'Ezra 7', 'Messiah', 'historicist', 'cut off', 'Antiochus']),
    ('d2300_w', W + '2300_day_prophecy', ['457', '1844', 'Antiochus', 'evenings', 'Seventh-day']),
    ('yk_w', W + 'Yom_Kippur', ['judgment', 'sealed', 'Book of Life', 'Rosh Hashanah', 'tenth day']),
    ('unet_w', W + 'Unetanneh_Tokef', ['inscribed', 'sealed', 'Yom Kippur', 'who shall live']),
    ('art1_w', W + 'Artaxerxes_I', ['465', '464', 'Ezra', 'Nehemiah', 'seventh year']),
    ('antio_w', W + 'Antiochus_IV_Epiphanes', ['Daniel', '167', 'Temple', 'abomination']),
    ('partj_w', W + 'Particular_judgment', ['death', 'Catholic', 'general judgment', 'Lutheran']),
    ('bol_w', W + 'Book_of_Life', ['Exodus 32', 'Revelation', 'Daniel 12', 'Malachi']),
    ('day_atone_w', W + 'Day_of_Atonement', ['Leviticus 16', 'scapegoat', 'Azazel', 'Hebrews']),
    ('ccc1022', 'https://www.scborromeo.org/ccc/para/1022.htm', ['particular judgment', 'death']),
    ('ccc1038', 'https://www.scborromeo.org/ccc/para/1038.htm', ['Last Judgment', 'resurrection']),
    ('fb24', 'https://www.adventist.org/christs-ministry-in-the-heavenly-sanctuary/', ['1844', 'investigative judgment', 'sanctuary', 'Daniel', 'Hebrews']),
    ('fb24b', 'https://www.adventist.org/beliefs/', ['Christ\'s Ministry in the Heavenly Sanctuary', '1844']),
    ('mishnah_rh', 'https://www.sefaria.org/api/texts/Mishnah_Rosh_Hashanah.1.2?context=0', ['pass before', 'judged', 'Tabernacles']),
    ('talmud_rh', 'https://www.sefaria.org/api/texts/Rosh_Hashanah.16b?context=0', ['three books', 'sealed', 'intermediate', 'Yom Kippur']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = [
    ('gc', 'en_GC', range(330, 520), ['central pillar', 'key which unlocked', 'descriptions of the same event', 'investigative judgment', 'come in review',
                                    'wounded hands', 'blotting out of sins', 'before the second advent', 'graven them', 'great day of atonement',
                                    'Advocate', 'heavenly sanctuary', 'pattern', 'scapegoat', 'Daniel 8:14', 'assurance']),
    ('ew', 'en_EW', range(1, 320), ['Most Holy', 'holy of holies', 'Father arise', 'Crosier']),
    ('ev', 'en_Ev', range(190, 260), ['foundation of our faith', 'sanctuary', '1844']),
    ('sc', 'en_SC', range(40, 90), ['accounted righteous', 'had not sinned']),
    ('col', 'en_COL', range(290, 340), ['wedding garment', 'investigative']),
    ('wlf', 'en_WLF', range(1, 30), ['Crosier', 'true light']),
    ('lde', 'en_LDE', range(1, 330), ['investigative judgment', 'sanctuary', 'assurance', 'judgment']),
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
