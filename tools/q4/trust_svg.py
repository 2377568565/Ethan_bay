# 《圣经可信吗？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：抄本数量对比 ----------------
def mss():
    W = 400
    rows = [('新约 · 拉丁文抄本', 10000, 'f1'), ('新约 · 其他古译本抄本', 9300, 'f1'), ('新约 · 希腊文抄本', 5800, 'f1'),
            ('荷马《伊利亚特》', 647, 'f0')]
    X0, X1, TOP, RH = 150, 330, 28, 40
    H = TOP + len(rows) * RH + 34
    mx = 10000
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="trf1t trf1d">',
           '<title id="trf1t">新约抄本与荷马《伊利亚特》抄本的数量</title>',
           '<desc id="trf1d">新约：拉丁文抄本一万多份，叙利亚文等其他古译本抄本约九千三百份，希腊文抄本五千八百多份；'
           '荷马《伊利亚特》：457份纸草、2份大写抄本、188份小写抄本，共约六百四十七份。</desc>']
    out.append(text(W / 2, 16, '保存下来的抄本数量（份）', 'tn hi', 'middle'))
    for i, (lab, n, c) in enumerate(rows):
        y = TOP + i * RH
        w = max(3, (X1 - X0) * n / mx)
        out.append(text(X0 - 8, y + 19, lab, 'tn', 'end'))
        out.append(f'<rect x="{X0}" y="{y + 6}" width="{w:.1f}" height="20" rx="4" class="{c} fillc"/>')
        out.append(text(X0 + w + 6, y + 21, f'{n:,}' + ('+' if n in (10000, 5800) else ''), 'ts'))
    out.append(text(W / 2, H - 18, '新约数字据经文鉴别学资料；《伊利亚特》据梅茨格的统计（457 + 2 + 188）', 'tw', 'middle'))
    out.append(text(W / 2, H - 5, '抄本越多，越能互相对照，找出原来的读法', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
