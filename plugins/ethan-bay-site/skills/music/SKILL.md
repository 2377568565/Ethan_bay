---
name: music
description: 网站“♪ 音乐”栏目的加歌、建文件夹、改曲名和中文名、音质与格式。用于用户说“上传了新的 release”“加歌”“新建文件夹”“歌名”“音质”“音量”“播放卡顿”时。
---

# 音乐栏目

## 现状（2026-10-05）
- 曲目文件在仓库 `music/`，清单 `music/list.json`（网页每次进入音乐页都读最新的清单，加歌不用重新生成网页）。
- 三个文件夹（`list.json` 的 `folders`，按顺序显示）：
  | id | 名字 | 歌数 | 说明 |
  |---|---|---|---|
  | worship | 英文敬拜与圣诗 | 82 | 用户本机 MUSIC 文件夹里的歌，OGG Opus 约 70 kbps |
  | new-2026-10 | 2026年10月 新收录 | 1 | 《My Redeemer Is Faithful and True》，用户上传的 Opus 138 kbps 原样 |
  | hymns-of-grace | 小小恩典圣诗 · Hymns Of Grace | 23 | release 标签 `Little_Hymns_Of_Grace`，约 138 kbps；底部注明版权来自 YouTube https://www.youtube.com/@hymnsofgrace（`credit`、`curl`） |
- 每首：`id`、`title`（英文曲名）、`sub`（中文名）、`intro`（一小段介绍，可选）、`file`、`dur`（秒）、`folder`、`type`、可选 `alt`（备用文件）。
- 中文名和介绍在 `music/names.json`（键是整理后的英文曲名，不分大小写），收歌时自动套用；可以直接改。
- **待办**：《Facing A Task Unfinished》在 release 里没传完整（下载 404），要用户重新上传；它的中文名和介绍已经写在 names.json。

## 用户定下的规矩
- 格式用 **OGG（Opus）**，用户试听后认定比 AAC 好一档；AAC 已删除。Hymns of Grace 保持约 138 kbps。
- 音量：统一音量用 `loudnorm=I=-16:TP=-1.5:LRA=11`（`music_import.py` 的 `LOUD`）。曾经调到 -11 LUFS 加限幅，用户觉得“忽高忽低”，已改回，**不要再调大**。
  手机上声音偏小是手机音量的问题，可以这样解释。
- 换格式或改文件名时**不要马上删旧文件**：微信会缓存旧网页（至少 10 分钟），旧网页还会去找旧文件，删了就“没有加载成功”。用户确认新网页没问题后再删。
- 版权：放上来的录音所有人都能听和下载，只用有权分享的录音；来源要写在文件夹底部。
- 较旧的苹果手机放不了 OGG：网页用 `canPlayType` 判断并提示；需要时在 `alt` 放一份 AAC。

## 加歌流程（文件很大也行）
git 单个文件不能超过 100 MB、网页上传不能超过 25 MB、Pages 网站不能超过 1 GB，所以原始文件放在 GitHub Releases，不进仓库：
1. 用户在仓库 Releases 新建一个发布，把歌拖进**说明框**（每首变成一个链接，保留中文文件名，单个 ≤25 MB）；
   附件区（单个 ≤2 GB）会删掉文件名里的中文，中文歌名要先压成 ZIP 再传（程序会解开，认得 GBK/Big5 文件名）。
2. 改 `music/request.json` 并推送：
   ```json
   {"release": "发布的标签或名称", "rev": 原来的数字+1, "codec": "opus", "kbps": 138, "folder": "文件夹名字", "reencode": false}
   ```
   - `folder` 写新名字就新建文件夹（排在最后）；不写就放进“某年某月 新收录”。
   - `codec`：opus（现在用的）/ heaac / aac / mp3 / keep（原样不压）。`reencode: true` 把已收的歌按新设置重压；`relevel` 配合它改文件名标记。
3. `.github/workflows/music.yml` 自动运行 `tools/q4/music_import.py`：下载还没收过的 → 统一音量 → 压缩 → 存成 `music/m<编号>.ogg` → 追加到 `list.json`。
   收过哪些记在 `music/sources.json`，同一个文件夹里同名同长度的不重复收。
4. 等任务跑完（`gh api repos/2377568565/Ethan_bay/actions/runs?per_page=5`），`git pull`，检查 `list.json` 新增的歌、曲名是否干净（去掉“with lyrics”“Official Video”、序号等），补 `names.json` 的中文名和介绍，推送。
- 本机也能收：`python3 tools/q4/music_import.py --dir 放歌的文件夹`（要 ffmpeg；容器里可用 pip 包 imageio-ffmpeg 自带的 ffmpeg）。

## 播放体验（已实现，改代码时别弄坏）
- 文件夹框 → 点进去是歌；`#music`、`#music-f-<文件夹>`、`#music-<歌>` 三种网址；搜索跨文件夹，中英文都能搜。
- 播放、进度条、下载（微信里提示“在浏览器打开”）、分享；全部播放、随机、循环。
- 左下角小窗：曲名和中文名、上一首/暂停/下一首/关闭，点曲名回到这首；锁屏和耳机按键可用；往下读时半透明。
- 网慢时先缓冲，但**最多等 7 秒就先播起来**；选中的这首优先下载，别的下载马上停；播完前预先下载下一首。
- 听过的歌缓存在手机里（Cache Storage，最多 40 首）。开始听朗读时音乐暂停，反之亦然。
- 格式对比试听页：`music-try.html`（文件在 `audio/music-try/`）。
