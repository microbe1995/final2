// ============================================================================
// 📦 필요한 모듈 import
// ============================================================================

import type { Metadata } from 'next';
import './globals.css';
import ThemeToggle from '../components/ThemeToggle';
import Navigation from '../components/Navigation';
import { AuthProvider } from './contexts/AuthContext';

// ============================================================================
// 🎯 메타데이터 설정
// ============================================================================

export const metadata: Metadata = {
  title: 'CBAM Calculator - 사용자 계정 관리 시스템',
  description: 'CBAM Calculator의 사용자 계정 관리 시스템입니다. 안전하고 편리한 회원가입과 로그인을 제공합니다.',
  keywords: 'CBAM, Calculator, 사용자관리, 회원가입, 로그인, PostgreSQL',
  authors: [{ name: 'CBAM Calculator Team' }],
  creator: 'CBAM Calculator',
  publisher: 'CBAM Calculator',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  
  // PWA 메타데이터
  manifest: '/manifest.json',
  themeColor: '#3b82f6',
  colorScheme: 'light dark',
  
  // Open Graph
  openGraph: {
    type: 'website',
    locale: 'ko_KR',
    url: 'https://cbam-calculator.com',
    title: 'CBAM Calculator - 사용자 계정 관리 시스템',
    description: '안전하고 편리한 사용자 계정 관리 시스템',
    siteName: 'CBAM Calculator',
  },
  
  // Twitter
  twitter: {
    card: 'summary_large_image',
    title: 'CBAM Calculator - 사용자 계정 관리 시스템',
    description: '안전하고 편리한 사용자 계정 관리 시스템',
  },
  
  // 아이콘
  icons: {
    icon: [
      { url: '/favicon.ico' },
      { url: '/icon-192x192.png', sizes: '192x192', type: 'image/png' },
      { url: '/icon-512x512.png', sizes: '512x512', type: 'image/png' },
    ],
    apple: [
      { url: '/icon-192x192.png', sizes: '192x192', type: 'image/png' },
    ],
  },
  
  // 뷰포트
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
  },
  
  // 기타
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

// ============================================================================
// 🎨 네비게이션 컴포넌트
// ============================================================================

// 중복 Navigation 함수 - 사용하지 않음 (별도 파일로 분리됨)
function OldNavigation() {
  return (
    <nav className="bg-white dark:bg-gray-900 shadow-lg border-b border-gray-200 dark:border-gray-700 transition-colors duration-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* 로고 및 브랜드 */}
          <div className="flex items-center">
            <a href="/" className="flex-shrink-0 flex items-center hover:opacity-80 transition-opacity duration-200">
              <div className="w-8 h-8 bg-blue-600 dark:bg-blue-500 rounded-lg flex items-center justify-center mr-3">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
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
        </div>
      </div>
    </nav>
  );
}

// ============================================================================
// 🎨 루트 레이아웃 컴포넌트
// ============================================================================

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="ko" className="h-full">
      <head>
        {/* PWA 관련 메타 태그 */}
        <meta name="application-name" content="CBAM Calculator" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="CBAM Calculator" />
        <meta name="description" content="CBAM Calculator 사용자 계정 관리 시스템" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="msapplication-TileColor" content="#3b82f6" />
        <meta name="msapplication-tap-highlight" content="no" />
        
        {/* 폰트 최적화 */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      
      <body className="h-full bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
        <AuthProvider>
          {/* 네비게이션 */}
          <Navigation />
          
          {/* 메인 콘텐츠 */}
          <main className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
            {children}
          </main>
          
          {/* 푸터 */}
          <footer className="bg-white dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 mt-auto transition-colors duration-200">
            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
              <div className="text-center">
                <p className="text-gray-500 dark:text-gray-400 text-sm transition-colors duration-200">
                  © 2024 CBAM Calculator. 모든 권리 보유.
                </p>
                <p className="text-gray-400 dark:text-gray-500 text-xs mt-2 transition-colors duration-200">
                  PostgreSQL 기반 안전한 사용자 데이터 관리
                </p>
              </div>
            </div>
          </footer>
        </AuthProvider>
      </body>
    </html>
  );
} 