---
name: tts-audio
description: 网站“🎧 听朗读”的预录人声（微信里也能听）：重新生成朗读稿、补录改过的段落、换声音。用于改了学课解读或问答文章之后，或用户提到“朗读”“读经”“声音”“录音”时。
---

# 朗读录音

微信内置浏览器没有手机自带朗读，自带的声音也很机械，所以改为预先录好人声 MP3。

## 现状
- 声音：**D —— Kokoro 女声 zf_001**（用户在五种试听里选的，`render.py` 的 `TTS_VOICE = 'kk-f'`）。
- 录音在 `audio/kk-f/`：每部分一个 MP3 和一个分段时间表 JSON；`audio/kk-f/index.json` 列出已录的部分。共约 14 小时、200 MB。
- 网页里录好的部分显示“🎧 听朗读”，逐段高亮、可拖进度、调语速，读完转到打卡；没录的部分在支持的浏览器里用手机自带语音。
- 试听页 `tts-try.html`（样本在 `audio/try/`）；`tools/q4/tts/check.py` 可以用语音识别比对读音。

## 内容改了以后补录
1. 先重新生成网页（`render.py all`）。
2. `python3 tools/q4/tts/speech.py`：从生成好的合集页取出每天原文、每段解读、问答文章，生成朗读稿 `tools/q4/tts/script.json`
   （经文出处读成“希伯来书一章一、二节”，去掉网址；分段和网页一致）。
3. 改 `tools/q4/tts/request.json` 并推送，`.github/workflows/tts.yml` 就会在 GitHub 上合成：
   ```json
   {"note": "这次为什么补录", "out": "audio/kk-f", "check": false,
    "jobs": [{"name": "", "engine": "kokoro", "voice": "zf_001", "ids": "l4-sun", "kinds": "", "lessons": ""}]}
   ```
   - `ids` 指定只补录哪些部分，多个用逗号。编号规则：`l4-sun` 第4课星期日的解读，`l4-yw-sun` 第4课星期日的原文，`l0-…` 导言；
     问答文章是 `kind: qa`。不确定时看 `script.json` 里的 `id`。全季重录时 `jobs` 改回每课一个任务（`kinds: "yw,jd,qa"`，`lessons` 0—13），约 40 分钟。
   - 在学课某天加了问题彩蛋入口，那天解读的段落会多一段，要补录那一天。
4. 等任务跑完，`git pull`，确认 `audio/kk-f/index.json` 更新、网页上那部分有“🎧 听朗读”。

## 健康栏目的朗读（2026-10-27 起）
- 声音：**C —— VoxCPM2 设计的女声**（用户在两轮试听里选的；第一轮 CosyVoice3 逐句合成被说“怪怪的”：提示音不是真人、一句一句合成语调断开、人为放慢）。
  提示音 `tools/q4/tts/voices/vx-dw.wav`（`gen.py --engine voxcpm --voice dw` 会直接用它，各台机器声音一致）。
- 朗读稿：`python3 tools/q4/tts/health_speech.py` → `tools/q4/tts/script-health.json`（单位 `h1`、`h2`、`h3`；`--demo` 只出试听用的 h2-demo）。
  新增健康文章时，把文件名和 `*_text` 模块加进 `health_speech.units_all()` 的 `mods`，生成器里 `col` 加 `audio=page_audio(IT['id'])`（见 `diabetes.py`）。
- 合成：`request.json` 例子
  ```json
  {"out": "audio/vx-w", "check": false, "jobs": [{"engine": "voxcpm", "voice": "dw", "ids": "h2", "script": "script-health.json",
    "pauses": "0.25,0.6,0.9", "chunk": "150", "parts": 6, "speed": "1", "design": "", "kinds": "", "lessons": "", "name": "", "maxblocks": "0", "instruct": ""}]}
  ```
  `parts`：一篇拆成几份并行（大约每 2,000—2,500 字一份；VoxCPM2 在 GitHub 的 CPU 上大约要音频长度的 10 倍时间）。全部任务最多 20 台同时跑，拼接在 publish 那一步（`gen.py --merge`）。
- 改 `health_speech.py` 的读法规则时，先确认已录好的几篇段落指纹没变（`page_audio(id)['h']` 和 `audio/vx-w/index.json` 里的 `h` 一样），否则它们的“听这一章”会失效。
- 只改了一篇，就只重录那一篇（`ids` 写那一篇）。改了文章没重录：还能听，但“听这一章”和上一章/下一章会隐藏（段落指纹对不上）。
- 本机测试播放器要用支持 Range 的服务器（`python3 -m http.server` 不支持，拖进度会跳回开头）；测试用的假录音别提交。
