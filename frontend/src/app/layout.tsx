// ============================================================================
// 📦 필요한 모듈 import
// ============================================================================

import type { Metadata } from 'next';
import './globals.css';
import AppTopNavigation from '@/components/organisms/AppTopNavigation';

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
  
  // PWA 관련 메타데이터
  applicationName: 'CBAM Calculator',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'CBAM Calculator',
  },
  
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
      
      <body className="h-full bg-[#0b0c0f] transition-colors duration-200">
        <div className="flex flex-col min-h-screen">
          <AppTopNavigation />
          <main className="min-h-screen bg-[#0b0c0f] transition-colors duration-200">
            {children}
          </main>
          <footer className="bg-[#1e293b] border-t border-[#334155] mt-auto transition-colors duration-200">
            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
              <div className="text-center">
                <p className="text-gray-500 text-sm transition-colors duration-200">
                  © 2024 CBAM Calculator. 모든 권리 보유.
                </p>
                <p className="text-gray-400 text-xs mt-2 transition-colors duration-200">
                  공정도 관리 시스템
                </p>
              </div>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
} 