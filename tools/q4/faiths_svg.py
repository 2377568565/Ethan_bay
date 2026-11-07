# 《宗教这么多，为什么偏偏是耶稣？》页面里的图（SVG，样式用 history.py 的 CSS 和颜色，夜间模式自动变）
# 本页颜色固定：金（f4）＝基督教；蓝绿（f1）＝伊斯兰教；橙（f2）＝佛教；蓝（f3）＝道家与道教；灰（f0）＝中性。
from history_svg import text


def _box(x, y, w, h, c, rx=12):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" class="{c} fillc"/>'


def _svg(W, H, key, title, desc):
    return [f'<svg viewBox="0 0 {W} {H}" class="dg" role="img" aria-labelledby="fa{key}t fa{key}d">',
            f'<title id="fa{key}t">{title}</title>', f'<desc id="fa{key}d">{desc}</desc>']


REL = [('f1', '伊斯兰教'), ('f2', '佛教'), ('f3', '道教'), ('f4', '基督教')]


# ---------------- 图：四个宗教，回答四个问题 ----------------
def four():
    W, H = 400, 520
    Q = [('人出了什么问题？', [('忘记、', '不顺服真主'), ('苦：', '贪爱与无明'), ('失道、', '生命短促'), ('罪：与上帝', '隔绝')]),
         ('出路在哪里？', [('顺服：', '信仰和善功'), ('八正道、', '修行'), ('修道、养生、', '炼丹'), ('上帝来救：', '十字架')]),
         ('靠谁？', [('自己的行为', '＋真主的怜悯'), ('主要靠自己', '（净土宗靠', '佛的愿力）'), ('靠自己修炼',), ('靠耶稣，', '白白的恩典')]),
         ('最后去哪里？', [('乐园',), ('涅槃：', '贪爱止息'), ('成仙、', '与道合一'), ('新天新地，', '与上帝同住')])]
    out = _svg(W, H, 1, '四个宗教，怎样回答四个大问题',
               '四个问题，每个问题下面并排四格，从左到右是伊斯兰教、佛教、道教、基督教。'
               '一、人出了什么问题：伊斯兰教说人忘记、不顺服真主；佛教说一切是苦，根源是贪爱和无明；道教说人失了道、生命短促；基督教说罪使人与上帝隔绝。'
               '二、出路在哪里：伊斯兰教是顺服，信仰加善功；佛教是八正道和修行；道教是修道、养生、炼丹；基督教是上帝亲自来救，在十字架上。'
               '三、靠谁：伊斯兰教靠自己的行为加上真主的怜悯；佛教主要靠自己，净土宗靠阿弥陀佛的愿力；道教靠自己修炼；基督教靠耶稣，白白的恩典。'
               '四、最后去哪里：伊斯兰教是乐园；佛教是涅槃，贪爱止息；道教是成仙、与道合一；基督教是新天新地，与上帝同住。'
               '这是编者为对照而作的简化，每一格的依据见正文。')
    for i, (c, n) in enumerate(REL):
        out.append(_box(8 + i * 97, 8, 91, 28, c, 8))
        out.append(text(8 + i * 97 + 45.5, 27, n, 'tnode2', 'middle'))
    y = 48
    for q, cells in Q:
        out.append(text(10, y + 14, q, 'tn hi'))
        for i, (c, n) in enumerate(REL):
            out.append(_box(8 + i * 97, y + 22, 91, 76, c, 10))
            lines = cells[i]
            top = y + 22 + 38 - (len(lines) - 1) * 9.5 + 4
            for j, ln in enumerate(lines):
                out.append(text(8 + i * 97 + 45.5, top + j * 19, ln, 'tnode2', 'middle'))
        y += 108
    out.append(text(W / 2, 508, '（编者为对照所作的简化，依据见正文各章）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：《古兰经》里的耶稣和圣经里的耶稣 ----------------
def isa():
    W, H = 400, 580
    out = _svg(W, H, 2, '《古兰经》里的耶稣，和圣经里的耶稣',
               '中间金绿两色的一栏是两本书都说的：童贞女所生（古兰经3:47、19:20；路1:34-35）；称为弥赛亚（3:45；太16:16）；'
               '称为“从他发出的一句话”与“道”（3:45、4:171；约1:1、14）；行神迹、医病、叫死人复活（3:49；约11）；被接升天（4:158；徒1:9-11）；还要再来（伊斯兰传统；徒1:11）。'
               '下面左右两栏是说法不同的地方：《古兰经》说他只是使者（4:171、5:75），圣经说“道就是上帝”（约1:1），多马称他“我的主！我的上帝！”（约20:28）；'
               '《古兰经》说他没有被钉十字架（4:157），圣经说他钉十字架、死了、第三天复活（林前15:3-4）；'
               '《古兰经》说真主不会收养儿子（19:35），圣经说上帝差他的儿子来作挽回祭（约壹4:10）。')
    out.append(text(W / 2, 22, '两本书都说的', 'tn hi', 'middle'))
    same = [('童贞女所生', '3:47；19:20｜路1:34-35'), ('称为“弥赛亚”', '3:45｜太16:16'), ('“一句话”／“道”', '3:45；4:171｜约1:1、14'),
            ('行神迹、医病、叫死人复活', '3:49｜约11章'), ('被接升天', '4:158｜徒1:9-11'), ('还要再来', '伊斯兰传统｜徒1:11')]
    for i, (a, r) in enumerate(same):
        y = 34 + i * 46
        out.append(_box(30, y, 340, 40, 'f0', 10))
        out.append(text(200, y + 18, a, 'tnode2', 'middle'))
        out.append(text(200, y + 34, r, 'tnode2', 'middle'))
    y0 = 340
    out.append(text(102, y0, '《古兰经》说', 'tn hi', 'middle'))
    out.append(text(298, y0, '圣经说', 'tn hi', 'middle'))
    diff = [('只是一个使者', '4:171；5:75', '上帝的儿子，“道就是上帝”', '约1:1；20:28'),
            ('没有被钉十字架', '4:157', '钉十字架、死、复活', '林前15:3-4'),
            ('真主不会收养儿子', '19:35；112:3', '上帝差儿子作挽回祭', '约壹4:10')]
    for i, (a, ar, b, br) in enumerate(diff):
        y = y0 + 12 + i * 66
        out.append(_box(10, y, 184, 56, 'f1'))
        out.append(_box(206, y, 184, 56, 'f4'))
        out.append(text(102, y + 24, a, 'tnode2', 'middle'))
        out.append(text(102, y + 44, ar, 'tnode2', 'middle'))
        out.append(text(298, y + 24, b, 'tnode2', 'middle'))
        out.append(text(298, y + 44, br, 'tnode2', 'middle'))
    out.append(text(W / 2, 554, '相同的地方很多；分歧集中在一个问题上：', 'ts', 'middle'))
    out.append(text(W / 2, 574, '耶稣是谁？十字架有没有发生？', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：天平和十字架 ----------------
def scale():
    W, H = 400, 470
    out = _svg(W, H, 3, '天平，还是十字架？',
               '左边是天平：善功放一边，恶行放一边，“善功的分量较重者才是成功的”（古兰经7:8）；连穆罕默德也说，人的善功不能使他进乐园，“除非真主赐恩慈给我”（布哈里圣训6463）。'
               '结果：没有人能确定自己够不够。'
               '右边是十字架：圣经承认天平上人人都不够——“世人都犯了罪，亏缺了上帝的荣耀”（罗3:23）；'
               '但上帝没有把天平拿走，而是自己承担了不够的部分——“如今却蒙上帝的恩典，因基督耶稣的救赎，就白白地称义”（罗3:24）。'
               '结果：“要叫你们知道自己有永生”（约壹5:13）。编者整理。')
    # 天平
    out.append(_box(10, 10, 184, 330, 'f1'))
    out.append(text(102, 38, '天平', 'tn hi', 'middle'))
    out.append('<path d="M102 70 L102 170 M50 92 L154 82 M50 92 L36 126 M50 92 L64 126 M154 82 L140 116 M154 82 L168 116 M82 170 L122 170" '
               'stroke="#fff" stroke-width="3" fill="none" stroke-linecap="round" opacity=".9"/>')
    out.append('<path d="M32 126 L68 126 M136 116 L172 116" stroke="#fff" stroke-width="4" stroke-linecap="round" opacity=".9"/>')
    out.append(text(50, 146, '恶行', 'tnode2', 'middle'))
    out.append(text(154, 136, '善功', 'tnode2', 'middle'))
    for i, s in enumerate(['“善功的分量较重者', '才是成功的”（7:8）', '“除非真主赐恩慈给我”', '（布哈里圣训6463）', '结果：没有人能确定', '自己够不够']):
        out.append(text(102, 206 + i * 22, s, 'tnode2', 'middle'))
    # 十字架
    out.append(_box(206, 10, 184, 330, 'f4'))
    out.append(text(298, 38, '十字架', 'tn hi', 'middle'))
    out.append('<path d="M298 64 L298 176 M262 96 L334 96" stroke="#fff" stroke-width="10" stroke-linecap="round" opacity=".9"/>')
    for i, s in enumerate(['天平上人人不够：', '“世人都犯了罪”（罗3:23）', '上帝自己承担不够的：', '“白白地称义”（罗3:24）', '结果：“叫你们知道', '自己有永生”（约壹5:13）']):
        out.append(text(298, 206 + i * 22, s, 'tnode2', 'middle'))
    out.append(text(W / 2, 372, '两边都说：光靠善行不够，需要上帝的怜悯。', 'ts', 'middle'))
    out.append(text(W / 2, 396, '不同在于：怜悯有没有确实的根据？', 'ts', 'middle'))
    out.append(text(W / 2, 420, '圣经说，根据就是十字架（罗3:25-26）', 'ts', 'middle'))
    out.append(text(W / 2, 452, '（编者整理）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：业力的链条，恩典的断开 ----------------
def chain():
    W, H = 400, 470
    out = _svg(W, H, 4, '业力的链条，和恩典',
               '上半部是业力：有意的行为（业）带来后果，后果又带来新的行为和来生，一环扣一环，在六道里轮回；'
               '要出来，靠自己的修行让贪爱止息（法句经“诸恶莫作，诸善奉行，自净其意，是诸佛教”）。'
               '下半部是恩典：圣经也说“人种的是什么，收的也是什么”（加6:7），后果是真实的；'
               '但上帝能赦免，“东离西有多远，他叫我们的过犯离我们也有多远”（诗103:12），'
               '因为后果由基督承担（赛53:5-6）；而且人只活一次，“按着定命，人人都有一死，死后且有审判”（来9:27）。编者整理。')
    out.append(_box(10, 10, 380, 200, 'f2'))
    out.append(text(W / 2, 36, '业力：一环扣一环', 'tn hi', 'middle'))
    for i in range(5):
        cx = 52 + i * 74
        out.append(f'<ellipse cx="{cx}" cy="86" rx="30" ry="18" fill="none" stroke="#fff" stroke-width="4" opacity=".9"/>')
    for i, s in enumerate(['行为', '后果', '新行为', '来生', '……']):
        out.append(text(52 + i * 74, 132, s, 'tnode2', 'middle'))
    out.append(text(W / 2, 166, '出路：靠自己修行，让贪爱止息', 'tnode2', 'middle'))
    out.append(text(W / 2, 190, '“自净其意，是诸佛教”（《法句经》）', 'tnode2', 'middle'))
    out.append(_box(10, 222, 380, 200, 'f4'))
    out.append(text(W / 2, 248, '恩典：有人替你承担', 'tn hi', 'middle'))
    for i in range(2):
        cx = 52 + i * 74
        out.append(f'<ellipse cx="{cx}" cy="298" rx="30" ry="18" fill="none" stroke="#fff" stroke-width="4" opacity=".9"/>')
    out.append('<path d="M196 270 L196 326 M174 290 L218 290" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".9"/>')
    for i in range(2):
        cx = 274 + i * 74
        out.append(f'<ellipse cx="{cx}" cy="298" rx="30" ry="18" fill="none" stroke="#fff" stroke-width="3" stroke-dasharray="5 6" opacity=".55"/>')
    out.append(text(52, 344, '罪', 'tnode2', 'middle'))
    out.append(text(126, 344, '后果', 'tnode2', 'middle'))
    out.append(text(196, 344, '十字架', 'tnode2', 'middle'))
    out.append(text(311, 344, '链条断开', 'tnode2', 'middle'))
    out.append(text(W / 2, 378, '“种的是什么，收的也是什么”（加6:7），', 'tnode2', 'middle'))
    out.append(text(W / 2, 400, '但基督替我们收了（赛53:5）；人只活一次（来9:27）', 'tnode2', 'middle'))
    out.append(text(W / 2, 450, '（编者整理）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：两个“道” ----------------
def dao():
    W, H = 400, 440
    out = _svg(W, H, 5, '两个“道”：老子的道，约翰的道',
               '左边是老子的道（《道德经》王弼本）：“有物混成，先天地生”（第25章）；“吾不知其名，字之曰道”；“道可道，非常道”（第1章）；“天地不仁，以万物为刍狗”（第5章）。'
               '右边是约翰福音的道（和合本把希腊文 logos 译作“道”）：“太初有道”（约1:1）；“道就是上帝”；“只有在父怀里的独生子将他表明出来”（约1:18）；“道成了肉身，住在我们中间，充充满满地有恩典有真理”（约1:14）。'
               '相同：都在天地以先。不同：一个说不出名字、不讲情；一个有名字、有恩典，来到人中间。编者整理。')
    cols = [(10, 'f3', '老子的道', [('在天地以先', ('“有物混成，先天地生”', '（25章）')), ('说不出', ('“吾不知其名，', '字之曰道”')), ('讲不清', ('“道可道，非常道”', '（1章）')), ('不讲情', ('“天地不仁”', '（5章）'))]),
            (206, 'f4', '约翰的道', [('在天地以先', ('“太初有道”', '（约1:1）')), ('有名字', ('“道就是上帝”', '（约1:1）')), ('表明出来', ('“独生子将他表明出来”', '（约1:18）')), ('满有恩典', ('“道成了肉身……”', '（约1:14）'))])]
    for x, c, t, rows in cols:
        out.append(_box(x, 10, 184, 360, c))
        out.append(text(x + 92, 38, t, 'tn hi', 'middle'))
        for i, (a, (b1, b2)) in enumerate(rows):
            y = 70 + i * 74
            out.append(text(x + 92, y + 8, '【' + a + '】', 'tnode2', 'middle'))
            out.append(text(x + 92, y + 30, b1, 'tnode2', 'middle'))
            out.append(text(x + 92, y + 48, b2, 'tnode2', 'middle'))
    out.append(text(W / 2, 398, '老子说：那个道，人说不出来；', 'ts', 'middle'))
    out.append(text(W / 2, 420, '约翰说：那个道，亲自来到人中间', 'ts', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：人往上爬，还是上帝下来 ----------------
def ladder():
    W, H = 400, 470
    out = _svg(W, H, 6, '人往上爬，还是上帝下来？',
               '左边三把梯子，代表人靠自己往上：伊斯兰教的善功、佛教的修行、道教的修炼。梯子的顶端都够不到上面。'
               '右边是一道从上往下的箭头，代表基督教：上帝自己下来——“除了从天降下、仍旧在天的人子，没有人升过天”（约3:13），'
               '“反倒虚己，取了奴仆的形象”（腓2:7），“道成了肉身，住在我们中间”（约1:14）。'
               '这不是说其他宗教全不讲恩典（伊斯兰教讲真主的怜悯，净土宗讲阿弥陀佛的愿力），而是说整体的方向不同。编者整理。')
    out.append(f'<rect x="10" y="10" width="380" height="40" rx="10" class="f0 fillc"/>')
    out.append(text(W / 2, 36, '上帝', 'tnode2', 'middle'))
    for i, (c, n) in enumerate([('f1', '善功'), ('f2', '修行'), ('f3', '修炼')]):
        x = 30 + i * 80
        out.append(f'<path d="M{x} 330 L{x} 120 M{x + 40} 330 L{x + 40} 120" stroke="var(--c{c[1]})" stroke-width="4" fill="none"/>')
        for k in range(8):
            yy = 320 - k * 26
            out.append(f'<path d="M{x} {yy} L{x + 40} {yy}" stroke="var(--c{c[1]})" stroke-width="3"/>')
        out.append(text(x + 20, 350, n, 'tn hi', 'middle'))
        out.append(text(x + 20, 104, '？', 'tn hi', 'middle'))
    out.append('<path d="M320 56 L320 300" stroke="var(--c4)" stroke-width="8" fill="none" stroke-linecap="round"/>')
    out.append('<path d="M302 284 L320 312 L338 284" stroke="var(--c4)" stroke-width="8" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
    out.append(text(320, 336, '上帝下来', 'tn hi', 'middle'))
    out.append(text(320, 354, '（约1:14；腓2:7）', 'ts', 'middle'))
    out.append(f'<rect x="10" y="370" width="380" height="30" rx="10" class="f0 fillc"/>')
    out.append(text(W / 2, 390, '人', 'tnode2', 'middle'))
    out.append(text(W / 2, 426, '“除了从天降下……的人子，没有人升过天”（约3:13）', 'ts', 'middle'))
    out.append(text(W / 2, 452, '（方向的对照，编者整理；各宗教里讲怜悯的部分见正文）', 'tw', 'middle'))
    out.append('</svg>')
    return '\n'.join(out)


# ---------------- 图：时间线 ----------------
def timeline():
    W, H = 400, 560
    out = _svg(W, H, 7, '四个传统的时间线',
               '从上到下按时间排列。约公元前6—5世纪：佛陀（释迦牟尼）在印度。传统说法前6世纪：老子；现存最早的《道德经》竹简（郭店）约在公元前300年以前。'
               '约公元前4年—公元30年代：耶稣在犹太地；约55年：保罗写哥林多前书，记下复活的见证人。西汉末到东汉前期：佛教传入中国，东汉永平十一年（68年）建洛阳白马寺。'
               '142年（据后来的传记）：张道陵创立天师道，道教成为有组织的宗教。约570—632年：穆罕默德；610年开始领受启示；622年迁往麦地那。唐朝：伊斯兰教传入中国，西安大清真寺始建于742年。'
               '1919年：中文和合本圣经出版，把约翰福音的 logos 译作“道”。')
    ev = [('f2', '前6—前5世纪', '佛陀在印度传道'), ('f3', '传统说前6世纪', '老子（郭店竹简约前300年以前）'),
          ('f4', '约前4年—30年代', '耶稣在犹太地'), ('f4', '约55年', '保罗写下复活的见证人（林前15章）'),
          ('f2', '西汉末—东汉', '佛教传入中国；68年建白马寺'), ('f3', '142年（传记所载）', '张道陵创天师道'),
          ('f1', '570—632年', '穆罕默德；610年开始领受启示'), ('f1', '唐朝', '伊斯兰教传入中国（西安大清真寺742年）'),
          ('f4', '1919年', '和合本出版，logos 译作“道”')]
    out.append('<path d="M40 20 L40 540" stroke="var(--rule)" stroke-width="3"/>')
    for i, (c, a, b) in enumerate(ev):
        y = 26 + i * 58
        out.append(f'<circle cx="40" cy="{y + 18}" r="8" class="{c} fillc"/>')
        out.append(_box(58, y, 332, 46, c, 10))
        out.append(text(70, y + 19, a, 'tnode2'))
        out.append(text(70, y + 38, b, 'tnode2'))
    out.append('</svg>')
    return '\n'.join(out)
