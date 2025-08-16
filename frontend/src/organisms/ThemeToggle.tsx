'use client';

import { useTheme } from '../hooks/useTheme';

// ============================================================================
// 🌙 테마 토글 버튼 컴포넌트
// ============================================================================

export default function ThemeToggle() {
  const { theme, toggleTheme, isLoading } = useTheme();

  // ============================================================================
  // 🚫 로딩 중일 때는 렌더링하지 않음
  // ============================================================================
  
  if (isLoading) {
    return (
      <div className="w-10 h-10 rounded-lg bg-gray-200 animate-pulse"></div>
    );
  }

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <button
      onClick={toggleTheme}
      className="relative p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-all duration-200 group"
      aria-label={`${theme === 'light' ? '다크모드' : '라이트모드'}로 전환`}
      title={`${theme === 'light' ? '다크모드' : '라이트모드'}로 전환`}
    >
      {/* 라이트모드 아이콘 */}
      <svg
        className={`w-5 h-5 text-yellow-500 transition-all duration-300 ${
          theme === 'light' 
            ? 'opacity-100 rotate-0 scale-100' 
            : 'opacity-0 rotate-90 scale-75 absolute'
        }`}
        fill="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.894a.75.75 0 001.06-1.06l-1.591-1.59a.75.75 0 10-1.061 1.06l1.59 1.591zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06 1.06l1.591-1.59a.75.75 0 10-1.06-1.061l-1.591 1.59zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.158 17.834a.75.75 0 011.06 0l1.591 1.591a.75.75 0 11-1.06 1.06l-1.591-1.59a.75.75 0 010-1.061zM2.25 12a.75.75 0 01.75-.75H5.25a.75.75 0 010 1.5H3a.75.75 0 01-.75-.75zM6.166 7.158a.75.75 0 010 1.06L4.575 8.757a.75.75 0 01-1.06-1.06l1.591-1.591a.75.75 0 011.06 0z" />
      </svg>

      {/* 다크모드 아이콘 */}
      <svg
        className={`w-5 h-5 text-blue-400 transition-all duration-300 ${
          theme === 'dark' 
            ? 'opacity-100 rotate-0 scale-100' 
            : 'opacity-0 -rotate-90 scale-75 absolute'
        }`}
        fill="currentColor"
        viewBox="0 0 24 24"
        aria-hidden="true"
      >
        <path d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" />
      </svg>

      {/* 호버 효과 */}
      <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-yellow-400/20 to-blue-400/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
      
      {/* 툴팁 */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 text-xs text-white bg-gray-900 rounded opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap">
        {theme === 'light' ? '다크모드로 전환' : '라이트모드로 전환'}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900" />
      </div>
    </button>
  );
}

// ============================================================================
// 🎨 간단한 토글 버튼 (모바일용)
// ============================================================================

export function SimpleThemeToggle() {
  const { theme, toggleTheme, isLoading } = useTheme();

  if (isLoading) {
    return (
      <div className="w-8 h-8 rounded bg-gray-200 animate-pulse"></div>
    );
  }

  return (
    <button
      onClick={toggleTheme}
      className="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-200"
      aria-label={`${theme === 'light' ? '다크모드' : '라이트모드'}로 전환`}
    >
      {theme === 'light' ? (
        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
        </svg>
      ) : (
        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
        </svg>
      )}
    </button>
  );
}
