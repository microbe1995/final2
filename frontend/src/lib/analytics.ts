// Google Analytics 추적 유틸리티

declare global {
  interface Window {
    gtag: (
      command: 'config' | 'event' | 'js' | 'set',
      targetId: string,
      config?: Record<string, unknown>
    ) => void;
    dataLayer: unknown[];
  }
}

// 페이지 뷰 추적
export const trackPageView = (url: string, title?: string) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('config', 'G-2GFHCRYLT8', {
      page_path: url,
      page_title: title,
    });
  }
};

// 이벤트 추적
export const trackEvent = (
  action: string,
  category: string,
  label?: string,
  value?: number
) => {
  if (typeof window !== 'undefined' && window.gtag) {
    window.gtag('event', action, {
      event_category: category,
      event_label: label,
      value: value,
    });
  }
};

// 사용자 로그인 추적
export const trackLogin = (method: string) => {
  trackEvent('login', 'authentication', method);
};

// 사용자 회원가입 추적
export const trackSignUp = (method: string) => {
  trackEvent('sign_up', 'authentication', method);
};

// 파일 업로드 추적
export const trackFileUpload = (fileType: string, fileSize: number) => {
  trackEvent('file_upload', 'data_management', fileType, fileSize);
};

// 페이지 방문 추적
export const trackPageVisit = (pageName: string) => {
  trackEvent('page_view', 'navigation', pageName);
};

// 에러 추적
export const trackError = (errorMessage: string, errorCode?: string) => {
  trackEvent(
    'error',
    'system',
    errorMessage,
    errorCode ? parseInt(errorCode) : undefined
  );
};
