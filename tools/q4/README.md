# 生成《预言的恩赐》网页用的程序（备份）

网站上的 HTML 都由这里的程序生成。这是工作区的备份，方便以后换新会话继续修改。

## 主要文件
- `render.py`：总入口。`python3 render.py all` 重新生成全部课程页、合集页和在线版（约 10 分钟）；`python3 _combined_only.py` 只重建合集页和在线版。
- `data/lNN.py`：每一课的解读内容与学课原文。
- `app.js`、`base.css`、`extra.css`：网页的交互与样式。
- `welcome.py`：欢迎页；`intro.py`：导言；`gen_yw.py`：学课原文部分。
- `bible.py`：经文识别与弹窗数据；`build.py`：字体子集化；`online.py`：拆出在线版（`index.html` + `site/`）。
- `qa_data.py` 与 `qa/`：问题彩蛋的文章（网页与 PDF 共用），`qa/build.py` 生成 PDF。
- `tcb_sdk.js`：腾讯云开发网页工具包（@cloudbase/js-sdk 3.10.1 的 app+auth+database 打包），提问区使用。

## 需要另外准备的大文件（放在环境变量 `Q4_WORK` 指向的目录）
- `fonts/`：Noto Serif SC（serif.ttf、serif600.ttf、serif900.ttf）、Gentium（gentium*.ttf）、Noto Serif Hebrew（hebrew.ttf），PDF 另用 Noto Sans SC 与 LXGW WenKai。
- `bible/`：和合本、KJV、NKJV 的 JSON（thiagobodruk/bible），STEPBible TAHOT/TAGNT 原文数据（CC BY 4.0）。
- `zhlit/zhlit.json`：中文直译（本目录已备份一份，复制过去即可）。
