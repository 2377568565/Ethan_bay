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

## 提问区（腾讯云开发 CloudBase，PostgreSQL）
- `ask_setup.sql`：数据表、权限规则、管理员名单。在云开发「SQL 型数据库」里整段运行一次；以后加管理员，运行文件末尾那行 `insert … q4_admins …`。
- `ask-bridge.html`：**连接页**。上传到云开发「静态网站托管」的根目录，地址是
  `https://wenda-d8gqka1o3902489eb-1492434734.tcloudbaseapp.com/ask-bridge.html`。
  免费体验版不能添加跨域（安全）域名，但静态托管的默认域名本来就在白名单里：网站把连接页嵌在提问区页面里，由它代为连数据库。
  连接页只接受 `2377568565.github.io` 的指令，只加载网站 `site/` 目录下的脚本；这个文件以后不需要改动或重传。
- `ask_bridge.js`：连接页里实际运行的脚本（随网站发布到 `site/`），负责匿名登录、执行查询，并把登录信息交给网站另存一份，防止手机清掉嵌入页的存储后身份改变。
- 以后如果升级套餐、把 `2377568565.github.io` 加进了「HTTP 网关 → 跨域设置」，也可以直接连：打开 `#ask` 时在网址加 `?askdirect` 测试。
