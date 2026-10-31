# 健康栏目 08《心梗》页面里的逻辑图（SVG，宽 400；颜色用页面的类，夜间模式自动变）
# 颜色的意思和前几篇一样：f1 青绿＝保护、能做的事；f6 红＝伤害、疾病；f4 金＝时间和警报；f5 紫＝药物和医院；f3 蓝＝中性的器官和阶段
from history_svg import text
from diabetes_svg import arrow, svg, bars
from osteo_svg import box, wrap


# ---------------- 图：斑块怎样变成心梗 ----------------
def artery():
    W, H = 400, 330
    out = svg(W, H, 'mia', '从斑块到心梗：四个阶段',
              '第一阶段，血管内壁光滑，血流通畅。第二阶段，坏胆固醇钻进血管壁，形成脂纹，鼓起一个小包，还没有症状。'
              '第三阶段，斑块长大，里面是软的脂质，外面盖着一层纤维帽；帽子薄的斑块最危险。'
              '第四阶段，纤维帽破裂，血小板聚集，血栓在几分钟里把血管堵死，后面的心肌缺血坏死，这就是心梗。'
              '吸烟、高血压、高血糖、高 LDL 会让每一步走得更快。')
    stages = [('f1', '1 光滑通畅', '内壁光滑 · 血流顺畅', 0, False, False),
              ('f3', '2 脂纹', '坏胆固醇钻进管壁|十几岁就可能出现', 8, False, False),
              ('f4', '3 斑块', '软的脂质“粥”加一层纤维帽|帽子薄的最危险', 18, False, False),
              ('f6', '4 破裂、血栓', '帽子破了|血栓几分钟内堵死血管 → 心梗', 18, True, True)]
    for i, (c, title, sub, bump, rup, clot) in enumerate(stages):
        y = 8 + i * 76
        out.append(box(8, y, 384, 68, c, '.12'))
        out.append(text(20, y + 20, title, 'tn'))
        for k, ln in enumerate(sub.split('|')):
            out.append(text(20, y + 38 + k * 14, ln, 'ts'))
        # 血管
        x0, x1, ty, by = 200, 384, y + 16, y + 56
        out.append(f'<path d="M{x0} {ty} L{x1} {ty} M{x0} {by} L{x1} {by}" class="cn" style="--c:var(--c3);stroke-width:3;fill:none"/>')
        if bump:
            cx = 292
            out.append(f'<path d="M{cx - 34} {by} Q{cx} {by - bump * 1.4} {cx + 34} {by} Z" class="f4 fillc"/>')
        if rup:
            out.append(f'<path d="M{cx - 6} {by - bump * .7} L{cx + 2} {by - bump * .9 - 4} L{cx + 8} {by - bump * .7}" class="cn" style="--c:var(--c6);stroke-width:2;fill:none"/>')
        if clot:
            out.append(f'<rect x="{cx - 20}" y="{ty + 1}" width="40" height="{by - ty - bump * .6:.1f}" rx="6" class="f6 fillc"/>')
            out.append(text(cx + 46, y + 40, '堵死', 'tw'))
        else:
            out.append(arrow(208, y + 36, 250 if bump else 372, y + 36))
    out.append(text(200, 322, '编者整理的示意图 · 吸烟、高血压、高血糖、高 LDL 让每一步更快', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：几十年的时间线 ----------------
def timeline():
    W, H = 400, 250
    out = svg(W, H, 'mit', '心梗的根在几十年前：一级预防要从年轻时开始',
              '横轴是年龄，从 10 岁到 80 岁。这是示意图。十几二十岁，血管里就可能出现脂纹；三四十岁斑块慢慢长大，大多没有症状；'
              '五十岁以后，斑块破裂引起心梗的风险越来越高。一级预防覆盖整个过程，越早开始越好；二级预防在第一次心梗以后。')
    x0, x1 = 30, 386
    X = lambda a: x0 + (x1 - x0) * (a - 10) / 70
    out.append(f'<path d="M{x0} 150 L{x1} 150" class="ax"/>')
    for a in (10, 20, 30, 40, 50, 60, 70, 80):
        out.append(text(X(a), 166, f'{a}', 'ta', 'middle'))
    out.append(text((x0 + x1) / 2, 182, '年龄（岁）', 'ta', 'middle'))
    # 斑块增长曲线
    pts = [(10, 4), (20, 10), (30, 20), (40, 36), (50, 58), (60, 80), (70, 98), (80, 112)]
    d = 'M' + ' L'.join(f'{X(a):.1f} {150 - v:.1f}' for a, v in pts)
    out.append(f'<path d="{d}" class="cn" style="--c:var(--c6);stroke-width:2.5;fill:none"/>')
    out.append(text(X(14), 96, '脂纹、斑块慢慢长', 'tw'))
    out.append(text(X(14), 110, '大多没有症状', 'ts'))
    out.append(f'<rect x="{X(30):.1f}" y="14" width="{X(63) - X(30):.1f}" height="22" rx="11" class="f6 fillc"/>')
    out.append(text((X(30) + X(63)) / 2, 29, '斑块破裂 → 心梗的风险越来越高', 'tnode2 s', 'middle'))
    out.append(f'<rect x="{X(10):.1f}" y="196" width="{X(80) - X(10):.1f}" height="20" rx="10" class="f1 fillc"/>')
    out.append(text((X(10) + X(80)) / 2, 210, '一级预防：越早开始越好', 'tnode2 s', 'middle'))
    out.append(f'<rect x="{X(55):.1f}" y="222" width="{X(80) - X(55):.1f}" height="20" rx="10" class="f5 fillc"/>')
    out.append(text((X(55) + X(80)) / 2, 236, '二级预防：心梗以后', 'tnode2 s', 'middle'))
    out.append(text(X(10) + 2, 236, '编者整理的示意', 'ts'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：三级预防 ----------------
def levels():
    W, H = 400, 352
    out = svg(W, H, 'mil', '心梗的三级预防',
              '一级预防：还没得过心梗的人，不让第一次发生：不吸烟、降 LDL、控血压、控血糖、管腰围、吃好、多动、管好压力和睡眠。'
              '二级预防：得过心梗或有冠心病的人，不让第二次发生：规范用药不停药、心脏康复、一级预防加倍认真。'
              '急救：万一发生，认出症状、马上打 120、尽快打通血管。本篇的重点是一级预防。')
    rows = [('f1', '一级预防', '本篇的重点', '还没得过心梗的人 · 不让第一次发生', '不吸烟 · 降 LDL · 控血压 · 控血糖 · 管腰围 · 吃好 · 多动 · 管压力和睡眠'),
            ('f4', '急救', '抢时间', '万一发生', '认出症状 · 马上打 120 · 尽快打通血管 · 学会心肺复苏'),
            ('f5', '二级预防', '不让再来', '得过心梗或有冠心病的人', '规范用药不停药 · 心脏康复 · 一级预防加倍认真 · 照顾心情')]
    y = 8
    for c, name, verb, who, todo in rows:
        h = 104
        out.append(box(8, y, 384, h, c))
        out.append(f'<rect x="16" y="{y + 10}" width="96" height="50" rx="10" class="{c} fillc"/>')
        out.append(text(64, y + 32, name, 'tnode2 b', 'middle'))
        out.append(text(64, y + 49, verb, 'tnode2 s', 'middle'))
        for k, ln in enumerate(wrap(who, 262)[:2]):
            out.append(text(122, y + 24 + k * 16, ln, 'tn' if k == 0 else 'tw'))
        for k, ln in enumerate(wrap(todo, 262)[:3]):
            out.append(text(122, y + 56 + k * 18, ln, 'tw'))
        y += h + 6
    out.append(text(200, 346, '最好的治疗，是不让它发生', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：INTERHEART 九个因素 ----------------
def nine():
    return bars('min', '心梗的可以改变的因素，各约占风险的多少（INTERHEART）',
                '52 个国家 15,152 名心梗病人和 14,820 名对照者的研究。各因素的人群归因风险：血脂异常约 49%，吸烟约 36%，心理社会压力约 33%，'
                '腹部肥胖约 20%，高血压约 18%，不是每天吃蔬菜水果约 14%，不规律运动约 12%，糖尿病约 10%。'
                '几项常常同时存在，所以不能简单相加；合起来约占男性的 90%、女性的 94%。',
                [('代谢和身体', [('血脂异常', 49.2, 'f6'), ('腹部肥胖', 20.1, 'f6'), ('高血压', 17.9, 'f6'), ('糖尿病', 9.9, 'f6')]),
                 ('生活习惯和心情', [('吸烟', 35.7, 'f4'), ('心理社会压力', 32.5, 'f4'), ('不是每天吃蔬果', 13.7, 'f4'), ('不规律运动', 12.2, 'f4')])],
                '%', 55, '几项不能简单相加；合起来约占九成 · 数据：Yusuf 2004（INTERHEART）')


# ---------------- 图：中国 46 万人的健康生活方式 ----------------
def lifestyle():
    W, H = 400, 300
    out = svg(W, H, 'mis', '中国 46 万人：健康习惯越多，冠心病越少',
              '中国慢性病前瞻性研究，461,211 人，跟踪约 7 年。六个健康习惯：不吸烟、不大量喝酒、活动量中等以上、多吃蔬菜水果少吃红肉、体重正常、腰不粗。'
              '和一项都没做到的人比，做到 4 项以上的人，重大冠心病事件少了约 58%，缺血性中风少了约 39%。'
              '研究者估计约 68% 的重大冠心病事件和没有坚持健康生活方式有关。这是观察研究。')
    habits = ['不吸烟', '不大量喝酒', '多活动', '多蔬果、少红肉', '体重正常', '腰不粗']
    out.append(box(8, 8, 384, 98, 'f1', '.12'))
    out.append(text(20, 28, '六个健康习惯', 'tn'))
    for i, hb in enumerate(habits):
        x = 18 + (i % 3) * 124
        y = 40 + (i // 3) * 30
        out.append(f'<rect x="{x}" y="{y}" width="116" height="24" rx="12" class="f1 fillc"/>')
        out.append(text(x + 58, y + 16, hb, 'tnode2 b', 'middle'))
    out.append(text(20, 132, '做到 4 项以上，和一项都没做到的人比：', 'tn'))
    rows = [('重大冠心病事件', 58), ('缺血性中风', 39)]
    for i, (lab, v) in enumerate(rows):
        y = 146 + i * 34
        out.append(text(128, y + 15, lab, 'tw', 'end'))
        w = 230 * v / 70
        out.append(f'<rect x="136" y="{y}" width="{w:.1f}" height="20" rx="5" class="f1 fillc"/>')
        out.append(text(142 + w, y + 15, f'少了约 {v}%', 'tw'))
    out.append(f'<rect x="20" y="222" width="360" height="40" rx="12" class="f6 fillc" opacity=".2"/>')
    out.append(text(200, 240, '约 68% 的重大冠心病事件', 'tn', 'middle'))
    out.append(text(200, 256, '和没有坚持健康生活方式有关（估计）', 'tw', 'middle'))
    out.append(text(200, 288, '观察研究 · 数据：Lv 2017（中国慢性病前瞻性研究）', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：证据台阶 ----------------
def ladder():
    W, H = 400, 360
    out = svg(W, H, 'mil2', '预防心梗的办法，证据有多硬',
              '第一层，随机试验证明减少心血管事件：降压、降 LDL、代用盐、地中海饮食加坚果或橄榄油、风险中等的人用复方药丸。'
              '第二层，大型观察研究一致支持：不吸烟和戒烟、多运动、多吃蔬菜水果和坚果、保持腰围、健康生活方式的组合。'
              '第三层，随机试验没有看到好处或可能有害：β-胡萝卜素、维生素 E、维生素 D、一般人群吃鱼油，单吃钙片可能增加心梗。'
              '第四层，没有证据：软化血管、清理血管的保健品和输液。')
    tiers = [('f1', '随机试验：减少心血管事件', '降压 · 降 LDL · 代用盐 · 地中海饮食加坚果或橄榄油 · 风险中等者用复方药丸'),
             ('f3', '大型观察研究：一致支持', '不吸烟和戒烟 · 多运动 · 多吃蔬果和坚果 · 保持腰围 · 健康生活方式组合'),
             ('f4', '随机试验：没好处或可能有害', 'β-胡萝卜素 · 维生素 E · 维生素 D · 一般人群吃鱼油 · 单吃钙片'),
             ('f6', '没有证据', '“软化血管”“清理血管”的保健品 · 输液“通血管”')]
    y = 8
    for c, head, s in tiers:
        h = 72
        out.append(box(8, y, 384, h, c))
        out.append(f'<rect x="16" y="{y + 8}" width="118" height="{h - 16}" rx="10" class="{c} fillc"/>')
        hl = wrap(head.replace('：', ' · '), 100, 11)[:3]
        for k, ln in enumerate(hl):
            out.append(text(75, y + h / 2 + 4 + (k - (len(hl) - 1) / 2) * 15, ln, 'tnode2 b', 'middle'))
        lines = wrap(s, 240)[:3]
        for k, ln in enumerate(lines):
            out.append(text(144, y + h / 2 + 4 + (k - (len(lines) - 1) / 2) * 17, ln, 'tw'))
        y += h + 8
    out.append(text(200, y + 12, '越往上，越有把握', 'tw', 'middle'))
    out.append(text(200, y + 32, '编者根据本篇引用的研究整理', 'ts', 'middle'))
    out.append('</svg>')
    out[0] = out[0].replace(f'0 0 {W} {H}', f'0 0 {W} {y + 40}')
    return '\n'.join(out)


# ---------------- 图：补充剂的大型试验 ----------------
def supps():
    return bars('mip', '补充剂的大型试验结果（风险比）',
                '风险比 1 表示两组一样，小于 1 表示减少，大于 1 表示增加。VITAL 试验：鱼油对主要心血管事件 0.92，没有统计学意义；'
                '维生素 D 0.97，没有意义。钙片单独吃，心梗 1.27（汇总分析）。代用盐（多钾少钠）：主要心血管事件减少，中风约 0.86。'
                '只有代用盐有好的随机试验证明有好处。',
                [('一般人群的大型试验（主要心血管事件）', [('鱼油（不显著）', 0.92, 'f3'), ('维生素 D（不显著）', 0.97, 'f3')]),
                 ('单吃钙片（心梗，汇总分析）', [('钙片', 1.27, 'f6')]),
                 ('代用盐：多钾少钠（中风）', [('代用盐', 0.86, 'f1')])],
                '', 1.5, '1＝两组一样 · 数据：Manson 2019、Bolland 2010、Neal 2021')


# ---------------- 图：心梗的信号 ----------------
def alarm():
    W, H = 400, 300
    out = svg(W, H, 'mia2', '认出心梗：典型和不典型的信号',
              '典型的：胸口正中压榨样、憋闷的痛，超过 15 分钟不缓解，可能放射到左肩、左臂、后背、脖子、下巴，伴随大汗、恶心、喘不上气。'
              '不典型的：只有“胃疼”、上腹不适、牙痛、肩痛、喘不过气、特别乏力；老年人、女性、糖尿病人更常见。'
              '中国的研究：94% 的病人有胸痛或胸闷，却只有 43% 想到是心脏的问题，从发病到医院的中位数是 4 小时。做法：马上打 120。')
    out.append(box(8, 8, 188, 176, 'f6'))
    out.append(text(102, 30, '典型的', 'tn', 'middle'))
    for k, t in enumerate(['胸口压榨样、憋闷的痛', '超过 15 分钟不缓解', '放射到左肩、左臂、后背', '脖子、下巴、牙齿', '大汗、恶心、喘不上气']):
        out.append(text(20, 54 + k * 24, '· ' + t, 'tw'))
    out.append(box(204, 8, 188, 176, 'f4'))
    out.append(text(298, 30, '不典型的', 'tn', 'middle'))
    for k, t in enumerate(['只有“胃疼”、上腹胀', '牙痛、肩痛', '喘不过气、特别乏力', '老人、女性、糖尿病人', '更常见、更容易误会']):
        out.append(text(216, 54 + k * 24, '· ' + t, 'tw'))
    out.append(f'<rect x="8" y="194" width="384" height="44" rx="12" class="f3 fillc" opacity=".25"/>')
    out.append(text(200, 212, '中国：94% 有胸痛或胸闷，只有 43% 想到是心脏', 'tw', 'middle'))
    out.append(text(200, 230, '从发病到医院的中位数：4 小时', 'tw', 'middle'))
    out.append(f'<rect x="80" y="246" width="240" height="34" rx="17" class="f6 fillc"/>')
    out.append(text(200, 268, '马上打 120，不要自己开车', 'tnode2 b', 'middle'))
    out.append(text(200, 296, '数据：Guan 2019（China PEACE）', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：二级预防 ----------------
def second():
    return bars('mis2', '得过心梗以后：这些办法减少了多少（随机试验）',
                '复方药丸（阿司匹林、降压药、他汀合成一粒）：3 年里主要心血管事件约少 24%。'
                '以运动为主的心脏康复：半年到一年里心梗约少 28%，住院约少 42%。'
                '血脂康（含洛伐他汀的红曲提取物）：中国心梗病人主要冠脉事件约少 45%。'
                '通心络（加在规范治疗上）：急性心梗后 30 天主要心脑血管事件约少 36%。',
                [('规范用药', [('复方药丸（3 年）', 24, 'f5'), ('血脂康（中国试验）', 45, 'f5')]),
                 ('心脏康复（半年到一年）', [('心梗', 28, 'f1'), ('住院', 42, 'f1')]),
                 ('中药加在规范治疗上', [('通心络（30 天）', 36, 'f4')])],
                '%', 60, '数据：Castellano 2022、Lu 2008、Dibben 2021、Yang 2023')


# ---------------- 图：一生的功课 ----------------
def ages():
    W, H = 400, 372
    out = svg(W, H, 'miz', '护心是一生的功课',
              '孩子和年轻人：不吸烟，少喝甜饮料，多运动，睡够觉，家族早发心血管病的查血脂。'
              '三四十岁：知道自己的数字，戒烟，管腰围，每周运动 150 分钟，学会休息。'
              '五十岁以上：每年体检算风险，该吃的药按时吃，阿司匹林问医生，不迷信保健品。'
              '得过心梗的：规范用药，心脏康复，加倍预防，家人会打 120 和心肺复苏。每个家庭：至少一人学会心肺复苏。')
    stages = [('f1', '孩子、年轻人', '护血管', '不吸烟 · 少喝甜饮料 · 多运动 · 睡够觉 · 有家族史查血脂'),
              ('f4', '三四十岁', '知道数字', '量血压查血脂血糖 · 戒烟 · 管腰围 · 每周运动 150 分钟 · 别熬夜'),
              ('f3', '五十岁以上', '算风险', '每年体检算 10 年风险 · 该吃的药按时吃 · 阿司匹林问医生'),
              ('f5', '得过心梗的', '不让再来', '规范用药不停药 · 心脏康复 · 一级预防加倍认真'),
              ('f6', '每个家庭', '会急救', '认出心梗 · 打 120 · 至少一人学会心肺复苏')]
    y = 8
    for c, age_, verb, s in stages:
        out.append(box(8, y, 384, 62, c))
        out.append(f'<rect x="16" y="{y + 9}" width="92" height="44" rx="10" class="{c} fillc"/>')
        out.append(text(62, y + 28, age_, 'tnode2 b', 'middle'))
        out.append(text(62, y + 44, verb, 'tnode2 s', 'middle'))
        for k, ln in enumerate(wrap(s, 266)[:2]):
            out.append(text(118, y + 28 + k * 18, ln, 'tw'))
        y += 70
    out.append(text(200, 366, '编者根据本篇引用的研究整理', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
