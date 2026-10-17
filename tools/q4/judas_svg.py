# 《犹大是注定要卖主的吗？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：耶稣挽回犹大的历程 ----------------
def rescue():
    W = 400
    rows = [('拣选', '整夜祷告后，列在十二人中', '路6:12-16'),
            ('差遣', '同样的权柄：传道、医病、赶鬼', '太10:1-8'),
            ('托付', '把钱囊交给他', '约12:6；13:29'),
            ('警告', '“你们中间有一个是魔鬼”（不点名）', '约6:70'),
            ('伯大尼', '只说“由她吧”，不揭穿', '约12:7'),
            ('洗脚', '跪下来洗他的脚', '约13:5、11'),
            ('明说', '“是我吗？”——“你说的是”', '太26:25'),
            ('递饼', '亲手蘸饼递给他', '约13:26'),
            ('园中', '“朋友”；“犹大！”', '太26:50；路22:48')]
    H = 30 + len(rows) * 44 + 30
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="jdf1t jdf1d">',
           '<title id="jdf1t">耶稣挽回犹大的历程</title>',
           '<desc id="jdf1d">从上到下九步：拣选（路6:12-16）；差遣，同样的权柄（太10:1-8）；托付钱囊（约12:6；13:29）；'
           '不点名的警告（约6:70）；伯大尼只说“由她吧”（约12:7）；洗他的脚（约13:5、11）；犹大问“拉比，是我吗？”耶稣说“你说的是”（太26:25）；'
           '亲手递饼（约13:26）；园中叫他“朋友”、叫他的名字（太26:50；路22:48）。</desc>']
    out.append(f'<path d="M58 30 L58 {30 + (len(rows) - 1) * 44}" class="ax"/>')
    for i, (a, b, r) in enumerate(rows):
        y = 30 + i * 44
        c = 'f4' if i == len(rows) - 1 else 'f1'
        out.append(f'<circle cx="58" cy="{y}" r="7" class="{c} fillc"/>')
        out.append(text(44, y + 5, a, 'tn hi', 'end'))
        out.append(text(74, y + 1, b, 'ts'))
        out.append(text(74, y + 19, r, 'tw'))
    out.append(text(W / 2, H - 8, '“凡能拯救犹大的，没有一样没有做”（《历代愿望》655）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：犹大的下坡路 ----------------
def down():
    W, H = 400, 360
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="jdf2t jdf2d">',
           '<title id="jdf2t">犹大的下坡路</title>',
           '<desc id="jdf2d">像台阶一样往下走的七步：爱钱（约12:6）；从钱囊里偷拿小钱；约翰福音6章以后，留着“随时退出”的心；'
           '批评、挑起谁为大的争论；伯大尼被温和责备，怀恨（太26:14）；去见祭司长：“你们愿意给我多少钱？”（太26:15）；'
           '拒绝洗脚时的感动，出去，“那时候是夜间了”（约13:30）。依据经文和怀爱伦《历代愿望》第76章的描写。</desc>']
    steps = ['爱钱', '偷拿钱囊里的小钱', '约6章后：留着退路', '批评、争谁为大', '被责备，怀恨在心', '“你们愿意给我多少钱？”', '压下感动，出去：是夜间']
    for i, s in enumerate(steps):
        x = 14 + i * 22
        y = 16 + i * 44
        c = 'f6' if i >= 5 else ('f3' if i >= 3 else 'f1')
        out.append(f'<rect x="{x}" y="{y}" width="230" height="34" rx="8" class="{c} fillc"/>')
        out.append(text(x + 115, y + 22, s, 'tnode2', 'middle'))
    out.append(text(W / 2, H - 10, '依据：约12:6；太26:14-15；约13:30；《历代愿望》716—720', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：彼得与犹大 ----------------
def two():
    W, H = 400, 340
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="jdf3t jdf3d">',
           '<title id="jdf3t">彼得与犹大：同一夜，两个结局</title>',
           '<desc id="jdf3d">左边彼得：三次不认主；主转过身来看他；出去痛哭；回到门徒中间；三次“你爱我吗？”，被托付牧养（约21:15-17）。'
           '右边犹大：用亲嘴的暗号卖主；后悔，把钱退给祭司长；“那与我们有什么相干？”；出去吊死了；“往自己的地方去了”（徒1:25）。'
           '中间写着：差别不在罪的大小，而在往哪里去。</desc>']
    cols = [(14, 'f4', '彼得', ['三次不认主', '主转过身来看他', '出去痛哭', '回到门徒中间', '“你爱我吗？”×3'], '路22:61-62；约21章'),
            (206, 'f6', '犹大', ['用亲嘴卖主', '后悔，退钱', '去找祭司长', '出去吊死了', '“往自己的地方去了”'], '太27:3-5；徒1:25')]
    for x, c, a, rows, r in cols:
        out.append(f'<rect x="{x}" y="14" width="180" height="270" rx="12" class="{c} fillc"/>')
        out.append(text(x + 90, 44, a, 'tn hi', 'middle'))
        for i, s in enumerate(rows):
            out.append(text(x + 90, 82 + i * 34, s, 'tnode2', 'middle'))
        out.append(text(x + 90, 266, r, 'tnode2', 'middle'))
    out.append(text(W / 2, 312, '差别不在罪的大小，而在往哪里去', 'ts', 'middle'))
    out.append(text(W / 2, 332, '（编者整理）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
