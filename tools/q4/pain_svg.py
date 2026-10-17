# 《一个好上帝，为什么允许苦难？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：圣经里的大故事 ----------------
def story():
    W = 400
    acts = [('f1', '起初：一切都甚好', '没有死亡、疾病、眼泪', '创1:31'),
            ('f6', '天上的背叛', '撒但控告上帝不公', '启12:7-9'),
            ('f2', '人选择离开', '罪进入，死也跟着进入', '创3；罗5:12'),
            ('f4', '十字架', '上帝亲自受苦，撒但被审判', '约12:31'),
            ('f0', '现在：麦子和稗子一齐长', '受造之物一同叹息', '太13:30；罗8:22'),
            ('f3', '最后：擦去一切眼泪', '不再有死亡、悲哀、疼痛', '启21:4')]
    RH, BH, TOP = 58, 48, 10
    H = TOP + len(acts) * RH + 20
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="pnf1t pnf1d">',
           '<title id="pnf1t">圣经里的大故事</title>',
           '<desc id="pnf1d">六幕：起初一切都甚好，没有死亡疾病眼泪；天上的背叛，撒但控告上帝不公；人选择离开，罪进入，死也跟着进入；'
           '十字架，上帝亲自受苦，撒但被审判；现在麦子和稗子一齐长，受造之物一同叹息；最后上帝擦去一切眼泪，不再有死亡、悲哀、疼痛。</desc>']
    out.append(f'<path d="M36 {TOP + BH / 2} L36 {TOP + (len(acts) - 1) * RH + BH / 2}" class="flow"/>')
    for i, (c, t, s, r) in enumerate(acts):
        y = TOP + i * RH
        out.append(f'<circle cx="36" cy="{y + BH / 2}" r="15" class="{c} fillc"/>')
        out.append(text(36, y + BH / 2 + 5, str(i + 1), 'tnode', 'middle'))
        out.append(f'<rect x="60" y="{y}" width="{W - 66}" height="{BH}" rx="10" class="box"/>')
        out.append(text(72, y + 20, t, 'tn'))
        out.append(text(72, y + 37, s, 'ts'))
        out.append(text(W - 14, y + 20, r, 'ts', 'end'))
    out.append(text(W / 2, H - 4, '我们活在第 5 幕：苦难是真的，但它不是故事的结局。', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
