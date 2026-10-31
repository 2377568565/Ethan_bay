# 《算命、风水、星座、看日子，到底灵不灵？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：两种面对未来的方式 ----------------
def two():
    W, H = 400, 300
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="ftf1t ftf1d">',
           '<title id="ftf1t">两种面对未来的方式</title>',
           '<desc id="ftf1d">左边是“算”的路：对未来不安，去算命、看日子，听到吉就放心一阵、听到凶就更害怕，于是再去算。'
           '右边是“信”的路：对未来不安，向上帝祷告交托（诗31:15），照常尽本分、作计划（雅4:15），心里有平安（腓4:7）。</desc>']
    out.append(text(100, 22, '“算”的路', 'tn hi', 'middle'))
    out.append(text(300, 22, '“信”的路', 'tn hi', 'middle'))
    left = [('f6', '对未来不安'), ('f6', '去算、去看日子'), ('f6', '吉：放心一阵'), ('f6', '凶：更加害怕')]
    right = [('f1', '对未来不安'), ('f1', '祷告，交托（诗31:15）'), ('f1', '尽本分，作计划（雅4:15）'), ('f1', '出人意外的平安（腓4:7）')]
    for col, (x, items) in enumerate(((20, left), (220, right))):
        for i, (c, t) in enumerate(items):
            y = 40 + i * 58
            out.append(f'<rect x="{x}" y="{y}" width="160" height="40" rx="10" class="{c} fillc"/>')
            out.append(text(x + 80, y + 25, t, 'tnode2', 'middle'))
            if i < len(items) - 1:
                out.append(f'<path d="M{x + 80} {y + 40} L{x + 80} {y + 58}" class="flow"/>')
    out.append('<path d="M20 254 C0 254 0 60 20 60" class="flow"/>')
    out.append(text(100, 284, '再去算……一直不安', 'ts', 'middle'))
    out.append(text(300, 284, '“我终身的事在你手中”', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
