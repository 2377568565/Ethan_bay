# 临时：核对问题彩蛋16—25要用的资料（网页关键句 + 怀著原版逐页文字）。查完删除。
import io, os, re, html, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
JOBS = [
    ('poe_w', W + 'Problem_of_evil', ['Epicurus', 'Lactantius', 'free will', 'Plantinga', 'logical problem']),
    ('lisbon_w', W + '1755_Lisbon_earthquake', ['Voltaire', 'All Saints', 'deaths', 'theodicy']),
    ('pain_w', W + 'The_Problem_of_Pain', ['megaphone', '1940']),
    ('frankl_w', W + "Man's_Search_for_Meaning", ['Nietzsche', 'why to live', 'logotherapy', 'million']),
    ('wsc_w', W + 'Westminster_Shorter_Catechism', ['chief end', '1647']),
    ('conf_w', W + 'Confessions_(Augustine)', ['restless', '397']),
    ('dss_w', W + 'Dead_Sea_Scrolls', ['Isaiah', '1947', 'radiocarbon', 'Masoretic']),
    ('greatisa_w', W + 'Great_Isaiah_Scroll', ['1QIsa', 'Masoretic', 'BCE', 'identical']),
    ('teldan_w', W + 'Tel_Dan_stele', ['House of David', '1993', 'BCE']),
    ('siloam_w', W + 'Siloam_inscription', ['Hezekiah', '1880', 'tunnel']),
    ('p52_w', W + 'Rylands_Library_Papyrus_P52', ['John', 'oldest', 'date']),
    ('pilate_w', W + 'Pilate_stone', ['1961', 'Caesarea', 'Tiberieum']),
    ('ntmss_w', W + 'Biblical_manuscript', ['5,800', 'Greek', 'manuscripts of the New Testament', 'Homer']),
    ('textcrit_w', W + 'Textual_criticism_of_the_New_Testament', ['variants', 'meaning', 'manuscripts']),
    ('merne_w', W + 'Merneptah_Stele', ['Israel', '1208']),
    ('creationism_w', W + 'Creationism', ['Young Earth', 'Old Earth', 'theistic evolution', 'Gap']),
    ('finetune_w', W + 'Fine-tuned_universe', ['cosmological constant', 'Hoyle', 'carbon']),
    ('sdafb_w', W + '28_Fundamental_Beliefs', ['Creation', 'six', '2015']),
    ('tithe_w', W + 'Tithe', ['Malachi', 'Abraham', 'Adventist']),
    ('ahs_w', W + 'Adventist_Health_Studies', ['Loma Linda', 'years', 'vegetarian', 'AHS-2']),
    ('blue_w', W + 'Blue_Zone', ['Loma Linda', 'Adventist', 'Okinawa']),
    ('barnum_w', W + 'Barnum_effect', ['Forer', '1948', 'horoscope', 'astrology']),
    ('astro_w', W + 'Astrology_and_science', ['Carlson', 'Nature', 'double-blind', 'Gauquelin']),
    ('fengshui_w', W + 'Feng_shui', ['pseudoscience', 'compass', 'qi']),
    ('rites_w', W + 'Chinese_Rites_controversy', ['Ricci', '1742', '1939', 'Confucius']),
    ('ancestor_w', W + 'Veneration_of_the_dead', ['China', 'Qingming', 'Protestant', 'Catholic']),
    ('qingming_w', W + 'Qingming_Festival', ['tomb', 'Tomb-Sweeping', 'Jie Zitui']),
    ('parstyle_w', W + 'Parenting_styles', ['Baumrind', 'authoritative', 'authoritarian', 'permissive']),
    ('interfaith_w', W + 'Interfaith_marriage_in_Christianity', ['unequally yoked', '2 Corinthians', 'Catholic']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = [
    ('gc', 'en_GC', range(1, 640), ['impossible to explain the origin of sin', 'intruder', 'blotted out of existence', 'The great controversy is ended',
                                    'service of love', 'spirits of the dead', 'astrolog', 'fortune', 'united with the human', 'infallible revelation', 'Divine and human']),
    ('pp', 'en_PP', range(1, 700), ['service of love', 'freedom of choice', 'Why Was Sin Permitted', 'Endor', 'Samuel was not present', 'literal days',
                                    'the week originated', 'indefinite periods', 'astrolog', 'unequally yoked', 'unbeliever']),
    ('da', 'en_DA', range(1, 760), ['end from the beginning', 'lives unto itself', 'Our Father, who art in heaven', 'cup of suffering']),
    ('sm1', 'en_1SM', range(1, 420), ['not the words of the Bible that are inspired', 'God committed the preparation', 'Bible is not given to us in grand superhuman',
                                      'mistake', 'utmost fidelity', 'infallibility']),
    ('ed', 'en_Ed', range(1, 300), ['harmonious development', "God's ideal for His children", 'Rightly understood', 'book of nature', 'long periods',
                                    'object of discipline', 'self-government', 'science falsely']),
    ('cg', 'en_CG', range(1, 560), ['in anger', 'the rod', 'self-government', 'scolding', 'Never correct', 'corporal']),
    ('cs', 'en_CS', range(1, 330), ['love of money', 'tithe is the Lord', 'stewards', 'debt']),
    ('col', 'en_COL', range(1, 300), ['Money has great value', 'great good', 'love of money', 'Talents']),
    ('mh', 'en_MH', range(80, 300), ['Pure air, sunlight', 'Grains, fruits, nuts', 'tobacco', 'true temperance', 'intoxicating', 'unequally yoked', 'unbeliever', 'The Child']),
    ('ah', 'en_AH', range(50, 400), ['unequally yoked', 'unbeliever', 'divorce', 'adultery', 'in anger', 'the rod']),
    ('sc', 'en_SC', range(1, 130), ['Why was sin permitted', 'suffering', 'permits', 'Nothing can touch']),
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
