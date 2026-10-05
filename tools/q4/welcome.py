"""欢迎页（网站首页）：黎明的光 + 今日经文（从本季学课中随机选出，点一下换一节）+ 今日学课 + 四个入口 + 本周共读与研读星星。"""
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

# 欢迎页“本站累计访问 N 人次”的起点：换成自己计数之前不蒜子上的数字（2026-10-01 为 368）。
# 同步任务第一次运行时会从不蒜子取最新的数字存进 data/ask.json（hits0），网页优先用那个。
VISITS_BASE = 368


def welcome_html(titles, ui):
    """欢迎页 = 网站的首页（2026-10 新设计“黎明的光”）：上半部是光和今日经文（点经文换一节），下半部是今日学课和四个入口。
    ui：render.py 传进来的图标和数字（I_BOOK 等、问答篇数、诗歌首数）。"""
    items = ''.join(f'<li data-r="{html.escape(r)}" data-l="{n}" data-t="{html.escape(titles[n])}">{html.escape(t.replace("“", "‘").replace("”", "’"))}</li>'
                    for r, t, n in pool(titles))
    stars = ''.join('<i><svg viewBox="-11 -11 22 22"><path d="M0-10C1-2 2-1 10 0C2 1 1 2 0 10C-1 2-2 1-10 0C-2-1-1-2 0-10Z"/></svg></i>' for _ in range(12))
    ring = ('<span class="wring" aria-hidden="true"><svg viewBox="0 0 62 62"><circle class="bgc" cx="31" cy="31" r="27"/>'
            '<circle class="fgc" cx="31" cy="31" r="27" stroke-dasharray="169.6" stroke-dashoffset="169.6"/></svg><i><b class="wr-n">0/7</b><small>本周</small></i></span>')
    return f'''<div id="welcome" class="welcome" role="dialog" aria-modal="true" aria-labelledby="wtitle" tabindex="-1" hidden>
<section class="whero">
  <div class="wsky" aria-hidden="true"><i class="wst"></i><i class="wdawn"></i><i class="whz"></i><i class="wgrain"></i></div>
  <div class="wtop">
    <button class="wacct glass" type="button" data-acct aria-label="账号：登录后在不同设备之间同步">{ui['user']}<span class="ac-n">账号</span></button>
    <span class="wtr"><button class="glass" type="button" data-rsearch aria-label="搜索全季内容">{ui['search']}</button><button class="glass" type="button" data-rsettings aria-label="字号与夜间模式">{ui['aa']}</button></span>
  </div>
  <div class="whin">
    <p class="weyebrow">安息日学研经指引 · 2026年第4季</p>
    <h2 id="wtitle" class="wtitle">预言的恩赐</h2>
    <span class="wrule" aria-hidden="true"></span>
    <div class="wverse" role="button" tabindex="0" aria-label="今日经文：轻点换一节">
      <blockquote class="wvt"></blockquote>
      <p class="wvr"></p>
    </div>
    <p class="wvbtns"><button class="wshuf" type="button">{ui['refresh']}换一节</button><button class="wshuf wimg" type="button" data-imgverse="welcome">{ui['image']}做成图片</button></p>
  </div>
</section>
<div class="wmain">
  <div class="wgreet"><b class="whello">平安</b><span class="wdate"></span></div>
  <a class="wtoday" id="wgo" href="#l1"><span class="wt-tx"><span class="l1"></span><b class="l2"></b><small class="l3"></small></span>{ring}</a>
  <p class="wclass" hidden><a href="#l1"></a></p>
  <nav class="wtiles" aria-label="栏目">
    <a class="wtile" href="#home">{ui['book']}<b>学课目录</b><small>导言 + 13 课</small></a>
    <a class="wtile egg" href="#qa">{ui['spark']}<b>问题彩蛋</b><small>{ui['nqa']} 篇深度解答</small></a>
    <a class="wtile" href="#music">{ui['note']}<b>音乐</b><small>{ui['nsongs']} 首诗歌</small></a>
    <a class="wtile" href="#ask">{ui['chat']}<b>提问区</b><small>一起问，一起查考</small></a>
  </nav>
  <div class="wnews" hidden></div>
  <p class="wresume" hidden></p>
  <div class="wcard wtogether" hidden>
    <p class="wk"><span>本周共读 · 读完打卡</span><span class="wk2">点某一天直接去读</span></p>
    <div class="wt-days"></div>
    <p class="wt-msg"></p>
  </div>
  <div class="wcard wprog">
    <p class="wk"><span>本周研读</span><b class="wmin"></b></p>
    <p class="wstars" aria-hidden="true">{stars}</p>
    <p class="wmsg m0">每读满 5 分钟点亮一颗星。点亮 12 颗星（本周累计 1 小时），上面的晨光会变成满天的荣光。</p>
    <p class="wmsg m1" hidden><b>本周你已在这里研读满 1 小时</b>，这是你第 <b class="wn">1</b> 周达成目标。<br>“你们要尝尝主恩的滋味，便知道他是美善。”（诗34:8）</p>
    <details class="wnote fold"><summary><span class="fs">时间怎么算？</span>{ui['down']}</summary><p>页面开着、你在阅读时才计时（停下 10 分钟不动就暂停）。时间记在这台设备的浏览器里，登录账号后各设备加起来；每周六晚上 12 点（北京时间）清零，重新计算。累计的“总使用时长”在“我的”里。</p></details>
  </div>
  <p class="wcredit">整理制作 · Ethan（HangZhou_XG）</p>
  <p class="wvisits" data-base="{VISITS_BASE}"><span hidden>本站累计访问 <b></b> 人次</span></p>
  <button class="wx" type="button" data-wclose aria-label="关闭首页，查看学课目录" hidden></button>
  <ol class="vpool" hidden>{items}</ol>
</div>
</div>
<div id="wtoast" class="wtoast" role="status" hidden>✦ 本周研读已满 1 小时！回到首页看看：晨光已经变成满天的荣光。</div>'''
