/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/atoms/**/*.{js,ts,jsx,tsx,mdx}',
    './src/molecules/**/*.{js,ts,jsx,tsx,mdx}',
    './src/organisms/**/*.{js,ts,jsx,tsx,mdx}',
    './src/templates/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      // ============================================================================
      // 🎨 색상 팔레트 (desing.json 기반)
      // ============================================================================
      colors: {
        // Primary Colors
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#2563eb',  // desing.json의 accent
          600: '#1d4ed8',
          700: '#1e40af',
          800: '#1e3a8a',
          900: '#1e3a8a',
        },
        
        // Background & Surface
        bg: '#0b0c0f',  // desing.json의 bg
        surface: '#ffffff',  // desing.json의 surface
        
        // Text Colors
        'text-primary': '#0f172a',    // desing.json의 text_primary
        'text-secondary': '#475569',  // desing.json의 text_secondary
        
        // Border & Muted
        border: '#e2e8f0',  // desing.json의 border
        muted: '#f1f5f9',
        'muted-foreground': '#64748b',
        
        // Status Colors
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#16a34a',  // desing.json의 success
          600: '#15803d',
          700: '#166534',
          800: '#14532d',
          900: '#14532d',
        },
        
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#d97706',  // desing.json의 warning
          600: '#b45309',
          700: '#92400e',
          800: '#78350f',
          900: '#78350f',
        },
        
        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#dc2626',  // desing.json의 danger
          600: '#b91c1c',
          700: '#991b1b',
          800: '#7f1d1d',
          900: '#7f1d1d',
        },
      },

      // ============================================================================
      // 🔤 타이포그래피 (desing.json 기반)
      // ============================================================================
      fontSize: {
        'body': ['14px', { lineHeight: '1.5' }],           // desing.json body
        'body-large': ['16px', { lineHeight: '1.5' }],     // desing.json body_large
        'h3': ['18px', { lineHeight: '1.3' }],             // desing.json h3
        'h2': ['22px', { lineHeight: '1.3' }],             // desing.json h2
        'h1': ['28px', { lineHeight: '1.3' }],             // desing.json h1
      },

      // ============================================================================
      // 📏 간격 스케일 (desing.json 기반)
      // ============================================================================
      spacing: {
        '4': '4px',    // desing.json s4
        '8': '8px',    // desing.json s8
        '12': '12px',  // desing.json s12
        '16': '16px',  // desing.json s16
        '20': '20px',  // desing.json s20
        '24': '24px',  // desing.json s24
        '32': '32px',  // desing.json s32
      },

      // ============================================================================
      // 🔄 Border Radius (desing.json 기반)
      // ============================================================================
      borderRadius: {
        'sm': '8px',   // desing.json radius-sm
        'md': '12px',  // desing.json radius-md
        'lg': '16px',  // desing.json radius-lg
        'pill': '999px', // desing.json radius-pill
      },

      // ============================================================================
      // 🎭 애니메이션 (desing.json 기반)
      // ============================================================================
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },

      // ============================================================================
      // 🎨 Box Shadow (desing.json 기반)
      // ============================================================================
      boxShadow: {
        'elevation-0': 'none',
        'elevation-1': '0 1px 2px rgba(0, 0, 0, 0.06)',  // desing.json elevation-1
        'elevation-2': '0 4px 12px rgba(0, 0, 0, 0.10)', // desing.json elevation-2
      },

      // ============================================================================
      // 🔧 Transition (desing.json 기반)
      // ============================================================================
      transitionDuration: {
        'standard': '160ms',  // desing.json standard_duration_ms
        'fast': '120ms',      // desing.json hover duration_ms
      },

      transitionTimingFunction: {
        'standard': 'cubic-bezier(0.2, 0, 0, 1)',  // desing.json standard easing
      },

      // ============================================================================
      // 📱 Breakpoints (desing.json 기반)
      // ============================================================================
      screens: {
        'sm': '640px',   // desing.json sm
        'md': '768px',   // desing.json md
        'lg': '1024px',  // desing.json lg
        'xl': '1280px',  // desing.json xl
      },

      // ============================================================================
      // 🎯 Grid System (desing.json 기반)
      // ============================================================================
      gridTemplateColumns: {
        'app-shell': '240px 1fr',  // desing.json sidebar width + main
      },

      gridTemplateRows: {
        'app-shell': '64px 1fr auto',  // desing.json header height + main + footer
      },
    },
  },
  plugins: [],
} 