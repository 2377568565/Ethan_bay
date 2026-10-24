# 《抽烟、喝酒、吃什么，和信仰有关系吗？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：生活方式和寿命 ----------------
def years():
    W = 400
    rows = [('加州复临信徒男性', 7.28, 'f1', '+7.3 年'), ('加州复临信徒女性', 4.42, 'f1', '+4.4 年'),
            ('一直吸烟的男医生', -10, 'f6', '约 −10 年')]
    Z, S, TOP, RH = 230, 14, 34, 42
    H = TOP + len(rows) * RH + 40
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="hlf1t hlf1d">',
           '<title id="hlf1t">生活方式和寿命</title>',
           '<desc id="hlf1d">和对照人群相比的预期寿命差别：加州复临信徒男性多约7.3年，女性多约4.4年（30岁时的预期寿命，2001年研究）；'
           '1900至1930年出生、一直吸烟的英国男医生，比终生不吸烟的人平均早死约10年。</desc>']
    out.append(text(W / 2, 16, '和对照人群相比，预期寿命多（少）几年', 'tn hi', 'middle'))
    out.append(f'<path d="M{Z} {TOP - 4} L{Z} {TOP + len(rows) * RH}" class="ax"/>')
    for i, (lab, v, c, t) in enumerate(rows):
        y = TOP + i * RH
        w = abs(v) * S
        x = Z if v > 0 else Z - w
        out.append(f'<rect x="{x:.1f}" y="{y + 8}" width="{w:.1f}" height="22" rx="4" class="{c} fillc"/>')
        if v > 0:
            out.append(text(Z - 6, y + 24, lab, 'tn', 'end'))
            out.append(text(Z + w + 6, y + 24, t, 'ts'))
        else:
            out.append(text(Z + 6, y + 24, lab, 'tn'))
            out.append(text(x - 6, y + 24, t, 'ts', 'end'))
    out.append(text(W / 2, H - 20, '复临信徒：Fraser 2001（30岁时预期寿命）；吸烟：Doll 2004（英国医生50年）', 'tw', 'middle'))
    out.append(text(W / 2, H - 7, '研究说明的是关联；原因包括饮食、不吸烟、运动、休息、社会支持等', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
