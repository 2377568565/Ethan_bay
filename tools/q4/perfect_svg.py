# 《要“完全”才能见主吗？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：圣经里“完全”的三个时态 ----------------
def tenses():
    W, H = 400, 270
    cols = [('已经', '在基督里的完全', ['“一次献祭，便叫', '……永远完全”', '来10:14；西2:10'], 'f2'),
            ('正在', '成长中的完全', ['“我乃是', '竭力追求”', '腓3:12-15；林后3:18'], 'f6'),
            ('将要', '主来时的完全', ['“我们也要改变……', '必要像他”', '林前15:52；约壹3:2'], 'f1')]
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="pf1t pf1d">',
           '<title id="pf1t">圣经里“完全”的三个时态</title>',
           '<desc id="pf1d">圣经说的“完全”有三个时态：已经——在基督里，因祂一次献祭，信徒在上帝面前永远完全（希伯来书10章14节）；正在——在生活中竭力追求、荣上加荣地长进（腓立比书3章12至15节）；将要——主来的时候，我们要改变，必要像祂（哥林多前书15章52节、约翰一书3章2节）。</desc>']
    out.append('<path d="M20 60 L380 60" class="ln f0"/>')
    for i, (t, h, lines, fam) in enumerate(cols):
        x = 20 + i * 127
        cx = x + 56
        out.append(f'<circle cx="{cx}" cy="60" r="22" class="{fam} fillc"/>')
        out.append(text(cx, 66, t, 'tnode', 'middle'))
        out.append(f'<rect x="{x}" y="96" width="112" height="140" rx="12" class="box"/>')
        out.append(f'<rect x="{x}" y="96" width="112" height="6" rx="3" class="{fam} fillc"/>')
        out.append(text(cx, 128, h, 'tn hi', 'middle'))
        for k, ln in enumerate(lines[:2]):
            out.append(text(cx, 160 + k * 18, ln, 'ts', 'middle'))
        out.append(text(cx, 220, lines[2], 'ts', 'middle'))
    out.append(text(200, 258, '三个时态都来自同一位基督（腓1:6）', 'tn', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
