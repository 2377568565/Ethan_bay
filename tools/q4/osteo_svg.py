# 健康栏目 05《骨质疏松与跌倒》页面里的逻辑图（SVG，宽 400；颜色用页面的类，夜间模式自动变）
# 颜色的意思和前几篇一样：f1 青绿＝保护、能做的事；f6 红＝伤害、疾病；f4 金＝时间和警报；f5 紫＝药物和医院；f3 蓝＝中性的器官和阶段
import math
from history_svg import text
from diabetes_svg import arrow, node, svg, bars

CV = dict(f1='c1', f3='c3', f4='c4', f5='c5', f6='c6')


def box(x, y, w, h, c, op='.22'):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="{c} fillc" opacity="{op}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" class="cn {c}" style="--c:var(--{CV[c]});fill:none"/>')


def wrap(s, w, px=11.5):
    """按“ · ”分开的短语排成几行"""
    lines, line = [], ''
    for p in s.split(' · '):
        cand = (line + ' · ' + p) if line else p
        if len(cand) * px > w and line:
            lines.append(line)
            line = p
        else:
            line = cand
    lines.append(line)
    return lines


# ---------------- 图：骨折的两条路 ----------------
def two():
    W, H = 400, 330
    out = svg(W, H, 'ost', '骨折的两条路：骨头变脆，加上摔了一跤',
              '左边是骨头这一边：年轻时存下的骨头少、绝经和年纪让骨头流失、伤骨头的药和病、活动少、钙和维生素 D 吃得不够，都会让骨头变脆。'
              '右边是跌倒这一边：腿上没力气、平衡变差、眼睛看不清、让人头晕的药、家里地滑灯暗，都会让人更容易摔、摔得更重。'
              '两条路在下面汇合，就是骨折。只防一边，只防住了一半：只补钙不防摔，重重一摔照样会断；只防摔不管骨头，总有防不住的一跤。')
    cols = [(8, 'f3', '骨头这一边：骨头变脆', ['年轻时存得少', '绝经、年纪', '伤骨头的药和病', '活动少', '钙和维生素 D 不够']),
            (208, 'f4', '跌倒这一边：更容易摔', ['腿上没力气', '平衡变差', '眼睛看不清', '让人头晕的药', '家里地滑、灯暗'])]
    for x, c, title, items in cols:
        out.append(box(x, 8, 184, 190, c))
        out.append(text(x + 92, 30, title, 'tn', 'middle'))
        for i, it in enumerate(items):
            out.append(f'<rect x="{x + 14}" y="{42 + i * 30}" width="156" height="24" rx="12" class="{c} fillc"/>')
            out.append(text(x + 92, 58 + i * 30, it, 'tnode2 b', 'middle'))
    out.append(arrow(100, 200, 172, 236))
    out.append(arrow(300, 200, 228, 236))
    out.append(f'<rect x="120" y="238" width="160" height="40" rx="20" class="f6 fillc"/>')
    out.append(text(200, 263, '骨折', 'tnode2 b', 'middle'))
    out.append(text(200, 300, '只防一边，只防住了一半', 'tw', 'middle'))
    out.append(text(200, 320, '编者整理的示意', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：一生的骨头账 ----------------
def life():
    W, H = 400, 334
    out = svg(W, H, 'osl', '一生的骨头账：年轻时存，中年以后取（示意图）',
              '横轴是年龄，从 0 到 90 岁；纵轴是骨量的多少。这是示意图，不是某一项研究的真实数据。骨量从小慢慢增加，二三十岁前后到达最高，叫“峰值骨量”；'
              '以后慢慢减少。女性在绝经前后的几年里流失得特别快，所以比男性更早碰到“骨质疏松”的那条线。'
              '虚线表示年轻时存得更多的女性：同样的流失速度，碰到那条线的时间晚了很多年。生活方式能影响峰值骨量的百分之二十到四十。')
    x0, x1, y0, y1 = 40, 386, 222, 30
    X = lambda a: x0 + (x1 - x0) * a / 90
    Y = lambda v: y0 - (y0 - y1) * v / 100
    out.append(f'<path d="M{x0} {y0} L{x1} {y0}" class="ax"/><path d="M{x0} {y0} L{x0} {y1 - 6}" class="ax"/>')
    for a in (0, 20, 30, 50, 70, 90):
        out.append(text(X(a), y0 + 16, f'{a}', 'ta', 'middle'))
    out.append(text((x0 + x1) / 2, y0 + 32, '年龄（岁）', 'ta', 'middle'))
    out.append(text(x0 - 6, y1 + 4, '骨量', 'ta', 'end'))

    def curve(pts):
        return 'M' + ' L'.join(f'{X(a):.1f} {Y(v):.1f}' for a, v in pts)
    men = [(0, 12), (10, 35), (18, 70), (25, 86), (32, 90), (45, 86), (60, 78), (75, 68), (90, 58)]
    wom = [(0, 11), (10, 33), (18, 64), (25, 76), (32, 78), (45, 74), (50, 70), (55, 56), (60, 50), (75, 38), (90, 28)]
    hi = [(0, 11), (10, 36), (18, 72), (25, 88), (32, 90), (45, 86), (50, 82), (55, 68), (60, 62), (75, 50), (90, 40)]
    tl = 42
    out.append(f'<path d="M{x0} {Y(tl):.1f} L{x1} {Y(tl):.1f}" class="cn dash" style="--c:var(--c6);stroke-width:1.5;fill:none"/>')
    out.append(text(X(22), Y(tl) + 15, '骨质疏松的那条线', 'ts'))
    out.append(f'<path d="{curve(men)}" class="cn" style="--c:var(--c3);stroke-width:2.5;fill:none"/>')
    out.append(f'<path d="{curve(wom)}" class="cn" style="--c:var(--c4);stroke-width:2.5;fill:none"/>')
    out.append(f'<path d="{curve(hi)}" class="cn dash" style="--c:var(--c1);stroke-width:2;fill:none"/>')
    lg = [('c3', '', '男性'), ('c4', '', '女性'), ('c1', ' dash', '年轻时存得多的女性')]
    lx = 44
    for c, d, t in lg:
        out.append(f'<path d="M{lx} 274 L{lx + 22} 274" class="cn{d}" style="--c:var(--{c});stroke-width:2.5;fill:none"/>')
        out.append(text(lx + 28, 278, t, 'tw'))
        lx += 28 + len(t) * 13 + 30
    out.append(f'<rect x="{X(4):.1f}" y="{y1 - 4}" width="{X(30) - X(4):.1f}" height="20" rx="10" class="f1 fillc"/>')
    out.append(text((X(4) + X(30)) / 2, y1 + 10, '存钱的年纪', 'tnode2 b', 'middle'))
    out.append(f'<rect x="{X(47):.1f}" y="{y1 - 4}" width="{X(64) - X(47):.1f}" height="20" rx="10" class="f4 fillc"/>')
    out.append(text((X(47) + X(64)) / 2, y1 + 10, '绝经前后', 'tnode2 b', 'middle'))
    out.append(text(200, 304, '峰值越高、流失越慢，碰到那条线就越晚', 'tw', 'middle'))
    out.append(text(200, 324, '示意图；生活方式影响峰值骨量的 20%—40%（Weaver 2016）', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：让老人容易摔的四类原因 ----------------
def wheel():
    W, H = 400, 304
    out = svg(W, H, 'osw', '老人为什么容易摔：四类原因常常一起出现',
              '四个方块是让老人更容易跌倒的四类原因。身体：肌肉少、平衡差、身体衰弱（衰弱的老人跌倒风险约是别人的 1.5 倍）、以前摔过、视力差。'
              '疾病：中风、帕金森病、糖尿病、抑郁、疼痛。药物：安眠镇静药、抗抑郁药、降压药，吃的药种类多。'
              '环境和习惯：夜里光线暗、地面湿滑、穿拖鞋、独居、喝酒。跌倒很少只有一个原因，所以防摔也要几方面一起做。')
    quads = [(8, 8, 'f3', '身体', '肌肉少 · 平衡差 · 衰弱（约 1.5 倍）· 以前摔过 · 眼睛花'),
             (206, 8, 'f6', '疾病', '中风 · 帕金森病 · 糖尿病 · 抑郁 · 疼痛'),
             (8, 160, 'f5', '药物', '安眠镇静药 · 抗抑郁药 · 降压药 · 药的种类多'),
             (206, 160, 'f4', '环境和习惯', '夜里灯暗 · 地滑 · 穿拖鞋 · 独居 · 喝酒')]
    for x, y, c, t, s in quads:
        out.append(box(x, y, 186, 116, c))
        out.append(text(x + 14, y + 24, t, 'tn'))
        for k, ln in enumerate(wrap(s, 158)):
            out.append(text(x + 14, y + 50 + k * 20, ln, 'tw'))
    out.append(f'<rect x="150" y="128" width="100" height="28" rx="14" class="f6 fillc"/>')
    out.append(text(200, 146, '跌倒', 'tnode2 b', 'middle'))
    for x1, y1, x2, y2 in ((120, 124, 152, 134), (280, 124, 248, 134), (120, 160, 152, 150), (280, 160, 248, 150)):
        out.append(arrow(x1, y1 if y1 < 140 else y1, x2, y2, head=5))
    out.append(text(200, 296, '跌倒很少只有一个原因（Xu 2022、Yang 2023、Woolcott 2009）', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：一跤之后的下坡路 ----------------
def spiral():
    W, H = 400, 340
    out = svg(W, H, 'oss', '一跤之后的下坡路：一件事推着一件事往下走',
              '六个环节连成一个圈：摔倒；骨折、手术、住院；疼和怕，就躺着；躺着肌肉就掉，健康老人卧床十天腿的力量少了约百分之十三；'
              '力气小了、心里怕了，更不敢走，髋部骨折后约三分之二的老人害怕再摔；越不走越不稳，又摔一跤，而骨折过一次的人再骨折的风险约翻倍。'
              '髋部骨折后头三个月，死亡风险是同龄人的五到八倍。每一个环节都可以出手把圈截断：练平衡、改环境、治骨头、早下床康复、帮老人克服害怕。')
    cx, cy, R = 200, 158, 112
    items = [('摔倒', '', 'f6'), ('骨折、手术', '住院', 'f6'), ('疼、怕', '就躺着', 'f4'),
             ('肌肉掉得快', '卧床 10 天力气少 13%', 'f4'), ('更不敢走', '约三分之二害怕再摔', 'f4'), ('走不稳', '再骨折风险约翻倍', 'f6')]
    pts = []
    for i in range(6):
        a = -math.pi / 2 + i * math.pi / 3
        pts.append((cx + R * math.cos(a), cy + R * math.sin(a)))
    for i in range(6):
        (xa, ya), (xb, yb) = pts[i], pts[(i + 1) % 6]
        dx, dy = xb - xa, yb - ya
        L = math.hypot(dx, dy)
        sh = 40 / L
        out.append(arrow(xa + dx * sh, ya + dy * sh, xb - dx * sh, yb - dy * sh))
    for (x, y), (t1, t2, c) in zip(pts, items):
        w = 132
        out.append(node(x - w / 2, y - 21, w, 42, c, t1, t2))
    out.append(text(cx, cy - 6, '下坡路', 'tn', 'middle'))
    out.append(text(cx, cy + 14, '每一环都能截断', 'tw', 'middle'))
    out.append(text(200, 314, '髋部骨折后头三个月，死亡风险是同龄人的 5—8 倍', 'tw', 'middle'))
    out.append(text(200, 332, '数据：Kortebein 2008、Ren 2026、Klotzbuecher 2000、Haentjens 2010', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：几种药减少了多少骨折 ----------------
def drugs():
    return bars('osd', '骨质疏松的药，在随机试验里减少了多少骨折',
                '三个大型随机双盲、安慰剂对照试验，用了三年。阿仑膦酸钠（一周一片）：已有脊椎骨折的女性，新的脊椎骨折少了约 47%，髋部骨折少了约 51%。'
                '唑来膦酸（一年一次点滴）：脊椎骨折少了 70%，髋部骨折少了 41%。地舒单抗（半年一针）：脊椎骨折少了 68%，髋部骨折少了 40%。'
                '另一项试验：髋部骨折手术后 90 天内开始用唑来膦酸，新的骨折少了 35%，死亡少了 28%。这些试验都由药厂资助。',
                [('新的脊椎骨折少了', [('阿仑膦酸钠', 47, 'f5'), ('唑来膦酸', 70, 'f5'), ('地舒单抗', 68, 'f5')]),
                 ('髋部骨折少了', [('阿仑膦酸钠', 51, 'f5'), ('唑来膦酸', 41, 'f5'), ('地舒单抗', 40, 'f5')]),
                 ('髋部骨折以后用唑来膦酸', [('新的骨折少了', 35, 'f1'), ('死亡少了', 28, 'f1')])],
                '%', 80, '数据：Black 1996、Black 2007、Cummings 2009、Lyles 2007')


# ---------------- 图：好处和风险放在秤上 ----------------
def weigh():
    return bars('osw2', '用药三年：防住的髋部骨折和多出的不典型骨折',
                '美国南加州约 19.6 万名用双膦酸盐的女性的研究，按模型估算用药三年的好处和风险。白人女性：防住 149 例髋部骨折，多出 2 例不典型股骨骨折。'
                '亚洲女性：防住 91 例髋部骨折，多出 8 例不典型股骨骨折。亚洲女性发生不典型骨折的风险约是白人的 4.8 倍，但好处仍然明显大于风险；停药以后，这种风险很快下降。',
                [('白人女性', [('防住的髋部骨折', 149, 'f1'), ('多出的不典型骨折', 2, 'f6')]),
                 ('亚洲女性', [('防住的髋部骨折', 91, 'f1'), ('多出的不典型骨折', 8, 'f6')])],
                ' 例', 170, '同样人数下的估算；数据：Black 2020（《新英格兰医学杂志》）')


# ---------------- 图：能少摔多少 ----------------
def falls():
    return bars('osf', '这些办法能让老人少摔多少',
                '运动：专门为防摔改编的太极，和只做伸展的组比，跌倒少了约 58%，和综合运动比也少了 31%；平衡加力量练习，跌倒可能少了 34%；'
                '平衡和功能性练习少了 24%；太极（汇总）少了约 19%。环境和饮食：改造家里环境，跌倒风险高的老人少了 38%，所有老人合起来少了 26%；'
                '养老院饭菜里加奶制品，跌倒少了 11%、骨折少了 33%。',
                [('运动（随机试验和汇总）', [('防摔改编的太极（对比伸展）', 58, 'f1'), ('平衡加力量', 34, 'f1'), ('平衡和功能练习', 24, 'f1'), ('太极（汇总）', 19, 'f1')]),
                 ('环境和饮食', [('改造家里（高风险老人）', 38, 'f1'), ('改造家里（所有老人）', 26, 'f1'), ('养老院加奶制品', 11, 'f1')])],
                '%', 65, '数据：Li 2018、Sherrington 2019、Clemson 2023、Iuliano 2021')


# ---------------- 图：补充剂，看人 ----------------
def supp():
    W, H = 400, 352
    out = svg(W, H, 'osp', '补充剂：补了有没有用，要看是谁在补',
              '上面一层：缺的人、弱的人补了有用。法国养老院平均 84 岁的女性每天补钙和维生素 D，髋部骨折少了 43%；维生素 D 偏低的养老院老人补维生素 D，跌倒次数可能少了约三分之一；'
              '养老院饭菜里加奶制品，骨折少了 33%。中间一层：不缺的健康人常规补，看不出用处：社区老人的 33 个随机试验、VITAL 试验每天 2000 国际单位维生素 D、'
              'COSMOS 试验的复合维生素矿物质片，骨折都没有减少。下面一层：用法不对反而有害：一年一次 50 万国际单位维生素 D，跌倒多 15%、骨折多 26%；钙加维生素 D 让肾结石多了 17%。')
    rows = [('f1', '补了有用：缺的人、弱的人', '养老院老人补钙和 D，髋部骨折少 43% · 维生素 D 偏低的老人补 D，跌倒可能少三分之一 · 养老院加奶制品，骨折少 33%'),
            ('f3', '看不出用处：不缺的健康人', '社区老人补钙或 D（33 个试验） · 每天 2000 单位维生素 D（VITAL） · 复合维生素矿物质片（COSMOS）'),
            ('f6', '反而有害：用法不对', '一年一次 50 万单位维生素 D：跌倒多 15%、骨折多 26% · 钙加 D：肾结石多 17%')]
    y = 10
    for c, t1, t2 in rows:
        out.append(box(8, y, 384, 94, c, '.26'))
        out.append(text(22, y + 22, t1, 'tn'))
        for k, ln in enumerate(wrap(t2, 352)[:3]):
            out.append(text(22, y + 44 + k * 18, ln, 'tw'))
        y += 104
    out.append(text(200, 334, '先算饭里吃了多少，再补差额；不缺不必补，不追求大剂量', 'tw', 'middle'))
    out.append(text(200, 350, '数据：第七部分引用的八项研究（见资料出处）', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：一生的功课 ----------------
def ages():
    W, H = 400, 372
    out = svg(W, H, 'osa', '一生的骨头功课：年轻多存，中年少取，老了少摔',
              '从上到下是五个阶段。孩子和青少年：多跑多跳，奶和豆制品，这是存骨头最快的几年。二三十岁：钙吃够，做负重和力量练习，不过度节食。'
              '四五十岁：女性绝经前后保住肌肉，男性少喝酒不吸烟，开始练平衡。六十五岁以上：问医生查骨密度，练平衡和太极，改造家里，查药箱和视力。'
              '骨折过一次以后：问是不是骨质疏松、要不要用药，尽早康复，认真防第二次。')
    stages = [('f1', '孩子、青少年', '多存', '多跑多跳 · 每天有奶或豆制品 · 多在户外'),
              ('f1', '二三十岁', '存满', '钙吃够 · 负重和力量练习 · 不过度节食'),
              ('f4', '四五十岁', '少取', '女性保住肌肉 · 男性少酒戒烟 · 开始练平衡'),
              ('f3', '六十五岁以上', '少摔', '查骨密度 · 练太极和平衡 · 改造家里 · 查药箱'),
              ('f5', '骨折过以后', '防第二次', '问要不要用药 · 尽早康复 · 别让害怕困住')]
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
