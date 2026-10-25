# 临时：核对问题彩蛋34（没听过耶稣的祖先会怎样）要用的资料。每读到一份就发一条 check run。查完删除。
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
WQ = 'https://en.wikiquote.org/wiki/'
WS = 'https://zh.wikisource.org/w/index.php?action=raw&title='
NA = 'https://www.newadvent.org/'
CC = 'https://www.scborromeo.org/ccc/para/{}.htm'
WA = 'https://web.archive.org/web/2024id_/'
JOBS = [
    # 历史上的人怎样问这个问题
    ('xavier_fh', 'https://sourcebooks.fordham.edu/mod/1552xavier4.asp', ['hell', 'ancestors', 'grieve', 'tears', 'remedy', 'parents']),
    ('xavier_fh2', 'https://sourcebooks.fordham.edu/mod/1552xavier.asp', ['hell', 'ancestors', 'grieve', 'tears']),
    ('xavier_ia', 'https://archive.org/advancedsearch.php?q=title%3A%28life+and+letters+of+st.+francis+xavier%29&fl%5B%5D=identifier&fl%5B%5D=title&fl%5B%5D=volume&rows=20&output=json', []),
    ('xavier_w', W + 'Francis_Xavier', ['Japan', '1549', 'Kagoshima', 'Yamaguchi', '1552', 'Shangchuan', 'hell']),
    ('radbod_w', W + 'Redbad,_King_of_the_Frisians', ['baptis', 'ancestors', 'Wulfram', 'hell', 'heaven', '719']),
    ('wulfram_w', W + 'Wulfram_of_Sens', ['Radbod', 'Redbad', 'baptis', 'ancestors']),
    ('virtuous_w', W + 'Virtuous_pagan', ['Justin', 'Zwingli', 'Dante', 'Limbo', 'Trajan', 'Socrates', 'Hercules', 'Aquinas', 'Wesley']),
    ('justin46', NA + 'fathers/0126.htm', ['Chapter 46', 'Heraclitus', 'Christians, even though']),
    ('aug_conf3', NA + 'fathers/110103.htm', ['son of these tears', 'Chapter 12']),
    ('dante4_it', 'https://it.wikisource.org/w/index.php?action=raw&title=Divina_Commedia/Inferno/Canto_IV', ['speme', 'battesmo', 'sospesi']),
    ('dante4_s', 'https://en.wikisource.org/w/api.php?action=query&list=search&srsearch=%22without+hope+we+live+on+in+desire%22&format=json', []),
    ('dante4_w', W + 'Limbo', ['Dante', 'Limbo of the Fathers', 'Limbo of Infants', '2007', 'International Theological Commission']),
    # 各派的说法
    ('wcf_text', 'https://www.opc.org/wcf.html', ['Elect infants', 'much less can men', 'light of nature', 'outward means']),
    ('ccc847', CC.format(847), ['through no fault', 'sincere heart']),
    ('ccc848', CC.format(848), ['ways known to himself', 'urgent']),
    ('ccc1260', CC.format(1260), ['ignorant of the Gospel', 'implicitly']),
    ('ccc1261', CC.format(1261), ['children who have died without Baptism']),
    ('lg16', 'https://www.vatican.va/archive/hist_councils/ii_vatican_council/documents/vat-ii_const_19641121_lumen-gentium_en.html', ['through no fault of their own', 'preparation for the Gospel', 'unknown God']),
    ('wesley106', 'https://wesley.nnu.edu/john-wesley/the-sermons-of-john-wesley-1872-edition/sermon-106-on-faith/', ['heathen', 'Mahometan', 'Father of the spirits', 'hateth nothing']),
    ('wesley106b', 'https://www.ccel.org/ccel/wesley/sermons.v.cvi.html', ['heathen', 'Mahometan', 'Father of the spirits']),
    ('lewis_mc_wq', WQ + 'Mere_Christianity', ['know Him can be saved', 'saved through Him', 'other religions', 'except through Christ']),
    ('lewis_lb_wq', WQ + 'The_Last_Battle', ['Emeth', 'Tash', 'service', 'accept it as done to me']),
    ('anon_w', W + 'Anonymous_Christian', ['Rahner', 'never heard']),
    ('inclus_w', W + 'Inclusivism', ['Christ', 'Rahner', 'Lewis', 'Pinnock']),
    ('restrict_w', W + 'Exclusivism', ['Christ', 'salvation']),
    ('extra_w', W + 'Extra_Ecclesiam_nulla_salus', ['Cyprian', 'Florence', 'invincible ignorance', 'Pius IX', 'Feeney']),
    ('harrow_w', W + 'Harrowing_of_Hell', ['1 Peter', 'Apostles', 'descended']),
    ('univ_w', W + 'Universal_reconciliation', ['Origen', 'apokatastasis']),
    ('bftd_w', W + 'Baptism_for_the_dead', ['Latter', '1 Corinthians 15:29', 'proxy', 'ancestors']),
    ('postmort_w', W + 'Postmortem_conversion', ['Peter', 'after death']),
    # 中国古代的“上帝”和最早的基督教
    ('shangdi_w', W + 'Shangdi', ['oracle', 'Shang', 'Zhou', 'Ricci', 'Legge', 'Heaven']),
    ('legge_w', W + 'James_Legge', ['Shangdi', 'God', 'Notions', '1852', 'Shang Di']),
    ('tianzhu_zw', ZW + '天主實義', ['1603', '上帝', '利瑪竇']),
    ('tianzhu_ws', WS + '天主實義', []),
    ('tianzhu_s', 'https://zh.wikisource.org/w/api.php?action=query&list=search&srsearch=%E5%8F%A4%E7%B6%93%E6%9B%B8%E6%89%80%E7%A8%B1%E4%B8%8A%E5%B8%9D&format=json', []),
    ('huangyi_ws', WS + '詩經/皇矣', []),
    ('daming_ws', WS + '詩經/大明', []),
    ('shundian_ws', WS + '尚書/舜典', []),
    ('xianjin_ws', WS + '論語/先進', []),
    ('stele_zw', ZW + '大秦景教流行中國碑', ['781', '635', '阿羅本', '貞觀', '西安']),
    ('stele_w', W + 'Nestorian_Stele', ['781', '635', 'Alopen', 'Xi']),
    ('ricci_w', W + 'Matteo_Ricci', ['1583', '1601', 'Beijing', 'True Meaning', '1603']),
    ('sinim_w', W + 'Sinim', ['China', 'Syene', 'Aswan', 'Isaiah 49']),
    ('sinim_w2', W + 'Land_of_Sinim', ['China', 'Syene', 'Aswan']),
    # 诗
    ('faber_hy', 'https://hymnary.org/text/theres_a_wideness_in_gods_mercy', ['wideness', 'kindness in his justice', 'Faber', '1854']),
    ('faber_ft', 'https://hymnary.org/text/theres_a_wideness_in_gods_mercy/fulltexts', ['wideness']),
    ('faber_ct', 'https://hymntime.com/tch/htm/t/h/e/r/thereswi.htm', ['wideness']),
    ('faber_w', W + "There's_a_Wideness_in_God's_Mercy", ['Faber', '1854', 'Souls of men']),
    ('faber_ws', 'https://en.wikisource.org/w/api.php?action=query&list=search&srsearch=%22Souls+of+men%2C+why+will+ye+scatter%22&format=json', []),
    ('whit_ws', 'https://en.wikisource.org/w/index.php?action=raw&title=The_Eternal_Goodness', []),
    ('whit_s', 'https://en.wikisource.org/w/api.php?action=query&list=search&srsearch=%22I+know+not+where+His+islands+lift%22&format=json', []),
    ('whit_w', W + 'The_Eternal_Goodness', ['Whittier', '1865', 'islands']),
    ('whit_gut', 'https://www.gutenberg.org/ebooks/search/?query=whittier+poems', []),
]


def job(j):
    key, url, pats = j
    try:
        c, t = get(url, raw=('action=raw' in url or 'api.php' in url or 'advancedsearch' in url))
    except Exception as e:
        c, t = str(e)[:80], ''
    if c != 200:
        time.sleep(3)
        try:
            c, t = get(url, raw=('action=raw' in url or 'api.php' in url or 'advancedsearch' in url))
        except Exception as e:
            c, t = str(e)[:80], ''
    return key, f'{c} {url}\n' + (ctx(t, pats) if pats else t[:60000])


with ThreadPoolExecutor(3) as ex:
    for key, txt in ex.map(job, JOBS):
        post(key, txt)

# ---------- 怀爱伦著作逐页原版（PK 188—189：以利亚和七千人，“在中国……”） ----------
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


RAW = [('pk', 'en_PK', range(58, 96))]
with ThreadPoolExecutor(2) as ex:
    for key, b, ps in RAW:
        ps = list(ps)
        texts = list(ex.map(page, [(b, p) for p in ps]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(ps, texts))
        post(f'raw_{key}{ps[0]}', full)
