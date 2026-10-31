# 用 listen.py 做模板，生成新专题的 X.py。用法：python3 newtopic.py spec.json
import json, os, sys
S = json.load(open(sys.argv[1]))
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'listen.py')).read()
R = [
 ('"""生成《家人总在念叨，我为什么越听越烦？》专题网页（仓库根目录 listen.html，问题彩蛋 15）。', f'"""生成《{S["title"]}》专题网页（仓库根目录 {S["slug"]}.html，问题彩蛋 {S["no"]}）。'),
 ('正文在 listen_text.py，图在 listen_svg.py', f'正文在 {S["slug"]}_text.py，图在 {S["slug"]}_svg.py'),
 ('python3 tools/q4/listen.py', f'python3 tools/q4/{S["slug"]}.py'),
 ('import listen_text as T, listen_svg as G', f'import {S["slug"]}_text as T, {S["slug"]}_svg as G'),
 ("'listen.html')", f"'{S['slug']}.html')"),
 ("TITLE = '家人总在念叨，我为什么越听越烦？'", f"TITLE = '{S['title']}'"),
 ("PDF = '研经问答15-家人总在念叨我为什么越听越烦.pdf'", f"PDF = '{S['pdf']}'"),
 ("FIGS = {'spiral': G.spiral}", "FIGS = {" + ', '.join(f"'{f}': G.{f}" for f in S['figs']) + "}"),
 ('<p class="eyebrow">问题彩蛋 · 15 · 家人之间</p>', f'<p class="eyebrow">问题彩蛋 · {S["no"]} · {S["eyebrow"]}</p>'),
 ('<small class="h1s">怎样不指责、不躲开，把安慰说进对方心里</small>', f'<small class="h1s">{S["h1s"]}</small>'),
 ("id='qa16', title=TITLE, page='listen.html'", f"id='{S['id']}', title=TITLE, page='{S['slug']}.html'"),
 ('点{ref("cycle")}之类的蓝色字', '点{ref("' + S['refdemo'] + '")}之类的蓝色字'),
]
for a, b in R:
    assert a in src, a
    src = src.replace(a, b)
def swap(s, start, end, new, inc=True):
    i = s.index(start); j = s.index(end, i) + (len(end) if inc else 0)
    return s[:i] + new + s[j:]
src = swap(src, '<p class="hsub">', '</p>', f'<p class="hsub">{S["hsub"]}</p>')
src = swap(src, '<p>下面先说烦躁和', '</p></div>', f'<p>{S["intro"]}', inc=False)
src = swap(src, '<p>本页的依据是圣经', '</p>', f'<p>{S["srcs"]}</p>')
src = swap(src, "return H.doc(TITLE, '", "', main, srcs", f"return H.doc(TITLE, '{S['desc']}", inc=False)
src = src.replace("return H.doc(TITLE, '" + S['desc'] + "', main", "return H.doc(TITLE, '" + S['desc'] + "', main")
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), S['slug'] + '.py'), 'w').write(src)
print('ok', S['slug'])
