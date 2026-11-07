#!/usr/bin/env python3
"""下载生成网站要用的字体与圣经数据（都是公开来源），放到工作目录，再做出派生字体。

用法：
    python3 tools/q4/fetch_assets.py            # 下载到 tools/q4/.work（或环境变量 Q4_WORK 指定的目录）
    python3 tools/q4/render.py all              # 然后就能重建全部网页

已经下载过的文件会跳过。每个文件都核对 SHA-256：和当初建站用的版本不同时会提示（来源更新过），但不会中断。
需要：Python 3.8+，pip install fonttools brotli
"""
import hashlib, html, json, os, re, sys, urllib.error, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get('Q4_WORK') or os.path.join(HERE, '.work')
GF = 'https://raw.githubusercontent.com/google/fonts/main/ofl/'
TB = 'https://raw.githubusercontent.com/thiagobodruk/bible/master/json/'

# 文件名 → (来源, 建站时那一份的 SHA-256)
FILES = {
    'fonts/serif.ttf': (GF + 'notoserifsc/NotoSerifSC%5Bwght%5D.ttf', '050080d9255a86808f2945bffac582b31ef32bc36411ce29563b4961670c66f9'),
    'fonts/sans.ttf': (GF + 'notosanssc/NotoSansSC%5Bwght%5D.ttf', 'a3041811a78c361b1de50f953c805e0244951c21c5bd412f7232ef0d899af0da'),
    'fonts/gentium.ttf': (GF + 'gentiumbookplus/GentiumBookPlus-Regular.ttf', 'fe7b64eeacc430fcf46836a6f0dfe00d2c5a15483ed36692a2a185cb23ec2a5c'),
    'fonts/gentium-italic.ttf': (GF + 'gentiumbookplus/GentiumBookPlus-Italic.ttf', '7a0ab4bd78701fa46d325e362654c41a47e2a0a5cb4a3eebc94dce89c2ee7df1'),
    'fonts/hebrew.ttf': ('https://raw.githubusercontent.com/notofonts/notofonts.github.io/main/fonts/NotoSerifHebrew/hinted/ttf/NotoSerifHebrew-Regular.ttf',
                         'dfd5a6aefe97a99f68fe43388342913d50bb9fbf6d3afc4d2c7725661bc4a2b1'),
    'fonts/wk_v1.520.ttf': ('https://github.com/lxgw/LxgwWenKai/releases/download/v1.520/LXGWWenKai-Regular.ttf',
                            '8d6ba638ac9553413354cfaab97637c1cd778444e259441ea1e5f8fb2c697fba'),
    'bible/en_kjv.json': (TB + 'en_kjv.json', 'fc99486e7d3b86e4ad1f0f424b36ab41b4ec4db858a776bd13aee1b7910f136b'),
    'bible/en_nkjv.json': (TB + 'en_nkjv.json', '64a84906983f7ffb59183ad1173880c12c9156ee12c9391141034ed2bbbbb857'),
    'bible/zh_cun.json': (TB + 'zh_cunpss-shen.json', '98442a70db5a3997244f514f133bf41dd3a0541364329805ed413686fc5b36e4'),
}
# STEPBible 原文逐字数据（CC BY 4.0）：仓库里的文件名很长，下载后改成短名
STEP_DIR = 'Translators Amalgamated OT+NT'
HEB, GRK = ' - Translators Amalgamated Hebrew OT - STEPBible.org CC BY.txt', ' - Translators Amalgamated Greek NT - STEPBible.org CC-BY.txt'
STEP = {
    'TAHOT Gen-Deu' + HEB: ('bible/TAHOT_Gen-Deu.txt', 'e9b8546ee48fe0bfc57c3b70f5f40e98d96580e803526d19026224e31753368b'),
    'TAHOT Jos-Est' + HEB: ('bible/TAHOT_Jos-Est.txt', '195fee1dc3653bab33701f170734eb894ed647c10cd08cc61749375fe8b73775'),
    'TAHOT Job-Sng' + HEB: ('bible/TAHOT_Job-Sng.txt', '84e118a97e5725e3847cdfdd593873513021c790c63cc91a0d41fca2b5db2ed5'),
    'TAHOT Isa-Mal' + HEB: ('bible/TAHOT_Isa-Mal.txt', 'f3ded203d2a74d6368932c97ae550d1d0754b271af491dc0dedf36fe3ba0bcc5'),
    'TAGNT Mat-Jhn' + GRK: ('bible/TAGNT_Mat-Jhn.txt', 'ab8eaaeb68e17a1dcfa34e1e9350358f22f03bc2a97244d848750ad81044bc8e'),
    'TAGNT Act-Rev' + GRK: ('bible/TAGNT_Act-Rev.txt', '524e32375361e6d3fa2f7ef00b87605fdc4317a762f395651a05fdc31ad031b7'),
}
STEP_RAW = 'https://raw.githubusercontent.com/STEPBible/STEPBible-Data/master/'


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def get(url, dst, want):
    path = os.path.join(WORK, dst)
    if os.path.exists(path) and os.path.getsize(path) > 100:
        print(f'  已有  {dst}')
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        print(f'  下载  {dst}  ← {urllib.parse.unquote(url)}')
        req = urllib.request.Request(url, headers={'User-Agent': 'Ethan_bay-build'})
        with urllib.request.urlopen(req, timeout=300) as r, open(path + '.part', 'wb') as f:
            while True:
                b = r.read(1 << 20)
                if not b:
                    break
                f.write(b)
        os.replace(path + '.part', path)
    if want and sha(path) != want:
        print(f'  注意：{dst} 和建站时用的版本不一样（来源可能更新过），生成结果可能略有不同。')


def step_listing():
    """文件改过名时，按开头的“TAHOT Gen-Deu”之类在仓库目录里重新找"""
    api = 'https://api.github.com/repos/STEPBible/STEPBible-Data/contents/' + urllib.parse.quote(STEP_DIR)
    req = urllib.request.Request(api, headers={'User-Agent': 'Ethan_bay-build', 'Accept': 'application/vnd.github+json'})
    return [x['name'] for x in json.load(urllib.request.urlopen(req, timeout=60))]


def step_files():
    names = None
    for name, (dst, want) in STEP.items():
        try:
            get(STEP_RAW + urllib.parse.quote(STEP_DIR + '/' + name), dst, want)
            continue
        except urllib.error.HTTPError as e:
            if e.code != 404:
                raise
        if names is None:
            names = step_listing()
        prefix = name[:13]
        hit = [n for n in names if n.startswith(prefix) and n.endswith('.txt')]
        if not hit:
            sys.exit(f'STEPBible 仓库里找不到以“{prefix}”开头的文件，请手动下载后放到 {os.path.join(WORK, dst)}')
        get(STEP_RAW + urllib.parse.quote(STEP_DIR + '/' + hit[0]), dst, want)


def derived():
    """问答 PDF 用的固定字重与楷体子集（网页本身在生成时另行子集化，不依赖这些）"""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    from fontTools import subset
    F = os.path.join(WORK, 'fonts')
    for src, w in (('serif', 600), ('serif', 900), ('sans', 400), ('sans', 700)):
        out = os.path.join(F, f'{src}{w}.ttf')
        if not os.path.exists(out):
            print(f'  生成  fonts/{src}{w}.ttf')
            instancer.instantiateVariableFont(TTFont(os.path.join(F, f'{src}.ttf')), {'wght': w}).save(out)
    out = os.path.join(F, 'wenkai-sub.ttf')
    if not os.path.exists(out):
        print('  生成  fonts/wenkai-sub.ttf（问答文章用到的字）')
        text = ''.join(html.unescape(re.sub(r'<[^>]+>', '', open(os.path.join(HERE, 'qa', f), encoding='utf-8').read()))
                       for f in os.listdir(os.path.join(HERE, 'qa')) if f.endswith('.html'))
        text += ''.join(chr(c) for c in range(0x20, 0x7f)) + '，。、；：？！“”‘’（）《》〈〉【】—…·'
        o = subset.Options(); o.layout_features = ['*']; o.notdef_outline = True
        font = TTFont(os.path.join(F, 'wk_v1.520.ttf'))
        s = subset.Subsetter(o); s.populate(text=text); s.subset(font); font.save(out)
    link = os.path.join(HERE, 'fonts')   # 问答 PDF 的样式按 ../fonts/ 找字体
    if not os.path.exists(link) and os.path.realpath(F) != os.path.realpath(link):
        os.symlink(os.path.relpath(F, HERE), link)


def main():
    print(f'工作目录：{WORK}')
    for dst, (url, want) in FILES.items():
        get(url, dst, want)
    step_files()
    derived()
    print('完成。现在可以运行：python3 tools/q4/render.py all' + ('' if WORK == os.path.join(HERE, '.work') else f'（记得设置 Q4_WORK={WORK}）'))


if __name__ == '__main__':
    main()
