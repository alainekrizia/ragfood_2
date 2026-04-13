import type { Config } from 'tailwindcss'
import defaultTheme from 'tailwindcss/defaultTheme'

const config: Config = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        background: '#faf8f3',
        foreground: '#1a1a1a',
        primary: '#d4602e',
        secondary: '#2d5016',
        accent: '#c9a961',
        'neutral-light': '#f5f1e8',
        'neutral-dark': '#3a3a3a',
      },
      fontFamily: {
        sans: ['var(--font-sans)', ...defaultTheme.fontFamily.sans],
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
export default config
