#!/usr/bin/env python3
"""健康栏目文章 → 朗读稿（给 gen.py 合成）。

和学课的 speech.py 分开写，因为健康文章数字多：百分比、年份、血压、小数、带逗号的大数、英文缩写，
都先改成适合读出来的中文，模型就不会读错、读得生硬。断句：每句单独合成，句与句、段与段、章节标题后面加不同长度的停顿（gen.py 里设）。

    python3 tools/q4/tts/health_speech.py            # 生成 tools/q4/tts/script-health.json（全部健康文章）
    python3 tools/q4/tts/health_speech.py --demo     # 只生成试听用的 h2-demo（高血压开头两章）
"""
import html, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

DIG = '零一二三四五六七八九'


def int_cn(n):
    """整数读法：12 → 十二，105 → 一百零五，451755 → 四十五万一千七百五十五"""
    n = int(n)
    if n == 0:
        return '零'
    if n >= 10 ** 8:
        hi, lo = divmod(n, 10 ** 8)
        return int_cn(hi) + '亿' + (('零' if lo < 10 ** 7 else '') + int_cn(lo) if lo else '')
    if n >= 10 ** 4:
        hi, lo = divmod(n, 10 ** 4)
        return int_cn(hi) + '万' + (('零' if lo < 1000 else '') + int_cn(lo) if lo else '')
    out, zero = '', False
    for unit, val in (('千', 1000), ('百', 100), ('十', 10), ('', 1)):
        d, n = divmod(n, val)
        if d:
            if zero:
                out += '零'
            out += DIG[d] + unit
            zero = False
        elif out:
            zero = True
    if out.startswith('一十'):
        out = out[1:]
    return out


def num_cn(s):
    """带小数和千分位逗号的数：2.45 → 二点四五，451,755 → 四十五万……；开头的“二千、二万”读“两千、两万”"""
    s = s.replace(',', '')
    if '.' in s:
        a, b = s.split('.', 1)
        return int_cn(a) + '点' + ''.join(DIG[int(c)] for c in b)
    return re.sub(r'^二(?=[千万亿])', '两', int_cn(s))


UNIT = r'(?:名|人|例|位|个|只|次|万|千|克|毫|公|元|对|项|篇|份|岁|天|小时|分钟|多|余|种|倍|条|杯|碗|片|件|顿|口)'
TWO = r'(?:个|种|次|倍|天|周|小时|分钟|项|组|条|杯|碗|片|位|名|人|岁|件|顿|口|克|公斤|千克|毫克|年|个月|周)'


def year_cn(y):
    return ''.join('〇' if c == '0' else DIG[int(c)] for c in y)


def say_numbers(t):
    t = t.replace('mmHg', '毫米汞柱')
    # 急救电话 120 读“一二零”（“中风 120”、“打 120”），不读“一百二十”
    t = re.sub(r'(中风|打了|打|拨打|告诉|急救电话)\s*120(?![\d/])', lambda m: m[1] + '一二零', t)
    # 年份段：2021—2022 年、2012 到 2015 年
    t = re.sub(r'(\d{4})\s*[—–-]\s*(\d{4})\s*年', lambda m: year_cn(m[1]) + '到' + year_cn(m[2]) + '年', t)
    t = re.sub(r'(?<![\d.])(\d{4})\s*年', lambda m: year_cn(m[1]) + '年', t)
    t = re.sub(r'(?<![\d.])(1[89]\d\d|20\d\d)(?=\s*(?:到|至|和|、)\s*(?:1[89]\d\d|20\d\d)\s*年)', lambda m: year_cn(m[1]), t)
    t = re.sub(r'（((?:19|20)\d\d)）', r'（\1年）', t)
    # 单独的年份（括号里的“2015”、“2016—2020”）：后面不是“名、人、例……”这类单位，就读成年份
    t = re.sub(r'(?<![\d.,])((?:19|20)\d\d)\s*[—–]\s*((?:19|20)\d\d)(?![\d.,%])(?!\s*' + UNIT + ')',
               lambda m: year_cn(m[1]) + '到' + year_cn(m[2]) + '年', t)
    t = re.sub(r'(?<![\d.,])((?:19|20)\d\d)(?![\d.,%])(?!\s*' + UNIT + ')', lambda m: year_cn(m[1]), t)
    t = t.replace('Lp(a)', '脂蛋白a').replace('β-', 'β').replace('β', '贝塔').replace(' ×', '乘以').replace('×', '乘以')
    # “2 个、2 次”读“两个、两次”（“第 2 年”“2 型”不变）
    t = re.sub(r'(?<![\d.,第])2(?![\d.,])(?=\s*' + TWO + ')', '两', t)
    # 百分比、范围
    t = re.sub(r'([\d.,]+)\s*%\s*[—–-]\s*([\d.,]+)\s*%', lambda m: '百分之' + num_cn(m[1]) + '到百分之' + num_cn(m[2]), t)
    t = re.sub(r'([\d.,]+)\s*%', lambda m: '百分之' + num_cn(m[1]), t)
    # 血压一类的“158/96”、“120/80”：读成“一百五十八、九十六”
    t = re.sub(r'(\d{2,3})/(\d{2,3})', lambda m: int_cn(m[1]) + '、' + int_cn(m[2]), t)
    # 数字范围 120—139
    t = re.sub(r'([\d.,]+)\s*[—–]\s*([\d.,]+)', lambda m: num_cn(m[1]) + '到' + num_cn(m[2]), t)
    # 其余数字
    t = re.sub(r'\d[\d,]*(?:\.\d+)?', lambda m: num_cn(m[0]), t)
    return t


def clean(h):
    """HTML 片段 → 纯文字（去掉出处小数字、图、展开框）"""
    h = re.sub(r'\{\{c:[^}]+\}\}', '', h)
    h = re.sub(r'\{\{fig:[^}]+\}\}', '', h)
    h = re.sub(r'\{\{faq\}\}', '', h)
    h = re.sub(r'（见\{\{ref:[^}]+\}\}[^）]*）', '', h)
    h = re.sub(r'\{\{ref:[^}]+\}\}', '后面的一章', h)
    h = re.sub(r'<sup>.*?</sup>', '', h)
    h = re.sub(r'<[^>]+>', '', h)
    h = html.unescape(h)
    h = re.sub(r'\s+', ' ', h).strip()
    h = re.sub(r'\s*([，。；：！？、“”（）])\s*', r'\1', h)
    return h


def blocks_of(chapter_html, verse):
    """一章拆成朗读段落：<p>、<li>、经文、小框的标题和内容；展开框（深入一点）先不读"""
    h = re.sub(r'\{\{deep:.*?</p>\}\}', '', chapter_html, flags=re.S)
    h = re.sub(r'\{\{v:([^}]+)\}\}', lambda m: '<p>经上说：' + re.sub(r'<cite>.*?</cite>', '', verse(m[1])) + '</p>', h)
    h = re.sub(r'<p class="lab">(.*?)</p>', r'<p>\1。</p>', h)
    out = []
    for m in re.finditer(r'<(p|li)\b[^>]*>(.*?)</\1>', h, flags=re.S):
        t = clean(m[2])
        if not t:
            continue
        if m[1] == 'li' and not re.search(r'[。！？；]$', t):
            t += '。'
        out.append(spoken(t))
    return [x for x in out if x]


CUE = r'(?:点正文|右下角|点.{0,12}可以(?:看到|跳到)|蓝色字|小数字)'
VISUAL_CLAUSE = re.compile(r'，[^，。！？；]*' + CUE + r'[^。！？；]*(?=[。！？；])')   # 句子后半截是“点这里看”的，只删这半截
VISUAL = re.compile(r'[^。！？；]*' + CUE + r'[^。！？；]*[。！？；]')


def spoken(t):
    """读出来的样子：数字改中文；括号改成停顿；只对眼睛有用的句子（“点正文里的小数字……”）不读"""
    t = VISUAL.sub('', VISUAL_CLAUSE.sub('', t))
    # 听的人看不见图：提醒一句可以对照网页上的图
    t = re.sub(r'请看(?:下面)?这张图[。：]', '网页上这里有一张图，方便的话可以对照着看。', t)
    t = re.sub(r'([。！？])编者的理解$', r'\1这是编者的理解。', t)
    t = say_numbers(t)
    # 括号：句子中间、又不带数字的注释，读出来会打断句子，就不读；其余改成停顿
    t = re.sub(r'（([^）\d〇一二三四五六七八九十百千万亿]*)）(?=[\u4e00-\u9fffA-Za-z])', '', t)
    t = re.sub(r'（([^）]*)）', r'，\1，', t)
    t = re.sub(r'，+([，。；：！？])', r'\1', t)
    t = re.sub(r'([，。；：！？、])，', r'\1', t)
    t = re.sub(r'(?<=[\u4e00-\u9fff，。；：！？、“”]) +| +(?=[\u4e00-\u9fff，。；：！？、“”])', '', t)
    return t.strip('，')


def fp(s):
    return s[:24]


def unit(uid, title, chapters, verse, src=''):
    t = spoken(title)
    bl = [{'say': t if re.search(r'[。！？]$', t) else t + '。', 'fp': fp(title)}]
    for no, (part, cid, name, body) in chapters:
        bl.append({'say': f'第{int_cn(no)}章，{spoken(name)}。', 'fp': fp(name), 'head': 1, 'cid': cid})
        bl += [{'say': s, 'fp': fp(s)} for s in blocks_of(body, verse)]
    return {'id': uid, 'kind': 'h', 'src': src or uid, 'blocks': bl}


AUDIO_DIR = 'audio/vx-w/'   # 2026-10-27 用户选定：试听 C（VoxCPM2 按文字描述设计的四十多岁女声，温暖亲切）


def fphash(fps):
    """和 gen.py 一样：每段指纹用 | 连起来，算 32 位 FNV-1a"""
    h = 0x811c9dc5
    for ch in '|'.join(fps):
        for b in ch.encode('utf-16-le'):
            h ^= b
            h = (h * 0x01000193) & 0xffffffff
    return format(h, '08x')


def units_all():
    import history as H
    import health_data
    import importlib
    mods = {'diabetes.html': 'diabetes_text', 'hypertension.html': 'hypertension_text', 'lipid.html': 'lipid_text', 'stroke.html': 'stroke_text', 'osteo.html': 'osteo_text'}
    out = []
    for it in health_data.ITEMS:
        T = importlib.import_module(mods[it['url']])
        chs = [(i + 1, c) for i, c in enumerate(T.CHAPTERS) if c[1] != 'faq']
        out.append(unit(it['id'], it['q'], chs, H.verse))
    return out


def page_audio(uid):
    """给网页用：录音在哪里、每章从第几段开始、段落指纹的校验码（录音和文章对得上，才能按章跳转）"""
    u = [x for x in units_all() if x['id'] == uid][0]
    heads = [[i, b['cid']] for i, b in enumerate(u['blocks']) if b.get('head')]
    return dict(id=uid, dir=AUDIO_DIR, heads=heads, h=fphash([b['fp'] for b in u['blocks']]), n=len(u['blocks']))


def main():
    import history as H
    import health_data
    import importlib
    units = []
    if '--demo' in sys.argv:
        T = importlib.import_module('hypertension_text')
        chs = [(i + 1, c) for i, c in enumerate(T.CHAPTERS) if c[1] in ('q', 'scale')]
        units.append(unit('h2-demo', '高血压，真的要吃一辈子药吗？', chs, H.verse))
    else:
        units = units_all()
    out = os.path.join(HERE, 'script-health.json')
    json.dump(units, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for u in units:
        print(u['id'], len(u['blocks']), '段', sum(len(b['say']) for b in u['blocks']), '字')


if __name__ == '__main__':
    main()
