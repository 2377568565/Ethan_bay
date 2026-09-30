# 由单文件合集生成在线版：字体与经文数据拆成独立文件（带内容哈希），首屏只下载正文
import re, base64, hashlib, os, sys
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
    if fam == 'LessonSerif': pre.append(f'<link rel="preload" href="{name}" as="font" type="font/woff2" crossorigin>')
    return m.group(0).split('src:')[0] + f'src:url({name}) format("woff2")}}'
h, n = re.subn(r'@font-face\{font-family:"(\w+)";font-weight:(\d+);font-style:\w+;font-display:swap;src:url\(data:font/woff2;base64,([^)]*)\) format\("woff2"\)\}', font, h)
assert n == 5, n
m = re.search(r'<script type="application/json" id="bdata">(.*?)</script>', h, re.S)
name = put(m.group(1).encode('utf-8'), 'json')
h = h[:m.start()] + f'<script type="application/json" id="bdata" data-src="{name}"></script>' + h[m.end():]
h = h.replace('<meta name="viewport"', '\n'.join(pre) + '\n<meta name="viewport"', 1)
open(os.path.join(root, 'index.html'), 'w', encoding='utf-8').write(h)
keep = set(re.findall(r'site/[0-9a-f]{10}\.\w+', h))
for f in os.listdir(os.path.join(root, 'site')):
    if f'site/{f}' not in keep: os.remove(os.path.join(root, 'site', f))
print('index.html', len(h.encode()), sorted(keep))
