# 《旧约的上帝和新约的上帝》页面里的两张图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图 1：出埃及记34:6 在旧约里的回声 ----------------
def echo():
    W, H = 400, 372
    refs = [('民14:18', '摩西为百姓求情'), ('尼9:17', '归回后的认罪'), ('诗86:15', '大卫的祷告'), ('诗103:8', '称颂的诗'),
            ('诗145:8', '赞美的诗'), ('珥2:13', '先知呼召悔改'), ('拿4:2', '约拿埋怨上帝太慈悲'), ('鸿1:3', '先知论审判')]
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="gf1t gf1d">',
           '<title id="gf1t">上帝自己的“名片”在旧约里的回声</title>',
           '<desc id="gf1d">出埃及记34章6节，上帝亲自宣告自己是有怜悯有恩典、不轻易发怒、有丰盛慈爱和诚实的上帝。这句话在旧约里又被引用了至少八次：民数记14章18节、尼希米记9章17节、诗篇86篇15节、103篇8节、145篇8节、约珥书2章13节、约拿书4章2节、那鸿书1章3节。</desc>']
    out.append(f'<rect x="10" y="10" width="380" height="74" rx="14" class="f6 fillc"/>')
    out.append(text(200, 36, '出埃及记 34:6 · 上帝亲口宣告', 'tnode', 'middle'))
    out.append(text(200, 58, '有怜悯有恩典，不轻易发怒，', 'tnode2', 'middle'))
    out.append(text(200, 74, '并有丰盛的慈爱和诚实', 'tnode2', 'middle'))
    out.append(text(200, 106, '这句话在旧约里一再被引用（下面是其中八处）', 'tw', 'middle'))
    for i, (r, d) in enumerate(refs):
        col, row = i % 2, i // 2
        x, y = 10 + col * 195, 120 + row * 58
        out.append(f'<rect x="{x}" y="{y}" width="185" height="48" rx="10" class="box"/>')
        out.append(f'<rect x="{x}" y="{y}" width="6" height="48" rx="3" class="f6 fillc"/>')
        out.append(text(x + 16, y + 21, r, 'tn hi'))
        out.append(text(x + 16, y + 38, d, 'ts'))
    out.append(text(200, 362, '旧约的“基调”，是上帝自己说的：慈爱和诚实', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 2：恩慈和严厉，两约都有 ----------------
def grid():
    W, H = 400, 330
    cells = [  # (行, 列, 标题, 例子)
        (0, 0, '旧约里的恩慈', ['“我以永远的爱爱你”（耶31:3）', '尼尼微悔改，上帝不降灾（拿3:10）', '“爱人如己”（利19:18）']),
        (0, 1, '新约里的恩慈', ['“上帝爱世人”（约3:16）', '浪子的父亲跑去抱他（路15:20）', '“要爱你们的仇敌”（太5:44）']),
        (1, 0, '旧约里的严厉', ['洪水（创6—8）', '所多玛（创19）', '乌撒扶约柜（撒下6:7）']),
        (1, 1, '新约里的严厉', ['“地狱”13次，11次出自耶稣', '亚拿尼亚和撒非喇（徒5）', '“羔羊的忿怒”（启6:16）']),
    ]
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="gf2t gf2d">',
           '<title id="gf2t">恩慈和严厉，两约都有</title>',
           '<desc id="gf2d">四格对照：旧约里有恩慈，例如“我以永远的爱爱你”、尼尼微悔改上帝不降灾、“爱人如己”；新约里有恩慈，例如“上帝爱世人”、浪子的父亲、“要爱你们的仇敌”。旧约里有严厉，例如洪水、所多玛、乌撒；新约里也有严厉，例如“地狱”一词13次中11次出自耶稣、亚拿尼亚和撒非喇、“羔羊的忿怒”。保罗说：“可见上帝的恩慈和严厉”（罗马书11章22节）。</desc>']
    out.append(text(105, 20, '旧约', 'tn hi', 'middle'))
    out.append(text(300, 20, '新约', 'tn hi', 'middle'))
    for r, c, h, ex in cells:
        x, y = 10 + c * 195, 30 + r * 140
        fam = 'f6' if r == 0 else 'f4'
        out.append(f'<rect x="{x}" y="{y}" width="185" height="130" rx="12" class="box"/>')
        out.append(f'<rect x="{x}" y="{y}" width="185" height="30" rx="12" class="{fam} fillc"/>')
        out.append(f'<rect x="{x}" y="{y + 18}" width="185" height="12" class="{fam} fillc"/>')
        out.append(text(x + 92.5, y + 20, h, 'tnode', 'middle'))
        for k, e in enumerate(ex):
            out.append(text(x + 10, y + 55 + k * 26, e, 'tw'))
    out.append(text(200, 322, '“可见上帝的恩慈和严厉”（罗11:22）——同一位上帝', 'tn', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
