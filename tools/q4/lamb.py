# 网站的像素形象“小羊”（用户 2026-10-22 选定）。
# 它代表跟随主的读者——“我的羊听我的声音……他们也跟着我”（约10:27）——不代表“上帝的羔羊”（约1:29）。
# 做法：下面的文字网格就是原稿，程序把它变成 SVG（每格一个方块，shape-rendering="crispEdges"，放大不糊）；
# 同样的网格永远得到同样的 SVG。
#   .  透明
#   W  羊毛    S  羊毛的阴影和耳朵里面    K  眼睛、鼻子、耳朵、手脚和轮廓    G  小铃铛（金色）
# 2026-10-22 用户说表情有些“可怕”，精修：去掉灰色脸罩、不画嘴（只留小鼻子）、方眼睛放低一格、耳朵向外向下垂。
# 颜色只用网站已有的颜色，最多 4 种；白天、夜间各一套（见 PAL 和 css()）。
import hashlib
import sys

# 正面站立的拟人小羊（用户 2026-10-22 要求：像 Claude 网页上的形象那样站立、拟人。只学它的像素画法——大块、正面、方眼睛、短手短脚——角色和颜色是我们自己的）
# 16×16：最小尺寸，用来做标志和剪影辨认测试
G16 = '''
................
....KK.KK.KK....
...KWWKWWKWWK...
..KWWWWWWWWWWK..
.KKWWWWWWWWWWKK.
KSKWWKWWWWKWWKSK
KKKWWKWWWWKWWKKK
..KWWWWKKWWWWK..
...KWWWWWWWWK...
...KKWWGGWWKK...
.KKWWWWWWWWWWKK.
...KWWWWWWWWK...
...KSSSSSSSSK...
....KKKKKKKK....
....KK....KK....
...KKK....KKK...
'''

# 24×24：正式版
G24 = '''
........................
........................
.......KKK.KK.KKK.......
......KWWWKWWKWWWK......
.....KWWWWWWWWWWWWK.....
....KWWWWWWWWWWWWWWK....
...KWWWWWWWWWWWWWWWWK...
.KKKWWWWWWWWWWWWWWWWKKK.
KSSKWWWWWWWWWWWWWWWWKSSK
KSKKWWWWKKWWWWKKWWWWKKSK
KK.KWWWWKKWWWWKKWWWWK.KK
...KWWWWWWWKKWWWWWWWK...
....KWWWWWWWWWWWWWWK....
.....KWWWWWWWWWWWWK.....
......KKWWWGGWWWKK......
.....KWWWWWGGWWWWWK.....
....KKWWWWWWWWWWWWKK....
...KKKWWWWWWWWWWWWKKK...
......KWWWWWWWWWWWK.....
......KSSSSSSSSSSSK.....
.......KSSSSSSSSSK......
........KKKKKKKKK.......
........KK.....KK.......
.......KKK.....KKK......
'''

# 白天、夜间两套颜色（都来自 theme.css 已有的颜色）
PAL = {
    'light': {'bg': '#F5F1E8', 'W': '#FFFDF8', 'S': '#E3DCCD', 'K': '#1A2132', 'G': '#9A742C'},
    'dark': {'bg': '#0C111C', 'W': '#ECE6DA', 'S': '#E3DCCD', 'K': '#767A86', 'G': '#9A742C'},   # 铃铛夜间也用深一点的金色：和羊毛对比 3.4:1
}
CLS = {'W': 'lw', 'S': 'ls', 'K': 'lk', 'G': 'lg'}


def rows(g):
    r = [l for l in g.strip('\n').split('\n')]
    assert len(r) == len(r[0]) and all(len(l) == len(r) for l in r), '网格要是正方形'
    assert set(''.join(r)) <= set('.WSKG'), '只能用 . W S K G'
    return r


def runs(r):
    """把同一行里相邻的同色格子合成一个长方形，文件更小。"""
    out = []
    for y, line in enumerate(r):
        x = 0
        while x < len(line):
            c = line[x]
            if c == '.':
                x += 1
                continue
            e = x
            while e + 1 < len(line) and line[e + 1] == c:
                e += 1
            out.append((c, x, y, e - x + 1))
            x = e + 1
    return out


def css(scope=''):
    """颜色跟着网站的白天/夜间设置走（data-theme 或手机的深色模式）。scope：外层选择器，例如 '.lamb'。"""
    L, D = PAL['light'], PAL['dark']
    sel = lambda pre, k: f'{pre}{scope} .{CLS[k]}'.strip()
    light = ''.join(f'{sel("", k)}{{fill:{L[k]}}}' for k in 'WSKG')
    auto = ''.join(f'{sel(":root:not([data-theme=light]) ", k)}{{fill:{D[k]}}}' for k in 'WSKG')
    forced = ''.join(f'{sel(":root[data-theme=dark] ", k)}{{fill:{D[k]}}}' for k in 'WSKG')
    return light + '@media (prefers-color-scheme:dark){' + auto + '}' + forced


def svg(g, px=None, title='小羊', mode=None, standalone=False, cls=''):
    """g：网格文字；px：显示大小（像素）；mode：'light'/'dark' 时直接写死颜色（做预览图用），否则用 class。"""
    r = rows(g)
    n = len(r)
    px = px or n * 2
    by = {}
    for c, x, y, w in runs(r):          # 每种颜色一条 path：M 起点 h 宽 v1 h-宽 z
        by.setdefault(c, []).append(f'M{x} {y}h{w}v1h-{w}z')
    parts = []
    for c in 'WSKG':                   # 固定顺序，保证同样的网格得到同样的文件
        if c not in by:
            continue
        paint = f'fill="{PAL[mode][c]}"' if mode else f'class="{CLS[c]}"'
        parts.append(f'<path {paint} d="{"".join(by[c])}"/>')
    head = '<svg xmlns="http://www.w3.org/2000/svg"' if standalone else '<svg'
    style = f'<style>{css()}</style>' if (standalone and not mode) else ''
    if cls:
        head += f' class="{cls}"'
    return (f'{head} viewBox="0 0 {n} {n}" width="{px}" height="{px}" shape-rendering="crispEdges" role="img" aria-label="{title}">'
            f'<title>{title}</title>{style}{"".join(parts)}</svg>')


def silhouette(g):
    return '\n'.join(''.join('K' if c != '.' else '.' for c in l) for l in rows(g))


# ======================= 第三步：状态与动作 =======================
# 小羊 = 一张“底图”（不含眼睛和手臂）+ 几层可以换的小图层。每一帧就是“底图 + 哪几层”。
# 这样所有动作放在一个 SVG 里，文件也很小；换帧只是切换图层的显示，不重新下载。
EYES = [(8, 9), (9, 9), (8, 10), (9, 10), (14, 9), (15, 9), (14, 10), (15, 10)]
ARM_L = [(4, 16), (3, 17), (4, 17)]
ARM_R = [(19, 16), (19, 17), (20, 17)]


def base24():
    r = [list(l) for l in rows(G24)]
    for x, y in EYES:
        r[y][x] = 'W'
    for x, y in ARM_L + ARM_R:
        r[y][x] = '.'
    return '\n'.join(''.join(l) for l in r)


def _k(pts, c='K'):
    return [(x, y, c) for x, y in pts]


LAYERS = {   # 图层名：[(x, y, 颜色), ...]
    'eo': _k(EYES),                                                        # 睁眼
    'ec': _k([(8, 10), (9, 10), (14, 10), (15, 10)]),                      # 闭眼
    'eh': _k([(7, 10), (8, 9), (9, 10), (14, 10), (15, 9), (16, 10)]),     # 笑眯眯 ^ ^
    'el': _k([(7, 9), (8, 9), (7, 10), (8, 10), (13, 9), (14, 9), (13, 10), (14, 10)]),   # 往左看
    'er': _k([(9, 9), (10, 9), (9, 10), (10, 10), (15, 9), (16, 9), (15, 10), (16, 10)]), # 往右看
    'ld': _k(ARM_L),                                                       # 左手放下
    'rd': _k(ARM_R),                                                       # 右手放下
    'lu': _k([(4, 16), (3, 16), (3, 15), (2, 15), (2, 14), (1, 14), (1, 13)]),                                 # 左手举起
    'ru': _k([(19, 16), (20, 16), (20, 15), (21, 15), (21, 14), (22, 14), (22, 13)]),                              # 右手斜举（挥手 1）
    'rv': _k([(19, 16), (19, 15), (20, 15), (19, 14), (20, 14), (20, 13)]),                              # 右手竖起（挥手 2）
    'z1': _k([(20, 1), (21, 1), (22, 1), (23, 1), (22, 2), (21, 3), (20, 4), (21, 4), (22, 4), (23, 4)]),  # 睡觉的 z
    'z2': _k([(21, 0), (22, 0), (23, 0), (22, 1), (21, 2), (22, 2), (23, 2)]),            # z 往上飘
    's1': _k([(1, 1), (0, 2), (1, 2), (2, 2), (1, 3), (22, 1), (21, 2), (22, 2), (23, 2), (22, 3)], 'G'),  # 金色闪光（十字）
    's2': _k([(1, 2), (22, 2)], 'G'),                                                                          # 闪光收成一点
}

FRAMES = {   # 帧名：哪几层（底图总是显示）
    'idle': 'eo ld rd', 'blink': 'ec ld rd', 'left': 'el ld rd', 'right': 'er ld rd',
    'wave1': 'eh ld ru', 'wave2': 'eh ld rv',
    'joy1': 'eh lu ru s1', 'joy2': 'eh lu ru s2',
    'sleep1': 'ec ld rd z1', 'sleep2': 'ec ld rd z2',
}

# 状态表：触发条件、帧序列（帧名, 毫秒）、总时长。自动动作都在 5 秒内停下。
STATES = {
    'idle':  ('平时', [('idle', 0)]),
    'blink': ('滑到它时眨一次；鼠标离开时眨一次', [('blink', 140), ('idle', 0)]),
    'look':  ('第一次滑到它时，左右看一下再看着读者', [('left', 420), ('idle', 160), ('right', 420), ('idle', 0)]),
    'wave':  ('电脑上鼠标放上去、手机上点一下', [('wave1', 200), ('wave2', 200), ('wave1', 200), ('wave2', 200), ('idle', 0)]),
    'joy':   ('完成打卡、读完一篇（跳三下）', [('joy1', 220), ('joy2', 220)] * 3 + [('idle', 0)]),
    'sleep': ('北京时间 23:00—05:00（z 飘三次后停住）', [('sleep1', 700), ('sleep2', 700)] * 3 + [('sleep1', 0)]),
}


def sprite(px=48, title='小羊', enter=''):
    """一个 SVG 里放好所有图层；data-on 写当前显示哪些层（由下面的程序切换）。
    enter：第一次滑到它时做什么（默认“看向读者”；页尾用 'joy'＝读完一篇）。"""
    parts = [f'<path class="{CLS[c]}" d="{d}"/>' for c, d in _paths(rows(base24()))]
    for name, pts in LAYERS.items():   # 每层一种颜色：颜色写在 g 上，横向相连的格子合成一段
        c = pts[0][2]
        g = [['.'] * 24 for _ in range(24)]
        for x, y, _ in pts:
            g[y][x] = c
        d = ''.join(f'M{x} {y}h{w}v1h-{w}z' for _, x, y, w in runs([''.join(r) for r in g]))
        parts.append(f'<g data-l="{name}" class="{CLS[c]}"><path d="{d}"/></g>')
    ent = f' data-enter="{enter}"' if enter else ''
    return (f'<svg class="lamb" data-on="{FRAMES["idle"]}"{ent} viewBox="0 0 24 24" width="{px}" height="{px}" '
            f'shape-rendering="crispEdges" role="img" aria-label="{title}">{"".join(parts)}</svg>')


def _paths(r):
    by = {}
    for c, x, y, w in runs(r):
        by.setdefault(c, []).append(f'M{x} {y}h{w}v1h-{w}z')
    return [(c, ''.join(by[c])) for c in 'WSKG' if c in by]


def sprite_css():
    """只显示 data-on 里列出的图层；跳起来只动 transform（交给显卡）。"""
    show = ','.join(f'.lamb[data-on~="{n}"] [data-l="{n}"]' for n in LAYERS)
    return (css('.lamb') + '.lamb [data-l]{visibility:hidden}' + show + '{visibility:visible}'
            '.lamb{display:block;cursor:pointer;-webkit-tap-highlight-color:transparent;transition:transform .12s ease-out}'
            '.lamb.hop{transform:translateY(-12%)}'
            '@media (prefers-reduced-motion:reduce){.lamb{transition:none}.lamb.hop{transform:none}}')


def sprite_js():
    """状态机：只在看得见时动；系统设了“减少动态效果”就不播放序列；任何自动动作 5 秒内停下。"""
    import json
    seq = {k: v[1] for k, v in STATES.items()}
    frames = {k: v for k, v in FRAMES.items()}
    return ('(function(){var F=' + json.dumps(frames, separators=(',', ':')) + ',S=' + json.dumps(seq, separators=(',', ':')) + ';'
            r'''var RM=matchMedia('(prefers-reduced-motion: reduce)').matches;
function night(){var h=(new Date().getUTCHours()+8)%24;return h>=23||h<5;}
function Lamb(el){var t=null,busy=false,seen=false,vis=false,cur='';
 function set(f){if(f===cur)return;cur=f;el.setAttribute('data-on',F[f]);el.classList.toggle('hop',f==='joy1'&&!RM);}
 function rest(){set(night()?'sleep1':'idle');}
 function stop(){clearTimeout(t);t=null;busy=false;}
 function play(name){if(!vis)return;stop();var s=S[name];
  if(RM){set(s[s.length-1][0]);return;}
  busy=true;var i=0;(function step(){var p=s[i++];set(p[0]);if(p[1]&&i<s.length)t=setTimeout(step,p[1]);else{busy=false;if(name!=='sleep')rest();}})();}
 el.q4play=play;
 if('IntersectionObserver' in window)new IntersectionObserver(function(es){es.forEach(function(e){vis=e.isIntersecting;
   if(!vis){stop();rest();return;}
   if(night()){play('sleep');return;}
   if(!seen){seen=true;var en=el.getAttribute('data-enter')||'look';play(en);if(en==='look')setTimeout(function(){if(!busy)play('blink');},1500);}});}).observe(el);
 else{vis=true;rest();}
 el.addEventListener('mouseenter',function(){if(!busy)play('wave');});
 el.addEventListener('mouseleave',function(){if(!busy)play('blink');});
 el.addEventListener('click',function(e){e.preventDefault();play('wave');});
 /* 电脑上：眼睛跟着鼠标往左、往右看（读者自己移动鼠标时才动） */
 if(matchMedia('(hover: hover)').matches&&!RM)addEventListener('pointermove',function(e){if(busy||!vis||night())return;
   var r=el.getBoundingClientRect(),dx=e.clientX-(r.left+r.width/2);set(dx<-60?'left':dx>60?'right':'idle');},{passive:true});
 rest();}
document.querySelectorAll('.lamb').forEach(Lamb);
window.q4lamb={bind:Lamb,joy:function(){document.querySelectorAll('.lamb').forEach(function(el){el.q4play&&el.q4play('joy');});}};
})();''')



def logo(px=32):
    """标志：16×16 小版（静止，不做动作）。放在首页左上角和电脑侧栏的深色底上。"""
    s = svg(G16, px, '小羊', cls='lamb16')     # 标志旁边已经有文字，读屏软件不必再读“小羊”
    return s.replace('role="img" aria-label="小羊"><title>小羊</title>', 'aria-hidden="true" focusable="false">')


def dark_css(scope):
    """深色底（首页上半部、侧栏标志）上：不管白天夜间，都用夜间那套颜色。"""
    D = PAL['dark']
    return ''.join(f'{scope} .{CLS[k]}{{fill:{D[k]}}}' for k in 'WSKG')



def pop_css():
    """打卡那一刻：屏幕下方弹出一张小卡片，小羊欢喜跳三下，2.2 秒后收起。只动 opacity 和 transform。"""
    return ('.lambpop{position:fixed;z-index:132;left:50%;bottom:calc(140px + env(safe-area-inset-bottom,0px));padding:10px 14px 8px;'
            'border-radius:18px;background:var(--surface);border:1px solid var(--rule);box-shadow:0 8px 24px rgba(20,24,40,.16);'
            'opacity:0;transform:translate(-50%,12px);transition:opacity .2s ease,transform .2s ease;pointer-events:none}'
            '.lambpop.on{opacity:1;transform:translate(-50%,0)}'
            '@media (min-width:1024px){.lambpop{bottom:96px}}'
            '@media (prefers-reduced-motion:reduce){.lambpop{transition:none;transform:translate(-50%,0)}}')


def pop_js():
    """q4lamb.pop()：打卡时调用。卡片第一次用到时才放进网页。"""
    import json
    svg = sprite(48, '小羊', enter='joy').replace('role="img" aria-label="小羊"', 'aria-hidden="true"')
    return ('(function(){var box=null,t=null;window.q4lamb.pop=function(){'
            'if(!box){box=document.createElement("div");box.className="lambpop";box.innerHTML=' + json.dumps(svg, ensure_ascii=False) + ';'
            'document.body.appendChild(box);window.q4lamb.bind(box.firstChild);}'
            'clearTimeout(t);box.offsetWidth;box.classList.add("on");var l=box.firstChild;setTimeout(function(){l.q4play&&l.q4play("joy");},60);'
            't=setTimeout(function(){box.classList.remove("on");},2200);};})();')


if __name__ == '__main__':
    # 用法：python3 tools/q4/lamb.py 输出目录    → 生成预览用的 SVG，并打印大小和校验值
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    files = {
        'lamb16.svg': svg(G16, 64, standalone=True),
        'lamb24.svg': svg(G24, 96, standalone=True),
        'lamb16-silhouette.svg': svg(silhouette(G16), 64, title='小羊剪影', mode='light', standalone=True),
        'lamb24-light.svg': svg(G24, 96, mode='light', standalone=True),
        'lamb24-dark.svg': svg(G24, 96, mode='dark', standalone=True),
    }
    for name, s in files.items():
        open(f'{out}/{name}', 'w', encoding='utf-8').write(s)
        print(f'{name}\t{len(s.encode())} bytes\t{hashlib.sha256(s.encode()).hexdigest()[:12]}')
