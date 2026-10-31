# 《婚姻是爱情的坟墓吗？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：越靠近上帝，彼此越靠近 ----------------
def rope():
    W, H = 400, 320
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="mrf1t mrf1d">',
           '<title id="mrf1t">越靠近上帝，彼此越靠近</title>',
           '<desc id="mrf1d">一个三角形：顶点是上帝，底边两端是丈夫和妻子。两人沿着两条边往上走，越靠近上帝，彼此之间的距离也越近。'
           '下面写着：三股合成的绳子不容易折断（传4:12）。这是编者用来帮助理解的图。</desc>']
    out.append('<path d="M200 40 L50 250 L350 250 Z" class="flow"/>')
    out.append('<circle cx="200" cy="40" r="24" class="f4 fillc"/>')
    out.append(text(200, 45, '上帝', 'tnode2', 'middle'))
    for y, c in ((250, 'f1'), (180, 'f1'), (110, 'f1')):
        dx = (y - 40) * 150 / 210
        out.append(f'<circle cx="{200 - dx:.1f}" cy="{y}" r="9" class="{c} fillc"/>')
        out.append(f'<circle cx="{200 + dx:.1f}" cy="{y}" r="9" class="f3 fillc"/>')
        out.append(f'<path d="M{200 - dx + 12:.1f} {y} L{200 + dx - 12:.1f} {y}" class="flow" stroke-dasharray="4 4"/>')
    out.append(text(50, 276, '丈夫', 'tn', 'middle'))
    out.append(text(350, 276, '妻子', 'tn', 'middle'))
    out.append(text(200, 300, '越靠近上帝，彼此越靠近（编者的图解）；“三股合成的绳子不容易折断”', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
