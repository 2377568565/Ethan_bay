# 临时：核对问题彩蛋33（宗教这么多，为什么偏偏是耶稣）要用的资料（第三次：犹太教）。每读到一份就发一条 check run。查完删除。
import os, re, html, json, time, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
API = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
HD = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}


def post(key, t):
    t = t or '(empty)'
    for i in range(0, len(t), 64000):
        k = key if i == 0 else f'{key}_{i // 64000}'
        r = requests.post(API, headers=HD, json={'name': f'chk:{k}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                          'conclusion': 'neutral', 'output': {'title': k, 'summary': k, 'text': t[i:i + 64000]}})
        print('check', k, len(t), r.status_code, flush=True)
        if i >= 64000 * 3:
            break


def get(url, raw=False):
    r = requests.get(url, headers=UA, timeout=40)
    if r.status_code != 200:
        return r.status_code, ''
    if raw:
        return 200, r.text
    t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', r.text)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    return 200, re.sub(r'\s+', ' ', t)


def ctx(full, pats, n=3, w=900):
    parts = []
    for pat in pats:
        ms = list(re.finditer(re.escape(pat), full, re.I))
        parts.append(f'[{pat}] {len(ms)}')
        last = -10**9
        k = 0
        for m in ms:
            if m.start() - last < w or k >= n:
                continue
            last = m.start(); k += 1
            parts.append('>> ' + full[max(0, m.start() - w):m.end() + w])
    return '\n'.join(parts)


# ---------- 二、网页资料 ----------
W = 'https://en.wikipedia.org/wiki/'
ZW = 'https://zh.wikipedia.org/wiki/'
WS = 'https://zh.wikisource.org/w/index.php?action=raw&title='
CB = 'https://cbdata.dila.edu.tw/stable/juans?work={w}&juan={j}'
SC = 'https://suttacentral.net/api/bilarasuttas/{s}/sujato?lang=en'
JOBS = [
    ('sf_rashi52', 'https://www.sefaria.org/api/texts/Rashi_on_Isaiah.52.13?context=0&commentary=0', []),
    ('sf_rashi53_3', 'https://www.sefaria.org/api/texts/Rashi_on_Isaiah.53.3?context=0&commentary=0', []),
    ('sf_rashi53_4', 'https://www.sefaria.org/api/texts/Rashi_on_Isaiah.53.4?context=0&commentary=0', []),
    ('sf_san43a', 'https://www.sefaria.org/api/texts/Sanhedrin.43a?context=0&commentary=0', []),
    ('sf_avot11', 'https://www.sefaria.org/api/texts/Pirkei_Avot.1.1?context=0&commentary=0', []),
    ('sf_makkot23b', 'https://www.sefaria.org/api/texts/Makkot.23b?context=0&commentary=0', []),
    ('sf_kings11', 'https://www.sefaria.org/api/texts/Mishneh_Torah,_Kings_and_Wars.11?context=0&commentary=0', []),
    ('sf_targum52', 'https://www.sefaria.org/api/texts/Targum_Jonathan_on_Isaiah.52.13?context=0&commentary=0', []),
    ('sf_arn4', "https://www.sefaria.org/api/texts/Avot_D'Rabbi_Natan.4?context=0&commentary=0", []),
    ('jud_w', W + 'Judaism', ['million', 'Orthodox', 'Conservative', 'Reform', 'Tanakh', 'Talmud']),
    ('jpop_w', W + 'Jewish_population_by_country', ['million', 'total', 'world']),
    ('princ_w', W + 'Jewish_principles_of_faith', ['Maimonides', 'thirteen', 'Messiah', 'resurrection', 'Ani Ma']),
    ('maim_w', W + 'Maimonides', ['1138', '1204', 'Mishneh Torah', 'Cordoba']),
    ('rashi_w', W + 'Rashi', ['1040', '1105', 'Troyes', 'commentary']),
    ('talmud_w', W + 'Talmud', ['Mishnah', '200 CE', 'Babylonian', 'Jerusalem Talmud', '500']),
    ('oral_w', W + 'Oral_Torah', ['Sinai', 'Mishnah', 'Pharisees']),
    ('613_w', W + '613_commandments', ['Makkot', '248', '365']),
    ('jmess_w', W + 'Jewish_messianism', ['Davidic', 'Temple', 'exiles', 'peace']),
    ('jvj_w', W + "Judaism's_view_of_Jesus", ['messiah', 'prophecies', 'Maimonides', 'did not fulfill']),
    ('jtalmud_w', W + 'Jesus_in_the_Talmud', ['Sanhedrin 43a', 'Passover', 'hanged', 'Yeshu']),
    ('isa53_w', W + 'Isaiah_53', ['Rashi', 'Israel', 'Targum', 'messiah', 'Acts 8']),
    ('siege70_w', W + 'Siege_of_Jerusalem_(70_CE)', ['70', 'Titus', 'Temple', 'destroyed']),
    ('rabbinic_w', W + 'Rabbinic_Judaism', ['Yohanan ben Zakkai', 'Yavne', 'sacrifice', 'prayer']),
    ('kaifeng_w', W + 'Kaifeng_Jews', ['Song', '1163', 'synagogue']),
    ('jdenom_w', W + 'Jewish_religious_movements', ['Orthodox', 'Conservative', 'Reform']),
    ('antisem_w', W + 'Antisemitism_in_Christianity', ['Crusade', '1096', 'Second Vatican', 'Nostra aetate', 'Luther']),
    ('messianic_w', W + 'Messianic_Judaism', ['Yeshua', 'estimate', 'Jews for Jesus']),
    ('shema_w', W + 'Shema_Yisrael', ['morning', 'evening', 'Deuteronomy 6']),
    ('yetzer_w', W + 'Yetzer_hara', ['inclination', 'evil', 'good']),
    ('yomkippur_w', W + 'Yom_Kippur', ['atonement', 'repentance', 'Temple']),
    ('dan9_w', W + "Daniel_9", ['anointed', 'cut off', 'seventy weeks']),
]


def job(j):
    key, url, pats = j
    try:
        c, t = get(url)
    except Exception as e:
        c, t = str(e)[:80], ''
    if c != 200:
        time.sleep(3)
        try:
            c, t = get(url)
        except Exception as e:
            c, t = str(e)[:80], ''
    return key, f'{c} {url}\n' + (ctx(t, pats) if pats else t[:60000])


with ThreadPoolExecutor(3) as ex:
    for key, txt in ex.map(job, JOBS):
        post(key, txt)

# ---------- 三、怀爱伦著作逐页原版 ----------
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'


def page(bp):
    b, p = bp
    for k in range(5):
        time.sleep(1.5 * (k + 1))
        try:
            c, t = get(M.format(b=b, p=p))
            if c == 200:
                return t.split('Nächste Seite »')[-1]
        except Exception:
            pass
    return ''


RAW = []
with ThreadPoolExecutor(2) as ex:
    for key, b, ps in RAW:
        ps = list(ps)
        texts = list(ex.map(page, [(b, p) for p in ps]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(ps, texts))
        post(f'raw_{key}{ps[0]}', full)
