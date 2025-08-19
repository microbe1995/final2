'use client';

import React from 'react';

// ============================================================================
// 🎯 Badge Props 인터페이스
// ============================================================================

export interface BadgeProps {
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
}

// ============================================================================
// 🎨 Badge 컴포넌트
// ============================================================================

const Badge: React.FC<BadgeProps> = ({ 
  variant = 'default', 
  size = 'md', 
  children, 
  className = '',
  onClick 
}) => {
  // variant별 스타일 매핑 - 다크 테마에 맞게 조정
  const variantStyles = {
    default: 'bg-[#334155] text-white border-[#475569]',
    primary: 'bg-blue-600 text-white border-blue-500',
    secondary: 'bg-gray-600 text-white border-gray-500',
    success: 'bg-green-900/30 text-green-300 border-green-500/50',
    warning: 'bg-yellow-900/30 text-yellow-300 border-yellow-500/50',
    error: 'bg-red-900/30 text-red-300 border-red-500/50',
    info: 'bg-blue-900/30 text-blue-300 border-blue-500/50'
  };

  // size별 스타일 매핑
  const sizeStyles = {
    sm: 'px-2 py-1 text-xs font-medium',
    md: 'px-3 py-1.5 text-sm font-medium',
    lg: 'px-4 py-2 text-base font-semibold'
  };

  const baseStyles = 'inline-flex items-center justify-center rounded-full border transition-colors duration-200';
  const variantStyle = variantStyles[variant];
  const sizeStyle = sizeStyles[size];
  const interactiveStyle = onClick ? 'cursor-pointer hover:opacity-80' : '';

  return (
    <span
      className={`${baseStyles} ${variantStyle} ${sizeStyle} ${interactiveStyle} ${className}`}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
    >
      {children}
    </span>
  );
};

export default Badge;
