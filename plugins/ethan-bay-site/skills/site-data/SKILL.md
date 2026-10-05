---
name: site-data
description: 网站的线上互动数据（提问区、我也想知道、读经打卡、讨论区、账号同步、访问人次）怎样存、怎样同步、怎样测试，以及回答“今天多少人”“这周每天多少人”。用于用户问人数、提问区出问题、管理员、账号、打卡、本周研读时间等。
---

# 互动数据与人数

## 存在哪里（全部在 GitHub 仓库，不用国内数据库）
用户明确不用腾讯云等国内服务（试过，安全域名要会员），数据存在 GitHub：
- 网页把消息签名后投到公开中转站 ntfy.sh（频道名是 `render.py` 的 `ASK_TOPIC`），所有人的网页马上能看到；
- `.github/workflows/ask-sync.yml` 每 30 分钟把中转站里的新消息验签、检查后写进仓库 `data/`，提交说明“提问区：同步新问题与回复”（中转站只保留 12 小时）。
  定时任务只在默认分支上触发，所以 `main` 上也放了一份 `ask-sync.yml`（用户同意过；main 上只放这个）。它会检出网站分支再同步。
- `data/` 里的文件：
  | 文件 | 内容 |
  |---|---|
  | `ask.json` | 网页读取的完整存档（问题、回复、想知道、打卡、账号列表 `accounts`、访问人次 `hits`/`hits0`） |
  | `ask.csv`、`discuss.csv`、`checkins.csv` | 给人看的表格（Excel 能打开）：提问与回复、讨论区回答、每天打卡人数（不记名字） |
  | `vault.json` | 账号同步的密文（平时打开网页不下载） |
  | `ask-admins.json` | 管理员名单（身份码）；不要外传 |
- 共同规则在 `tools/q4/ask_core.js`（验签、防刷、谁能回复/删除/置顶），网页和同步任务共用；`ask_sync.js` 是同步脚本。
- 身份：每台设备第一次发言时生成密钥对（只在这台设备上），身份码 = 公钥哈希；管理员能回答、删除、置顶、关联问答文章。
- 位置：发问时可以选择让浏览器定位；读者主要在中国大陆。

## 账号（可选）
账号 + 密码，无需手机号邮箱。密码在本机用 PBKDF2 派生两把钥匙（AES-GCM 加密、HMAC 编格子号），网上只有密文；**忘记密码无法找回**。
同步：字号、夜间模式、朗读速度、称呼、地区、写下的回答、行动勾选、读到哪里、打卡、本周研读时间、达到目标的周、身份。

## 本周研读时间
每台设备各记各的，欢迎页显示加总；**每周日凌晨 0 点（北京时间）重新计算**（用户要求“周六晚上 24 点刷新”）。
键 `time:<那周星期日 YYYY-MM-DD>`，按 UTC+8 计算；达到 1 小时显示“更美的欢迎页”。

## 回答“今天多少人”
用户只要在对话里看一个表，**不要做到网站上**。数字是“人次”（打开网页一次算一次，同一台设备 10 分钟内只算一次，自动测试的浏览器不算），不是人数。
```sh
git pull -q origin claude/adventist-lesson-analysis-dhqrxg
# 总数 = hits0（不蒜子时期的旧数，2026-10-01 为 368）+ hits；按北京时间看每次同步时的 hits：
for c in $(git log -40 --format=%H -- data/ask.json); do
  echo "$(TZ=Asia/Shanghai git show -s --format='%ad' --date=format-local:'%m-%d %H:%M' $c) $(git show $c:data/ask.json | python3 -c 'import json,sys;d=json.load(sys.stdin);print(d.get("hits"))')"
done
```
每天的增加 = 当天最后一次同步的 hits − 前一天最后一次的 hits。最新数据要等下一次同步（最多 30 分钟）；急的话可以手动触发：
`gh api -X POST repos/2377568565/Ethan_bay/actions/workflows/ask-sync.yml/dispatches -f ref=main`。

## 本机测试互动功能
脚本在本技能的 `scripts/`：
```sh
node plugins/ethan-bay-site/skills/site-data/scripts/mock_ntfy.js &   # 本机模拟中转站（8090 端口），记下进程号
# 测试脚本里：const L=require('<路径>/lib_dev.js'); const b=await L.launch(); const p=await L.device(b,'A',errs);
#   p 打开线上网址，但网页文件由本机仓库提供、中转站换成本机；L.sync() 运行一次同步。
```
- 测完：`kill <进程号>`（**不要用 `pkill -f`**，会把当前 shell 一起关掉）；`git checkout data/` 恢复，**测试数据绝不推到线上**。
- 不要在线上网站发测试问题或打卡。
