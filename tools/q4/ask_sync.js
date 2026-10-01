// 提问区同步：把中转站（ntfy）里的新消息验签、检查后写进 data/ask.json，并导出 data/ask.csv（可用 Excel 打开）。
// 由 .github/workflows/ask-sync.yml 定时运行；也可以本地运行：node tools/q4/ask_sync.js
const fs = require('fs'), path = require('path');
const { Q4Ask } = require('./ask_core.js');

const ROOT = path.join(__dirname, '..', '..');
const DATA = path.join(ROOT, 'data', 'ask.json');
const ADMINS = path.join(ROOT, 'data', 'ask-admins.json');
const VAULT = path.join(ROOT, 'data', 'vault.json');   // 账号同步的加密数据单独放，平时打开网页的人不用下载
const OUT = name => path.join(ROOT, 'data', name);
const TOPIC = process.env.Q4_TOPIC;
const RELAY = (process.env.Q4_RELAY || 'https://ntfy.sh').replace(/\/+$/, '');

function readJSON(f, d) { try { return JSON.parse(fs.readFileSync(f, 'utf8')); } catch (e) { return d; } }
async function fetchText(url) {
  for (let i = 0; ; i++) {
    try { const r = await fetch(url); if (!r.ok) throw new Error('HTTP ' + r.status); return await r.text(); }
    catch (e) { if (i >= 3) throw e; await new Promise(ok => setTimeout(ok, 4000 * (i + 1))); }
  }
}
function csvCell(v) { v = String(v == null ? '' : v); return /[",\n\r]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v; }
function fmt(ms) {
  const d = new Date(ms + 8 * 3600e3);   // 北京时间
  return d.toISOString().slice(0, 16).replace('T', ' ');
}
function csv(rows) { return '\ufeff' + rows.map(r => r.map(csvCell).join(',')).join('\r\n') + '\r\n'; }
const votes = (S, id) => (S.votes[id] || []).length;
function askCSV(S) {
  const rows = [['时间（北京）', '类型', '称呼', '地区', '内容', '回复的问题', '想知道人数', '置顶', '身份码']];
  for (const q of S.questions.slice().sort((a, b) => a.ts - b.ts)) {
    rows.push([fmt(q.ts), '问题', q.name, q.loc, q.text, '', votes(S, q.id), q.pin ? '是' : '', q.uid]);
    for (const r of S.replies.filter(r => r.qid === q.id).sort((a, b) => a.ts - b.ts))
      rows.push([fmt(r.ts), r.admin ? '管理员回答' : '回复', r.name, r.loc, r.text, q.text.slice(0, 30), '', '', r.uid]);
  }
  return csv(rows);
}
const DAYN = { sab: '安息日下午', sun: '星期日', mon: '星期一', tue: '星期二', wed: '星期三', thu: '星期四', fri: '星期五', sum: '安息日课堂' };
function dayName(k) { const m = /^l(\d+)-(\w+)/.exec(k); return m ? `第${m[1]}课 ${DAYN[m[2]] || m[2]}` : k; }
function discussCSV(S) {
  const rows = [['时间（北京）', '课 / 日', '题号', '称呼', '地区', '回答', '有帮助人数', '身份码']];
  for (const a of S.answers.slice().sort((x, y) => x.k.localeCompare(y.k, 'en', { numeric: true }) || x.ts - y.ts))
    rows.push([fmt(a.ts), dayName(a.k), a.k.split('-').pop(), a.name, a.loc, a.text, votes(S, a.id), a.uid]);
  return csv(rows);
}
function checkinsCSV(S) {
  const rows = [['课 / 日', '读完打卡人数']];
  for (const k of Object.keys(S.checks).sort((a, b) => a.localeCompare(b, 'en', { numeric: true }))) rows.push([dayName(k), S.checks[k].length]);
  return csv(rows);
}

(async () => {
  if (!TOPIC) throw new Error('Q4_TOPIC 没有设置');
  const S = Q4Ask.norm(readJSON(DATA, {}));
  S.vault = (readJSON(VAULT, {}) || {}).vault || {};
  const before = JSON.stringify(S);
  S.admins = readJSON(ADMINS, []).filter(u => /^[0-9a-f]{32}$/.test(u));
  const since = S.last ? Math.max(0, S.last - 120) : 'all';
  const txt = await fetchText(`${RELAY}/${TOPIC}/json?poll=1&since=${since}`);
  const msgs = txt.split('\n').map(l => { try { return JSON.parse(l); } catch (e) { return null; } }).filter(Boolean);
  const out = await Q4Ask.merge(S, msgs);
  const cut = Math.floor(Date.now() / 1000) - 2 * 86400;   // 两天前的消息编号不用再记
  for (const k of Object.keys(S.seen)) if (S.seen[k] < cut) delete S.seen[k];
  console.log(`中转站消息 ${msgs.length} 条，新处理 ${out.length} 条：` + (out.map(o => o.why || 'ok').join(', ') || '无'));
  // 表格每次都按当前存档重新导出，内容没变就不动文件（表格格式升级后也会自动补上）
  const sheets = { 'ask.csv': askCSV(S), 'discuss.csv': discussCSV(S), 'checkins.csv': checkinsCSV(S) };
  const stale = Object.keys(sheets).filter(f => { try { return fs.readFileSync(OUT(f), 'utf8') !== sheets[f]; } catch (e) { return true; } });
  if (JSON.stringify(S) === before && fs.existsSync(DATA) && !stale.length) { console.log('没有变化'); return; }
  fs.mkdirSync(path.dirname(DATA), { recursive: true });
  if (JSON.stringify(S) !== before || !fs.existsSync(DATA)) {
    S.updated = Math.floor(Date.now() / 1000);
    const { vault, ...pub } = S;
    fs.writeFileSync(DATA, JSON.stringify(pub));
    fs.writeFileSync(VAULT, JSON.stringify({ updated: S.updated, vault }));
  }
  for (const f of stale) fs.writeFileSync(OUT(f), sheets[f]);
  console.log(`已写入：问题 ${S.questions.length} 个，回复 ${S.replies.length} 条，讨论回答 ${S.answers.length} 条，打卡 ${Object.values(S.checks).reduce((n, a) => n + a.length, 0)} 次，账号 ${Object.keys(S.accounts).length} 个` + (stale.length ? `；更新表格 ${stale.join('、')}` : ''));
})().catch(e => { console.error(e); process.exit(1); });
