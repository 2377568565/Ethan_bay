# 《旧约律法，哪些还要守？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：约柜里与约柜旁 ----------------
def ark():
    W, H = 400, 300
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="lwf1t lwf1d">',
           '<title id="lwf1t">约柜里和约柜旁</title>',
           '<desc id="lwf1d">左边：十条诫，上帝亲口宣讲、用指头写在两块石版上，放在约柜里（出31:18；申4:13；10:4-5）。'
           '右边：其他律例典章，由摩西写在书上，放在约柜旁（申31:24-26）。</desc>']
    out.append(text(W / 2, 22, '同一座山上，两种写法、两个位置', 'tn hi', 'middle'))
    cols = [(14, 'f4', '约柜里', ['十条诫', '上帝亲口宣讲', '上帝的指头写', '刻在两块石版上'], '出31:18；申10:4-5'),
            (206, 'f1', '约柜旁', ['律例典章', '（献祭、节期、洁净、', '国家的法律等）', '摩西写在书上'], '申31:24-26')]
    for x, c, a, rows, r in cols:
        out.append(f'<rect x="{x}" y="40" width="180" height="200" rx="12" class="{c} fillc"/>')
        out.append(text(x + 90, 70, a, 'tn hi', 'middle'))
        for i, s in enumerate(rows):
            out.append(text(x + 90, 104 + i * 26, s, 'tnode2', 'middle'))
        out.append(text(x + 90, 224, r, 'tnode2', 'middle'))
    out.append(text(W / 2, 268, '一个在柜里，一个在柜旁', 'ts', 'middle'))
    out.append(text(W / 2, 290, '（圣经的记载；分类见下文）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：三种律法，三种结局 ----------------
def three():
    W, H = 400, 330
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="lwf2t lwf2d">',
           '<title id="lwf2t">三种律法，三种结局</title>',
           '<desc id="lwf2d">道德律（十条诫）：仍然有效，写在心上（太5:17；来8:10）。'
           '礼仪律（献祭、祭司、节期、割礼、洁净礼）：后事的影儿，在基督里成全（西2:17；来9:10）。'
           '民事律（以色列国的法律和刑罚）：随那个国家终止，公平的原则仍可借鉴（约8:11；申4:6）。'
           '依据：阿奎那、加尔文、《威斯敏斯德信条》第19章的三分法。</desc>']
    rows = [('f4', '道德律（十条诫）', '仍然有效，写在心上', '太5:17；来8:10'),
            ('f1', '礼仪律（献祭、节期、割礼……）', '后事的影儿，在基督里成全', '西2:17；来9:10'),
            ('f3', '民事律（以色列国的法律）', '随那个国家终止，原则可借鉴', '约8:11；申4:6')]
    for i, (c, a, b, r) in enumerate(rows):
        y = 14 + i * 100
        out.append(f'<rect x="20" y="{y}" width="360" height="76" rx="12" class="{c} fillc"/>')
        out.append(text(200, y + 24, a, 'tnode2', 'middle'))
        out.append(text(200, y + 46, b, 'tnode2', 'middle'))
        out.append(text(200, y + 66, r, 'tnode2', 'middle'))
    out.append(text(W / 2, 322, '三分法：阿奎那、加尔文、《威斯敏斯德信条》都采用', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：每周的安息日与年节的安息日 ----------------
def sabb():
    W, H = 400, 330
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="lwf3t lwf3d">',
           '<title id="lwf3t">每周的安息日与年节的“安息日”</title>',
           '<desc id="lwf3d">对比两种“安息日”。每周的安息日：从创造开始（创2:2-3）；每到第七日；写在十条诫里的石版上（出20:8-11）；'
           '回头纪念创造；为人设立（可2:27）。年节的安息日：西奈山以后设立（利23章）；跟着日期走，例如七月初一、七月初十；'
           '写在律法书里；预表基督和救恩；“在耶和华的安息日以外”（利23:38）。</desc>']
    out.append(text(W / 2, 20, '利23:38：“在耶和华的安息日以外”', 'tn hi', 'middle'))
    cols = [(14, 'f4', '每周的安息日', ['从创造开始', '每到第七日', '写在十诫石版上', '纪念创造', '“为人设立”'], '创2:2-3；出20:8-11'),
            (206, 'f1', '年节的“安息日”', ['西奈山以后', '跟着日期走', '写在律法书里', '预表基督', '和献祭相连'], '利23:24、32、37-38')]
    for x, c, a, rows, r in cols:
        out.append(f'<rect x="{x}" y="36" width="180" height="250" rx="12" class="{c} fillc"/>')
        out.append(text(x + 90, 64, a, 'tn hi', 'middle'))
        for i, s in enumerate(rows):
            out.append(text(x + 90, 98 + i * 30, s, 'tnode2', 'middle'))
        out.append(text(x + 90, 268, r, 'tnode2', 'middle'))
    out.append(text(W / 2, 314, '（编者整理）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
