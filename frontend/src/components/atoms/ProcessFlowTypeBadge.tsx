'use client';

import React from 'react';
interface ProcessTypeBadgeProps {
  processType: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

const ProcessTypeBadge: React.FC<ProcessTypeBadgeProps> = ({
  processType,
  size = 'md',
  className = ''
}) => {
  // 간단한 타입별 스타일링
  const getTypeStyle = (type: string) => {
    switch (type) {
      case 'manufacturing': return { color: 'bg-blue-500', icon: '🏭', label: '제조' };
      case 'quality': return { color: 'bg-green-500', icon: '✅', label: '품질' };
      case 'packaging': return { color: 'bg-purple-500', icon: '📦', label: '포장' };
      case 'shipping': return { color: 'bg-orange-500', icon: '🚚', label: '배송' };
      default: return { color: 'bg-gray-500', icon: '⚙️', label: '기타' };
    }
  };
  
  const config = getTypeStyle(processType);
  
  const sizeClasses = {
    sm: 'px-2 py-1 text-xs',
    md: 'px-3 py-1.5 text-sm',
    lg: 'px-4 py-2 text-base'
  };

  const baseClasses = `${config.color} text-white rounded-full font-medium`;
  const finalClasses = `${baseClasses} ${sizeClasses[size as keyof typeof sizeClasses]} ${className}`.trim();

  return (
    <span className={finalClasses}>
      {config.icon} {config.label}
    </span>
  );
};

export default ProcessTypeBadge;
