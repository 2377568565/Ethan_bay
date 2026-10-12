# 《“我必快来”，为什么还没来？》页面里的两张图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图 1：按圣经年岁推算的时间线（创造纪年） ----------------
def chrono():
    W, H = 400, 300
    x0, x1 = 20, 380
    am = 6000

    def X(a):
        return x0 + (x1 - x0) * a / am
    pts = [(0, '创造', '亚当', 'f0'), (1656, '洪水', '创7:6', 'f4'), (2008, '亚伯兰', '约2008', 'f2'),
           (2513, '出埃及', '约2513', 'f2'), (2993, '建殿', '约2993', 'f3'), (3955, '耶稣降生', '约3955', 'f6'), (5980, '今天', '约5980', 'f1')]
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="sf1t sf1d">',
           '<title id="sf1t">按圣经年岁推算的时间线</title>',
           '<desc id="sf1d">以亚当被造为第0年（创造纪年），按创世记5章、11章的年岁，洪水在1656年；采用“他拉130岁生亚伯兰、430年从亚伯拉罕蒙召算起”的一种算法，亚伯兰约生于2008年，出埃及约2513年，所罗门建殿约2993年；之后要用历史年代换算，耶稣降生约在3955年前后，到今天约5980年。不同算法得出的总数在约5900到6200年之间。</desc>']
    for k in range(0, 6001, 1000):
        out.append(f'<path d="M{X(k):.1f} 150 L{X(k):.1f} 156" class="ax"/>')
        out.append(text(X(k), 170, str(k), 'ta', 'middle'))
    out.append(text(200, 188, '创造纪年（从亚当被造算起的年数，一种算法）', 'ts', 'middle'))
    out.append(f'<path d="M{X(0):.1f} 150 L{X(2993):.1f} 150" class="ln f2"/>')
    out.append(f'<path d="M{X(2993):.1f} 150 L{X(5980):.1f} 150" class="ln f6 dash"/>')
    for i, (a, t1, t2, fam) in enumerate(pts):
        x = X(a)
        up = i % 2 == 0
        y = 150
        out.append(f'<circle cx="{x:.1f}" cy="{y}" r="5" class="dot"/>')
        ty = 108 if up else 60
        out.append(f'<path d="M{x:.1f} {y - 6} L{x:.1f} {ty + 8}" class="ldr"/>')
        anchor = 'start' if i == 0 else ('end' if i == len(pts) - 1 else 'middle')
        out.append(text(x, ty - 12, t1, 'tn', anchor))
        out.append(text(x, ty + 2, t2, 'ts', anchor))
    out.append(text(20, 218, '实线：圣经直接给出的年岁相加', 'tw'))
    out.append(text(20, 236, '虚线：建殿以后要借历史年代换算（所罗门约在公元前十世纪）', 'tw'))
    out.append(text(20, 262, '不同算法：约 5,900—6,200 年（见下表）', 'tn'))
    out.append(text(20, 282, '耶稣说：“那日子，那时辰，没有人知道。”（太24:36）', 'tw'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 2：还在等待圣经翻译开始的语言 ----------------
def langs():
    data = [('1999', 5000, '5,000 多种'), ('2020', 2000, '2,000 多种'), ('2024', 985, '985 种'), ('2025', 544, '544 种')]
    W, H = 400, 250
    bx, bw = 70, 300
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="sf2t sf2d">',
           '<title id="sf2t">还在等待圣经翻译开始的语言数</title>',
           '<desc id="sf2d">据威克理夫全球联会的统计：1999年还有5000多种语言在等待圣经翻译开始；2020年还有2000多种；2024年还有985种；到2025年8月1日，全世界7396种语言中只剩544种。</desc>']
    out.append(text(10, 18, '还在等待圣经翻译开始的语言（全世界共 7,396 种）', 'tn'))
    for i, (yr, v, lab) in enumerate(data):
        y = 38 + i * 46
        w = bw * v / 5000
        out.append(text(10, y + 21, yr, 'tn hi'))
        out.append(f'<rect x="{bx}" y="{y + 4}" width="{w:.1f}" height="26" rx="4" class="f6 fillc"/>')
        if w > 120:
            out.append(text(bx + w - 8, y + 22, lab, 'tnode2', 'end'))
        else:
            out.append(text(bx + w + 8, y + 22, lab, 'tw'))
    out.append(text(10, 232, '资料：威克理夫全球联会，2025年8月1日统计', 'ts'))
    out.append('</svg>')
    return '\n'.join(out)
