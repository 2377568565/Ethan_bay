# 健康栏目 07《白内障》页面里的逻辑图和数据图（SVG，宽 400；颜色用页面的类，夜间模式自动变）
# 颜色的意思和前几篇一样：f1 青绿＝保护、能做的事；f6 红＝伤害、疾病；f4 金＝时间和警报；f5 紫＝药物和医院；f3 蓝＝中性的器官和阶段
from history_svg import text
from diabetes_svg import arrow, svg, bars
from osteo_svg import box, wrap


# ---------------- 图：眼睛像照相机 ----------------
def eye():
    W, H = 400, 300
    out = svg(W, H, 'cte', '眼睛像照相机：白内障是“镜头”变混了',
              '上面是清亮的眼睛：光线穿过角膜和瞳孔，经过透明的晶状体（镜头），清楚地聚在后面的视网膜（底片）上。'
              '下面是有白内障的眼睛：晶状体变混，光线被散开、挡住，到视网膜上的像模糊、发暗，看灯会有光晕。'
              '治疗的办法是手术取出混浊的晶状体，换一个透明的人工晶体。')
    for k, (y0, cloudy) in enumerate(((10, False), (150, True))):
        cy = y0 + 62
        out.append(box(8, y0, 384, 128, 'f6' if cloudy else 'f1', '.12'))
        out.append(text(20, y0 + 20, '有白内障：镜头混了' if cloudy else '清亮的眼睛', 'tn'))
        # 眼球
        out.append(f'<circle cx="250" cy="{cy}" r="52" class="cn f3" style="--c:var(--c3);fill:none;stroke-width:2"/>')
        # 角膜
        out.append(f'<path d="M196 {cy - 26} Q186 {cy} 196 {cy + 26}" class="cn" style="--c:var(--c3);fill:none;stroke-width:2.5"/>')
        # 晶状体
        cls = 'f6 fillc' if cloudy else 'f3 fillc" opacity=".35'
        out.append(f'<ellipse cx="214" cy="{cy}" rx="10" ry="22" class="{cls}"/>')
        # 视网膜
        out.append(f'<path d="M290 {cy - 34} Q306 {cy} 290 {cy + 34}" class="cn" style="--c:var(--c4);fill:none;stroke-width:4"/>')
        # 光线
        if not cloudy:
            for dy in (-16, 0, 16):
                out.append(f'<path d="M40 {cy + dy} L204 {cy + dy} L300 {cy}" class="flow" style="fill:none"/>')
            out.append(f'<circle cx="300" cy="{cy}" r="4" class="f1 fillc"/>')
            out.append(text(316, cy + 4, '像清楚', 'tw'))
        else:
            for dy in (-16, 0, 16):
                out.append(f'<path d="M40 {cy + dy} L204 {cy + dy}" class="flow" style="fill:none"/>')
            for dx, dy in ((240, -30), (250, 22), (262, -6), (232, 10), (270, 30)):
                out.append(f'<path d="M224 {cy} L{dx} {cy + dy}" class="flow" style="fill:none;opacity:.6"/>')
            out.append(text(312, cy + 4, '像模糊、发暗', 'tw'))
        out.append(text(186, cy + 42, '角膜', 'ts', 'middle'))
        out.append(text(214, cy - 30, '晶状体＝镜头', 'ts', 'middle'))
        out.append(text(312, cy + 36, '视网膜＝底片', 'ts'))
        out.append(text(40, cy - 22, '光线', 'ts'))
    out.append(text(200, 294, '编者整理的示意图；治疗＝把混了的镜头换成透明的人工晶体', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：全球失明和视力损伤的原因 ----------------
def global_():
    return bars('ctg', '2020 年全世界 50 岁以上的人：失明和视力损伤的主要原因（百万人）',
                '这是全球疾病负担研究视力专家组的模型估计。失明的原因：白内障约 1,520 万人，青光眼约 360 万，没有配好的眼镜约 230 万，'
                '老年黄斑变性约 180 万，糖尿病视网膜病变约 86 万。中度到重度视力损伤的原因：没有配好的眼镜约 8,610 万，白内障约 7,880 万。'
                '排在最前面的白内障和没有配好的眼镜，都是可以治好的。',
                [('失明', [('白内障', 15.2, 'f6'), ('青光眼', 3.6, 'f3'), ('没有配好的眼镜', 2.3, 'f3'), ('老年黄斑变性', 1.8, 'f3'), ('糖尿病视网膜病变', 0.86, 'f3')], ' 百万'),
                 ('中度到重度视力损伤', [('没有配好的眼镜', 86.1, 'f3'), ('白内障', 78.8, 'f6')], ' 百万')],
                '', None, '模型估计 · 数据：GBD 视力专家组 2021（Lancet Glob Health）')


# ---------------- 图：人数在增加，比例在下降 ----------------
def trend():
    W, H = 400, 282
    out = svg(W, H, 'ctt', '全世界失明的人：人数在增加，按年龄标准化的比例在下降',
              '左边是全世界失明的人数：2020 年约 4,330 万，比 1990 年增加了约 51%（按这个增幅推算 1990 年约 2,880 万）；预测到 2050 年约 6,100 万。'
              '右边是 50 岁以上的人里，按年龄标准化以后的失明比例，从 1990 年到 2020 年下降了约 28.5%。'
              '人数增加，是因为人口增长和老化；比例下降，研究者认为有眼科服务（尤其是白内障手术）的功劳。这些都是模型估计。')
    out.append(box(8, 8, 214, 236, 'f6', '.12'))
    out.append(text(115, 28, '失明的人数（百万）', 'tn', 'middle'))
    vals = [('1990', 28.8, '约 28.8（推算）'), ('2020', 43.3, '约 43.3'), ('2050', 61.0, '约 61.0（预测）')]
    base = 218
    for i, (yr, v, lab) in enumerate(vals):
        x = 28 + i * 64
        h = v * 2.3
        op = '.55' if yr == '2050' else '1'
        out.append(f'<rect x="{x}" y="{base - h:.1f}" width="44" height="{h:.1f}" rx="6" class="f6 fillc" opacity="{op}"/>')
        out.append(text(x + 22, base + 16, yr, 'tw', 'middle'))
        out.append(text(x + 22, base - h - 6, lab.split('（')[0], 'tw', 'middle'))
    out.append(text(115, 46, '（2050 年是预测；1990 年按增幅推算）', 'ts', 'middle'))
    out.append(box(232, 8, 160, 236, 'f1', '.12'))
    out.append(text(312, 28, '50 岁以上：失明的比例', 'tn', 'middle'))
    out.append(text(312, 44, '（按年龄标准化）', 'ts', 'middle'))
    out.append(f'<rect x="258" y="80" width="40" height="138" rx="6" class="f3 fillc"/>')
    out.append(f'<rect x="326" y="{80 + 138 * .285:.1f}" width="40" height="{138 * .715:.1f}" rx="6" class="f1 fillc"/>')
    out.append(text(278, 234, '1990', 'tw', 'middle'))
    out.append(text(346, 234, '2020', 'tw', 'middle'))
    out.append(text(346, 112, '−28.5%', 'tn', 'middle'))
    out.append(text(200, 264, '人数↑ 因为人多了、老人多了；比例↓ 因为手术普及了', 'tw', 'middle'))
    out.append(text(200, 278, '模型估计 · 数据：GBD 视力专家组 2021', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：中国，年纪越大越常见 ----------------
def age():
    W, H = 400, 310
    out = svg(W, H, 'cta', '中国：年纪越大，白内障越常见',
              '左边是有白内障（包括已经做过手术）的比例：45—49 岁男性约 6.7%、女性约 8.4%；85—89 岁男性约 73.0%、女性约 77.5%。'
              '右边是中国 45—89 岁有白内障的人数：2015 年约 1.12 亿，按人口老化推算，2050 年约 2.41 亿。'
              '这是汇总 1990 年以来各地研究、用模型推算的数字，不是一次全国统一调查。')
    out.append(box(8, 8, 228, 270, 'f3', '.12'))
    out.append(text(122, 28, '有白内障的比例', 'tn', 'middle'))
    groups = [('45—49 岁', 6.71, 8.39), ('85—89 岁', 73.01, 77.51)]
    base = 230
    for i, (g, m, f) in enumerate(groups):
        x0 = 30 + i * 104
        for j, (lab, v, c) in enumerate((('男', m, 'f3'), ('女', f, 'f5'))):
            x = x0 + j * 40
            h = v * 2.2
            out.append(f'<rect x="{x}" y="{base - h:.1f}" width="32" height="{max(h, 2):.1f}" rx="5" class="{c} fillc"/>')
            out.append(text(x + 16, base - h - 5, f'{v:.0f}%' if v > 20 else f'{v:.1f}%', 'tw', 'middle'))
            out.append(text(x + 16, base + 14, lab, 'ts', 'middle'))
        out.append(text(x0 + 36, 264, g, 'tw', 'middle'))
    out.append(box(246, 8, 146, 270, 'f6', '.12'))
    out.append(text(319, 28, '有白内障的人数', 'tn', 'middle'))
    out.append(text(319, 44, '（45—89 岁）', 'ts', 'middle'))
    for j, (yr, v, op) in enumerate((('2015', 1.12, '1'), ('2050', 2.41, '.55'))):
        x = 266 + j * 58
        h = v * 70
        out.append(f'<rect x="{x}" y="{230 - h:.1f}" width="44" height="{h:.1f}" rx="6" class="f6 fillc" opacity="{op}"/>')
        out.append(text(x + 22, 230 - h - 6, f'{v:.2f} 亿', 'tw', 'middle'))
        out.append(text(x + 22, 250, yr + ('（推算）' if yr == '2050' else ''), 'ts', 'middle'))
    out.append(text(200, 300, '汇总各地研究的模型推算 · 数据：Song 2018（J Glob Health）', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：中国的白内障手术 ----------------
def chinasvc():
    W, H = 400, 330
    out = svg(W, H, 'cts', '中国的白内障手术：三十年追了很远，还有人被落下',
              '上面是每百万人口一年的白内障手术例数：1988 年约 83 例，2017 年约 2,205 例，“十三五”末（2020 年）超过 3,000，'
              '“十四五”规划目标 2025 年 3,500 以上，新方案目标 2030 年超过 4,000。'
              '下面是 2014 年 9 省农村调查：因白内障严重看不清或失明的人里，约 62.7% 做过手术，比 2006 年提高约 81%；'
              '没做手术的多是年纪更大的、女性、没上过学的老人。')
    out.append(text(8, 22, '每百万人口一年做多少例白内障手术', 'tn'))
    pts = [('1988', 83, '约 83', '1'), ('2017', 2205, '约 2,205', '1'), ('2020', 3000, '超过 3,000', '1'), ('2025', 3500, '目标 3,500+', '.45'), ('2030', 4000, '目标 4,000+', '.45')]
    base = 176
    for i, (yr, v, lab, op) in enumerate(pts):
        x = 20 + i * 76
        h = v / 4000 * 130
        out.append(f'<rect x="{x}" y="{base - h:.1f}" width="48" height="{max(h, 2):.1f}" rx="6" class="f1 fillc" opacity="{op}"/>')
        out.append(text(x + 24, base - h - 6, lab, 'tw', 'middle'))
        out.append(text(x + 24, base + 15, yr, 'tw', 'middle'))
    out.append(text(200, 206, '浅色＝规划目标，不是已经达到的数字', 'ts', 'middle'))
    out.append(box(8, 218, 384, 92, 'f4', '.14'))
    out.append(text(20, 238, '2014 年 9 省农村（51,310 名 50 岁以上的人）', 'tn'))
    out.append(text(20, 258, '因白内障严重看不清或失明的人：约 62.7% 做过手术', 'tw'))
    out.append(text(20, 276, '比 2006 年提高约 81%；各地从约 43% 到 84% 不等', 'tw'))
    out.append(text(20, 296, '没做的多是：年纪更大的 · 女性 · 没上过学的', 'tw'))
    out.append(text(200, 326, '数据：新华网 2018、“十四五”眼健康规划、2026 年工作方案、Zhao 2018', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：危险因素的证据 ----------------
def risk():
    W, H = 400, 330
    out = svg(W, H, 'ctr', '哪些因素让白内障来得更早：证据有多硬',
              '从上到下按证据的分量排。最硬：吸烟（综述的综述里唯一达到最高一级的关联，基因研究也支持因果）。'
              '较强：2 型糖尿病（风险约 2 倍）、激素（吸入激素每天每增加 1,000 微克风险约增加 25%）。'
              '有关联但较弱：阳光紫外线（晒得最多的人约高 15%）、烧柴煤做饭的烟（模型估计的负担比吸烟还大）。'
              '试验里没有用：大剂量抗氧化维生素。年纪是最大的因素，但改变不了。')
    tiers = [('f6', '证据最硬', '吸烟 · 正在吸烟和白内障是唯一达到最高一级的关联 · 戒烟二十年风险仍偏高'),
             ('f4', '证据较强', '2 型糖尿病：风险约 2 倍 · 激素：吸入剂量每天多 1,000 微克，风险约多 25%'),
             ('f3', '有关联，较弱', '紫外线：晒得最多约高 15% · 烧柴煤做饭的烟：模型估计负担不小'),
             ('f1', '试验里没有用', '大剂量β-胡萝卜素、维生素 C、维生素 E · 叶黄素（总体）')]
    y = 8
    for c, head, s in tiers:
        out.append(box(8, y, 384, 66, c))
        out.append(f'<rect x="16" y="{y + 9}" width="98" height="48" rx="10" class="{c} fillc"/>')
        out.append(text(65, y + 37, head, 'tnode2 b', 'middle'))
        lines = wrap(s, 262)[:3]
        for k, ln in enumerate(lines):
            out.append(text(124, y + 37 + (k - (len(lines) - 1) / 2) * 17, ln, 'tw'))
        y += 74
    out.append(text(200, y + 8, '最大的因素是年纪，但改变不了；能改变的，从上往下做', 'tw', 'middle'))
    out.append(text(200, y + 26, '数据：Kai 2023、Larsson 2022、Li 2014、Weatherall 2009', 'ts', 'middle'))
    out.append(text(200, y + 40, 'Li 2021、GBD 2021、Mathew 2012', 'ts', 'middle'))
    out.append('</svg>')
    out[0] = out[0].replace(f'0 0 {W} {H}', f'0 0 {W} {y + 48}')
    return '\n'.join(out)


# ---------------- 图：三级预防 ----------------
def levels():
    W, H = 400, 374
    out = svg(W, H, 'ctl', '白内障的三级预防：不得晚得、早发现早手术、治好少并发症',
              '左边是一条时间线：晶状体清亮、开始混浊、影响生活、手术以后。上面对应三级预防。'
              '一级预防在还没有或刚开始的时候：不吸烟、管血糖、慎用激素、防晒、厨房通风、均衡饮食。'
              '二级预防在已经有了、还没伤到生活的时候：有症状就查、高风险的人定期查、不等熟、及时手术，免得跌倒、车祸、失明。'
              '三级预防在手术和术后：选正规医院、选合适的晶体、按时复查、处理后发障、第二只眼。')
    rows = [('f1', '一级预防', '不得 · 晚得', '晶状体还清亮，或刚开始混', '不吸烟 · 管血糖 · 慎用激素 · 防晒 · 厨房通风 · 均衡饮食'),
            ('f4', '二级预防', '早发现 · 早手术', '已经有了，还没伤到生活', '有症状就查 · 高风险定期查 · 不等熟 · 及时手术，免得跌倒、车祸、失明'),
            ('f5', '三级预防', '治好 · 少并发症', '手术和术后', '正规医院 · 选对晶体 · 按时复查 · 激光处理后发障 · 第二只眼')]
    y = 8
    for c, name, verb, when, todo in rows:
        out.append(box(8, y, 384, 104, c))
        out.append(f'<rect x="16" y="{y + 10}" width="96" height="50" rx="10" class="{c} fillc"/>')
        out.append(text(64, y + 32, name, 'tnode2 b', 'middle'))
        out.append(text(64, y + 49, verb, 'tnode2 s', 'middle'))
        out.append(text(122, y + 24, '什么时候：' + when, 'tw'))
        for k, ln in enumerate(wrap(todo, 262)[:3]):
            out.append(text(122, y + 46 + k * 18, ln, 'tw'))
        if y < 200:
            out.append(arrow(64, y + 62, 64, y + 108))
        y += 116
    out.append(text(200, 366, '白内障没有药能化掉，所以“及时手术”是二级预防的核心', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：做了手术以后 ----------------
def benefit():
    return bars('ctb', '做了白内障手术以后，少了多少',
                '跌倒：英国随机试验，70 岁以上女性早做第一只眼的手术，一年里跌倒的次数少了约 34%。'
                '车祸：美国观察研究，做了手术的人车祸率约少 53%。髋部骨折：美国一百多万人的观察研究，一年内约少 16%。'
                '痴呆：美国观察研究，以后得痴呆的风险约少 29%。只有跌倒一项是随机试验，其余是观察研究。',
                [('随机试验', [('跌倒次数', 34, 'f1')]),
                 ('观察研究（可能有健康人更愿意做手术的影响）', [('车祸', 53, 'f3'), ('痴呆', 29, 'f3'), ('一年内髋部骨折', 16, 'f3')])],
                '%', 60, '数据：Harwood 2005、Owsley 2002、Lee 2022、Tseng 2012')


# ---------------- 图：手术怎样做 ----------------
def surgery():
    W, H = 400, 300
    out = svg(W, H, 'ctu', '超声乳化白内障手术：四步“换镜头”',
              '第一步：滴药麻醉，在角膜边上做一个两三毫米的小切口。第二步：在晶状体前面的薄膜上开一个圆形小窗。'
              '第三步：用超声探头把混浊的晶状体震碎、吸出来，后面的囊膜留下。第四步：把折叠的人工晶体推进囊袋，自己展开、固定。'
              '多数用滴眼药水麻醉，当天就能回家。')
    steps = [('f3', '1', '小切口', '滴药麻醉 · 角膜边上两三毫米'),
             ('f4', '2', '开小窗', '晶状体前面的薄膜上开一个圆口'),
             ('f6', '3', '震碎吸出', '超声探头把混了的晶状体震碎吸走'),
             ('f1', '4', '放入人工晶体', '折叠着推进去，在囊袋里展开')]
    for i, (c, n, t, s) in enumerate(steps):
        x = 8 + (i % 2) * 196
        y = 8 + (i // 2) * 128
        out.append(box(x, y, 188, 118, c))
        out.append(f'<circle cx="{x + 26}" cy="{y + 26}" r="15" class="{c} fillc"/>')
        out.append(text(x + 26, y + 31, n, 'tnode2 b', 'middle'))
        out.append(text(x + 50, y + 31, t, 'tn'))
        # 小示意：晶状体
        cx, cy = x + 94, y + 70
        lens_cls = 'f6 fillc' if i < 2 else ('f6 fillc" opacity=".35' if i == 2 else 'f1 fillc" opacity=".55')
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="34" ry="14" class="{lens_cls}"/>')
        out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="38" ry="17" class="cn" style="--c:var(--c3);fill:none;stroke-width:1.5"/>')
        if i == 1:
            out.append(f'<circle cx="{cx}" cy="{cy}" r="9" class="cn" style="--c:var(--c4);fill:none;stroke-width:2;stroke-dasharray:3 2"/>')
        if i == 2:
            out.append(f'<path d="M{cx + 50} {cy - 22} L{cx + 8} {cy - 2}" class="cn" style="--c:var(--c5);stroke-width:3"/>')
        if i == 3:
            out.append(f'<path d="M{cx - 30} {cy} L{cx - 46} {cy - 10} M{cx + 30} {cy} L{cx + 46} {cy - 10}" class="cn" style="--c:var(--c1);stroke-width:2"/>')
        out.append(text(x + 94, y + 108, s, 'ts', 'middle'))
    out.append(text(200, 280, '编者整理的示意，细节以医生讲解为准', 'ts', 'middle'))
    out.append(text(200, 295, '后面那层囊膜留下，正好托住人工晶体', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：多焦点和单焦点 ----------------
def lens():
    return bars('ctn', '多焦点晶体和单焦点晶体比：得到什么、付出什么（倍数）',
                '考克兰汇总 20 项随机试验。看远：两种差不多（需要戴眼镜看远的风险约 0.96 倍）。'
                '看近：多焦点的人需要戴眼镜的风险约是单焦点的 0.63 倍，也就是更可能不戴眼镜。'
                '代价：多焦点的人有眩光的风险约 1.41 倍，有光圈的风险约 3.58 倍。1 倍表示两种一样。',
                [('得到的（越小越好）', [('看远不够清楚', 0.96, 'f3'), ('看近要戴眼镜', 0.63, 'f1')]),
                 ('付出的（越大越麻烦）', [('眩光', 1.41, 'f6'), ('光圈', 3.58, 'f6')])],
                ' 倍', 4, '1 倍＝两种一样 · 数据：de Silva 2016（Cochrane）')


# ---------------- 图：一生的功课 ----------------
def ages():
    W, H = 400, 372
    out = svg(W, H, 'ctg2', '保护眼睛里的“镜头”：一生的功课',
              '从上到下是五个阶段。年轻人：不吸烟，户外戴帽子和太阳镜，防眼外伤，不乱用激素眼药水。'
              '四五十岁：戒烟，管好血糖，慎用激素并定期查眼，厨房通风，吃得均衡。'
              '六十岁以上：模糊、怕光、夜里看灯有光圈就去眼科，糖尿病人定期查眼底，不信化掉白内障的眼药水，不必等熟。'
              '决定手术时：正规医院和有经验的医生，按需要选晶体，术后按时复查。'
              '手术以后：又模糊先查后发障，第二只眼和医生商量，其他眼病仍要定期查。')
    stages = [('f1', '年轻人', '不伤镜头', '不吸烟 · 帽子和太阳镜 · 防眼外伤 · 不乱用激素眼药水'),
              ('f4', '四五十岁', '少伤镜头', '戒烟 · 管血糖 · 慎用激素 · 厨房通风 · 吃得均衡'),
              ('f3', '六十岁以上', '早发现', '模糊怕光就查 · 糖尿病查眼底 · 不信化掉的眼药水 · 不必等熟'),
              ('f5', '决定手术时', '选对', '正规医院 · 有经验的医生 · 按需要选晶体'),
              ('f6', '手术以后', '管好', '按时复查 · 又模糊查后发障 · 第二只眼 · 其他眼病照查')]
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
