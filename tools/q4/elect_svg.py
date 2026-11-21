# 《上帝早就定好谁得救吗？》页面里的两张图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图 1：罗马书 9—11 章的思路 ----------------
def map911():
    rows = [('9:1-5', '保罗的忧愁', '为骨肉之亲“心里时常伤痛”', 'f0'),
            ('9:6', '问题', '以色列人不信，上帝的话落空了吗？', 'f0'),
            ('9:6-13', '应许的线', '以撒、雅各：上帝按应许拣选', 'f2'),
            ('9:14-29', '上帝有权怜悯', '摩西、法老、窑匠', 'f2'),
            ('9:30—10:21', '原因', '“不凭着信心求”；上帝“整天伸手”', 'f4'),
            ('11:1-24', '没有弃绝', '因不信折下，若信“仍要被接上”', 'f6'),
            ('11:32', '结论', '“特意要怜恤众人”', 'f6')]
    W, rh = 400, 52
    H = 16 + rh * len(rows)
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="ef1t ef1d">',
           '<title id="ef1t">罗马书9到11章的思路</title>',
           '<desc id="ef1d">罗马书9到11章是一整段：保罗先为不信的以色列人忧愁；然后问上帝的话是否落空；接着讲上帝按应许拣选以撒、雅各；上帝有权怜悯，举摩西、法老和窑匠为例；然后说明以色列跌倒的原因是不凭信心求，而上帝整天伸手招呼；第11章说上帝没有弃绝他们，因不信被折下的，若不长久不信，仍要被接上；结论是上帝将众人都圈在不顺服之中，特意要怜恤众人。</desc>']
    for i, (ref, h, d, fam) in enumerate(rows):
        y = 8 + i * rh
        out.append(f'<rect x="10" y="{y}" width="92" height="{rh - 10}" rx="10" class="{fam} fillc"/>')
        out.append(text(56, y + (rh - 10) / 2 + 5, ref, 'tnode', 'middle'))
        out.append(text(114, y + 16, h, 'tn hi'))
        out.append(text(114, y + 34, d, 'tw'))
        if i < len(rows) - 1:
            out.append(f'<path d="M56 {y + rh - 10} L56 {y + rh}" class="flow"/>')
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 2：法老的心是谁使它刚硬的 ----------------
def pharaoh():
    ev = [('杖变蛇', '7:13', 'p'), ('① 血', '7:22', 'p'), ('② 青蛙', '8:15', 'P'), ('③ 虱子', '8:19', 'p'), ('④ 苍蝇', '8:32', 'P'),
          ('⑤ 畜疫', '9:7', 'p'), ('⑥ 疮', '9:12', 'G'), ('⑦ 冰雹', '9:34-35', 'P'), ('⑧ 蝗虫', '10:20', 'G'), ('⑨ 黑暗', '10:27', 'G'),
          ('⑩ 长子', '11:10', 'G'), ('红海', '14:8', 'G')]
    lab = {'p': ('法老的心刚硬', 'f0'), 'P': ('法老自己硬着心', 'f4'), 'G': ('耶和华使他刚硬', 'f6')}
    W, rh = 400, 30
    H = 70 + rh * len(ev)
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="ef2t ef2d">',
           '<title id="ef2t">出埃及记里，法老的心是谁使它刚硬的</title>',
           '<desc id="ef2d">按和合本出埃及记的记载：从杖变蛇到第五灾，经文说法老的心刚硬，或法老自己硬着心（7章13节、22节，8章15节、19节、32节，9章7节）；到第六灾才第一次说耶和华使法老的心刚硬（9章12节）；第七灾法老又自己硬着心（9章34节）；之后第八、九、十灾和红海，都说耶和华使法老的心刚硬。上帝在4章21节和7章3节事先说过祂要使法老的心刚硬。</desc>']
    keys = [('p', 10), ('P', 140), ('G', 270)]
    for k, x in keys:
        t, fam = lab[k]
        out.append(f'<rect x="{x}" y="8" width="14" height="14" rx="4" class="{fam} fillc"/>')
        out.append(text(x + 20, 20, t, 'ts'))
    out.append(text(10, 46, '事先预告：出4:21；7:3', 'tw'))
    for i, (n, ref, k) in enumerate(ev):
        y = 60 + i * rh
        t, fam = lab[k]
        out.append(text(10, y + 15, n, 'tn'))
        out.append(text(92, y + 15, '出' + ref, 'ts'))
        out.append(f'<rect x="170" y="{y + 2}" width="220" height="{rh - 8}" rx="8" class="{fam} fillc"/>')
        out.append(text(280, y + 17, t, 'tnode2', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
