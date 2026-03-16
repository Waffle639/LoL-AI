/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        gold: {
          DEFAULT: '#C8A96E',
          bright:  '#D4B483',
          dim:     '#7a5f38',
          dark:    '#3a2c15',
        },
        teal: {
          DEFAULT: '#0AC8B9',
          dim:     '#063d38',
        },
        red: {
          rift: '#C83020',
        },
        bg: {
          DEFAULT: '#020915',
          2: '#060f1e',
          3: '#0b1628',
          4: '#101e35',
        },
      },
      fontFamily: {
        cinzel:  ['Cinzel', 'serif'],
        rajdhani: ['Rajdhani', 'sans-serif'],
        mono:    ['"Share Tech Mono"', 'monospace'],
        exo:     ['"Exo 2"', 'sans-serif'],
      },
      letterSpacing: {
        widest2: '0.3em',
        widest3: '0.4em',
        widest4: '0.5em',
      },
      clipPath: {
        hex:      'polygon(50% 0%, 100% 25%, 100% 75%, 50% 100%, 0% 75%, 0% 25%)',
        skew:     'polygon(10px 0%, 100% 0%, calc(100% - 10px) 100%, 0% 100%)',
        'skew-sm':'polygon(7px 0%, 100% 0%, calc(100% - 7px) 100%, 0% 100%)',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'scroll-hint': 'scrollHint 2s ease-in-out infinite',
        'blink': 'blink 1s ease-in-out infinite',
      },
      keyframes: {
        scrollHint: {
          '0%, 100%': { opacity: '0.15' },
          '50%':      { opacity: '0.75' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.15' },
        },
      },
    },
  },
  plugins: [],
}