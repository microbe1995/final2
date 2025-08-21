'use client';

import { useRouter } from 'next/navigation';
import { mockProjects } from '@/lib/mocks';

export default function DashboardPage() {
  const router = useRouter();

  const handleProjectClick = (projectId: string) => {
    router.push(`/lca/projects/${projectId}/scope`);
  };

  const handleNewProject = () => {
    const newProjectId = `proj-${Date.now()}`;
    router.push(`/lca/projects/${newProjectId}/scope`);
  };

  // 최신 프로젝트 가져오기 (updatedAt 기준)
  const latestProject = [...mockProjects].sort(
    (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
  )[0];

  return (
    <div className='min-h-screen'>
      <div className='px-4 sm:px-6 lg:px-8 py-8'>
        {/* Header */}
        <div className='mb-8'>
          <h1 className='text-3xl font-bold text-foreground mb-2'>대시보드</h1>
          <p className='text-muted-foreground'>
            진행 중인 LCA 프로젝트를 관리하세요
          </p>
        </div>

        {/* 프로젝트 통계 섹션 - 최상단 */}
        <div className='mb-8'>
          <h2 className='text-xl font-semibold text-foreground mb-4 flex items-center'>
            <span className='w-2 h-2 bg-primary rounded-full mr-3'></span>
            프로젝트 통계
          </h2>
          <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
            <div className='flex justify-between items-center p-4 rounded-lg bg-card border border-border/30 shadow-sm'>
              <div>
                <span className='text-muted-foreground font-medium'>
                  전체 프로젝트
                </span>
                <p className='text-xs text-muted-foreground'>활성 프로젝트</p>
              </div>
              <span className='text-foreground font-bold text-2xl'>
                {mockProjects.length}개
              </span>
            </div>
            <div className='flex justify-between items-center p-4 rounded-lg bg-card border border-border/30 shadow-sm'>
              <div>
                <span className='text-muted-foreground font-medium'>
                  진행 중
                </span>
                <p className='text-xs text-muted-foreground'>작업 진행 중</p>
              </div>
              <span className='text-green-500 font-bold text-2xl'>
                {mockProjects.filter(p => p.status === '진행 중').length}개
              </span>
            </div>
            <div className='flex justify-between items-center p-4 rounded-lg bg-card border border-border/30 shadow-sm'>
              <div>
                <span className='text-muted-foreground font-medium'>완료</span>
                <p className='text-xs text-muted-foreground'>분석 완료</p>
              </div>
              <span className='text-blue-500 font-bold text-2xl'>
                {mockProjects.filter(p => p.status === '완료').length}개
              </span>
            </div>
          </div>
        </div>

        {/* 최신 프로젝트 하이라이트 섹션 */}
        {latestProject && (
          <div className='mb-8'>
            <h2 className='text-xl font-semibold text-foreground mb-4 flex items-center'>
              <span className='w-2 h-2 bg-green-500 rounded-full mr-3'></span>
              최신 프로젝트
            </h2>
            <div className='bg-gradient-to-r from-primary/10 to-primary/5 border border-primary/20 rounded-xl p-6'>
              <div className='flex items-start justify-between'>
                <div className='flex-1'>
                  <h3 className='text-lg font-semibold text-foreground mb-2'>
                    {latestProject.name}
                  </h3>
                  <p className='text-muted-foreground mb-3'>
                    {latestProject.description}
                  </p>
                  <div className='flex items-center gap-4 text-sm'>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        latestProject.status === '진행 중'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                          : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                      }`}
                    >
                      {latestProject.status}
                    </span>
                    <span className='text-muted-foreground'>
                      최종 업데이트:{' '}
                      {new Date(latestProject.updatedAt).toLocaleDateString(
                        'ko-KR'
                      )}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => handleProjectClick(latestProject.id)}
                  className='bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:bg-primary/90 transition-colors text-sm font-medium ml-4'
                >
                  프로젝트 보기
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 프로젝트 목록 섹션 */}
        <div className='mb-8'>
          <h2 className='text-xl font-semibold text-foreground mb-4'>
            모든 프로젝트
          </h2>
          <div className='overflow-x-auto'>
            <div className='flex flex-nowrap gap-4 pb-4 min-w-max lg:min-w-0 lg:grid lg:grid-cols-1 xl:grid-cols-2 2xl:grid-cols-3 lg:gap-6'>
              {mockProjects.map(project => (
                <div
                  key={project.id}
                  className='bg-card border border-border/30 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow min-w-[300px] lg:min-w-0'
                >
                  <div className='flex items-start justify-between mb-3'>
                    <h3 className='text-lg font-semibold text-foreground'>
                      {project.name}
                    </h3>
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-medium ${
                        project.status === '진행 중'
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400'
                          : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400'
                      }`}
                    >
                      {project.status}
                    </span>
                  </div>
                  <p className='text-muted-foreground text-sm mb-4 line-clamp-2'>
                    {project.description}
                  </p>
                  <div className='text-xs text-muted-foreground mb-4'>
                    <div>생성일: {project.createdAt}</div>
                    <div>수정일: {project.updatedAt}</div>
                  </div>
                  <button
                    onClick={() => handleProjectClick(project.id)}
                    className='w-full border border-border/50 bg-transparent text-foreground px-4 py-2 rounded-lg hover:bg-muted/50 transition-colors text-sm font-medium'
                  >
                    열기
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 플로팅 액션 버튼 - 우측 하단 고정 */}
        <div className='fixed right-8 bottom-8 z-50'>
          <button
            onClick={handleNewProject}
            aria-label='새 프로젝트 시작하기'
            className='bg-primary text-primary-foreground w-16 h-16 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-110 flex items-center justify-center'
          >
            <svg
              className='w-6 h-6'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M12 4v16m8-8H4'
              />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
