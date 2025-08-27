const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: true, // 개발 환경에서 PWA 비활성화
  buildExcludes: [
    /middleware-manifest\.json$/,
    /app-build-manifest\.json$/,        // PWA에서 문제되는 파일 제외
    /_buildManifest\.js$/,
    /_ssgManifest\.js$/
  ],
  publicExcludes: [
    '!workbox-*.js',
    '!sw.js'
  ],
  runtimeCaching: [
    {
      urlPattern: /^https:\/\/gateway-production-da31\.up\.railway\.app/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'gateway-api-cache-v2',  // 캐시 버전 업데이트
        expiration: {
          maxEntries: 100,
          maxAgeSeconds: 60 * 60 * 24, // 24시간
        },
        cacheableResponse: {
          statuses: [0, 200],
        },
      },
    },
    {
      urlPattern: /^https:\/\/www\.greensteel\.site/,
      handler: 'NetworkFirst',
      options: {
        cacheName: 'greensteel-api-cache-v2',  // 캐시 버전 업데이트
        expiration: {
          maxEntries: 100,
          maxAgeSeconds: 60 * 60 * 24, // 24시간
        },
        cacheableResponse: {
          statuses: [0, 200],
        },
      },
    },
    {
      urlPattern: /\.(?:png|jpg|jpeg|svg|gif|webp|avif)$/,
      handler: 'CacheFirst',
      options: {
        cacheName: 'image-cache-v2',
        expiration: {
          maxEntries: 200,
          maxAgeSeconds: 60 * 60 * 24 * 30, // 30일
        },
      },
    },
    {
      urlPattern: /\.(?:js|css)$/,
      handler: 'StaleWhileRevalidate',
      options: {
        cacheName: 'static-resources-v2',
        expiration: {
          maxEntries: 100,
          maxAgeSeconds: 60 * 60 * 24 * 7, // 7일
        },
      },
    },
  ],
});

/** @type {import('next').NextConfig} */
const nextConfig = {
  assetPrefix:
    process.env.NODE_ENV === 'production'
      ? process.env.NEXT_PUBLIC_ASSET_PREFIX || ''
      : '',
  basePath: '',
  trailingSlash: false,
  poweredByHeader: false,
  compress: true,
  images: {
    domains: ['greensteel.site'],
    formats: ['image/webp', 'image/avif'],
    dangerouslyAllowSVG: true,
    contentSecurityPolicy: "default-src 'self'; script-src 'none'; sandbox;",
  },
  // experimental: {
  //   optimizeCss: true,
  // },
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
                     {
             key: 'Content-Security-Policy',
             value: `default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://dapi.kakao.com https://t1.daumcdn.net https://greensteel.site https://lca-final.vercel.app; style-src 'self' 'unsafe-inline' https://lca-final.vercel.app https://fonts.googleapis.com https://fonts.gstatic.com; img-src 'self' data: https: https://www.google-analytics.com https://greensteel.site https://lca-final.vercel.app; connect-src 'self' ${process.env.NEXT_PUBLIC_API_BASE_URL || 'https://api.greensteel.site'} http://localhost:8080 http://localhost:8083 https://www.google-analytics.com https://analytics.google.com https://dapi.kakao.com https://greensteel.site https://lca-final.vercel.app; font-src 'self' data: https://fonts.gstatic.com; frame-src 'self' https://greensteel.site https://postcode.map.daum.net;`,
           },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'Referrer-Policy',
            value: 'strict-origin-when-cross-origin',
          },
          {
            key: 'Permissions-Policy',
            value: 'camera=(), microphone=(), geolocation=()',
          },
        ],
      },
    ];
  },
  // API 프록시 설정
  async rewrites() {
    const GATEWAY_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://gateway-production-da31.up.railway.app';
    
    return [
      {
        source: '/api/v1/:path*',
        destination: `${GATEWAY_URL}/api/v1/:path*`,
      },
      {
        source: '/api/:path*',
        destination: `${GATEWAY_URL}/api/:path*`,
      },
    ];
  },
};

module.exports = withPWA(nextConfig);
