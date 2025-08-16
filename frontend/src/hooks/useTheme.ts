'use client';

import { useState, useEffect } from 'react';

// ============================================================================
// 🎯 테마 타입 정의
// ============================================================================

export type Theme = 'light' | 'dark';

// ============================================================================
// 🌙 테마 관리 훅
// ============================================================================

export function useTheme() {
  const [theme, setTheme] = useState<Theme>('light');
  const [isLoading, setIsLoading] = useState(true);

  // ============================================================================
  // 🔧 테마 변경 함수
  // ============================================================================
  
  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    
    // 로컬 스토리지에 저장
    if (typeof window !== 'undefined') {
      localStorage.setItem('theme', newTheme);
      
      // HTML 요소에 테마 속성 설정
      document.documentElement.setAttribute('data-theme', newTheme);
      
      // 시스템 테마와 동기화
      if (newTheme === 'dark') {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  };

  // ============================================================================
  // 🔍 테마 감지 및 초기화
  // ============================================================================
  
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // 로컬 스토리지에서 저장된 테마 확인
    const savedTheme = localStorage.getItem('theme') as Theme;
    
    // 시스템 테마 감지
    const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    
    // 우선순위: 저장된 테마 > 시스템 테마 > 기본값(라이트)
    const initialTheme = savedTheme || systemTheme;
    
    setTheme(initialTheme);
    
    // HTML 요소에 테마 속성 설정
    document.documentElement.setAttribute('data-theme', initialTheme);
    
    if (initialTheme === 'dark') {
      document.documentElement.classList.add('dark');
    }
    
    setIsLoading(false);
  }, []);

  // ============================================================================
  // 👂 시스템 테마 변경 감지
  // ============================================================================
  
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      // 사용자가 직접 테마를 설정한 경우가 아니라면 시스템 테마를 따름
      if (!localStorage.getItem('theme')) {
        const newTheme = e.matches ? 'dark' : 'light';
        setTheme(newTheme);
        document.documentElement.setAttribute('data-theme', newTheme);
        
        if (newTheme === 'dark') {
          document.documentElement.classList.add('dark');
        } else {
          document.documentElement.classList.remove('dark');
        }
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // ============================================================================
  // 🎨 테마별 메타데이터 업데이트
  // ============================================================================
  
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // 테마 색상에 따른 메타 태그 업데이트
    const metaThemeColor = document.querySelector('meta[name="theme-color"]');
    if (metaThemeColor) {
      metaThemeColor.setAttribute('content', theme === 'dark' ? '#0f172a' : '#3b82f6');
    }

    // 다크모드일 때 추가 메타 태그 설정
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  return {
    theme,
    toggleTheme,
    isLoading,
    isDark: theme === 'dark'
  };
}
