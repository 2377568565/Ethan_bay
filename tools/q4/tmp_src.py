# 临时：核对问题彩蛋33（宗教这么多，为什么偏偏是耶稣）要用的资料。每读到一份就发一条 check run。查完删除。
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


# ---------- 一、《古兰经》：马坚中译本 + Sahih International 英译 ----------
AYAT = ['1:1', '1:2', '1:3', '1:4', '1:5', '1:6', '1:7', '2:62', '2:75', '2:79', '2:136', '2:183', '2:256', '3:19', '3:45', '3:46', '3:47', '3:49', '3:55',
        '3:59', '3:85', '4:48', '4:157', '4:158', '4:171', '5:46', '5:47', '5:68', '5:72', '5:73', '5:75', '5:116', '5:117', '6:115', '7:8', '7:9',
        '9:30', '10:94', '17:13', '19:19', '19:20', '19:21', '19:30', '19:33', '19:34', '19:35', '23:102', '23:103', '33:40', '39:53', '46:9',
        '61:6', '96:1', '96:2', '96:3', '96:4', '96:5', '99:7', '99:8', '101:6', '101:7', '101:8', '101:9', '112:1', '112:2', '112:3', '112:4', '2:285', '4:136']


def ayah(a):
    for k in range(4):
        try:
            r = requests.get(f'https://api.alquran.cloud/v1/ayah/{a}/editions/zh.jian,en.sahih', headers=UA, timeout=40)
            if r.status_code == 200:
                d = r.json()['data']
                return f'{a}\t' + '\t'.join(f"{e['edition']['identifier']}: {e['text']}" for e in d)
        except Exception as e:
            pass
        time.sleep(2 + 2 * k)
    return f'{a}\tFAIL'


with ThreadPoolExecutor(3) as ex:
    rows = list(ex.map(ayah, AYAT))
post('quran', '\n'.join(rows))

# ---------- 二、网页资料 ----------
W = 'https://en.wikipedia.org/wiki/'
ZW = 'https://zh.wikipedia.org/wiki/'
WS = 'https://zh.wikisource.org/w/index.php?action=raw&title='
CB = 'https://cbdata.dila.edu.tw/stable/juans?work={w}&juan={j}'
SC = 'https://suttacentral.net/api/bilarasuttas/{s}/sujato?lang=en'
JOBS = [
    # 伊斯兰教
    ('hadith_bk', 'https://sunnah.com/bukhari:6463', ['enter Paradise', 'deeds', 'mercy']),
    ('hadith_bk2', 'https://sunnah.com/bukhari:5673', ['enter Paradise', 'deeds', 'mercy']),
    ('hadith_gab', 'https://sunnah.com/muslim:8a', ['Islam', 'Iman', 'Ihsan', 'prayer']),
    ('islam_w', W + 'Islam', ['Muhammad', '610', '622', '632', 'Sunni', 'Shia', 'billion', 'Five Pillars']),
    ('muh_w', W + 'Muhammad', ['570', '610', '622', '632', 'Hijra', 'Medina', 'Cave of Hira']),
    ('quran_w', W + 'Quran', ['recitation', 'Uthman', '114', 'Arabic']),
    ('pillars_w', W + 'Five_Pillars_of_Islam', ['Shahada', 'Salah', 'Zakat', 'Sawm', 'Hajj']),
    ('iman_w', W + 'Iman_(Islam)', ['six', 'angels', 'books', 'Day of Judgement', 'predestination', 'Gabriel']),
    ('jesusislam_w', W + 'Jesus_in_Islam', ['virgin', 'crucif', 'substitution', 'Messiah', 'Injil', 'return', 'son of God']),
    ('tawhid_w', W + 'Tawhid', ['oneness', 'Surah 112', 'shirk']),
    ('tahrif_w', W + 'Tahrif', ['corrupt', 'Torah', 'Gospel', 'Ibn Hazm']),
    ('islamchina_w', W + 'Islam_in_China', ['651', 'Tang', 'Hui']),
    ('majian_w', ZW + '马坚', ['古兰经', '1981', '译']),
    ('mizan_w', W + 'Mizan', ['scale', 'weigh', 'deeds']),
    ('pew_w', W + 'Major_religious_groups', ['Christianity', 'Islam', 'Buddhism', 'percent', 'Pew']),
    ('tacitus_w', W + 'Tacitus_on_Jesus', ['Annals', '116', 'Pontius Pilate', 'Christus']),
    ('josephus_w', W + 'Josephus_on_Jesus', ['Antiquities', '93', 'James', 'Pilate']),
    # 佛教
    ('cb_t0099_15', CB.format(w='T0099', j=15), ['苦聖諦', '轉法輪', '集', '滅', '道']),
    ('cb_t0210_2', CB.format(w='T0210', j=2), ['諸惡莫作', '自淨其意']),
    ('cb_t0360_1', CB.format(w='T0360', j=1), ['十方眾生', '至心信樂', '乃至十念', '不取正覺']),
    ('cb_t0026_60', CB.format(w='T0026', j=60), ['箭', '世有常', '如來終', '不可盡']),
    ('cb_t0001_2', CB.format(w='T0001', j=2), ['自熾燃', '自歸依', '法歸依']),
    ('cb_t0235_1', CB.format(w='T0235', j=1), ['一切有為法', '夢幻泡影']),
    ('cb_t0251_1', CB.format(w='T0251', j=1), ['色即是空', '無苦集滅道', '涅槃']),
    ('ws_xinjing', WS + '般若波羅蜜多心經', ['色即是空', '涅槃']),
    ('ws_fajujing', WS + '法句經/卷下', ['諸惡莫作']),
    ('ws_wuliang', WS + '佛說無量壽經/卷上', ['至心信樂', '十念']),
    ('sc_sn56_11', SC.format(s='sn56.11'), ['suffering', 'origin', 'cessation', 'path', 'craving']),
    ('sc_ud6_4', SC.format(s='ud6.4'), ['elephant', 'blind', 'king']),
    ('sc_mn63', SC.format(s='mn63'), ['arrow', 'eternal', 'undeclared']),
    ('buddha_w', W + 'The_Buddha', ['BCE', 'Lumbini', 'Kushinagar', 'Bodh Gaya', 'Siddhartha', 'four sights']),
    ('fnt_w', W + 'Four_Noble_Truths', ['dukkha', 'samudaya', 'nirodha', 'magga', 'craving']),
    ('marks_w', W + 'Three_marks_of_existence', ['anicca', 'dukkha', 'anatta']),
    ('anatta_w', W + 'Anattā', ['self', 'soul', 'rebirth']),
    ('karma_w', W + 'Karma_in_Buddhism', ['intention', 'rebirth', 'cetana']),
    ('nirvana_w', W + 'Nirvana_(Buddhism)', ['blowing out', 'extinguish', 'rebirth']),
    ('pureland_w', W + 'Pure_Land_Buddhism', ['Amitabha', 'eighteenth vow', 'nianfo', 'Shandao', 'China']),
    ('jodo_w', W + 'Jōdo_Shinshū', ['Shinran', 'Barth', 'Christian', 'other power', 'tariki']),
    ('tanni_w', W + 'Tannishō', ['good person', 'evil person', 'Yuien']),
    ('bodhi_w', W + 'Bodhisattva', ['Mahayana', 'compassion', 'Avalokiteśvara', 'Guanyin']),
    ('buddhachina_w', W + 'Buddhism_in_China', ['Han', 'Emperor Ming', 'White Horse', '67']),
    ('elephant_w', W + 'Blind_men_and_an_elephant', ['Udana', 'Buddh', 'king', 'Jain', 'Newbigin']),
    ('arrow_w', W + 'Parable_of_the_Poisoned_Arrow', ['Malunkyaputta', 'arrow', 'unanswered']),
    ('samsara_w', W + 'Saṃsāra_(Buddhism)', ['six realms', 'gods', 'devas']),
    # 道教
    ('ws_ddj', WS + '道德經', ['道可道', '有物混成', '道生一', '天地不仁', '谷神不死']),
    ('ctext_ddj', 'https://ctext.org/dao-de-jing/zh', ['道可道', '有物混成', '道生一', '天地不仁']),
    ('taoism_w', W + 'Taoism', ['Zhang Daoling', 'Celestial Masters', 'philosophical', 'religious', 'immortality']),
    ('ddj_w', W + 'Tao_Te_Ching', ['Laozi', 'Guodian', '4th century', 'Mawangdui']),
    ('laozi_w', W + 'Laozi', ['historicity', 'legend', 'deified', 'Taishang Laojun']),
    ('zhang_w', W + 'Zhang_Daoling', ['142', 'Five Pecks', 'Celestial']),
    ('elixir_w', W + 'Chinese_alchemical_elixir_poisoning', ['Tang', 'emperor', 'mercury', 'Qin Shi Huang']),
    ('xian_w', W + 'Xian_(Taoism)', ['immortal', 'transcendent']),
    ('cuv_w', W + 'Chinese_Union_Version', ['1919', 'Shangdi', 'Shen', 'Logos', 'Dao']),
    ('logos_w', W + 'Logos_(Christianity)', ['Chinese', 'Dao', 'Tao']),
    # 其他
    ('trilemma_w', W + "Lewis's_trilemma", ['lunatic', 'liar', 'Lord', 'Mere Christianity']),
    ('lewis_wq', 'https://en.wikiquote.org/wiki/Mere_Christianity', ['poached egg', 'lunatic', 'Son of God']),
    ('hound_w', W + 'The_Hound_of_Heaven', ['Francis Thompson', '1890', 'I fled Him']),
    ('hound_txt', 'https://www.gutenberg.org/cache/epub/25269/pg25269.txt', ['I fled Him, down the nights', 'Halts by me']),
    ('hound_ws', 'https://en.wikisource.org/w/index.php?action=raw&title=The_Hound_of_Heaven', ['I fled Him', 'Halts by me']),
    ('sdafb_wa', 'https://web.archive.org/web/2024id_/https://www.adventist.org/the-great-controversy/', ['Christ', 'universe']),
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


RAW = [('da', 'en_DA', range(528, 542)), ('pk', 'en_PK', range(270, 300))]
with ThreadPoolExecutor(2) as ex:
    for key, b, ps in RAW:
        ps = list(ps)
        texts = list(ex.map(page, [(b, p) for p in ps]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(ps, texts))
        post(f'raw_{key}{ps[0]}', full)
