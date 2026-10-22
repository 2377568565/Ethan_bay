# 《“我原谅你”，为什么要用血来写？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
# 颜色的意思在本页固定：红（f6）＝罪与死；金（f4）＝上帝的恩典、十字架；蓝绿（f1）、蓝（f3）＝中性的分类。
from history_svg import text


def _box(x, y, w, h, c, rx=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{c} fillc"/>'


# ---------------- 图：“血”在圣经里是什么意思 ----------------
def life():
    W, H = 400, 400
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="blf1t blf1d">',
           '<title id="blf1t">“血”在圣经里是什么意思</title>',
           '<desc id="blf1d">从上到下三步。一、血在身体里：活物的生命是在血中（利17:11）。'
           '二、血流出来：生命交出去了，也就是死；保罗说“靠着他的血称义”，接着说“藉着上帝儿子的死得与上帝和好”（罗5:9-10）。'
           '三、血在坛上：一条命替另一条命交出来，“可以在坛上为你们的生命赎罪”（利17:11）。'
           '结论：“流血”的意思不是血有魔力，而是有生命替我们交出来。</desc>']
    rows = [('f1', '血在身体里', '＝生命', '“活物的生命是在血中”（利17:11）'),
            ('f6', '血流出来', '＝生命交出去，就是死', '“靠着他的血”＝“藉着…死”（罗5:9-10）'),
            ('f4', '血在坛上', '＝一条命替另一条命交出', '“为你们的生命赎罪”（利17:11）')]
    for i, (c, a, b, r) in enumerate(rows):
        y = 14 + i * 108
        out.append(_box(30, y, 340, 80, c))
        out.append(text(200, y + 26, a + ' ' + b, 'tnode2', 'middle'))
        out.append(text(200, y + 56, r, 'tnode2', 'middle'))
        if i < 2:
            out.append(f'<path d="M200 {y + 80} L200 {y + 108}" class="flow"/>')
    out.append(text(W / 2, 362, '“流血”不是说血有魔力，', 'ts', 'middle'))
    out.append(text(W / 2, 386, '而是说：有一条生命替我们交出来了', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：罪，就是离开生命的源头 ----------------
def source():
    W, H = 400, 380
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="blf2t blf2d">',
           '<title id="blf2t">罪，就是离开生命的源头</title>',
           '<desc id="blf2d">左边：葡萄树和枝子连在一起，枝子活着、结果子（约15:5）；这代表人和上帝连在一起，上帝是生命的源头（约5:26）。'
           '右边：枝子离了葡萄树，就枯干（约15:6）；这代表罪使人与上帝隔绝（赛59:2），结局是死（罗6:23）。'
           '下方说明：死不是上帝随意加上的惩罚，而是离开生命源头的必然结果（怀爱伦《历代愿望》764页）。比方出自耶稣自己。</desc>']
    cols = [(14, 'f4', '连着', ['上帝：生命的源头', '“父怎样在自己有生命”', '（约5:26）', '枝子连在树上：活着', '“常在我里面的…多结果子”', '（约15:5）']),
            (206, 'f6', '断开', ['罪：自己离开源头', '“你们的罪孽使你们', '与上帝隔绝”（赛59:2）', '枝子离了树：枯干', '“罪的工价乃是死”', '（罗6:23）'])]
    for x, c, a, rows in cols:
        out.append(_box(x, 14, 180, 270, c))
        out.append(text(x + 90, 44, a, 'tn hi', 'middle'))
        for i, s in enumerate(rows):
            out.append(text(x + 90, 82 + i * 34, s, 'tnode2', 'middle'))
    out.append(text(W / 2, 314, '死，不是上帝随手加上的惩罚，', 'ts', 'middle'))
    out.append(text(W / 2, 338, '而是离开生命源头的必然结果', 'ts', 'middle'))
    out.append(text(W / 2, 364, '（比方是耶稣自己用的：约15:5-6；参《历代愿望》764）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：“原谅”只有三条路 ----------------
def three():
    W, H = 400, 410
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="blf3t blf3d">',
           '<title id="blf3t">面对一笔真实的亏欠，只有三条路</title>',
           '<desc id="blf3d">第一条：让犯错的人自己赔——有公义，没有怜悯；对罪人来说，就是死（罗6:23）。'
           '第二条：当作没发生——没有公义，伤害也没有真正处理（出34:7“万不以有罪的为无罪”；箴17:15）。'
           '第三条：受亏欠的一方自己承担——公义和怜悯都在（太18:27“免了他的债”）。'
           '十字架是第三条路，而且承担的是上帝自己（林后5:19）。编者整理。</desc>']
    rows = [('f6', '① 让犯错的人自己赔', '有公义，没有怜悯：罪人只有死', '罗6:23'),
            ('f1', '② 当作没发生', '既没有公义，伤害也没有处理', '出34:7；箴17:15'),
            ('f4', '③ 受亏欠的一方自己承担', '公义和怜悯都在', '太18:27“免了他的债”')]
    for i, (c, a, b, r) in enumerate(rows):
        y = 14 + i * 104
        out.append(_box(20, y, 360, 84, c))
        out.append(text(200, y + 26, a, 'tnode2', 'middle'))
        out.append(text(200, y + 50, b, 'tnode2', 'middle'))
        out.append(text(200, y + 72, r, 'tnode2', 'middle'))
    out.append(text(W / 2, 352, '十字架是第三条路——', 'ts', 'middle'))
    out.append(text(W / 2, 376, '而且承担的，是上帝自己（林后5:19）', 'ts', 'middle'))
    out.append(text(W / 2, 400, '（编者整理）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：公义与慈爱在十字架相遇 ----------------
def meet():
    W, H = 400, 400
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="blf4t blf4d">',
           '<title id="blf4t">公义与慈爱在十字架相遇</title>',
           '<desc id="blf4d">左上是公义：“公义和公平是你宝座的根基”（诗89:14），“万不以有罪的为无罪”（出34:7）。'
           '右上是慈爱：“有怜悯有恩典的上帝”（出34:6），“喜爱施恩”（弥7:18）。'
           '两条线向下汇合到中间的十字架：上帝“自己为义，也称信耶稣的人为义”（罗3:26）。'
           '下方经文：“慈爱和诚实彼此相遇；公义和平安彼此相亲”（诗85:10）。</desc>']
    out.append(_box(10, 14, 170, 92, 'f3'))
    out.append(text(95, 40, '公义', 'tnode2', 'middle'))
    out.append(text(95, 66, '“宝座的根基”（诗89:14）', 'tnode2', 'middle'))
    out.append(text(95, 90, '“万不以有罪的为无罪”', 'tnode2', 'middle'))
    out.append(_box(220, 14, 170, 92, 'f1'))
    out.append(text(305, 40, '慈爱', 'tnode2', 'middle'))
    out.append(text(305, 66, '“有怜悯有恩典”（出34:6）', 'tnode2', 'middle'))
    out.append(text(305, 90, '“喜爱施恩”（弥7:18）', 'tnode2', 'middle'))
    out.append('<path d="M95 106 L188 196" class="flow"/><path d="M305 106 L212 196" class="flow"/>')
    # 十字架
    out.append(_box(186, 178, 28, 120, 'f4', 4))
    out.append(_box(156, 204, 88, 24, 'f4', 4))
    out.append(text(W / 2, 324, '上帝“自己为义”，', 'ts', 'middle'))
    out.append(text(W / 2, 346, '又“称信耶稣的人为义”（罗3:26）', 'ts', 'middle'))
    out.append(text(W / 2, 384, '“慈爱和诚实彼此相遇；公义和平安彼此相亲”（诗85:10）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：撒但的三个指控，十字架的回答 ----------------
def charge():
    W, H = 400, 450
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="blf5t blf5d">',
           '<title id="blf5t">撒但的三个指控，十字架的回答</title>',
           '<desc id="blf5d">左边红色是撒但的三个指控，右边金色是十字架的回答。'
           '一、律法是不能遵守的——耶稣作为人完全遵守了（来4:15；约8:46）。'
           '二、公义和怜悯不能并存，犯了罪就不可能被赦免——十字架显明上帝的公义没有毁掉祂的怜悯，罪可以被赦免（罗3:26）。'
           '三、堕落的人类从此是撒但合法的子民——上帝赐下儿子承担刑罚，把人赎回（可10:45）。'
           '指控的内容依据怀爱伦《历代愿望》761—762页、《先祖与先知》69页；圣经说撒但是“控告我们弟兄的”（启12:10）。</desc>']
    out.append(text(102, 26, '撒但的指控', 'tn hi', 'middle'))
    out.append(text(298, 26, '十字架的回答', 'tn hi', 'middle'))
    rows = [('律法是不能遵守的', '', '耶稣作为人完全遵守了', '来4:15；约8:46'),
            ('公义和怜悯不能并存，', '罪人不可能被赦免', '公义没有毁掉怜悯，', '罪可以被赦免（罗3:26）'),
            ('犯了罪的人类', '从此是他的子民', '上帝赐下儿子，', '把人赎回（可10:45）')]
    for i, (a1, a2, b1, b2) in enumerate(rows):
        y = 44 + i * 112
        out.append(_box(10, y, 184, 90, 'f6'))
        out.append(_box(206, y, 184, 90, 'f4'))
        out.append(text(102, y + 40, a1, 'tnode2', 'middle'))
        out.append(text(102, y + 64, a2, 'tnode2', 'middle'))
        out.append(text(298, y + 40, b1, 'tnode2', 'middle'))
        out.append(text(298, y + 64, b2, 'tnode2', 'middle'))
    out.append(text(W / 2, 400, '撒但是“昼夜控告我们弟兄的”（启12:10）', 'ts', 'middle'))
    out.append(text(W / 2, 424, '指控的内容据《历代愿望》761—762、《先祖与先知》69', 'tw', 'middle'))
    out.append(text(W / 2, 444, '（怀爱伦著作，作补充）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：谁为谁献上？ ----------------
def who():
    W, H = 400, 420
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="blf6t blf6d">',
           '<title id="blf6t">谁为谁献上？人想象的献祭与圣经启示的献祭</title>',
           '<desc id="blf6d">左边：人想象的献祭，方向是从人到神，目的是平息神的怒气、换取好处，甚至把儿女烧了献上；'
           '上帝说这是祂“所憎嫌所恨恶的”（申12:31），“这并不是我所吩咐的，也不是我心所起的意”（耶7:31）。'
           '右边：圣经启示的献祭，方向是从上帝到人：“上帝必自己预备作燔祭的羊羔”（创22:8）；'
           '“不是我们爱上帝，乃是上帝爱我们，差他的儿子为我们的罪作了挽回祭”（约壹4:10）。'
           '下方：禁止人献上儿女的上帝，自己献上了儿子（罗8:32）。编者整理。</desc>']
    cols = [(10, 'f6', '人想象的献祭', '人 → 神', ['为了平息神的怒气', '为了换取好处', '甚至焚烧儿女献上', '上帝：“所憎嫌所恨恶的”', '（申12:31）']),
            (206, 'f4', '圣经启示的献祭', '上帝 → 人', ['“上帝必自己预备', '作燔祭的羊羔”（创22:8）', '“乃是上帝爱我们，', '差他的儿子…作了挽回祭”', '（约壹4:10）'])]
    for x, c, a, d, rows in cols:
        out.append(_box(x, 14, 184, 300, c))
        out.append(text(x + 92, 42, a, 'tnode2', 'middle'))
        out.append(text(x + 92, 76, d, 'tnode2', 'middle'))
        for i, s in enumerate(rows):
            out.append(text(x + 92, 120 + i * 36, s, 'tnode2', 'middle'))
    out.append(text(W / 2, 346, '禁止人献上儿女的上帝，', 'ts', 'middle'))
    out.append(text(W / 2, 370, '自己献上了儿子（罗8:32）', 'ts', 'middle'))
    out.append(text(W / 2, 400, '（编者整理）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：十字架的五幅圣经画面 ----------------
def five():
    W, H = 400, 470
    out = [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="blf7t blf7d">',
           '<title id="blf7t">十字架的五幅圣经画面</title>',
           '<desc id="blf7d">圣经用五幅画面讲同一个十字架。法庭：从被定罪到称义（罗3:24-26；罗8:1）。'
           '圣殿：从不洁到洁净、挽回（来9:14；约壹2:2）。市场：从奴仆到被赎出（可10:45；彼前1:18-19）。'
           '战场：从被掳到得胜（来2:14-15；西2:15）。家庭：从仇敌到和好（罗5:10；林后5:18-20）。'
           '五幅画面不互相排斥，是从五个角度看同一件事。</desc>']
    rows = [('f3', '法庭', '被定罪 → 称义', '罗3:24-26；罗8:1'),
            ('f4', '圣殿', '不洁 → 洁净、挽回', '来9:14；约壹2:2'),
            ('f1', '市场', '作奴仆 → 被赎出', '可10:45；彼前1:18-19'),
            ('f6', '战场', '被掳 → 得胜', '来2:14-15；西2:15'),
            ('f4', '家庭', '作仇敌 → 和好', '罗5:10；林后5:18-20')]
    for i, (c, a, b, r) in enumerate(rows):
        y = 14 + i * 80
        out.append(_box(20, y, 360, 64, c))
        out.append(text(70, y + 38, a, 'tnode2', 'middle'))
        out.append(text(250, y + 27, b, 'tnode2', 'middle'))
        out.append(text(250, y + 50, r, 'tnode2', 'middle'))
    out.append(text(W / 2, 438, '五幅画面，同一个十字架：', 'ts', 'middle'))
    out.append(text(W / 2, 460, '不是互相排斥，而是从五个角度看同一件事', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)
