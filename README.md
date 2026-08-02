# 呪 CURSED ARCHIVE — Shibuya Incident Files

An immersive **Jujutsu Kaisen** manga experience — CSS-drawn manga panels, domain clashes, Shibuya Incident rules, and the sorcerers who survived it.

> Fan-made tribute · Jujutsu Kaisen © Gege Akutami / Shueisha

---

## ✨ Features

- **Manga Panel Design System** — every card, quote, and section is framed as a comic panel with halftone screentones, speed lines, onomatopoeia (ゴゴゴ, ドドド, バキッ), and speech bubbles — all pure CSS, no images
- **JJK Color Theory** — Gojo cyan, Sukuna red, Megumi violet, Nanami/Nobara gold on a near-black ink base with manga paper white accents
- **Domain Clash Simulator** — two manga panels battle with a VS beam, screen shake, and rotating clash results (Infinite Void vs Malevolent Shrine, etc.)
- **Shibuya Rules Section** — 8 official rules of the Shibuya Incident arc: Domain Expansion, Binding Vows, Black Flash, Simple Domain, Domain Amplification, Prison Realm, Mahoraga, Hollow Wicker Basket
- **Sorcerer Vault** — manga-panel character cards with onomatopoeia tags, cursed energy meters, and expandable domains
- **Domain Expansion Overlay** — full-screen canvas domain expansion with expanding slashes
- **Immersive preloader** — manga-style loading screen with ゴゴゴ onomatopoeia
- **Custom cursor** — cursed-energy cursor dot & ring with click ripples and velocity slashes
- **Animated hero** — glitch text, parallax layers, live typewriter, manga panel frame background
- **Curse Index** — cursed spirits, cursed objects & binding vows as manga panels
- **Grade ladder** — Grade 4 to Special Grade with animated bars
- **Creed section** — dramatic manga-panel reveal of Yuji Itadori's creed
- **Marquee ticker** — scrolling Japanese/English cursed-energy terms
- **Support section + Ko-fi** — dedicated donation shrine + floating Ko-fi badge → [ko-fi.com/himanshu18](https://ko-fi.com/himanshu18)
- **Fully responsive** — mobile drawer menu, touch-friendly interactions, reduced-motion support

## 🛠️ Tech Stack

- **HTML5** — semantic structure
- **CSS3** — custom properties, keyframe animations, manga panel primitives (halftone, speed lines, bubbles), responsive layout
- **Vanilla JavaScript** — DOM manipulation, canvas effects, parallax, typewriter, domain clash engine
- **Google Fonts** — Anton, Noto Serif JP, Rajdhani, Share Tech Mono, Bangers
- **GitHub Pages / any static host** — no build step required

## 🚀 Getting Started

Open `index.html` in your browser — no build step required.

```bash
# Clone the repo
git clone https://github.com/Himeshbror18/cursed-archive.git

# Open the project
cd cursed-archive
open index.html   # macOS
# or
xdg-open index.html   # Linux
```

## 📁 Project Structure

```
cursed-archive/
├── index.html      # Main page structure
├── style.css       # All styling, manga panel primitives & animations
├── script.js       # Interactivity, canvas effects & domain clash engine
└── .gitignore      # Git ignore rules
```

## 🎨 Customization

- **Colors** — edit CSS custom properties in `style.css` (see the color theory comment at the top)
- **Sorcerers** — roster is injected by `script.js`; add/remove entries there
- **Domain Clash** — clash pairs & results live in `CLASH_PAIRS` in `script.js`
- **Shibuya Rules** — edit the rule cards in `index.html`
- **Ko-fi link** — search `ko-fi.com/himanshu18` in `index.html` to point it anywhere

## ☕ Support

If this domain expanded your pupils, consider a coffee:

**[https://ko-fi.com/himanshu18](https://ko-fi.com/himanshu18)**

## 📧 Contact

Maintained by **himesh bror** — [himeshbror@gmail.com](mailto:himeshbror@gmail.com)

---

*Built with cursed energy, vanilla JS & manga panels.*