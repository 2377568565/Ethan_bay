---
name: verify-sources
description: 核对经文和怀爱伦著作等引文是否逐字准确、出处是否可靠。用于写或改任何带引文的内容之前和之后，用户说“核实引用”“确保准确”“查原文”，或需要读取容器里打不开的网站（egwwritings.org 等）时。
---

# 引文核对

用户最看重的一条：**引用一定要准确**。宁可少引，不可错引；查不到原文的话不用，或者明说“未能核对”。

## 1. 圣经
- 中文一律用和合本（上帝版）原文逐字。工具：`tools/q4/bible.py`
  ```python
  import bible                                   # 在 tools/q4 里运行，先设好 Q4_WORK
  b = bible.NAME2IDX['约']                        # 书卷用中文简称或全名
  bible.cuv(b, 14, 30)                            # 和合本
  bible.en('K', b, 14, 30); bible.en('N', b, 14, 30)   # KJV / NKJV
  bible.original({(b, 14, 30)})                   # 原文逐字：(原文, 音译, 英文义, Strong 编号, 词条, 释义)
  ```
  圣经数据来自 thiagobodruk/bible（和合本、KJV、NKJV）和 STEPBible TAHOT/TAGNT（希伯来文、希腊文，CC BY 4.0）。
  和合本数据里约 63 章有并节，已经用 `bible_fix.json` 修正。
- 写完后批量核对：
  ```sh
  Q4_WORK=<目录> python3 plugins/ethan-bay-site/skills/verify-sources/scripts/check_cuv.py jesus.html tools/q4/jesus_text.py
  ```
  它找出所有 `“……”（书卷 章:节）` 的引用，和和合本逐字比对（忽略标点；“……”当省略；祂/他、像/象 视为相同）。
  列出的“不符”逐条处理：改成和合本原文，或把出处改对（例如“从圣灵来的”是太1:20，不是路1:35）。
  学课原文部分是季刊自己的文字，不要改。
  用户 2026-10-05 说：解读里的意引、异体字（借/藉等）**只要意思没有偏离就可以**；专题页里加引号、标出处的经文仍按原文逐字。
- NKJV 有版权：网站上 NKJV 最多 1000 节（`bible.nkjv_choice()` 按使用频率选），其余用 KJV，并标注版本。不要提交完整的 NKJV 数据。
- 讲原文时：希伯来文/希腊文词用 `original()` 的数据（Strong 编号、词义），不要凭记忆写；英文对照 KJV 和 NKJV。

## 2. 怀爱伦著作
- 按英文原著页码引用（如 DA 49、5BC 1128），中文写“编者译”。期刊按原刊日期（如 RH Dec 15, 1896）。
- **每一句英文都要找到可靠来源核对过**，可用的渠道：
  1. WebSearch 搜英文原句（加引号），看搜索结果里出现的原文和页码；
  2. CCEL（ccel.org/ccel/white/…）有《历代愿望》《拾级就主》等全文；
  3. 复临教会档案馆原刊扫描 PDF：`documents.adventistarchives.org`（《评论与通讯》RH、《时兆》ST、《青年导报》YI、《事工》Ministry）；
  4. 可靠的原文汇编：Fortin 编《怀爱伦论基督的人性》、1956 年《事工》杂志汇编等，出处说明里写明“据……核对”。
- **egwwritings.org、whiteestate.org、gutenberg 在容器里打不开（代理 403），不要设法绕过代理去抓。**
  需要读这类网站或大 PDF 时，用下面的“临时任务”在 GitHub 的机器上读。
- 已核对过的怀著原句，可以在 `tools/q4/history_sources.py`（键如 `da49`、`bc5`、`rh1896`）和 jesus 系列页面里找到，复用时照抄。

## 3. 其他资料（历史、教会文件）
- 出处登记在 `history_sources.py`：`SRC['键'] = (中文说明, 网址或 None, [核对关键词])`。
- `python3 tools/q4/history_sources.py --check --facts`（可加 `--only=键1,键2`）逐个打开网址，打印和关键词对应的原句，人工核对。
- 核对通过的网址写进 `history_checked.py`：`CHECKED['键'] = (网址, 'live')`；用网页时光机存档核对的写存档说明。
- 分类（出处列表里显示）：原始文献、怀爱伦著作、百科全书、学术研究、官方网站、书籍——见 `history.py` 的 `src_kind()`。

## 4. 临时任务：在 GitHub 上读打不开的网页
容器里打不开、但 GitHub Actions 能打开的网页或 PDF：
1. 复制 `templates/tmp-src.yml` 到 `.github/workflows/tmp-src.yml`，`templates/tmp_src.py` 到 `tools/q4/tmp_src.py`，在 `JOBS` 里写（键, 网址, 关键词）。
2. 提交推送（提交说明写“临时：核对……（查完会删掉）”）。任务把每份资料的关键句存成一条“检查结果”（check run）。
3. 读结果：
   ```sh
   gh api "repos/2377568565/Ethan_bay/commits/<提交SHA>/check-runs?per_page=100&filter=all" --jq '.check_runs[]|[.id,.name]|@tsv'
   gh api repos/2377568565/Ethan_bay/check-runs/<id> --jq .output.text
   ```
   （`gh api .../jobs/<id>/logs` 读日志会被拒绝，所以用 check run 传文字。）
4. 查完**马上清理**：删掉这两个文件并提交；有版权的全文，用 PATCH 把那些 check run 的 `output.text` 改成空；
   `gh api -X DELETE repos/2377568565/Ethan_bay/actions/runs/<run_id>/logs` 删掉日志。
- 这样做只是让 GitHub 的机器替我们打开公开网页，不是绕过限制；如果网站本身拒绝（403/429），换别的来源，不要硬闯。

## 5. 写进网页时
- 每条引文后标出处 `{{c:键}}`（专题页）或括号出处（学课页）。
- 中文译文贴近原文，不加油添醋；需要解释的另起一句，标“编者的理解”。
- 有争议的说法写清是谁说的、在哪里说的，不把一派的解释写成“怀爱伦说”。
