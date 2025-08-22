'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  BarChart3,
  FileText,
  TrendingUp,
  Database,
  Zap,
  CheckCircle,
  FolderOpen,
  Settings,
  Plus,
} from 'lucide-react';

interface LCANavigationProps {
  onClose?: () => void;
}

export const LCANavigation: React.FC<LCANavigationProps> = ({ onClose }) => {
  const pathname = usePathname();

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

  return (
    <aside className='h-full flex flex-col bg-white/5 border-r border-white/10'>
      <div className='flex-1 overflow-y-auto p-4'>
        {/* 헤더 */}
        <div className='mb-6'>
          <h2 className='text-lg font-semibold text-white mb-2'>LCA 관리</h2>
          <p className='text-xs text-white/60'>생명주기 평가 시스템</p>
        </div>

        {/* 새 프로젝트 버튼 */}
        <div className='mb-6'>
          <Link
            href='/lca/projects/new/scope'
            className='w-full flex items-center gap-3 px-4 py-3 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors'
            onClick={onClose}
          >
            <Plus className='h-4 w-4' />
            <span className='font-medium'>새 프로젝트 시작</span>
          </Link>
        </div>

        {/* 메인 네비게이션 */}
        <div className='mb-6'>
          <h3 className='text-xs font-semibold text-white/60 uppercase tracking-wider mb-3'>
            메인 메뉴
          </h3>
          <ul className='space-y-1'>
            {mainItems.map(item => {
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

        {/* 하위 페이지 네비게이션 */}
        <div className='mb-6'>
          <h3 className='text-xs font-semibold text-white/60 uppercase tracking-wider mb-3'>
            프로젝트 워크플로우
          </h3>
          <ul className='space-y-1'>
            {subItems.map(item => {
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

        {/* 빠른 액션 */}
        <div className='mb-6'>
          <h3 className='text-xs font-semibold text-white/60 uppercase tracking-wider mb-3'>
            빠른 액션
          </h3>
          <div className='space-y-2'>
            <button className='w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-white/60 hover:bg-white/5 hover:text-white transition-colors'>
              <Database className='h-4 w-4' />
              <span>데이터 가져오기</span>
            </button>
            <button className='w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md text-white/60 hover:bg-white/5 hover:text-white transition-colors'>
              <FileText className='h-4 w-4' />
              <span>템플릿 다운로드</span>
            </button>
          </div>
        </div>
      </div>

      {/* 모바일에서 닫기 버튼 */}
      {onClose && (
        <div className='p-4 border-t border-white/10 md:hidden'>
          <button
            className='w-full rounded-lg bg-primary text-white py-2 font-medium hover:bg-primary/90 transition-colors'
            onClick={onClose}
          >
            닫기
          </button>
        </div>
      )}
    </aside>
  );
};
