'use client';

import { useEffect, useRef } from 'react';

// ============================================================================
// 🎯 Modal 컴포넌트 Props 타입
// ============================================================================

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  showCloseButton?: boolean;
}

// ============================================================================
// 🎨 Modal 컴포넌트
// ============================================================================

export default function Modal({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);

  // ============================================================================
  // 🔧 사이즈별 스타일 매핑
  // ============================================================================
  
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl'
  };

  // ============================================================================
  // 🎯 접근성 및 키보드 네비게이션
  // ============================================================================
  
  useEffect(() => {
    if (isOpen) {
      // 이전 포커스 요소 저장
      previousFocusRef.current = document.activeElement as HTMLElement;
      
      // 모달 내부로 포커스 이동
      const focusableElements = modalRef.current?.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
      );
      
      if (focusableElements && focusableElements.length > 0) {
        (focusableElements[0] as HTMLElement).focus();
      }
      
      // ESC 키 이벤트 리스너
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') {
          onClose();
        }
      };
      
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden'; // 스크롤 방지
      
      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.body.style.overflow = 'unset';
        
        // 이전 포커스로 복원
        if (previousFocusRef.current) {
          previousFocusRef.current.focus();
        }
      };
    }
  }, [isOpen, onClose]);

  // ============================================================================
  // 🖱️ 클릭 이벤트 처리
  // ============================================================================
  
  const handleBackdropClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  // ============================================================================
  // 🚫 모달이 닫혀있으면 렌더링하지 않음
  // ============================================================================
  
  if (!isOpen) return null;

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <div
      className="modal-overlay"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
    >
      <div
        ref={modalRef}
        className={`modal-content ${sizeClasses[size]}`}
        role="document"
      >
        {/* 헤더 */}
        <div className="flex items-center justify-between p-6 border-b border-[#334155]">
          <h2
            id="modal-title"
            className="text-xl font-semibold text-[#ffffff]"
          >
            {title}
          </h2>
          
          {showCloseButton && (
            <button
              onClick={onClose}
              className="p-2 text-[#94a3b8] hover:text-[#cbd5e1] hover:bg-[#1e293b] rounded-lg transition-colors"
              aria-label="모달 닫기"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          )}
        </div>

        {/* 콘텐츠 */}
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
}
