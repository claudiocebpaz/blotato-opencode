const { chromium } = require('playwright');
const path = require('path');

const htmlPath = process.argv[2];
const outDir = process.argv[3] || path.dirname(path.resolve(htmlPath));

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 2 });
  const page = await context.newPage();
  await page.goto('file://' + path.resolve(htmlPath), { waitUntil: 'networkidle' });
  await page.evaluate(async () => { await document.fonts.ready; });
  await new Promise(r => setTimeout(r, 1200));
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    await slides[i].screenshot({ path: path.join(outDir, `slide${i + 1}.png`) });
    console.log('rendered slide', i + 1);
  }
  await browser.close();
  console.log('DONE', slides.length, 'slides ->', outDir);
})().catch(e => { console.error(e); process.exit(1); });
