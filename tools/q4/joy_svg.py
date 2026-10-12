# 《喜乐的心，为什么是良药？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图 1：哪些说法有根据（证据强弱） ----------------
def evid():
    W = 400
    bands = [
        ('f1', '证据较强（多项大型研究或荟萃分析）', [
            '乐观 → 心血管病较少、寿命较长',
            '医生诊断的抑郁 → 骨密度偏低（女性更明显）',
            '长期压力 → 多种免疫功能下降',
            '抑郁 → 两种炎症因子升高',
            '常去聚会的女性 → 死亡率较低']),
        ('f4', '有一些证据（还在研究）', [
            '感恩练习 → 正面情绪增加，焦虑抑郁减轻',
            '反复担忧 → 身体的压力反应拖得更久',
            '心理因素与癌症 → 结果不一，可能有发表偏倚']),
        ('f0', '没有找到可靠证据', [
            '生活压力、工作压力 → 乳腺癌等癌症发病',
            '情绪 → 肺、乳腺、甲状腺结节',
            '“生病是因为不够喜乐”']),
    ]
    LH, HH, GAP = 17, 24, 10
    H = 8 + sum(HH + len(it) * LH + 8 + GAP for _, _, it in bands) + 18
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="jf1t jf1d">',
           '<title id="jf1t">心情与身体：哪些说法有根据</title>',
           '<desc id="jf1d">证据较强的：乐观的人心血管病较少、寿命较长；医生诊断的抑郁与骨密度偏低有关，女性更明显；长期压力使多种免疫功能下降；'
           '抑郁的人两种炎症因子升高；常去聚会的女性死亡率较低。有一些证据、还在研究的：感恩练习使正面情绪增加、焦虑抑郁减轻；反复担忧使身体的压力反应拖得更久；'
           '心理因素与癌症的研究结果不一，可能有发表偏倚。没有找到可靠证据的：生活压力、工作压力导致乳腺癌等癌症；情绪导致肺、乳腺、甲状腺结节；“生病是因为不够喜乐”。'
           '这些研究多是观察到的关联，不一定是因果。</desc>']
    y = 8
    for cls, head, items in bands:
        h = HH + len(items) * LH + 8
        out.append(f'<rect x="4" y="{y}" width="{W - 8}" height="{h}" rx="10" class="box"/>')
        out.append(f'<rect x="4" y="{y}" width="{W - 8}" height="{HH}" rx="10" class="{cls} fillc"/>')
        out.append(f'<rect x="4" y="{y + HH - 10}" width="{W - 8}" height="10" class="{cls} fillc"/>')
        out.append(text(16, y + 16, head, 'tnode2'))
        for i, it in enumerate(items):
            out.append(text(18, y + HH + 15 + i * LH, '· ' + it, 'tn'))
        y += h + GAP
    out.append(text(W / 2, y + 6, '注：多数是观察到的“关联”，不一定是“因果”；出处见正文', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 2：反刍的路，交托的路 ----------------
def loop():
    W = 400
    left = [('一件烦心事', ''), ('反复去想', '越想越大'), ('身体一直绷着', '睡不好、心跳快'),
            ('更累、更烦', ''), ('更容易往坏处想', '又回到“反复去想”')]
    right = [('一件烦心事', ''), ('说出来，交给上帝', '腓4:6'), ('带着感谢', '数一数已有的恩典'),
             ('平安保守心怀意念', '腓4:7'), ('思念真实、可爱的事', '腓4:8'), ('做今天能做的一步', '太6:34')]
    RH, BH, TOP = 52, 40, 36
    H = TOP + len(right) * RH + 28
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="jf2t jf2d">',
           '<title id="jf2t">反刍的路，交托的路</title>',
           '<desc id="jf2d">左边是反刍的路：一件烦心事，反复去想，越想越大；身体一直绷着，睡不好、心跳快；更累、更烦；更容易往坏处想，又回到反复去想，成了一个圈。'
           '右边是腓立比书4章的路：一件烦心事，凡事藉着祷告说出来、交给上帝；带着感谢，数一数已有的恩典；上帝出人意外的平安保守心怀意念；'
           '思念真实、可爱的事；做今天能做的一步，一天的难处一天当。</desc>']
    out.append(text(104, 20, '反刍的路（绕圈子）', 'tn hi', 'middle'))
    out.append(text(300, 20, '交托的路（腓立比书4章）', 'tn hi', 'middle'))

    def col(items, x0, w, cls):
        for i, (t, r) in enumerate(items):
            y = TOP + i * RH
            out.append(f'<rect x="{x0}" y="{y}" width="{w}" height="{BH}" rx="10" class="{cls} fillc"/>')
            if r:
                out.append(text(x0 + w / 2, y + 17, t, 'tnode2', 'middle'))
                out.append(text(x0 + w / 2, y + 32, r, 'tnode2', 'middle'))
            else:
                out.append(text(x0 + w / 2, y + 25, t, 'tnode2', 'middle'))
            if i < len(items) - 1:
                out.append(f'<path d="M{x0 + w / 2} {y + BH} L{x0 + w / 2} {y + RH}" class="flow"/>')

    col(left, 22, 168, 'f2')
    col(right, 210, 180, 'f1')
    # 左边的圈：从最后一格回到第二格
    y2, y5 = TOP + RH + BH / 2, TOP + 4 * RH + BH / 2
    out.append(f'<path d="M22 {y5} L10 {y5} L10 {y2} L20 {y2}" class="flow"/>')
    out.append(f'<path d="M15 {y2 - 4} L21 {y2} L15 {y2 + 4}" class="flow"/>')
    out.append(text(200, H - 8, '“上帝所赐、出人意外的平安必在基督耶稣里保守你们的心怀意念。”（腓4:7）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
