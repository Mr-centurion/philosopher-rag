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
        stoic: '#eab308',
        existential: '#ef4444',
        deontological: '#3b82f6',
        virtue: '#10b981',
        daoist: '#8b5cf6',
        parchment: {
          50: '#fbf9f4',
          100: '#f5f0e6',
          200: '#ebe1cb',
          800: '#1a1815',
          900: '#0f0e0c',
        }
      },
      fontFamily: {
        serif: ['"Cinzel"', '"Merriweather"', 'Georgia', 'serif'],
        sans: ['"Inter"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"Fira Code"', 'monospace']
      }
    },
  },
  plugins: [],
}
