# 《666 和兽的印记，到底是什么？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：但以理书7章的四兽合成启示录13章的海兽 ----------------
def map():
    W, H = 400, 330
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="bsf1t bsf1d">',
           '<title id="bsf1t">但以理书7章的四兽与启示录13章的海兽</title>',
           '<desc id="bsf1d">上排是但以理书7章的四个兽：狮子（巴比伦，但2:38）、熊（米底亚和波斯，但8:20）、豹（希腊，但8:21）、'
           '有十角的第四兽（罗马）。下面是启示录13章的海兽：形状像豹、脚像熊、口像狮子、有十角，龙把座位给它。'
           '它把前面四个兽合在一起，并且从第四兽中兴起。</desc>']
    out.append(text(W / 2, 16, '但以理书7章：四个兽（但以理向前看）', 'tn hi', 'middle'))
    beasts = [('f3', '狮子', '巴比伦', '但2:38'), ('f4', '熊', '米底亚波斯', '但8:20'),
              ('f1', '豹', '希腊', '但8:21'), ('f6', '第四兽·十角', '罗马', '但7:7、24')]
    for i, (c, a, b, r) in enumerate(beasts):
        x = 6 + i * 98
        out.append(f'<rect x="{x}" y="28" width="92" height="76" rx="10" class="{c} fillc"/>')
        out.append(text(x + 46, 52, a, 'tnode2', 'middle'))
        out.append(text(x + 46, 72, b, 'tnode2', 'middle'))
        out.append(text(x + 46, 92, r, 'tnode2', 'middle'))
        out.append(f'<path d="M{x + 46} 104 L{200 + (i - 1.5) * 40:.0f} 176" class="flow"/>')
    out.append('<rect x="60" y="176" width="280" height="96" rx="14" class="box"/>')
    out.append(text(W / 2, 200, '启示录13章：海中上来的兽', 'tn hi', 'middle'))
    out.append(text(W / 2, 222, '形状像豹 · 脚像熊 · 口像狮子 · 十角', 'ts', 'middle'))
    out.append(text(W / 2, 242, '（约翰向后看，次序倒过来）', 'ts', 'middle'))
    out.append(text(W / 2, 262, '“那龙将自己的能力、座位和大权柄都给了它”', 'ts', 'middle'))
    out.append(text(W / 2, 296, '继承前面的帝国，从第四兽（罗马）中兴起', 'tw', 'middle'))
    out.append(text(W / 2, 314, '启13:1-2；但7:2-8', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：1260年时间线 ----------------
def timeline():
    W, H = 400, 250
    X0, X1, Y = 40, 360, 120

    def x(yr):
        return X0 + (yr - 538) * (X1 - X0) / (1798 - 538)
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="bsf2t bsf2d">',
           '<title id="bsf2t">1260年：复临信徒采用的算法</title>',
           '<desc id="bsf2d">时间线：493年奥多亚克被杀（赫鲁利），534年汪达尔王国灭亡，538年东哥特人从罗马撤围，'
           '从538年到1798年共1260年；1798年2月法军进入罗马，教皇庇护六世被俘，1799年死于法国瓦朗斯（“受了死伤”）。'
           '依据：三年半=四十二个月=一千二百六十天，一日顶一年（民14:34；结4:6）。历史派内部也有其他算法。</desc>']
    out.append(text(W / 2, 18, '一载二载半载 = 42个月 = 1260天 → 1260年', 'tn hi', 'middle'))
    out.append(f'<rect x="{X0}" y="{Y - 14}" width="{X1 - X0}" height="28" rx="6" class="f1 fillc"/>')
    out.append(text(W / 2, Y + 5, '1260 年', 'tnode2', 'middle'))
    for yr, lab, dy in ((538, '538', 1), (1798, '1798', 1)):
        out.append(f'<path d="M{x(yr):.1f} {Y - 22} L{x(yr):.1f} {Y + 22}" class="ax"/>')
        out.append(text(x(yr), Y + 40, lab, 'tn hi', 'middle'))
    out.append(text(X0, 52, '493 赫鲁利 · 534 汪达尔', 'ts'))
    out.append(text(X0, 70, '538 东哥特人从罗马撤围', 'ts'))
    out.append(f'<path d="M{X0} 76 L{X0} {Y - 16}" class="flow"/>')
    out.append(text(X1, 52, '1798 法军进入罗马', 'ts', 'end'))
    out.append(text(X1, 70, '教皇被俘（“死伤”）', 'ts', 'end'))
    out.append(f'<path d="M{X1} 76 L{X1} {Y - 16}" class="flow"/>')
    out.append(text(W / 2, 192, '被连根拔出的三角（但7:8）：复临信徒的理解', 'tw', 'middle'))
    out.append(text(W / 2, 210, '依据：民14:34；结4:6（一日顶一年）', 'tw', 'middle'))
    out.append(text(W / 2, 228, '历史派内部对起止年份还有其他算法', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：上帝的印与兽的印记 ----------------
def two():
    W, H = 400, 360
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="bsf3t bsf3d">',
           '<title id="bsf3t">上帝的印与兽的印记</title>',
           '<desc id="bsf3d">左边是上帝的印，右边是兽的印记，逐项对照：位置——只在额上（启7:3）对额上或右手上（启13:16）；'
           '敬拜——敬拜那创造天地海的（启14:7）对拜兽和兽像（启14:9）；标记——守上帝诫命和耶稣真道（启14:12）对想改变节期和律法（但7:25）；'
           '方式——邀请，愿意的都可以来（启22:17）对强迫，不得做买卖、被杀（启13:15-17）；结局——站在玻璃海上唱歌（启15:2）对喝上帝大怒的酒（启14:10）。</desc>']
    out.append(text(105, 20, '上帝的印', 'tn hi', 'middle'))
    out.append(text(295, 20, '兽的印记', 'tn hi', 'middle'))
    rows = [('只在额上', '7:3', '额上或右手上', '13:16'),
            ('敬拜创造天地海的', '14:7', '拜兽和兽像', '14:9'),
            ('守上帝诫命和耶稣真道', '14:12', '想改变节期和律法', '但7:25'),
            ('邀请：愿意的都可以来', '22:17', '强迫：不得买卖、被杀', '13:15-17'),
            ('站在玻璃海上唱歌', '15:2', '喝上帝大怒的酒', '14:10')]
    for i, (a, ra, b, rb) in enumerate(rows):
        y = 34 + i * 62
        out.append(f'<rect x="10" y="{y}" width="190" height="50" rx="10" class="f1 fillc"/>')
        out.append(f'<rect x="200" y="{y}" width="190" height="50" rx="10" class="f6 fillc"/>')
        out.append(text(105, y + 22, a, 'tnode2', 'middle'))
        out.append(text(105, y + 40, ('启' if ra[0].isdigit() else '') + ra, 'tnode2', 'middle'))
        out.append(text(295, y + 22, b, 'tnode2', 'middle'))
        out.append(text(295, y + 40, ('启' if rb[0].isdigit() else '') + rb, 'tnode2', 'middle'))
    out.append('<path d="M200 34 L200 344" stroke="var(--surface)" stroke-width="4"/>')
    out.append('</svg>')
    return '\n'.join(out)
