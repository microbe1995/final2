'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useMediaQuery } from '@/hooks/useMediaQuery';
import {
  BarChart3,
  FileText,
  TrendingUp,
  Database,
  Zap,
  CheckCircle,
  FolderOpen,
  Settings,
  Download,
  Upload,
  X,
  Menu,
} from 'lucide-react';

interface LCASidebarProps {
  projectId?: string;
  isMainPage?: boolean;
  onClose?: () => void;
  isOpen?: boolean;
  onToggle?: () => void;
}

export const LCASidebar: React.FC<LCASidebarProps> = ({
  projectId,
  isMainPage = false,
  onClose,
  isOpen = true,
  onToggle,
}) => {
  const pathname = usePathname();
  const isMobile = useMediaQuery('(max-width: 1024px)');

  const mainMenuItems = [
    {
      name: '대시보드',
      href: '/lca',
      icon: BarChart3,
      description: 'LCA 프로젝트 개요 및 통계',
    },
  ];

  const projectWorkflowItems = [
    {
      name: '목적 및 범위',
      href: `/lca/scope`,
      icon: FileText,
      description: '프로젝트 목적과 분석 범위 정의',
    },
    {
      name: 'LCI',
      href: `/lca/lci`,
      icon: Database,
      description: '생명주기 인벤토리 데이터 입력 및 관리',
    },
    {
      name: 'LCIA',
      href: `/lca/lcia`,
      icon: Zap,
      description: '생명주기 영향평가 실행 및 결과 분석',
    },
    {
      name: '해석',
      href: `/lca/interpretation`,
      icon: TrendingUp,
      description: 'LCA 결과 해석 및 결론',
    },
    {
      name: '보고서',
      href: `/lca/report`,
      icon: CheckCircle,
      description: 'LCA 보고서 생성 및 관리',
    },
  ];

  // 빠른 액션 항목 제거 - 이미지에 없음

  const renderNavigationItems = (
    items: typeof mainMenuItems,
    title: string
  ) => (
    <div>
      <h3 className='text-xs font-semibold text-white/60 uppercase tracking-wider mb-3'>
        {title}
      </h3>
      <ul className='space-y-1'>
        {items.map(item => {
          const isActive = pathname === item.href;
          const linkClassName = isActive
            ? 'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md bg-primary/20 text-primary border border-primary/30 transition-colors'
            : 'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-white/60 hover:bg-white/5 hover:text-white transition-colors';

          return (
            <li key={item.name}>
              <Link
                href={item.href}
                className={linkClassName}
                onClick={() => {
                  if (isMobile && onClose) {
                    onClose();
                  }
                }}
              >
                <item.icon className='h-4 w-4' />
                <div className='flex-1'>
                  <div className='font-medium'>{item.name}</div>
                  <div className='text-xs text-white/40'>
                    {item.description}
                  </div>
                </div>
              </Link>
            </li>
          );
        })}
      </ul>
    </div>
  );

  // 모바일에서는 오버레이와 함께 표시
  if (isMobile) {
    return (
      <>
        {/* 모바일 토글 버튼 */}
        <button
          onClick={onToggle}
          className='lg:hidden fixed top-4 left-4 z-50 p-3 bg-white/10 backdrop-blur-sm rounded-lg border border-white/20 hover:bg-white/20 transition-colors min-h-[44px] min-w-[44px] flex items-center justify-center'
        >
          <Menu className='h-5 w-5 text-white' />
        </button>

        {/* 모바일 사이드바 오버레이 */}
        {isOpen && (
          <div
            className='fixed inset-0 bg-black/50 z-40 lg:hidden'
            onClick={onClose}
          />
        )}

        {/* 모바일 사이드바 */}
        <aside
          className={`fixed inset-y-0 left-0 z-50 w-80 bg-white/5 backdrop-blur-md border-r border-white/10 transform transition-transform duration-300 ease-in-out lg:hidden ${
            isOpen ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <div className='flex flex-col h-full'>
            {/* 모바일 헤더 */}
            <div className='flex items-center justify-between p-4 border-b border-white/10'>
              <h2 className='text-lg font-semibold text-white'>LCA 관리</h2>
              <button
                onClick={onClose}
                className='p-2 rounded-lg hover:bg-white/10 transition-colors min-h-[40px] min-w-[40px] flex items-center justify-center'
              >
                <X className='h-5 w-5 text-white' />
              </button>
            </div>

            {/* 모바일 네비게이션 */}
            <div className='flex-1 overflow-y-auto p-4'>
              <div className='mb-6'>
                <h2 className='text-lg font-semibold text-white mb-2'>
                  LCA 관리
                </h2>
                <p className='text-xs text-white/60'>생명주기 평가 시스템</p>
              </div>

              <nav className='space-y-6'>
                {/* 메인 메뉴 */}
                {renderNavigationItems(mainMenuItems, '메인')}

                {/* 프로젝트 워크플로우 - 프로젝트 페이지에서만 표시 */}
                {!isMainPage && (
                  <div>
                    <h3 className='text-xs font-semibold text-white/60 uppercase tracking-wider mb-3'>
                      LCA 워크플로우
                    </h3>
                    <ul className='space-y-1'>
                      {projectWorkflowItems.map(item => {
                        const isActive = pathname === item.href;
                        const linkClassName = isActive
                          ? 'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md bg-primary/20 text-primary border border-primary/30 transition-colors'
                          : 'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-white/60 hover:bg-white/5 hover:text-white transition-colors';

                        return (
                          <li key={item.name}>
                            <Link
                              href={item.href}
                              className={linkClassName}
                              onClick={onClose}
                            >
                              <item.icon className='h-4 w-4' />
                              <div className='flex-1'>
                                <div className='font-medium'>{item.name}</div>
                                <div className='text-xs text-white/40'>
                                  {item.description}
                                </div>
                              </div>
                            </Link>
                          </li>
                        );
                      })}
                    </ul>
                  </div>
                )}
              </nav>
            </div>
          </div>
        </aside>
      </>
    );
  }

  // 데스크톱에서는 항상 표시
  return (
    <aside className='h-full flex flex-col bg-white/5 border-r border-white/10'>
      <div className='flex-1 overflow-y-auto p-4'>
        <div className='mb-6'>
          <h2 className='text-lg font-semibold text-white mb-2'>LCA 관리</h2>
          <p className='text-xs text-white/60'>생명주기 평가 시스템</p>
        </div>

        <nav className='space-y-6'>
          {/* 메인 메뉴 */}
          {renderNavigationItems(mainMenuItems, '메인')}

          {/* 프로젝트 워크플로우 - 프로젝트 페이지에서만 표시 */}
          {!isMainPage && (
            <div>
              <h3 className='text-xs font-semibold text-white/60 uppercase tracking-wider mb-3'>
                LCA 워크플로우
              </h3>
              <ul className='space-y-1'>
                {projectWorkflowItems.map(item => {
                  const isActive = pathname === item.href;
                  const linkClassName = isActive
                    ? 'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md bg-primary/20 text-primary border border-primary/30 transition-colors'
                    : 'flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-white/60 hover:bg-white/5 hover:text-white transition-colors';

                  return (
                    <li key={item.name}>
                      <Link href={item.href} className={linkClassName}>
                        <item.icon className='h-4 w-4' />
                        <div className='flex-1'>
                          <div className='font-medium'>{item.name}</div>
                          <div className='text-xs text-white/40'>
                            {item.description}
                          </div>
                        </div>
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          )}
        </nav>
      </div>
    </aside>
  );
};
