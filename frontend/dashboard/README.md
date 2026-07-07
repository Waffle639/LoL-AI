# LoL-AI Dashboard

Interactive prediction dashboard for the LoL-AI API. Built with React 18, Vite, and anime.js.

## What it does

This is the workspace where authenticated users run predictions, manage credits, and inspect model status.

- **Predict Live** — fill 24 match fields (identity + combat + objectives) and hit the Neural Network. Auto-fills historical stats when you pick a team + player + champion.
- **Pre-Game** — a visual champion selector inspired by the LoL client. Lock in 5 players per side, assign champions from a searchable grid, and get a Random Forest prediction before the match starts.
- **Models** — health check and loaded model versions.
- **Billing** — Stripe checkout integration; credit balance and top-up history.
- **Account** — JWT profile, API key prefix, logout.
- **Login** — JWT authentication with splash art background.

## Stack

- **React 18** + **Vite**
- **react-router-dom v6** — client-side routing with protected routes
- **anime.js 3.2** — all animations (panel entrances, particle bursts, progress bars, staggered lists)
- **CSS Modules** — scoped styles per component (no global class collisions)
- **Custom design tokens** — `src/styles/tokens.css` defines the colour palette (teal, gold, red, dark blues)
- **No Tailwind, no UI library** — 100 % custom components

## Structure

```
src/
├── assets/
│   └── splash.jpg              # Login background
├── components/
│   ├── charts/                 # DonutChart, Sparkline
│   ├── layout/                 # AppLayout, Topbar, Sidebar
│   ├── screens/                # One file per route
│   │   ├── Login.jsx
│   │   ├── Dashboard.jsx
│   │   ├── PredictLive.jsx     # Live match prediction form
│   │   ├── PreGame.jsx         # Champion picker + draft predictor
│   │   ├── Billing.jsx
│   │   ├── Account.jsx
│   │   ├── Models.jsx
│   │   └── History.jsx         # (currently commented out in router)
│   └── ui/                     # Reusable primitives
│       ├── Badge, Button, FormField, Logo, Panel, SearchSelect, StatCard
├── constants/
│   ├── champions.js            # Champion list + roles
│   └── navigation.jsx          # Route definitions
├── context/
│   └── AppContext.jsx          # Auth state, credits, sidebar
├── hooks/
│   ├── useAnime.js             # anime.js helpers
│   └── useSidebar.js           # Sidebar open/close logic
├── styles/
│   └── tokens.css              # CSS custom properties (colours, spacing)
├── api/
│   ├── auth.js                 # JWT login / register / refresh
│   └── billing.js              # Stripe checkout calls
├── utils/
│   └── championIcons.js        # Data Dragon URL builder
├── main.jsx
└── App.jsx                     # Router + protected routes
```

## Setup

```bash
npm install
npm run dev
```

Runs on `http://localhost:5174` by default.

## Environment

Create `.env` in the dashboard root:

```
VITE_API_URL=http://localhost:8000
```

## Authentication flow

1. User logs in at `/login` → receives JWT access token + httpOnly refresh cookie.
2. `AppContext` stores the token and fetches the user profile + credit balance.
3. All authenticated screens are wrapped in `AuthenticatedRoute`; unauthenticated users are redirected to `/login`.
4. The token refreshes silently via `/auth/refresh` when needed.
5. API calls to prediction endpoints use the JWT Bearer header. The Predict Live screen can also use an explicit `X-API-Key` if the user prefers.

## Key UI details

- **Predict Live** — SearchSelect components for team/player/champion fetch `/predict/options` on mount. Changing team + player + champion triggers `/predict/stats` to auto-populate the 5 historical performance fields (winrates, KDA). The result card shows a blue-vs-red probability bar and an anime.js particle burst on prediction.
- **Pre-Game** — Slot-based UI: click a portrait to search a player, then click a champion from the grid. Role filters (ALL / TOP / JNG / MID / BOT / SUP) and a search input narrow the champion list. When all 10 slots are filled, the "Lock In & Predict" button calls `/predict/pregame`.
- **Billing** — Credit bundles redirect to Stripe Checkout; a webhook on the backend updates the balance automatically. The dashboard polls `/billing/credits` after a successful return.

## Notes

- The dashboard is fully responsive down to tablet size; the Pre-Game grid collapses gracefully.
- All numeric inputs use `inputMode="numeric"` or `decimal` for better mobile UX.
- The `AppContext` exposes `consumeCredit()` so every screen can decrement the local balance immediately after a successful prediction, avoiding an extra round-trip.
