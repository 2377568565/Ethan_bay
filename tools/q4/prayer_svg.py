# 《祷告为什么常常没有应验？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：上帝回答祷告的几种样子 ----------------
def answers():
    W, H = 400, 330
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="prf1t prf1d">',
           '<title id="prf1t">上帝回答祷告的几种样子</title>',
           '<desc id="prf1d">四个方块：好——照你所求的（哈拿，撒上1:20）；不——我有别的计划（摩西，申3:26）；'
           '等一等——时候未到（但以理二十一日，但10:12-13）；更好的——不同于你所求的（保罗的刺，林后12:9）。'
           '中间写着：没有看见所求的那件事，不等于上帝没有回答。编者整理，不是圣经的分类。</desc>']
    boxes = [(14, 30, 'f4', '好', '照你所求的', '哈拿：撒上1:20'),
             (206, 30, 'f3', '不', '我有别的计划', '摩西：申3:26'),
             (14, 160, 'f1', '等一等', '时候还没有到', '但以理：但10:12-13'),
             (206, 160, 'f6', '更好的', '不同于你所求的', '保罗：林后12:9')]
    for x, y, c, a, b, r in boxes:
        out.append(f'<rect x="{x}" y="{y}" width="180" height="110" rx="12" class="{c} fillc"/>')
        out.append(text(x + 90, y + 34, a, 'tn hi', 'middle'))
        out.append(text(x + 90, y + 62, b, 'tnode2', 'middle'))
        out.append(text(x + 90, y + 88, r, 'tnode2', 'middle'))
    out.append(text(W / 2, 18, '祷告的回答', 'tn hi', 'middle'))
    out.append(text(W / 2, 296, '没有看见所求的那件事，不等于上帝没有回答', 'ts', 'middle'))
    out.append(text(W / 2, 318, '（编者整理，不是圣经里的分类）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：客西马尼园的祷告怎样“蒙了应允” ----------------
def geth():
    W, H = 400, 400
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="prf2t prf2d">',
           '<title id="prf2t">客西马尼园的祷告怎样“蒙了应允”</title>',
           '<desc id="prf2d">从上到下五步：一、三次求“叫这杯离开我”（太26:39、42、44）；二、“只要照你的意思”；'
           '三、天使显现，加添祂的力量（路22:43）；四、十字架：“成了”（约19:30）；五、第三天复活：'
           '“就因他的虔诚蒙了应允”（来5:7）。</desc>']
    rows = [('f3', '三次求：“叫这杯离开我”', '太26:39、42、44'),
            ('f1', '“只要照你的意思”', '太26:39；路22:42'),
            ('f6', '天使显现，加添祂的力量', '路22:43'),
            ('f4', '十字架：“成了”', '约19:30'),
            ('f4', '第三天复活：“蒙了应允”', '来5:7')]
    for i, (c, a, r) in enumerate(rows):
        y = 12 + i * 78
        out.append(f'<rect x="40" y="{y}" width="320" height="56" rx="12" class="{c} fillc"/>')
        out.append(text(200, y + 24, a, 'tnode2', 'middle'))
        out.append(text(200, y + 44, r, 'tnode2', 'middle'))
        if i < 4:
            out.append(f'<path d="M200 {y + 56} L200 {y + 78}" class="flow"/>')
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：但以理的二十一日 ----------------
def wait():
    W, H = 400, 230
    X0, X1 = 30, 370
    def x(d):
        return X0 + (d - 1) * (X1 - X0) / 20
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="prf3t prf3d">',
           '<title id="prf3t">但以理的二十一日</title>',
           '<desc id="prf3d">一条从第1日到第21日的时间线。第1日：但以理的言语已蒙应允，天使出发。'
           '中间二十一日：波斯国的魔君拦阻，米迦勒来帮助。第21日以后：天使来到但以理面前。'
           '地上看见的是“没有回应”，天上已经在行动。依据：但10:2-3、12-13。</desc>']
    out.append(text(W / 2, 20, '但以理书10章：地上在等，天上在动', 'tn hi', 'middle'))
    out.append(f'<rect x="{X0}" y="60" width="{X1 - X0}" height="26" rx="6" class="f1 fillc"/>')
    out.append(text(W / 2, 78, '二十一日：波斯国的魔君拦阻', 'tnode2', 'middle'))
    for d, a, b in [(1, '第1日', '已蒙应允'), (21, '第21日', '米迦勒来帮助')]:
        out.append(f'<path d="M{x(d):.1f} 48 L{x(d):.1f} 98" class="ax"/>')
        anc = 'start' if d == 1 else 'end'
        out.append(text(x(d), 44, a, 'ts', anc))
        out.append(text(x(d), 114, b, 'ts', anc))
    out.append(text(W / 2, 150, '地上：三个七日禁食，没有看见回应（但10:2-3）', 'ts', 'middle'))
    out.append(text(W / 2, 174, '天上：“我是因你的言语而来”（但10:12）', 'ts', 'middle'))
    out.append(text(W / 2, 212, '没有看见回应，不等于没有被听见', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
