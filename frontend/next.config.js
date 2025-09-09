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
    domains: ['envioatlas.cloud', 'greensteel.site'],
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
            value: `default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://dapi.kakao.com https://t1.daumcdn.net http://envioatlas.cloud https://envioatlas.cloud https://greensteel.site; style-src 'self' 'unsafe-inline'; img-src 'self' data: https: http: https://www.google-analytics.com http://envioatlas.cloud https://envioatlas.cloud https://greensteel.site; connect-src 'self' https://gateway-production-22ef.up.railway.app https://lcafinal-production.up.railway.app https://*.up.railway.app https://www.google-analytics.com https://analytics.google.com https://dapi.kakao.com http://envioatlas.cloud https://envioatlas.cloud https://greensteel.site; font-src 'self' data:; frame-src 'self' http://envioatlas.cloud https://envioatlas.cloud https://greensteel.site https://postcode.map.daum.net;`,
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
};

// 🔴 PWA 플러그인 완전 제거 (CORS 문제 해결 후 재활성화)
module.exports = nextConfig;
