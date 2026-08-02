# 呪 CURSED ARCHIVE — Jujutsu Kaisen Compendium

An immersive, visually-stunning Jujutsu Kaisen fan page covering:

- **Cursed Energy & Techniques** — the power system explained
- **Characters** — 9 sorcerers with signature cursed-energy colors
- **Domain Expansion** — Unlimited Void, Malevolent Shrine, Chimera Shadow Garden, Self-Embodiment of Perfection + full mechanic explainer
- **Season 2 Rules** — Hidden Inventory / Premature Death + Shibuya Incident arcs with the veil barrier, Prison Realm, binding vows, and the 200% Hollow Purple

## Features

- **Procedural cursed-energy flames** — generated in pure Python (`tools/gen_ce.py`), no dependencies, fractal noise + radial falloff, 8 colors per character
- **HD upscaled panels** — all manga images upscaled 2x with Lanczos3 via sharp (`tools/upscale.js`)
- **Animated cursed energy particle canvas** — 110 glowing particles with motion trails
- **Manga-influenced design** — kanji watermarks, corner brackets, grid-line background, color-theory-driven palette
- **No emojis in content** — kanji labels instead (呪力 呪術式 縛り 黒閃 獄門疆...)

## Usage

Open `index.html` in any modern browser. All assets are local — no external requests.

## Credits

- All characters, images, and lore belong to Gege Akutami and their respective owners.
- Maintained by **HIMESH BROR**
- Support on [Ko-fi](https://ko-fi.com/himanshu18)

## Asset Generation

```bash
# Upscale images (requires Node.js + sharp)
node tools/upscale.js

# Generate cursed-energy flame textures (pure Python, no deps)
python3 tools/gen_ce.py