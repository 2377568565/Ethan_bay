# 临时（2026-10-26，圣经栏目第二期）：在 GitHub 上下载容器里打不开的两份公开数据，整理成精简结果，
# 压缩后存进 tools/q4/bdata/ 由工作流提交（简短情况写进“检查结果”）。查完删除本文件和 .github/workflows/tmp-src.yml。
#  1) BSB（Berean Standard Bible，CC0）USFM：小标题的位置和英文、哪些节是诗歌（\q）
#  2) ChiUns（和合本简体，带 Strong 编号，CrossWire，公有领域）：每个原文编号在和合本里译成哪些词
import io, os, re, zipfile, json, gzip, base64, collections, requests
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) Chrome/124 Safari/537.36'}
api = f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/check-runs"
hd = {'Authorization': 'Bearer ' + os.environ['GH_TOKEN'], 'Accept': 'application/vnd.github+json'}


def post(key, text):
    r = requests.post(api, headers=hd, json={'name': f'chk:{key}', 'head_sha': os.environ['GITHUB_SHA'], 'status': 'completed',
                                            'conclusion': 'neutral', 'output': {'title': key, 'summary': key, 'text': text[:65000]}})
    print('check', key, r.status_code, flush=True)


OUTD = 'tools/q4/bdata'
os.makedirs(OUTD, exist_ok=True)


def send(key, obj):   # 存成文件，最后由工作流提交到本分支
    s = json.dumps(obj, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode()
    open(os.path.join(OUTD, key + '.json.gz'), 'wb').write(gzip.compress(s, 9, mtime=0))
    post(key, f'{key}: {len(s)} bytes')


def bsb():
    for url in ['https://ebible.org/Scriptures/engbsb_usfm.zip', 'https://bereanbible.com/bsb_usfm.zip']:
        try:
            r = requests.get(url, headers=UA, timeout=120)
            print(url, r.status_code, len(r.content), flush=True)
            if r.status_code == 200 and r.content[:2] == b'PK':
                break
        except Exception as e:
            print(url, e)
    else:
        post('bsb-fail', 'no usfm'); return
    z = zipfile.ZipFile(io.BytesIO(r.content))
    heads, poetry, notes = [], {}, []
    for name in sorted(z.namelist()):
        if not name.lower().endswith(('.usfm', '.sfm')):
            continue
        t = z.read(name).decode('utf-8-sig')
        m = re.search(r'\\id (\w+)', t)
        if not m:
            continue
        bk = m.group(1)
        c, v, pend = 0, 0, []
        inq = False
        for line in t.split('\n'):
            line = line.rstrip()
            mm = re.match(r'\\(\w+\d?)\s?(.*)', line)
            if not mm:
                continue
            tag, rest = mm.group(1), mm.group(2)
            if tag == 'c':
                c, v = int(rest.split()[0]), 0; continue
            if tag in ('s', 's1', 's2', 's3', 'ms', 'ms1', 'ms2', 'd', 'mr', 'sr', 'r', 'qa'):
                txt = re.sub(r'\\\w+\*?', '', rest).strip()
                pend.append((tag, txt)); continue
            if tag.startswith('q') or tag in ('p', 'm', 'pi', 'pi1', 'pi2', 'li', 'li1', 'li2', 'pc', 'nb', 'b', 'mi'):
                inq = tag.startswith('q') and tag not in ('qa',)
                if inq and v and not re.match(r'\\\w+\s*\\v ', line):   # 本行不是以新的一节开头：是上一节的续行
                    poetry.setdefault(f'{bk}.{c}', set()).add(v)
                if tag.startswith('q') and tag not in ('qa',):
                    pass
            for vm in re.finditer(r'\\v (\d+)', line):
                v = int(vm.group(1))
                for tg, tx in pend:
                    heads.append([bk, c, v, tg, tx])
                pend = []
                if inq:
                    poetry.setdefault(f'{bk}.{c}', set()).add(v)
            # a \q line without \v continues the current verse
    send('bsbh', heads)
    send('bsbq', {k: sorted(s) for k, s in poetry.items()})
    post('bsb-info', f'heads {len(heads)} poetry chapters {len(poetry)} files {len(z.namelist())}\n' + '\n'.join(sorted(z.namelist())[:5]))


def chius():
    url = 'https://www.crosswire.org/ftpmirror/pub/sword/packages/rawzip/ChiUns.zip'
    r = requests.get(url, headers=UA, timeout=120)
    print(url, r.status_code, len(r.content), flush=True)
    if r.status_code != 200:
        post('cuvs-fail', str(r.status_code)); return
    d = '/tmp/sw'
    zipfile.ZipFile(io.BytesIO(r.content)).extractall(d)
    conf = open(os.path.join(d, 'mods.d', 'chiuns.conf'), encoding='utf-8', errors='replace').read()
    post('cuvs-conf', conf[:6000])
    from pysword.modules import SwordModules
    mods = SwordModules(d).parse_modules()
    print(list(mods), flush=True)
    bible = SwordModules(d).get_bible_from_module(list(mods)[0])
    from pysword.canons import canons
    can = canons['kjv']
    cnt = collections.defaultdict(collections.Counter)
    sample, per = [], {}
    for testament in ('ot', 'nt'):
        for bi, bk in enumerate(can[testament]):
            name, osis, _, chs = bk[0], bk[1], bk[2], bk[3]
            for ci, nv in enumerate(chs):
                for vi in range(nv):
                    try:
                        raw = bible.get(books=[name], chapters=[ci + 1], verses=[vi + 1], clean=False)
                    except Exception as e:
                        continue
                    if len(sample) < 6 and ci == 0 and vi < 2:
                        sample.append(raw[:600])
                    toks = []
                    for m in re.finditer(r'<w\b([^>]*)>(.*?)</w>|([^<]+)', raw):
                        if m.group(3) is not None:
                            toks.append(['', re.sub(r'\s+', '', m.group(3))]); continue
                        lm = re.findall(r'strong:([HG]\d+[a-z]?)', m.group(1))
                        w = re.sub(r'<[^>]+>', '', m.group(2)).strip()
                        toks.append([' '.join(lm), w])
                        for s in lm:
                            if w:
                                cnt[s][w] += 1
                    per[f'{osis}.{ci + 1}.{vi + 1}'] = toks
    post('cuvs-sample', '\n\n'.join(sample))
    top = {s: c.most_common(6) for s, c in cnt.items()}
    send('cuvs', top)
    send('cuva', per)


for f in (bsb, chius):
    try:
        f()
    except Exception as e:
        import traceback
        post(f.__name__ + '-err', traceback.format_exc()[-3000:])
