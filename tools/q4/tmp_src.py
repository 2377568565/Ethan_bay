# 临时：下载原始资料并打印文字（全文或只打印关键词附近），供人工核对。查完删除。
import io, re, sys, html, requests
from pypdf import PdfReader

UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36'}
WIKI = 'https://en.wikipedia.org/w/index.php?action=raw&title='
ADV = 'https://documents.adventistarchives.org/'
MIN = 'https://cdn.ministerialassociation.org/cdn/ministrymagazine.org/issues/'
JOBS = [
    ('valentine', 'https://encyclopedia.adventist.org/assets/pdf/article-6JJ3.pdf', None),
    ('esda_cabf', 'https://encyclopedia.adventist.org/article?id=CABF', None),
    ('unruh1977', 'https://www.adventistlaymen.org/Selected%20Documents%20and%20Manuscripts/THE%20SEVENTH-DAY%20ADVENTIST%20EVANGELICAL%20CONFERENCES%20OF%201955-1956.pdf', None),
    ('min2003', 'https://www.ministrymagazine.org/archive/2003/08/questions-on-doctrine-then-and-now.html', None),
    ('min2004', 'https://www.ministrymagazine.org/archive/2004/08/thoughts-on-the-republished-questions-on-doctrine.html', None),
    ('news2003', 'https://adventist.news/news/world-church-questions-on-doctrine-book-annotated-republished', None),
    ('qod2007', 'https://digitalcommons.andrews.edu/qod/', None),
    ('knight_dc', 'https://digitalcommons.andrews.edu/adventist-books/1', None),
    ('w_qod', WIKI + 'Questions_on_Doctrine', None),
    ('w_andreasen', WIKI + 'M._L._Andreasen', None),
    ('w_barnhouse', WIKI + 'Donald_Barnhouse', None),
    ('w_martin', WIKI + 'Walter_Ralston_Martin', None),
    ('w_froom', WIKI + 'Le_Roy_Froom', None),
    ('w_chalc', WIKI + 'Chalcedonian_Definition', None),
    ('min1956_09', 'https://www.ministrymagazine.org/archive/1956/09/christs-nature-during-the-incarnation', None),
    ('min1957_06', 'https://www.ministrymagazine.org/archive/1957/06/seventh-day-adventists-answer-questions-on-doctrine', None),
    ('bri', 'https://adventistbiblicalresearch.org/articles/what-human-nature-did-jesus-take', None),
    ('fortin', 'https://www.andrews.edu/~fortind/EGWNatureofChrist.htm', None),
    ('toews', "https://www.andrews.edu/~toews/classes/sources/adventist/Christ's%20Nature.pdf", None),
    ('min1989', 'https://www.ministrymagazine.org/archive/1989/12/sources-clarify-ellen-whites-christology', None),
    ('car_andreasen', 'https://centerforadventistresearch.org/wp-content/uploads/2023/03/M.-L.-Andreasen-Papers-115.pdf', 12000),
    ('puc', 'https://library.puc.edu/heritage/bib-EvanSDA.html', None),
    ('auss16', 'https://www.andrews.edu/library/car/cardigital/Periodicals/AUSS/2006-1/2006-1-16.pdf', None),
    ('auss17', 'https://www.andrews.edu/library/car/cardigital/Periodicals/AUSS/2006-1/2006-1-17.pdf', None),
    ('greg101', 'https://www.newadvent.org/fathers/3103a.htm', ['not assumed', 'healed', 'Apollinar']),
    ('rh1896a', ADV + 'Periodicals/RH/RH18961215-V73-50.pdf', ['sinful nature', 'vestments of humanity']),
    ('rh1896b', ADV + 'Periodicals/RH/RH18961215-V73-51.pdf', ['sinful nature', 'vestments of humanity']),
    ('yi1900a', ADV + 'Periodicals/YI/YI19001220-V48-50.pdf', ['fallen, suffering', 'defiled by sin', 'human nature']),
    ('yi1900b', ADV + 'Periodicals/YI/YI19001220-V48-51.pdf', ['fallen, suffering', 'defiled by sin', 'human nature']),
    ('br1914', ADV + 'Books/BR1914.pdf', ['sinful, fallen', 'fallen nature', 'sinful nature']),
    ('br1949', ADV + 'Books/BR1949.pdf', ['sinful, fallen', 'fallen nature', 'sinful nature', 'nature of man', 'human nature']),
    ('qod1957', ADV + 'Books/QOD1957.pdf', ['Sinless Human Nature', 'exempt from the inherited', 'vicariously', 'lunatic fringe', 'complete sacrific', 'atoning act']),
    ('min1956_09pdf', MIN + '1956/issues/MIN1956-09.pdf', ['Sinless Human Nature', 'Human, Not Carnal', 'lunatic', 'vicarious', 'Incarnation']),
    ('min1957_04pdf', MIN + '1957/issues/MIN1957-04.pdf', ['Sinless Human Nature', 'Incarnation', 'vicarious']),
]

def text_of(url):
    r = requests.get(url, headers=UA, timeout=90)
    ct = r.headers.get('content-type', '')
    info = f'{r.status_code} {ct} {len(r.content)}B'
    if r.status_code != 200:
        return info, ''
    if 'pdf' in ct or r.content[:4] == b'%PDF':
        pdf = PdfReader(io.BytesIO(r.content))
        t = '\n'.join(f'[[p{i + 1}]] ' + (p.extract_text() or '') for i, p in enumerate(pdf.pages))
    else:
        t = r.text
        if 'action=raw' not in url:
            t = re.sub(r'(?is)<(script|style|nav|footer|header)\b.*?</\1>', ' ', t)
            links = re.findall(r'href="([^"]*(?:viewcontent|\.pdf)[^"]*)"', t)
            t = html.unescape(re.sub(r'<[^>]+>', ' ', t))
            if links:
                t += '\nLINKS: ' + ' '.join(sorted(set(links))[:20])
    return info, re.sub(r'[ \t\r\f\v]+', ' ', re.sub(r'\n\s*\n+', '\n', t))

for key, url, mode in JOBS:
    print(f'\n\n######## {key} {url}', flush=True)
    try:
        info, t = text_of(url)
    except Exception as e:
        print('ERROR', e); continue
    print('##', info, len(t), 'chars')
    if not t:
        continue
    if mode is None:
        print(t[:90000])
    elif isinstance(mode, int):
        print(t[:mode])
    else:
        for pat in mode:
            ms = list(re.finditer(re.escape(pat), t, re.I))
            print(f'  [{pat}] {len(ms)} hits')
            for m in ms[:6]:
                print('   >>', t[max(0, m.start() - 500):m.end() + 500].replace('\n', ' '))
    sys.stdout.flush()
