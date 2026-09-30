import re, base64, io, sys
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools import subset
import os
S = os.environ.get('Q4_WORK', '/tmp/claude-0/-home-user-Ethan-bay/7a8f6135-8731-54b9-8b54-015171d16fd2/scratchpad')
src, out = sys.argv[1], sys.argv[2]
html = open(src, encoding='utf-8').read()
body = re.sub(r'<style.*?</style>|<script.*?</script>', '', html, flags=re.S)
text = re.sub(r'<[^>]+>', '', body)
text += re.sub(r'.*?content:"([^"]*)".*?', r'\1', ''.join(re.findall(r'content:"[^"]*"', html)))
text += '已保存在本机此浏览器无法保存＋－今天是月日星期安息日本周学课第课进入今日导言本季学课将于开始先读已经学完回顾全季十三课今日安息日学课堂小时分钟出自《》✦→—'
jm = re.search(r'<script type="application/json" id="bdata">(.*?)</script>', html, re.S)
jtext = jm.group(1) if jm else ''
heb = ''.join(sorted({c for c in jtext + text if '\u0590' <= c <= '\u05FF' or '\uFB1D' <= c <= '\uFB4F'}))
grk = ''.join(sorted({c for c in jtext if ('\u0370' <= c <= '\u03FF' or '\u1F00' <= c <= '\u1FFF' or '\u00C0' <= c <= '\u024F' or '\u1E00' <= c <= '\u1EFF') }))
text += '和合本上帝版原文直译希伯来文希腊文逐字连读英文中文词典原形字义节此处只显示前经文较长共三版本对照点单词看今天下午开始新课今日安息日学课堂知信行与讨论'
chars = set(text) | set('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz .,:;!?-—–“”‘’（）《》「」、。，：；！？…·/↔→')
chars = ''.join(sorted(c for c in chars if not c.isspace() or c == ' '))
def sub(font, keep):
    o = subset.Options(); o.flavor = 'woff2'; o.layout_features = ['*']; o.notdef_outline = True
    s = subset.Subsetter(o); s.populate(text=keep); s.subset(font)
    b = io.BytesIO(); font.flavor = 'woff2'; font.save(b); return b.getvalue()
faces = []
for w in (600, 900):
    f = instancer.instantiateVariableFont(TTFont(f'{S}/fonts/serif.ttf'), {'wght': w})
    faces.append(('LessonSerif', w, 'normal', sub(f, chars)))
for fn, st in (('gentium.ttf', 'normal'), ('gentium-italic.ttf', 'italic')):
    faces.append(('LessonGreek', 400, st, sub(TTFont(f'{S}/fonts/{fn}'), ''.join(c for c in chars if ord(c) < 0x3000) + grk)))
if heb:
    faces.append(('LessonHebrew', 400, 'normal', sub(TTFont(f'{S}/fonts/hebrew.ttf'), heb + '־ ')))
css = '\n'.join(f'@font-face{{font-family:"{n}";font-weight:{w};font-style:{st};font-display:swap;src:url(data:font/woff2;base64,{base64.b64encode(d).decode()}) format("woff2")}}' for n, w, st, d in faces)
html = html.replace('/*FONTS*/', css, 1)
open(out, 'w', encoding='utf-8').write(html)
print('chars', len(chars), 'bytes', len(html.encode()), [len(d) for *_, d in faces])
