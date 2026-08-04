const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const srcDir = '/home/himesh/Documents/pt2/jjk_panels';
const outDir = '/home/himesh/Documents/pt2/jjk_panels_hd';
fs.mkdirSync(outDir, { recursive: true });

const files = fs.readdirSync(srcDir).filter(f => /\.(webp|png|jpg|gif)$/i.test(f));

(async () => {
  for (const f of files) {
    const src = path.join(srcDir, f);
    const out = path.join(outDir, f.replace(/\.(webp|png|jpg|gif)$/i, '.png'));
    try {
      const meta = await sharp(src).metadata();
      // upscale 2x, cap at 1600px on long edge, lanczos3, then compress
      const img = sharp(src, { animated: false }).resize({
        width: Math.min(meta.width * 2, 1600),
        height: Math.min(meta.height * 2, 1600),
        fit: 'inside',
        kernel: sharp.kernel.lanczos3
      });
      await img.png({ compressionLevel: 9, palette: false }).toFile(out);
      const sz = fs.statSync(out).size;
      console.log(`OK  ${f} (${meta.width}x${meta.height}) -> ${path.basename(out)} (${(sz/1024).toFixed(0)}KB)`);
    } catch (e) {
      console.log(`ERR ${f}: ${e.message}`);
    }
  }
  console.log('=== UPSCALE DONE ===');
})();