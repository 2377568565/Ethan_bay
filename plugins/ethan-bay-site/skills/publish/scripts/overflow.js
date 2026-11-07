// 手机宽度检查：页面在 320/360/390 宽、白天/夜间、标准字号和“特大”字号下有没有横向超出屏幕。
// 用法（仓库根目录）：node plugins/ethan-bay-site/skills/publish/scripts/overflow.js jesus.html history.html
//   SHOT=目录  另存每种情况的整页截图（看排版用）
// 结果每行一种情况：sw 是页面实际宽度，vw 是屏幕宽度；sw > vw 就是超出，后面列出超出的元素。
const path = require('path'), fs = require('fs');
let pw;
try { pw = require('playwright'); } catch (e) { pw = require('/opt/node22/lib/node_modules/playwright'); }

(async () => {
  const files = process.argv.slice(2);
  if (!files.length) { console.log('用法：node overflow.js 页面.html [...]'); process.exit(2); }
  const shot = process.env.SHOT;
  if (shot) fs.mkdirSync(shot, { recursive: true });
  const browser = await pw.chromium.launch();
  let bad = 0;
  for (const f of files) {
    const url = 'file://' + path.resolve(f);
    for (const width of [320, 360, 390]) for (const theme of ['light', 'dark']) for (const fsz of ['1', '1.25']) {
      const ctx = await browser.newContext({ viewport: { width, height: 800 }, isMobile: true, hasTouch: true, deviceScaleFactor: 2, colorScheme: theme });
      const p = await ctx.newPage();
      await p.addInitScript(([t, s]) => { try { localStorage.setItem('q4:theme', t); localStorage.setItem('q4:fs', s); } catch (e) {} }, [theme, fsz]);
      await p.goto(url, { waitUntil: 'load' });
      await p.waitForTimeout(800);
      const r = await p.evaluate(() => {
        const vw = innerWidth, sw = document.documentElement.scrollWidth, over = [];
        for (const el of document.querySelectorAll('body *')) {
          const b = el.getBoundingClientRect();
          if (b.width && b.right > vw + 1 && getComputedStyle(el).position !== 'fixed') {
            let sc = false;
            for (let a = el.parentElement; a; a = a.parentElement) { const o = getComputedStyle(a).overflowX; if (o === 'auto' || o === 'scroll' || o === 'hidden') { sc = true; break; } }
            if (!sc) over.push(el.tagName + '.' + (el.className && el.className.baseVal === undefined ? String(el.className).split(' ')[0] : '') + (el.id ? '#' + el.id : ''));
          }
        }
        return { vw, sw, over: [...new Set(over)].slice(0, 6) };
      });
      const tag = `${path.basename(f)} ${width} ${theme} 字号${fsz}`;
      if (r.sw > r.vw) bad++;
      console.log((r.sw > r.vw ? '✗ ' : '✓ ') + tag + ` sw=${r.sw} vw=${r.vw}` + (r.over.length ? ' 超出：' + r.over.join(' ') : ''));
      if (shot) await p.screenshot({ path: path.join(shot, `${path.basename(f, '.html')}-${width}-${theme}-${fsz}.png`), fullPage: true });
      await ctx.close();
    }
  }
  await browser.close();
  process.exit(bad ? 1 : 0);
})();
