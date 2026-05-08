/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        cream: '#F7F3EC',
        forest: '#2D6A4F',
        coffee: '#6B4226',
        primary: '#2C1A0E',
        muted: '#8B6F52',
      },
      keyframes: {
        bob: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-8px)' },
        },
        fly: {
          '0%': { transform: 'translateX(-120px)', opacity: '0' },
          '10%': { opacity: '1' },
          '90%': { opacity: '1' },
          '100%': { transform: 'translateX(110vw)', opacity: '0' },
        },
        borderPulse: {
          '0%, 100%': { borderColor: 'rgba(45, 106, 79, 0.4)' },
          '50%': { borderColor: 'rgba(45, 106, 79, 0.9)' },
        },
      },
      animation: {
        bob: 'bob 3s ease-in-out infinite',
        fly: 'fly 2.5s ease-in-out infinite',
        'border-pulse': 'borderPulse 2s ease-in-out infinite',
      },
    },
  },
  plugins: [],
}
