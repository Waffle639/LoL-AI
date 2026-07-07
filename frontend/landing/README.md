# LoL-AI Landing Page

Cinematic landing page for the LoL-AI prediction project.

## What it does

- **Hero** — full-viewport scroll-driven experience. A custom HTML5 Canvas (`DraftCanvas.jsx`) draws both team rosters with real champion icons from Riot Data Dragon, progressively revealing a mock AI prediction as you scroll.
- **Scenes** — alternating left/right feature sections highlighting the two models (Pre-Game Random Forest and Live Neural Network) with real accuracy metrics pulled from the API metadata.
- **Players, Stats, Pricing, CupCTA** — supporting sections with custom cursor effects and Tailwind styling.

## Stack

- **React 18** + **Vite**
- **Tailwind CSS** — utility-first styling
- **Custom Canvas 2D engine** — no external chart or game libraries; pure `CanvasRenderingContext2D` with gradient sheens, slot-by-slot entrance animations, and dynamic `devicePixelRatio` scaling.
- **anime.js** — used inside the dashboard; the landing relies mostly on CSS transitions and scroll-driven JS.
- **Google Fonts** — Cinzel, Rajdhani, Share Tech Mono, Exo 2.

## Structure

```
src/
├── components/
│   ├── Hero.jsx           # Scroll wrapper + text overlay + DraftCanvas
│   ├── DraftCanvas.jsx    # The canvas draft animation (Data Dragon icons)
│   ├── Scene.jsx          # Feature section layout (image + text)
│   ├── Players.jsx        # Pro player showcase
│   ├── Stats.jsx          # Model stats grid
│   ├── Pricing.jsx        # Credit bundle cards
│   ├── CupCTA.jsx         # Final CTA + footer
│   ├── Navbar.jsx         # Fixed nav
│   └── Cursor.jsx         # Custom cursor follower
├── hooks/
│   └── index.js           # useHeroScroll (scroll progress 0→1)
├── data/
│   └── content.js         # DRAFT_BLUE / DRAFT_RED roster arrays
├── main.jsx
└── App.jsx
```

## Setup

```bash
npm install
npm run dev
```

Runs on `http://localhost:5173` by default.

## Environment

Create `.env` if you need to point the dashboard link elsewhere:

```
VITE_DASHBOARD_URL=http://localhost:5174
```

## Notes

- Champion icons are fetched from `https://ddragon.leagueoflegends.com/cdn/{VERSION}/img/champion/{name}.png` with a small key-mapping for edge cases like `Kha'Zix → Khazix`.
- The canvas is `pointer-events-none` so scroll and clicks pass through to the DOM layer.
- The background stadium image (`/images/EstadioRojoyAzul.jpg`) is layered under four gradient overlays for readability.
