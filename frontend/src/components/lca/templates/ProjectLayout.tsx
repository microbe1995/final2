'use client';

import React, { useState } from 'react';
import { useParams } from 'next/navigation';
import { Menu, X } from 'lucide-react';
import { LCASidebar } from '../organisms/LCASidebar';

interface ProjectLayoutProps {
  children: React.ReactNode;
  title: string;
  description?: string;
  isMainPage?: boolean;
}

export const ProjectLayout: React.FC<ProjectLayoutProps> = ({
  children,
  title,
  description,
  isMainPage = false,
}) => {
  const params = useParams();
  const projectId = params.projectId as string;
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className='flex h-screen bg-black/50 backdrop-blur-sm'>
      {/* 모바일 사이드바 오버레이 */}
      {sidebarOpen && (
        <div className='fixed inset-0 z-40 md:hidden'>
          <div
            className='fixed inset-0 bg-black/50'
            onClick={() => setSidebarOpen(false)}
          />
          <div className='fixed left-0 top-0 h-full w-80 z-50'>
            <LCASidebar
              projectId={projectId}
              isMainPage={isMainPage}
              onClose={() => setSidebarOpen(false)}
            />
          </div>
        </div>
      )}

      {/* 데스크톱 사이드바 */}
      <div className='hidden md:block w-80'>
        <LCASidebar projectId={projectId} isMainPage={isMainPage} />
      </div>

      {/* 메인 콘텐츠 */}
      <div className='flex-1 flex flex-col overflow-hidden'>
        {/* 헤더 */}
        <header className='bg-white/5 border-b border-white/10 px-6 py-4'>
          <div className='flex items-center justify-between'>
            <div className='flex items-center gap-4'>
              <button
                onClick={() => setSidebarOpen(true)}
                className='md:hidden p-2 rounded-lg hover:bg-white/5 transition-colors'
              >
                <Menu className='h-5 w-5 text-white' />
              </button>
              <div>
                <h1 className='text-2xl font-bold text-white'>{title}</h1>
                {description && (
                  <p className='text-white/60 text-sm mt-1'>{description}</p>
                )}
              </div>
            </div>
            {!isMainPage && projectId && (
              <div className='text-sm text-white/40'>
                프로젝트 ID: {projectId}
              </div>
            )}
          </div>
        </header>

        {/* 콘텐츠 영역 */}
        <main className='flex-1 overflow-y-auto p-6'>{children}</main>
      </div>
    </div>
  );
};
