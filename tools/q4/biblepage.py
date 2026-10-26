#!/usr/bin/env python3
"""“圣经”栏目单独打开的网页（仓库根目录 bible.html，网址 #58.11.1）。网站里的“圣经”页（index.html #bible）用同一套 bible.js、bible.css。
数据由 biblesite.py 生成在 site/bible/。用法：python3 tools/q4/biblesite.py && python3 tools/q4/biblepage.py"""
import os, glob, json
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
THEME = open(os.path.join(HERE, 'theme.css'), encoding='utf-8').read()
TOKENS = THEME[THEME.index(':root{'):THEME.index('@media (min-width:600px)')]   # 网站的颜色（白天、夜间）
COLORS = (':root{--c1:#08968C;--c2:#B0631C;--c3:#3A5FC8;--c4:#B07F0E;--c5:#7B4FC4;--c6:#A8324A;'
          '--serif:"LessonSerif","Noto Serif SC","Source Han Serif SC","Songti SC","STSong","SimSun",serif}\n'
          '@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--c1:#1A9C93;--c2:#C9722E;--c3:#5F82E0;--c4:#B5871A;--c5:#946FE0;--c6:#DB5F78}}\n'
          ':root[data-theme="dark"]{--c1:#1A9C93;--c2:#C9722E;--c3:#5F82E0;--c4:#B5871A;--c5:#946FE0;--c6:#DB5F78}\n'
          ':root{--tbh:env(safe-area-inset-bottom,0px)}*{box-sizing:border-box}html,body{margin:0;background:var(--paper);-webkit-text-size-adjust:100%}\n')
CSS = open(os.path.join(HERE, 'bible.css'), encoding='utf-8').read()
JS = open(os.path.join(HERE, 'bible.js'), encoding='utf-8').read()


def index_file():
    cur = os.path.join(ROOT, 'site', 'bible', 'current.txt')
    assert os.path.exists(cur), '先运行 biblesite.py'
    return 'site/bible/' + open(cur, encoding='utf-8').read().strip()


def page():
    cfg = json.dumps({'index': index_file(), 'prefix': '', 'site': False})
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>圣经 · 预言的恩赐</title>
<meta name="description" content="和合本、KJV 和原文（希伯来文、希腊文）圣经：切换、对照、划线笔记，搜书卷、人名地名、词语和经文。">
<script>try{{var t=localStorage.getItem('q4:theme');if(t==='light'||t==='dark')document.documentElement.setAttribute('data-theme',t);}}catch(e){{}}</script>
<style>{TOKENS}{COLORS}{CSS}</style></head>
<body><div id="bbroot"></div>
<script>{JS}</script>
<script>Q4Bible.mount(document.getElementById('bbroot'),{cfg});</script>
</body></html>'''


if __name__ == '__main__':
    h = page()
    out = os.path.join(ROOT, 'bible.html')
    open(out, 'w', encoding='utf-8').write(h)
    print(out, len(h.encode()), 'bytes')
