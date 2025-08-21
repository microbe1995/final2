'use client';

import React, { useState, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import { env } from '@/lib/env';
import {
  Menu,
  X,
  Home,
  BarChart3,
  FileText,
  Upload,
  Settings,
  ChevronDown,
  User,
  LogOut,
  Bell,
  Search,
} from 'lucide-react';

interface CommonShellProps {
  children: React.ReactNode;
}

const CommonShell: React.FC<CommonShellProps> = ({ children }) => {
  const pathname = usePathname();
  const router = useRouter();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);

  const navigation = [
    {
      name: '홈',
      href: '/dashboard',
      icon: Home,
      current: pathname === '/dashboard',
      description: 'ESG 요약 및 최근 활동',
    },
    {
      name: 'LCA',
      href: '/lca',
      icon: BarChart3,
      current: pathname.startsWith('/lca'),
      description: '생명주기 평가 프로젝트 관리',
    },
    {
      name: 'CBAM',
      href: '/cbam',
      icon: FileText,
      current: pathname.startsWith('/cbam'),
      description: 'CBAM 보고서 및 계산',
    },
    {
      name: '데이터 업로드',
      href: '/data-upload',
      icon: Upload,
      current: pathname === '/data-upload',
      description: 'ESG 데이터 업로드 및 관리',
    },
    {
      name: '설정',
      href: '/settings',
      icon: Settings,
      current: pathname === '/settings',
      description: '계정 및 환경설정',
    },
  ];

  const handleNavigation = (href: string) => {
    router.push(href);
    setIsSidebarOpen(false);
    setIsMobileMenuOpen(false);
  };

  const handleGoHome = () => {
    router.push('/');
  };

  // 모바일에서 사이드바 외부 클릭 시 닫기
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (isSidebarOpen && !target.closest('.sidebar')) {
        setIsSidebarOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isSidebarOpen]);

  // 경로 변경 시 모바일 메뉴 닫기
  useEffect(() => {
    setIsMobileMenuOpen(false);
    setIsSidebarOpen(false);
  }, [pathname]);

  return (
    <div className='min-h-screen bg-ecotrace-background text-ecotrace-text'>
      {/* 헤더 */}
      <header className='border-b border-ecotrace-border bg-ecotrace-background/95 backdrop-blur-sm sticky top-0 z-50'>
        <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-4'>
          <div className='flex items-center justify-between'>
            {/* 로고 및 브랜드 */}
            <div className='flex items-center gap-4'>
              <button
                onClick={() => setIsSidebarOpen(!isSidebarOpen)}
                className='lg:hidden p-2 rounded-lg hover:bg-ecotrace-secondary/10'
              >
                <Menu className='w-5 h-5' />
              </button>

              <div className='w-8 h-8 bg-gradient-to-br from-ecotrace-accent to-ecotrace-accent/70 rounded-lg flex items-center justify-center'>
                <svg
                  className='w-5 h-5 text-white'
                  fill='none'
                  stroke='currentColor'
                  viewBox='0 0 24 24'
                >
                  <path
                    strokeLinecap='round'
                    strokeLinejoin='round'
                    strokeWidth={2}
                    d='M13 10V3L4 14h7v7l9-11h-7z'
                  />
                </svg>
              </div>
              <div className='flex flex-col'>
                <span className='text-xl font-bold text-white'>
                  {env.NEXT_PUBLIC_APP_NAME}
                </span>
                <span className='text-xs text-ecotrace-textSecondary'>
                  ESG Platform
                </span>
              </div>
            </div>

            {/* 데스크톱 네비게이션 */}
            <nav className='hidden lg:flex items-center gap-6'>
              {navigation.map(item => (
                <button
                  key={item.name}
                  onClick={() => handleNavigation(item.href)}
                  className={cn(
                    'text-sm font-medium transition-all duration-200 px-3 py-2 rounded-lg cursor-pointer flex items-center gap-2',
                    item.current
                      ? 'text-ecotrace-text bg-ecotrace-secondary/20 border border-ecotrace-accent/30'
                      : 'text-ecotrace-textSecondary hover:text-ecotrace-text hover:bg-ecotrace-secondary/10'
                  )}
                >
                  <item.icon className='w-4 h-4' />
                  {item.name}
                </button>
              ))}
            </nav>

            {/* 우측 액션 */}
            <div className='flex items-center gap-4'>
              {/* 검색 */}
              <button className='p-2 rounded-lg hover:bg-ecotrace-secondary/10'>
                <Search className='w-5 h-5' />
              </button>

              {/* 알림 */}
              <button className='p-2 rounded-lg hover:bg-ecotrace-secondary/10 relative'>
                <Bell className='w-5 h-5' />
                <span className='absolute -top-1 -right-1 w-3 h-3 bg-red-500 rounded-full'></span>
              </button>

              {/* 프로필 드롭다운 */}
              <div className='relative'>
                <button
                  onClick={() =>
                    setIsProfileDropdownOpen(!isProfileDropdownOpen)
                  }
                  className='flex items-center gap-2 p-2 rounded-lg hover:bg-ecotrace-secondary/10'
                >
                  <div className='w-8 h-8 bg-ecotrace-accent rounded-full flex items-center justify-center'>
                    <User className='w-4 h-4 text-white' />
                  </div>
                  <ChevronDown className='w-4 h-4' />
                </button>

                {isProfileDropdownOpen && (
                  <div className='absolute right-0 mt-2 w-48 bg-ecotrace-secondary border border-ecotrace-border rounded-lg shadow-lg py-2'>
                    <button
                      onClick={() => handleNavigation('/settings')}
                      className='w-full px-4 py-2 text-left hover:bg-ecotrace-secondary/50 flex items-center gap-2'
                    >
                      <Settings className='w-4 h-4' />
                      설정
                    </button>
                    <button
                      onClick={handleGoHome}
                      className='w-full px-4 py-2 text-left hover:bg-ecotrace-secondary/50 flex items-center gap-2'
                    >
                      <LogOut className='w-4 h-4' />
                      홈으로
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className='flex'>
        {/* 사이드바 */}
        <div
          className={cn(
            'fixed inset-y-0 left-0 z-40 w-64 bg-ecotrace-secondary border-r border-ecotrace-border transform transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0 sidebar',
            isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
          )}
        >
          <div className='flex flex-col h-full'>
            {/* 사이드바 헤더 */}
            <div className='flex items-center justify-between p-4 border-b border-ecotrace-border'>
              <h2 className='text-lg font-semibold text-white'>메뉴</h2>
              <button
                onClick={() => setIsSidebarOpen(false)}
                className='lg:hidden p-1 rounded-lg hover:bg-ecotrace-secondary/50'
              >
                <X className='w-5 h-5' />
              </button>
            </div>

            {/* 사이드바 네비게이션 */}
            <nav className='flex-1 p-4 space-y-2'>
              {navigation.map(item => (
                <button
                  key={item.name}
                  onClick={() => handleNavigation(item.href)}
                  className={cn(
                    'w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center gap-3 group',
                    item.current
                      ? 'bg-ecotrace-accent text-white'
                      : 'text-ecotrace-textSecondary hover:text-white hover:bg-ecotrace-secondary/50'
                  )}
                >
                  <item.icon
                    className={cn(
                      'w-5 h-5',
                      item.current
                        ? 'text-white'
                        : 'text-ecotrace-textSecondary group-hover:text-white'
                    )}
                  />
                  <div className='flex-1'>
                    <div className='font-medium'>{item.name}</div>
                    <div className='text-xs opacity-75'>{item.description}</div>
                  </div>
                </button>
              ))}
            </nav>

            {/* 사이드바 푸터 */}
            <div className='p-4 border-t border-ecotrace-border'>
              <div className='text-xs text-ecotrace-textSecondary text-center'>
                GreenSteel v1.0.0
              </div>
            </div>
          </div>
        </div>

        {/* 메인 컨텐츠 */}
        <main className='flex-1 lg:ml-0'>
          <div className='mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8'>
            {children}
          </div>
        </main>
      </div>

      {/* 모바일 메뉴 오버레이 */}
      {isSidebarOpen && (
        <div className='fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden' />
      )}
    </div>
  );
};

export default CommonShell;
