// Render a diagram HTML file to PNG via headless Chrome.
// Usage: NODE_PATH="$HOME/node_modules" node render.js <input.html> <output.png>
// Screenshots the #canvas element, so the PNG is cropped to the diagram.
const puppeteer = require('puppeteer');
const path = require('path');

(async () => {
  const [, , htmlPath, outPath] = process.argv;
  if (!htmlPath || !outPath) {
    console.error('Usage: node render.js <input.html> <output.png>');
    process.exit(1);
  }
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath:
      process.env.CHROME_PATH ||
      '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--force-color-profile=srgb'],
  });
  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 1000, deviceScaleFactor: 2 });
  await page.goto('file://' + path.resolve(htmlPath), { waitUntil: 'networkidle0' });
  await page.evaluate(async () => { await document.fonts.ready; });
  await new Promise((r) => setTimeout(r, 200));
  const el = await page.$('#canvas');
  await el.screenshot({ path: outPath });
  await browser.close();
  console.log('wrote', outPath);
})();
