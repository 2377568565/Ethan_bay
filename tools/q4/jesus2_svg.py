# 《耶稣是人还是神？》补充问答页的两张图（SVG，样式用 history.py 的 CSS 和颜色）
import math
from history_svg import text


# ---------------- 图 1：三架天平（我们生来、耶稣、重生以后） ----------------
def scale():
    W, H = 400, 372
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="js1t js1d">',
           '<title id="js1t">三架天平</title>',
           '<desc id="js1d">每个人都有一架天平，一边是上帝，一边是自己。我们的天平生来就向“自己”一边倾斜；耶稣的天平生来是平的，撒但在“自己”一边压上最重的试探，它也没有倒过去；重生以后，圣灵把我们的天平交在父手中，一点一点扶正。</desc>']
    rows = [
        (14, '我们：生来就倾斜', ['诗51:5：“我是在罪孽里生的”', '再加上自己一次次往那边放砝码', '（遗传的倾向＋养成的倾向）'], 'f3', 13, None),
        (134, '耶稣：生来是平的', ['路1:35：“所要生的圣者”', '撒但压上最重的试探：饥饿、死亡、', '被父离弃——天平一次也没有倒过去'], 'f6', 0, '试探'),
        (254, '重生以后：正在被扶正', ['结36:26：“我也要赐给你们一个新心”', '圣灵“胜过一切遗传的和养成的作恶倾向”', '主再来时完全扶正（约一3:2）'], 'f5', 6, None),
    ]
    for y, title, lines, fam, deg, weight in rows:
        cx, cy, half = 82, y + 30, 58
        a = math.radians(deg)
        lx, ly = cx - half * math.cos(a), cy - half * math.sin(a)
        rx, ry = cx + half * math.cos(a), cy + half * math.sin(a)
        out.append(f'<rect x="6" y="{y - 6}" width="{W - 12}" height="112" rx="14" class="box"/>')
        out.append(f'<path d="M{cx} {cy} L{cx} {y + 88}" class="sbeam"/>')
        out.append(f'<path d="M{cx - 20} {y + 92} L{cx + 20} {y + 92}" class="sbeam"/>')
        out.append(f'<path d="M{lx:.1f} {ly:.1f} L{rx:.1f} {ry:.1f}" class="sbeam {fam}"/>')
        out.append(f'<circle cx="{cx}" cy="{cy}" r="4" class="spiv"/>')
        for px, py, lab in ((lx, ly, '上帝'), (rx, ry, '自己')):
            out.append(f'<path d="M{px:.1f} {py:.1f} L{px:.1f} {py + 22:.1f}" class="sline"/>')
            out.append(f'<path d="M{px - 18:.1f} {py + 22:.1f} Q{px:.1f} {py + 36:.1f} {px + 18:.1f} {py + 22:.1f} Z" class="span"/>')
            out.append(text(px, py + 48, lab, 'ts', 'middle'))
        if weight:
            out.append(f'<rect x="{rx - 11:.1f}" y="{ry + 6:.1f}" width="22" height="16" rx="3" class="sw"/>')
            out.append(f'<path d="M{rx:.1f} {y - 2} L{rx:.1f} {ry - 4:.1f}" class="sarr"/>')
            out.append(text(rx - 6, y + 12, weight, 'ts', 'end'))
        tx = 168
        out.append(text(tx, y + 18, title, 'tn'))
        for i, s in enumerate(lines):
            out.append(text(tx, y + 40 + i * 17, s, 'ts'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 2：两条路线（耶稣从终点开始，我们由祂领着走到终点） ----------------
def path():
    W, H = 400, 404
    L, R, w, h = 8, 212, 180, 58
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="js2t js2d">',
           '<title id="js2t">两条路线</title>',
           '<desc id="js2d">耶稣：从圣灵成孕，一生无罪、倚靠父，复活成为初熟的果子。我们：从肉身生，带着倾向；从灵重生，罪疚赦免、得新心；一生成圣，倾向一天天被治死；复活改变，必要像祂。两条路线由同一位圣灵连起来。</desc>']

    def vstack(x, y, s):            # 两列之间很窄：中文竖排，一行一个字
        for i, ch in enumerate(s):
            out.append(text(x, y + 12 + i * 13, ch, 'tw halo', 'middle'))

    def head(x, label, fam):
        out.append(f'<rect x="{x}" y="6" width="{w}" height="30" rx="15" class="{fam} fillc"/>')
        out.append(text(x + w / 2, 26, label, 'tnode', 'middle'))

    def box(x, y, a, b, c=''):
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" class="box"/>')
        out.append(text(x + 12, y + 21, a, 'tn'))
        out.append(text(x + 12, y + 38, b, 'ts'))
        if c:
            out.append(text(x + 12, y + 52, c, 'ts'))

    head(L, '耶稣', 'f6')
    head(R, '我们', 'f5')
    ys = [48, 134, 220, 306]
    # 我们的四步
    us = [('① 从肉身生', '带着向罪的倾向', '诗51:5；弗2:3'), ('② 从灵重生', '罪疚赦免，得着新心', '徒2:38；结36:26'),
          ('③ 一生成圣', '倾向一天天被治死', '西3:5；林后4:16'), ('④ 复活改变', '倾向除尽，“必要像他”', '林前15:52；约一3:2')]
    for (a, b, c), y in zip(us, ys):
        box(R, y, a, b, c)
    for y in ys[:-1]:
        out.append(f'<path d="M{R + w / 2} {y + h} L{R + w / 2} {y + 86}" class="flow"/>')
    # 耶稣的三步（起点对着我们的“重生”，终点对着我们的“复活”）
    jy = [ys[0], ys[1] + 43, ys[3]]
    js = [('从圣灵成孕', '“所要生的圣者”', '路1:35'), ('一生无罪，倚靠父', '受试探与我们一样，', '只是没有犯罪（来4:15）'),
          ('从死里复活', '“睡了之人初熟的果子”', '林前15:20')]
    for (a, b, c), y in zip(js, jy):
        box(L, y, a, b, c)
    out.append(f'<path d="M{L + w / 2} {jy[0] + h} L{L + w / 2} {jy[1]}" class="flow"/>')
    out.append(f'<path d="M{L + w / 2} {jy[1] + h} L{L + w / 2} {jy[2]}" class="flow"/>')
    # 同一位圣灵：耶稣的起点 → 我们的重生
    out.append(f'<path d="M{L + w} {jy[0] + h / 2} C{L + w + 14} {jy[0] + h / 2} {R - 14} {ys[1] + h / 2} {R} {ys[1] + h / 2}" class="jdash2"/>')
    vstack(200, jy[0] + h + 2, '同一位圣灵')
    # 终点相同
    out.append(f'<path d="M{L + w} {jy[2] + h / 2} L{R} {ys[3] + h / 2}" class="jdash2"/>')
    vstack(200, ys[3] + 8, '像祂')
    out.append(text(W / 2, H - 14, '耶稣从终点的样子开始；我们从起点出发，由祂领着走到终点', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
