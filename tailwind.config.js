/** @type {import('tailwindcss').Config} */
module.exports = {
  // Scan every Django template + every JS file that might emit class names.
  // Add new template directories here if/when the project grows.
  content: [
    './templates/**/*.html',
    './apps/**/templates/**/*.html',
    './static/js/**/*.js',
  ],
  theme: {
    extend: {
      // Mirrors the (former) inline `tailwind.config = {...}` block in landing.html.
      // Brand = green (project palette). Mint = lighter accent for gradient variation.
      colors: {
        brand: {
          50:  '#F0FDF4',
          100: '#DCFCE7',
          200: '#BBF7D0',
          500: '#22C55E',
          600: '#16A34A',
          700: '#15803D',
          800: '#166534',
          900: '#14532D',
        },
        mint: {
          50:  '#ECFDF5',
          100: '#D1FAE5',
          200: '#A7F3D0',
          400: '#34D399',
          500: '#10B981',
          600: '#059669',
        },
        ink: {
          900: '#0B1220',
          700: '#1F2937',
          500: '#4B5563',
          400: '#6B7280',
        },
      },
      fontFamily: {
        sans:    ['Inter', 'system-ui', 'sans-serif'],
        display: ['"Plus Jakarta Sans"', 'Inter', 'sans-serif'],
      },
      boxShadow: {
        soft: '0 2px 8px rgba(15,23,42,.04), 0 12px 24px rgba(15,23,42,.06)',
        glow: '0 24px 48px -12px rgba(22,163,74,.32)',
        mint: '0 24px 48px -12px rgba(16,185,129,.28)',
      },
    },
  },
  plugins: [
    require('tailwindcss-rtl'),
  ],
};
