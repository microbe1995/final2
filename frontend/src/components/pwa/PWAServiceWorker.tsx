'use client';

import { useEffect } from 'react';

export default function PWAServiceWorker() {
  useEffect(() => {
    // 🔴 임시로 PWA Service Worker 비활성화 (CORS 문제 해결 후 재활성화)
    if (false && typeof window !== 'undefined' && 'serviceWorker' in navigator) {
      // 서비스 워커 등록
      const registerSW = async () => {
        try {
          const registration = await navigator.serviceWorker.register(
            '/sw.js',
            {
              scope: '/',
            }
          );

          // 서비스 워커 등록 성공

          // 서비스 워커 업데이트 확인
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (
                  newWorker.state === 'installed' &&
                  navigator.serviceWorker.controller
                ) {
                  // 새로운 서비스 워커가 설치되었을 때 사용자에게 알림
                  if (
                    confirm(
                      '새로운 버전이 사용 가능합니다. 새로고침하시겠습니까?'
                    )
                  ) {
                    window.location.reload();
                  }
                }
              });
            }
          });

          // 서비스 워커가 제어권을 가졌을 때
        } catch (error) {
          // 서비스 워커 등록 실패 시 무시
        }
      };

      registerSW();

      // 서비스 워커 메시지 수신
      const handleMessage = (event: MessageEvent) => {
        if (event.data && event.data.type === 'SKIP_WAITING') {
          window.location.reload();
        }
      };

      navigator.serviceWorker.addEventListener('message', handleMessage);

      return () => {
        navigator.serviceWorker.removeEventListener('message', handleMessage);
      };
    }
  }, []);

  return null; // 이 컴포넌트는 UI를 렌더링하지 않음
}
