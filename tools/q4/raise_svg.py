# 《打骂孩子，还是由着孩子？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：四种教养方式 ----------------
def four():
    W, H = 400, 330
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="rsf1t rsf1d">',
           '<title id="rsf1t">四种教养方式</title>',
           '<desc id="rsf1d">横轴是要求和规矩（少到多），纵轴是温暖和回应（少到多）。'
           '右上：权威型（温暖多、规矩多）；左上：放任型（温暖多、规矩少）；右下：专制型（温暖少、规矩多）；左下：忽视型（都少）。'
           '来源：鲍姆林德的分类，后人加了第四种。</desc>']
    X0, Y0, S = 60, 20, 150
    cells = [(0, 0, 'f3', '放任型', '温暖多，规矩少'), (1, 0, 'f1', '权威型', '温暖 + 规矩'),
             (0, 1, 'f6', '忽视型', '都少'), (1, 1, 'f4', '专制型', '规矩多，温暖少')]
    for cx, cy, c, t, d in cells:
        x, y = X0 + cx * (S + 8), Y0 + cy * (S - 30 + 8)
        out.append(f'<rect x="{x}" y="{y}" width="{S}" height="{S - 30}" rx="12" class="{c} fillc"/>')
        out.append(text(x + S / 2, y + 54, t, 'tnode2', 'middle'))
        out.append(text(x + S / 2, y + 76, d, 'tnode2', 'middle'))
    yb = Y0 + 2 * (S - 30) + 8
    out.append(f'<path d="M{X0} {yb + 12} L{X0 + 2 * S + 8} {yb + 12}" class="flow"/>')
    out.append(text(X0 + S + 4, yb + 32, '要求和规矩：少 → 多', 'ts', 'middle'))
    out.append(f'<path d="M{X0 - 12} {yb} L{X0 - 12} {Y0}" class="flow"/>')
    out.append(text(X0 - 20, Y0 + 14, '多', 'ts', 'end'))
    out.append(text(X0 - 20, yb - 4, '少', 'ts', 'end'))
    out.append(text(X0 - 20, Y0 + S - 30, '温暖', 'ts', 'end'))
    out.append(text(X0 - 20, Y0 + S - 12, '回应', 'ts', 'end'))
    out.append(text(W / 2, H - 6, '鲍姆林德的分类（后人加了“忽视型”）；也有学者批评它太笼统', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
