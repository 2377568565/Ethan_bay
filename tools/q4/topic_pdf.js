// 把问题彩蛋专题网页（history.html、jesus.html……）打印成 PDF 学习版，存进 lessons/2026-Q4/qa/。
// 用法：node tools/q4/topic_pdf.js <网页.html> <输出.pdf> [标题]
// 字体：用 Q4_WORK（默认 tools/q4/.work）/fonts 里的思源黑体、思源宋体，PDF 里只嵌入用到的字。
const path = require('path'), fs = require('fs');
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('/opt/node22/lib/node_modules/playwright'); }
const [src, out, title = ''] = process.argv.slice(2);
if (!src || !out) { console.log('用法：node topic_pdf.js 网页.html 输出.pdf [标题]'); process.exit(2); }
const W = process.env.Q4_WORK || path.join(__dirname, '.work');
const F = n => 'file://' + path.join(W, 'fonts', n);
for (const n of ['sans400.ttf', 'sans700.ttf', 'serif600.ttf', 'serif900.ttf'])
  if (!fs.existsSync(path.join(W, 'fonts', n))) { console.error('缺少字体 ' + n + '：先运行 python3 tools/q4/fetch_assets.py'); process.exit(1); }
const FONTS = `
@font-face{font-family:"Noto Sans SC";font-weight:400;src:url(${F('sans400.ttf')})}
@font-face{font-family:"Noto Sans SC";font-weight:700;src:url(${F('sans700.ttf')})}
@font-face{font-family:"Noto Serif SC";font-weight:600;src:url(${F('serif600.ttf')})}
@font-face{font-family:"Noto Serif SC";font-weight:900;src:url(${F('serif900.ttf')})}
:root{--sans:"Noto Sans SC",sans-serif!important;--serif:"Noto Serif SC",serif!important}
@page{size:A4;margin:16mm 15mm 18mm}
body{font-size:10.5pt!important}
.hero{padding-top:0!important}
`;

(async () => {
  const b = await pw.chromium.launch();
  const p = await b.newPage({ colorScheme: 'light' });
  await p.addInitScript(() => { try { localStorage.setItem('q4:theme', 'light'); localStorage.removeItem('q4:fs'); } catch (e) {} });
  await p.goto('file://' + path.resolve(src), { waitUntil: 'load' });
  await p.addStyleTag({ content: FONTS });
  await p.evaluate(() => { document.querySelectorAll('details').forEach(d => { d.open = true; }); });
  await p.emulateMedia({ media: 'print' });
  await p.evaluate(() => document.fonts.ready);
  const miss = await p.evaluate(() => [...document.fonts].filter(f => f.status === 'error').map(f => f.family + ' ' + f.weight));
  const foot = `<div style="width:100%;font-size:7.5pt;color:#8a8f9c;padding:0 15mm;display:flex;justify-content:space-between;font-family:'WenQuanYi Zen Hei',sans-serif">
    <span>${title ? title + ' · ' : ''}问题彩蛋 · 整理制作 · Ethan（HangZhou_XG）</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>`;
  await p.pdf({ path: out, format: 'A4', printBackground: true, preferCSSPageSize: true, outline: true, tagged: true,
    displayHeaderFooter: true, headerTemplate: '<span></span>', footerTemplate: foot });
  await b.close();
  console.log(out, fs.statSync(out).size, 'bytes', miss.length ? '字体没载入：' + miss.join(', ') : '');
})();
