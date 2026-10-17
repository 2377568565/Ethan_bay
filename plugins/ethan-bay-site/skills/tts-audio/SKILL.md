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
