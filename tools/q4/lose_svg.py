# 《信了主，还会失去救恩吗？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：离开的路，回家的路 ----------------
def road():
    W, H = 400, 360
    away = [('随流失去', '来2:1'), ('思虑钱财挤住了道', '太13:22'), ('离弃起初的爱心', '启2:4'),
            ('被罪迷惑，心刚硬', '来3:13'), ('不信的恶心，离弃上帝', '来3:12')]
    home = [('回想从哪里坠落', '启2:5'), ('醒悟、起来', '路15:17-18'), ('认罪', '约壹1:9'), ('父亲跑去抱他', '路15:20'), ('死而复活，失而又得', '路15:24')]
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="lf1t lf1d">',
           '<title id="lf1t">离开的路，回家的路</title>',
           '<desc id="lf1d">左边是圣经描写的人怎样渐渐离开上帝：随流失去；世上的思虑和钱财的迷惑把道挤住；离弃起初的爱心；被罪迷惑，心里刚硬；最后存着不信的恶心，离弃永生上帝。右边是回家的路：回想是从哪里坠落的；像浪子一样醒悟起来；认罪；父亲远远看见就跑去抱他；死而复活，失而又得。离开很少是一下子的，回来却随时可以开始。</desc>']
    out.append(text(100, 22, '离开的路（渐渐的）', 'tn hi', 'middle'))
    out.append(text(300, 22, '回家的路（随时可以开始）', 'tn hi', 'middle'))
    for i, (t, r) in enumerate(away):
        y = 40 + i * 60
        out.append(f'<rect x="10" y="{y}" width="180" height="46" rx="10" class="f4 fillc"/>')
        out.append(text(100, y + 21, t, 'tnode2', 'middle'))
        out.append(text(100, y + 37, r, 'tnode2', 'middle'))
        if i < len(away) - 1:
            out.append(f'<path d="M100 {y + 46} L100 {y + 60}" class="flow"/>')
    for i, (t, r) in enumerate(home):
        y = 280 - i * 60
        out.append(f'<rect x="210" y="{y}" width="180" height="46" rx="10" class="f6 fillc"/>')
        out.append(text(300, y + 21, t, 'tnode2', 'middle'))
        out.append(text(300, y + 37, r, 'tnode2', 'middle'))
        if i < len(home) - 1:
            out.append(f'<path d="M300 {y} L300 {y - 14}" class="flow"/>')
    out.append('<path d="M190 303 L210 303" class="flow"/>')
    out.append(text(200, 352, '“你们转回，转回吧！……何必死亡呢？”（结33:11）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
