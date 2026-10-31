#!/usr/bin/env python3
"""试听样本的客观检查：用语音识别（Whisper）把合成的声音转回文字，和朗读稿比对，算出错字率。
错字率越低，说明读音越准（多音字、经文出处、数字等）。用法：python3 check.py 目录"""
import glob, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from speech import num  # noqa: E402


def norm(t):
    try:
        import opencc
        t = opencc.OpenCC('t2s').convert(t)
    except Exception:
        pass
    t = re.sub(r'\d+', lambda m: num(m[0]), t)
    return re.sub(r'[^一-鿿A-Za-z]', '', t)


def lev(a, b):
    prev = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        cur = [i]
        for j, y in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (x != y)))
        prev = cur
    return prev[-1]


def main(d):
    from faster_whisper import WhisperModel
    model = WhisperModel('small', device='cpu', compute_type='int8')
    units = {u['id']: u for u in json.load(open(os.path.join(HERE, 'script.json'), encoding='utf-8'))}
    rep = {}
    for mp3 in sorted(glob.glob(os.path.join(d, '*.mp3'))):
        name = os.path.basename(mp3)[:-4]
        meta = json.load(open(mp3[:-4] + '.json'))
        u = units[meta['src']]
        ref = norm(''.join(b['say'] for b in u['blocks'][:meta['n']]))
        segs, _ = model.transcribe(mp3, language='zh', beam_size=5, initial_prompt='以下是普通话朗读的安息日学课，含圣经经文出处。')
        hyp_raw = ''.join(s.text for s in segs)
        hyp = norm(hyp_raw)
        cer = lev(ref, hyp) / max(1, len(ref))
        rep[name] = {'cer': round(cer * 100, 1), 'asr': hyp_raw}
        print(f'{name}: 错字率 {cer * 100:.1f}%', flush=True)
    json.dump(rep, open(os.path.join(d, 'asr.json'), 'w'), ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main(sys.argv[1])
