# 《家人总在念叨，我为什么越听越烦？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图：越劝越僵，先听再说 ----------------
def spiral():
    W = 400
    left = [('妈妈担心，说出来', ''), ('孩子劝：“别想那么多”', '好心，却像没听见'), ('妈妈觉得没被理解', '再说一遍，说得更用力'),
            ('孩子更烦', '语气变重，或者躲开'), ('妈妈更不安', '又回到“说出来”')]
    right = [('妈妈担心，说出来', ''), ('孩子先听完', '雅1:19'), ('说出她的感受', '“你是怕我受委屈吧”'),
             ('说出自己的情况和感谢', '弗4:29'), ('一起交给上帝', '彼前5:7'), ('妈妈放心一些', '下次说得更少、更轻')]
    RH, BH, TOP = 52, 40, 36
    H = TOP + len(right) * RH + 28
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="lsf1t lsf1d">',
           '<title id="lsf1t">越劝越僵，先听再说</title>',
           '<desc id="lsf1d">左边是越劝越僵的圈子：妈妈担心，说出来；孩子劝她别想那么多，是好心，却像没听见；妈妈觉得没被理解，再说一遍，说得更用力；'
           '孩子更烦，语气变重或者躲开；妈妈更不安，又回到说出来。右边是先听再说的路：妈妈担心，说出来；孩子先听完；说出她的感受，例如你是怕我受委屈吧；'
           '说出自己的情况和感谢；一起把担心交给上帝；妈妈放心一些，下次说得更少、更轻。</desc>']
    out.append(text(104, 20, '越劝越僵（绕圈子）', 'tn hi', 'middle'))
    out.append(text(300, 20, '先听，再说', 'tn hi', 'middle'))

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
    y1, y5 = TOP + BH / 2, TOP + 4 * RH + BH / 2
    out.append(f'<path d="M22 {y5} L10 {y5} L10 {y1} L20 {y1}" class="flow"/>')
    out.append(f'<path d="M15 {y1 - 4} L21 {y1} L15 {y1 + 4}" class="flow"/>')
    out.append(text(200, H - 8, '“你们各人要快快地听，慢慢地说，慢慢地动怒。”（雅1:19）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
