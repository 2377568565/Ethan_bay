# 点阵星空：每个点是一个方格（和小羊的像素一样大），程序生成，同样的输入得到同样的输出。
#   月亮和启明星：Bayer 4×4 有序抖动（亮处点密，暗处点疏）；
#   星星：带种子的泊松圆盘排布（不挤在一起，也不排成格子）；
#   地平线上的晨光：同样用抖动，越近地平线、越靠小羊那边越亮。
# 颜色不写死：用 class，跟着网站的主题变量（白天、夜间自动换）。
import math

COLS, ROWS = 180, 56          # 格子数；手机上每格 2px（360×112），电脑上每格 4px（720×224）
HZ = 50                       # 地平线所在的行
BAYER = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
MOON = (30, 17, 9.5)          # 月亮：圆心、半径（格）
MSTAR = (146, 11)             # 启明星（启22:16“明亮的晨星”）
LAMB = (126, HZ - 24, 24)     # 小羊站的位置（左上角 x、y，边长），星星要让开


def dith(x, y, v):
    """亮度 v（0—1）在格子 (x, y) 上要不要点一个点。"""
    return v > (BAYER[y % 4][x % 4] + 0.5) / 16


class Rng:                    # 固定的小随机数发生器（不依赖 Python 版本）
    def __init__(self, s):
        self.s = s & 0xFFFFFFFF

    def __call__(self):
        self.s = (1664525 * self.s + 1013904223) & 0xFFFFFFFF
        return self.s / 2 ** 32


def poisson(w, h, r, seed, k=24):
    """Bridson 泊松圆盘：点与点至少相隔 r 格。"""
    rnd = Rng(seed)
    cs = r / math.sqrt(2)
    gw, gh = int(w / cs) + 1, int(h / cs) + 1
    grid = [[None] * gw for _ in range(gh)]
    p0 = (rnd() * w, rnd() * h)
    pts, act = [p0], [p0]
    grid[int(p0[1] / cs)][int(p0[0] / cs)] = p0
    while act:
        i = int(rnd() * len(act))
        px, py = act[i]
        for _ in range(k):
            a, d = rnd() * 2 * math.pi, r * (1 + rnd())
            x, y = px + d * math.cos(a), py + d * math.sin(a)
            if not (0 <= x < w and 0 <= y < h):
                continue
            gx, gy = int(x / cs), int(y / cs)
            if all(grid[j][i2] is None or math.dist(grid[j][i2], (x, y)) >= r
                   for j in range(max(0, gy - 2), min(gh, gy + 3)) for i2 in range(max(0, gx - 2), min(gw, gx + 3))):
                grid[gy][gx] = (x, y)
                pts.append((x, y))
                act.append((x, y))
                break
        else:
            act.pop(i)
    return pts


def sky():
    """返回 {(x, y): 种类}；种类：m 月亮、g 金色亮点、s 普通星、d 晨光、h 地平线。"""
    pts = {}
    cx, cy, r = MOON
    sx, sy = MSTAR
    for y in range(ROWS):
        for x in range(COLS):
            # 月牙：大圆减去往右上偏的圆；外缘实，往里（明暗交界）用抖动渐暗
            d1 = math.hypot(x + .5 - cx, y + .5 - cy)
            d2 = math.hypot(x + .5 - cx - 4.2, y + .5 - cy + 2.6)
            if d1 <= r and d2 > r * .86:
                v = .3 + .7 * min(1, (d2 - r * .86) / 3)
                if dith(x, y, v) or d1 > r - 1.2:
                    pts[(x, y)] = 'm'
            # 启明星：周围一圈淡淡的抖动光晕
            ds = math.hypot(x - sx, y - sy)
            if 2.5 < ds < 6 and dith(x, y, .28 * (1 - (ds - 2.5) / 3.5)):
                pts[(x, y)] = 'g'
            # 晨光：地平线上方 12 行
            if HZ - 12 <= y < HZ:
                t = (y - (HZ - 12)) / 12
                c = max(0, 1 - abs(x + .5 - COLS * .62) / (COLS * .55))
                if dith(x, y, .36 * t ** 1.8 * c ** 1.2):
                    pts[(x, y)] = 'd'
    # 启明星本体：中心一点，四个方向各伸 3 格，斜角各 1 格
    for i in range(-3, 4):
        pts[(sx + i, sy)] = pts[(sx, sy + i)] = 'g'
    for dx in (-1, 1):
        for dy in (-1, 1):
            pts[(sx + dx, sy + dy)] = 'g'
    # 地平线：一条点线（每隔一格），两头渐淡
    for x in range(COLS):
        c = 1 - abs(x + .5 - COLS / 2) / (COLS / 2)
        if x % 2 == 0 and dith(x, HZ, .25 + .75 * c):
            pts[(x, HZ)] = 'h'
    # 星星：泊松圆盘，越往下越稀；让开月亮、启明星、小羊
    lx, ly, ls = LAMB
    for i, (x, y) in enumerate(poisson(COLS, HZ - 3, 8.5, seed=36 * 9)):
        x, y = int(x), int(y)
        if math.hypot(x - cx, y - cy) < r + 7 or math.hypot(x - sx, y - sy) < 9:
            continue
        if lx - 2 <= x < lx + ls + 2 and y >= ly - 2:
            continue
        if Rng(x * 131 + y * 7)() < y / HZ * .55:      # 下面稀一些
            continue
        pts[(x, y)] = 's'
        if i % 7 == 3 and y < HZ - 14:               # 少数亮星：金色小十字
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
                pts[(x + dx, y + dy)] = 'g'
    return pts


CLS = {'m': 'km', 'g': 'kg', 's': 'ks', 'd': 'kd', 'h': 'kh'}


def svg():
    pts = sky()
    out = []
    for k in 'mgsdh':
        d = []
        for y in range(ROWS):
            x = 0
            while x < COLS:
                if pts.get((x, y)) == k:
                    w = 1
                    while pts.get((x + w, y)) == k:
                        w += 1
                    d.append(f'M{x} {y}h{w}v1h-{w}z')
                    x += w
                else:
                    x += 1
        if d:
            out.append(f'<path class="{CLS[k]}" d="{"".join(d)}"/>')
    return (f'<svg class="sky" viewBox="0 0 {COLS} {ROWS}" shape-rendering="crispEdges" aria-hidden="true" focusable="false">'
            + ''.join(out) + '</svg>')


CSS = '.sky .km,.sky .kg{fill:var(--gold)}.sky .ks,.sky .kh{fill:var(--muted)}.sky .kd{fill:var(--gold);opacity:.55}'

if __name__ == '__main__':
    import hashlib
    s = svg()
    print(len(s.encode()), 'bytes', hashlib.md5(s.encode()).hexdigest(), len(sky()), 'dots')
