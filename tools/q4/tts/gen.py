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
    }

    def __init__(self, voice, model_dir, repo_dir, v3=True, instruct=''):
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
        if voice == 'm' and not os.path.exists(wav):
            raise SystemExit('缺少男声提示音 voices/m.wav：先用 --make-male-prompt 生成')
        self.prompt_wav = wav
        self.prompt_text = ('You are a helpful assistant.<|endofprompt|>' + text) if v3 else text
        self.instruct = instruct
        self.v3 = v3

    def __call__(self, text):
        if self.instruct:
            it = self.m.inference_instruct2(text, 'You are a helpful assistant. ' + self.instruct + '<|endofprompt|>', self.prompt_wav, stream=False)
        else:
            it = self.m.inference_zero_shot(text, self.prompt_text, self.prompt_wav, stream=False)
        parts = [j['tts_speech'].squeeze(0).cpu().numpy() for j in it]
        return np.concatenate(parts) if parts else np.zeros(0, np.float32)


def make_male_prompt(repo_dir, sft_dir):
    """用 CosyVoice-300M-SFT 内置的“中文男”合成一句话，当作 CosyVoice3 的男声提示音"""
    sys.path.insert(0, repo_dir)
    sys.path.insert(0, os.path.join(repo_dir, 'third_party', 'Matcha-TTS'))
    from cosyvoice.cli.cosyvoice import AutoModel
    import soundfile as sf
    m = AutoModel(model_dir=sft_dir)
    text = Cosy.PROMPTS['m'][1]
    a = np.concatenate([j['tts_speech'].squeeze(0).numpy() for j in m.inference_sft(text, '中文男', stream=False)])
    out = Cosy.PROMPTS['m'][0]
    os.makedirs(os.path.dirname(out), exist_ok=True)
    sf.write(out, a, m.sample_rate)
    print('男声提示音', out, round(len(a) / m.sample_rate, 1), '秒')


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


def render(unit, tts, outdir, maxblocks=0, bitrate='32k'):
    t0 = time.time()
    chunks, starts, fps, pos = [], [], [], 0
    blocks = unit['blocks'][:maxblocks] if maxblocks else unit['blocks']
    for i, b in enumerate(blocks):
        fps.append(b['fp'])
        if not b['say']:
            starts.append(-1)
            continue
        starts.append(round(pos / SR, 2))
        for s in sentences(b['say']):
            a = tts(s).astype(np.float32)
            chunks.append(a)
            pos += len(a)
        gap = PAUSE_HEAD if (i == 0 or len(b['say']) < 24) else PAUSE_PARA
        z = np.zeros(int(gap * SR), np.float32)
        chunks.append(z)
        pos += len(z)
    audio = np.concatenate(chunks) if chunks else np.zeros(SR, np.float32)
    peak = float(np.max(np.abs(audio))) or 1.0
    audio = audio / peak * 0.89
    dur = len(audio) / SR
    os.makedirs(outdir, exist_ok=True)
    mp3 = os.path.join(outdir, unit['id'] + '.mp3')
    pcm = (np.clip(audio, -1, 1) * 32767).astype('<i2').tobytes()
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 's16le', '-ar', str(SR), '-ac', '1', '-i', '-',
                    '-ar', '24000', '-ac', '1', '-c:a', 'libmp3lame', '-b:a', bitrate, mp3], input=pcm, check=True)
    meta = {'d': round(dur, 2), 'h': fphash(fps), 'n': len(blocks), 't': starts, 'src': unit.get('src', unit['id'])}
    with open(os.path.join(outdir, unit['id'] + '.json'), 'w') as f:
        json.dump(meta, f)
    took = time.time() - t0
    chars = sum(len(b['say']) for b in blocks)
    print(f"{unit['id']}: {chars} 字，{dur:.0f} 秒音频，用时 {took:.0f} 秒（实时率 {took / max(dur, 1):.2f}），{os.path.getsize(mp3) // 1024} KB", flush=True)
    return {'id': unit['id'], 'chars': chars, 'dur': round(dur, 1), 'took': round(took, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--engine', required=True, choices=['kokoro', 'cosy3', 'cosy2'])
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
    ap.add_argument('--make-male-prompt', default='', help='CosyVoice-300M-SFT 模型目录')
    a = ap.parse_args()
    if a.make_male_prompt:
        make_male_prompt(a.repo_dir, a.make_male_prompt)
        return
    units = json.load(open(os.path.join(HERE, 'script.json'), encoding='utf-8'))
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
    else:
        tts = Cosy(a.voice, a.model_dir, a.repo_dir, v3=a.engine == 'cosy3', instruct=a.instruct)
    stats = []
    for u in units:
        if a.name:
            u = dict(u, id=a.name, src=u['id'])
        stats.append(render(u, tts, a.out, a.maxblocks, a.bitrate))
    with open(os.path.join(a.out, f'stats-{a.engine}-{a.voice}-{a.name or "x"}-{int(time.time())}.json'), 'w') as f:
        json.dump(stats, f, ensure_ascii=False)


if __name__ == '__main__':
    main()
