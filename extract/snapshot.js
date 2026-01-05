import { chromium } from 'playwright';
import fs from 'fs';
import yaml from 'yaml';
import path from 'path';

const config = yaml.parse(fs.readFileSync('config/source_urls.yaml', 'utf8'));

const MAX_PAGES = 100;
const CRAWL_DEPTH = 2;

(async () => {
  console.log('🚀 Starting dynamic content extraction with link crawling...');
  
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });
  const page = await context.newPage();

  if (!fs.existsSync('raw/html')) {
    fs.mkdirSync('raw/html', { recursive: true });
  }

  const visited = new Set();
  const toVisit = [];
  
  for (const url of config.urls) {
    toVisit.push({ url, depth: 0 });
  }

  const baseUrl = new URL(config.urls[0]);
  const allowedDomain = baseUrl.hostname;

  console.log('📍 Base domain: ' + allowedDomain);
  console.log('📊 Max pages: ' + MAX_PAGES + ', Crawl depth: ' + CRAWL_DEPTH + '\n');

  let pageCount = 0;

  while (toVisit.length > 0 && pageCount < MAX_PAGES) {
    const { url, depth } = toVisit.shift();
    
    if (visited.has(url)) continue;
    visited.add(url);
    
    console.log('📄 [' + (pageCount + 1) + '/' + MAX_PAGES + '] Depth ' + depth + ': ' + url);
    
    try {
      await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
      await page.waitForTimeout(2000);
      
      const html = await page.content();
      const urlPath = new URL(url).pathname;
      const fname = urlPath.replace(/\//g, '_').replace(/^_/, '') || 'index.html';
      fs.writeFileSync(path.join('raw/html', fname), html);
      
      console.log('  ✅ Saved: ' + fname);
      pageCount++;
      
      if (depth < CRAWL_DEPTH) {
        const links = await page.evaluate(() => {
          return Array.from(document.querySelectorAll('a[href]'))
            .map(a => a.href)
            .filter(href => href.endsWith('.html') || href.endsWith('.htm'));
        });
        
        let newLinks = 0;
        for (const link of links) {
          try {
            const linkUrl = new URL(link);
            if (linkUrl.hostname === allowedDomain && !visited.has(link)) {
              if (depth === 1 && link.includes('Index.html')) continue;
              toVisit.push({ url: link, depth: depth + 1 });
              newLinks++;
            }
          } catch (e) {}
        }
        console.log('  🔗 Found ' + newLinks + ' new links to crawl');
      }
    } catch (error) {
      console.error('  ❌ Failed: ' + error.message);
    }
  }

  await browser.close();
  console.log('\n🏁 Snapshot complete: ' + pageCount + ' pages captured');
})();