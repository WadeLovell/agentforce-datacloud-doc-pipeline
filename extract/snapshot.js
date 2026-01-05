import { chromium } from 'playwright';
import fs from 'fs';
import yaml from 'yaml';
import path from 'path';

const config = yaml.parse(fs.readFileSync('config/source_urls.yaml', 'utf8'));

(async () => {
  console.log('🚀 Starting dynamic content extraction...');
  
  const browser = await chromium.launch({
    headless: true
  });
  
  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
  });
  
  const page = await context.newPage();

  // Ensure output directory exists
  if (!fs.existsSync('raw/html')) {
    fs.mkdirSync('raw/html', { recursive: true });
  }

  for (const url of config.urls) {
    console.log(`📄 Processing: ${url}`);
    
    try {
      await page.goto(url, { 
        waitUntil: 'networkidle',
        timeout: 60000 
      });
      
      // Wait for main content to render (adjust selector as needed)
      await page.waitForSelector('main, #content, .content, article', {
        timeout: 30000
      }).catch(() => {
        console.log('  ⚠️  No standard content selector found, using body');
      });
      
      // Additional wait for JS frameworks to finish rendering
      await page.waitForTimeout(2000);
      
      const html = await page.content();
      const fname = encodeURIComponent(url).slice(0, 200) + '.html';
      fs.writeFileSync(path.join('raw/html', fname), html);
      
      console.log(`  ✅ Saved: ${fname}`);
      
    } catch (error) {
      console.error(`  ❌ Failed: ${url}`);
      console.error(`     Error: ${error.message}`);
    }
  }

  await browser.close();
  console.log('🏁 Snapshot complete');
})();
