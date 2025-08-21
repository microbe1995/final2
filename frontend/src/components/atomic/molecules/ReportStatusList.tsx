import React from 'react';
import StatusBadge from '@/components/atomic/atoms/StatusBadge';

interface ReportStatusItem {
  label: string;
  status: 'completed' | 'pending' | 'error';
}

interface ReportStatusListProps {
  items: ReportStatusItem[];
  className?: string;
}

const ReportStatusList: React.FC<ReportStatusListProps> = ({
  items,
  className = '',
}) => {
  return (
    <div className={`space-y-3 ${className}`}>
      {items.map((item, index) => (
        <div key={index} className='flex items-center justify-between'>
          <span className='text-muted-foreground'>{item.label}</span>
          <StatusBadge status={item.status}>
            {item.status === 'completed'
              ? '완료'
              : item.status === 'pending'
                ? '진행중'
                : '오류'}
          </StatusBadge>
        </div>
      ))}
    </div>
  );
};

export default ReportStatusList;
