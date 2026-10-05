---
name: topic-pages
description: 做“问题彩蛋”的专题文章或独立专题网页（如《基督教两千年家谱》history.html、《耶稣是人还是神？》jesus.html），以及上架、下架、修订问题彩蛋。用于用户提出一个信仰或历史问题、要“放进问题彩蛋”“做成网页”“加图表”“下架”“重新上架”时。
---

# 问题彩蛋与专题网页

## 现有内容（`tools/q4/qa_data.py`）
| 编号 | 题目 | 形式 | 学课里的入口 |
|---|---|---|---|
| qa1 | 罪孽为何使人与上帝隔绝？（赛59:2） | 网页文章 + PDF（`qa/q1.html`） | 第1课星期三 |
| qa2 | 罪从哪里来？ | 网页文章 + PDF（`qa/q2.html`） | 第1课星期一 |
| qa3 | 基督教两千年家谱 | 独立网页 `history.html` | 第12课星期三 |
| qa4 | 耶稣是人还是神？ | 独立网页 `jesus.html` | 第4课星期日 |
| qa5 | 耶稣是人还是神？补充问答 | 独立网页 `jesus-qa.html`，**2026-10-04 下架修订中**（在 `DRAFTS`） | 不加（`nochip=True`） |

## 和用户合作的顺序（很重要）
1. 用户提出问题后，**先在对话里分析给他看**（Markdown，可以有表格）：结合圣经，用户要求时也结合怀著；逻辑清楚、例子恰当。
2. 他和妻子会读、会追问；追问也先在对话里回答。用户说“上面的不动”就保留原样，在后面补充。
3. 他明确说“放进网站/做成网页/发布”才动网站。**原有页面保持不变**，除非他点名要改。
4. 有不同说法的问题：客观列出各方说法和依据，让读者判断；用户要时再加“编者的评估”，并说明理由。
5. 他说“下架”就立刻下架，不做“正在修订”之类的占位页；源文件留在 GitHub 以后修改。

## 两种形式
**A. 短文（像 qa1、qa2）**：正文写在 `tools/q4/qa/qN.html`，网页和 PDF 共用；`qa_data.ITEMS` 加一条：
```python
dict(id='qa6', no=6, src='q6.html', q='题目', sub='副题', lesson=课号, day='sun'..'fri', dayname='星期日《当天标题》',
     teaser='卡片上的一句话', pdf='研经问答06-….pdf')
```
然后 `python3 tools/q4/qa/build.py`（PDF）和 `render.py all`（学课里多了入口，段落会变，记得补录朗读）。

**B. 独立专题网页（像 history.html、jesus.html）**：内容多、图表多时用。`qa_data.ITEMS` 里写 `url='xxx.html'`（不写 src/pdf）；
不想在学课那天再加入口就写 `nochip=True`，只改卡片时用 `_combined_only.py` 重建首页即可。

### 专题网页的程序结构（照 jesus.py 抄）
- `xxx.py`：入口。`import history as H`，用 `H.doc(title, desc, main, srcs, toc_html, cites)` 套版式；
  自己的样式写在 `EXTRA_CSS`，生成时临时接在 `H.CSS` 后面（见 `jesus.py` 的 `page()`），**不要改动共用 CSS 影响其他页面**。
- `xxx_text.py`：`PARTS`（部分标题）、`HERO`（开头的“先说结论”几步）、`CHAPTERS = [(部分, 'id', '标题', '''HTML''')]`、`FAQ`。
- `xxx_svg.py`：手写 SVG 图（用 `history_svg.text()` 写字；颜色用 CSS 变量，夜间模式自动变）。
- 正文里的记号：
  - `{{c:键}}` 资料出处（自动编号，点了显示出处，文末有“资料出处”列表）；
  - `{{v:约14:30}}` 整段和合本经文（自动取原文）；
  - `{{ref:章id}}` 跳到某一章；`{{fig:名}}` 插入图。
- 现成的版式：`.box`（带 `.lab` 标题的提示框）、`ol.steps`、`table.mini`（小表格，手机上会换行）、`.tblwrap` 包宽表格、
  `.cause/.ci`（编号卡片）、`.quote`、`.prof`（人物卡）、`figure.fig`、时间线 `.yr`。新表格先看 320 宽会不会超出。
- 资料：`history_sources.py` 的 `SRC['键'] = (说明, 网址或 None, [核对关键词])`；书籍（如怀著）网址写 None、说明里写清书名和英文原著页码；
  核对通过的网址写进 `history_checked.py` 的 `CHECKED['键'] = (网址, 'live' 或存档说明)`。页面只用核对过的网址，没核对的生成时会提示。
  怀著的键加进 `EGW_KEYS`（出处列表里归类为“怀爱伦著作”）。
- 风格：跟《基督教两千年家谱》一致——开头“先说结论”，分部分、分章，目录按钮随时跳，图表充分，语言通俗，篇幅不怕长但要精炼不丢信息。
- 写完：生成 → `verify-sources` 核对所有引文 → `publish` 的手机宽度检查 → 发布。README（`tools/q4/README.md`）里补一节说明。

## 下架 / 重新上架
- 下架：把那一条从 `ITEMS` 移到 `DRAFTS`（写上日期和原因），删掉根目录的那个 html，运行 `_combined_only.py`，提交推送。生成程序和正文留着。
- 重新上架：移回 `ITEMS`，运行它的生成程序（如 `jesus2.py`），再 `_combined_only.py`，检查后发布。

## 当前未完成：补充问答 jesus-qa.html
- 程序：`jesus2.py`、`jesus2_text.py`（16 问 + 结语）、`jesus2_svg.py`（三架天平、两条路线）。
- 下架原因：页面写的是“耶稣没有遗传犯罪的倾向”，用户觉得不妥。
- 2026-10-05 对话里提出的修订框架（用户说“暂时告一段落，不影响认识救恩的核心”，还没决定是否修订）：
  把“倾向”分成两样——A 肢体（身体）的软弱和需要（infirmities, heredity）：耶稣和我们一样都有；
  B 心里的偏向（propensity，“bent of mind/will”）：我们生来就有，耶稣没有（Baker 信，5BC 1128）。
  依据：罗7:22-23、罗8:3、约14:30、来4:15、DA 49、DA 123（“So it may be with us”）、GC 505 与 1SM 254（enmity）、5BC 1129（“will ever remain a mystery”）。
  用户原先倾向“propensity 指心里珍藏的倾向”的解释；已坦白说明 Baker 信里“born with inherent propensities”与这个解释不合。
- 背景：本会牧师（溪边树-李牧）指出讲耶稣的人性必须了解 1955—1957 年《教义问答》的历史，所以 jesus.html 第 5 章补了这段历史。
