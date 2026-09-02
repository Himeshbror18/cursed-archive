# 呪 CURSED ARCHIVE — Jujutsu Kaisen Compendium

An interactive, fan-made **Jujutsu Kaisen** web compendium focused on cursed energy, cursed techniques, characters, Domain Expansion, and the major Season 2 story mechanics.

The project is intentionally built as a mostly self-contained static website: no framework, no build system, and no database required. Just HTML, CSS, JavaScript, and a frankly unreasonable number of visual effects.

## What is here?

The site is split into two main experiences:

### Main archive — `index.html`

The main landing page combines:

- Cursed Energy and cursed-technique explanations
- Character cards with character-specific visual treatments
- Cursed-energy aura and flame effects
- Domain Expansion reference cards
- Season 2 / Shibuya reference material
- Responsive layouts for desktop and mobile
- Animated background particles
- Scroll-reveal animations
- Hero-image parallax
- Local image assets

### Domain Expansion Simulator — `domain-expansion.html`

A separate interactive page that turns the Domain Expansion concept into an actual browser experience.

It includes:

- Domain selection and activation
- Character/domain display changes
- Domain-specific colors and visual filters
- Full-screen activation flashes and rings
- Kanji overlays
- Particle effects
- Web Audio-generated activation sounds
- Finger-count input for domain selection
- Camera/hand-tracking interaction where supported
- A manual interaction path so the experience is not completely dependent on a webcam

The simulator is intentionally client-side. The browser does the work; there is no backend quietly judging your cursed energy output.

## Project structure

```text
cursed-archive/
├── index.html                  # Main compendium
├── jjk.html                    # Alternate/older archive page
├── domain-expansion.html       # Interactive Domain Expansion experience
├── fandom_page.html            # Fandom/content reference page
├── jjk_feed.json               # Local feed/data used by the project
│
├── assets/                    # Images and visual assets
│   └── ...
│
├── jjk_panels/                # Source manga panels
├── jjk_panels_hd/             # Upscaled panels
├── jjk_panels_ce/             # Cursed-energy variants
│
├── tools/
│   ├── gen_ce.py              # Generates cursed-energy textures
│   └── upscale.js             # Upscales panels with Sharp
│
├── download_jjk.py            # Asset/content downloader
├── download_jjk2.py           # Alternate downloader
└── download_jjk.sh            # Shell-based downloader
```

## Design

The visual language is deliberately closer to a dark editorial/manga interface than a conventional anime fan page.

### Visual system

- Near-black layered backgrounds
- Cyan / violet cursed-energy palette
- Kanji used as structural decoration
- Grid-line and corner-bracket motifs
- Large editorial typography
- Character-specific accent colors
- Soft glow rather than constant neon overload
- Responsive cards and grids

The goal is **atmosphere without turning every pixel into an RGB gaming keyboard**.

## Interaction system

### Main archive

The main page uses browser-native JavaScript for:

```text
Particle canvas
      │
      ├── floating cursed-energy particles
      ├── motion trails
      └── color variation

IntersectionObserver
      │
      └── reveal sections as they enter the viewport

Scroll listener
      │
      └── hero parallax

CSS animations
      │
      ├── character hover effects
      ├── cursed-energy flames
      ├── card transitions
      └── domain visual effects
```

This keeps the page lightweight and avoids a framework being introduced solely to make a div move three pixels to the left.

### Domain simulator

The simulator has a larger interaction loop:

```text
User input
   │
   ├── manual selection
   │
   └── hand/finger input
           │
           ▼
     Domain selection
           │
           ▼
     triggerDomain()
           │
     ┌─────┼─────────────┐
     ▼     ▼             ▼
  visuals audio       character
     │     │             │
     └─────┼─────────────┘
           ▼
     particle / FX loop
```

The domain activation function changes the active domain, updates colors and character information, triggers the visual overlay, and plays a synthesized activation sound.

## Browser requirements

The main archive works as a normal static webpage.

For the Domain Expansion simulator:

- A modern browser is recommended.
- Web Audio requires user interaction before audio can play in many browsers.
- Camera-based interaction requires browser camera permission.
- Hand/finger detection is naturally more sensitive to lighting, camera quality, hand position, and background clutter.
- If camera interaction is unreliable, manual interaction should be preferred.

For local development, opening the HTML files directly is enough for the basic static experience. A local HTTP server is preferable when testing browser APIs such as camera access.

Example:

```bash
python3 -m http.server 8000
```

Then open:

```text
http://localhost:8000/
```

## Asset generation

### Generate cursed-energy textures

```bash
python3 tools/gen_ce.py
```

The generator is dependency-free Python and produces the visual cursed-energy assets used by the site.

### Upscale panels

```bash
node tools/upscale.js
```

The upscaler uses **Sharp** and is intended for preparing higher-resolution panel assets.

Install Sharp if the script requires it:

```bash
npm install sharp
```

Generated assets should be reviewed before committing. Bigger does not automatically mean better; sometimes it just means the same pixels have been given more confidence.

## Current code review

The website is structurally healthy for a static project:

- No framework dependency
- No build step for the main pages
- CSS and JavaScript are contained with the pages
- Responsive breakpoints are present
- Animation work is mostly GPU-friendly CSS/canvas work
- `IntersectionObserver` is used instead of continuously checking scroll position for reveal effects
- The Domain Expansion page separates domain state from the visual activation logic reasonably well
- The site has a clear fallback path for manual domain interaction

### Things worth keeping an eye on

**Performance:** The particle canvases, large images, glow effects, and animated assets can become expensive on low-end phones. Reduced-motion and lower-particle-count modes would be a worthwhile future improvement.

**Accessibility:** The visual design is strong, but keyboard focus states, semantic controls, reduced-motion handling, and screen-reader descriptions could be improved.

**Content accuracy:** This is a fan compendium, not an authoritative canon database. Some explanations should be treated as simplified descriptions rather than exact technical rules.

**Asset size:** The repository contains substantial image assets. Keeping generated/upscaled copies organized is important so the website does not become a giant image folder with an HTML file attached.

**Camera interaction:** Finger-count detection is inherently probabilistic. It should be treated as an input convenience, not a guaranteed control mechanism.

## Hand-sign recognition

The Domain Expansion simulator supports an optional local **Real-time-GesRec** recognition backend. It uses the temporal gesture-recognition approach from ahmetgunduz/Real-time-GesRec, while keeping the browser landmark detector as a fallback. The upstream project is a PyTorch implementation for real-time hand-gesture detection/classification using temporal video clips. citeturn1search0

Because the upstream pretrained classes are **not Jujutsu Kaisen hand seals**, Cursed Archive does not pretend that an off-the-shelf checkpoint recognizes them. The included bridge expects a custom six-class checkpoint trained/fine-tuned for the project's seals. See `gesture_bridge/README.md`.

### Credit

Cursed Archive uses an integration layer inspired by and built to work with:

- **Ahmet Gunduz — Real-time-GesRec**
- Okan Köpüklü
- Neslihan Kose
- Gerhard Rigoll

Please retain the upstream project's license and academic citation requirements when using its source code or pretrained models. The original project documents the associated research and pretrained models. citeturn1search0

## Recommended next improvements

In priority order:

1. Add a **reduced-motion mode** and respect `prefers-reduced-motion`.
2. Add a **low-power/mobile FX mode** with fewer canvas particles.
3. Improve keyboard navigation and visible focus states.
4. Add a loading strategy for large images.
5. Give the Domain Expansion simulator a clearer manual control panel.
6. Add a small on-screen camera status/error message when hand tracking cannot initialize.
7. Consolidate duplicate/older HTML pages once the preferred page is confirmed.
8. Add a simple automated HTML/link check to catch broken local asset paths.

## Credits

- **Jujutsu Kaisen**, its characters, artwork, terminology, and story belong to **Gege Akutami** and the respective rights holders.
- This repository is a fan-made project and is not affiliated with the official franchise.
- Maintained by **HIMESH BROR**.
- Support: [Ko-fi](https://ko-fi.com/himanshu18)

## License

See the repository's license files for the applicable terms.

## Name

Yes, it is called **Cursed Archive**.

Yes, the name is staying.
