import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: '#191919',
        secondary: '#242424',
        success: '#10b91e',
        warning: '#f59e0b',
        danger: '#ef4444',
        info: '#3b82f6',
        'module-identity': '#8b5cf6',
        'module-content': '#ec4899',
        'module-rewards': '#f59e0b',
        'module-community': '#10b981',
        'module-advertising': '#3b82f6',
        'module-messaging': '#06b6d4',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}

export default config

















