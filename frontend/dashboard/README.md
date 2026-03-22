# LoL-AI — React Frontend

Dashboard de predicciones para la API LoL-AI. Construido con React 18 + Vite + anime.js.

## Estructura

```
src/
├── assets/               # Imágenes estáticas (splash.jpg)
├── components/
│   ├── charts/           # DonutChart, Sparkline
│   ├── layout/           # AppLayout, Topbar, Sidebar
│   ├── screens/          # Una pantalla por archivo
│   └── ui/               # Badge, Button, FormField, Logo, Panel, StatCard
├── constants/            # navigation.jsx, champions.js
├── context/              # AppContext (credits, sidebar, user)
├── hooks/                # useAnime.js, useSidebar.js
└── styles/               # tokens.css (design tokens globales)
```

## Setup

```bash
npm install
npm run dev
```

## Splash art del login

Pon el archivo `splash.jpg` en `src/assets/` (la imagen de siluetas LoL que ya tienes).

## Variables de entorno

Crea un `.env` en la raíz:

```
VITE_API_URL=http://localhost:8000
```

## Conectar con la API

En cada screen, reemplaza los datos mock por llamadas reales:

```js
// Ejemplo en PredictLive.jsx
const res = await fetch(`${import.meta.env.VITE_API_URL}/predict`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-API-Key': apiKey,
  },
  body: JSON.stringify(formData),
})
const data = await res.json()
```

## Stack

- **React 18** + Vite
- **react-router-dom v6** — rutas
- **animejs 3.2** — todas las animaciones
- **CSS Modules** — estilos con scope por componente
- Sin Tailwind, sin UI libraries — 100% custom
