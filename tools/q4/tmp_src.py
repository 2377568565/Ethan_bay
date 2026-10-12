# 临时：核对《安息日与星期日》要用的资料（网页 + 怀著原版逐页文字），只存关键句前后文。查完删除。
import io, os, re, html, requests
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
W = 'https://en.wikipedia.org/wiki/'
JOBS = [
    ('augsburg', 'https://bookofconcord.org/augsburg-confession/', ['Sabbath', "Lord's Day"]),
    ('ccc', 'https://www.vatican.va/archive/ENG0015/__P7O.HTM', ['2174', '2175', '2190']),
    ('cathen', 'https://www.newadvent.org/cathen/14335a.htm', ['Sabbath', 'Constantine', '321']),
    ('gibbons', 'https://www.gutenberg.org/cache/epub/27435/pg27435.txt', ['sanctification of Sunday', 'Saturday', 'Sabbath']),
    ('wcf', 'https://bpc.org/wcf-ch-21', ['first day of the week', "Lord's day"]),
    ('dies', 'https://www.vatican.va/content/john-paul-ii/en/apost_letters/1998/documents/hf_jp-ii_apl_05071998_dies-domini.html', ['Constantine', 'civil', 'Sabbath']),
    ('greg', W + 'Gregorian_calendar', ['15 October', 'day of the week', 'weekday']),
    ('days', W + 'Names_of_the_days_of_the_week', ['Sabbath', 'sábado', 'Shabbat']),
    ('week', W + 'Week', ['ISO 8601', 'continuous', 'Sabbath', 'Monday']),
    ('zhweek', 'https://zh.wikipedia.org/wiki/%E6%98%9F%E6%9C%9F', ['礼拜', '星期日', '星期六', '传教士']),
    ('sunday', W + 'Sunday', ['venerable', '321', 'Constantine']),
    ('sabx', W + 'Sabbath_in_Christianity', ['Seventh-day', 'Ethiopian', 'Laodicea']),
    ('bates', W + 'Joseph_Bates_(Adventist)', ['Sabbath', '1846']),
    ('preston', W + 'Rachel_Oakes_Preston', ['Sabbath', '1844']),
    ('st1936', 'https://documents.adventistarchives.org/Periodicals/STAUS/STAUS19360608-V51-23.pdf', ['October', '1582']),
]
M = 'https://media2.egwwritings.org/swf/{b}/files/assets/seo/page{p}.html'
EGW = [('gc_a', 'en_GC', range(38, 76), ['Sunday', 'Constantine', 'first day']),
       ('gc_b', 'en_GC', range(338, 382), ['Sabbath', 'fourth commandment', 'first day', 'change']),
       ('da_a', 'en_DA', range(218, 276), ['Sabbath was', 'made for man', 'Lord also of the Sabbath', 'sign']),
       ('pp_a', 'en_PP', range(36, 62), ['Sabbath', 'seventh day'])]


def get(url):
    r = requests.get(url, headers=UA, timeout=90)
    if r.status_code != 200:
        return r.status_code, ''
    if r.content[:4] == b'%PDF':
        from pypdf import PdfReader
        t = ' '.join(f'[[p{i + 1}]] ' + (p.extract_text() or '') for i, p in enumerate(PdfReader(io.BytesIO(r.content)).pages))
    else:
        t = re.sub(r'(?is)<(script|style)\b.*?</\1>', ' ', r.text)
        t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
    return 200, re.sub(r'\s+', ' ', t).replace('ﬁ', 'fi').replace('ﬂ', 'fl')


def ctx(key, full, pats, n=4, w=900):
    parts = [key]
    for pat in pats:
        ms = list(re.finditer(re.escape(pat), full, re.I))
        parts.append(f'[{pat}] {len(ms)}')
        for m in ms[:n]:
            parts.append('>> ' + full[max(0, m.start() - w):m.end() + w])
    return '\n'.join(parts)


OUT = {}
for key, url, pats in JOBS:
    try:
        code, t = get(url)
    except Exception as e:
        code, t = str(e)[:80], ''
    print(key, code, len(t), flush=True)
    OUT[key] = f'{code} {url}\n' + ctx(key, t, pats)
for key, b, ps, pats in EGW:
    full = ''
    for p in ps:
        try:
            c, t = get(M.format(b=b, p=p))
        except Exception:
            t = ''
        full += f' {{seo{p}}} ' + t.split('Nächste Seite »')[-1]
    OUT[key] = key + ' marks: ' + ' '.join(re.findall(r'\{seo\d+\} \S+ \S+ \S+|\[\d{2,3}\]', full)) + '\n' + ctx(key, full, pats, n=6, w=1400)
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}
for key, t in OUT.items():
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                      'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': t[:65000]}})
    print('check', key, len(t), r.status_code)
