// Renders a branded carousel (HTML/CSS) to PNGs, one file per slide.
// Each slide is a 1080x1350 <div class="slide"> in the HTML.
//
// Usage:
//   NODE_PATH="$HOME/node_modules" node scripts/carousel/render.js <html> [outDir]
//
// Requires: Google Chrome installed + puppeteer resolved via NODE_PATH.
// Output: <outDir>/slide1.png, slide2.png, ... (2x, 2160x2700).
const puppeteer = require('puppeteer');
const path = require('path');

const htmlPath = process.argv[2] || path.join(__dirname, 'carousel.html');
const outDir = process.argv[3] || path.dirname(path.resolve(htmlPath));
const CHROME = process.env.CHROME_PATH ||
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--force-color-profile=srgb', '--hide-scrollbars'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1080, height: 1350, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve(htmlPath), { waitUntil: 'networkidle0' });
  await page.evaluate(async () => { await document.fonts.ready; });
  await new Promise(r => setTimeout(r, 800)); // ensure webfonts are loaded
  const slides = await page.$$('.slide');
  for (let i = 0; i < slides.length; i++) {
    await slides[i].screenshot({ path: path.join(outDir, `slide${i + 1}.png`) });
    console.log('rendered slide', i + 1);
  }
  await browser.close();
  console.log('DONE', slides.length, 'slides ->', outDir);
})().catch(e => { console.error(e); process.exit(1); });
