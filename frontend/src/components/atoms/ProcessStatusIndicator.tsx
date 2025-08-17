'use client';

import React from 'react';

interface ProcessStatusIndicatorProps {
  status: 'active' | 'inactive' | 'error' | 'warning';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const ProcessStatusIndicator: React.FC<ProcessStatusIndicatorProps> = ({
  status,
  size = 'md',
  className = ''
}) => {
  const statusConfig = {
    active: { color: 'bg-green-400', label: '활성' },
    inactive: { color: 'bg-gray-400', label: '비활성' },
    error: { color: 'bg-red-400', label: '오류' },
    warning: { color: 'bg-yellow-400', label: '경고' }
  };

  const sizeClasses = {
    sm: 'w-2 h-2',
    md: 'w-3 h-3',
    lg: 'w-4 h-4'
  };

  const config = statusConfig[status];
  const baseClasses = `${config.color} rounded-full`;
  const finalClasses = `${baseClasses} ${sizeClasses[size]} ${className}`.trim();

  return (
    <div className="flex items-center gap-2">
      <div className={finalClasses} title={config.label} />
    </div>
  );
};

export default ProcessStatusIndicator;
