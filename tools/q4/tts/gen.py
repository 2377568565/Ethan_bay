#!/usr/bin/env python3
"""把朗读稿（tts/script.json）合成成声音文件。在 GitHub Actions 里运行（需要下载模型，CPU 即可）。

    python3 gen.py --engine kokoro --voice zf_001 --ids l1-yw-thu --out out/
    python3 gen.py --engine cosy3 --voice f --kinds yw --lessons 1,2 --out out/

每个朗读单位输出：<out>/<id>.mp3，以及 <out>/<id>.json（每段开始的秒数、总长、段落指纹的校验码），
网页靠后者在播放时逐段高亮。
"""
import argparse, json, os, re, subprocess, sys, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 24000
PAUSE_HEAD = 0.6    # 标题后停顿（秒）
PAUSE_PARA = 0.38   # 段落之间停顿


def fphash(fps):
    """和网页里的算法一致：把每段指纹用 | 连起来，算 32 位 FNV-1a，转成 16 进制"""
    h = 0x811c9dc5
    for ch in '|'.join(fps):
        for b in ch.encode('utf-16-le'):
            h ^= b
            h = (h * 0x01000193) & 0xffffffff
    return format(h, '08x')


# ---------------- 引擎 ----------------
class Kokoro:
    def __init__(self, voice):
        import torch
        from kokoro import KModel, KPipeline
        repo = 'hexgrad/Kokoro-82M-v1.1-zh'
        torch.set_num_threads(os.cpu_count() or 4)
        self.model = KModel(repo_id=repo).eval()
        en = KPipeline(lang_code='a', repo_id=repo, model=False)

        def en_callable(text):
            return next(en(text)).phonemes
        self.pipe = KPipeline(lang_code='z', repo_id=repo, model=self.model, en_callable=en_callable)
        self.voice = voice

    @staticmethod
    def speed(n):   # 官方建议：长句稍放慢
        s = 0.8 if n > 183 else (1 if n <= 83 else 1 - (n - 83) / 500)
        return s * 1.05

    def __call__(self, text):
        parts = [r.audio.numpy() for r in self.pipe(text, voice=self.voice, speed=self.speed) if r.audio is not None]
        return np.concatenate(parts) if parts else np.zeros(0, np.float32)


class Cosy:
    """CosyVoice3 / CosyVoice2（通义实验室开源，Apache-2.0）。voice: f=女声（官方示例提示音），m=男声（用 300M-SFT 的“中文男”做提示音）"""
    PROMPTS = {
        'f': ('asset/zero_shot_prompt.wav', '希望你以后能够做的比我还好呦。'),
        'm': (os.path.join(HERE, 'voices', 'm.wav'), '在上帝的话语里，我们找到安慰和盼望，也找到前行的力量。'),
        'w': (os.path.join(HERE, 'voices', 'w.wav'), '各位弟兄姊妹，今天我们一起来认识自己的身体，学习怎样好好照顾它。'),
    }
    SFT_SPK = {'m': '中文男', 'w': '中文女'}   # 用 CosyVoice-300M-SFT 内置的声音先合成一句话，当作提示音

    def __init__(self, voice, model_dir, repo_dir, v3=True, instruct='', speed=1.0):
        sys.path.insert(0, repo_dir)
        sys.path.insert(0, os.path.join(repo_dir, 'third_party', 'Matcha-TTS'))
        import torch
        torch.set_num_threads(os.cpu_count() or 4)
        from cosyvoice.cli.cosyvoice import AutoModel
        self.m = AutoModel(model_dir=model_dir)
        global SR
        SR = self.m.sample_rate
        wav, text = self.PROMPTS[voice]
        if not os.path.isabs(wav):
            wav = os.path.join(repo_dir, wav)
        if voice in self.SFT_SPK and not os.path.exists(wav):
            raise SystemExit(f'缺少提示音 voices/{voice}.wav：先用 --make-prompt 生成')
        self.prompt_wav = wav
        self.prompt_text = ('You are a helpful assistant.<|endofprompt|>' + text) if v3 else text
        self.instruct = instruct
        self.v3 = v3
        self.speed = speed

    def __call__(self, text):
        if self.instruct:
            ins = 'You are a helpful assistant. ' + self.instruct + '<|endofprompt|>'
            call = lambda **k: self.m.inference_instruct2(text, ins, self.prompt_wav, stream=False, **k)
        else:
            call = lambda **k: self.m.inference_zero_shot(text, self.prompt_text, self.prompt_wav, stream=False, **k)
        try:
            parts = [j['tts_speech'].squeeze(0).cpu().numpy() for j in call(speed=self.speed)]
        except TypeError:            # 旧版接口没有 speed 参数
            parts = [j['tts_speech'].squeeze(0).cpu().numpy() for j in call()]
        return np.concatenate(parts) if parts else np.zeros(0, np.float32)



class Vox:
    """VoxCPM2（OpenBMB 开源，Apache-2.0，2B）。两种用法：
    voice=f：照着官方真人提示音（voices/f.wav，来自 CosyVoice 仓库）说话；
    design='一段声音描述'：先按描述“设计”一个声音说一句开场白（固定随机种子，各台机器得到同一个声音），再照着它读全文。"""
    DESIGN_TEXT = '各位弟兄姊妹，大家好。今天我们一起来聊一聊身体的健康，学一学怎样好好照顾自己。'

    def __init__(self, voice, model_dir, design='', seed=2026):
        import torch, random, hashlib
        torch.set_num_threads(os.cpu_count() or 4)
        cfg = os.path.join(model_dir, 'config.json')
        c = json.load(open(cfg))
        if c.get('dtype') != 'float32':          # CPU 上用 float32 更快、更稳
            c['dtype'] = 'float32'
            json.dump(c, open(cfg, 'w'))
        from voxcpm import VoxCPM
        self.m = VoxCPM(voxcpm_model_path=model_dir, zipenhancer_model_path=None, enable_denoiser=False,
                        optimize=False, device='cpu')
        global SR
        SR = self.m.tts_model.sample_rate
        if design:
            torch.manual_seed(seed); random.seed(seed); np.random.seed(seed)
            a = self.m.generate(text=f'({design}){self.DESIGN_TEXT}', cfg_value=2.0, inference_timesteps=10)
            import soundfile as sf
            path = os.path.join(HERE, 'voices', f'vx-{voice}.wav')
            os.makedirs(os.path.dirname(path), exist_ok=True)
            sf.write(path, a, SR)
            print('设计的声音', voice, round(len(a) / SR, 1), '秒，指纹', hashlib.md5(np.round(a, 3).tobytes()).hexdigest()[:10], flush=True)
            self.prompt = (path, self.DESIGN_TEXT)
        else:
            self.prompt = (os.path.join(HERE, 'voices', 'f.wav'), '希望你以后能够做的比我还好呦。')

    def __call__(self, text):
        return self.m.generate(text=text, prompt_wav_path=self.prompt[0], prompt_text=self.prompt[1],
                               cfg_value=2.0, inference_timesteps=10).astype(np.float32)


def trim(a, keep_head=0.03, keep_tail=0.08):
    """去掉模型输出前后多余的静音，句间停顿才能统一由我们控制"""
    if not len(a):
        return a
    thr = max(float(np.max(np.abs(a))) * 0.02, 1e-4)
    idx = np.nonzero(np.abs(a) > thr)[0]
    if not len(idx):
        return a[:0]
    lo = max(0, idx[0] - int(keep_head * SR))
    hi = min(len(a), idx[-1] + int(keep_tail * SR))
    return a[lo:hi]

def make_prompt(repo_dir, sft_dir, voice='m'):
    """用 CosyVoice-300M-SFT 内置的“中文男”/“中文女”合成一句话，当作 CosyVoice3 的提示音（voices/m.wav、voices/w.wav）"""
    sys.path.insert(0, repo_dir)
    sys.path.insert(0, os.path.join(repo_dir, 'third_party', 'Matcha-TTS'))
    from cosyvoice.cli.cosyvoice import AutoModel
    import soundfile as sf
    m = AutoModel(model_dir=sft_dir)
    text = Cosy.PROMPTS[voice][1]
    a = np.concatenate([j['tts_speech'].squeeze(0).numpy() for j in m.inference_sft(text, Cosy.SFT_SPK[voice], stream=False)])
    out = Cosy.PROMPTS[voice][0]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sf.write(out, a, m.sample_rate)
    print('提示音', voice, out, round(len(a) / m.sample_rate, 1), '秒')


# ---------------- 合成一个单位 ----------------
def sentences(t, limit=120):
    """太长的段落按句号切开再合成（模型对超长输入不稳定）"""
    out = []
    for s in re.split(r'(?<=[。！？；])', t):
        if not s.strip():
            continue
        if out and len(out[-1]) + len(s) <= limit:
            out[-1] += s
        else:
            out.append(s)
    return out


CHUNK = 0      # 逐句合成时，每次最多合成多少字（0＝一句一句；大一点语调更连贯）
PAUSE = None   # 逐句合成时的停顿（秒）：{'sent': 句与句, 'para': 段与段, 'head': 章节标题后}；None＝旧做法（学课录音不变）


def split_sent(t):
    """逐句切开（句号、问号、叹号、分号；破折号后面的补充也算一句的一部分），太短的并到前一句"""
    out = []
    for x in re.split(r'(?<=[。！？；])', t):
        x = x.strip()
        if not x:
            continue
        if out and len(x) < 6:
            out[-1] += x
        else:
            out.append(x)
    return out


def ranges(blocks, n):
    """按字数把段落平均分成 n 份（连续的几段一份），给并行合成用"""
    total = sum(len(b['say']) for b in blocks) or 1
    cuts, acc, k = [0], 0, 1
    for i, b in enumerate(blocks):
        acc += len(b['say'])
        while k < n and acc >= total * k / n and i + 1 > cuts[-1]:
            cuts.append(i + 1)
            k += 1
    while len(cuts) < n:
        cuts.append(len(blocks))
    cuts.append(len(blocks))
    return [(cuts[j], cuts[j + 1]) for j in range(n)]


def synth(blocks, tts, lo=0):
    """合成第 lo 段起的这些段落，返回（声音、每段开始的秒数）。停顿也算在里面"""
    chunks, starts, pos = [], [], 0
    for j, b in enumerate(blocks):
        i = lo + j
        if not b['say']:
            starts.append(-1)
            continue
        starts.append(round(pos / SR, 2))
        if PAUSE:
            ss = sentences(b['say'], CHUNK) if CHUNK else split_sent(b['say'])
            for k, s in enumerate(ss):
                a = trim(tts(s).astype(np.float32))
                chunks.append(a)
                pos += len(a)
                if k < len(ss) - 1:
                    z = np.zeros(int(PAUSE['sent'] * SR), np.float32)
                    chunks.append(z)
                    pos += len(z)
            gap = PAUSE['head'] if (i == 0 or b.get('head')) else PAUSE['para']
        else:
            for s in sentences(b['say']):
                a = tts(s).astype(np.float32)
                chunks.append(a)
                pos += len(a)
            gap = PAUSE_HEAD if (i == 0 or len(b['say']) < 24) else PAUSE_PARA
        z = np.zeros(int(gap * SR), np.float32)
        chunks.append(z)
        pos += len(z)
    audio = np.concatenate(chunks) if chunks else np.zeros(0, np.float32)
    return audio, starts


def finish(uid, src, audio, starts, fps, outdir, bitrate='32k'):
    """整条声音：统一音量，存成 mp3 和 json"""
    if not len(audio):
        audio = np.zeros(SR, np.float32)
    peak = float(np.max(np.abs(audio))) or 1.0
    audio = audio / peak * 0.89
    dur = len(audio) / SR
    os.makedirs(outdir, exist_ok=True)
    mp3 = os.path.join(outdir, uid + '.mp3')
    pcm = (np.clip(audio, -1, 1) * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-',
                    '-ar', '24000', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', bitrate, mp3], input=pcm, check=True)
    meta = {'d': round(dur, 2), 'h': fphash(fps), 'n': len(fps), 't': starts, 'src': src}
    with open(os.path.join(outdir, uid + '.json'), 'w') as f:
        json.dump(meta, f)
    return dur, mp3


def render(unit, tts, outdir, maxblocks=0, bitrate='32k', part=None):
    """合成一个朗读单位。part=(k, n)：只合成第 k 份（共 n 份），存成 <id>.partK.npy/.json，最后用 --merge 拼起来"""
    t0 = time.time()
    blocks = unit['blocks'][:maxblocks] if maxblocks else unit['blocks']
    lo, hi = ranges(blocks, part[1])[part[0]] if part else (0, len(blocks))
    audio, starts = synth(blocks[lo:hi], tts, lo)
    chars = sum(len(b['say']) for b in blocks[lo:hi])
    if part:
        os.makedirs(outdir, exist_ok=True)
        base = os.path.join(outdir, f"{unit['id']}.part{part[0]:02d}")
        np.save(base + '.npy', audio.astype(np.float16))
        with open(base + '.part', 'w') as f:
            json.dump({'k': part[0], 'n': part[1], 'sr': SR, 'lo': lo, 'hi': hi, 't': starts,
                       'fp': [b['fp'] for b in blocks[lo:hi]], 'src': unit.get('src', unit['id'])}, f, ensure_ascii=False)
        dur, took = len(audio) / SR, time.time() - t0
        print(f"{unit['id']} 第 {part[0] + 1}/{part[1]} 份（第 {lo + 1}—{hi} 段）：{chars} 字，{dur:.0f} 秒，用时 {took:.0f} 秒", flush=True)
        return {'id': f"{unit['id']}#{part[0]}", 'chars': chars, 'dur': round(dur, 1), 'took': round(took, 1)}
    dur, mp3 = finish(unit['id'], unit.get('src', unit['id']), audio, starts, [b['fp'] for b in blocks], outdir, bitrate)
    took = time.time() - t0
    print(f"{unit['id']}: {chars} 字，{dur:.0f} 秒音频，用时 {took:.0f} 秒（实时率 {took / max(dur, 1):.2f}），{os.path.getsize(mp3) // 1024} KB", flush=True)
    return {'id': unit['id'], 'chars': chars, 'dur': round(dur, 1), 'took': round(took, 1)}


def merge(outdir, bitrate='32k'):
    """把并行合成的几份（<id>.partK.npy/.part）按次序拼成一条，存 mp3 和 json，删掉分片"""
    import glob
    global SR
    groups = {}
    for f in sorted(glob.glob(os.path.join(outdir, '*.part'))):
        uid = re.sub(r'\.part\d+\.part$', '', os.path.basename(f))
        groups.setdefault(uid, []).append(f)
    for uid, fs in groups.items():
        ps = sorted(((json.load(open(f, encoding='utf-8')), f) for f in fs), key=lambda x: x[0]['k'])
        n = ps[0][0]['n']
        if [p['k'] for p, _ in ps] != list(range(n)):
            print(f'{uid}: 分片不全（{[p["k"] for p, _ in ps]} / {n}），先不拼', flush=True)
            continue
        SR = ps[0][0]['sr']
        chunks, starts, fps, pos = [], [], [], 0
        for p, f in ps:
            a = np.load(f[:-5] + '.npy').astype(np.float32)
            starts += [-1 if t < 0 else round(t + pos / SR, 2) for t in p['t']]
            fps += p['fp']
            chunks.append(a)
            pos += len(a)
        dur, mp3 = finish(uid, ps[0][0]['src'], np.concatenate(chunks), starts, fps, outdir, bitrate)
        for _, f in ps:
            os.remove(f)
            os.remove(f[:-5] + '.npy')
        print(f'{uid}: {n} 份拼好，{dur:.0f} 秒，{os.path.getsize(mp3) // 1024} KB', flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', required=True, choices=['kokoro', 'cosy3', 'cosy2', 'voxcpm'])
    ap.add_argument('--voice', default='f')
    ap.add_argument('--instruct', default='')
    ap.add_argument('--ids', default='')
    ap.add_argument('--kinds', default='')
    ap.add_argument('--lessons', default='')
    ap.add_argument('--maxblocks', type=int, default=0)
    ap.add_argument('--name', default='', help='试听用：输出文件改用这个名字')
    ap.add_argument('--out', required=True)
    ap.add_argument('--model-dir', default='')
    ap.add_argument('--repo-dir', default='')
    ap.add_argument('--bitrate', default='32k')
    ap.add_argument('--make-prompt', default='', help='CosyVoice-300M-SFT 模型目录（配合 --voice m 或 w）')
    ap.add_argument('--script', default='script.json', help='朗读稿：script.json（学课）或 script-health.json（健康栏目）')
    ap.add_argument('--speed', type=float, default=1.0, help='CosyVoice 语速，1＝正常')
    ap.add_argument('--pauses', default='', help='逐句合成并加停顿：句,段,标题（秒），例如 0.35,0.8,1.1')
    ap.add_argument('--part', default='', help='并行合成：k/n 只合成第 k 份（从 0 数），之后用 --merge 拼')
    ap.add_argument('--chunk', type=int, default=0, help='配合 --pauses：每次合成最多多少字（按句号合并），0＝一句一句')
    ap.add_argument('--design', default='', help='VoxCPM2：用文字描述设计声音')
    ap.add_argument('--merge', action='store_true', help='把 --out 里的分片拼成完整的声音')
    a = ap.parse_args()
    if a.merge:
        merge(a.out, a.bitrate)
        return
    if a.make_prompt:
        make_prompt(a.repo_dir, a.make_prompt, a.voice)
        return
    global PAUSE, CHUNK
    CHUNK = a.chunk
    if a.pauses:
        x = [float(v) for v in a.pauses.split(',')]
        PAUSE = {'sent': x[0], 'para': x[1], 'head': x[2]}
    units = json.load(open(os.path.join(HERE, a.script or 'script.json'), encoding='utf-8'))
    if a.ids:
        want = a.ids.split(',')
        units = [u for u in units if u['id'] in want]
    if a.kinds:
        units = [u for u in units if u['kind'] in a.kinds.split(',')]
    if a.lessons:
        ls = set(a.lessons.split(','))
        units = [u for u in units if re.match(r'(?:l|qa)(\d+)', u['id']) and re.match(r'(?:l|qa)(\d+)', u['id'])[1] in ls]
    if not units:
        raise SystemExit('没有要合成的内容')
    if a.engine == 'kokoro':
        tts = Kokoro(a.voice)
    elif a.engine == 'voxcpm':
        tts = Vox(a.voice, a.model_dir, a.design)
    else:
        tts = Cosy(a.voice, a.model_dir, a.repo_dir, v3=a.engine == 'cosy3', instruct=a.instruct, speed=a.speed or 1.0)
    stats = []
    for u in units:
        if a.name:
            u = dict(u, id=a.name, src=u['id'])
        part = tuple(int(x) for x in a.part.split('/')) if a.part else None
        stats.append(render(u, tts, a.out, a.maxblocks, a.bitrate, part))
    tag = a.part.replace('/', 'of') if a.part else 'all'
    with open(os.path.join(a.out, f'stats-{a.engine}-{a.voice}-{a.name or "x"}-{tag}-{int(time.time())}.json'), 'w') as f:
        json.dump(stats, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
