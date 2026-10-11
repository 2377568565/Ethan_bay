# 《基督教两千年家谱》页面里的三张图（SVG，由程序算位置，手机上也看得清）
# 颜色按“家族”：f0 早期共同的教会、f1 东方亚述、f2 东方正统、f3 东正教、f4 天主教、f5 新教、f6 复临
# （色板已用色盲检查脚本验证：浅色、深色两套都通过）

def esc(s):
    return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, cls='t', anchor='start'):
    return f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{esc(s)}</text>'


# ---------------- 图 1：两千年总家谱（河流图） ----------------
def overview():
    W, H = 400, 340
    # 年份 → 横坐标（分段：前面几百年压缩一些，近代放宽）
    seg = [(30, 16), (451, 110), (1054, 190), (1517, 250), (1844, 318), (2026, 392)]

    def X(y):
        for (y0, x0), (y1, x1) in zip(seg, seg[1:]):
            if y <= y1:
                return x0 + (y - y0) / (y1 - y0) * (x1 - x0)
        return seg[-1][1]
    END = X(2026)
    rows = {'east': 42, 'orient': 80, 'trunk': 122, 'ortho': 122, 'cath': 164, 'prot': 216, 'sda': 262}
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="fig1t fig1d">',
           '<title id="fig1t">基督教两千年总家谱</title>',
           '<desc id="fig1d">从耶稣和使徒的教会开始：431年东方亚述教会分出，451年东方正统教会分出，1054年东西方教会分裂为东正教和天主教，1517年宗教改革从天主教中产生新教，1844年起新教中的复临运动在1863年组成基督复临安息日会。</desc>']
    bands = [(30, 313, '使徒与迫害'), (313, 590, '帝国教会'), (590, 1517, '中世纪'), (1517, 1800, '宗教改革'), (1800, 2026, '近现代')]
    for i, (a, b, lab) in enumerate(bands):
        out.append(f'<rect x="{X(a):.1f}" y="16" width="{X(b) - X(a):.1f}" height="{H - 62}" class="band{i % 2}"/>')
        out.append(text((X(a) + X(b)) / 2, 11, lab, 'tb', 'middle'))

    def branch(x0, y0, y1, xend, cls):
        return (f'<path d="M{x0:.1f} {y0} C{x0 + 9:.1f} {y0} {x0 + 3:.1f} {y1} {x0 + 14:.1f} {y1} L{xend:.1f} {y1}" class="ln {cls}"/>')
    out.append(f'<path d="M{X(30):.1f} {rows["trunk"]} L{X(1054):.1f} {rows["trunk"]}" class="ln f0"/>')
    out.append(branch(X(431), rows['trunk'], rows['east'], END, 'f1'))
    out.append(branch(X(451), rows['trunk'], rows['orient'], END, 'f2'))
    out.append(f'<path d="M{X(1054):.1f} {rows["trunk"]} L{END:.1f} {rows["trunk"]}" class="ln f3"/>')
    out.append(branch(X(1054), rows['trunk'], rows['cath'], END, 'f4'))
    out.append(branch(X(1517), rows['cath'], rows['prot'], END, 'f5'))
    out.append(branch(X(1844), rows['prot'], rows['sda'], END, 'f6'))
    for yr, y in [(431, rows['trunk']), (451, rows['trunk']), (1054, rows['trunk']), (1517, rows['cath']), (1844, rows['prot'])]:
        out.append(f'<circle cx="{X(yr):.1f}" cy="{y}" r="3.6" class="dot"/>')
    out.append(f'<circle cx="{X(30):.1f}" cy="{rows["trunk"]}" r="5.5" class="dot root"/>')
    # 名字：年份和名字写在一起，放在各自那条线的上方（复临在线的下方）
    def lab(x, y, yr, name, anchor='start'):
        return (f'<text x="{x:.1f}" y="{y}" class="tn" text-anchor="{anchor}"><tspan class="ty">{yr}</tspan> {esc(name)}</text>')
    out += [text(X(30) - 2, rows['trunk'] - 12, '耶稣与使徒', 'tn'),
            text(X(30) - 2, rows['trunk'] + 18, '一个大公教会', 'ts'),
            lab(X(431) + 18, rows['east'] - 7, '431', '东方亚述教会（唐代称“景教”）'),
            lab(X(451) + 18, rows['orient'] - 7, '451', '东方正统教会（科普特、亚美尼亚等）'),
            lab(X(1054) + 8, rows['ortho'] - 7, '1054', '东正教'),
            lab(X(1054) + 18, rows['cath'] - 7, '1054', '罗马天主教'),
            lab(X(1517) + 16, rows['prot'] - 20, '1517', '新教（更正教）'),
            text(X(1517) + 16, rows['prot'] - 7, '路德宗、长老会、浸信会……', 'ts'),
            text(END, rows['sda'] + 17, '基督复临安息日会', 'tn hi', 'end'),
            text(END, rows['sda'] + 30, '1844 复临运动 → 1863 组成', 'ts', 'end')]
    ay = H - 26
    out.append(f'<path d="M{X(30):.1f} {ay} L{END:.1f} {ay}" class="ax"/>')
    for yr, t in [(30, '公元30'), (451, '451'), (1054, '1054'), (1517, '1517'), (1844, '1844'), (2026, '今天')]:
        out.append(f'<path d="M{X(yr):.1f} {ay - 3} L{X(yr):.1f} {ay + 3}" class="ax"/>')
        out.append(text(X(yr), ay + 15, t, 'ta', 'middle' if 30 < yr < 2026 else ('start' if yr == 30 else 'end')))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 2：宗教改革以后的新教家谱 ----------------
PROT = [  # 名字, 开始年, 父, 家族色, 说明（显示在横条上）, 虚线
    ('天主教', 1500, None, 'f4', '', False),
    ('路德宗（信义会）', 1517, '天主教', 'f5', '1517 路德', False),
    ('改革宗', 1519, '天主教', 'f5', '1519 慈运理 · 1536 加尔文', False),
    ('重洗派 · 门诺会', 1525, '改革宗', 'f5', '1525 苏黎世', False),
    ('长老会', 1560, '改革宗', 'f5', '1560 诺克斯（苏格兰）', False),
    ('基督会（复原运动）', 1832, '长老会', 'f5', '1832', False),
    ('圣公会', 1534, '天主教', 'f5', '1534 英国', False),
    ('弟兄会', 1831, '圣公会', 'f5', '1831 达秘', False),
    ('清教徒 · 公理会', 1570, '圣公会', 'f5', '1620 五月花号', False),
    ('浸信会', 1609, '清教徒 · 公理会', 'f5', '1609 史密斯', False),
    ('安息日浸信会', 1650, '浸信会', 'f5', '1650年代 英国', False),
    ('复临运动', 1831, '浸信会', 'f6', '1831—1844 米勒耳', True),
    ('基督复临安息日会', 1863, '复临运动', 'f6', '1863', False),
    ('复临基督教会', 1860, '复临运动', 'f6', '1860', False),
    ('贵格会（公谊会）', 1652, '清教徒 · 公理会', 'f5', '1652 福克斯', False),
    ('卫理公会（循道宗）', 1738, '圣公会', 'f5', '1738 卫斯理', False),
    ('圣洁运动', 1867, '卫理公会（循道宗）', 'f5', '1867', False),
    ('五旬节运动', 1901, '圣洁运动', 'f5', '1901 · 1906', False),
    ('神召会', 1914, '五旬节运动', 'f5', '1914', False),
    ('真耶稣教会', 1917, '五旬节运动', 'f5', '1917 北京', False),
]
EXTRA = [('卫理公会（循道宗）', '复临运动', 1835), ('安息日浸信会', '基督复临安息日会', 1846)]   # 额外的影响（虚线）


def protestant():
    W = 400
    L, R = 132, 392            # 横条的范围：1500 年 → 2026 年
    top, rh = 34, 27
    H = top + rh * len(PROT) + 30

    def X(y):
        return L + (y - 1500) / (2026 - 1500) * (R - L)
    ys = {name: top + i * rh for i, (name, *_ ) in enumerate(PROT)}
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="fig2t fig2d">',
           '<title id="fig2t">宗教改革以后的新教家谱</title>',
           '<desc id="fig2d">每一横条是一个宗派，从它出现的年份开始；竖线连到它是从哪一个宗派分出来的。复临运动从浸信会和卫理公会的信徒中兴起，1863年组成基督复临安息日会，安息日的信仰来自安息日浸信会。</desc>']
    for yr in (1500, 1600, 1700, 1800, 1900, 2000):
        out.append(f'<path d="M{X(yr):.1f} {top - 14} L{X(yr):.1f} {H - 22}" class="grid"/>')
        out.append(text(X(yr), top - 18, str(yr), 'ta', 'middle'))
    # 先画所有竖线（在横条下面），再画横条，最后写字（字有底色描边，压住经过的竖线）
    for name, start, parent, fam, note, dashed in PROT:
        if parent:
            out.append(f'<path d="M{X(start):.1f} {ys[parent]} L{X(start):.1f} {ys[name]}" class="cn {fam}"/>')
    for a, b, yr in EXTRA:
        out.append(f'<path d="M{X(yr):.1f} {ys[a]} L{X(yr):.1f} {ys[b]}" class="cn f6 dash"/>')
    for name, start, parent, fam, note, dashed in PROT:
        y = ys[name]
        end = X(1844) if name == '复临运动' else R
        out.append(f'<path d="M{X(start):.1f} {y} L{end:.1f} {y}" class="bar {fam}{" dash" if dashed else ""}{" hi" if name == "基督复临安息日会" else ""}"/>')
    for a, b, yr in EXTRA:
        out.append(f'<circle cx="{X(yr):.1f}" cy="{ys[b]}" r="2.6" class="dot"/>')
    for name, start, parent, fam, note, dashed in PROT:
        y = ys[name]
        out.append(f'<circle cx="{X(start):.1f}" cy="{y}" r="3.4" class="dot"/>')
        out.append(text(L - 8, y + 4, name, 'tn hi' if name == '基督复临安息日会' else 'tn', 'end'))
        if note:
            tx = X(start) + 6
            anchor = 'start'
            if tx > R - 70:
                tx, anchor = X(start) - 6, 'end'
            out.append(text(tx, y - 6, note, 'ts halo', anchor))
    out.append(text(L, H - 6, '竖线：从哪里分出来　虚线：重要影响（人或信仰）', 'ts'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图 3：复临信仰的源流 ----------------
STREAMS = [
    ('唯独圣经', '宗教改革', '一切信仰都要用圣经来检验'),
    ('因信称义', '路德等改革家', '人得救全是本乎恩、也因着信'),
    ('信徒受浸 · 宗教自由', '浸信会、重洗派', '信了才受洗，全身入水；政教分离'),
    ('成圣 · 自由意志', '卫理公会', '恩典使人能选择、也能活出圣洁'),
    ('不立信条，只凭圣经', '基督徒联会', '怀雅各、贝约瑟原属此会'),
    ('研究预言 · 基督复临', '米勒耳运动', '但以理书、启示录；基督亲自再来'),
    ('第七日安息日', '安息日浸信会', '1844 年由瑞秋·奥克斯传给复临信徒'),
    ('人没有天然不死的灵魂', '斯托尔斯等', '死是睡觉，复活时才得永生'),
    ('天上的圣所 · 1844', '爱德森、克罗泽', '基督开始了天上至圣所的服务'),
    ('预言之灵 · 健康改良', '怀爱伦', '确认真理、劝勉教会、整合组织'),
]


def streams():
    W = 400
    bh, gap, top = 44, 8, 8
    H = top + len(STREAMS) * (bh + gap) + 4
    bw = 236
    nx, nw = 300, 96
    ny0, ny1 = H / 2 - 66, H / 2 + 66
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="fig3t fig3d">',
           '<title id="fig3t">复临信仰的源流</title>',
           '<desc id="fig3d">十道源流汇成基督复临安息日会的信仰：唯独圣经、因信称义、信徒受浸与宗教自由、成圣与自由意志、不立信条、预言研究与基督复临、第七日安息日、有条件的永生、天上的圣所、预言之灵与健康改良。</desc>']
    for i, (what, who, why) in enumerate(STREAMS):
        y = top + i * (bh + gap)
        cy = y + bh / 2
        ty = ny0 + 18 + i * (ny1 - ny0 - 36) / (len(STREAMS) - 1)
        out.append(f'<path d="M{bw + 2} {cy:.1f} C{bw + 34} {cy:.1f} {nx - 34} {ty:.1f} {nx} {ty:.1f}" class="flow"/>')
        out.append(f'<rect x="2" y="{y}" width="{bw}" height="{bh}" rx="9" class="box"/>')
        out.append(f'<rect x="2" y="{y}" width="5" height="{bh}" rx="2.5" class="{"f6" if i >= 5 else "f5"} fillc"/>')
        out.append(text(14, y + 18, what, 'tn'))
        out.append(text(bw - 6, y + 18, who, 'tw', 'end'))
        out.append(text(14, y + 36, why, 'ts'))
    out.append(f'<rect x="{nx}" y="{ny0:.1f}" width="{nw}" height="{ny1 - ny0:.1f}" rx="14" class="node f6 fillc"/>')
    for j, s in enumerate(['基督复临', '安息日会', '1863']):
        out.append(text(nx + nw / 2, (ny0 + ny1) / 2 - 14 + j * 22, s, 'tnode' if j < 2 else 'tnode2', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
