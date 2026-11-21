// 表格“挤成一个字宽”检查（2026-10-23 用户反映：电脑上“经文”一栏被挤成一个字一行）。
// 在手机和电脑几种宽度下，找出表格里被挤窄的格子：排成 3 行以上，而且平均每行不到 2 个字。
// 用法（仓库根目录）：node plugins/ethan-bay-site/skills/publish/scripts/cols.js heaven.html blood.html
// 全部 ✓ 才算过；✗ 后面列出表格和那一栏的内容开头。CSS='…' 可以临时加一段样式试验修法。
const path = require('path');
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('/opt/node22/lib/node_modules/playwright'); }

(async () => {
  const files = process.argv.slice(2);
  if (!files.length) { console.log('用法：node cols.js 页面.html [...]'); process.exit(2); }
  const browser = await pw.chromium.launch();
  let bad = 0;
  for (const f of files) {
    const url = 'file://' + path.resolve(f);
    for (const width of [320, 390, 768, 1280, 1600]) {
      const mobile = width < 700;
      const ctx = await browser.newContext({ viewport: { width, height: 900 }, isMobile: mobile, hasTouch: mobile, deviceScaleFactor: 1 });
      const p = await ctx.newPage();
      await p.goto(url, { waitUntil: 'load' });
      if (process.env.CSS) await p.addStyleTag({ content: process.env.CSS });   // 试验新样式用
      await p.waitForTimeout(600);
      const r = await p.evaluate(() => {
        const out = [];
        document.querySelectorAll('table').forEach((t, ti) => {
          for (const c of t.querySelectorAll('td,th')) {
            const txt = c.textContent.replace(/\s+/g, '');
            if (txt.length < 3) continue;
            // 数一数这一格实际排成了几行：平均每行不到 2 个字，就是被挤成了“一个字一行”
            const rg = document.createRange(); rg.selectNodeContents(c);
            const cs = getComputedStyle(c), fz = parseFloat(cs.fontSize);
            const lh = cs.lineHeight === 'normal' ? fz * 1.4 : parseFloat(cs.lineHeight);
            const n = Math.round(rg.getBoundingClientRect().height / lh);   // 按高度算行数（上标的出处小数字不算一行）
            if (n >= 3 && txt.replace(/\d+$/, '').length / n < 2) {
              const sec = c.closest('section');
              out.push(`表${ti + 1}${sec && sec.id ? '（#' + sec.id + '）' : ''} 第${c.cellIndex + 1}栏「${txt.slice(0, 12)}」排成${n}行`);
              break;
            }
          }
        });
        return out;
      });
      const tag = `${path.basename(f)} ${width}`;
      if (r.length) bad++;
      console.log((r.length ? '✗ ' : '✓ ') + tag + (r.length ? ' 太窄：' + r.slice(0, 6).join('；') : ''));
      await ctx.close();
    }
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
