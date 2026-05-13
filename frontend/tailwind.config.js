/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#1a1a2e',
          light: '#16213e',
          lighter: '#0f3460',
        },
        accent: {
          DEFAULT: '#e94560',
          hover: '#ff6b81',
        },
      },
    },
  },
  plugins: [],
}
