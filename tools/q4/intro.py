"""本季导言章：学课原文（导言两页）+ 全季总览解读（取自全季剖析 Markdown 的 〇—四 部分）。"""
import re, html

MD_PATH = '/home/user/Ethan_bay/lessons/2026-Q4-gift-of-prophecy.md'

def inline(s, fmt):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'(?<![*\w])\*([^*\n]+?)\*(?!\*)', r'<i class="tr">\1</i>', s)
    return fmt(s)

def md_blocks(lines, fmt):
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip() or ln.strip() == '---':
            i += 1; continue
        if ln.startswith('### '):
            out.append(f'<h3 class="ph">{inline(ln[4:], fmt)}</h3>'); i += 1; continue
        if ln.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', c) for c in cells): rows.append(cells)
                i += 1
            th = ''.join(f'<th>{inline(c, fmt)}</th>' for c in rows[0])
            tb = ''.join('<tr>' + ''.join(f'<td>{inline(c, fmt)}</td>' for c in r) + '</tr>' for r in rows[1:])
            out.append(f'<div class="tbl"><table><thead><tr>{th}</tr></thead><tbody>{tb}</tbody></table></div>')
            continue
        if ln.startswith('> '):
            q = []
            while i < len(lines) and lines[i].startswith('>'):
                q.append(inline(lines[i].lstrip('> ').rstrip(), fmt)); i += 1
            out.append(f'<blockquote class="pq">{"<br>".join(q)}</blockquote>'); continue
        m = re.match(r'(\d+)\. |- ', ln)
        if m:
            tag = 'ol' if ln[0].isdigit() else 'ul'; items = []
            while i < len(lines) and re.match(r'(\d+)\. |- ', lines[i]):
                items.append(inline(re.sub(r'^(\d+\. |- )', '', lines[i]), fmt)); i += 1
            out.append(f'<{tag}>' + ''.join(f'<li>{x}</li>' for x in items) + f'</{tag}>'); continue
        para = [ln]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'(#|\||> |\d+\. |- |---)', lines[i]):
            para.append(lines[i]); i += 1
        out.append(f'<p>{inline("".join(p.strip() for p in para), fmt)}</p>')
    return '\n'.join(out)

def overview_sections(fmt):
    text = open(MD_PATH, encoding='utf-8').read()
    parts = re.split(r'^## ', text, flags=re.M)[1:]
    secs = []
    for p in parts:
        title, _, body = p.partition('\n')
        if title.startswith('五'): break
        num, _, name = title.partition('、')
        secs.append((num, name.strip(), md_blocks(body.split('\n'), fmt)))
    return secs

def render_intro(yw_article, fmt):
    secs = overview_sections(fmt)
    keys = [f'ov{i}' for i in range(len(secs))]
    nav_ov = ''.join(f'<a href="#{k}"><span class="d">{n}</span><span class="t">{t}</span></a>' for k, (n, t, _) in zip(keys, secs))
    days = []
    for k, (n, t, body) in zip(keys, secs):
        days.append(f'''<section class="day" id="{k}">
  <header class="dayhead">
    <p class="when"><span class="dn">全季总览 · {n}</span></p>
    <h2>{t}</h2>
    {'<p class="btnrow"><a class="btn" href="#yw-intro">阅读导言原文 →</a></p>' if k == 'ov0' else ''}
  </header>
  <div class="prose">{body}</div>
</section>''')
    yw_article = yw_article.replace('<h3 class="ywtitle">预言的恩赐</h3>',
        '<h3 class="ywtitle">预言的恩赐</h3>\n    <p class="btnrow"><a class="btn" href="#ov0">查看全季总览解读 →</a></p>')
    yw_article = yw_article.replace('</div>\n</article>',
        '</div>\n  <p class="btnrow end"><a class="btn ghost" href="#ov0">原文读完，查看全季总览 →</a></p>\n</article>')
    return f'''<header class="masthead">
  <p class="eyebrow">安息日学研经指引 · 2026年第4季 ·《预言的恩赐》</p>
  <p class="meta"><b>本季导言</b><span>9月26日—12月25日 · 共十三课</span></p>
  <h1>预言的恩赐</h1>
  <div class="memory">
    <span class="k">本季主题经文 · 希伯来书1:1、2</span>
    <blockquote>“上帝既在古时借着众先知多次多方地晓谕列祖，就在这末世借着他儿子晓谕我们；又早已立他为承受万有的，也曾借着他创造诸世界。”</blockquote>
  </div>
  <p class="btnrow top"><a class="btn solid" href="#yuanwen">导言原文</a><a class="btn" href="#yandu">全季总览</a></p>
</header>

<div class="layout">
<nav class="nav" aria-label="导言目录">
  <div class="navrow" data-row="yw"><span class="k">原文</span><a href="#yw-intro"><span class="d">导言</span><span class="t">预言的恩赐</span></a></div>
  <div class="navrow" data-row="jd"><span class="k">解读</span>{nav_ov}</div>
</nav>
<main>
<section class="yw" id="yuanwen">
  <header class="parthead">
    <p class="k">第一部分</p>
    <h2>学课原文</h2>
    <p>《安息日学研经指引》2026年第4季的导言原文。</p>
  </header>
{yw_article}
</section>
<header class="parthead jdhead" id="yandu">
  <p class="k">第二部分</p>
  <h2>全季总览解读</h2>
  <p>先看全季的主线、结构和“知 · 信 · 行”，再进入第1课。</p>
</header>
{chr(10).join(days)}
<p class="btnrow end"><a class="btn solid" href="#NEXTLESSON">进入第1课 →</a></p>
</main>
</div>'''
