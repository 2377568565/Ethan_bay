# 《耶稣是人还是神？》页面里的两张图（SVG，样式用 history.py 的 CSS 和颜色）
from history_svg import esc, text


# ---------------- 图 1：一位，两性（迦克墩信经与四个偏差） ----------------
def chalcedon():
    W, H = 400, 372
    cx, cy, bw, bh = 200, 186, 196, 116
    x0, y0 = cx - bw / 2, cy - bh / 2
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="jf1t jf1d">',
           '<title id="jf1t">一位，两性</title>',
           '<desc id="jf1d">中间是一位耶稣基督，左半是完全的神，右半是完全的人；四边是迦克墩信经的四个界线：不相混、不相变、不分开、不分离。四个角是历史上四种偏差：只把祂当作次等的神（亚流派）、只是看起来像人（幻影说）、分成两个位格（聂斯脱利派）、两性混成一性（欧迪奇派）。</desc>']
    # 四个偏差（四角），先画连线
    errs = [
        (8, 8, '否认“完全的神”', '亚流派（4世纪）', '圣子是被造的，比父低', 'l'),
        (W - 8, 8, '否认“完全的人”', '幻影说（1世纪起）', '只是看起来像人', 'r'),
        (8, H - 74, '把一位分成两位', '聂斯脱利派（5世纪）', '神性和人性像两个人', 'l'),
        (W - 8, H - 74, '把两性混成一性', '欧迪奇派（5世纪）', '人性被神性吞没', 'r'),
    ]
    ew, eh = 150, 66
    for ex, ey, what, who, why, side in errs:
        bx = ex if side == 'l' else ex - ew
        tx = bx + ew / 2
        ty = ey + eh
        tyy = y0 if ey < cy else y0 + bh
        out.append(f'<path d="M{tx:.1f} {ty if ey < cy else ey} L{(x0 + 24 if side == "l" else x0 + bw - 24):.1f} {tyy:.1f}" class="cn f0 dash"/>')
    # 中间：一位，两性
    out.append(f'<rect x="{x0}" y="{y0}" width="{bw / 2}" height="{bh}" rx="14" class="f3 fillc"/>')
    out.append(f'<rect x="{cx}" y="{y0}" width="{bw / 2}" height="{bh}" rx="14" class="f6 fillc"/>')
    out.append(f'<rect x="{cx - 14}" y="{y0}" width="28" height="{bh}" class="f3 fillc"/>')
    out.append(f'<rect x="{cx}" y="{y0}" width="14" height="{bh}" class="f6 fillc"/>')
    out.append(f'<line x1="{cx}" y1="{y0 + 10}" x2="{cx}" y2="{y0 + bh - 10}" class="jsep"/>')
    out.append(text(cx - bw / 4, cy - 14, '完全的神', 'tnode', 'middle'))
    out.append(text(cx - bw / 4, cy + 6, '与父同质', 'tnode2', 'middle'))
    out.append(text(cx - bw / 4, cy + 24, '约1:1；西2:9', 'tnode2', 'middle'))
    out.append(text(cx + bw / 4, cy - 14, '完全的人', 'tnode', 'middle'))
    out.append(text(cx + bw / 4, cy + 6, '与我们同质', 'tnode2', 'middle'))
    out.append(text(cx + bw / 4, cy + 24, '约1:14；来2:17', 'tnode2', 'middle'))
    out.append(f'<rect x="{cx - 58}" y="{y0 - 15}" width="116" height="26" rx="13" class="jone"/>')
    out.append(text(cx, y0 + 3, '一位：耶稣基督', 'tn', 'middle'))
    # 四个界线（贴在中间方块的四边）
    for lx, ly, lab, anc in [(cx, y0 - 22, '', 'middle'), (x0 - 6, cy + 4, '不相混', 'end'), (x0 + bw + 6, cy + 4, '不相变', 'start'),
                             (cx - 44, y0 + bh + 18, '不分开', 'middle'), (cx + 44, y0 + bh + 18, '不分离', 'middle')]:
        if lab:
            out.append(text(lx, ly, lab, 'ty halo', anc))
    for ex, ey, what, who, why, side in errs:
        bx = ex if side == 'l' else ex - ew
        out.append(f'<rect x="{bx}" y="{ey}" width="{ew}" height="{eh}" rx="10" class="box"/>')
        out.append(f'<text x="{bx + 10}" y="{ey + 19}" class="jx">✕</text>')
        out.append(text(bx + 26, ey + 19, what, 'tn'))
        out.append(text(bx + 10, ey + 38, who, 'tw'))
        out.append(text(bx + 10, ey + 55, why, 'ts'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 2：能力从哪里来 ----------------
def power():
    W, H = 400, 404
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="jf2t jf2d">',
           '<title id="jf2t">能力从哪里来</title>',
           '<desc id="jf2d">天父借着圣灵、话语和祷告，把能力赐给作为人的耶稣，祂靠这能力胜过试探，并为别人行神迹；同样的管道也向我们敞开。耶稣自己的神性一直都在，但祂不为自己使用。</desc>']
    # 天父
    out.append(f'<rect x="130" y="8" width="140" height="40" rx="20" class="f4 fillc"/>')
    out.append(text(200, 33, '天父', 'tnode', 'middle'))
    # 三个管道
    chans = [('圣灵', '路4:1、14；徒10:38'), ('话语', '太4:4；赛50:4'), ('祷告', '可1:35；来5:7')]
    for i, (a, b) in enumerate(chans):
        x = 18 + i * 126
        out.append(f'<path d="M200 48 C200 64 {x + 56} 64 {x + 56} 82" class="flow"/>')
        out.append(f'<rect x="{x}" y="82" width="112" height="50" rx="10" class="box"/>')
        out.append(text(x + 56, 103, a, 'tn', 'middle'))
        out.append(text(x + 56, 121, b, 'ts', 'middle'))
    # 两个接受者
    for i, (who, sub, fam, res1, res2) in enumerate([
            ('耶稣（作为人）', '完全倚靠父', 'f6', '胜过一切试探', '为别人行神迹、医病'),
            ('我们', '同样倚靠父', 'f5', '胜过试探（林前10:13）', '结出圣灵的果子')]):
        x = 18 + i * 194
        for j in range(3):
            out.append(f'<path d="M{18 + j * 126 + 56} 132 C{18 + j * 126 + 56} 156 {x + 91} 152 {x + 91} 176" class="flow"/>')
        out.append(f'<rect x="{x}" y="176" width="182" height="52" rx="12" class="{fam} fillc"/>')
        out.append(text(x + 91, 198, who, 'tnode', 'middle'))
        out.append(text(x + 91, 217, sub, 'tnode2', 'middle'))
        out.append(f'<path d="M{x + 91} 228 L{x + 91} 248" class="flow"/>')
        out.append(f'<rect x="{x}" y="248" width="182" height="50" rx="10" class="box"/>')
        out.append(text(x + 91, 269, res1, 'tn', 'middle'))
        out.append(text(x + 91, 287, res2, 'ts', 'middle'))
    # 耶稣自己的神性：一直在，但不为自己用
    out.append(f'<rect x="18" y="314" width="364" height="80" rx="12" class="jdash"/>')
    out.append(text(32, 336, '耶稣自己的神性：一直都在，祂却不拿来帮自己', 'tn'))
    out.append(text(32, 356, '“反倒虚己，取了奴仆的形像”（腓2:7）', 'tw'))
    out.append(text(32, 374, '不把石头变饼（太4:3-4）· 不求十二营天使（太26:53）', 'ts'))
    out.append(text(32, 389, '不从十字架上下来（太27:40-42）', 'ts'))
    out.append('</svg>')
    return '\n'.join(out)
