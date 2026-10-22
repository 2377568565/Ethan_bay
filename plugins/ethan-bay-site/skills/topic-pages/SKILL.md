---
name: topic-pages
description: 做“问题彩蛋”的专题文章或独立专题网页（如《基督教两千年家谱》history.html、《耶稣是人还是神？》jesus.html），以及上架、下架、修订问题彩蛋。用于用户提出一个信仰或历史问题、要“放进问题彩蛋”“做成网页”“加图表”“下架”“重新上架”时。
---

# 问题彩蛋与专题网页

- 新专题可以用 `python3 tools/q4/newtopic.py spec.json`（以 listen.py 为模板生成 X.py）；spec 里写 slug、no、id、title、pdf、figs、eyebrow、h1s、hsub、intro、srcs、desc、refdemo。

## 现有内容（`tools/q4/qa_data.py`）
| 编号 | 题目 | 形式 | 学课里的入口 |
|---|---|---|---|
| qa1 | 罪孽为何使人与上帝隔绝？（赛59:2） | 网页文章 + PDF（`qa/q1.html`） | 第1课星期三 |
| qa2 | 罪从哪里来？ | 网页文章 + PDF（`qa/q2.html`） | 第1课星期一 |
| qa3 | 基督教两千年家谱 | 独立网页 `history.html` | 第12课星期三 |
| qa4 | 耶稣具有完全的人性和完全的神性吗？ | 独立网页 `jesus.html` | 第4课星期日 |
| qa5（编号32） | 耶稣是人还是神？补充问答 | 独立网页 `jesus-qa.html`，**2026-10-04 下架修订中**（在 `DRAFTS`） | 不加（`nochip=True`） |
| qa6（编号05） | 根据圣经，人死了去哪里？ | 独立网页 `death.html`（`death.py`、`death_text.py`、`death_svg.py`），2026-10-11 上架 | 不加（`nochip=True`；对应第9课星期一） |
| qa7（编号06） | 谁改了安息日？ | 独立网页 `sabbath.html`（`sabbath.py`、`sabbath_text.py`、`sabbath_svg.py`），2026-10-12 上架 | 不加（`nochip=True`） |
| qa8（编号07） | 安息日，到底能做什么？ | 独立网页 `keep.html`（`keep.py`、`keep_text.py`、`keep_svg.py`），2026-10-12 上架 | 不加（`nochip=True`） |
| qa9（编号08） | 我还会犯罪，能得救吗？ | 独立网页 `rom7.html`（`rom7.py`、`rom7_text.py`、`rom7_svg.py`），2026-10-12 上架 | 不加（`nochip=True`） |
| qa10（编号09） | 旧约的上帝和新约的上帝，是同一位吗？ | 独立网页 `god.html`（`god.py`、`god_text.py`、`god_svg.py`），2026-10-12 上架 | 不加（`nochip=True`） |
| qa11（编号10） | 上帝早就定好谁得救吗？ | 独立网页 `elect.html`（`elect.py`、`elect_text.py`、`elect_svg.py`），2026-10-12 上架 | 不加（`nochip=True`） |
| qa12（编号11） | “我必快来”，为什么两千年了还没来？ | 独立网页 `soon.html`（`soon.py`、`soon_text.py`、`soon_svg.py`），2026-10-12 上架 | 不加（`nochip=True`） |
| qa13（编号12） | 要“完全”才能见主吗？ | 独立网页 `perfect.html`（`perfect.py`、`perfect_text.py`、`perfect_svg.py`），2026-10-12 上架 | 不加（`nochip=True`） |
| qa14（编号13） | 信了主，还会失去救恩吗？ | 独立网页 `lose.html`（`lose.py`、`lose_text.py`、`lose_svg.py`），2026-10-12 上架 | 不加（`nochip=True`） |
| qa15（编号14） | 喜乐的心，为什么是良药？ | 独立网页 `joy.html`（`joy.py`、`joy_text.py`、`joy_svg.py`），2026-10-12 上架 | 不加（`nochip=True`） |
| qa16（编号15） | 家人总在念叨，我为什么越听越烦？ | 独立网页 `listen.html`（`listen.py`、`listen_text.py`、`listen_svg.py`），2026-10-12 上架 | 不加（`nochip=True`） |
| qa17（编号16） | 一个好上帝，为什么允许苦难？ | 独立网页 `pain.html`（`pain.py`、`pain_text.py`、`pain_svg.py`），2026-10-13 上架 | 不加（`nochip=True`） |
| qa18（编号17） | 人活着，到底为了什么？ | 独立网页 `life.html`（`life.py`…），2026-10-13 上架 | 不加（`nochip=True`） |
| qa19（编号18） | 圣经可信吗？会不会是后人编的？ | 独立网页 `trust.html`（`trust.py`…），2026-10-13 上架 | 不加（`nochip=True`） |
| qa20（编号19） | 世界是演化来的，还是上帝造的？ | 独立网页 `origin.html`（`origin.py`…），2026-10-13 上架 | 不加（`nochip=True`） |
| qa21（编号20） | 钱是万恶之根吗？ | 独立网页 `money.html`（`money.py`…），2026-10-13 上架 | 不加（`nochip=True`） |
| qa22（编号21） | 抽烟、喝酒、吃什么，和信仰有关系吗？ | 独立网页 `health.html`（`health.py`…），2026-10-13 上架 | 不加（`nochip=True`） |
| qa23（编号22） | 算命、风水、星座、看日子，到底灵不灵？ | 独立网页 `fortune.html`（`fortune.py`…），2026-10-13 上架 | 不加（`nochip=True`） |
| qa24（编号23） | 清明祭祖，基督徒算不算不孝？ | 独立网页 `ancestor.html`（`ancestor.py`…），2026-10-13 上架 | 不加（`nochip=True`） |
| qa25（编号24） | 婚姻是爱情的坟墓吗？ | 独立网页 `marriage.html`（`marriage.py`…），2026-10-13 上架 | 不加（`nochip=True`） |
| qa26（编号25） | 打骂孩子，还是由着孩子？ | 独立网页 `raise.html`（`raise.py`…），2026-10-13 上架 | 不加（`nochip=True`） |
| qa27（编号26） | 666 和兽的印记，到底是什么？ | 独立网页 `beast.html`（`beast.py`、`beast_text.py`、`beast_svg.py`），2026-10-13 上架 | 不加（`nochip=True`） |
| qa28（编号27） | 1844 年，天上发生了什么？ | 独立网页 `judgment.html`（`judgment.py`、`judgment_text.py`、`judgment_svg.py`），2026-10-13 上架 | 不加（`nochip=True`） |
| qa29（编号28） | 旧约律法，哪些还要守？ | 独立网页 `law.html`（`law.py`、`law_text.py`、`law_svg.py`），2026-10-13 上架 | 不加（`nochip=True`） |
| qa30（编号29） | 祷告为什么常常没有应验？ | 独立网页 `prayer.html`（`prayer.py`、`prayer_text.py`、`prayer_svg.py`），2026-10-13 上架 | 不加（`nochip=True`） |
| qa31（编号30） | 犹大是注定要卖主的吗？ | 独立网页 `judas.html`（`judas.py`、`judas_text.py`、`judas_svg.py`），2026-10-13 上架 | 不加（`nochip=True`） |
| qa32（编号31） | “我原谅你”，为什么要用血来写？ | 独立网页 `blood.html`（`blood.py`、`blood_text.py`、`blood_svg.py`），2026-10-23 上架 | 不加（`nochip=True`） |

## 和用户合作的顺序（很重要）
1. 用户提出问题后，**先在对话里分析给他看**（Markdown，可以有表格）：结合圣经，用户要求时也结合怀著；逻辑清楚、例子恰当。
2. 他和妻子会读、会追问；追问也先在对话里回答。用户说“上面的不动”就保留原样，在后面补充。
3. 他明确说“放进网站/做成网页/发布”才动网站。**原有页面保持不变**，除非他点名要改。
4. 有不同说法的问题：客观列出各方说法和依据，让读者判断；用户要时再加“编者的评估”，并说明理由。
5. 他说“下架”就立刻下架，不做“正在修订”之类的占位页；源文件留在 GitHub 以后修改。

## 每个问题彩蛋都必须有：分享 + 下载 PDF（用户 2026-10-05 定下）
- 短文（qa1、qa2）：文末“分享这篇”和 PDF 下载链接（`render.py` 的 `qa_pages()`）。
- 独立专题网页：用 `tools/q4/topic_tools.py`：
  ```python
  tools = topic_tools.build(id='qa6', title='标题', page='xxx.html', pdf='研经问答06-标题.pdf', quiz=T.QUIZ, ref=ref)
  return H.doc(title, desc, main, srcs, toc_html, cites, tools)
  ```
  顶栏多两个圆形按钮（分享、下载），开头“先说结论”下面和文末各有一排“分享这一篇 / 下载 PDF”。
  - **分享**：微信分享（在微信里提示点右上角 ···；手机浏览器复制链接并打开微信；电脑显示二维码）、复制链接、系统分享；分享后送一节经文。
  - **下载**：先答题。`QUIZ` 写在正文模块里（如 `jesus_text.QUIZ`），**至少 5 题**，每次随机抽 3 题，答对 2 题才出现下载按钮；
    每题当场显示对错、正确答案、一句解释和“第 N 章”链接；答错可以换 3 道题再答；答对过的手机以后直接下载。
    题目必须是读过本页才答得出来的（答案和解释都要能在本页找到原话），选择题 4 个选项，干扰项不能也是对的。
  - **PDF**：`python3 tools/q4/xxx.py --pdf` 同时生成网页和 PDF（`topic_pdf.js` 用 Chromium 打印，思源黑体/宋体，A4，有书签和页码），
    存到 `lessons/2026-Q4/qa/研经问答NN-标题.pdf`。**正文改了就要重新生成 PDF。** 生成后抽几页转成图片看一眼。
- 专题网页会在网站里用浮层打开（`app.js`），“← 问题彩蛋”等 `./#…` 链接自动交给网站处理；新专题网页不用另外做什么。

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
- 风格：跟《基督教两千年家谱》一致——开头“先说结论”，分部分、分章，目录按钮随时跳，图表充分（至少 3 张逻辑图，见下一节），语言通俗，篇幅不怕长但要精炼不丢信息。
- 写完：生成 → `verify-sources` 核对所有引文 → `publish` 的手机宽度检查 → 发布。README（`tools/q4/README.md`）里补一节说明。

## 页面外壳的新版式（2026-10-22）
`history.py` 的 `doc()` 统一加上：树形目录、像素进度条和阅读时间、图自动编号（取 SVG `<title>`）、开头和页尾的装饰、页尾“相关阅读”。
开头和页尾的装饰（2026-10-22 起）是像素小羊（`lamb.py`）和点阵星空（`pixsky.py`）：开头的小羊第一次看到时左右看一下，页尾的小羊读到最后时欢喜跳三下。不要在正文、经文旁边再放会动的东西。
**新增问题彩蛋时，在 `qa_data.py` 的 `RELATED` 里给它配三篇相关文章**（也可以顺便把它加进别的文章的 RELATED）；SVG 的 `<title>` 要写成读者能看懂的图名，因为它会显示成“图 N · 标题”。

## 用图讲道理：每篇至少三张“逻辑图”（用户 2026-10-22 定下）
用户从一份读书材料里的“身体与心意”图（外框＝身体、内框＝心意、内框里的点区分两种状态）得到的启发：
**很多真理可以浓缩成一张有逻辑的图，读一千字不如看一幅图深刻。**图不是装饰色块，而是把文字里的精髓、关系和内在逻辑画出来。

**要求**
- 每篇问题彩蛋**至少 3 张逻辑图**，放在最需要讲清楚的地方（核心概念、容易混淆的分别、过程或因果）。
- 先提炼，再画：用一句话写出这张图要说明的道理（写在 `<desc>` 里），图里的每个形状、颜色、位置都要对应这句话里的一个意思；说不出对应什么的元素就删掉。
- 图要能独立看懂：有标题、有图例（“外框＝……；内框＝……”），经文出处写在图里；编者的补充或推测在图里注明“编者补充 / 编者整理”。
- 图和文字配合，不重复：图给结构，正文给经文和解释；正文里只说“见上图”时，图本身必须已经说清楚。

**常用的图形和适合的问题**（先选形状，再选颜色）

| 图形 | 适合表达 | 本站例子 |
|---|---|---|
| 框中框（外框/内框，加点、加色区分状态） | 一个东西的两个层面，以及它在不同阶段的状态 | jesus.html“身体与心意”六格图 |
| 并排对照（两栏或多栏） | 两种东西、两条路、两个人的同与不同 | judas.html 彼得与犹大；law.html 约柜里/约柜旁、每周与年节的安息日 |
| 时间线 / 纵向步骤 | 历史先后、一步步的过程、挽回的历程 | judas.html 挽回历程；judgment.html 七十个七；prayer.html 但以理的二十一日 |
| 台阶 / 下坡 / 上坡 | 渐进的堕落或成长 | judas.html 下坡路 |
| 分类方块（2×2、三层） | 一个问题的几种答案、几种类型 | prayer.html 好/不/等/更好；law.html 三种律法三种结局 |
| 天平、圈子、流程箭头 | 平衡、恶性循环、因果 | jesus-qa 三架天平；listen.html 越劝越僵的圈子 |
| 统计图（柱、线） | 有真实数据的比较（数据要有出处） | trust.html 抄本数量对比；soon.html 圣经翻译统计 |

**画法约定**（`xxx_svg.py`，照 `jesus_svg.natures()`、`judas_svg.py` 抄）
- 宽 400 的 `viewBox`；用 `history_svg.text()` 写字；每张图有 `<title>` 和完整说明意思的 `<desc>`（读屏和搜索用）。
- 颜色只用页面的类（`f1 f3 f4 f6` 加 `fillc`、`box`、`dot`、`root`、`ax`、`flow`），**不要用纯黑/纯白表示意思**：夜间模式会反过来（2026-10-22 “身体与心意”图就因此从黑白改成金/红）。
  同一页里颜色意思要固定，例如金＝向着上帝/好的，红＝罪/危险，蓝绿＝中性分类。
- 彩色方块里的字用 `tnode2`（白字），方块外的说明用 `ts`/`tw`；彩色块上不要用 `ts` 灰字（看不清）。
- 写好后用 `secshotn.js` 截白天和夜间两张图逐一看：文字不重叠、不出框，320 宽手机上能看清。
- 图里引用的经文同样要和正文一样准确；`check_cuv.py` 也会检查 `<desc>` 里带出处的引号。

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
- 背景：本会一位牧师读后指出讲耶稣的人性必须了解 1955—1957 年《教义问答》的历史，所以 jesus.html 第 5 章补了这段历史。

## 图里的每个记号都要解释（2026-10-23，提供参考资料的牧者提醒）
图里哪怕多一个点，也要在图下写明意思，否则读者会误解。照别人的原图重画时，**不要自己加记号**；原图的颜色有意义（例如白＝圣洁、黑点＝罪的污染），就照原图的颜色画。
夜间模式会把颜色反过来时，把这类颜色写死在图里（像《耶稣具有完全的人性和完全的神性吗？》的“身体与心意”图），不要为了配色改掉原意。

## 分类与经文索引（2026-10-23）
- 问题彩蛋页按 7 类排列（`qa_data.CATS`）。**新增一篇时，在 `qa_data.CAT_OF` 里给它一个类别**（每篇只放一类）；是给不信主的朋友看的，加进 `SEEKER`；适合放进“三条阅读路线”的，改 `PATHS`。
- 类别颜色：`theme.css` 和 `qa_index.py` 里的 `--qc-类别`（白天、夜间各一套）。类名用读者的话，不用神学术语。
- 生成顺序：先生成专题页（`xxx.py`），再 `python3 tools/q4/qa_index.py`（经文索引，读各页正文里带出处的经文），最后 `_combined_only.py`（首页卡片上的“约几分钟 · 几章”也是从专题页读出来的）。

