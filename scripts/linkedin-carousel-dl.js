const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const https = require('https');

const LINKEDIN_EMAIL = process.env.LINKEDIN_EMAIL;
const LINKEDIN_PASSWORD = process.env.LINKEDIN_PASSWORD;

const POST_URL = process.argv[2];
if (!POST_URL) {
  console.error('Usage: LINKEDIN_EMAIL=x LINKEDIN_PASSWORD=y node linkedin-carousel-dl.js <post-url>');
  process.exit(1);
}
if (!LINKEDIN_EMAIL || !LINKEDIN_PASSWORD) {
  console.error('Set LINKEDIN_EMAIL and LINKEDIN_PASSWORD env vars');
  process.exit(1);
}

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const file = fs.createWriteStream(dest);
    https.get(url, { headers: { 'User-Agent': 'Mozilla/5.0' } }, (res) => {
      if (res.statusCode === 301 || res.statusCode === 302) {
        file.close();
        fs.unlinkSync(dest);
        return download(res.headers.location, dest).then(resolve).catch(reject);
      }
      res.pipe(file);
      file.on('finish', () => { file.close(); resolve(dest); });
    }).on('error', (err) => { fs.unlinkSync(dest); reject(err); });
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
  });
  const page = await context.newPage();

  console.log('Logging into LinkedIn...');
  await page.goto('https://www.linkedin.com/login', { waitUntil: 'networkidle' });
  await page.fill('#username', LINKEDIN_EMAIL);
  await page.fill('#password', LINKEDIN_PASSWORD);
  await page.click('button[type="submit"]');
  await page.waitForURL('**/feed/**', { timeout: 30000 });
  console.log('Logged in.');

  console.log('Navigating to post...');
  await page.goto(POST_URL, { waitUntil: 'networkidle', timeout: 30000 });

  // Wait for content to render
  await page.waitForTimeout(3000);

  // Try multiple selectors to find carousel images
  let images = await page.evaluate(() => {
    const urls = new Set();

    // Try document viewer slides
    document.querySelectorAll('.document-viewer__slide img, .carousel-slide img, .ivm-view-attr__img--centered')
      .forEach(img => { if (img.src) urls.add(img.src); });

    // Try any large image inside the feed update (carousel context)
    document.querySelectorAll('.feed-shared-update-v2__content img[src*="licdn.com"], .update-components-image img[src*="licdn.com"]')
      .forEach(img => { if (img.src) urls.add(img.src); });

    // Try carousel navigation items (dots may reveal images)
    document.querySelectorAll('[data-control-name="carousel_dot"]')
      .forEach(dot => urls.add(`DOT:${dot.getAttribute('data-slide')}`));

    // Fallback: all lcdn images in the post area
    const feedEl = document.querySelector('.feed-shared-update-v2__content, .update-components-article, .occludable-update');
    if (feedEl) {
      feedEl.querySelectorAll('img[src*="licdn.com"]').forEach(img => {
        if (img.src && img.offsetWidth > 100) urls.add(img.src);
      });
    }

    return [...urls];
  });

  // If carousel has dots, click through to collect all slides
  const dots = await page.$$('[data-control-name="carousel_dot"]');
  if (dots.length > 0) {
    for (let i = 0; i < dots.length; i++) {
      await dots[i].click();
      await page.waitForTimeout(1000);
      const slideImgs = await page.evaluate(() => {
        return [...document.querySelectorAll('.document-viewer__slide img, .carousel-slide img, .ivm-view-attr__img--centered, img[src*="licdn.com"]')]
          .map(img => img.src)
          .filter(Boolean);
      });
      slideImgs.forEach(u => images.push(u));
    }
  }

  images = [...new Set(images.filter(u => u.startsWith('http') && u.includes('licdn.com')))];

  if (images.length === 0) {
    console.log('No carousel images found via selectors. Trying fallback...');
    const html = await page.content();
    const matches = html.match(/https?:\/\/media\.licdn\.com\/dms\/image\/[^"'\s]+/g) || [];
    images = [...new Set(matches)];
  }

  console.log(`Found ${images.length} carousel images.`);

  if (images.length === 0) {
    console.log('Could not find carousel images. The post may not have a carousel, or auth failed.');
    await browser.close();
    process.exit(0);
  }

  // Save images
  const slug = process.argv[3] || 'carousel';
  const outDir = path.resolve(__dirname, `../posts/assets/${slug}`);
  fs.mkdirSync(outDir, { recursive: true });

  for (let i = 0; i < images.length; i++) {
    const ext = path.extname(new URL(images[i]).pathname).split('?')[0] || '.jpg';
    const dest = path.join(outDir, `slide${i + 1}${ext}`);
    console.log(`Downloading slide ${i + 1}/${images.length}...`);
    await download(images[i], dest);
  }

  console.log(`Done. ${images.length} images saved to posts/assets/${slug}/`);
  await browser.close();
})();
