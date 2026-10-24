# 由单文件合集生成在线版：字体与经文数据拆成独立文件（带内容哈希），首屏只下载正文
import re, base64, hashlib, json, os, sys
src, root = sys.argv[1], sys.argv[2]
h = open(src, encoding='utf-8').read()
os.makedirs(os.path.join(root, 'site'), exist_ok=True)
def put(data, ext):
    name = f'site/{hashlib.sha1(data).hexdigest()[:10]}.{ext}'
    open(os.path.join(root, name), 'wb').write(data); return name
pre = []
def font(m):
    fam, w, d = m.group(1), m.group(2), base64.b64decode(m.group(3))
    name = put(d, 'woff2')
    return m.group(0).split('src:')[0] + f'src:url({name}) format("woff2")}}'
h, n = re.subn(r'@font-face\{font-family:"(\w+)";font-weight:(\d+);font-style:\w+;font-display:swap;src:url\(data:font/woff2;base64,([^)]*)\) format\("woff2"\)\}', font, h)
assert n == 5, n
# 正文字体（LessonSerif 两个粗细，各约 400 KB）不写在样式表里：由 app.js 从手机里取（没有才下载），见 app.js 的 q4keep
wf = []
def body_font(m):
    wf.append([m.group(1), m.group(2), m.group(3)]); return ''
h, n = re.subn(r'@font-face\{font-family:"(LessonSerif)";font-weight:(\d+);font-style:normal;font-display:swap;src:url\((site/[0-9a-f]{10}\.woff2)\) format\("woff2"\)\}', body_font, h)
assert n == 2, n
h = h.replace('</head>', '<script type="application/json" id="wfonts">' + json.dumps(wf) + '</script>\n</head>', 1)
m = re.search(r'<script type="application/json" id="bdata">(.*?)</script>', h, re.S)
name = put(m.group(1).encode('utf-8'), 'json')
h = h[:m.start()] + f'<script type="application/json" id="bdata" data-src="{name}"></script>' + h[m.end():]
# 正文字体（两个各约 400 KB）不在首屏抢网速：脚本就绪后才给 html 加上 wf，这时 --serif 才用到它们（字体会自动换上）
h = h.replace('</head>', '<style>html:not(.wf){--serif:"Noto Serif SC","Source Han Serif SC","Songti SC","STSong","SimSun",serif}</style>\n</head>', 1)
# 各课正文（<main> 里面，约 1.2 MB）和主程序（约 220 KB）拆成带内容哈希的独立文件：
# 首页只剩骨架；这两份由开头的小脚本取来（手机里存过就直接用，没有才下载），放回原处后再运行主程序。
# 网站每次发布，读者只需重新下载骨架；正文和程序只有真的改了（换了名字）才重新下载。
lz = {}
for n in range(0, 14):
    i = h.index(f'<div class="lesson" id="l{n}"')
    a = h.index('<main>', i) + len('<main>'); b = h.index('</main>', a)
    assert h.index('<div class="layout">', i) < a < h.index('</div>', h.index('<nav class="lnext"', i)) and '<script' not in h[a:b]
    lz[f'l{n}'] = h[a:b]
    h = h[:a] + h[b:]
bname = put(json.dumps(lz, ensure_ascii=False, separators=(',', ':')).encode('utf-8'), 'json')
big = [m for m in re.finditer(r'<script>(.*?)</script>', h, re.S) if len(m.group(1)) > 100000]
assert len(big) == 1
m = big[0]
jname = put(m.group(1).encode('utf-8'), 'js')
h = h[:m.start()] + h[m.end():]
boot = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'boot.js'), encoding='utf-8').read()
boot = re.sub(r'(?m)^\s*//.*\n', '', boot).replace('%B%', json.dumps(bname)).replace('%J%', json.dumps(jname))
h = h.replace('</head>', '<script>' + boot + '</script>\n</head>', 1)
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(h)
keep = set(re.findall(r'site/[0-9a-f]{10}\.\w+', h))
for f in os.listdir(os.path.join(root, 'site')):
    if f'site/{f}' not in keep: os.remove(os.path.join(root, 'site', f))
print('index.html', len(h.encode()), sorted(keep))
