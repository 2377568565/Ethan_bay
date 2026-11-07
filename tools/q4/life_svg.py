# 《人活着，到底为了什么？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：日光之下，在主里面 ----------------
def sun():
    W = 400
    left = [('享乐', '传2:1'), ('事业成就', '传2:4-11'), ('财富', '传5:10'), ('知识学问', '传1:18'), ('被人记住', '传1:11')]
    right = [('认识上帝', '约17:3'), ('爱人如己', '太22:39'), ('忠心做今天的事', '西3:23'), ('为别人活', '罗14:7'), ('复活的盼望', '林前15:58')]
    RH, BH, TOP = 50, 38, 40
    H = TOP + len(left) * RH + 62
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="lff1t lff1d">',
           '<title id="lff1t">日光之下，在主里面</title>',
           '<desc id="lff1d">左边是日光之下：享乐、事业成就、财富、知识学问、被人记住，结局是虚空、捕风，像一口气。右边是在主里面：'
           '认识上帝、爱人如己、忠心做今天的事、为别人活、复活的盼望，结局是不是徒然的，存到永远。</desc>']
    out.append(text(104, 22, '日光之下（传道书）', 'tn hi', 'middle'))
    out.append(text(300, 22, '在主里面', 'tn hi', 'middle'))
    for col, items, x0, cls in [(0, left, 22, 'f0'), (1, right, 210, 'f1')]:
        for i, (t, r) in enumerate(items):
            y = TOP + i * RH
            out.append(f'<rect x="{x0}" y="{y}" width="168" height="{BH}" rx="10" class="{cls} fillc"/>')
            out.append(text(x0 + 84, y + 16, t, 'tnode2', 'middle'))
            out.append(text(x0 + 84, y + 31, r, 'tnode2', 'middle'))
    yb = TOP + len(left) * RH + 4
    out.append(f'<rect x="22" y="{yb}" width="168" height="34" rx="10" class="box"/>')
    out.append(text(106, yb + 22, '虚空、捕风（一口气）', 'tn', 'middle'))
    out.append(f'<rect x="210" y="{yb}" width="168" height="34" rx="10" class="box"/>')
    out.append(text(294, yb + 22, '不是徒然的（存到永远）', 'tn', 'middle'))
    out.append(text(200, H - 6, '左边的东西都不坏；只是承受不起整个人生的重量。', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
