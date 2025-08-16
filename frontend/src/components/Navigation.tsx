'use client';

import { useAuth } from '@/app/contexts/AuthContext';
import ThemeToggle from './ThemeToggle';

// ============================================================================
// 🧭 네비게이션 컴포넌트
// ============================================================================

export default function Navigation() {
  const { user, isAuthenticated, logout } = useAuth();

  // ============================================================================
  // 🚪 로그아웃 처리
  // ============================================================================
  
  const handleLogout = () => {
    logout();
    // 홈페이지로 리다이렉트
    window.location.href = '/';
  };

  return (
    <nav className="bg-white dark:bg-gray-900 shadow-lg border-b border-gray-200 dark:border-gray-700 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* 로고 영역 */}
          <div className="flex items-center">
            <a
              href="/"
              className="flex-shrink-0 flex items-center hover:opacity-80 transition-opacity duration-200"
            >
              <div className="w-8 h-8 bg-blue-600 dark:bg-blue-500 rounded-lg flex items-center justify-center mr-3">
                <svg
                  className="w-5 h-5 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2zm0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
                  />
                </svg>
              </div>
              <h1 className="text-xl font-bold text-gray-900 dark:text-white transition-colors duration-200">
                CBAM Calculator
              </h1>
            </a>
          </div>

          {/* 네비게이션 링크 */}
          <div className="hidden sm:ml-6 sm:flex sm:items-center sm:space-x-8">
            <a
              href="/"
              className="border-transparent text-gray-500 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200"
            >
              Home
            </a>
            
            {isAuthenticated ? (
              // 로그인된 사용자 메뉴
              <>
                <a
                  href="/profile"
                  className="border-transparent text-gray-500 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200"
                >
                  Profile
                </a>
                <button
                  onClick={handleLogout}
                  className="border-transparent text-gray-500 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200 cursor-pointer"
                >
                  Logout
                </button>
              </>
            ) : (
              // 로그인되지 않은 사용자 메뉴
              <>
                <a
                  href="/login"
                  className="border-transparent text-gray-500 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200"
                >
                  SignIn
                </a>
                <a
                  href="/register"
                  className="border-transparent text-gray-500 dark:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-white inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors duration-200"
                >
                  SignUp
                </a>
              </>
            )}
          </div>

          {/* 우측 영역: 테마 토글 + 모바일 메뉴 */}
          <div className="flex items-center space-x-4">
            {/* 테마 토글 버튼 */}
            <ThemeToggle />
            
            {/* 모바일 메뉴 버튼 */}
            <div className="sm:hidden">
              <button
                type="button"
                className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 dark:text-gray-300 hover:text-gray-500 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors duration-200"
                aria-controls="mobile-menu"
                aria-expanded="false"
              >
                <span className="sr-only">메뉴 열기</span>
                <svg
                  className="block h-6 w-6"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  aria-hidden="true"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 모바일 메뉴 */}
      <div className="sm:hidden" id="mobile-menu">
        <div className="pt-2 pb-3 space-y-1 bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700">
          <a
            href="/"
            className="bg-blue-50 dark:bg-blue-900/20 border-blue-500 text-blue-700 dark:text-blue-300 block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200"
          >
            Home
          </a>
          
          {isAuthenticated ? (
            // 로그인된 사용자 모바일 메뉴
            <>
              <a
                href="/profile"
                className="border-transparent text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-white block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200"
              >
                Profile
              </a>
              <button
                onClick={handleLogout}
                className="w-full text-left border-transparent text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-white block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200 cursor-pointer"
              >
                Logout
              </button>
            </>
          ) : (
            // 로그인되지 않은 사용자 모바일 메뉴
            <>
              <a
                href="/login"
                className="border-transparent text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-white block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200"
              >
                SignIn
              </a>
              <a
                href="/register"
                className="border-transparent text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 hover:text-gray-700 dark:hover:text-white block pl-3 pr-4 py-2 border-l-4 text-base font-medium transition-colors duration-200"
              >
                SignUp
              </a>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
