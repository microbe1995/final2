export const env = {
  NEXT_PUBLIC_API_BASE_URL: 'https://gateway-production-22ef.up.railway.app', // 🔴 강제 기본값 사용
  NEXT_PUBLIC_ENV: process.env.NODE_ENV || 'development',
  NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || 'greensteel',
  NEXT_PUBLIC_APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION || '1.0.0',
  NEXT_PUBLIC_ENABLE_LCA: process.env.NEXT_PUBLIC_ENABLE_LCA === 'true',
  NEXT_PUBLIC_ENABLE_CBAM: process.env.NEXT_PUBLIC_ENABLE_CBAM === 'true',
  NEXT_PUBLIC_ENABLE_DATA_UPLOAD:
    process.env.NEXT_PUBLIC_ENABLE_DATA_UPLOAD === 'true',
} as const;

// 🔴 단순화: 항상 올바른 Gateway URL 사용
console.log('🚀 Frontend 환경 설정:', {
  API_BASE_URL: env.NEXT_PUBLIC_API_BASE_URL,
  ENV: env.NEXT_PUBLIC_ENV,
  NODE_ENV: process.env.NODE_ENV
});
