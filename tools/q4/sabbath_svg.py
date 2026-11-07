# 《谁改了安息日？》页面里的两张图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
from history_svg import text


# ---------------- 图 1：受难周的三天，对上今天的星期 ----------------
def week():
    W, H = 400, 292
    days = [('五', '星期五', 'f0'), ('六', '星期六', 'f6'), ('日', '星期日', 'f3')]
    bible = [('预备日', '耶稣被钉、埋葬', '路23:54；可15:42'), ('安息日', '妇女“遵着诫命安息”', '路23:56'), ('七日的头一日', '耶稣复活', '路24:1；可16:9')]
    church = ['受难日', '（安息日）', '复活节']
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="sf1t sf1d">',
           '<title id="sf1t">受难周的三天对上今天的星期</title>',
           '<desc id="sf1d">福音书里连续的三天：预备日耶稣被钉，安息日妇女遵着诫命安息，七日的头一日耶稣复活。全世界的教会在星期五纪念受难、在星期日庆祝复活，所以中间的安息日就是星期六。</desc>']
    out.append(text(14, 22, '福音书的记载', 'tn'))
    out.append(text(14, 174, '全世界教会的日历', 'tn'))
    xs = [14, 141, 268]
    bw = 118
    for i, ((short, name, fam), (b1, b2, ref), ch) in enumerate(zip(days, bible, church)):
        x = xs[i]
        out.append(f'<rect x="{x}" y="34" width="{bw}" height="96" rx="12" class="box"/>')
        out.append(f'<rect x="{x}" y="34" width="{bw}" height="6" rx="3" class="{fam} fillc"/>')
        out.append(text(x + bw / 2, 66, b1, 'tn hi', 'middle'))
        out.append(text(x + bw / 2, 88, b2, 'tw', 'middle'))
        out.append(text(x + bw / 2, 112, ref, 'ts', 'middle'))
        out.append(f'<path d="M{x + bw / 2} 134 L{x + bw / 2} 156" class="cn {fam} dash"/>')
        out.append(f'<rect x="{x}" y="184" width="{bw}" height="60" rx="12" class="{fam} fillc"/>')
        out.append(text(x + bw / 2, 212, name, 'tnode', 'middle'))
        out.append(text(x + bw / 2, 232, ch, 'tnode2', 'middle'))
    out.append(text(W / 2, 274, '复活日是星期日 → 前一天的安息日就是星期六', 'tn', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 2：安息日到星期日的演变（时间轴） ----------------
def timeline():
    W, H = 400, 424
    ev = [(30, '约30年', '耶稣和门徒守安息日', '路4:16；23:56', 'f6'),
          (50, '约50年', '保罗“照素常的规矩”在安息日讲道', '徒17:2；18:4', 'f6'),
          (110, '约110年', '伊格那丢提到“主的日子”', '原文与翻译有争议', 'f0'),
          (155, '约155年', '游斯丁：基督徒在“太阳日”聚会', '第一次明确提到星期日聚会', 'f0'),
          (202, '约202年', '特土良第一次提到星期日休息', '据天主教百科全书', 'f0'),
          (321, '321年', '君士坦丁：“可敬的太阳日”休息令', '第一条星期日国家法律', 'f2'),
          (364, '约364年', '老底嘉会议：不可在安息日休息', '违者“被咒诅”', 'f2'),
          (440, '约440年', '几乎各地教会仍在安息日聚会', '罗马、亚历山大城除外', 'f0')]
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="sf2t sf2d">',
           '<title id="sf2t">安息日到星期日的演变</title>',
           '<desc id="sf2d">时间轴：约30年耶稣和门徒守安息日；约50年保罗照素常的规矩在安息日讲道；约110年伊格那丢提到主的日子；约155年游斯丁记载基督徒在太阳日聚会；约202年特土良提到星期日休息；321年君士坦丁颁布太阳日休息令；约364年老底嘉会议禁止在安息日休息；约440年几乎各地教会仍在安息日聚会，只有罗马和亚历山大城例外。</desc>']
    x0, y0, step = 92, 26, 48
    out.append(f'<path d="M{x0} {y0} L{x0} {y0 + step * (len(ev) - 1)}" class="ax"/>')
    for i, (yr, lab, t1, t2, fam) in enumerate(ev):
        y = y0 + step * i
        out.append(text(x0 - 12, y + 4, lab, 'ty', 'end'))
        out.append(f'<circle cx="{x0}" cy="{y}" r="6" class="{fam} fillc"/>')
        out.append(text(x0 + 14, y + 1, t1, 'tn'))
        out.append(text(x0 + 14, y + 17, t2, 'ts'))
    out.append(text(x0 + 14, H - 10, '红：守安息日　灰：星期日渐起　橙：法令与教规', 'ts'))
    out.append('</svg>')
    return '\n'.join(out)
