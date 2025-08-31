'use client';

import { useEffect } from 'react';

export default function PWAServiceWorker() {
  // 🔴 PWA Service Worker 완전 비활성화 (CORS 문제 해결 후 재활성화)
  useEffect(() => {
    // 개발/디버그 동안 SW 완전 해제
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      // 기존 서비스워커 등록 해제
      navigator.serviceWorker.getRegistrations().then((registrations) => {
        for (const registration of registrations) {
          registration.unregister();
          console.log('🚫 PWA Service Worker 등록 해제됨:', registration.scope);
        }
      });
      
      // 서비스워커 완전 비활성화
      console.log('🚫 PWA Service Worker 완전 비활성화됨');
      console.log('💡 개발/디버그 동안 SW 해제 방법:');
      console.log('   1. 브라우저 DevTools → Application 탭');
      console.log('   2. Service Workers → Unregister');
      console.log('   3. Storage → Clear site data');
    }
  }, []);

  return null; // 이 컴포넌트는 UI를 렌더링하지 않음
}
