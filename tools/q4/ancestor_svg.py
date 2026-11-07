# 《清明祭祖，基督徒算不算不孝？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：孝敬的三段 ----------------
def three():
    W, H = 400, 330
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="anf1t anf1d">',
           '<title id="anf1t">孝敬的三段</title>',
           '<desc id="anf1d">从上到下三段：生前孝敬——听从、照顾、报答（出20:12、提前5:4）；'
           '过世后纪念——安葬、立碑、流泪、讲述（创23、创35:20、约11:35）；'
           '将来重逢——主再来时，在基督里死了的人先复活（帖前4:16）。旁边写着：不向亡者献祭、跪拜、求保佑（出20:3-5、申26:14）。</desc>']
    rows = [('f1', '生前：孝敬', '听从、照顾、报答', '出20:12；提前5:4'),
            ('f3', '过世后：纪念', '安葬、立碑、流泪、讲述', '创23；创35:20；约11:35'),
            ('f4', '将来：重逢', '主再来，在基督里死了的人先复活', '帖前4:16')]
    for i, (c, t, d, r) in enumerate(rows):
        y = 16 + i * 96
        out.append(f'<rect x="40" y="{y}" width="320" height="72" rx="14" class="{c} fillc"/>')
        out.append(text(200, y + 24, t, 'tnode2', 'middle'))
        out.append(text(200, y + 44, d, 'tnode2', 'middle'))
        out.append(text(200, y + 62, r, 'tnode2', 'middle'))
        if i < 2:
            out.append(f'<path d="M200 {y + 72} L200 {y + 96}" class="flow"/>')
    out.append(text(200, 314, '不做：向亡者献祭、跪拜、求保佑（出20:3-5；申26:14）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
