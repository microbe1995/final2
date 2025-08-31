const withPWA = require('next-pwa')({
  dest: 'public',
  register: true,
  skipWaiting: true,
  disable: true, // 🔴 임시로 PWA 완전 비활성화 (CORS 문제 해결 후 재활성화)
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
    // 🔴 API 캐싱 제거 (CORS 문제 해결 후 재활성화)
    // {
    //   urlPattern: /^https:\/\/gateway-production-22ef\.up\.railway\.app/,
    //   handler: 'NetworkFirst',
    //   options: {
    //     cacheName: 'gateway-api-cache-v2',
    //     expiration: {
    //       maxEntries: 100,
    //       maxAgeSeconds: 60 * 60 * 24,
    //     },
    //     cacheableResponse: {
    //       statuses: [0, 200],
    //     },
    //   },
    // },
    // {
    //   urlPattern: /^https:\/\/www\.greensteel\.site/,
    //   handler: 'NetworkFirst',
    //   options: {
    //     cacheName: 'greensteel-api-cache-v2',
    //     expiration: {
    //       maxEntries: 100,
    //       maxAgeSeconds: 60 * 60 * 24,
    //     },
    //     cacheableResponse: {
    //       statuses: [0, 200],
    //       },
    //     },
    //   },
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
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: `default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://dapi.kakao.com https://t1.daumcdn.net https://greensteel.site; style-src 'self' 'unsafe-inline'; img-src 'self' data: https: https://www.google-analytics.com https://greensteel.site; connect-src 'self' https://gateway-production-22ef.up.railway.app https://lcafinal-production.up.railway.app https://*.up.railway.app https://www.google-analytics.com https://analytics.google.com https://dapi.kakao.com https://greensteel.site; font-src 'self' data:; frame-src 'self' https://greensteel.site https://postcode.map.daum.net;`,
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
  // 🔴 API 프록시 설정 제거 (Vercel에서 처리)
  // async rewrites() {
  //   // Vercel에서 API 프록시 처리
  //   return [];
  // },
};

module.exports = withPWA(nextConfig);
