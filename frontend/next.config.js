const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development'
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    GATEWAY_URL: process.env.GATEWAY_URL || 'http://localhost:8080',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'
  },
  // Vercel 배포를 위한 설정
  experimental: {
    esmExternals: false
  }
}

module.exports = withPWA(nextConfig) 