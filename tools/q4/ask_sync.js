// 提问区同步：把中转站（ntfy）里的新消息验签、检查后写进 data/ask.json，并导出 data/ask.csv（可用 Excel 打开）。
// 由 .github/workflows/ask-sync.yml 定时运行；也可以本地运行：node tools/q4/ask_sync.js
const fs = require('fs'), path = require('path');
const { Q4Ask } = require('./ask_core.js');

const ROOT = path.join(__dirname, '..', '..');
const DATA = path.join(ROOT, 'data', 'ask.json');
const ADMINS = path.join(ROOT, 'data', 'ask-admins.json');
const CSV = path.join(ROOT, 'data', 'ask.csv');
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
function toCSV(S) {
  const rows = [['时间（北京）', '类型', '称呼', '地区', '内容', '回复的问题', '身份码']];
  const qs = S.questions.slice().sort((a, b) => a.ts - b.ts);
  for (const q of qs) {
    rows.push([fmt(q.ts), '问题', q.name, q.loc, q.text, '', q.uid]);
    for (const r of S.replies.filter(r => r.qid === q.id).sort((a, b) => a.ts - b.ts))
      rows.push([fmt(r.ts), r.admin ? '管理员回答' : '回复', r.name, r.loc, r.text, q.text.slice(0, 30), r.uid]);
  }
  return '﻿' + rows.map(r => r.map(csvCell).join(',')).join('\r\n') + '\r\n';
}

(async () => {
  if (!TOPIC) throw new Error('Q4_TOPIC 没有设置');
  const S = Object.assign(Q4Ask.empty(), readJSON(DATA, {}));
  const before = JSON.stringify(S);
  S.admins = readJSON(ADMINS, []).filter(u => /^[0-9a-f]{32}$/.test(u));
  const since = S.last ? Math.max(0, S.last - 120) : 'all';
  const txt = await fetchText(`${RELAY}/${TOPIC}/json?poll=1&since=${since}`);
  const msgs = txt.split('\n').map(l => { try { return JSON.parse(l); } catch (e) { return null; } }).filter(Boolean);
  const out = await Q4Ask.merge(S, msgs);
  const cut = Math.floor(Date.now() / 1000) - 2 * 86400;   // 两天前的消息编号不用再记
  for (const k of Object.keys(S.seen)) if (S.seen[k] < cut) delete S.seen[k];
  console.log(`中转站消息 ${msgs.length} 条，新处理 ${out.length} 条：` + (out.map(o => o.why || 'ok').join(', ') || '无'));
  if (JSON.stringify(S) === before && fs.existsSync(DATA)) { console.log('没有变化'); return; }
  S.updated = Math.floor(Date.now() / 1000);
  fs.mkdirSync(path.dirname(DATA), { recursive: true });
  fs.writeFileSync(DATA, JSON.stringify(S));
  fs.writeFileSync(CSV, toCSV(S));
  console.log(`已写入：问题 ${S.questions.length} 个，回复 ${S.replies.length} 条`);
})().catch(e => { console.error(e); process.exit(1); });
