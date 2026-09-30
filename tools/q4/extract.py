import pymupdf, json, re, sys, html
PDF='/root/.claude/uploads/7a8f6135-8731-54b9-8b54-015171d16fd2/d03e8250-16051.pdf'
doc=pymupdf.open(PDF)
END='。？！”」）)?!'
def page_blocks(pno):
    p=doc[pno]; W=p.rect.width; mid=W/2
    out=[]
    for b in p.get_text('dict')['blocks']:
        if b['type']!=0: continue
        x0,y0,x1,y1=b['bbox']
        spans=[s for l in b['lines'] for s in l['spans'] if s['text'].strip()!='' or s['text']==' ']
        if not spans: continue
        txt=''.join(s['text'] for s in spans).strip()
        if not txt: continue
        sizes=[s['size'] for s in spans]; fonts=[s['font'] for s in spans]
        if y0<50 and max(sizes)<=10: continue          # running header
        if txt in ('page',) or re.fullmatch(r'\d+',txt): continue
        kind='p'
        if any('SerifCN-Bold' in f for f in fonts) and max(sizes)>=14: kind='title'
        elif any('Kaiti' in f for f in fonts): kind='q'
        col=0 if (x0<mid-20 or (x1-x0)>W*0.6) else 1
        # build html with small-size spans as refs
        parts=[]; cur=None; buf=''
        for s in spans:
            r = s['size']<9.5 and kind!='title'
            if cur is None: cur=r
            if r!=cur:
                parts.append((cur,buf)); buf=''; cur=r
            buf+=s['text']
        parts.append((cur,buf))
        h=''.join((f'<span class="ref">{html.escape(t)}</span>' if r else html.escape(t)) for r,t in parts)
        out.append(dict(col=col,y=y0,x=x0,kind=kind,text=txt,html=h,size=max(sizes)))
    out.sort(key=lambda b:(b['col'],b['y']))
    return out
def merge(blocks):
    res=[]
    for b in blocks:
        if res and b['kind']==res[-1]['kind'] and b['kind'] in('p','q') and not res[-1]['text'].rstrip().endswith(tuple(END)):
            res[-1]['text']+=b['text']; res[-1]['html']+=b['html']
        else: res.append(dict(b))
    return res
if __name__=='__main__':
    for pno in map(int,sys.argv[1:]):
        print(f'===== page {pno+1}')
        for b in merge(page_blocks(pno)):
            print(f"[{b['kind']}|c{b['col']}|{b['size']:.0f}] {b['text']}")
