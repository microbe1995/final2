const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: false  // Vercel에서도 PWA 활성화
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    // API Gateway 설정
    GATEWAY_URL: process.env.GATEWAY_URL || 'http://localhost:8080',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1'
  },
  
  // CORS 설정 (개발용)
  async headers() {
    return [
      {
        source: '/api/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' },
        ],
      },
    ]
  },
  
  // 이미지 도메인 설정
  images: {
    domains: ['localhost', 'lca-final.vercel.app'],
  },

  // Vercel Analytics 비활성화
  experimental: {
    instrumentationHook: false
  }
}

module.exports = withPWA(nextConfig) 