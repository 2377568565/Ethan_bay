# 《1844年，天上发生了什么？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：圣所的三部分 ----------------
def plan():
    W, H = 400, 300
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="jgf1t jgf1d">',
           '<title id="jgf1t">圣所的三部分与基督的工作</title>',
           '<desc id="jgf1d">从左到右：外院有燔祭坛，预表十字架上一次献上的祭；圣所（头一层）有灯台、陈设饼、香坛，天天服事，'
           '预表基督升天以后的代求；至圣所（第二层）有约柜和施恩座，一年一次的赎罪日，预表审判和洁净。'
           '依据：出25—27章；来8—9章；利16章。复临信徒的理解。</desc>']
    boxes = [(10, 'f3', '外院', '燔祭坛', '十字架', '一次献上', '来9:26'),
             (140, 'f1', '圣所', '灯台·饼·香坛', '天天的服事', '代求、赦免', '来7:25'),
             (270, 'f4', '至圣所', '约柜·施恩座', '一年一次', '赎罪日、审判', '利16；但7:10')]
    for x, c, a, b, d, e, r in boxes:
        out.append(f'<rect x="{x}" y="40" width="120" height="180" rx="12" class="{c} fillc"/>')
        out.append(text(x + 60, 70, a, 'tnode2', 'middle'))
        out.append(text(x + 60, 100, b, 'tnode2', 'middle'))
        out.append(text(x + 60, 140, d, 'tnode2', 'middle'))
        out.append(text(x + 60, 162, e, 'tnode2', 'middle'))
        out.append(text(x + 60, 198, r, 'tnode2', 'middle'))
    out.append('<path d="M130 130 L140 130 M260 130 L270 130" class="flow"/>')
    out.append(text(W / 2, 22, '地上的圣所：天上事的“形状和影像”（来8:5）', 'tn hi', 'middle'))
    out.append(text(W / 2, 252, '升天以后：代求 → 1844年起：审判和洁净 → 复临', 'ts', 'middle'))
    out.append(text(W / 2, 276, '（复临信徒的理解）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：七十个七与二千三百日 ----------------
def time():
    W, H = 400, 290
    X0, X1 = 30, 370
    def x(yr):
        return X0 + (yr + 457) * (X1 - X0) / 2300
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="jgf2t jgf2d">',
           '<title id="jgf2t">七十个七与二千三百日</title>',
           '<desc id="jgf2d">一条长线从公元前457年到公元1844年，共2300年。开头一段490年（七十个七）从前457年到公元34年：'
           '49年到前408年，483年到公元27年（耶稣受洗受膏），一七之半是公元31年（十字架），490年到公元34年。'
           '余下1810年到1844年。复临信徒的算法。</desc>']
    out.append(text(W / 2, 20, '2300 年（但8:14）', 'tn hi', 'middle'))
    out.append(f'<rect x="{X0}" y="34" width="{X1 - X0}" height="22" rx="5" class="f1 fillc"/>')
    out.append(text(W / 2, 50, '前457年 → 公元1844年', 'tnode2', 'middle'))
    x34 = x(34)
    out.append(f'<rect x="{X0}" y="76" width="{x34 - X0:.1f}" height="22" rx="5" class="f4 fillc"/>')
    out.append(text(X0 + 4, 116, '490年（七十个七，但9:24）', 'ts'))
    out.append(f'<path d="M{x34:.1f} 70 L{x34:.1f} 104" class="ax"/>')
    out.append(f'<path d="M{X1} 30 L{X1} 64" class="ax"/>')
    rows = [('前457', '出令重建耶路撒冷（拉7章）'), ('前408', '49年：城重新建造'), ('公元27', '483年：受膏君（可1:15）'),
            ('公元31', '一七之半：十字架（但9:27）'), ('公元34', '490年：七十个七满'), ('1844', '2300年满：圣所洁净')]
    for i, (a, b) in enumerate(rows):
        y = 146 + i * 22
        out.append(text(96, y, a, 'tn hi', 'end'))
        out.append(text(108, y, b, 'ts'))
    out.append(text(W / 2, 284, '复临信徒的算法；各步骤都有不同意见', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：审判的三个阶段 ----------------
def three():
    W, H = 400, 300
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="jgf3t jgf3d">',
           '<title id="jgf3t">审判的三个阶段</title>',
           '<desc id="jgf3d">复临信徒常把圣经中的审判分为三个阶段：一、复临以前，在天上（但7:9-10；启14:7），审查自称属上帝的人；'
           '基督复临；二、千禧年中，圣徒参与审判（启20:4；林前6:2-3）；三、千禧年以后，执行审判（启20:11-15）。</desc>']
    rows = [('f1', '一、复临以前（天上）', '案卷展开；审查自称属上帝的人', '但7:9-10；启14:7'),
            ('f3', '二、千禧年中', '圣徒参与审判', '启20:4；林前6:2-3'),
            ('f6', '三、千禧年以后', '白色大宝座，执行审判', '启20:11-15')]
    for i, (c, a, b, r) in enumerate(rows):
        y = 14 + i * 96
        out.append(f'<rect x="30" y="{y}" width="340" height="66" rx="12" class="{c} fillc"/>')
        out.append(text(200, y + 22, a, 'tnode2', 'middle'))
        out.append(text(200, y + 40, b, 'tnode2', 'middle'))
        out.append(text(200, y + 58, r, 'tnode2', 'middle'))
    out.append('<path d="M200 80 L200 110" class="flow"/>')
    out.append(text(208, 99, '基督复临', 'ts'))
    out.append('<path d="M200 176 L200 206" class="flow"/>')
    out.append(text(W / 2, 294, '复临信徒常用的整理方式', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
