# 健康栏目 04《中风》页面里的逻辑图（SVG，宽 400；颜色用页面的类，夜间模式自动变）
# 颜色的意思和前三篇一样：f1 青绿＝保护、能做的事；f6 红＝伤害、疾病；f4 金＝时间和警报；f5 紫＝药物和医院；f3 蓝＝中性的器官和阶段
from history_svg import text
from diabetes_svg import arrow, node, svg, bars


# ---------------- 图：两种中风 ----------------
def two():
    W, H = 400, 300
    out = svg(W, H, 'stt', '两种中风：血管堵了，或者血管破了',
              '左边是缺血性中风（脑梗死）：血块或斑块把脑子里的一根血管堵住，下游的脑组织得不到血。堵住的中心很快坏死；'
              '周围一圈叫“半暗带”，还靠旁边的小血管勉强供着血，暂时没死，是抢救的对象。右边是出血性中风：脑子里的血管破了，血流进脑组织（脑出血），'
              '或流到脑子表面的腔隙里（蛛网膜下腔出血）。两种中风的治疗正好相反：一种要把血管打通，一种要止血、降压。'
              '只有做了脑部 CT 或核磁共振才能分清，所以在医院做检查以前，不要给病人乱吃药。中国 2020 年住院的中风病人里，约八成是缺血性的。')
    for x0, title, sub, cls in ((8, '缺血性中风（脑梗死）', '血管堵了', 'f3'), (208, '出血性中风', '血管破了', 'f6')):
        out.append(f'<rect x="{x0}" y="8" width="184" height="236" rx="12" class="cn {cls}" style="--c:var(--{"c3" if cls == "f3" else "c6"});fill:none"/>')
        out.append(text(x0 + 92, 30, title, 'tn', 'middle'))
        out.append(text(x0 + 92, 46, sub, 'ts', 'middle'))
    # 左：一根血管被堵，下游一片
    out.append('<path d="M24 92 C60 92 70 92 98 100" class="cn f3" style="--c:var(--c3);stroke-width:7;fill:none"/>')
    out.append('<circle cx="100" cy="101" r="7" class="f6 fillc"/>')
    out.append(text(100, 84, '血块', 'tw', 'middle'))
    out.append('<path d="M107 104 C126 112 140 124 150 140" class="cn dash" style="--c:var(--muted);stroke-width:4;fill:none"/>')
    out.append('<ellipse cx="128" cy="168" rx="58" ry="44" class="f4 fillc" opacity=".35"/>')
    out.append('<ellipse cx="128" cy="168" rx="28" ry="21" class="f6 fillc"/>')
    out.append(text(128, 172, '核心：坏死', 'tnode2 b', 'middle'))
    out.append(text(128, 206, '半暗带：还能救', 'tw', 'middle'))
    out.append(text(100, 232, '治疗：尽快打通血管', 'ts', 'middle'))
    # 右：血管破了
    out.append('<path d="M224 92 C262 92 272 92 300 100 C320 106 330 118 340 132" class="cn f6" style="--c:var(--c6);stroke-width:7;fill:none"/>')
    out.append('<path d="M300 100 l-6 -10 l12 4 z" class="f6 fillc"/>')
    out.append('<ellipse cx="300" cy="160" rx="40" ry="30" class="f6 fillc" opacity=".55"/>')
    out.append(text(300, 164, '流出的血', 'tw', 'middle'))
    out.append(text(300, 204, '压迫、损伤脑组织', 'tw', 'middle'))
    out.append(text(300, 232, '治疗：止血、降压，必要时手术', 'ts', 'middle'))
    out.append(text(200, 266, '两种的治疗正好相反——只有脑部 CT 或核磁共振才能分清', 'tw', 'middle'))
    out.append(text(200, 288, '中国 2020 年住院病人：缺血性约 82%，脑出血约 15%，蛛网膜下腔出血约 3%', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：中风 120 ----------------
def onetwozero():
    W, H = 400, 262
    out = svg(W, H, 'st120', '认出中风：“中风 120”，再加上走路不稳、眼睛看不清',
              '“中风 120”是中国医生为普通人设计的口诀：1 看 1 张脸，口角歪不歪、两边对不对称；2 查 2 只胳膊，平举时有没有一边无力、往下掉；'
              '0（聆）听讲话，有没有说不清、说不出、听不懂。有任何一项，立刻拨打 120。'
              '美国的研究发现，只看脸、胳膊、说话，会漏掉约 14% 的缺血性中风；再加上突然走路不稳、头晕站不住，和突然一只眼或两眼看不清，漏掉的降到约 4%。')
    cards = [('1', '看 1 张脸', '口角歪斜、两边不对称', 'f6'), ('2', '查 2 只胳膊', '平举时一边无力、往下掉', 'f6'), ('0', '（聆）听讲话', '说不清、说不出、听不懂', 'f6')]
    for i, (n, t1, t2, c) in enumerate(cards):
        x = 8 + i * 130
        out.append(f'<rect x="{x}" y="10" width="124" height="96" rx="12" class="{c} fillc"/>')
        out.append(text(x + 62, 50, n, 'tbig', 'middle'))
        out.append(text(x + 62, 76, t1, 'tnode2 b', 'middle'))
        out.append(text(x + 62, 94, t2, 'tnode2 s', 'middle'))
    out.append(node(8, 118, 189, 44, 'f4', '还要留意：突然走路不稳', '头晕站不住、一边腿软'))
    out.append(node(203, 118, 189, 44, 'f4', '还要留意：眼睛突然看不清', '一只眼或两眼、看东西重影'))
    out.append(f'<rect x="60" y="176" width="280" height="44" rx="22" class="f5 fillc"/>')
    out.append(text(200, 204, '有任何一项：立刻拨打 120', 'tnode2 b', 'middle'))
    out.append(text(200, 238, '记下“最后一次看到他正常”的时间，告诉医生', 'tw', 'middle'))
    out.append(text(200, 256, '口诀：中国“中风 120”；补充两项据 BE-FAST 研究', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：时间窗 ----------------
def window():
    W, H = 400, 300
    out = svg(W, H, 'stw', '和时间赛跑：溶栓、取栓的时间窗，越早越好',
              '横轴是从发病（或最后一次看到病人正常）开始的小时数。静脉溶栓：9 个随机试验、6756 人的汇总显示，3 小时内用药，'
              '三到六个月后没有明显残疾的人，用药组 32.9%，对照组 23.1%；3 到 4.5 小时内是 35.3% 对 30.1%；超过 4.5 小时，差别不再明显。'
              '取栓（用导管把大血管里的血块拉出来）：一般在 6 小时内；经过特殊的影像评估，部分病人到 24 小时内仍然受益，'
              '例如 DAWN 研究里，取栓组 49% 生活能自理，对照组 13%。脑子每过一分钟，大约损失 190 万个神经细胞。')
    x0, x1 = 30, 382
    X = lambda h: x0 + (x1 - x0) * h / 24
    yb = 168
    out.append(f'<path d="M{x0} {yb} L{x1} {yb}" class="ax"/>')
    for h in (0, 3, 4.5, 6, 12, 24):
        out.append(f'<path d="M{X(h):.1f} {yb} L{X(h):.1f} {yb + 5}" class="ax"/>')
        out.append(text(X(h), yb + 17, f'{h:g}', 'ta', 'middle'))
    out.append(text(200, yb + 34, '从发病（最后一次看到他正常）算起的小时数', 'ta', 'middle'))
    # 溶栓
    out.append(text(x0, 22, '静脉溶栓（打一针“溶血块”的药）', 'tn'))
    out.append(f'<rect x="{X(0):.1f}" y="30" width="{X(3) - X(0):.1f}" height="26" rx="6" class="f1 fillc"/>')
    out.append(f'<rect x="{X(3):.1f}" y="30" width="{X(4.5) - X(3):.1f}" height="26" rx="6" class="f1 fillc" opacity=".55"/>')
    out.append(text(X(1.5), 47, '0—3 小时', 'tnode2 s', 'middle'))
    out.append(text(X(4.5) + 6, 41, '3 小时内：无残疾 32.9% 对 23.1%', 'ts'))
    out.append(text(X(4.5) + 6, 54, '3—4.5 小时：35.3% 对 30.1%；再晚没有明显好处', 'ts'))
    # 取栓
    out.append(text(x0, 92, '取栓（导管把大血管里的血块拉出来）', 'tn'))
    out.append(f'<rect x="{X(0):.1f}" y="100" width="{X(6) - X(0):.1f}" height="26" rx="6" class="f5 fillc"/>')
    out.append(f'<rect x="{X(6):.1f}" y="100" width="{X(24) - X(6):.1f}" height="26" rx="6" class="f5 fillc" opacity=".45"/>')
    out.append(text(X(3), 117, '6 小时内', 'tnode2 b', 'middle'))
    out.append(text(X(15), 117, '6—24 小时：经影像挑选的部分病人', 'tw', 'middle'))
    out.append(text(x0, 142, '只适合大血管堵塞；DAWN 研究（6—24 小时）：生活能自理 49% 对 13%', 'ts'))
    # 每分钟
    out.append(f'<rect x="{x0}" y="218" width="{x1 - x0}" height="50" rx="10" class="f4 fillc"/>')
    out.append(text(206, 240, '每拖一分钟：大约 190 万个脑细胞死去', 'tnode2 b', 'middle'))
    out.append(text(206, 258, '能不能用这些治疗，由医生判断；家属能做的，是不耽误一分钟', 'tnode2 s', 'middle'))
    out.append(text(200, 292, '数据：Emberson 2014（溶栓汇总）、DAWN 2018、Saver 2006', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：下游、上游、上游的上游 ----------------
def river():
    W, H = 400, 394
    out = svg(W, H, 'str', '中风是一条河的下游：上游是几种病，上游的上游是几十年的生活和环境',
              '最下面是中风本身。往上一层是直接把人推向中风的几种病和状态：高血压（最大的一个）、房颤、血脂异常、糖尿病、颈动脉和脑动脉的斑块、吸烟、大量喝酒。'
              '再往上一层，是造成这些病的生活和环境：盐多钾少、吃得不合宜、动得少、腹部肥胖、睡不好、长期的压力和忧虑、空气污染；还有年龄、遗传这些改不了的因素。'
              '越往上游出手，能挡住的越多；到了下游，只能和时间赛跑。研究估计，十项可以改变的危险因素加起来，和全世界约九成的中风有关。')
    # 三层带子
    layers = [(8, 'f1', '上游的上游：几十年的生活和环境', ['盐多钾少', '饭桌不合宜', '动得少', '腹部肥胖', '睡不好', '压力和忧虑', '空气污染']),
              (138, 'f4', '上游：把人推向中风的几种病', ['高血压', '房颤', '血脂异常', '糖尿病', '血管里的斑块', '吸烟', '大量喝酒']),
              (268, 'f6', '下游：中风', [])]
    for y, c, title, chips in layers:
        hh = 96 if chips else 74
        out.append(f'<rect x="8" y="{y}" width="384" height="{hh}" rx="12" class="{c} fillc" opacity=".22"/>')
        out.append(f'<rect x="8" y="{y}" width="384" height="{hh}" rx="12" class="cn {c}" style="--c:var(--{dict(f1="c1", f4="c4", f6="c6")[c]});fill:none"/>')
        out.append(text(20, y + 20, title, 'tn'))
        cx, cy = 20, y + 34
        for ch in chips:
            w = 14 * len(ch) + 16
            if cx + w > 384:
                cx, cy = 20, cy + 30
            out.append(f'<rect x="{cx}" y="{cy}" width="{w}" height="24" rx="12" class="{c} fillc"/>')
            out.append(text(cx + w / 2, cy + 16, ch, 'tnode2 b', 'middle'))
            cx += w + 6
    out.append(text(20, 310, '缺血性中风（约八成）· 出血性中风', 'tw'))
    out.append(text(20, 328, '只能和时间赛跑：溶栓、取栓、止血、康复', 'tw'))
    for x in (60, 140, 220):
        out.append(arrow(x, 106, x, 136))
        out.append(arrow(x, 236, x, 266))
    out.append(text(392, 124, '越往上游出手，挡住的越多', 'ts', 'end'))
    out.append(text(392, 254, '到了下游，只能和时间赛跑', 'ts', 'end'))
    out.append(text(200, 364, '还有改不了的：年龄、性别、家族史——它们是更要小心的理由', 'tw', 'middle'))
    out.append(text(200, 384, '编者整理的示意，依据 INTERSTROKE 和全球疾病负担研究', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：十项危险因素（INTERSTROKE） ----------------
def ten():
    return bars('stx', '十项可以改变的危险因素，和多少中风有关（INTERSTROKE，32 个国家）',
                '国际 INTERSTROKE 研究比较了 32 个国家约 1.3 万名首次中风的病人和同样多的没有中风的人。下面是每一项的“人群归因风险”，'
                '意思是：如果这一项在人群里消失，理论上能少多少中风。高血压 47.9%，不规律运动 35.8%，载脂蛋白比例（血脂）26.8%，饮食不合宜 23.2%，'
                '腰臀比大（腹部肥胖）18.6%，心理社会压力 17.4%，吸烟 12.4%，心脏病（主要是房颤）9.1%，喝酒 5.8%，糖尿病 3.9%。'
                '各项之间有重叠，不能直接相加；十项合起来约 90.7%。',
                [('如果这一项消失，理论上能少多少中风', [('高血压', 47.9, 'f6'), ('不规律运动', 35.8, 'f4'), ('血脂（载脂蛋白比例）', 26.8, 'f4'),
                                        ('饮食不合宜', 23.2, 'f4'), ('腹部肥胖', 18.6, 'f4'), ('压力、忧虑', 17.4, 'f4'),
                                        ('吸烟', 12.4, 'f4'), ('心脏病（主要是房颤）', 9.1, 'f4'), ('喝酒', 5.8, 'f4'), ('糖尿病', 3.9, 'f4')])],
                '%', 55, '各项有重叠，不能相加；十项合起来约 90.7%（O’Donnell 等，《柳叶刀》2016）')


# ---------------- 图：小中风以后，快和慢的差别 ----------------
def tia():
    return bars('sti', '小中风以后：越快看医生、越快用药，再次中风越少',
                '英国牛津的 EXPRESS 研究：短暂性脑缺血发作（小中风）或轻微中风以后，原来平均要等 20 天才开始用药，90 天内再次中风 10.3%；'
                '改成当天或第二天就评估、立即用药以后，降到 2.1%，减少约八成。中国的 CHANCE 研究：轻微中风或高危小中风 24 小时内开始治疗，'
                '阿司匹林加氯吡格雷的组 90 天内中风 8.2%，只用阿司匹林的组 11.7%，出血没有增加（两组都是 0.3%）。',
                [('EXPRESS（英国）：90 天内再次中风', [('等约 20 天才用药', 10.3, 'f6'), ('当天就评估、用药', 2.1, 'f1')]),
                 ('CHANCE（中国）：90 天内中风', [('只用阿司匹林', 11.7, 'f6'), ('阿司匹林加氯吡格雷', 8.2, 'f1')])],
                '%', 13, '数据：Rothwell 2007；Wang 2013（具体用哪种药，由医生决定）')


# ---------------- 图：中国的三个预防试验 ----------------
def china():
    return bars('stc', '在中国做的预防试验：中风减少了多少',
                '三个在中国做的大型随机对照试验。农村高血压控制项目（CRHCP，326 个村、约 3.4 万人）：由村医按简单的流程给高血压病人用药、调药，目标收缩压低于 130，'
                '三年里中风减少 34%（风险比 0.66）。代用盐试验（SSaSS，600 个村、约 2.1 万名中风或高危老人）：中风减少 14%。'
                '中国脑卒中一级预防试验（CSPPT，约 2.1 万名高血压病人）：降压药里加叶酸，首次中风减少 21%（风险比 0.79）。',
                [('中风减少的比例', [('村医强化降压（CRHCP）', 34, 'f1'), ('降压药加叶酸（CSPPT）', 21, 'f1'), ('换用代用盐（SSaSS）', 14, 'f1')])],
                '%', 40, '数据：He 2023、Huo 2015、Neal 2021（三个都是随机对照试验）')


# ---------------- 图：证据的台阶 ----------------
def ladder():
    W, H = 400, 392
    out = svg(W, H, 'stl', '各种治疗和做法，证据有多硬：一级一级的台阶',
              '编者按本篇引用的研究整理。最上面一级，是大型随机对照试验反复证实的：发病后及时溶栓、取栓；控制血压；房颤用抗凝药；他汀和抗血小板药预防再次中风；'
              '少盐、不吸烟、多动这些生活方式。第二级，是有一个或几个大型随机试验支持、但还需要更多验证的：例如丁苯酞、通心络、三七总皂苷；降压药加叶酸（在叶酸偏低的中国人群）。'
              '第三级，是试验质量偏低、结论不确定的：针灸（和假针刺比较时没有确认效果）、丹参制剂、安宫牛黄丸。最下面一级，是没有可靠证据、而且可能耽误抢救的：'
              '掐人中、十指放血、等一等看看、春秋两季“输液通血管”。')
    steps = [
        ('f1', '反复证实（多个大型随机试验）', '及时溶栓、取栓 · 控制血压 · 房颤抗凝 · 他汀和抗血小板 · 少盐、不吸烟、多动'),
        ('f3', '有大型试验支持，还要更多验证', '丁苯酞 · 通心络、三七总皂苷 · 降压药加叶酸（叶酸偏低的人群）'),
        ('f4', '试验质量偏低，结论不确定', '针灸（对照假针刺时没有确认）· 丹参制剂 · 安宫牛黄丸'),
        ('f6', '没有可靠证据，还会耽误时间', '掐人中 · 十指放血 · 等等看、睡一觉 · 春秋“输液通血管”'),
    ]
    y = 12
    for i, (c, t1, t2) in enumerate(steps):
        x = 8 + i * 18
        w = 384 - i * 36
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="70" rx="12" class="{c} fillc" opacity=".3"/>')
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="70" rx="12" class="cn {c}" style="--c:var(--{dict(f1="c1", f3="c3", f4="c4", f6="c6")[c]});fill:none"/>')
        out.append(text(x + 14, y + 22, f'{i + 1}　{t1}', 'tn'))
        parts = t2.split(' · ')
        line, lines = '', []
        for p in parts:
            cand = (line + ' · ' + p) if line else p
            if len(cand) * 11.5 > w - 28:
                lines.append(line)
                line = p
            else:
                line = cand
        lines.append(line)
        for k, ln in enumerate(lines[:2]):
            out.append(text(x + 14, y + 42 + k * 16, ln, 'tw'))
        y += 82
    out.append(text(200, 352, '评价一种疗法，不看它是“中”是“西”、“天然”还是“化学”，', 'tw', 'middle'))
    out.append(text(200, 370, '只看它有没有经过公平的比较、对病人有没有真实的好处', 'tw', 'middle'))
    out.append(text(200, 388, '编者按本篇引用的研究整理', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
