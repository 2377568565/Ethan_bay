# 生成《预言的恩赐》网页用的程序

网站上的 HTML 都由这里的程序生成。换电脑、换会话都可以从这里一键重建。

## 一键重建
```sh
pip install fonttools brotli          # 需要 Python 3.8+
python3 tools/q4/fetch_assets.py      # 下载字体和圣经数据到 tools/q4/.work（约 220 MB，只需一次）
python3 tools/q4/render.py all        # 重新生成全部课程页、合集页和在线版（约 8 分钟）
```
- 下载来源都是公开的（Google Fonts、Noto、霞鹜文楷、thiagobodruk/bible、STEPBible），每个文件都核对 SHA-256，和建站时用的版本一致。
- 想把大文件放别处：设置环境变量 `Q4_WORK=目录`，下载和生成都用同一个。
- 生成结果是固定的：同样的输入两次生成的文件完全相同，所以 git 里只会出现真正改过的地方。
- 只改了网页的交互或样式时，可以用 `python3 tools/q4/_combined_only.py`，只重建合集页和在线版，快很多。
- 学课原文已从季刊 PDF 提取成 `pdf_blocks.json`，平时不需要 PDF。要从 PDF 重新提取：`Q4_PDF=季刊.pdf python3 tools/q4/extract.py --cache`。

## 主要文件
- `render.py`：总入口。
- `data/lNN.py`：每一课的解读内容与学课原文。
- `app.js`、`base.css`、`extra.css`：网页的交互与样式。
- `welcome.py`：欢迎页；`intro.py`：导言；`gen_yw.py` 与 `extract.py`：学课原文部分。
- `bible.py`：经文识别与弹窗数据；`build.py`：字体子集化；`online.py`：拆出在线版（`index.html` + `site/`）。
- `qa_data.py` 与 `qa/`：问题彩蛋的文章（网页与 PDF 共用），`qa/build.py` 生成 PDF。
- `zhlit/zhlit.json`：中文直译。
- `ask_core.js`：线上互动的共同规则（验签、防刷、谁能回复/删除/置顶），网页和 GitHub 同步任务共用；`render.py` 会把它放进网页。
- `ask_sync.js`：GitHub 同步任务运行的脚本。

## 线上互动：数据存在 GitHub 仓库里
提问区、“我也想知道”、读经打卡、讨论区都用同一套机制。
- 存档（在仓库的 `data/` 目录，都可以用 Excel 打开 CSV）：
  - `ask.json`：网页读取的完整存档。
  - `ask.csv`：提问和回复（含“想知道人数”“置顶”）。
  - `discuss.csv`：讨论区里大家分享的回答。
  - `checkins.csv`：每天读完打卡的人数（不记名字）。
  - `ask-admins.json`：管理员名单（放“我是整理者”里看到的身份码）。
- 流程：网页把消息签名后投到免注册的公开中转站 ntfy.sh（频道名见 `render.py` 的 `ASK_TOPIC`），所有人的网页马上能看到；
  `.github/workflows/ask-sync.yml` 每 30 分钟把中转站里的新消息验签、检查后写进上面的存档（中转站只保留 12 小时）。
- 身份：每台设备第一次发言时生成一对密钥（只存在这台设备上），身份码 = 公钥哈希；没有这台设备的签名，谁也删不了、冒充不了它发的内容。
- 管理员能做的：回答问题、删除任何内容、置顶问题、把问题关联到某篇问答文章。
- 定时任务只在默认分支（main）上生效，所以 main 上也放了一份 `ask-sync.yml`；它会检出网站所在的分支再同步。

## 网页里的阅读工具（都只存在读者自己的浏览器里）
- 字号（5 档）、夜间模式（跟随系统 / 浅色 / 深色）。
- 朗读（浏览器自带的语音，可调语速；经文“3:16”读成“3章16节”）。
- 全文搜索（全季 13 课解读、学课原文、问题彩蛋文章；多个词用空格分开）。
- 继续阅读：记住上次读到的段落，下次打开时提示跳回去。
- 做成图片：经文、问答文章、已回答的问题都能生成带二维码的分享图。
- 新消息提醒：有新的回答或新的问答文章时，按钮上出现小红点。
