# 生成《预言的恩赐》网页用的程序（备份）

网站上的 HTML 都由这里的程序生成。这是工作区的备份，方便以后换新会话继续修改。

## 主要文件
- `render.py`：总入口。`python3 render.py all` 重新生成全部课程页、合集页和在线版（约 10 分钟）；`python3 _combined_only.py` 只重建合集页和在线版。
- `data/lNN.py`：每一课的解读内容与学课原文。
- `app.js`、`base.css`、`extra.css`：网页的交互与样式。
- `welcome.py`：欢迎页；`intro.py`：导言；`gen_yw.py`：学课原文部分。
- `bible.py`：经文识别与弹窗数据；`build.py`：字体子集化；`online.py`：拆出在线版（`index.html` + `site/`）。
- `qa_data.py` 与 `qa/`：问题彩蛋的文章（网页与 PDF 共用），`qa/build.py` 生成 PDF。
- `ask_core.js`：提问区的共同规则（验签、防刷、谁能回复/删除），网页和 GitHub 同步任务共用；`render.py` 会把它放进网页。
- `ask_sync.js`：GitHub 同步任务运行的脚本。

## 需要另外准备的大文件（放在环境变量 `Q4_WORK` 指向的目录）
- `fonts/`：Noto Serif SC（serif.ttf、serif600.ttf、serif900.ttf）、Gentium（gentium*.ttf）、Noto Serif Hebrew（hebrew.ttf），PDF 另用 Noto Sans SC 与 LXGW WenKai。
- `bible/`：和合本、KJV、NKJV 的 JSON（thiagobodruk/bible），STEPBible TAHOT/TAGNT 原文数据（CC BY 4.0）。
- `zhlit/zhlit.json`：中文直译（本目录已备份一份，复制过去即可）。

## 提问区：问题存在 GitHub 仓库里
- 存档：`data/ask.json`（网页读取）和 `data/ask.csv`（可直接用 Excel 打开）。管理员名单：`data/ask-admins.json`（放“我是整理者”里看到的身份码）。
- 流程：网页把问题签名后投到免注册的公开中转站 ntfy.sh（频道名见 `render.py` 的 `ASK_TOPIC`），所有人的网页马上能看到；
  `.github/workflows/ask-sync.yml` 每 30 分钟把中转站里的新消息验签、检查后写进上面的存档（中转站只保留 12 小时）。
- 身份：每台设备第一次提问时生成一对密钥（只存在这台设备上），身份码 = 公钥哈希；没有这台设备的签名，谁也删不了、冒充不了它发的内容。
- 定时任务只在默认分支（main）上生效，所以 main 上也放了一份 `ask-sync.yml`；它会检出网站所在的分支再同步。
