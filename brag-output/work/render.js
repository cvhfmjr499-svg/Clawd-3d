const { chromium } = require('playwright');
const [,, mode, out, ...rest] = process.argv;
(async () => {
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  p.on('pageerror', e => console.log('err:', e.message));
  await p.goto('file://' + __dirname + '/video.html');
  await p.evaluate(() => window.ready);
  const times = mode === 'stills' ? rest.map(Number) : Array.from({ length: 600 }, (_, i) => i / 30);
  const fs = require('fs'); fs.mkdirSync(out, { recursive: true });
  const t0 = Date.now();
  for (let i = 0; i < times.length; i++) {
    await p.evaluate(t => renderAt(t), times[i]);
    const name = mode === 'stills' ? `s_${times[i].toFixed(2)}.jpg` : `f_${String(i).padStart(4, '0')}.jpg`;
    await p.screenshot({ path: `${out}/${name}`, type: 'jpeg', quality: 93 });
    if (i % 60 === 0) console.log(i, ((Date.now() - t0) / 1000).toFixed(1) + 's');
  }
  await b.close();
})();
