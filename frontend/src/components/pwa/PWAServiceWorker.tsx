'use client';

import { useEffect } from 'react';

export default function PWAServiceWorker() {
  // 🔴 PWA Service Worker 완전 비활성화 (CORS 문제 해결 후 재활성화)
  useEffect(() => {
    // 아무것도 하지 않음
    console.log('🚫 PWA Service Worker 비활성화됨');
  }, []);

  return null; // 이 컴포넌트는 UI를 렌더링하지 않음
}
