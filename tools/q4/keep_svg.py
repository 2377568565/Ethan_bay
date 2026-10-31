# 《安息日，到底能做什么？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：拿不准的事，按次序问五个问题 ----------------
def flow():
    W, rh = 400, 74
    rows = [('1  为了谋生、赚钱、前途，', '或是做买卖吗？', '出20:9-10；尼13:15', '是', '留给六天', 'f2'),
            ('2  能在六天里做完，', '或在星期五预备好吗？', '出16:23', '能', '提前做好', 'f2'),
            ('3  是必要的事吗？', '（生命、健康、安全）', '太12:3-4', '是', '可以做', 'f6'),
            ('4  是怜悯、行善的事吗？', '（救人、医病、探访）', '太12:12；路14:5', '是', '正该做', 'f6'),
            ('5  让我更亲近上帝和人，', '又能凭信心去做吗？', '赛58:13；罗14:23', '是', '可以做', 'f1')]
    H = 20 + rh * len(rows) + 24
    qx, qw, bh, ox, ow = 10, 236, 50, 296, 94
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="kf1t kf1d">',
           '<title id="kf1t">遇到拿不准的事，按次序问五个问题</title>',
           '<desc id="kf1d">第一问：是为了谋生、赚钱、前途或买卖吗？是，就留给六天。否则第二问：能在六天里做完或星期五预备好吗？能，就提前做好。否则第三问：是必要的事吗？是，就可以做。否则第四问：是怜悯、行善的事吗？是，就正该做。否则第五问：它让我更亲近上帝和人、又能凭信心去做吗？是，就可以做；否则就放下。</desc>']
    for i, (a, b, ref, yes, res, fam) in enumerate(rows):
        y = 14 + i * rh
        out.append(f'<rect x="{qx}" y="{y}" width="{qw}" height="{bh}" rx="12" class="box"/>')
        out.append(text(qx + 12, y + 21, a, 'tn'))
        out.append(text(qx + 26, y + 39, b, 'tn'))
        out.append(f'<path d="M{qx + qw} {y + bh / 2} L{ox - 4} {y + bh / 2}" class="flow"/>')
        out.append(f'<path d="M{ox - 10} {y + bh / 2 - 4} L{ox - 4} {y + bh / 2} L{ox - 10} {y + bh / 2 + 4}" class="flow"/>')
        out.append(text((qx + qw + ox) / 2, y + bh / 2 - 6, yes, 'tw', 'middle'))
        out.append(f'<rect x="{ox}" y="{y + 4}" width="{ow}" height="{bh - 8}" rx="10" class="{fam} fillc"/>')
        out.append(text(ox + ow / 2, y + bh / 2 + 5, res, 'tnode', 'middle'))
        cx = qx + 40
        if i < len(rows) - 1:
            out.append(f'<path d="M{cx} {y + bh} L{cx} {y + rh - 2}" class="flow"/>')
            out.append(f'<path d="M{cx - 4} {y + rh - 8} L{cx} {y + rh - 2} L{cx + 4} {y + rh - 8}" class="flow"/>')
            out.append(text(cx + 8, y + bh + 16, '否', 'tw'))
            out.append(text(qx + qw, y + bh + 16, ref, 'ts', 'end'))
        else:
            out.append(text(qx + qw, y + bh + 16, ref, 'ts', 'end'))
            out.append(text(cx - 30, y + bh + 16, '否 → 放下，留到别的日子', 'tw'))
    out.append('</svg>')
    return '\n'.join(out)
