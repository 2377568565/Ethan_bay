# 《我还会犯罪，能得救吗？》页面里的两张图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


def _arrow(x1, y1, x2, y2):
    return (f'<path d="M{x1} {y1} L{x2} {y2}" class="flow"/>'
            f'<path d="M{x2 - 4} {y2 - 6} L{x2} {y2} L{x2 + 4} {y2 - 6}" class="flow"/>')


# ---------------- 图 1：罪的两面，救恩的两面 ----------------
def two():
    W, H = 400, 404
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="rf1t rf1d">',
           '<title id="rf1t">罪的两面，救恩的两面</title>',
           '<desc id="rf1d">罪有两面：一面是罪责，就是我们欠下的债，需要赦免，上帝因信称我们为义，这是立刻、完全的；另一面是罪的权势，就是里面的败坏和捆绑，需要改变，上帝赐新心、借圣灵使人成圣，这是一生之久的。两面都来自基督，祂是我们的公义、圣洁、救赎。</desc>']
    out.append(f'<rect x="130" y="10" width="140" height="44" rx="12" class="f0 fillc"/>')
    out.append(text(200, 38, '罪', 'tnode', 'middle'))
    out.append('<path d="M200 54 L200 70 L100 70 L100 86 M200 70 L300 70 L300 86" class="flow"/>')
    cols = [(10, 'f2', '罪责', '我欠下的债、被定罪', '需要：赦免', '称义', '立刻的、完全的', '罗5:1；约壹1:9'),
            (210, 'f6', '罪的权势', '里面的败坏、被捆绑', '需要：改变', '成圣', '一生之久、渐渐长进', '罗6:14；林后3:18')]
    for x, fam, h, s, need, ans, how, ref in cols:
        out.append(f'<rect x="{x}" y="88" width="180" height="62" rx="12" class="box"/>')
        out.append(text(x + 90, 114, h, 'tn hi', 'middle'))
        out.append(text(x + 90, 134, s, 'tw', 'middle'))
        out.append(_arrow(x + 90, 150, x + 90, 174))
        out.append(text(x + 98, 166, need, 'ts'))
        out.append(f'<rect x="{x}" y="176" width="180" height="76" rx="12" class="{fam} fillc"/>')
        out.append(text(x + 90, 206, ans, 'tnode', 'middle'))
        out.append(text(x + 90, 226, how, 'tnode2', 'middle'))
        out.append(text(x + 90, 243, ref, 'tnode2', 'middle'))
    out.append('<path d="M100 252 L100 274 L300 274 L300 252 M200 274 L200 290" class="flow"/>')
    out.append(f'<rect x="60" y="292" width="280" height="56" rx="12" class="f1 fillc"/>')
    out.append(text(200, 316, '都来自基督', 'tnode', 'middle'))
    out.append(text(200, 336, '祂“成为我们的公义、圣洁、救赎”', 'tnode2', 'middle'))
    out.append(text(200, 366, '林前1:30', 'ts', 'middle'))
    out.append(text(200, 390, '罗马书7章的呼喊，问的主要是右边这一面', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 2：罗马书 5—8 章的一条路 ----------------
def road():
    W, rh = 400, 82
    rows = [('5', '因信称义，与上帝相和', '“我们既因信称义，就……得与上帝相和。”', '罗5:1', 'f2'),
            ('6', '向罪死了，不容罪作王', '“我们可以仍在罪中、叫恩典显多吗？断乎不可！”', '罗6:1-2、12', 'f3'),
            ('7', '靠自己、靠律法：做不到', '“我真是苦啊！谁能救我……？”', '罗7:18、24', 'f0'),
            ('8', '靠圣灵：不定罪，也能顺从', '“律法的义成就在我们这……只随从圣灵的人身上。”', '罗8:1-4', 'f6')]
    H = 14 + rh * len(rows) + 8
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="rf2t rf2d">',
           '<title id="rf2t">罗马书5到8章的一条路</title>',
           '<desc id="rf2d">第5章：因信称义，与上帝相和。第6章：向罪死了，不容罪在身上作王。第7章：一个人想靠自己、靠律法行善，却做不到，呼喊“我真是苦啊”。第8章：靠着圣灵，在基督里的人不被定罪，律法的义也成就在随从圣灵的人身上。第7章不是终点，第8章才是答案。</desc>']
    for i, (n, t1, t2, ref, fam) in enumerate(rows):
        y = 10 + i * rh
        out.append(f'<circle cx="30" cy="{y + 28}" r="20" class="{fam} fillc"/>')
        out.append(text(30, y + 34, n, 'tnode', 'middle'))
        out.append(text(60, y + 14, '第' + n + '章', 'ts'))
        out.append(text(60, y + 33, t1, 'tn hi'))
        out.append(text(60, y + 52, t2, 'tw'))
        out.append(text(W - 8, y + 14, ref, 'ts', 'end'))
        if i < len(rows) - 1:
            out.append(f'<path d="M30 {y + 50} L30 {y + rh + 4}" class="cn {rows[i + 1][4]} dash"/>')
    out.append('</svg>')
    return '\n'.join(out)
