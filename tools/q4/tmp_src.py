# 临时：核对问题彩蛋32（天堂）要用的资料（网页关键句 + 怀著原版逐页文字）。查完删除。
import io, os, re, html, requests
from concurrent.futures import ThreadPoolExecutor
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
JOBS = [
    ('ccc1023', 'https://www.scborromeo.org/ccc/para/1023.htm', []),
    ('ccc1024', 'https://www.scborromeo.org/ccc/para/1024.htm', []),
    ('ccc1025', 'https://www.scborromeo.org/ccc/para/1025.htm', []),
    ('ccc1026', 'https://www.scborromeo.org/ccc/para/1026.htm', []),
    ('ccc1027', 'https://www.scborromeo.org/ccc/para/1027.htm', []),
    ('ccc1028', 'https://www.scborromeo.org/ccc/para/1028.htm', []),
    ('ccc1029', 'https://www.scborromeo.org/ccc/para/1029.htm', []),
    ('ccc1042', 'https://www.scborromeo.org/ccc/para/1042.htm', []),
    ('ccc1043', 'https://www.scborromeo.org/ccc/para/1043.htm', []),
    ('ccc1044', 'https://www.scborromeo.org/ccc/para/1044.htm', []),
    ('ccc1045', 'https://www.scborromeo.org/ccc/para/1045.htm', []),
    ('ccc1046', 'https://www.scborromeo.org/ccc/para/1046.htm', []),
    ('ccc1047', 'https://www.scborromeo.org/ccc/para/1047.htm', []),
    ('ccc1048', 'https://www.scborromeo.org/ccc/para/1048.htm', []),
    ('aug2230', 'https://www.newadvent.org/fathers/120122.htm', ['rest and see', 'end without end', 'seventh day', 'free will', 'recogni', 'know one another', 'see God']),
    ('aug2229', 'https://www.newadvent.org/fathers/120122.htm', ['Chapter 29', 'bodily eyes', 'spiritual body']),
    ('iren532', 'https://www.newadvent.org/fathers/0103532.htm', ['that very creation', 'restored', 'Abraham', 'inherit']),
    ('iren536', 'https://www.newadvent.org/fathers/0103536.htm', ['mansions', 'new heaven', 'hundred-fold', 'paradise', 'city']),
    ('ber17a', 'https://www.sefaria.org/api/texts/Berakhot.17a?context=0&commentary=0', ['World-to-Come', 'World to Come', 'eating', 'radiance', 'crowns']),
    ('lewis_mc', 'https://archive.org/stream/MereChristianityCSLewis/Mere%20Christianity%20-%20C.%20S.%20Lewis_djvu.txt', ['another world', 'no experience in this world', 'Aim at Heaven']),
    ('lewis_mc2', 'https://www.fadedpage.com/books/20140843/html.php', ['another world', 'no experience in this world', 'Aim at Heaven']),
    ('chesterton', 'https://www.gutenberg.org/cache/epub/130/pg130.txt', ['Do it again', 'appetite of infancy', 'younger than we']),
    ('sdafb_pdf', 'https://www.adventist.org/wp-content/uploads/2020/06/ADV-28Beliefs2020.pdf', ['Millennium', 'New Earth', 'eternal home', 'thousand years']),
    ('heaven_w', W + 'Heaven_in_Christianity', ['harp', 'cloud', 'New Earth', 'beatific', 'Adventist', 'recogni']),
    ('newjer_w', W + 'New_Jerusalem', ['12,000', 'stadia', 'cube', 'Holy of Holies', '144']),
    ('stadion_w', W + 'Stadion_(unit)', ['185', 'Attic', 'metres', 'Roman']),
    ('twain_w', W + 'Letters_from_the_Earth', ['harp', 'heaven', '1909', '1962', 'sing']),
    ('wright_w', W + 'Surprised_by_Hope', ['2008', 'end of the world', 'resurrection', 'new creation']),
    ('beat_w', W + 'Beatific_vision', ['face to face', '1 Corinthians', 'Aquinas', 'Benedict XII']),
    ('inter_w', W + 'Intermediate_state', ['soul sleep', 'Adventist', 'Luther', 'Tyndale']),
    ('parad_w', W + 'Paradise', ['Persian', 'pairi', 'walled', 'Septuagint']),
    ('mc_w', W + 'Mere_Christianity', ['1952', 'broadcast', 'BBC', '1941']),
    ('wtc_w', W + 'World_to_come', ['Olam', 'Berakhot', 'eating', 'Maimonides']),
    ('somasema_w', W + 'Soma_sema', ['tomb', 'Gorgias', 'Cratylus', 'Orphic']),
    ('mansion_w', 'https://en.wiktionary.org/wiki/mansio', ['dwelling', 'staying', 'station']),
    ('nhe_w', W + 'New_Heaven_and_New_Earth', ['Isaiah 65', 'Revelation 21', 'renewal', 'annihilation', 'Adventist']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = []
RAW = [('gca', 'en_GC', range(576, 585)), ('gcb', 'en_GC', range(606, 617)), ('ed', 'en_Ed', range(230, 245)), ('pp', 'en_PP', range(36, 43)), ('sm1', 'en_1SM', range(155, 173))]


def get(url):
    r = requests.get(url, headers=UA, timeout=40)
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
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}


def post(key, t):
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                      'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:65000]}})
    print('check', key, len(t), r.status_code, flush=True)


for key, url, pats in JOBS:
    try:
        c, t = get(url)
    except Exception as e:
        c, t = str(e)[:80], ''
    post(key, f'{c} {url}\n' + (ctx(key, t, pats) if pats else t[:60000]))


def page(bp):
    b, p = bp
    import time
    for k in range(5):
        time.sleep(1.5 * (k + 1))
        try:
            c, t = get(M.format(b=b, p=p))
            if c == 200:
                return t.split('Nächste Seite »')[-1]
        except Exception:
            pass
    return ''


with ThreadPoolExecutor(2) as ex:
    for key, b, ps, pats in EGW:
        ps = list(ps)
        texts = list(ex.map(page, [(b, p) for p in ps]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(ps, texts))
        r = ctx(key, full, pats, n=4)
        for i in range(0, max(1, len(r)), 60000):
            OUT[f'{key}_{i // 60000}'] = f'{key} pages ok {sum(1 for t in texts if t)}/{len(ps)}\n' + r[i:i + 60000]
OFF = {'en_GC': 0, 'en_Ed': 0, 'en_PP': 0, 'en_1SM': 0}   # 这次直接用 seo 页号
with ThreadPoolExecutor(2) as ex:
    for key, b, ps in RAW:
        seo = [p + OFF[b] for p in ps]
        texts = list(ex.map(page, [(b, p) for p in seo]))
        full = ''.join(f' {{seo{p}}} ' + t for p, t in zip(seo, texts))
        for i in range(0, max(1, len(full)), 60000):
            post(f'raw_{key}{ps[0]}_{i // 60000}', full[i:i + 60000])
