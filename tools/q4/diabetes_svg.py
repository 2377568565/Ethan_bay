# 健康栏目 01《糖尿病》页面里的逻辑图（SVG，宽 400；颜色用页面的类，夜间模式自动变）
# 这一页颜色的意思固定：f1 青绿＝保护、能做的事；f6 红＝伤害、疾病；f4 金＝胰岛素；f5 紫＝药物；f3 蓝＝中性的器官和阶段
from history_svg import text, esc


def arrow(x1, y1, x2, y2, cls='flow', head=6):
    """直线箭头（箭头画成小三角）"""
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - head * math.cos(a), y2 - head * math.sin(a)
    l = (hx + head * .55 * math.sin(a), hy - head * .55 * math.cos(a))
    r = (hx - head * .55 * math.sin(a), hy + head * .55 * math.cos(a))
    return (f'<path d="M{x1:.1f} {y1:.1f} L{hx:.1f} {hy:.1f}" class="{cls}"/>'
            f'<path d="M{x2:.1f} {y2:.1f} L{l[0]:.1f} {l[1]:.1f} L{r[0]:.1f} {r[1]:.1f} Z" class="ahd"/>')


def node(x, y, w, h, cls, t1, t2=''):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="9" class="{cls} fillc"/>',
           text(x + w / 2, y + (h / 2 + 4 if not t2 else h / 2 - 2), t1, 'tnode2 b', 'middle')]
    if t2:
        out.append(text(x + w / 2, y + h / 2 + 11, t2, 'tnode2 s', 'middle'))
    return ''.join(out)


def svg(W, H, tid, title, desc):
    return [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="{tid}t {tid}d">',
            f'<title id="{tid}t">{esc(title)}</title>', f'<desc id="{tid}d">{esc(desc)}</desc>']


# ---------------- 图：血糖从哪里来，到哪里去 ----------------
def pool():
    W, H = 400, 300
    out = svg(W, H, 'dmp', '血糖从哪里来、到哪里去：胰岛素是开门的钥匙',
              '血液里的糖只有大约一茶匙，却时时刻刻在进出。进来的有两路：吃进去的食物经过肠道吸收；空腹和夜里由肝脏自己造糖、放糖。'
              '出去的有四路：饭后最大的去处是肌肉，其次是肝脏和脂肪，这三处都要胰岛素来开门；大脑用糖不需要胰岛素。'
              '胰岛素由胰腺里的β细胞分泌。2 型糖尿病有两个环节出问题：门锁生了锈（胰岛素抵抗），钥匙也不够（β细胞分泌不足）。')
    # 中间的血液
    out.append('<rect x="148" y="104" width="104" height="92" rx="46" class="f6 fillc" opacity=".18"/>')
    out.append('<rect x="148" y="104" width="104" height="92" rx="46" class="cn f6" style="--c:var(--c6)"/>')
    out.append(text(200, 140, '血液里的糖', 'tn', 'middle'))
    out.append(text(200, 156, '全身只有约一茶匙', 'ts', 'middle'))
    out.append(text(200, 170, '（约 4—5 克）', 'ts', 'middle'))
    # 进
    out.append(node(8, 86, 100, 38, 'f3', '吃进的食物', '肠道吸收'))
    out.append(node(8, 176, 100, 38, 'f3', '肝脏造糖、放糖', '空腹和夜里'))
    out.append(arrow(110, 105, 150, 135))
    out.append(arrow(110, 195, 150, 168))
    out.append(text(58, 80, '进', 'ty', 'middle'))
    # 出
    outs = [('肌肉', '饭后最大的去处', 56, True), ('肝脏', '存成肝糖原', 106, True), ('脂肪', '存成脂肪', 156, True), ('大脑', '不用钥匙', 206, False)]
    for t1, t2, y, key in outs:
        out.append(node(292, y, 100, 38, 'f1' if key else 'f3', t1, t2))
        out.append(arrow(252, 150, 290, y + 19))
        if key:
            out.append(f'<circle cx="282" cy="{y + 19}" r="7" class="f4 fillc"/>')
    out.append(text(342, 50, '出', 'ty', 'middle'))
    # 胰岛素
    out.append(node(150, 16, 100, 38, 'f4', '胰腺 β 细胞', '分泌胰岛素'))
    out.append(f'<path d="M250 35 C300 35 282 70 282 70" class="flow dash"/>')
    out.append(f'<circle cx="300" cy="24" r="7" class="f4 fillc"/>')
    out.append(text(312, 28, '＝胰岛素“开门”', 'tw'))
    out.append(text(200, 236, '2 型糖尿病：两个环节一起出问题', 'tn', 'middle'))
    out.append(node(14, 248, 180, 40, 'f6', '门锁生锈：胰岛素抵抗', '肌肉、肝脏对钥匙不灵'))
    out.append(node(206, 248, 180, 40, 'f6', '钥匙不够：β 细胞乏力', '分泌赶不上需要'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：2 型糖尿病的自然病程，和三个可以出手的时机 ----------------
def course():
    W, H = 400, 318
    out = svg(W, H, 'dmc', '十几年的一条路：2 型糖尿病怎样一步步来，哪里可以出手',
              '从左到右是常见的病程：先是血糖正常；接着出现胰岛素抵抗，β细胞加班多分泌胰岛素，血糖还能维持正常，这一段往往持续多年；'
              '然后β细胞跟不上，进入糖尿病前期；再往下就是 2 型糖尿病，血糖越来越难控制；多年后出现眼、肾、神经和心脑血管并发症。'
              '三个出手的时机：糖尿病前期以前，改变生活方式可以预防或推迟（大庆研究、美国糖尿病预防计划）；确诊早期大幅减重，相当一部分人可以缓解（英国 DiRECT 研究）；'
              '任何阶段，规范治疗都能减少并发症（英国前瞻性糖尿病研究等）。')
    stages = [('血糖正常', '', 'f1'), ('胰岛素抵抗', 'β细胞加班，血糖还正常', 'f3'), ('糖尿病前期', '空腹或饭后偏高', 'f4'),
              ('2 型糖尿病', 'β细胞越来越累', 'f6'), ('并发症', '眼、肾、神经、心脑血管', 'f6')]
    y = 14
    for i, (t1, t2, c) in enumerate(stages):
        out.append(node(20, y, 150, 40, c, t1, t2))
        if i < len(stages) - 1:
            out.append(arrow(95, y + 41, 95, y + 55))
        y += 56
    out.append(text(95, y + 6, '常常要十几年；前面几段没有感觉', 'ts', 'middle'))
    # 右边三个时机
    tags = [[1], [1], [1], [2, 3], [3]]          # 每个阶段旁边标出可以出手的时机
    for i, ts in enumerate(tags):
        for j, n in enumerate(ts):
            cx, cy = 180 + j * 0, 34 + i * 56 + (j - (len(ts) - 1) / 2) * 16
            out.append(f'<circle cx="{cx}" cy="{cy:.1f}" r="7" class="f1 fillc"/>')
            out.append(text(cx, cy + 3.5, str(n), 'tnode2 s', 'middle'))
    boxes = [(64, '① 预防或推迟', '改变饮食、多动、减重', '大庆研究、DPP、芬兰研究'),
             (166, '② 争取缓解', '确诊早期，大幅减重', 'DiRECT：病程越短越有望'),
             (250, '③ 减少并发症', '规范用药，管好血压血脂', 'UKPDS 等长期研究')]
    for y0, a, b, c in boxes:
        out.append(f'<rect x="200" y="{y0}" width="190" height="56" rx="10" class="box"/>')
        out.append(f'<rect x="200" y="{y0}" width="6" height="56" rx="3" class="f1 fillc"/>')
        out.append(text(214, y0 + 18, a, 'tn'))
        out.append(text(214, y0 + 34, b, 'tw'))
        out.append(text(214, y0 + 48, c, 'ts'))
    out.append(text(295, 40, '可以出手的三个时机', 'ty', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：为什么年纪大了容易得——几股水流进同一个杯子 ----------------
def converge():
    W, H = 400, 330
    out = svg(W, H, 'dmv', '为什么年纪越大越容易得：几股水流进同一个杯子',
              '左边是随年龄来的变化：肌肉变少；肌肉里的线粒体变弱，脂肪钻进肌肉；腹部、肝脏、胰腺的脂肪变多；β细胞的储备和对肠道激素的反应变差。'
              '右边是几十年生活习惯的累积：睡得少、坐得多、吃得精、喝甜饮料、吸烟。它们都流进同一个杯子。每个人杯子的大小（个人能承受的阈值）不同，'
              '和遗传、出生前后的营养有关，东亚人的杯子平均偏小。水一旦漫过杯口，血糖就升高。年纪本身不是病因，而是让杯子里的水一点点涨起来的时间。'
              '这张图是编者根据本页引用的研究整理的示意。')
    left = ['肌肉变少', '线粒体变弱', '肝、胰、腹部脂肪变多', 'β细胞储备下降']
    right = ['睡得少', '坐得多', '吃得精、甜饮料', '吸烟']
    out.append(text(80, 16, '随年龄来的变化', 'ty', 'middle'))
    out.append(text(320, 16, '几十年的生活习惯', 'ty', 'middle'))
    for i, t in enumerate(left):
        y = 26 + i * 34
        out.append(node(8, y, 144, 26, 'f6', t))
        out.append(arrow(152, y + 13, 166 + i * 6, 168))
    for i, t in enumerate(right):
        y = 26 + i * 34
        out.append(node(248, y, 144, 26, 'f6', t))
        out.append(arrow(248, y + 13, 234 - i * 6, 168))
    # 杯子
    out.append('<path d="M150 176 L162 300 L238 300 L250 176" class="cn f3" style="--c:var(--c3);stroke-width:2.4"/>')
    out.append('<path d="M156 226 L244 226 L238 300 L162 300 Z" class="f3 fillc" opacity=".22"/>')
    out.append('<path d="M146 190 L254 190" class="cn f6 dash" style="--c:var(--c6)"/>')
    out.append(text(258, 194, '杯口＝个人阈值', 'tw'))
    out.append(text(200, 252, '代谢负担', 'tn', 'middle'))
    out.append(text(200, 268, '一年年涨上来', 'ts', 'middle'))
    out.append(text(52, 220, '杯子大小：', 'tw'))
    out.append(text(52, 234, '遗传、出生前后', 'ts'))
    out.append(text(52, 247, '的营养、种族', 'ts'))
    out.append(text(52, 260, '（东亚人偏小）', 'ts'))
    out.append(text(300, 236, '漫过杯口', 'tw'))
    out.append(text(300, 250, '＝血糖升高', 'tn'))
    out.append(text(200, 322, '编者整理的示意：年纪不是病因，而是让水慢慢涨上来的时间', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：降糖药各在哪里用力 ----------------
def drugs():
    W, H = 400, 300
    out = svg(W, H, 'dmd', '降糖药各在哪里用力：管住血糖，但不负责清走多余的脂肪',
              '二甲双胍主要让肝脏少放糖，也改善身体对胰岛素的反应；磺脲类药让β细胞多分泌胰岛素；GLP-1 受体激动剂和 DPP-4 抑制剂借着肠道激素，按血糖高低促进胰岛素分泌、减少胰高糖素，'
              'GLP-1 受体激动剂还让人吃得少、体重下降；SGLT2 抑制剂让肾脏把多余的糖从尿里排出去；胰岛素直接补上钥匙。'
              '它们都在“管血糖”，其中几类还能减少心脏和肾脏的病；但是堵在肝脏和胰腺里的多余脂肪，主要要靠减轻体重来清走。')
    org = [('肝脏', 14, '二甲双胍', '让肝脏少放糖'), ('胰腺 β 细胞', 74, '磺脲类', '逼β细胞多分泌'),
           ('肠道激素', 134, 'GLP-1 类、DPP-4 抑制剂', '按需促分泌；前者还减重'), ('肾脏', 194, 'SGLT2 抑制剂', '把多余的糖排到尿里')]
    for name, y, d, how in org:
        out.append(node(8, y, 110, 46, 'f3', name))
        out.append(arrow(186, y + 23, 120, y + 23))
        out.append(f'<rect x="188" y="{y}" width="204" height="46" rx="9" class="box"/>')
        out.append(f'<rect x="188" y="{y}" width="6" height="46" rx="3" class="f5 fillc"/>')
        out.append(text(202, y + 19, d, 'tn'))
        out.append(text(202, y + 35, how, 'tw'))
    out.append(node(8, 254, 110, 38, 'f4', '胰岛素', '直接补上钥匙'))
    out.append(f'<rect x="132" y="248" width="260" height="48" rx="10" class="box"/>')
    out.append(f'<rect x="132" y="248" width="6" height="48" rx="3" class="f1 fillc"/>')
    out.append(text(146, 266, '肝脏、胰腺里多余的脂肪：', 'tn'))
    out.append(text(146, 284, '主要靠减轻体重来清走（见“缓解”一章）', 'tw'))
    out.append('</svg>')
    return '\n'.join(out)


def bars(tid, title, desc, groups, unit, maxv, note):
    """横向条形图：groups = [(组名, [(标签, 数值, 类), …]), …]"""
    W = 400
    rows = sum(len(g[1]) for g in groups)
    H = 20 + len(groups) * 26 + rows * 22 + 26
    out = svg(W, H, tid, title, desc)
    x0, x1, y = 128, 350, 14
    for g in groups:
        gname, items = g[0], g[1]
        u = g[2] if len(g) > 2 else unit
        out.append(text(8, y + 12, gname, 'tn'))
        y += 22
        gm = maxv or max(v for _, v, _ in items) * 1.1      # maxv 为 None：每组按自己的最大值画
        for lab, v, cls in items:
            w = (x1 - x0) * v / gm
            out.append(text(x0 - 6, y + 11, lab, 'tw', 'end'))
            out.append(f'<rect x="{x0}" y="{y + 2}" width="{max(w, 1.5):.1f}" height="13" rx="4" class="{cls} fillc"/>')
            out.append(text(x0 + w + 5, y + 12, f'{v:g}{u}', 'tw'))
            y += 22
        y += 4
    out.append(text(W / 2, H - 8, note, 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：DiRECT——减掉的体重越多，缓解的人越多 ----------------
def remit():
    return bars('dmr', '减掉的体重越多，缓解的人越多（DiRECT 研究，12 个月）',
                '英国 DiRECT 研究 12 个月时，按体重变化分组看糖尿病缓解的比例：体重增加的 76 人中没有人缓解；减重 0—5 公斤的 7%；5—10 公斤的 34%；10—15 公斤的 57%；减重 15 公斤以上的 86%。'
                '缓解的定义是停用所有降糖药后，糖化血红蛋白低于 6.5%。参加的人病程都在 6 年以内、没有用胰岛素。',
                [('12 个月时体重的变化', [('体重增加', 0, 'f6'), ('减 0—5 公斤', 7, 'f3'), ('减 5—10 公斤', 34, 'f3'),
                                     ('减 10—15 公斤', 57, 'f1'), ('减 15 公斤以上', 86, 'f1')])],
                '%', 100, '数据：Lean 等，《柳叶刀》2018（病程 6 年内、未用胰岛素的病人）')


# ---------------- 图：三个预防试验 ----------------
def prevent():
    return bars('dmx', '生活方式能不能预防？三个随机对照试验的结果',
                '中国大庆研究（糖耐量受损的人，6 年累计发病）：对照组 67.7%，饮食组 43.8%，运动组 41.1%，饮食加运动组 46.0%。'
                '美国糖尿病预防计划（平均 2.8 年，每 100 人每年的发病数）：安慰剂 11.0，二甲双胍 7.8，生活方式 4.8。'
                '芬兰糖尿病预防研究（4 年累计发病）：对照组 23%，生活方式组 11%。三个研究的人群、时间和计算方法不同，只能各自比较，不能横向比较。',
                [('中国大庆研究（6 年累计发病）', [('对照组', 67.7, 'f6'), ('饮食组', 43.8, 'f1'), ('运动组', 41.1, 'f1'), ('饮食加运动', 46.0, 'f1')], '%'),
                 ('美国 DPP（每百人每年发病）', [('安慰剂', 11.0, 'f6'), ('二甲双胍', 7.8, 'f5'), ('生活方式', 4.8, 'f1')]),
                 ('芬兰 DPS（4 年累计发病）', [('对照组', 23, 'f6'), ('生活方式', 11, 'f1')], '%')],
                '', None, '每组各自按比例画，组与组之间不能比较；大庆、芬兰是 %，DPP 是每百人每年')
