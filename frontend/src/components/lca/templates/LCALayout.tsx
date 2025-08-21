'use client';

import React, { useState, useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  Menu,
  X,
  BarChart3,
  FileText,
  TrendingUp,
  Database,
  Zap,
  CheckCircle,
  FolderOpen,
  Settings,
  Plus,
  User,
  LogOut,
  Bell,
  Search,
  ChevronDown,
} from 'lucide-react';

interface LCALayoutProps {
  children: React.ReactNode;
}

const LCALayout: React.FC<LCALayoutProps> = ({ children }) => {
  const pathname = usePathname();
  const router = useRouter();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);

  const navigationItems = [
    {
      name: 'LCA 대시보드',
      href: '/lca',
      icon: BarChart3,
      description: 'LCA 프로젝트 개요 및 통계',
      isMain: true,
    },
    {
      name: '프로젝트 관리',
      href: '/lca/projects',
      icon: FolderOpen,
      description: 'LCA 프로젝트 생성 및 관리',
      isMain: true,
    },
    {
      name: '프로젝트 스코프',
      href: '/lca/projects/new/scope',
      icon: FileText,
      description: '프로젝트 목적과 분석 범위 정의',
      isSub: true,
    },
    {
      name: '생명주기 인벤토리',
      href: '/lca/projects/new/lci',
      icon: Database,
      description: 'LCI 데이터 입력 및 관리',
      isSub: true,
    },
    {
      name: '생명주기 영향평가',
      href: '/lca/projects/new/lcia',
      icon: Zap,
      description: 'LCIA 실행 및 결과 분석',
      isSub: true,
    },
    {
      name: '결과 해석',
      href: '/lca/projects/new/interpretation',
      icon: TrendingUp,
      description: 'LCA 결과 해석 및 결론',
      isSub: true,
    },
    {
      name: '보고서 생성',
      href: '/lca/projects/new/report',
      icon: CheckCircle,
      description: 'LCA 보고서 생성 및 관리',
      isSub: true,
    },
    {
      name: 'LCA 설정',
      href: '/lca/settings',
      icon: Settings,
      description: 'LCA 관련 설정 및 구성',
      isMain: true,
    },
  ];

  const mainItems = navigationItems.filter(item => item.isMain);
  const subItems = navigationItems.filter(item => item.isSub);

  const handleNavigation = (href: string) => {
    router.push(href);
    setIsSidebarOpen(false);
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
                <span className='text-xl font-bold text-white'>GreenSteel</span>
                <span className='text-xs text-ecotrace-textSecondary'>
                  LCA Platform
                </span>
              </div>
            </div>

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
              <h2 className='text-lg font-semibold text-white'>LCA 관리</h2>
              <button
                onClick={() => setIsSidebarOpen(false)}
                className='lg:hidden p-1 rounded-lg hover:bg-ecotrace-secondary/50'
              >
                <X className='w-5 h-5' />
              </button>
            </div>

            {/* 새 프로젝트 버튼 */}
            <div className='p-4 border-b border-ecotrace-border'>
              <button
                onClick={() => handleNavigation('/lca/projects/new/scope')}
                className='w-full flex items-center gap-3 px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors'
              >
                <Plus className='w-5 h-5' />
                <span className='font-medium'>새 프로젝트</span>
              </button>
            </div>

            {/* 사이드바 네비게이션 */}
            <nav className='flex-1 p-4 space-y-2 overflow-y-auto'>
              {/* 메인 메뉴 */}
              <div className='mb-6'>
                <h3 className='text-xs font-semibold text-ecotrace-textSecondary uppercase tracking-wider mb-3 px-2'>
                  메인
                </h3>
                <div className='space-y-1'>
                  {mainItems.map(item => (
                    <button
                      key={item.name}
                      onClick={() => handleNavigation(item.href)}
                      className={cn(
                        'w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center gap-3 group',
                        pathname === item.href
                          ? 'bg-ecotrace-accent text-white'
                          : 'text-ecotrace-textSecondary hover:text-white hover:bg-ecotrace-secondary/50'
                      )}
                    >
                      <item.icon
                        className={cn(
                          'w-5 h-5',
                          pathname === item.href
                            ? 'text-white'
                            : 'text-ecotrace-textSecondary group-hover:text-white'
                        )}
                      />
                      <div className='flex-1'>
                        <div className='font-medium'>{item.name}</div>
                        <div className='text-xs opacity-75'>
                          {item.description}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>

              {/* LCA 워크플로우 */}
              <div>
                <h3 className='text-xs font-semibold text-ecotrace-textSecondary uppercase tracking-wider mb-3 px-2'>
                  LCA 워크플로우
                </h3>
                <div className='space-y-1'>
                  {subItems.map(item => (
                    <button
                      key={item.name}
                      onClick={() => handleNavigation(item.href)}
                      className={cn(
                        'w-full text-left p-3 rounded-lg transition-all duration-200 flex items-center gap-3 group',
                        pathname === item.href
                          ? 'bg-ecotrace-accent text-white'
                          : 'text-ecotrace-textSecondary hover:text-white hover:bg-ecotrace-secondary/50'
                      )}
                    >
                      <item.icon
                        className={cn(
                          'w-5 h-5',
                          pathname === item.href
                            ? 'text-white'
                            : 'text-ecotrace-textSecondary group-hover:text-white'
                        )}
                      />
                      <div className='flex-1'>
                        <div className='font-medium'>{item.name}</div>
                        <div className='text-xs opacity-75'>
                          {item.description}
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </nav>

            {/* 사이드바 푸터 */}
            <div className='p-4 border-t border-ecotrace-border'>
              <div className='text-xs text-ecotrace-textSecondary text-center'>
                GreenSteel LCA v1.0.0
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

export { LCALayout };
