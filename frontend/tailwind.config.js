/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        parchment: {
          50: '#FAF8F3',
          100: '#F4EFE6',
          150: '#EFE8DD',
          200: '#E8DFCFAF',
          300: '#DACDB8',
          800: '#1C1914',
          900: '#13110E',
        },
        ink: {
          950: '#18140E',
          900: '#2B2419',
          800: '#3D3425',
          700: '#564936',
          600: '#726149',
          500: '#8F7B5E',
          400: '#AD997B',
        },
        maroon: {
          900: '#561A1A',
          800: '#6E2222',
          700: '#8B2E2E',
          600: '#A43A3A',
          500: '#BE4A4A',
          100: '#FBE8E8',
          50: '#FDF4F4',
        },
        gold: {
          800: '#7B622E',
          700: '#92763A',
          600: '#A68846',
          500: '#B8995C',
          400: '#CBAD73',
          300: '#DDC492',
          200: '#ECDCB7',
          100: '#F6EED8',
          50: '#FAF6EC',
        },
        stoic: '#92763A',
        existential: '#8B2E2E',
        deontological: '#324E7B',
        virtue: '#366854',
        daoist: '#583D72',
      },
      fontFamily: {
        serif: ['"EB Garamond"', '"Playfair Display"', 'Georgia', 'serif'],
        display: ['"Playfair Display"', 'Georgia', 'serif'],
        body: ['"EB Garamond"', 'Georgia', 'serif'],
        sans: ['"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"Fira Code"', 'monospace']
      },
      boxShadow: {
        'parchment-sm': '0 1px 3px rgba(43, 36, 25, 0.06), 0 1px 2px rgba(184, 153, 92, 0.1)',
        'parchment-md': '0 4px 12px rgba(43, 36, 25, 0.08), 0 2px 4px rgba(184, 153, 92, 0.15)',
        'parchment-lg': '0 10px 25px rgba(43, 36, 25, 0.1), 0 4px 10px rgba(184, 153, 92, 0.2)',
        'inner-gold': 'inset 0 0 0 1px rgba(184, 153, 92, 0.35)',
      }
    },
  },
  plugins: [],
}
