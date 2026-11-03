# 健康栏目 12《产后浑身酸痛》页面里的逻辑图（SVG，宽 400；颜色用页面的类，夜间模式自动变）
# 颜色的意思和前几篇一样：f1 青绿＝保护、能做的事；f6 红＝伤害、疼；f4 金＝时间和警报；f5 紫＝药物和医院；f3 蓝＝中性的器官和阶段
from history_svg import text
from diabetes_svg import arrow, svg, bars
from osteo_svg import box, wrap


# ---------------- 图：很多妈妈都这样 ----------------
def scale():
    return bars('ppa', '产后酸痛：很多妈妈都有',
                '香港 259 位妈妈，产后 2 个月电话访问：57.5% 产后新出现手腕痛，其中 84% 到第 2 个月还在痛。'
                '北京 1,038 位产后 6 周的妈妈：32.2% 有骨盆带痛。波兰 395 位哺乳妈妈：84% 每个月至少背痛一次。'
                '挪威 300 位初产妇：腹直肌分离在产后 6 周约 60%，6 个月约 45%，12 个月约 33%。',
                [('有多少妈妈痛', [('香港：产后手腕痛', 57.5, 'f6'), ('北京：产后 6 周骨盆带痛', 32.2, 'f6'), ('波兰：哺乳妈妈每月背痛', 84, 'f6')], '%'),
                 ('腹直肌分离：慢慢合拢', [('产后 6 周', 60, 'f4'), ('产后 6 个月', 45.4, 'f4'), ('产后 12 个月', 32.6, 'f1')], '%')],
                '%', 100, 'Sit 2017、Li 2024、Ratajczak 2024、Sperstad 2016')


# ---------------- 图：三股力量汇在一起 ----------------
def why():
    W, H = 400, 330
    out = svg(W, H, 'ppw', '为什么出了月子反而更疼：三股力量汇在一起',
              '第一股，重复的负荷：一天抱几十次、喂七八次，孩子越长越重。第二股，身体还没恢复：腹肌和核心变薄，腹直肌分离，足弓变低。'
              '第三股，睡不够、心里累：睡眠差让人对疼更敏感，也更难好。三股汇在一起，就成了浑身的酸痛。碰冷水不是主要原因。')
    srcs = [('f4', '重复的负荷', '一天抱几十次 · 喂七八次', '孩子越长越重'),
            ('f3', '身体还没恢复', '核心肌肉变薄 · 腹直肌分离', '足弓变低'),
            ('f5', '睡不够、心里累', '睡眠差 · 对疼更敏感', '也更难好')]
    for i, (c, a, b, d) in enumerate(srcs):
        x = 8 + i * 130
        out.append(box(x, 10, 124, 92, c, '.16'))
        out.append(text(x + 62, 34, a, 'tn', 'middle'))
        for k, ln in enumerate(wrap(b, 110, 11)[:2]):
            out.append(text(x + 62, 54 + k * 15, ln, 'ts', 'middle'))
        out.append(text(x + 62, 54 + min(len(wrap(b, 110, 11)), 2) * 15, d, 'ts', 'middle'))
        out.append(arrow(x + 62, 104, 200, 150))
    out.append(box(60, 152, 280, 64, 'f6', '.18'))
    out.append(text(200, 178, '手腕、肩颈、腰、胯、脚', 'tn', 'middle'))
    out.append(text(200, 198, '一处接一处地酸痛，几天也消不掉', 'ts', 'middle'))
    out.append(box(8, 236, 384, 62, 'f1', '.12'))
    out.append(text(20, 258, '好消息：三股力量都可以减弱', 'tn'))
    out.append(text(20, 278, '改抱法和喂法 · 慢慢练回力量 · 家人分担夜里', 'ts'))
    out.append(text(392, 320, '碰冷水：没有研究说明它会造成关节病 · 编者整理', 'ts', 'end'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：疼痛地图 ----------------
def body():
    W, H = 400, 380
    out = svg(W, H, 'ppb', '产后疼痛地图：哪里疼，可能是什么',
              '1 拇指根和手腕拇指一侧：妈妈手，也就是桡骨茎突狭窄性腱鞘炎。2 手指发麻：腕管综合征，或颈部姿势压迫。'
              '3 手指根部疼、弯伸卡住：扳机指。4 肩颈：喂奶低头、同一姿势太久。5 腰：核心肌肉变薄、弯腰抱孩子。'
              '6 胯和屁股两侧：骨盆带痛，常在骶髂关节。7 脚和脚趾：久站、足弓变低。')
    # 简化的人形（线条），站在左边
    cx = 104
    out.append(f'<circle cx="{cx}" cy="40" r="22" class="cn f3" style="--c:var(--c3);fill:none"/>')
    out.append(f'<path d="M{cx} 62 L{cx} 70 M{cx - 40} 82 Q{cx} 66 {cx + 40} 82 L{cx + 34} 190 Q{cx} 204 {cx - 34} 190 Z" class="cn f3" style="--c:var(--c3);fill:none"/>')
    out.append(f'<path d="M{cx - 40} 84 L{cx - 62} 150 L{cx - 70} 210 M{cx + 40} 84 L{cx + 62} 150 L{cx + 70} 210" class="cn f3" style="--c:var(--c3);fill:none"/>')
    out.append(f'<path d="M{cx - 22} 198 L{cx - 28} 290 L{cx - 30} 350 L{cx - 52} 358 M{cx + 22} 198 L{cx + 28} 290 L{cx + 30} 350 L{cx + 52} 358" class="cn f3" style="--c:var(--c3);fill:none"/>')
    dots = [(cx - 70, 212, '1'), (cx + 62, 156, '2'), (cx + 70, 214, '3'), (cx + 26, 76, '4'), (cx, 170, '5'), (cx + 30, 198, '6'), (cx - 46, 356, '7')]
    for x, y, n in dots:
        out.append(f'<circle cx="{x}" cy="{y}" r="10" class="f6 fillc"/>')
        out.append(text(x, y + 4, n, 'tnode2 b', 'middle'))
    items = [('1', '拇指根、手腕拇指侧', '妈妈手（腱鞘炎）'),
             ('2', '手指发麻', '腕管综合征 · 或颈部'),
             ('3', '手指根疼、弯伸卡住', '扳机指'),
             ('4', '肩颈', '低头喂奶 · 同一姿势太久'),
             ('5', '腰', '核心变薄 · 弯腰抱孩子'),
             ('6', '胯、屁股两侧', '骨盆带痛（骶髂关节）'),
             ('7', '脚、脚趾', '久站 · 足弓变低')]
    for i, (n, a, b) in enumerate(items):
        y = 12 + i * 50
        out.append(box(210, y, 182, 44, 'f6' if n in '123' else 'f4' if n in '45' else 'f3', '.12'))
        out.append(text(222, y + 19, f'{n}  {a}', 'tn'))
        out.append(text(238, y + 36, b, 'ts'))
    out.append(text(392, 372, '示意图 · 编者根据本篇引用的研究整理', 'ts', 'end'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：妈妈手是怎么回事 ----------------
def thumb():
    W, H = 400, 300
    out = svg(W, H, 'ppt', '妈妈手：两条肌腱挤过一条窄隧道',
              '在手腕拇指一侧，有两条管拇指张开和伸直的肌腱，一起穿过一条由腱鞘包着的窄隧道。'
              '抱孩子时拇指张开、手腕往小指方向弯，肌腱在隧道里反复来回摩擦，腱鞘变厚、隧道变窄，就会疼。'
              '自测：拇指握在拳头里，手腕往小指方向弯，拇指一侧手腕剧痛，就很像妈妈手。')
    # 隧道
    out.append(text(8, 20, '手腕拇指一侧（放大示意）', 'tn'))
    out.append(box(30, 34, 340, 74, 'f3', '.10'))
    out.append('<rect x="150" y="44" width="100" height="54" rx="14" class="f6 fillc" opacity=".28"/>')
    out.append('<rect x="150" y="44" width="100" height="54" rx="14" class="cn f6" style="--c:var(--c6);fill:none"/>')
    for y in (62, 80):
        out.append(f'<path d="M40 {y} L360 {y}" class="cn f5" style="--c:var(--c5);fill:none;stroke-width:4"/>')
    out.append(text(200, 124, '腱鞘变厚 · 隧道变窄 · 肌腱一动就疼', 'ts', 'middle'))
    out.append(text(44, 56, '通往拇指', 'ts'))
    out.append(text(356, 56, '通往前臂', 'ts', 'end'))
    # 自测三步
    steps = [('①', '拇指弯进掌心', '其余四指握住它'), ('②', '手腕往小指方向弯', '慢慢地，不要用力甩'), ('③', '拇指一侧手腕剧痛', '很像妈妈手 · 请医生确认')]
    for i, (n, a, b) in enumerate(steps):
        x = 8 + i * 130
        out.append(box(x, 146, 124, 84, 'f4' if i < 2 else 'f6', '.14'))
        out.append(text(x + 62, 170, n, 'tn', 'middle'))
        out.append(text(x + 62, 192, a, 'ts', 'middle'))
        for k, ln in enumerate(wrap(b, 112, 10.5)[:2]):
            out.append(text(x + 62, 210 + k * 14, ln, 'ts', 'middle'))
        if i < 2:
            out.append(arrow(x + 125, 188, x + 131, 188))
    out.append(text(8, 256, '为什么新妈妈多：抱孩子时拇指张开、手腕往小指方向弯，', 'tw'))
    out.append(text(8, 274, '一天几十次；第一胎、孩子越大越常见。', 'tw'))
    out.append(text(392, 294, '示意图 · Sit 2017、Ferraro 2023、Daglan 2024', 'ts', 'end'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：麻在哪几根手指 ----------------
def numb():
    W, H = 400, 290
    out = svg(W, H, 'ppn', '手指发麻：看麻在哪几根',
              '示意图画的是左手、手心朝向自己。左边：拇指、食指、中指和无名指靠拇指的一半发麻，夜里麻醒、甩甩手会好，多半是腕管综合征，正中神经在手腕被挤。'
              '右手示意：无名指靠小指的一半和小指发麻，可能是肘部的尺神经，或颈部的神经根。麻木伴着肩颈痛、转头加重、手臂发麻发沉的，要想到颈部。')

    def hand(x0, hot, cls, half=None):
        o = []
        o.append(f'<rect x="{x0 + 20}" y="110" width="104" height="96" rx="20" class="cn f3" style="--c:var(--c3);fill:none"/>')
        fingers = [(x0 + 0, 120, 26, 60), (x0 + 22, 40, 22, 74), (x0 + 48, 30, 22, 84), (x0 + 74, 38, 22, 76), (x0 + 100, 56, 20, 58)]
        # 拇指斜放
        for i, (x, y, w, h) in enumerate(fingers):
            on = i in hot
            if i == 0:
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" transform="rotate(-28 {x + w / 2} {y + h})" class="{cls if on else "f3"} fillc" opacity="{.75 if on else .18}"/>')
            elif i == 3 and half:
                # 无名指只麻一半：靠拇指的一半（腕管）或靠小指的一半（尺神经）
                lc, rc = (cls, 'f3') if half == 'l' else ('f3', cls)
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h + 4}" rx="11" class="f3 fillc" opacity=".18"/>')
                o.append(f'<rect x="{x + (0 if half == "l" else w / 2)}" y="{y + 2}" width="{w / 2}" height="{h}" rx="6" class="{cls} fillc" opacity=".75"/>')
            else:
                o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h + 4}" rx="11" class="{cls if on else "f3"} fillc" opacity="{.75 if on else .18}"/>')
        return o
    out += hand(30, (0, 1, 2), 'f5', 'l')
    out += hand(236, (4,), 'f4', 'r')
    out.append(text(102, 228, '拇指、食指、中指（和半个无名指）', 'ts', 'middle'))
    out.append(text(102, 246, '→ 多半是腕管综合征', 'tn', 'middle'))
    out.append(text(300, 228, '小指和半个无名指', 'ts', 'middle'))
    out.append(text(300, 246, '→ 肘部尺神经或颈部', 'tn', 'middle'))
    out.append(text(200, 270, '麻木伴着肩颈痛、转头加重：要想到颈部', 'tw', 'middle'))
    out.append(text(392, 286, '示意图 · 左手，手心朝向自己 · 编者整理', 'ts', 'end'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：抱孩子，换个手法 ----------------
def hold():
    W = 400
    rows = [('用虎口卡住腋下往上提', '拇指张开、手腕往小指方向弯', '手掌朝上，像托盘一样托住', '用前臂和身体承重'),
            ('弯腰从床上、地上抱起', '腰一直弯着用力', '先蹲下、靠近，再站起来', '把孩子贴近身体再起身'),
            ('总用同一只手、同一边', '一侧手腕、肩膀累坏', '左右轮换', '常换手、换边'),
            ('长时间单手托着', '手腕一直撑着', '用背带、腰凳分担', '让肩、腰一起承重')]
    H = 34 + len(rows) * 70 + 22
    out = svg(W, H, 'pph', '抱孩子：换个手法，手腕少受累',
              '左边是容易伤手腕的做法，右边是换一个做法。用虎口卡住腋下往上提，改成手掌朝上像托盘一样托住，用前臂和身体承重；'
              '弯腰从床上抱起，改成先蹲下、靠近再站起；总用同一只手，改成左右轮换；长时间单手托着，改成用背带、腰凳分担。')
    out.append(text(100, 20, '容易伤手腕的做法', 'tn', 'middle'))
    out.append(text(300, 20, '换一个做法', 'tn', 'middle'))
    y = 32
    for a, a2, b, b2 in rows:
        out.append(box(8, y, 184, 60, 'f6', '.13'))
        out.append(text(18, y + 24, '✗ ' + a, 'tw'))
        out.append(text(32, y + 44, a2, 'ts'))
        out.append(arrow(194, y + 30, 206, y + 30))
        out.append(box(208, y, 184, 60, 'f1', '.13'))
        out.append(text(218, y + 24, '✓ ' + b, 'tw'))
        out.append(text(232, y + 44, b2, 'ts'))
        y += 70
    out.append(text(392, H - 6, '编者根据本篇引用的研究和康复常规整理', 'ts', 'end'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：喂奶的姿势 ----------------
def feed():
    W = 400
    items = [('f1', '孩子来就乳', '用枕头把孩子垫到乳房的高度 · 不要人弯腰去够'),
             ('f1', '背有靠、脚有垫', '坐着喂：背后垫枕头 · 脚下垫小凳 · 肩膀放松'),
             ('f1', '侧躺：头有枕、背有垫', '头下枕头够高、脖子直 · 背后再垫一个'),
             ('f4', '不要一个姿势太久', '左右两边轮换 · 坐、躺、半躺换着来'),
             ('f4', '喂完动一动', '慢慢转头、耸肩、扩胸 · 看远处一会儿')]
    H = 10 + len(items) * 58 + 24
    out = svg(W, H, 'ppf', '喂奶：让身体每一处都有东西托着',
              '孩子来就乳，用枕头把孩子垫到乳房高度，不要人弯腰去够。坐着喂：背后垫枕头，脚下垫小凳，肩膀放松。'
              '侧躺喂：头下枕头够高、脖子直，背后再垫一个。不要一个姿势太久，左右轮换，坐、躺、半躺换着来。喂完慢慢转头、耸肩、扩胸。')
    y = 10
    for c, a, b in items:
        out.append(box(8, y, 384, 50, c, '.13'))
        out.append(f'<rect x="16" y="{y + 9}" width="6" height="32" rx="3" class="{c} fillc"/>')
        out.append(text(32, y + 21, a, 'tn'))
        out.append(text(32, y + 39, b, 'ts'))
        y += 58
    out.append(text(392, H - 6, 'Ratajczak 2024、Aburub 2022 · 编者整理', 'ts', 'end'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：哪些办法有证据 ----------------
def ladder():
    W = 400
    tiers = [('f1', '随机试验支持', ['针对性的稳定练习：产后骨盆带痛（Stuge 2004）', '打一针激素：妈妈手（16 个试验汇总）', '运动：孕期腰痛和骨盆痛（考克兰综述）']),
             ('f3', '有一些证据', ['晚上戴护腕：腕管综合征', '针灸：孕期骨盆带痛（单个试验）', '改喂奶姿势、缩短每次时间（调查研究）']),
             ('f4', '证据不足，舒服就用', ['热敷、冷敷', '按摩、贴扎']),
             ('f6', '没有证据', ['捂着不碰水、不洗澡', '“月子病一辈子好不了”'])]
    H = 10 + sum(36 + len(t[2]) * 18 for t in tiers) + 20
    out = svg(W, H, 'ppl', '哪些办法有证据：从强到弱',
              '随机试验支持：针对性的稳定练习治疗产后骨盆带痛；打一针激素治疗妈妈手；运动减轻孕期腰痛和骨盆痛。'
              '有一些证据：晚上戴护腕治疗腕管综合征；针灸治疗孕期骨盆带痛；改喂奶姿势。证据不足，舒服就用：热敷冷敷、按摩、贴扎。'
              '没有证据：捂着不碰水、不洗澡；“月子病一辈子好不了”的说法。')
    y = 10
    for c, name, lines in tiers:
        h = 36 + len(lines) * 18
        out.append(box(8, y, 384, h - 6, c, '.13'))
        out.append(text(18, y + 20, name, 'tn'))
        for k, ln in enumerate(lines):
            out.append(text(28, y + 40 + k * 18, '· ' + ln, 'ts'))
        y += h
    out.append(text(392, H - 6, '编者根据本篇引用的研究整理', 'ts', 'end'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：浑身酸痛，先分三条路 ----------------
def check():
    W, H = 400, 404
    out = svg(W, H, 'ppc', '浑身酸痛：先分三条路',
              '第一条路，马上去医院：一条腿又肿又痛、胸痛气短、发烧、关节红肿发热、手没力气拿不住东西、有伤害自己的念头。'
              '第二条路，近期去查血：手指脚趾小关节肿痛、早上僵硬超过一小时、两边对称；或者特别乏力、怕冷或心慌手抖、体重变化大。'
              '查血常规和铁蛋白、甲状腺功能和抗体、血沉和 C 反应蛋白、类风湿因子和抗 CCP 抗体、维生素 D。'
              '第三条路，没有这些：改抱法和喂法、慢慢练、睡够；四到六周不见好转，去康复科或骨科。')
    out.append(box(110, 8, 180, 36, 'f3', '.18'))
    out.append(text(200, 31, '产后浑身酸痛', 'tn', 'middle'))
    paths = [('f6', '马上去医院', ['一条腿又肿又痛', '胸痛、气短', '发烧、关节红肿发热', '手没力气、拿不住东西', '有伤害自己的念头']),
             ('f5', '近期去查血', ['手指脚趾小关节肿痛', '早上僵硬超过一小时', '特别乏力、怕冷或心慌', '体重变化大', '挂风湿免疫科']),
             ('f1', '先自己调理', ['改抱法、改喂法', '慢慢练回力量', '家人分担夜里', '止痛药问医生', '四到六周不好转：康复科'])]
    for i, (c, name, lines) in enumerate(paths):
        x = 8 + i * 130
        out.append(arrow(200, 46, x + 62, 66))
        out.append(box(x, 68, 124, 172, c, '.14'))
        out.append(text(x + 62, 90, name, 'tn', 'middle'))
        for k, ln in enumerate(lines):
            for j, l2 in enumerate(wrap(ln, 112, 10.5)[:1]):
                out.append(text(x + 62, 114 + k * 26, l2, 'ts', 'middle'))
    out.append(box(8, 254, 384, 122, 'f5', '.10'))
    out.append(text(18, 276, '查血可以请医生考虑这些：', 'tn'))
    tests = ['血常规、铁蛋白（贫血、缺铁）', '甲状腺功能、甲状腺抗体（产后甲状腺炎）', '血沉、C 反应蛋白（有没有炎症）',
             '类风湿因子、抗 CCP 抗体（类风湿关节炎）', '维生素 D']
    for k, t in enumerate(tests):
        out.append(text(28, 298 + k * 17, '· ' + t, 'ts'))
    out.append(text(392, 398, 'Kamel 2014、Nguyen 2019、Silman 1992 · 编者整理', 'ts', 'end'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：大概多久会好 ----------------
def course():
    W = 400
    rows = [('f6', '妈妈手', '香港：产后 2 个月，八成多还在痛', '孩子长大、抱得少会减轻；打针后约七成多完全缓解'),
            ('f5', '腕管综合征（手麻）', '多在产后慢慢消退', '有的要到断奶以后'),
            ('f4', '腰痛、骨盆带痛', '产后严重的约 7%', '孕期就很痛、很怕动的人，容易拖久'),
            ('f3', '腹直肌分离', '6 周约 60% → 12 个月约 33%', '分离本身和腰骨盆痛多少没有差别'),
            ('f1', '肩颈', '跟姿势走', '换姿势、缩短每次喂奶，常在几周内减轻')]
    H = 10 + len(rows) * 72 + 24
    out = svg(W, H, 'ppk', '大概多久会好：多数会一点点好起来',
              '妈妈手：香港的调查里，产后 2 个月八成多还在痛；孩子长大、抱得少会减轻，超声引导打针后约七成多完全缓解。'
              '腕管综合征：多在产后慢慢消退，有的要到断奶以后。腰痛和骨盆带痛：产后严重的约 7%；孕期就很痛、很怕动的人容易拖久。'
              '腹直肌分离：6 周约 60%，12 个月约 33%；有没有分离，腰骨盆痛差不多。肩颈：跟姿势走，常在几周内减轻。')
    y = 10
    for c, name, a, b in rows:
        out.append(box(8, y, 384, 64, c, '.13'))
        out.append(f'<rect x="16" y="{y + 9}" width="6" height="46" rx="3" class="{c} fillc"/>')
        out.append(text(32, y + 21, name, 'tn'))
        out.append(text(32, y + 39, a, 'ts'))
        out.append(text(32, y + 55, b, 'ts'))
        y += 72
    out.append(text(392, H - 6, 'Sit 2017、He 2023、Wu 2004、Burani 2023、Sperstad 2016', 'ts', 'end'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：一家人能做的事 ----------------
def family():
    W = 400
    stages = [('f1', '妈妈', '先照顾好自己', '改抱法喂法 · 每天练一点 · 说出来哪里疼'),
              ('f4', '丈夫', '接一班夜里', '夜里冲奶、换尿布、拍嗝 · 抱孩子的活多做'),
              ('f3', '老人', '帮忙不添堵', '不逼着捂、不说“月子病好不了”'),
              ('f5', '医生和康复师', '查清楚、教动作', '查血排除别的病 · 手把手教练习'),
              ('f6', '教会和朋友', '送一顿饭', '来看看、陪说话 · 让她睡一个午觉')]
    y = 8
    out = []
    for c, who, verb, s in stages:
        out.append(box(8, y, 384, 62, c))
        out.append(f'<rect x="16" y="{y + 9}" width="104" height="44" rx="10" class="{c} fillc"/>')
        out.append(text(68, y + 28, who, 'tnode2 b', 'middle'))
        out.append(text(68, y + 44, verb, 'tnode2 s', 'middle'))
        for k, ln in enumerate(wrap(s, 256)[:2]):
            out.append(text(130, y + 28 + k * 18, ln, 'tw'))
        y += 70
    H = y + 20
    head = svg(W, H, 'ppz', '一家人一起，让妈妈少疼一点',
               '妈妈：先照顾好自己，改抱法喂法，每天练一点，说出来哪里疼。丈夫：接一班夜里，冲奶、换尿布、拍嗝，抱孩子的活多做。'
               '老人：帮忙不添堵，不逼着捂，不说月子病好不了。医生和康复师：查血排除别的病，手把手教练习。教会和朋友：送一顿饭，来看看、陪说话，让她睡一个午觉。')
    out = head + out
    out.append(text(200, H - 6, '编者根据本篇引用的研究整理', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
