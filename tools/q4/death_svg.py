# 《根据圣经，人死了去哪里？》页面里的两张图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


def _box(x, y, w, h, fam, t1, t2=''):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="{fam} fillc"/>']
    if t2:
        out.append(text(x + w / 2, y + h / 2 - 3, t1, 'tnode', 'middle'))
        out.append(text(x + w / 2, y + h / 2 + 14, t2, 'tnode2', 'middle'))
    else:
        out.append(text(x + w / 2, y + h / 2 + 5, t1, 'tnode', 'middle'))
    return out


# ---------------- 图 1：尘土 + 生气 = 有灵的活人；死亡倒过来 ----------------
def made():
    W, H = 400, 300
    bw, bh = 104, 52
    xs = [10, 148, 286]
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="df1t df1d">',
           '<title id="df1t">人是怎样造的，死的时候发生了什么</title>',
           '<desc id="df1d">第一行：尘土加上上帝吹进鼻孔的生气，成了有灵的活人（创世记2章7节）。第二行：死的时候倒过来，尘土归于地，气息归于上帝，活人就不再存在（传道书12章7节）。第三行：复活的时候，上帝再赐生命，人又成为活人。</desc>']
    rows = [(18, '造人', '创2:7', [('f2', '尘土', '身体的材料'), ('f1', '生气', '上帝吹进鼻孔'), ('f6', '有灵的活人', '活的生命体')], ['＋', '＝']),
            (118, '死亡', '传12:7', [('f6', '活人', '不再存在'), ('f2', '尘土归地', '身体朽坏'), ('f1', '气归上帝', '不是有知觉的“我”')], ['→', '＋']),
            (218, '复活', '林前15:52', [('f2', '上帝记得', '每一个人'), ('f1', '再赐生命', '号筒吹响的时候'), ('f6', '复活的人', '穿上不朽坏')], ['＋', '＝'])]
    for y, lab, ref, boxes, ops in rows:
        out.append(text(10, y - 4, lab, 'tn'))
        out.append(text(W - 10, y - 4, ref, 'ts', 'end'))
        for (fam, t1, t2), x in zip(boxes, xs):
            out += _box(x, y + 4, bw, bh, fam, t1, t2)
        for op, x in zip(ops, [xs[0] + bw + 17, xs[1] + bw + 17]):
            out.append(text(x, y + 4 + bh / 2 + 7, op, 'dop', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 2：从死到复活的时间线 ----------------
def timeline():
    W, H = 400, 214
    y = 92
    pts = [(22, '断气', '“睡了”（约11:11）', 'f0'), (150, '主再来', '义人复活（帖前4:16）', 'f6'),
           (268, '一千年后', '其余的死人复活（启20:5）', 'f2'), (378, '新天新地', '不再有死亡（启21:4）', 'f1')]
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="df2t df2d">',
           '<title id="df2t">从死到复活</title>',
           '<desc id="df2d">时间线：人断气以后在坟墓里安睡，毫无所知；主再来的时候，在基督里死了的人先复活，和活着的信徒一同被提，与主永远同在；一千年后，其余的死人复活受审判，第二次的死；最后是新天新地，不再有死亡。对睡了的人来说，从断气到复活只像一眨眼。</desc>']
    # 安睡的一段（虚线）和之后的实线
    out.append(f'<path d="M{pts[0][0]} {y} L{pts[1][0]} {y}" class="cn f0 dash"/>')
    out.append(f'<path d="M{pts[1][0]} {y} L{pts[3][0]} {y}" class="ln f6"/>')
    # 安睡段上方的说明
    mid = (pts[0][0] + pts[1][0]) / 2
    out.append(f'<path d="M{pts[0][0] + 6} {y - 30} Q{mid} {y - 62} {pts[1][0] - 6} {y - 30}" class="flow"/>')
    out.append(text(mid, y - 64, '对睡了的人：只像一眨眼', 'tn', 'middle'))
    out.append(text(mid, y - 14, '在坟墓里安睡，毫无所知', 'tw', 'middle'))
    out.append(text(mid, y + 24, '传9:5；诗146:4', 'ts', 'middle'))
    # 千年段说明
    out.append(text((pts[1][0] + pts[2][0]) / 2, y - 14, '一千年', 'tw', 'middle'))
    out.append(text((pts[1][0] + pts[2][0]) / 2, y + 24, '启20:4-6', 'ts', 'middle'))
    for i, (x, t1, t2, fam) in enumerate(pts):
        out.append(f'<circle cx="{x}" cy="{y}" r="{7 if i in (1, 3) else 5.5}" class="dot"/>')
        anchor = 'start' if i == 0 else ('end' if i == 3 else 'middle')
        dy = 52 if i % 2 == 0 else 74
        out.append(text(x, y + dy, t1, 'tn', anchor))
        out.append(text(x, y + dy + 15, t2, 'ts', anchor))
    out.append(text(pts[1][0] + 8, y + 108, '活着的信徒一同被提，与主永远同在（帖前4:17）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
