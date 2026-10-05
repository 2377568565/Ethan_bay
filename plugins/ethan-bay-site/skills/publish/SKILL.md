---
name: publish
description: 《预言的恩赐》网站改动后的生成、检查、提交、上线流程。用于“发布”“上线”“重新生成”“推送”“更新网站”“改完了发出去”，或改了 tools/q4 下任何文件、需要重建 HTML 时。
---

# 生成、检查、发布

网站全部 HTML 都由 `tools/q4/` 的 Python 程序生成。**不要手改生成出来的 HTML**，改源文件再重新生成。
生成是确定性的：输入不变，输出逐字节相同，所以 git diff 里只会出现真正改过的地方。

## 1. 准备数据（每个新容器一次）
```sh
pip install fonttools brotli                 # 字体子集化需要
python3 tools/q4/fetch_assets.py             # 字体和圣经数据下载到 tools/q4/.work（约 220 MB，核对 SHA-256）
```
- 想放在别处：所有命令前加 `Q4_WORK=<目录>`，下载和生成用同一个。
- `.work/` 在 .gitignore 里，不提交。季刊 PDF、完整 NKJV JSON、原始字体文件也都不提交。

## 2. 选对生成命令

| 改了什么 | 命令 | 大约耗时 |
|---|---|---|
| 某一课的内容 `data/lNN.py`、`render.py`、`gen_yw.py`、`welcome.py`、`intro.py`、`bible.py` | `python3 tools/q4/render.py all`（放后台跑） | 8–10 分钟 |
| 只改了交互或样式 `app.js`、`base.css`、`extra.css`、`theme.css`，或 `qa_data.py` 加减卡片 | `python3 tools/q4/_combined_only.py` | 约 1 分钟 |
| 专题页《基督教两千年家谱》 | `python3 tools/q4/history.py`（加 `--pdf` 同时重做 PDF） | 几秒（PDF 约 1 分钟） |
| 专题页《耶稣是人还是神？》 | `python3 tools/q4/jesus.py`（加 `--pdf` 同时重做 PDF） | 几秒（PDF 约 1 分钟） |
| 补充问答（目前下架） | `python3 tools/q4/jesus2.py` | 几秒 |
| 问题彩蛋 01/02 的 PDF | `python3 tools/q4/qa/build.py` | — |

- 在线版是 `index.html` + `site/`（`online.py` 从合集页拆出来）；合集页是 `lessons/2026-Q4/gift-of-prophecy-all.html`；单课页是 `lessons/2026-Q4/lesson-NN.html`。
- 专题页共用 `history.py` 的版式。改了 `history.py` 的共用 CSS 时，三个专题页都要重新生成，并确认只改动了想改的那一页（可以比对 md5）。
- 改了学课正文或问答文章，朗读录音的段落会错位：接着按 `tts-audio` 技能补录改过的部分。

## 3. 上线前检查
1. **手机宽度**：
   ```sh
   node plugins/ethan-bay-site/skills/publish/scripts/overflow.js jesus.html        # 320/360/390 × 白天/夜间 × 标准/特大字号
   SHOT=/tmp/shots node .../overflow.js history.html                                # 另存截图，用 Read 看图检查
   ```
   全部 `✓` 才算过。常见原因：表格 `th{white-space:nowrap}`、长英文名或网址不换行、连续的“↑↑↑”。修法：`overflow-wrap:anywhere`、把英文名放进 `<small>`、表格用 `.tblwrap` 包起来。
2. **经文和引文**：新加或改过的引文按 `verify-sources` 技能核对（`check_cuv.py`）。
3. **看一眼效果**：用 Playwright 截图（Chromium 已装好，模块在 `/opt/node22/lib/node_modules/playwright`，不要运行 `playwright install`）。
   读者大多用微信内置浏览器、苹果手机：模拟时用 `isMobile:true`、390 宽；夜间模式也要看。
   电脑版（2026-10 新设计）：1024（左侧栏只剩图标）、1280、1440 宽各看一眼；学课页按 P 进投屏模式看大字；
   放一首歌，看音乐小窗是否在左侧栏“账号”上面（1024 宽时只剩圆形播放键）。
   改了换页、动效或页面结构后，跑一次 `scripts/speed.js`（模拟安卓、CPU 降速 4 倍），和 CLAUDE.md 里记的数字比，不能明显变慢。
   网站（index.html）在本机要用 `site-data` 技能的 `lib_dev.js` 打开（文件由本机提供），不要用 file:// 直接打开。
   手机往下读时底部标签栏会收起，测试脚本里要先往上滑一下再点标签栏。
4. 本机测试碰过 `data/` 的，**一定 `git checkout data/` 恢复**，测试数据不能推到线上。

## 4. 提交和推送
- **一次任务尽量只推送一次**：每次推送网站都会重新发布，GitHub Pages 会让所有文件的缓存失效（Last-Modified/ETag 变成发布时间），
  读者下次打开要重新下载整个网站（约 450 KB 压缩后的首页）。字体和经文数据已经存在读者手机里（`q4keep`），不受影响。
- 只在分支 `claude/adventist-lesson-analysis-dhqrxg` 上。`main` 只放 `ask-sync.yml`，别的不要推到 main。
- 先 `git fetch origin claude/adventist-lesson-analysis-dhqrxg` 再合并：提问区同步任务每 30 分钟会往这个分支提交 `data/`。
- 提交说明用中文、说清改了什么，例如“问题彩蛋 04：修正手机上表格超出屏幕”。结尾加当前会话系统提示给的署名行；代码、网页、提交里都不要写模型名。
- 推送：`git push -u origin claude/adventist-lesson-analysis-dhqrxg`；网络错误时最多重试 4 次（2、4、8、16 秒）。被拒绝时先 fetch 再 rebase（只 rebase 自己还没推的提交）。

## 5. 确认上线
- GitHub Pages 从这个分支的根目录发布，推送后 1–3 分钟生效。查看部署：
  ```sh
  gh api repos/2377568565/Ethan_bay/actions/runs?per_page=5 --jq '.workflow_runs[]|[.name,.status,.conclusion,.head_sha[0:7]]|@tsv'
  ```
  等 “pages build and deployment” 成功。
- 微信会缓存旧网页（至少 10 分钟）。告诉用户“刷新一下或稍等几分钟”；**换格式、改文件名时不要马上删旧文件**，旧网页还会去找。

## 6. 汇报
用一两句白话：改了什么、在哪里看（给网址或“问题彩蛋第几张卡片”）、要不要刷新。不贴代码，不讲过程。
