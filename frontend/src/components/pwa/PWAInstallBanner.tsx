'use client';

import { useState, useEffect } from 'react';
import Button from '../atomic/atoms/Button';
import { X, Download, Smartphone } from 'lucide-react';

interface BeforeInstallPromptEvent extends Event {
  readonly platforms: string[];
  readonly userChoice: Promise<{
    outcome: 'accepted' | 'dismissed';
    platform: string;
  }>;
  prompt(): Promise<void>;
}

export default function PWAInstallBanner() {
  const [deferredPrompt, setDeferredPrompt] =
    useState<BeforeInstallPromptEvent | null>(null);
  const [showBanner, setShowBanner] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  useEffect(() => {
    // PWA 설치 이벤트 리스너
    const handleBeforeInstallPrompt = (e: Event) => {
      // preventDefault()를 제거하고 이벤트를 저장만 함
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setShowBanner(true);
    };

    // PWA 설치 완료 이벤트 리스너
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setShowBanner(false);
      localStorage.setItem('pwa-installed', 'true');
    };

    // 이미 설치되었는지 확인
    if (localStorage.getItem('pwa-installed') === 'true') {
      setIsInstalled(true);
    }

    // PWA 설치 가능 여부 확인
    if (window.matchMedia('(display-mode: standalone)').matches) {
      setIsStandalone(true);
      setIsInstalled(true);
    }

    // 모바일 기기에서 PWA 설치 안내
    const isMobile =
      /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(
        navigator.userAgent
      );
    if (isMobile && !isInstalled && !isStandalone) {
      // 모바일에서는 약간의 지연 후 배너 표시
      const timer = setTimeout(() => {
        if (!localStorage.getItem('pwa-banner-dismissed')) {
          setShowBanner(true);
        }
      }, 3000);
      return () => clearTimeout(timer);
    }

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener(
        'beforeinstallprompt',
        handleBeforeInstallPrompt
      );
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, [isInstalled, isStandalone]);

  const handleInstallClick = async () => {
    if (!deferredPrompt) {
      return;
    }

    try {
      // 설치 프롬프트 표시
      deferredPrompt.prompt();

      // 사용자 응답 대기
      const { outcome } = await deferredPrompt.userChoice;

      if (outcome === 'accepted') {
        // 사용자가 설치를 수락한 경우
        setShowBanner(false);
        localStorage.setItem('pwa-installed', 'true');
      }
    } catch (error) {
      // 에러 발생 시 배너 숨김
      setShowBanner(false);
    }

    // 프롬프트 초기화
    setDeferredPrompt(null);
  };

  const handleDismiss = () => {
    setShowBanner(false);
    localStorage.setItem('pwa-banner-dismissed', 'true');
  };

  const handleLearnMore = () => {
    // PWA 설치 방법 안내 페이지로 이동하거나 모달 표시
    window.open('https://web.dev/install-criteria/', '_blank');
  };

  // 이미 설치되었거나 배너를 닫았거나 표시하지 않음
  if (
    isInstalled ||
    isStandalone ||
    !showBanner ||
    localStorage.getItem('pwa-banner-dismissed') === 'true'
  ) {
    return null;
  }

  return (
    <div className='fixed bottom-4 left-4 right-4 md:left-auto md:right-4 md:w-96 z-50'>
      <div className='bg-gray-900 border border-gray-700 rounded-xl shadow-2xl p-6'>
        <div className='flex items-start space-x-4'>
          <div className='flex-shrink-0'>
            <div className='w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center'>
              <Smartphone className='w-6 h-6 text-white' />
            </div>
          </div>

          <div className='flex-1 min-w-0'>
            <h3 className='text-lg font-semibold text-white mb-1'>
              GreenSteel 앱 설치
            </h3>
            <p className='text-sm text-gray-300 leading-relaxed'>
              홈 화면에 추가하여 더 빠르게 접근하고 오프라인에서도 사용하세요
            </p>
          </div>

          <button
            onClick={handleDismiss}
            className='flex-shrink-0 text-gray-400 hover:text-gray-300 p-1 rounded-lg hover:bg-gray-800'
          >
            <X className='w-4 h-4' />
          </button>
        </div>

        <div className='mt-4 flex flex-col sm:flex-row gap-3'>
          {deferredPrompt ? (
            <Button
              onClick={handleInstallClick}
              className='flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-medium py-2.5 px-4 rounded-lg transition-all duration-200 transform hover:scale-105'
            >
              <Download className='h-4 w-4 mr-2' />
              설치하기
            </Button>
          ) : (
            <Button
              onClick={handleLearnMore}
              className='flex-1 bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white font-medium py-2.5 px-4 rounded-lg transition-all duration-200 transform hover:scale-105'
            >
              <Smartphone className='h-4 w-4 mr-2' />
              설치 방법 보기
            </Button>
          )}

          <Button
            onClick={handleDismiss}
            variant='outline'
            className='flex-1 py-2.5 px-4 border-gray-600 text-gray-300 hover:bg-gray-800 rounded-lg transition-all duration-200'
          >
            나중에
          </Button>
        </div>

        {/* PWA 기능 설명 */}
        <div className='mt-4 pt-4 border-t border-gray-700'>
          <div className='grid grid-cols-2 gap-3 text-xs'>
            <div className='flex items-center gap-2 text-gray-400'>
              <div className='w-2 h-2 bg-green-500 rounded-full'></div>
              오프라인 지원
            </div>
            <div className='flex items-center gap-2 text-gray-400'>
              <div className='w-2 h-2 bg-blue-500 rounded-full'></div>
              빠른 로딩
            </div>
            <div className='flex items-center gap-2 text-gray-400'>
              <div className='w-2 h-2 bg-purple-500 rounded-full'></div>홈 화면
              추가
            </div>
            <div className='flex items-center gap-2 text-gray-400'>
              <div className='w-2 h-2 bg-orange-500 rounded-full'></div>
              푸시 알림
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
