# 研经问答 PDF：核对经文引文 → 组装 HTML → Chromium 输出 PDF → 每页 PNG 预览
import re, os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'q4'))
import bible

def verses(ref):
    m = re.match(r'(\D+?)(\d.*)$', ref)
    b = bible.NAME2IDX[m.group(1)]
    out, ch = [], None
    for part in re.split('[、，,；;]', m.group(2)):
        if ':' in part: ch, vs = part.split(':')
        else: vs = part
        a, _, z = vs.partition('-')
        for v in range(int(a), int(z or a) + 1):
            try: out.append(bible.cuv(b, int(ch), v))
            except IndexError:   # 数据源个别章节合并了经节，退回整章比对
                out.append(''.join(bible.cuv(b, int(ch), i + 1) for i in range(len(bible._cuv[b]['chapters'][int(ch) - 1]))))
    return ''.join(out)

def norm(s):
    s = re.sub(r'<[^>]+>', '', s).replace('藉', '借')
    return re.sub(r'[\s　，。；：、！？“”‘’「」『』（）()…—\-－·,.;:!?]', '', s)

def check(html, name):
    bad = 0
    for m in re.finditer(r'<(\w+)[^>]*data-ref="([^"]+)"[^>]*>(.*?)</\1>', html, re.S):
        body = re.sub(r'<cite>.*?</cite>', '', m.group(3), flags=re.S)
        src = norm(verses(m.group(2)))
        for chunk in body.split('……'):
            c = norm(chunk)
            if c and c not in src:
                bad += 1; print(f'  ✗ {name} {m.group(2)}: 「{chunk.strip()}」\n    和合本：{verses(m.group(2))}')
    n = len(re.findall('data-ref=', html))
    print(f'{name}: 经文引文 {n} 处，不符 {bad} 处')
    return bad

def heb(key):
    b, c, v = map(int, key.split('.'))
    ws = bible.original([(b, c, v)])[(b, c, v)]
    s = ''
    for w in ws: s += w[0] + ('' if w[0].endswith('־') else ' ')
    return s.strip()

def page(frag):
    title = re.search(r'<!--title: (.*?)-->', frag).group(1)
    frag = re.sub(r'\{\{HEB ([\d.]+)\}\}', lambda m: heb(m.group(1)), frag)
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{title}</title>
<link rel="stylesheet" href="style.css"></head><body>{frag}</body></html>'''

if __name__ == '__main__':
    jobs = [('q1', '研经问答01-罪孽为何使人与上帝隔绝'), ('q2', '研经问答02-罪从哪里来')]
    bad = 0
    for key, out in jobs:
        frag = open(os.path.join(HERE, key + '.html'), encoding='utf-8').read()
        bad += check(frag, key)
        open(os.path.join(HERE, f'_{key}.html'), 'w', encoding='utf-8').write(page(frag))
    if bad and '--force' not in sys.argv: sys.exit('经文核对未通过')
    json.dump(jobs, open(os.path.join(HERE, '_jobs.json'), 'w'), ensure_ascii=False)
    subprocess.run(['node', os.path.join(HERE, 'pdf.js')], check=True)
