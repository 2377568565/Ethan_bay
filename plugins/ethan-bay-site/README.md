# ethan-bay-site 插件

《预言的恩赐》安息日学研读网站（https://2377568565.github.io/Ethan_bay/）的操作手册。这一路做网站积累下来的做法、版式、规矩都写在里面。
它和仓库根目录的 `CLAUDE.md` 配套使用：

| 文件 | 管什么 |
|---|---|
| `CLAUDE.md`（项目记忆） | 记录这是什么项目、和用户怎样合作、必须遵守的规矩、做过什么、还有什么没做完 |
| 本插件（操作手册） | 记录每一类工作具体怎么做 |

## 里面有什么
| 技能 | 内容 |
|---|---|
| `publish` | 生成、手机宽度检查、提交、推送、确认上线（附 `scripts/overflow.js`） |
| `lesson-pages` | 逐课研读页的结构、内容格式、写作规范、做下一季的步骤 |
| `topic-pages` | 问题彩蛋和专题网页的做法、上架和下架 |
| `verify-sources` | 经文和怀著引文核对（附 `scripts/check_cuv.py`）、临时读取打不开的网站（附 `templates/`） |
| `faith-answers` | 回答信仰问题的依据、写法和格式 |
| `music` | 音乐栏目：加歌、文件夹、格式、音量 |
| `tts-audio` | 朗读录音的补录 |
| `site-data` | 提问区等互动数据、访问人次、本机测试（附 `scripts/mock_ntfy.js`、`lib_dev.js`） |

## 怎样用

**云端会话（claude.ai/code、Claude App）**
- 不用做任何设置。新会话会下载仓库，并自动读取 `CLAUDE.md`；`CLAUDE.md` 会告诉 Claude 去读这里的手册。
- 注意：云端会话不会自动安装仓库里声明的插件，所以手册是当作普通文件来读的，效果一样。

**本机 Claude Code（Windows：`C:\Users\Ethan\.claude`）**，两种方法任选一种：
1. **解压安装（最简单）**：把 `ethan-bay-site` 文件夹放到 `C:\Users\Ethan\.claude\skills\ethan-bay-site\`。
   - 解压后要能看到 `C:\Users\Ethan\.claude\skills\ethan-bay-site\.claude-plugin\plugin.json`。
   - 下次启动 Claude Code 会自动加载，名字是 `ethan-bay-site@skills-dir`。
2. **从 GitHub 安装**：在终端运行下面两条命令。
   ```
   claude plugin marketplace add 2377568565/Ethan_bay#claude/adventist-lesson-analysis-dhqrxg
   claude plugin install ethan-bay-site@ethan-bay
   ```

装好后在 Claude Code 里输入 `/ethan-bay-site:publish` 之类就能直接调用某一本手册；平时 Claude 也会按需要自动使用。

**注意**：手册里的命令都要在仓库里运行（例如 `tools/q4/render.py`）。在本机使用时，要先把仓库 clone 下来。

## 更新
网站有新做法、新规矩时，改这里对应的 `SKILL.md` 和根目录的 `CLAUDE.md`，然后一起提交。
改完可以运行 `claude plugin validate plugins/ethan-bay-site` 检查格式。
如果修改涉及版本，记得把 `.claude-plugin/plugin.json` 里的 `version` 加一。
