'use client';

import { useEffect, useState } from 'react';

// ============================================================================
// 🎯 Toast 타입 정의
// ============================================================================

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface ToastProps {
  id: string;
  type: ToastType;
  title: string;
  message?: string;
  duration?: number;
  onClose: (id: string) => void;
}

// ============================================================================
// 🎨 Toast 컴포넌트
// ============================================================================

export default function Toast({
  id,
  type,
  title,
  message,
  duration = 5000,
  onClose
}: ToastProps) {
  const [isVisible, setIsVisible] = useState(true);

  // ============================================================================
  // 🔧 타입별 아이콘 및 스타일
  // ============================================================================
  
  const toastConfig = {
    success: {
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
        </svg>
      ),
      bgColor: 'bg-[#16a34a]/10',
      borderColor: 'border-[#16a34a]/20',
      textColor: 'text-[#16a34a]',
      iconColor: 'text-[#16a34a]'
    },
    error: {
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
      ),
      bgColor: 'bg-[#dc2626]/10',
      borderColor: 'border-[#dc2626]/20',
      textColor: 'text-[#dc2626]',
      iconColor: 'text-[#dc2626]'
    },
    warning: {
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      ),
      bgColor: 'bg-[#d97706]/10',
      borderColor: 'border-[#d97706]/20',
      textColor: 'text-[#d97706]',
      iconColor: 'text-[#d97706]'
    },
    info: {
      icon: (
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      bgColor: 'bg-[#2563eb]/10',
      borderColor: 'border-[#2563eb]/20',
      textColor: 'text-[#2563eb]',
      iconColor: 'text-[#2563eb]'
    }
  };

  const config = toastConfig[type];

  // ============================================================================
  // ⏰ 자동 닫기 타이머
  // ============================================================================
  
  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [duration]);

  // ============================================================================
  // 🖱️ 닫기 처리
  // ============================================================================
  
  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => {
      onClose(id);
    }, 150); // 애니메이션 완료 후 제거
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <div
      className={`toast ${config.bgColor} border ${config.borderColor} rounded-lg shadow-lg transition-all duration-150 ${
        isVisible ? 'opacity-100 translate-x-0' : 'opacity-0 translate-x-full'
      }`}
      role="status"
      aria-live="polite"
      aria-atomic="true"
    >
      <div className="flex items-start p-4">
        {/* 아이콘 */}
        <div className={`flex-shrink-0 ${config.iconColor}`}>
          {config.icon}
        </div>

        {/* 콘텐츠 */}
        <div className="ml-3 flex-1">
          <h3 className={`text-sm font-medium ${config.textColor}`}>
            {title}
          </h3>
          {message && (
            <p className={`mt-1 text-sm ${config.textColor} opacity-90`}>
              {message}
            </p>
          )}
        </div>

        {/* 닫기 버튼 */}
        <button
          onClick={handleClose}
          className={`ml-4 flex-shrink-0 ${config.textColor} hover:opacity-70 transition-opacity`}
          aria-label="알림 닫기"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  );
}

// ============================================================================
// 🚀 Toast Manager Hook
// ============================================================================

export function useToast() {
  const [toasts, setToasts] = useState<ToastProps[]>([]);

  const addToast = (toast: Omit<ToastProps, 'id' | 'onClose'>) => {
    const id = Math.random().toString(36).substr(2, 9);
    const newToast: ToastProps = {
      ...toast,
      id,
      onClose: removeToast
    };

    setToasts(prev => [...prev, newToast]);
  };

  const removeToast = (id: string) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const showSuccess = (title: string, message?: string) => {
    addToast({ type: 'success', title, message });
  };

  const showError = (title: string, message?: string) => {
    addToast({ type: 'error', title, message });
  };

  const showWarning = (title: string, message?: string) => {
    addToast({ type: 'warning', title, message });
  };

  const showInfo = (title: string, message?: string) => {
    addToast({ type: 'info', title, message });
  };

  return {
    toasts,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeToast
  };
}
