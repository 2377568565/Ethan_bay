#!/usr/bin/env python3
"""把整理者上传的歌曲批量收进“音乐”栏目。

原始文件（MP3 / M4A / FLAC / WAV / 视频都可以，每个最大 2 GB）先作为附件传到仓库 Releases 里一个
标签为 music-src 的草稿（草稿不公开），然后由 .github/workflows/music.yml 运行本程序：
  1. 下载还没收过的附件；
  2. 只取声音，统一音量（loudnorm），压成 96 kbps 的 MP3（约 0.7 MB/分钟），去掉封面和其它标签；
  3. 存成 music/<编号>.mp3，曲名取自歌曲标签或文件名，追加到 music/list.json；
  4. 在 music/sources.json 里记下收过哪些附件，下次只收新的。

本地也能用：python3 tools/q4/music_import.py --dir 放歌的文件夹
"""
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, '..', '..'))
EXT = {'.mp3', '.m4a', '.aac', '.flac', '.wav', '.ogg', '.oga', '.opus', '.wma', '.ape', '.mp4', '.m4v', '.mov', '.webm', '.mkv', '.avi', '.flv'}
SITE_BUDGET = 450 * 1024 * 1024   # 音乐目录的上限：GitHub Pages 整个网站不能超过 1 GB


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


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


JUNK = re.compile(r'\s*[\(\[【（](?:[^\)\]】）]*?(?:lyric|lyrics|歌词|字幕|official|官方|mv|video|audio|视频|高清|hd|hq|live版?|现场)[^\)\]】）]*)[\)\]】）]', re.I)


def clean_title(t):
    t = t.strip()
    if os.path.splitext(t)[1].lower() in EXT:
        t = os.path.splitext(t)[0]
    t = JUNK.sub('', t)
    for _ in range(3):   # 去掉结尾的“- Official Lyric Video”“Lyrics”“歌词版”之类
        t = re.sub(r'\s*[-–—_|]?\s*(official\s*)?(lyrics?|lyric\s*video|music\s*video|video|audio|mv|歌词版?|字幕版?|官方\s*mv|高清)\s*$', '', t, flags=re.I)
    t = re.sub(r'[_]+', ' ', t)
    return re.sub(r'\s{2,}', ' ', t).strip(' -_') or '未命名'


def encode(src, dst, kbps):
    run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-map', '0:a:0', '-map_metadata', '-1',
         '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11', '-ac', '2', '-ar', '44100',
         '-c:a', 'libmp3lame', '-b:a', f'{kbps}k', '-id3v2_version', '3', dst])


class _Redirect(urllib.request.HTTPRedirectHandler):
    """附件下载会跳转到别的网址（已带签名），这时不能再带钥匙，否则对方拒绝"""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new is not None and urllib.parse.urlsplit(newurl).netloc != urllib.parse.urlsplit(req.full_url).netloc:
            new.remove_header('Authorization')
        return new


_open = urllib.request.build_opener(_Redirect).open


def api(url, token, accept='application/vnd.github+json'):
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}', 'Accept': accept, 'User-Agent': 'Ethan_bay-music'})
    return _open(req, timeout=600)


def release_assets(repo, tag, token):
    rels = json.load(api(f'https://api.github.com/repos/{repo}/releases?per_page=100', token))   # 带权限时草稿也会列出来
    rel = next((r for r in rels if r.get('tag_name') == tag or r.get('name') == tag), None)
    if not rel:
        sys.exit(f'找不到标签为 {tag} 的 Release（草稿也可以）。请先在仓库 Releases 里新建一个，把歌曲作为附件传上去。')
    assets = []
    page = 1
    while True:
        batch = json.load(api(f"https://api.github.com/repos/{repo}/releases/{rel['id']}/assets?per_page=100&page={page}", token))
        assets += batch
        if len(batch) < 100:
            break
        page += 1
    return [{'name': a['name'], 'label': a.get('label') or '', 'size': a['size'], 'key': f"{a['name']}|{a['size']}|{a['updated_at']}", 'url': a['url']} for a in assets]


def file_title(it):
    """附件名：GitHub 会把空格换成点，所以没有原名（label）时把点换回空格"""
    if it.get('label'):
        return it['label']
    base, ext = os.path.splitext(it['name'])
    if it.get('url') and ' ' not in base and base.count('.') >= 1:
        base = base.replace('.', ' ')
    return base


def download(asset, token, dst):
    with api(asset['url'], token, 'application/octet-stream') as r, open(dst, 'wb') as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--release', default='', help='Release 的标签（例如 music-src）')
    ap.add_argument('--dir', default='', help='或者：本地放歌的文件夹')
    ap.add_argument('--music', default=os.path.join(ROOT, 'music'))
    ap.add_argument('--kbps', type=int, default=96)
    a = ap.parse_args()
    os.makedirs(a.music, exist_ok=True)
    LIST, SRC = os.path.join(a.music, 'list.json'), os.path.join(a.music, 'sources.json')
    lst = json.load(open(LIST, encoding='utf-8')) if os.path.exists(LIST) else {'songs': []}
    lst.setdefault('songs', [])
    done = json.load(open(SRC, encoding='utf-8')) if os.path.exists(SRC) else {}
    token = os.environ.get('GITHUB_TOKEN', '')
    if a.release:
        items = release_assets(os.environ.get('GITHUB_REPOSITORY', '2377568565/Ethan_bay'), a.release, token)
    elif a.dir:
        items = [{'name': n, 'size': os.path.getsize(os.path.join(a.dir, n)), 'path': os.path.join(a.dir, n)} for n in sorted(os.listdir(a.dir))]
        for it in items:
            it['key'] = f"{it['name']}|{it['size']}"
    else:
        sys.exit('请指定 --release 或 --dir')
    items = [it for it in items if os.path.splitext(it['name'])[1].lower() in EXT]
    todo = [it for it in items if it['key'] not in done]
    used = sum(os.path.getsize(os.path.join(a.music, f)) for f in os.listdir(a.music) if f.endswith('.mp3'))
    print(f'附件 {len(items)} 个，新的 {len(todo)} 个；音乐目录现在 {used / 1048576:.0f} MB')
    ids = {s['id'] for s in lst['songs']}
    added = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, it in enumerate(sorted(todo, key=lambda x: x['name'].lower()), 1):
            src = it.get('path') or os.path.join(tmp, 'src' + os.path.splitext(it['name'])[1].lower())
            try:
                if not it.get('path'):
                    download(it, token, src)
                dur, tag_title, artist = probe(src)
                base = 'm' + hashlib.sha1(it['name'].encode('utf-8')).hexdigest()[:8]
                sid, n = base, 1
                while any(s['id'] == sid and s.get('src') != it['name'] for s in lst['songs']):   # 编号撞了（极少见）就加个尾号
                    sid, n = f'{base}{n}', n + 1
                kbps = a.kbps
                if used + dur * kbps * 125 > SITE_BUDGET:   # 快超过网站容量时自动压得更小
                    kbps = 64
                dst = os.path.join(a.music, sid + '.mp3')
                encode(src, dst, kbps)
                size = os.path.getsize(dst)
                used += size
                title = clean_title(tag_title if tag_title and not re.fullmatch(r'(track\s*)?\d+', tag_title, re.I) else file_title(it))
                if re.fullmatch(r'(default|untitled|track)?[\s\d._-]*', title, re.I):
                    title = '未命名'
                # 栏目里已经有同名、同长度的歌（同一首传了两次）就不重复收
                same = None if title == '未命名' else next((x for x in lst['songs'] if x['title'].lower() == title.lower() and x['id'] != sid and abs(x.get('dur', 0) - dur) < 3), None)
                if same:
                    os.remove(dst);used -= size;done[it['key']] = same['id']
                    print(f'[{i}/{len(todo)}] {it["name"]}：已经有《{same["title"]}》，跳过', flush=True)
                    continue
                song = {'id': sid, 'title': title, 'sub': artist.strip()[:40], 'file': sid + '.mp3', 'dur': round(dur), 'src': it['name']}
                lst['songs'] = [s for s in lst['songs'] if s['id'] != sid] + [song]
                ids.add(sid)
                done[it['key']] = sid
                added += 1
                print(f'[{i}/{len(todo)}] {it["name"]} → {sid}.mp3 《{title}》 {dur / 60:.1f} 分钟，{size / 1048576:.1f} MB（{kbps} kbps）', flush=True)
            except Exception as e:   # 一首出错不影响其它的
                print(f'[{i}/{len(todo)}] {it["name"]} 处理失败：{e}', flush=True)
            finally:
                if not it.get('path') and os.path.exists(src):
                    os.remove(src)
            if added and added % 10 == 0:   # 每收 10 首存一次，中途出问题也不白做
                save(LIST, SRC, lst, done)
    save(LIST, SRC, lst, done)
    print(f'完成：新收 {added} 首，共 {len(lst["songs"])} 首；音乐目录 {used / 1048576:.0f} MB')


def save(LIST, SRC, lst, done):
    with open(LIST, 'w', encoding='utf-8') as f:
        json.dump(lst, f, ensure_ascii=False, indent=1)
    with open(SRC, 'w', encoding='utf-8') as f:
        json.dump(done, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
