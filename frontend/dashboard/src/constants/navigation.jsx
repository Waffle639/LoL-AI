// ─────────────────────────────────────────────────────────────────
// NAVIGATION
// Single source of truth for routes and sidebar items
// ─────────────────────────────────────────────────────────────────

export const ROUTES = {
  LOGIN:        '/',
  DASHBOARD:    '/dashboard',
  PREDICT_LIVE: '/predict/live',
  PRE_GAME:     '/predict/pregame',
  HISTORY:      '/history',
  BILLING:      '/billing',
  ACCOUNT:      '/account',
  MODELS:       '/models',
}

// Sidebar nav items — icon is a render function returning SVG paths
export const NAV_ITEMS = [
  {
    label: 'Dashboard',
    route: ROUTES.DASHBOARD,
    section: 'Navigation',
    icon: () => (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1"/>
        <rect x="14" y="3" width="7" height="7" rx="1"/>
        <rect x="3" y="14" width="7" height="7" rx="1"/>
        <rect x="14" y="14" width="7" height="7" rx="1"/>
      </>
    ),
  },
  {
    label: 'Predict Live',
    route: ROUTES.PREDICT_LIVE,
    section: 'Navigation',
    icon: () => <path d="M13 2L4.5 13.5H11L10 22L19.5 10H13Z"/>,
  },
  {
    label: 'Pre-Game',
    route: ROUTES.PRE_GAME,
    section: 'Navigation',
    icon: () => (
      <>
        <path d="M6 3l15 9-15 9V3z" opacity=".3"/>
        <path d="M3 12l6-9v18L3 12z"/>
        <path d="M21 12l-6-9v18l6-9z" opacity=".6"/>
      </>
    ),
  },
  {
    label: 'Historial',
    route: ROUTES.HISTORY,
    section: 'Navigation',
    icon: () => (
      <path d="M19 3H5a2 2 0 00-2 2v14a2 2 0 002 2h14a2 2 0 002-2V5a2 2 0 00-2-2zM7 7h10v1.5H7zm0 4h10v1.5H7zm0 4h6v1.5H7z"/>
    ),
  },
  {
    label: 'Billing',
    route: ROUTES.BILLING,
    section: 'Account',
    icon: () => (
      <>
        <path d="M12 2L2 8l10 14L22 8 12 2zm0 3.2L18.5 9 12 19.2 5.5 9 12 5.2z"/>
        <path d="M5.5 9h13L12 19.2 5.5 9z" opacity=".35"/>
      </>
    ),
  },
  {
    label: 'Mi Cuenta',
    route: ROUTES.ACCOUNT,
    section: 'Account',
    icon: () => (
      <path d="M12 2a5 5 0 100 10A5 5 0 0012 2zm0 12c-5.33 0-8 2.67-8 4v1h16v-1c0-1.33-2.67-4-8-4z"/>
    ),
  },
  {
    label: 'Modelos',
    route: ROUTES.MODELS,
    section: 'Account',
    icon: () => (
      <>
        <circle cx="4" cy="6" r="2"/>
        <circle cx="4" cy="18" r="2"/>
        <circle cx="12" cy="12" r="2"/>
        <circle cx="20" cy="4" r="2"/>
        <circle cx="20" cy="12" r="2"/>
        <circle cx="20" cy="20" r="2"/>
        <line x1="6" y1="6.8" x2="10" y2="11.2" stroke="currentColor" strokeWidth="1" opacity=".45"/>
        <line x1="6" y1="17.2" x2="10" y2="12.8" stroke="currentColor" strokeWidth="1" opacity=".45"/>
        <line x1="14" y1="11.3" x2="18" y2="4.8" stroke="currentColor" strokeWidth="1" opacity=".45"/>
        <line x1="14" y1="12" x2="18" y2="12" stroke="currentColor" strokeWidth="1" opacity=".45"/>
        <line x1="14" y1="12.7" x2="18" y2="19.2" stroke="currentColor" strokeWidth="1" opacity=".45"/>
      </>
    ),
  },
]

// Top navbar links (mockup navigator)
export const TOP_NAV = [
  { label: 'Login',        route: ROUTES.LOGIN },
  { label: 'Dashboard',   route: ROUTES.DASHBOARD },
  { label: 'Predict Live',route: ROUTES.PREDICT_LIVE },
  { label: 'Pre-Game',    route: ROUTES.PRE_GAME },
  { label: 'Historial',   route: ROUTES.HISTORY },
  { label: 'Billing',     route: ROUTES.BILLING },
  { label: 'Mi Cuenta',   route: ROUTES.ACCOUNT },
  { label: 'Modelos',     route: ROUTES.MODELS },
]
