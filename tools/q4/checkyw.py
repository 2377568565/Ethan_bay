import re,html,sys
full=open('full.txt',encoding='utf-8').read()
pages=re.split(r'===== PDF页 (\d+) =====',full)
pg={int(pages[i]):pages[i+1] for i in range(1,len(pages),2)}
def norm(s): return re.sub(r'[\s　]','',s)
def check(n):
    s=open(f'_l{n:02d}.html',encoding='utf-8').read()
    y=s[s.index('<section class="yw"'):s.index('</main>')]
    t=norm(html.unescape(re.sub(r'<[^>]+>','',y)))
    first=6+7*(n-1)
    src=''.join(pg[p] for p in range(first,first+7))
    sents=[norm(x) for x in re.split(r'[。？！]',src)]
    miss=[x for x in sents if len(x)>=12 and x not in t and '�' not in x and 'page' not in x and '研经指引' not in x]
    print(f'第{n}课 原文字数 {len(t)}，疑似缺失 {len(miss)} 句')
    for m in miss[:12]: print('   -', m[:80])
for a in sys.argv[1:]: check(int(a))
