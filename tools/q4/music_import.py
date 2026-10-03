#!/usr/bin/env python3
"""把整理者的歌曲批量收进“音乐”栏目。

歌曲放在仓库 Releases 里的一个发布（草稿也可以）：
  - 拖进“说明”框：每首变成一个 user-attachments 链接，链接文字就是原来的文件名（中文也保留）。单个文件最大 25 MB。
  - 或者拖进下面的附件区：单个文件最大 2 GB，但 GitHub 会把附件名里的空格换成点、删掉中文，
    全中文名的文件还会因为“重名”传不上去——中文歌名请先压成 ZIP 再传。
然后由 .github/workflows/music.yml 运行：python3 tools/q4/music_import.py --release 标签
本地也能用：python3 tools/q4/music_import.py --dir 放歌的文件夹（需要 ffmpeg）
MP3 / M4A / FLAC / WAV / 视频都可以，ZIP 压缩包会自动解开。

处理（现在 request.json 用 codec=opus：压成 OGG〔Opus，约 70 kbps〕；以下是 heaac 的说明）：只取声音，统一音量（loudnorm），压成 48 kbps 的 HE-AAC（.m4a，约 0.36 MB/分钟，听感接近 96 kbps 的 MP3，
大小只有一半，网速慢时少卡）；去掉封面和其它标签。HE-AAC 要用完整版的 fdk-aac（music.yml 会现场编译），
没有时改用 64 kbps 的 AAC-LC。
存成 music/<编号>.m4a，曲名取自文件名（或歌曲标签），追加到 music/list.json；
在 music/sources.json 里记下收过哪些文件，下次只收新的。
--reencode：把已经收过的歌从原始文件按现在的格式重新压一遍（编号、曲名不变；--keep-old 时先留着旧文件）。
--folder 名字：这一批新歌放进哪个文件夹（没有就新建，排在最后）；不写时放进“某年某月 新收录”。
--request music/request.json：从这个文件读 release、codec、reencode、folder（GitHub 上的 music.yml 用它）。
--codec keep：不压缩，原样放上去（MP3 / M4A / OGG）。OGG（Opus、Vorbis）在较旧的苹果手机上放不出来，
所以另外压一份 48 kbps HE-AAC 备用（list.json 里的 alt），网页按手机能不能放 OGG 自动选。
"""
import argparse, datetime, hashlib, json, os, re, shutil, subprocess, sys, tempfile, urllib.parse, urllib.request, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
EXT = {'.mp3', '.m4a', '.aac', '.flac', '.wav', '.ogg', '.oga', '.opus', '.wma', '.ape', '.mp4', '.m4v', '.mov', '.webm', '.mkv', '.avi', '.flv'}
SITE_BUDGET = 450 * 1024 * 1024   # 音乐目录的上限：GitHub Pages 整个网站不能超过 1 GB


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def ext(name):
    return os.path.splitext(name)[1].lower()


def probe(path):
    """时长（秒）、标签里的曲名和歌手。没有 ffprobe 时从 ffmpeg 的输出里读"""
    try:
        out = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration:format_tags=title,artist', '-of', 'json', path]).stdout
        f = json.loads(out).get('format', {})
        tags = {k.lower(): v for k, v in (f.get('tags') or {}).items()}
        return float(f.get('duration') or 0), tags.get('title', ''), tags.get('artist', '')
    except FileNotFoundError:
        err = subprocess.run(['ffmpeg', '-hide_banner', '-i', path], capture_output=True, text=True).stderr
        m = re.search(r'Duration:\s*(\d+):(\d+):([\d.]+)', err)
        dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0
        tag = lambda k: (re.search(r'^\s{4}' + k + r'\s*:\s*(.+)$', err, re.M | re.I) or [None, ''])[1].strip()
        return dur, tag('title'), tag('artist')


JUNK = re.compile(r'\s*[\(\[【（](?:[^\)\]】）]*?(?:lyric|lyrics|歌词|歌詞|字幕|official|官方|mv|video|audio|视频|視頻|高清|hd|hq|live版?|现场|現場)[^\)\]】）]*)[\)\]】）]', re.I)
EMPTY = re.compile(r'(default|untitled|track|audio|video|vid|img|rec|recording|新建|录音|錄音|未命名)?[\s\d._()\-]*', re.I)


def clean_title(t):
    t = (t or '').strip()
    if ext(t) in EXT:
        t = os.path.splitext(t)[0]
    t = re.sub(r'\s*\(\d{1,2}\)$', '', t)   # 下载重名时加的“(1)”
    t = re.sub(r'\s*[-–—|｜]?\s*official\s+cover$', '', t, flags=re.I)
    if ' ' not in t and len(re.findall(r'[-_.]', t)) >= 2:   # “What-A-Friend-We-Have”“Be.Thou.My.Vision”
        t = re.sub(r'[-_.]+', ' ', t)
    t = JUNK.sub('', t)
    for _ in range(3):   # 去掉结尾的“- Official Lyric Video”“Lyrics”“歌词版”之类
        t = re.sub(r'\s*[-–—_|]?\s*(official\s*)?(lyrics?|lyric\s*video|music\s*video|video|audio|mv|歌词版?|歌詞版?|字幕版?|官方\s*mv|高清)\s*$', '', t, flags=re.I)
    t = re.sub(r'^\d{1,3}\s*[.\-_、．]\s*', '', t)   # 开头的曲目序号“01 - ”“3.”
    t = re.sub(r'[_]+', ' ', t)
    t = re.sub(r'\s{2,}', ' ', t).strip(' -_')
    return '' if EMPTY.fullmatch(t) else t


# 格式：扩展名、每秒千比特。opus = OGG（Opus 编码，VBR 64k，实际约 70 kbps），现在用的就是它
FMT = {'opus': ('.ogg', 64), 'heaac': ('.m4a', 48), 'aac': ('.m4a', 64), 'mp3': ('.mp3', 96)}
OGG_TYPE = 'audio/ogg; codecs="opus"'


def fdk_ok(profile):
    """fdkaac 能不能压这种格式（Ubuntu 自带的 libfdk-aac 去掉了 HE-AAC）"""
    if not shutil.which('fdkaac'):
        return False
    with tempfile.TemporaryDirectory() as t:
        w, o = os.path.join(t, 'a.wav'), os.path.join(t, 'a.m4a')
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'sine=d=1', '-ac', '2', '-ar', '44100', w], capture_output=True)
        r = subprocess.run(['fdkaac', '-S', '-p', str(profile), '-b', '48000', '-o', o, w], capture_output=True)
        return r.returncode == 0 and os.path.exists(o)


def fmt_of(codec):
    if codec == 'heaac' and not fdk_ok(5):
        print('fdkaac 不支持 HE-AAC，改用 AAC-LC 64 kbps', flush=True)
        return 'aac'
    return codec


KEEP = {'.mp3': '', '.m4a': '', '.ogg': 'audio/ogg', '.oga': 'audio/ogg', '.opus': 'audio/ogg'}   # 可以原样放上去的格式


def codec_name(path):
    try:
        out = run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_name', '-of', 'csv=p=0', path]).stdout
        return out.strip()
    except FileNotFoundError:
        m = re.search(r'Audio:\s*(\w+)', subprocess.run(['ffmpeg', '-hide_banner', '-i', path], capture_output=True, text=True).stderr)
        return m[1] if m else ''


def encode(src, dst, codec, kbps):
    pre = ['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-map', '0:a:0', '-map_metadata', '-1',
           '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ac', '2', '-ar', '44100']
    if codec == 'opus':   # Opus 只支持 48 kHz
        run(pre[:-1] + ['48000', '-c:a', 'libopus', '-b:a', f'{kbps}k', '-vbr', 'on', dst])
    elif codec == 'mp3':
        run(pre + ['-c:a', 'libmp3lame', '-b:a', f'{kbps}k', '-id3v2_version', '3', dst])
    elif codec == 'aac' and not shutil.which('fdkaac'):
        run(pre + ['-c:a', 'aac', '-b:a', f'{kbps}k', '-movflags', '+faststart', dst])
    else:   # ffmpeg 解码、统一音量 → fdkaac 压缩（HE-AAC 或 AAC-LC）；moov 放在前面，边下边播
        dec = subprocess.Popen(pre + ['-f', 'wav', '-'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        enc = subprocess.run(['fdkaac', '-S', '-p', '5' if codec == 'heaac' else '2', '-b', str(kbps * 1000), '-I', '--moov-before-mdat', '-o', dst, '-'],
                             stdin=dec.stdout, capture_output=True)
        dec.stdout.close()
        err = dec.stderr.read().decode('utf-8', 'replace')
        if dec.wait() or enc.returncode or not os.path.exists(dst) or os.path.getsize(dst) < 1000:
            raise RuntimeError('压缩失败：' + (err + enc.stderr.decode('utf-8', 'replace'))[-300:])


def save_stream(r, dst):
    with r, open(dst, 'wb') as f:
        shutil.copyfileobj(r, f, 1 << 20)


# ---------------- GitHub Releases ----------------
class _Redirect(urllib.request.HTTPRedirectHandler):
    """下载会跳转到别的网址（已带签名），这时不能再带钥匙，否则对方拒绝"""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and urllib.parse.urlsplit(newurl).netloc != urllib.parse.urlsplit(req.full_url).netloc:
            new.remove_header('Authorization')
        return new


_open = urllib.request.build_opener(_Redirect).open


def api(url, token, accept='application/vnd.github+json'):
    h = {'Accept': accept, 'User-Agent': 'Ethan_bay-music'}
    if token:
        h['Authorization'] = f'Bearer {token}'
    return _open(urllib.request.Request(url, headers=h), timeout=600)


UA_LINK = re.compile(r'https://github\.com/user-attachments/(?:files|assets)/([\w-]+)/([^)\s\]]+)')


def release_items(repo, tag, token):
    rels = json.load(api(f'https://api.github.com/repos/{repo}/releases?per_page=100', token))   # 带权限时草稿也会列出来
    rel = next((r for r in rels if tag in (r.get('tag_name'), r.get('name'))), None)
    if not rel:
        sys.exit(f'找不到标签或名称为 {tag} 的 Release。')
    items = []
    # 1) 拖进说明框的文件：链接文字是原来的文件名
    body = rel.get('body') or ''
    body = re.sub(r'(https://github\.com/user-attachments/)\s+', r'\1', body)   # 说明里换了行的链接接回去
    named = {m[2]: m[1].strip() for m in re.finditer(r'\[([^\]\n]+)\]\((' + UA_LINK.pattern + r')\)', body)}
    seen = set()
    for m in UA_LINK.finditer(body):
        url, fid = m[0], m[1]
        if fid in seen:
            continue
        seen.add(fid)
        name = named.get(url) or urllib.parse.unquote(m[2])
        items.append({'name': name, 'key': f'ua:{fid}', 'named': url in named,
                      'get': (lambda u: lambda dst: save_stream(api(u, ''), dst))(url)})
    # 2) 附件区的文件：GitHub 把附件名里的空格换成点、删掉中文，所以附件名不可靠，曲名优先用歌曲标签
    assets, page = [], 1
    while True:
        batch = json.load(api(f"https://api.github.com/repos/{repo}/releases/{rel['id']}/assets?per_page=100&page={page}", token))
        assets += batch
        if len(batch) < 100:
            break
        page += 1
    for a in assets:
        items.append({'name': a.get('label') or a['name'], 'key': f"{a['name']}|{a['size']}|{a['updated_at']}", 'named': bool(a.get('label')),
                      'get': (lambda u: lambda dst: save_stream(api(u, token, 'application/octet-stream'), dst))(a['url'])})
    return items


# ---------------- ZIP 压缩包 ----------------
def zip_name(info):
    """Windows 自带的压缩会用 GBK/Big5 存中文文件名（不标 UTF-8），这里猜回来"""
    if info.flag_bits & 0x800:
        return info.filename
    raw = info.filename.encode('cp437')
    for enc in ('utf-8', 'gb18030', 'big5'):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return info.filename


# ---------------- 主程序 ----------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--release', default='', help='Release 的标签或名称')
    ap.add_argument('--dir', default='', help='本地放歌的文件夹')
    ap.add_argument('--music', default=os.path.join(ROOT, 'music'))
    ap.add_argument('--codec', default='heaac', choices=sorted(FMT) + ['keep'])
    ap.add_argument('--reencode', action='store_true', help='把已收的歌换成现在的格式重新压一遍')
    ap.add_argument('--keep-old', action='store_true', help='重新压时先不删旧文件')
    ap.add_argument('--folder', default='', help='新歌放进哪个文件夹（名字）')
    ap.add_argument('--request', default='', help='从 request.json 读设置')
    a = ap.parse_args()
    if a.request:
        r = json.load(open(a.request, encoding='utf-8'))
        a.release = a.release or r.get('release', '')
        a.codec = r.get('codec', a.codec) if a.codec == 'heaac' else a.codec
        a.reencode = a.reencode or bool(r.get('reencode'))
        a.keep_old = a.keep_old or bool(r.get('reencode'))
        a.folder = a.folder or r.get('folder', '')
        a.kbps = int(r.get('kbps') or 0)
    os.makedirs(a.music, exist_ok=True)
    LIST, SRC = os.path.join(a.music, 'list.json'), os.path.join(a.music, 'sources.json')
    lst = json.load(open(LIST, encoding='utf-8')) if os.path.exists(LIST) else {'songs': []}
    lst.setdefault('songs', [])
    lst.setdefault('folders', [])
    done = json.load(open(SRC, encoding='utf-8')) if os.path.exists(SRC) else {}
    NAMES = os.path.join(a.music, 'names.json')   # 可选：曲名 → 显示的曲名和中文名
    names = json.load(open(NAMES, encoding='utf-8')).get('names', {}) if os.path.exists(NAMES) else {}
    if a.release:
        items = release_items(os.environ.get('GITHUB_REPOSITORY', '2377568565/Ethan_bay'), a.release, os.environ.get('GITHUB_TOKEN', ''))
    elif a.dir:
        items = []
        for d, _, fs in os.walk(a.dir):
            for n in sorted(fs):
                p = os.path.join(d, n)
                items.append({'name': n, 'key': f'{os.path.relpath(p, a.dir)}|{os.path.getsize(p)}', 'named': True, 'path': p})
    else:
        sys.exit('请指定 --release 或 --dir')
    items = sorted((it for it in items if ext(it['name']) in EXT or ext(it['name']) == '.zip'), key=lambda x: x['name'].lower())
    todo = [it for it in items if it['key'] not in done]
    keep = a.codec == 'keep'
    codec = fmt_of('heaac' if keep else a.codec)   # keep 时用它压备用的那一份，以及不能原样放的格式
    EXT_OUT, KBPS = FMT[codec]
    KBPS = getattr(a, 'kbps', 0) or KBPS
    if a.reencode:
        return reencode(a, lst, done, items, codec, LIST, SRC)
    used = sum(os.path.getsize(os.path.join(a.music, f)) for f in os.listdir(a.music) if ext(f) in ('.mp3', '.m4a'))
    print(f'找到 {len(items)} 个文件，新的 {len(todo)} 个；音乐目录现在 {used / 1048576:.0f} MB', flush=True)
    st = {'added': 0, 'used': used, 'failed': 0}

    def take(src, name, key, named, sub=''):
        """收一首：src 是本地文件"""
        dur, tag_title, artist = probe(src)
        if dur < 20:
            print(f'  {name}：只有 {dur:.0f} 秒，不像一首歌，跳过', flush=True)
            done[key] = ''
            return
        base = 'm' + hashlib.sha1(key.encode('utf-8')).hexdigest()[:8]
        sid, n = base, 1
        while any(s['id'] == sid and s.get('src') != name for s in lst['songs']):   # 编号撞了（极少见）就加个尾号
            sid, n = f'{base}{n}', n + 1
        kbps = KBPS if st['used'] + dur * KBPS * 125 <= SITE_BUDGET else KBPS * 2 // 3   # 快超过网站容量时自动压得更小
        extra = {}
        if keep and ext(name) in KEEP:   # 原样放上去
            out_ext = '.ogg' if KEEP[ext(name)] else ext(name)
            dst = os.path.join(a.music, sid + out_ext)
            shutil.copyfile(src, dst)
            if KEEP[ext(name)]:   # OGG：注明编码，另压一份 HE-AAC 给放不了 OGG 的手机
                extra['type'] = 'audio/ogg; codecs="%s"' % (codec_name(src) or 'opus')
                encode(src, os.path.join(a.music, sid + EXT_OUT), codec, kbps)
                extra['alt'] = sid + EXT_OUT
        else:
            out_ext = EXT_OUT
            dst = os.path.join(a.music, sid + out_ext)
            encode(src, dst, codec, kbps)
            if out_ext == '.ogg':
                extra['type'] = OGG_TYPE
        size = os.path.getsize(dst)
        # 曲名：文件名可靠时用文件名（整理者自己起的），否则用歌曲标签
        cands = [name, tag_title] if named else [tag_title, re.sub(r'\.(?=.*\.)', ' ', name)]   # 附件名里的点原来是空格
        title = next((t for t in map(clean_title, cands) if t), '') or '未命名'
        nm = names.get(title.lower(), {})
        title = nm.get('title') or title
        # 栏目里已经有同名、同长度的歌（同一首传了两次）就不重复收
        fid = folder_id(lst, a.folder)   # 只在同一个文件夹里查重：不同专辑的同名歌是不同的录音
        same = None if title == '未命名' else next((x for x in lst['songs'] if x['title'].lower() == title.lower() and x['id'] != sid and x.get('folder') == fid and abs(x.get('dur', 0) - dur) <= 6), None)
        if same:
            os.remove(dst)
            if extra.get('alt'):
                os.remove(os.path.join(a.music, extra['alt']))
            done[key] = same['id']
            print(f'  已经有《{same["title"]}》，跳过', flush=True)
            return
        song = {'id': sid, 'title': title, 'sub': (nm.get('sub') or artist.strip() or sub or '')[:40], 'file': os.path.basename(dst), 'dur': round(dur), 'src': name,
                'folder': folder_id(lst, a.folder)}
        if nm.get('intro'):
            song['intro'] = nm['intro']
        song.update(extra)
        lst['songs'] = [s for s in lst['songs'] if s['id'] != sid] + [song]
        done[key] = sid
        st['used'] += size
        st['added'] += 1
        print(f'  → {os.path.basename(dst)} 《{title}》 {dur / 60:.1f} 分钟，{size / 1048576:.1f} MB' + ('（原样）' if keep and ext(name) in KEEP else f'（{kbps} kbps）') + (f'，备用 {extra["alt"]}' if extra.get('alt') else ''), flush=True)
        if st['added'] % 10 == 0:   # 每收 10 首存一次，中途出问题也不白做
            save(LIST, SRC, lst, done)

    with tempfile.TemporaryDirectory() as tmp:
        for i, it in enumerate(todo, 1):
            print(f'[{i}/{len(todo)}] {it["name"]}', flush=True)
            src = it.get('path') or os.path.join(tmp, 'src' + ext(it['name']))
            try:
                if not it.get('path'):
                    it['get'](src)
                if ext(it['name']) != '.zip':
                    take(src, it['name'], it['key'], it['named'])
                    continue
                ok = True
                with zipfile.ZipFile(src) as z:
                    for info in z.infolist():
                        name = zip_name(info)
                        key = f"{it['key']}#{name}"
                        if info.is_dir() or ext(name) not in EXT or key in done or '__MACOSX' in name:
                            continue
                        part = os.path.join(tmp, 'part' + ext(name))
                        try:
                            with z.open(info) as r, open(part, 'wb') as f:
                                shutil.copyfileobj(r, f, 1 << 20)
                            take(part, os.path.basename(name), key, True, os.path.dirname(name).split('/')[-1])
                        except Exception as e:
                            ok = False
                            st['failed'] += 1
                            print(f'  {name} 处理失败：{e}', flush=True)
                        finally:
                            if os.path.exists(part):
                                os.remove(part)
                if ok:
                    done[it['key']] = 'zip'
            except Exception as e:   # 一首出错不影响其它的
                st['failed'] += 1
                print(f'  处理失败：{e}', flush=True)
            finally:
                if not it.get('path') and os.path.exists(src):
                    os.remove(src)
    save(LIST, SRC, lst, done)
    print(f'完成：新收 {st["added"]} 首，失败 {st["failed"]} 个，共 {len(lst["songs"])} 首；音乐目录 {st["used"] / 1048576:.0f} MB')
    untitled = [s['file'] for s in lst['songs'] if s['title'] == '未命名']
    if untitled:
        print(f'有 {len(untitled)} 首没找到曲名，请在 music/list.json 里补上：', ', '.join(untitled))


def reencode(a, lst, done, items, codec, LIST, SRC):
    """已经收过的歌：从原始文件按现在的格式重新压一遍（编号、曲名都不变）"""
    EXT_OUT, KBPS = FMT[codec]
    by_key = {it['key']: it for it in items}
    todo = [s for s in lst['songs'] if ext(s['file']) != EXT_OUT]
    print(f'要换成 {codec}（{KBPS} kbps {EXT_OUT}）的歌：{len(todo)} 首', flush=True)
    ok = bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, s in enumerate(todo, 1):
            it = next((by_key[k] for k, v in done.items() if v == s['id'] and k in by_key), None)
            print(f"[{i}/{len(todo)}] 《{s['title']}》", flush=True)
            if not it:
                print('  找不到原始文件，保留现在的', flush=True)
                bad += 1
                continue
            src = it.get('path') or os.path.join(tmp, 'src' + ext(it['name']))
            dst = os.path.join(a.music, s['id'] + EXT_OUT)
            try:
                if not it.get('path'):
                    it['get'](src)
                encode(src, dst, codec, KBPS)
                old = os.path.join(a.music, s['file'])
                if not a.keep_old and os.path.exists(old) and old != dst:
                    os.remove(old)
                s['file'] = s['id'] + EXT_OUT
                s['dur'] = round(probe(dst)[0]) or s.get('dur', 0)
                s.pop('alt', None)
                if EXT_OUT == '.ogg':
                    s['type'] = OGG_TYPE
                else:
                    s.pop('type', None)
                ok += 1
                print(f'  → {s["file"]} {os.path.getsize(dst) / 1048576:.2f} MB', flush=True)
            except Exception as e:
                bad += 1
                if os.path.exists(dst) and ext(s['file']) != EXT_OUT:
                    os.remove(dst)
                print(f'  失败，保留原来的：{e}', flush=True)
            finally:
                if not it.get('path') and os.path.exists(src):
                    os.remove(src)
            if ok and ok % 10 == 0:
                save(LIST, SRC, lst, done)
    save(LIST, SRC, lst, done)
    total = sum(os.path.getsize(os.path.join(a.music, s['file'])) for s in lst['songs'] if os.path.exists(os.path.join(a.music, s['file'])))
    print(f'完成：换好 {ok} 首，没换 {bad} 首；网页用到的音乐共 {total / 1048576:.0f} MB')


def folder_id(lst, name):
    """新歌放进的文件夹：按名字找，没有就新建，排在最后（不写名字时用“某年某月 新收录”）"""
    today = datetime.date.today()
    name = (name or f'{today.year}年{today.month}月 新收录').strip()
    for f in lst['folders']:
        if f['name'] == name:
            return f['id']
    fid = 'f' + hashlib.sha1(name.encode('utf-8')).hexdigest()[:6]
    lst['folders'].append({'id': fid, 'name': name, 'sub': '', 'date': today.isoformat()})
    print(f'新建文件夹《{name}》', flush=True)
    return fid


def save(LIST, SRC, lst, done):
    with open(LIST, 'w', encoding='utf-8') as f:
        json.dump(lst, f, ensure_ascii=False, indent=1)
    with open(SRC, 'w', encoding='utf-8') as f:
        json.dump(done, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
