# 呪術廻戦 · JUJUTSU KAISEN — Cursed Energy

An immersive **Jujutsu Kaisen** fan experience — cursed energy, domain expansions and the sorcerers who bear them.

> Fan-made tribute · Jujutsu Kaisen © Gege Akutami / Shueisha

---

## ✨ Features

- **Immersive preloader** — a domain-expansion style loading screen with a percentage counter
- **Custom cursor** — a cursed-energy cursor dot & ring that follows your mouse
- **Animated hero** — glitch text, parallax layers, and a live typewriter effect
- **Curses section** — cursed spirits, cursed objects & binding vows
- **Sorcerers roster** — hover cards that charge cursed energy, with expandable domains
- **Domain showcase** — an interactive domain visual with a "random domain" button
- **Grade ladder** — from Grade 4 to Special Grade, with animated bars
- **Creed section** — a dramatic reveal of Yuji Itadori's creed
- **Domain overlay** — a full-screen canvas-based domain expansion effect
- **Marquee ticker** — scrolling Japanese/English cursed-energy terms
- **Fully responsive** — mobile drawer menu, touch-friendly interactions

## 🛠️ Tech Stack

- **HTML5** — semantic structure
- **CSS3** — custom properties, animations, glitch effects, responsive layout
- **Vanilla JavaScript** — DOM manipulation, canvas effects, parallax, typewriter
- **Google Fonts** — Anton, Noto Serif JP, Rajdhani
- **Vercel** — static deployment

## 🚀 Getting Started

### Local Development

Simply open `index.html` in your browser — no build step required.

```bash
# Clone the repo
git clone https://github.com/Himeshbror18/cursed-archive.git

# Open the project
cd cursed-archive
open index.html   # macOS
# or
xdg-open index.html   # Linux
```

### Deploy to Vercel

The project includes a `vercel.json` configured for static hosting.

```bash
# Install Vercel CLI (if not already)
npm i -g vercel

# Deploy
vercel
```

## 📁 Project Structure

```
cursed-archive/
├── index.html      # Main page structure
├── style.css       # All styling & animations
├── script.js       # Interactivity & canvas effects
├── vercel.json     # Vercel deployment config
└── .gitignore      # Git ignore rules
```

## 🎨 Customization

- **Colors** — edit CSS custom properties in `style.css` (e.g. `--c` variables on cards)
- **Sorcerers** — the roster is injected by `script.js`; add/remove entries there
- **Domains** — domain names & descriptions live in `script.js`
- **Text content** — all copy is in `index.html`

## 📧 Contact

Maintained by **himesh bror** — [himeshbror@gmail.com](mailto:himeshbror@gmail.com)

---

*Built with cursed energy & vanilla JS.*