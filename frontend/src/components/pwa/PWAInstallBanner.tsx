'use client';

import { useEffect } from 'react';

export default function PWAInstallBanner() {
  // 🔴 PWA Install Banner 완전 비활성화 (CORS 문제 해결 후 재활성화)
  useEffect(() => {
    console.log('🚫 PWA Install Banner 완전 비활성화됨');
    console.log('💡 CORS 문제 해결 후 재활성화 예정');
  }, []);

  // 🔴 완전히 렌더링하지 않음
  return null;
}
