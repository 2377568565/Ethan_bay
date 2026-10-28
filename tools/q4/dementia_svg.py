# 健康栏目 06《老年痴呆》页面里的逻辑图（SVG，宽 400；颜色用页面的类，夜间模式自动变）
# 颜色的意思和前几篇一样：f1 青绿＝保护、能做的事；f6 红＝伤害、疾病；f4 金＝时间和警报；f5 紫＝药物和医院；f3 蓝＝中性的器官和阶段
from history_svg import text
from diabetes_svg import arrow, svg, bars
from osteo_svg import box, wrap


# ---------------- 图：越来越多的两层原因 ----------------
def more():
    W, H = 400, 312
    out = svg(W, H, 'adm', '病人越来越多，同龄人的风险却在降：两层原因',
              '左边：老人越来越多。2025 年末，中国 60 岁及以上的人有 3.23 亿，占总人口的 23.0%；65 岁及以上的有 2.24 亿，占 15.9%。'
              '2015—2018 年的全国调查里，60 岁以上的人约 6.0% 有痴呆，约 15.5% 有轻度认知障碍。老人多了，病人的人数就多了。'
              '右边：同龄人的风险在降。欧美 7 个人群研究跟踪了 1988—2015 年，同样年纪的人得痴呆的比例每十年少了约 13%。'
              '下面的结论：病人越来越多，主要是活到老年的人多了；老了不等于一定会痴呆。')
    cols = [(8, 'f4', '老人越来越多', [('60 岁以上', '3.23 亿 · 占 23.0%'), ('65 岁以上', '2.24 亿 · 占 15.9%'), ('其中有痴呆', '约 6.0%'), ('轻度认知障碍', '约 15.5%')],
             '人数 ↑', '2025 年末统计；2015—2018 全国调查'),
            (208, 'f1', '同龄人的风险在降', [('欧美 7 个人群', '1988—2015 年'), ('同样年纪的人', '每十年少约 13%'), ('男性', '约少 24%'), ('女性', '约少 8%')],
             '风险 ↓', 'Wolters 2020')]
    for x, c, title, rows, big, src in cols:
        out.append(box(x, 8, 184, 222, c))
        out.append(text(x + 92, 30, title, 'tn', 'middle'))
        for i, (a, b) in enumerate(rows):
            y = 42 + i * 36
            out.append(f'<rect x="{x + 12}" y="{y}" width="160" height="30" rx="9" class="{c} fillc"/>')
            out.append(text(x + 92, y + 13, a, 'tnode2 s', 'middle'))
            out.append(text(x + 92, y + 25, b, 'tnode2 b', 'middle'))
        out.append(text(x + 92, 208, big, 'tn', 'middle'))
        out.append(text(x + 92, 222, src, 'ts', 'middle'))
    out.append(f'<rect x="40" y="244" width="320" height="44" rx="14" class="f3 fillc"/>')
    out.append(text(200, 262, '病人越来越多，主要是活到老年的人多了', 'tnode2 b', 'middle'))
    out.append(text(200, 279, '老了，不等于一定会痴呆', 'tnode2 b', 'middle'))
    out.append(text(200, 305, '编者根据国家统计局、Jia 2020、Wolters 2020 整理', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：从正常到痴呆的台阶 ----------------
def stairs():
    W, H = 400, 318
    out = svg(W, H, 'ads', '从正常老化到痴呆：一段往下走的台阶',
              '从上到下是五级台阶。第一级正常老化：反应慢一点，提醒一下就记得，日子照常过。第二级主观认知下降：自己觉得记性差了，测验还正常。'
              '第三级轻度认知障碍：测验比同龄人差，家人看得出来，但买菜做饭管钱大体还能自己做；中国 60 岁以上约 15.5% 在这一级。'
              '第四级轻度痴呆：影响日常生活，忘了刚发生的事、迷路、管不了钱。第五级中重度痴呆：吃饭穿衣洗澡都要人帮。'
              '右边有一条往回走的箭头：查出能治好的原因（缺 B12、甲状腺、抑郁、药物等）治好了，有些人可以退回上一级。')
    steps = [('f1', '正常老化', '提醒一下就记得 · 日子照常过'),
             ('f3', '主观认知下降', '自己觉得差了 · 测验还正常'),
             ('f4', '轻度认知障碍', '测验比同龄人差 · 日子大体还能自理 · 中国 60 岁以上约 15.5%'),
             ('f6', '轻度痴呆', '影响日常生活 · 迷路、管不了钱'),
             ('f6', '中重度痴呆', '吃饭、穿衣、洗澡要人帮')]
    path = []
    for i, (c, a, b) in enumerate(steps):
        x, y = 8 + i * 22, 10 + i * 56
        out.append(f'<rect x="{x}" y="{y}" width="{322 - x}" height="48" rx="10" class="{c} fillc" opacity=".16"/>')
        out.append(f'<rect x="{x + 6}" y="{y + 6}" width="104" height="36" rx="9" class="{c} fillc"/>')
        out.append(text(x + 58, y + 29, a, 'tnode2 b', 'middle'))
        lines = wrap(b, 318 - x - 124)[:2]
        for k, ln in enumerate(lines):
            out.append(text(x + 118, y + 28 + (k - (len(lines) - 1) / 2) * 15, ln, 'tw'))
    out.append(arrow(340, 250, 340, 40))
    for k, t in enumerate(('能治好的', '原因', '治好了', '可以', '退回来')):
        out.append(text(368, 120 + k * 14, t, 'ts', 'middle'))
    out.append(text(200, 308, '编者整理的示意；判断要请医生做测验和检查', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：阿尔茨海默病的时间线 ----------------
def brain():
    W, H = 400, 290
    out = svg(W, H, 'adb', '阿尔茨海默病：脑子里的改变，比症状早很多年',
              '横轴是时间，大约跨二十多年。这是示意图，不是某一项研究的真实数据。最先开始的是β-淀粉样蛋白在神经细胞外面越积越多，形成斑块；'
              '接着是神经细胞里面的 tau 蛋白变形，缠成一团；然后神经细胞之间的连接减少、细胞死去，海马和大脑萎缩。'
              '前面很多年，人看起来还正常，因为大脑的储备还能顶上。等到储备用完，才出现轻度认知障碍，然后是痴呆。'
              '新的抗体药清除淀粉样蛋白，只用在早期；而管血压、听力、活动这些预防的事，要在症状出现以前很多年就开始。')
    x0, x1 = 30, 386
    rows = [('f4', 'β-淀粉样蛋白斑块', 0.00, 0.95), ('f5', 'tau 缠结', 0.25, 0.95), ('f6', '神经细胞减少、脑萎缩', 0.45, 0.95)]
    for i, (c, lab, a, b) in enumerate(rows):
        y = 18 + i * 40
        xa, xb = x0 + (x1 - x0) * a, x0 + (x1 - x0) * b
        out.append(f'<rect x="{xa:.1f}" y="{y}" width="{xb - xa:.1f}" height="26" rx="13" class="{c} fillc"/>')
        out.append(text(xa + 10, y + 17, lab, 'tnode2 b'))
    # 症状线
    yS = 160
    out.append(f'<path d="M{x0} {yS} L{x1} {yS}" class="ax"/>')
    xm = x0 + (x1 - x0) * .62
    xd = x0 + (x1 - x0) * .80
    out.append(f'<rect x="{x0}" y="{yS - 22}" width="{xm - x0:.1f}" height="18" rx="9" class="f1 fillc" opacity=".55"/>')
    out.append(text((x0 + xm) / 2, yS - 9, '看起来正常：大脑的储备还能顶上', 'tnode2 s', 'middle'))
    out.append(f'<rect x="{xm:.1f}" y="{yS - 22}" width="{xd - xm:.1f}" height="18" rx="9" class="f4 fillc"/>')
    out.append(text((xm + xd) / 2, yS - 9, '轻度认知障碍', 'tnode2 s', 'middle'))
    out.append(f'<rect x="{xd:.1f}" y="{yS - 22}" width="{x1 - xd:.1f}" height="18" rx="9" class="f6 fillc"/>')
    out.append(text((xd + x1) / 2, yS - 9, '痴呆', 'tnode2 s', 'middle'))
    out.append(text(x0, yS + 16, '早', 'ta'))
    out.append(text(x1, yS + 16, '晚（约二十多年）', 'ta', 'end'))
    # 两个时机
    out.append(box(8, 190, 186, 70, 'f1'))
    out.append(text(101, 210, '预防：越早越好', 'tn', 'middle'))
    out.append(text(101, 228, '中年管好血压、听力', 'tw', 'middle'))
    out.append(text(101, 245, '保护的是二十年后的大脑', 'tw', 'middle'))
    out.append(box(206, 190, 186, 70, 'f5'))
    out.append(text(299, 210, '新抗体药：只用在早期', 'tn', 'middle'))
    out.append(text(299, 228, '先证实有淀粉样蛋白', 'tw', 'middle'))
    out.append(text(299, 245, '病越重，越来不及', 'tw', 'middle'))
    out.append(text(200, 282, '编者整理的示意，不是真实数据', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：十四个可以改变的因素 ----------------
def fourteen():
    return bars('ad14', '十四个可以改变的危险因素，各约占痴呆的多少',
                '《柳叶刀》痴呆委员会 2024 年的估计，十四个因素加起来约占全世界痴呆的 45%。早年：受教育少约 5%。'
                '中年：听力下降约 7%，坏胆固醇（低密度脂蛋白）偏高约 7%，抑郁约 3%，头部外伤约 3%，活动少、糖尿病、吸烟、高血压各约 2%，肥胖、喝酒过量各约 1%。'
                '老年：和人来往少约 5%，空气污染约 3%，视力下降没有治约 2%。这是根据观察研究对一大群人的估计，不是对一个人的保证。',
                [('早年', [('受教育少', 5, 'f3')]),
                 ('中年（四五十岁）', [('听力下降', 7, 'f4'), ('坏胆固醇偏高', 7, 'f4'), ('抑郁', 3, 'f4'), ('头部外伤', 3, 'f4'),
                                    ('活动少', 2, 'f4'), ('糖尿病', 2, 'f4'), ('吸烟', 2, 'f4'), ('高血压', 2, 'f4'), ('肥胖', 1, 'f4'), ('喝酒过量', 1, 'f4')]),
                 ('老年', [('和人来往少', 5, 'f6'), ('空气污染', 3, 'f6'), ('视力下降没有治', 2, 'f6')])],
                '%', 8, '合计约 45%（估计）· 数据：Livingston 2024')


# ---------------- 图：两项降压试验 ----------------
def bp():
    W, H = 400, 300
    out = svg(W, H, 'adp', '降血压能少得痴呆吗：两项随机试验',
              '上面是美国的 SPRINT 研究：9,361 名有高血压的人，收缩压降到 120 以下的一组，和降到 140 以下的一组比，轻度认知障碍少了约 19%，'
              '痴呆少了约 17% 但还不够有把握，因为试验提前停了。下面是中国农村的试验：326 个村、33,995 名血压没控制好的人，'
              '村医按简单的步骤开药加药，四年里收缩压多降了约 22，痴呆少了约 15%，严重不良事件少了约 6%。')
    blocks = [(8, 'SPRINT（美国，2019）', '9,361 人 · 目标 120 对 140',
               [('轻度认知障碍', 19, True), ('痴呆（不够有把握）', 17, False)]),
              (150, '中国农村（2025）', '326 个村、33,995 人 · 村医强化降压 4 年 · 收缩压多降约 22',
               [('痴呆', 15, True), ('严重不良事件', 6, True)])]
    for y, title, sub, items in blocks:
        out.append(box(8, y, 384, 132, 'f1'))
        out.append(text(20, y + 22, title, 'tn'))
        for k, ln in enumerate(wrap(sub, 350)[:2]):
            out.append(text(20, y + 40 + k * 15, ln, 'tw'))
        for i, (lab, v, sig) in enumerate(items):
            yy = y + 68 + i * 30
            out.append(text(150, yy + 13, lab, 'tw', 'end'))
            w = 200 * v / 25
            cls = 'f1 fillc' if sig else 'f1 fillc" opacity=".45'
            out.append(f'<rect x="158" y="{yy}" width="{w:.1f}" height="18" rx="5" class="{cls}"/>')
            out.append(text(164 + w, yy + 13, f'少了约 {v}%', 'tw'))
    out.append(text(200, 294, '浅色的条＝差别还不够有把握 · 数据：Williamson 2019、He 2025', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：预防办法的证据台阶 ----------------
def ladder():
    W, H = 400, 352
    out = svg(W, H, 'adl', '预防痴呆的办法，证据有多硬',
              '从上到下四层。第一层，随机试验证明能少得痴呆：降血压（中国农村试验痴呆少约 15%）。'
              '第二层，随机试验里认知成绩好一点，还没证明少得痴呆：多管齐下的生活方式（芬兰 FINGER、美国 POINTER）、配助听器（只在高风险老人里可能有帮助）、反应速度训练（有争议）。'
              '第三层，只有观察研究：多走路、睡够觉、白内障手术、和人来往、少用抗胆碱药和安眠药、带状疱疹疫苗。'
              '第四层，试验做了却没看到效果：银杏防痴呆、MIND 饮食试验、司美格鲁肽治早期阿尔茨海默病。')
    tiers = [('f1', '随机试验：少得痴呆', '降血压'),
             ('f3', '随机试验：成绩好一点', '多管齐下的生活方式 · 助听器（高风险老人）· 反应速度训练（有争议）'),
             ('f4', '只有观察研究', '多走路 · 睡够觉 · 白内障手术 · 和人来往 · 少用伤脑的药 · 带状疱疹疫苗'),
             ('f6', '试验做了，没看到效果', '银杏防痴呆 · MIND 饮食试验 · 司美格鲁肽治早期阿尔茨海默病')]
    y = 8
    for i, (c, head, s) in enumerate(tiers):
        h = 72 if i else 58
        out.append(box(8, y, 384, h, c))
        out.append(f'<rect x="16" y="{y + 8}" width="118" height="{h - 16}" rx="10" class="{c} fillc"/>')
        for k, ln in enumerate(wrap(head.replace('：', ' · '), 100, 11)[:3]):
            out.append(text(75, y + h / 2 + 4 + (k - (len(wrap(head.replace('：', ' · '), 100, 11)[:3]) - 1) / 2) * 15, ln, 'tnode2 b', 'middle'))
        lines = wrap(s, 240)[:3]
        for k, ln in enumerate(lines):
            out.append(text(144, y + h / 2 + 4 + (k - (len(lines) - 1) / 2) * 17, ln, 'tw'))
        y += h + 8
    out.append(text(200, y + 12, '越往上，越有把握；', 'tw', 'middle'))
    out.append(text(200, y + 30, '下面几层的事，对血管、心情、防跌倒多半也有好处', 'tw', 'middle'))
    out.append(text(200, y + 52, '编者根据本篇引用的研究整理', 'ts', 'middle'))
    out.append('</svg>')
    out[0] = out[0].replace(f'0 0 {W} {H}', f'0 0 {W} {y + 60}')
    return '\n'.join(out)


# ---------------- 图：新抗体药的好处和风险 ----------------
def antibody():
    W, H = 400, 330
    out = svg(W, H, 'ada', '两种新抗体药：好处有多大，风险有多大',
              '病情评分满分 18 分，分数越高越重。仑卡奈单抗的试验，18 个月里安慰剂组加重了 1.66 分，用药组加重了 1.21 分，差 0.45 分。'
              '多奈单抗的试验，76 周里安慰剂组加重了 2.42 分，用药组加重了 1.72 分，差约 0.7 分。病情加重的速度慢了约四分之一到三成。'
              '风险：脑部磁共振上出现水肿或渗出，仑卡奈单抗约 12.6%，多奈单抗约 24%（安慰剂约 2%）；打针时的反应分别约 26% 和 9%。')
    out.append(text(8, 22, '病情评分加重了多少（满分 18 分，越高越重）', 'tn'))
    rows = [('仑卡奈单抗 18 个月', 1.66, 1.21), ('多奈单抗 76 周', 2.42, 1.72)]
    y = 36
    for lab, p, d in rows:
        out.append(text(8, y + 12, lab, 'tw'))
        for j, (name, v, c) in enumerate((('安慰剂', p, 'f6'), ('用药', d, 'f5'))):
            yy = y + 18 + j * 22
            w = 220 * v / 2.6
            out.append(text(84, yy + 12, name, 'tw', 'end'))
            out.append(f'<rect x="92" y="{yy}" width="{w:.1f}" height="16" rx="5" class="{c} fillc"/>')
            out.append(text(98 + w, yy + 12, f'{v:g} 分', 'tw'))
        y += 70
    out.append(text(200, y + 6, '加重的速度慢了约四分之一到三成：是“慢一点”，不是“好起来”', 'tn', 'middle'))
    y += 22
    out.append(box(8, y, 384, 92, 'f4'))
    out.append(text(20, y + 20, '风险', 'tn'))
    risks = [('脑水肿或渗出（磁共振上）', '约 12.6%', '约 24%'), ('打针时的反应', '约 26%', '约 9%')]
    out.append(text(272, y + 20, '仑卡奈', 'tw', 'middle'))
    out.append(text(350, y + 20, '多奈', 'tw', 'middle'))
    for i, (a, b, c) in enumerate(risks):
        yy = y + 42 + i * 20
        out.append(text(20, yy, a, 'tw'))
        out.append(text(272, yy, b, 'tn', 'middle'))
        out.append(text(350, yy, c, 'tn', 'middle'))
    out.append(text(20, y + 84, '只用于早期、证实有淀粉样蛋白的病人；要定期做磁共振', 'ts'))
    out.append(text(200, H - 8, '数据：van Dyck 2023（卫材、渤健资助）、Sims 2023（礼来开展）', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：一生的功课 ----------------
def ages():
    W, H = 400, 372
    out = svg(W, H, 'adg', '保护大脑是一生的功课',
              '从上到下是五个阶段。孩子和年轻人：多读书，骑车戴头盔，耳机音量别太大，不吸烟。'
              '四五十岁：管好血压、血脂、血糖，听力下降就查、该配助听器就配，戒烟少酒，多运动，睡够觉，抑郁要治。'
              '六十五岁以上：管好血压，查听力和视力，白内障该做就做，多和人来往，学新东西，请医生审一遍药，防跌倒。'
              '已经有轻度认知障碍或早期痴呆：先查能治好的原因，在医生指导下用药，趁早安排钱和照护，坚持活动和交往。'
              '照顾的人：分担、喘口气、学照护、照顾好自己。')
    stages = [('f1', '孩子、年轻人', '存储备', '多读书 · 骑车戴头盔 · 耳机别太大声 · 不吸烟'),
              ('f4', '四五十岁', '最关键', '管好血压血脂血糖 · 听力下降就查 · 戒烟少酒 · 多运动、睡够觉'),
              ('f3', '六十五岁以上', '多来往', '查听力视力 · 白内障该做就做 · 学新东西 · 请医生审药 · 防跌倒'),
              ('f5', '已经有症状', '早查早安排', '先查能治好的原因 · 遵医嘱用药 · 安排钱和照护 · 坚持活动'),
              ('f6', '照顾的人', '也要被照顾', '家人分担 · 每周喘口气 · 学照护 · 顾好自己的身体')]
    y = 8
    for c, age, verb, s in stages:
        out.append(box(8, y, 384, 62, c))
        out.append(f'<rect x="16" y="{y + 9}" width="92" height="44" rx="10" class="{c} fillc"/>')
        out.append(text(62, y + 28, age, 'tnode2 b', 'middle'))
        out.append(text(62, y + 44, verb, 'tnode2 s', 'middle'))
        for k, ln in enumerate(wrap(s, 266)[:2]):
            out.append(text(118, y + 28 + k * 18, ln, 'tw'))
        y += 70
    out.append(text(200, 366, '编者根据本篇引用的研究整理', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
