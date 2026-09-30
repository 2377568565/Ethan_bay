import re, html, sys, json
sys.path.insert(0, __import__('os').path.dirname(__import__('os').path.abspath(__file__)))
from extract import page_blocks
END = '。？！”」）)?!'
DAYS = [('sab','安息日下午'),('sun','星期日'),('mon','星期一'),('tue','星期二'),('wed','星期三'),('thu','星期四'),('fri','星期五')]
REF = re.compile(r'（[^（）]{0,60}?\d+：[\d\-、，；,]+[^（）]{0,20}?）')

def clean(t):
    t=t.replace('�','').replace('㸝','安')
    t=re.sub(r'\s+：','：',t)
    t=re.sub(r'(?<=[一-鿿]) (?=\d)','',t)
    return t.strip()

def merged(pno):
    res=[]
    for b in page_blocks(pno):
        t=clean(b['text'])
        if '安息日学研经指引' in t and b['y']<60: continue
        b=dict(b); b['text']=t; b['html']=clean(b['html'])
        if res and b['kind']!='title' and res[-1]['kind']!='title' and not res[-1]['text'].endswith(tuple(END)):
            res[-1]['text']+=b['text']; res[-1]['html']+=b['html']
        else:
            res.append(b)
    return res

def para_html(kind, h, text, qlink=None):
    if kind=='q':
        link=f' <a class="toans" href="#{qlink}">看参考解答 →</a>' if qlink else ''
        qid = f' id="yw-{qlink}"' if qlink else ''
        return f'<p class="yq"{qid}>{h}</p>' + (f'<p class="yqlink">{link.strip()}</p>' if link else '')
    if text.startswith('■'):
        return f'<p class="ynote">{h}</p>'
    if text.startswith('“') and ('─怀爱伦' in text or '─《' in text or '─ 怀爱伦' in text):
        return f'<blockquote class="yquote">{h}</blockquote>'
    if text.startswith('欲了解更多内容'):
        return f'<p class="ynote">{h}</p>'
    return f'<p>{h}</p>'

def esc_with_refs(t):
    # escape and wrap scripture refs in parentheses for manual text
    out=html.escape(t)
    return re.sub(r'（([^（）]*?\d+：[^（）]*?)）', r'<span class="ref">（\1）</span>', out)

def day_article(key, dayname, date, title, paras, lesson_title=None, head_extra=''):
    body='\n'.join(paras)
    nxt = {'sab':'sun','sun':'mon','mon':'tue','tue':'wed','wed':'thu','thu':'fri'}.get(key)
    nxtname = dict(DAYS).get(nxt,'')
    nav = f'<a class="btn ghost" href="#{key}">返回本日解读</a>'
    if nxt: nav += f'<a class="btn ghost" href="#yw-{nxt}">下一天原文：{nxtname} →</a>'
    else: nav += '<a class="btn ghost" href="#sab">原文读完，开始逐日解读 →</a>'
    return f'''<article class="ywday" id="yw-{key}">
  <header class="ywhead">
    <p class="when"><span class="dn">{dayname}</span><span class="dt">{date}</span><span class="src">学课原文</span></p>
    <h3 class="ywtitle">{html.escape(title)}</h3>
    <p class="btnrow"><a class="btn" href="#{key}">查看本日解读 →</a></p>
  </header>
  {head_extra}
  <div class="ywbody">
{body}
  </div>
  <p class="btnrow end">{nav}</p>
</article>'''

def build(lesson_no, first_page, dates, lesson_title, overrides, qids, intro_pages=None):
    arts=[]
    if intro_pages:
        paras=[]
        for pno in intro_pages:
            for b in merged(pno):
                if b['kind']=='title': continue
                paras.append(b)
        # merge across pages
        mp=[]
        for b in paras:
            if mp and not mp[-1]['text'].endswith(tuple(END)):
                mp[-1]['text']+=b['text']; mp[-1]['html']+=b['html']
            else: mp.append(b)
        out=[]
        for b in mp:
            t=b['text']
            if t.startswith('上帝使用预言的恩赐有五个关键目的'):
                m=re.match(r'(上帝使用预言的恩赐有五个关键目的：)1(.*?)2(.*?)3(.*?)4(.*?)5(.*?。)(.*)$',t)
                items=''.join(f'<li>{esc_with_refs(x)}</li>' for x in m.groups()[1:6])
                out.append(f'<p>{esc_with_refs(m.group(1))}</p><ol class="yol">{items}</ol><p>{esc_with_refs(m.group(7))}</p>')
            else:
                out.append(f'<p>{esc_with_refs(t)}</p>')
        arts.append(f'''<article class="ywday" id="yw-intro">
  <header class="ywhead">
    <p class="when"><span class="dn">本季导言</span><span class="src">学课原文</span></p>
    <h3 class="ywtitle">预言的恩赐</h3>
  </header>
  <div class="ywbody">
{chr(10).join(out)}
  </div>
</article>''')
    for i,(key,dayname) in enumerate(DAYS):
        pno=first_page+i
        date=dates[i]
        qn=0; paras=[]
        if key in overrides:
            title, items = overrides[key]
            for kind, t in items:
                if kind=='q':
                    qn+=1; qid=qids.get(f'{key}-{qn}')
                    paras.append(para_html('q', esc_with_refs(t), t, qid))
                elif kind=='html':
                    paras.append(t)
                else:
                    paras.append(para_html(kind, esc_with_refs(t), t))
            arts.append(day_article(key, dayname, date, title, paras))
            continue
        blocks=merged(pno)
        if key=='sab':
            allhead=''.join(b['text'] for b in blocks[:3])
            reading=re.search(r'阅读本周学课经文(.*?。)', allhead).group(1)
            used={0}
            for j,b in enumerate(blocks[:3]):
                if b['text'].startswith('阅读本周学课经文'): used.add(j)
            mi=[j for j,b in enumerate(blocks) if b['text'].startswith('存心节')][0]
            used.add(mi)
            memtext=blocks[mi]['text'][len('存心节'):]
            if not memtext.rstrip().endswith('）') and mi+1<len(blocks) and blocks[mi+1]['text'].startswith('（') and len(blocks[mi+1]['text'])<30:
                memtext+=blocks[mi+1]['text']; used.add(mi+1)
            extra=f'''<div class="ywbox"><p><b>阅读本周学课经文</b><br>{esc_with_refs(reading)}</p><p><b>存心节</b><br>{esc_with_refs(memtext)}</p></div>'''
            for j,b in enumerate(blocks):
                if j in used: continue
                paras.append(para_html('p', b['html'], b['text']))
            arts.append(day_article(key, dayname, date, lesson_title, paras, head_extra=extra))
            continue
        title=[b for b in blocks if b['kind']=='title'][0]['text']
        for b in blocks:
            if b['kind']=='title': continue
            if b['kind']=='q':
                qn+=1; qid=qids.get(f'{key}-{qn}')
                paras.append(para_html('q', b['html'], b['text'], qid))
            else:
                paras.append(para_html('p', b['html'], b['text']))
        arts.append(day_article(key, dayname, date, title, paras))
    return '\n'.join(arts)
