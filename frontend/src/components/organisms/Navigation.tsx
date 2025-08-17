'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/zustand/authStore';

// ============================================================================
// 🎯 Navigation 컴포넌트
// ============================================================================

const Navigation: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
  };

  return (
    <nav className="bg-[#1e293b] dark:bg-gray-900 shadow-lg border-b border-[#334155] dark:border-gray-700 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-20"> {/* 높이를 h-16에서 h-20으로 증가 */}
          {/* 로고 및 브랜드 */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-white font-bold text-lg">C</span>
              </div>
              <span className="text-white font-bold text-xl">CBAM Calculator</span>
            </Link>
          </div>

          {/* 데스크톱 네비게이션 */}
          <div className="hidden sm:flex sm:items-center sm:space-x-8">
            <Link
              href="/"
              className="text-white hover:text-blue-300 px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
            >
              Home
            </Link>
            
            <Link
              href="/process-flow"
              className="text-white hover:text-blue-300 px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
            >
              공정도
            </Link>
            
            {user && (
              <Link
                href="/profile"
                className="text-white hover:text-blue-300 px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
              >
                {user.full_name}
              </Link>
            )}
            
            <button
              onClick={handleLogout}
              className="text-white hover:text-red-300 px-3 py-2 rounded-md text-base font-medium transition-colors duration-200"
            >
              로그아웃
            </button>
          </div>

          {/* 모바일 메뉴 버튼 */}
          <div className="sm:hidden">
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="text-white hover:text-blue-300 p-2 rounded-md text-base font-medium focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors duration-200"
            >
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {isMobileMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* 모바일 메뉴 */}
      <div className="sm:hidden" id="mobile-menu">
        <div className="pt-2 pb-3 space-y-1 bg-[#1e293b] dark:bg-gray-900 border-t border-[#334155] dark:border-gray-700">
          <a
            href="/"
            className="border-transparent text-white hover:bg-[#334155] dark:hover:bg-gray-800 hover:border-[#475569] dark:hover:border-gray-600 hover:text-blue-300 dark:hover:text-white block pl-3 pr-4 py-3 border-l-4 text-base font-medium transition-colors duration-200"
          >
            Home
          </a>
          
          <a
            href="/process-flow"
            className="border-transparent text-white hover:bg-[#334155] dark:hover:bg-gray-800 hover:border-[#475569] dark:hover:border-gray-600 hover:text-blue-300 dark:hover:text-white block pl-3 pr-4 py-3 border-l-4 text-base font-medium transition-colors duration-200"
          >
            공정도
          </a>
          
          {user && (
            <a
              href="/profile"
              className="border-transparent text-white hover:bg-[#334155] dark:hover:bg-gray-800 hover:border-[#475569] dark:hover:border-gray-600 hover:text-blue-300 dark:hover:text-white block pl-3 pr-4 py-3 border-l-4 text-base font-medium transition-colors duration-200"
            >
              {user.full_name}
            </a>
          )}
          
          <button
            onClick={handleLogout}
            className="border-transparent text-white hover:bg-[#334155] dark:hover:bg-gray-800 hover:border-[#475569] dark:hover:border-gray-600 hover:text-red-300 dark:hover:text-red-300 block pl-3 pr-4 py-3 border-l-4 text-base font-medium transition-colors duration-200 w-full text-left"
          >
            로그아웃
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
