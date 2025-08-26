import React from 'react';
import Button from '@/components/atomic/atoms/Button';

interface ProjectCardProps {
  project: {
    id: string;
    name: string;
    description: string;
    status: 'draft' | 'in-progress' | 'completed' | 'archived';
    lastModified: string;
    progress?: number;
    owner: string;
    department: string;
  };
  onClick: (projectId: string) => void;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onClick,
}) => {
  const statusLabels = {
    draft: '초안',
    'in-progress': '진행중',
    completed: '완료',
    archived: '보관',
  };

  const statusColors = {
    draft: 'bg-gray-500',
    'in-progress': 'bg-blue-500',
    completed: 'bg-green-500',
    archived: 'bg-yellow-500',
  };

  return (
    <div className='bg-white/5 border border-white/10 rounded-lg p-6 shadow-sm hover:shadow-md transition-shadow min-w-[300px] lg:min-w-0'>
      <div className='flex items-start justify-between mb-3'>
        <h3 className='text-lg font-semibold text-white'>{project.name}</h3>
        <span
          className={`px-2 py-1 rounded-full text-xs font-medium ${statusColors[project.status]}`}
        >
          {statusLabels[project.status]}
        </span>
      </div>
      <p className='text-white/60 text-sm mb-4 line-clamp-2'>
        {project.description}
      </p>

      {/* 진행률 표시 */}
      {project.progress !== undefined && (
        <div className='mb-4'>
          <div className='flex items-center justify-between text-xs text-white/60 mb-2'>
            <span>진행률</span>
            <span>{project.progress}%</span>
          </div>
          <div className='w-full bg-white/10 rounded-full h-2'>
            <div
              className='bg-gradient-to-r from-blue-500 to-green-500 h-2 rounded-full transition-all duration-300'
              style={{ width: `${project.progress}%` }}
            />
          </div>
        </div>
      )}

      <div className='text-xs text-white/40 mb-4'>
        <div>담당자: {project.owner}</div>
        <div>부서: {project.department}</div>
        <div>최종 수정일: {project.lastModified}</div>
      </div>
      <Button
        onClick={() => onClick(project.id)}
        variant='outline'
        size='md'
        className='w-full border-white/20 text-white hover:bg-white/10'
      >
        열기
      </Button>
    </div>
  );
};
