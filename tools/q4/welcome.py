"""欢迎页：天国景象（内联 SVG）+ 随机经文池 + 本周推荐 + 研读时间星星。"""
import os, re, random, html, importlib, sys

Q4 = os.path.dirname(os.path.abspath(__file__))

# 候选经文（和合本）。只有能在某一课（解读或原文）里找到的经文才会进入经文池。
VERSES = [
 ('太11:29', '我心里柔和谦卑，你们当负我的轭，学我的样式；这样，你们心里就必得享安息。'),
 ('约14:3', '我若去为你们预备了地方，就必再来接你们到我那里去，我在哪里，叫你们也在那里。'),
 ('启21:4', '上帝要擦去他们一切的眼泪；不再有死亡，也不再有悲哀、哭号、疼痛，因为以前的事都过去了。'),
 ('赛41:10', '你不要害怕，因为我与你同在；不要惊惶，因为我是你的上帝。我必坚固你，我必帮助你，我必用我公义的右手扶持你。'),
 ('哀3:22', '我们不至消灭，是出于耶和华诸般的慈爱，是因他的怜悯不至断绝。每早晨这都是新的；你的诚实极其广大！', '哀3:22、23'),
 ('提后2:13', '我们纵然失信，他仍是可信的，因为他不能背乎自己。'),
 ('来13:5', '我总不撇下你，也不丢弃你。'),
 ('林后1:3', '愿颂赞归与我们的主耶稣基督的父上帝，就是发慈悲的父，赐各样安慰的上帝。我们在一切患难中，他就安慰我们，叫我们能用上帝所赐的安慰去安慰那遭各样患难的人。', '林后1:3、4'),
 ('诗34:8', '你们要尝尝主恩的滋味，便知道他是美善；投靠他的人有福了！'),
 ('耶15:16', '我得着你的言语就当食物吃了；你的言语是我心中的欢喜快乐。'),
 ('诗119:105', '你的话是我脚前的灯，是我路上的光。'),
 ('约8:32', '你们必晓得真理，真理必叫你们得以自由。'),
 ('约20:29', '那没有看见就信的有福了。'),
 ('路24:32', '在路上，他和我们说话，给我们讲解圣经的时候，我们的心岂不是火热的吗？'),
 ('罗8:32', '上帝既不爱惜自己的儿子，为我们众人舍了，岂不也把万物和他一同白白地赐给我们吗？'),
 ('诗8:3', '我观看你指头所造的天，并你所陈设的月亮星宿，便说：人算什么，你竟顾念他！世人算什么，你竟眷顾他！', '诗8:3、4'),
 ('启22:17', '圣灵和新妇都说：“来！”听见的人也该说：“来！”口渴的人也当来；愿意的都可以白白取生命的水喝。'),
 ('彼后3:9', '主所应许的尚未成就，有人以为他是耽延，其实不是耽延，乃是宽容你们，不愿有一人沉沦，乃愿人人都悔改。'),
 ('结33:11', '我指着我的永生起誓，我断不喜悦恶人死亡，惟喜悦恶人转离所行的道而活。'),
 ('赛58:11', '耶和华也必时常引导你，在干旱之地使你心满意足，骨头强壮；你必像浇灌的园子，又像水流不绝的泉源。'),
 ('撒上7:12', '到如今耶和华都帮助我们。'),
 ('太5:16', '你们的光也当这样照在人前，叫他们看见你们的好行为，便将荣耀归给你们在天上的父。'),
 ('约1:14', '道成了肉身，住在我们中间，充充满满地有恩典有真理。我们也见过他的荣光，正是父独生子的荣光。'),
 ('赛55:10、11', '我口所出的话也必如此，决不徒然返回，却要成就我所喜悦的，在我发他去成就的事上必然亨通。', '赛55:11'),
 ('彼后1:19', '我们并有先知更确的预言，如同灯照在暗处，你们在这预言上留意，直等到天发亮，晨星在你们心里出现的时候，才是好的。'),
 ('启1:3', '念这书上预言的和那些听见又遵守其中所记载的，都是有福的，因为日期近了。'),
 ('帖前5:20', '不要藐视先知的讲论。但要凡事察验，善美的要持守。', '帖前5:20、21'),
 ('赛40:1', '你们的上帝说：你们要安慰，安慰我的百姓。'),
 ('士4:14', '起来！今日就是耶和华将西西拉交在你手的日子。耶和华岂不在你前头行吗？'),
 ('创3:9', '耶和华上帝呼唤那人，对他说：“你在哪里？”'),
 ('雅5:7、8', '你们也当忍耐，坚固你们的心，因为主来的日子近了。', '雅5:8'),
 ('约17:21', '使他们都合而为一。正如你父在我里面，我在你里面，使他们也在我们里面，叫世人可以信你差了我来。'),
 ('约13:35', '你们若有彼此相爱的心，众人因此就认出你们是我的门徒了。'),
 ('罗10:13', '凡求告主名的就必得救。'),
 ('林前2:2', '因为我曾定了主意，在你们中间不知道别的，只知道耶稣基督并他钉十字架。'),
 ('弗4:13', '直等到我们众人在真道上同归于一，认识上帝的儿子，得以长大成人，满有基督长成的身量。'),
]

MEMORY_L1 = ('来1:1', '上帝既在古时借着众先知多次多方地晓谕列祖，就在这末世借着他儿子晓谕我们。', '来1:1、2')

BOOK_SHORT = {'以赛亚书':'赛','历代志下':'代下','哥林多前书':'林前','启示录':'启','罗马书':'罗','路加福音':'路',
              '约翰一书':'约壹','希伯来书':'来','阿摩司书':'摩','约珥书':'珥','提摩太后书':'提后'}

def _corpus():
    """每课的全部文字（解读数据 + 学课原文），经文冒号统一为半角。"""
    full = open(os.path.join(Q4, 'full.txt'), encoding='utf-8').read()
    pages = re.split(r'===== PDF页 (\d+) =====', full)
    pg = {int(pages[i]): pages[i + 1] for i in range(1, len(pages), 2)}
    out = {}
    for n in range(1, 14):
        first = 6 + 7 * (n - 1)
        txt = ''.join(pg.get(p, '') for p in range(first, first + 7))
        for f in ([f'l{n:02d}.py'] + (['l01_frag.html'] if n == 1 else [])):
            p = os.path.join(Q4, 'data', f)
            if os.path.exists(p): txt += open(p, encoding='utf-8').read()
        out[n] = re.sub(r'\s+', '', txt).replace('：', ':')
    return out

def pool(titles):
    """返回 [(显示经文出处, 经文, 课号)]；每节经文归到第一次提到它的那一课。"""
    corp = _corpus()
    res = []
    sys.path.insert(0, os.path.join(Q4, 'data'))
    mems = {1: MEMORY_L1}
    for n in range(2, 14):
        L = importlib.import_module(f'l{n:02d}').L
        b = re.match(r'(\D+)(.*)', L['mem_ref'])
        mems[n] = (None, L['mem'], BOOK_SHORT.get(b.group(1), b.group(1)) + b.group(2))
    for n, (_, t, disp) in mems.items():
        res.append((disp, t, n))
    for v in VERSES:
        ref, text = v[0], v[1]
        disp = v[2] if len(v) > 2 else ref
        pat = re.escape(ref) + r'(?!\d)'
        hit = next((n for n in range(1, 14) if re.search(pat, corp[n])), None)
        if hit is None and '、' not in ref:
            ch, vs = ref.split(':')
            hit = next((n for n in range(1, 14)
                        if re.search(re.escape(ch) + r':\d+[-–]\d+', corp[n]) and
                        any(int(a) <= int(vs) <= int(b) for a, b in re.findall(re.escape(ch) + r':(\d+)[-–](\d+)', corp[n]))), None)
        if hit is None:
            print('  经文池跳过（课文中未提及）:', ref, file=sys.stderr)
            continue
        res.append((disp, text, hit))
    return res

def _stars(rng, n):
    out = []
    for _ in range(n):
        x = rng.uniform(10, 1590); y = rng.uniform(10, 470) ** 1.0
        r = rng.choice([0.7, 0.9, 1.1, 1.3, 1.6, 2.1])
        d = rng.uniform(2.2, 5.5); dl = -rng.uniform(0, 5)
        out.append(f'<circle class="tw" cx="{x:.0f}" cy="{y:.0f}" r="{r}" style="animation-duration:{d:.1f}s;animation-delay:{dl:.1f}s"/>')
    return ''.join(out)

def _sparkles(rng, n):
    out = []
    for _ in range(n):
        x = rng.uniform(80, 1520); y = rng.uniform(60, 620); s = rng.uniform(5, 13)
        d = rng.uniform(2.5, 5); dl = -rng.uniform(0, 5)
        out.append(f'<path class="sp" transform="translate({x:.0f} {y:.0f}) scale({s/10:.2f})" d="M0-10C1 -2 2-1 10 0C2 1 1 2 0 10C-1 2-2 1-10 0C-2-1-1-2 0-10Z" style="animation-duration:{d:.1f}s;animation-delay:{dl:.1f}s"/>')
    return ''.join(out)

def scene_svg():
    rng = random.Random(1844)
    cx, hy = 800, 662           # 城门中心、地平线（城、山、路在下移 OFF 的组内绘制）
    OFF = 150; HY = hy + OFF
    rays = []
    for i in range(15):
        a = -168 + i * 11.2
        import math
        w = 2.6 if i % 2 else 1.4
        pts = []
        for da in (-w, w):
            t = math.radians(a + da)
            pts.append(f'{cx + 1900 * math.cos(t):.0f},{HY - 40 + 1900 * math.sin(t):.0f}')
        rays.append(f'<polygon points="{cx},{HY - 40} {pts[0]} {pts[1]}"/>')
    bows = []
    for i, c in enumerate(['#E86A6A', '#F2A65A', '#F6DE6C', '#7CCB8A', '#6FB6E0', '#7C86D8', '#A77CD0']):
        r = 520 - i * 9
        bows.append(f'<path d="M{cx - r} {HY + 160}V{HY}A{r} {r} 0 0 1 {cx + r} {HY}V{HY + 160}" stroke="{c}"/>')
    # 圣城：城墙、垛口、塔楼、中央殿宇、三座珍珠门
    wall_x0, wall_x1, wall_top = 548, 1052, 604
    cren = ''.join(f'<rect x="{x}" y="{wall_top - 9}" width="11" height="10"/>' for x in range(wall_x0 + 4, wall_x1 - 8, 22))
    towers = []
    for x, w, h in [(548, 34, 92), (628, 28, 70), (700, 30, 104), (870, 30, 104), (944, 28, 70), (1018, 34, 92)]:
        top = hy - h
        towers.append(f'<rect x="{x}" y="{top}" width="{w}" height="{h}"/>'
                      f'<path d="M{x - 3} {top + 1}L{x + w / 2:.0f} {top - 26}L{x + w + 3} {top + 1}Z"/>')
    temple = (f'<rect x="{cx - 58}" y="520" width="116" height="{hy - 520}"/>'
              f'<rect x="{cx - 70}" y="512" width="140" height="12"/>'
              f'<path d="M{cx - 46} 514 A46 46 0 0 1 {cx + 46} 514Z"/>'
              f'<rect x="{cx - 3}" y="438" width="6" height="30"/><rect x="{cx - 11}" y="446" width="22" height="5"/>')
    gates = ''.join(f'<path d="M{x - 15} {hy + 2}V{hy - 30}A15 15 0 0 1 {x + 15} {hy - 30}V{hy + 2}Z"/>' for x in (660, cx, 940))
    return f'''<svg class="wscene" viewBox="0 0 1600 1000" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">
<defs>
 <linearGradient id="wsky" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" style="stop-color:var(--sky1)"/><stop offset=".4" style="stop-color:var(--sky2)"/>
  <stop offset=".64" style="stop-color:var(--sky3)"/><stop offset=".8" style="stop-color:var(--sky4)"/><stop offset=".88" style="stop-color:var(--sky5)"/>
 </linearGradient>
 <radialGradient id="wglow" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#FFFDF2" stop-opacity="1"/><stop offset=".18" stop-color="#FFF1C4" stop-opacity=".9"/>
  <stop offset=".45" stop-color="#FFD58A" stop-opacity=".38"/><stop offset="1" stop-color="#FFC66E" stop-opacity="0"/>
 </radialGradient>
 <radialGradient id="whalo" cx="50%" cy="50%" r="50%">
  <stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/><stop offset=".5" stop-color="#FFF4D6" stop-opacity=".45"/><stop offset="1" stop-color="#FFF4D6" stop-opacity="0"/>
 </radialGradient>
 <linearGradient id="wpath" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="#FFF8DC" stop-opacity=".95"/><stop offset=".5" stop-color="#F7D58C" stop-opacity=".55"/><stop offset="1" stop-color="#E9B45E" stop-opacity=".12"/>
 </linearGradient>
 <linearGradient id="wcity" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" style="stop-color:var(--city1)"/><stop offset="1" style="stop-color:var(--city2)"/>
 </linearGradient>
 <filter id="wblur" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="22"/></filter>
 <filter id="wsoft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="5"/></filter>
</defs>
<rect width="1600" height="1000" fill="url(#wsky)"/>
<g class="wskystars">{_stars(rng, 90)}</g>
<g class="wrays">{''.join(rays)}</g>
<circle class="wglow" cx="{cx}" cy="{HY - 60}" r="620" fill="url(#wglow)"/>
<g class="wbow" fill="none" stroke-width="8">{''.join(bows)}</g>
<g transform="translate(0 {OFF})">
<g class="wclouds" filter="url(#wblur)">
 <g class="cl c1"><ellipse cx="260" cy="560" rx="260" ry="38"/><ellipse cx="420" cy="540" rx="160" ry="30"/></g>
 <g class="cl c2"><ellipse cx="1320" cy="548" rx="280" ry="40"/><ellipse cx="1150" cy="566" rx="170" ry="28"/></g>
 <g class="cl c3"><ellipse cx="620" cy="420" rx="200" ry="24"/><ellipse cx="1040" cy="400" rx="220" ry="26"/></g>
</g>
<g class="wcity" fill="url(#wcity)">
 <rect x="{wall_x0}" y="{wall_top}" width="{wall_x1 - wall_x0}" height="{hy - wall_top + 20}"/>{cren}{''.join(towers)}{temple}
</g>
<g class="wgates">{gates}</g>
<ellipse class="whalo" cx="{cx}" cy="{hy - 70}" rx="240" ry="150" fill="url(#whalo)"/>
<path class="wh1" d="M0 700C170 660 360 700 540 672S820 650 1060 672S1420 646 1600 690V1000H0Z"/>
<path class="wpath" d="M790 668H810C832 760 900 880 1010 1000H590C700 880 768 760 790 668Z" fill="url(#wpath)"/>
<path class="wh2" d="M0 790C220 740 420 800 610 772C650 766 700 770 730 778L700 1000H0Z"/>
<path class="wh2" d="M1600 780C1400 736 1180 796 990 770C950 765 900 770 870 778L900 1000H1600Z"/>
<path class="wh3" d="M0 900C200 850 400 900 560 880L520 1000H0Z"/>
<path class="wh3" d="M1600 890C1400 846 1200 896 1040 878L1080 1000H1600Z"/>
<g class="wpathglow" filter="url(#wsoft)"><path d="M796 672H804C820 760 870 870 950 1000H650C730 870 780 760 796 672Z" fill="#FFF3C8" opacity=".35"/></g>
</g>
<g class="wspark">{_sparkles(rng, 26)}</g>
</svg>'''

# 欢迎页“本站累计访问 N 人次”的起点：换成自己计数之前不蒜子上的数字（2026-10-01 为 368）。
# 同步任务第一次运行时会从不蒜子取最新的数字存进 data/ask.json（hits0），网页优先用那个。
VISITS_BASE = 368


def welcome_html(titles):
    items = ''.join(f'<li data-r="{html.escape(r)}" data-l="{n}" data-t="{html.escape(titles[n])}">{html.escape(t.replace("“", "‘").replace("”", "’"))}</li>'
                    for r, t, n in pool(titles))
    stars = ''.join('<i><svg viewBox="-11 -11 22 22"><path d="M0-10C1-2 2-1 10 0C2 1 1 2 0 10C-1 2-2 1-10 0C-2-1-1-2 0-10Z"/></svg></i>' for _ in range(12))
    return f'''<div id="welcome" class="welcome" role="dialog" aria-modal="true" aria-labelledby="wtitle" tabindex="-1" hidden>
{scene_svg()}
<div class="winner">
  <button class="wacct" type="button" data-acct aria-label="账号：登录后在不同设备之间同步"><svg class="ic" viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="8.2" r="3.6" fill="none" stroke="currentColor" stroke-width="2"/><path d="M4.8 19.5c1.2-3.6 4-5.4 7.2-5.4s6 1.8 7.2 5.4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg><span class="ac-n">账号</span></button>
  <button class="wx" type="button" data-wclose aria-label="关闭欢迎页">×</button>
  <p class="weyebrow">安息日学研经指引 · 2026年第4季</p>
  <h2 id="wtitle" class="wtitle">预言的恩赐</h2>
  <p class="winvite"><span class="q">“凡劳苦担重担的人可以到我这里来，<br>我就使你们得安息。”</span><span class="by">—— 耶稣的邀请（太11:28）</span></p>
  <div class="wrec">
    <p class="wdate"></p>
    <p class="wbtns"><a class="wbtn gold" id="wgo" href="#l1"><span class="l1"></span><span class="l2"></span></a><a class="wbtn ghost" href="#home">学课目录</a><a class="wbtn egg" href="#qa"><span class="st">✦</span>问题彩蛋</a><a class="wbtn music" href="#music"><span class="st">♪</span>音乐</a></p>
    <p class="wclass" hidden><a href="#l1"></a></p>
    <p class="wresume" hidden></p>
    <div class="wnews" hidden></div>
  </div>
  <div class="wcards">
  <div class="wcard wverse">
    <p class="wk"><span>今日经文 · 从本季学课中随机选出</span><span class="wvbtns"><button class="wshuf wimg" type="button" data-imgverse="welcome">做成图片</button><button class="wshuf" type="button">换一节 ↻</button></span></p>
    <blockquote class="wvt"></blockquote>
    <p class="wvr"></p>
  </div>
  <div class="wcard wtogether" hidden>
    <p class="wk"><span>本周共读 · 读完打卡</span></p>
    <div class="wt-days"></div>
    <p class="wt-msg"></p>
  </div>
  <div class="wcard wprog">
    <p class="wk"><span>本周研读</span><b class="wmin"></b></p>
    <p class="wstars" aria-hidden="true">{stars}</p>
    <p class="wmsg m0">每读满 5 分钟点亮一颗星。点亮 12 颗星（本周累计 1 小时），这里会换上荣耀的景象。</p>
    <p class="wmsg m1" hidden><b>本周你已在这里研读满 1 小时</b>，这是你第 <b class="wn">1</b> 周达成目标。<br>“你们要尝尝主恩的滋味，便知道他是美善。”（诗34:8）</p>
    <p class="wnote">研读时间只记录在这台设备的这个浏览器里，每周从安息日开始重新计算。</p>
  </div>
  </div>
  <p class="wcredit">整理制作 · Ethan（HangZhou_XG）</p>
  <p class="wvisits" data-base="{VISITS_BASE}"><span hidden>本站累计访问 <b></b> 人次</span></p>
  <ol class="vpool" hidden>{items}</ol>
</div>
</div>
<div id="wtoast" class="wtoast" role="status" hidden>✦ 本周研读已满 1 小时！下次打开，欢迎页会换上荣耀的景象。</div>'''
