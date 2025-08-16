const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: process.env.NODE_ENV === 'development', // 개발 환경에서만 비활성화
  runtimeCaching: [
    {
      urlPattern: /^https?.*/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'offlineCache',
        expiration: {
          maxEntries: 200,
        },
      },
    },
  ],
})

/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    // API Gateway 설정 - 실제 사용하는 /api/v1 경로로 통일
    GATEWAY_URL: process.env.GATEWAY_URL || 'http://localhost:8080',
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080',
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080/api/v1',
    
    // Railway 배포 환경 설정 - 실제 사용하는 /api/v1 경로로 통일
    NEXT_PUBLIC_RAILWAY_API_URL: process.env.NEXT_PUBLIC_RAILWAY_API_URL || 'http://localhost:8080',
    NEXT_PUBLIC_RAILWAY_API_BASE_URL: process.env.NEXT_PUBLIC_RAILWAY_API_BASE_URL || 'http://localhost:8080/api/v1',
    
    // 환경 구분 (NODE_ENV 제거 - Vercel에서 자동 설정)
    IS_RAILWAY_DEPLOYED: process.env.IS_RAILWAY_DEPLOYED || 'false'
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
    unoptimized: false,
  },

  // Vercel Analytics 비활성화
  experimental: {
    instrumentationHook: false
  },
  
  // 빌드 시 정적 페이지 생성 문제 해결
  trailingSlash: false,
  
  // Vercel 배포 최적화
  swcMinify: true,
  
  // Vercel 자동 감지 최적화
  distDir: '.next',
  
  // 빌드 최적화
  compress: true,
}

module.exports = withPWA(nextConfig) 