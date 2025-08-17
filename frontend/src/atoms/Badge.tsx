'use client';

import React from 'react';

// ============================================================================
// 🎯 Badge Props 인터페이스
// ============================================================================

export interface BadgeProps {
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info';
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
  // variant별 스타일 매핑
  const variantStyles = {
    default: 'bg-gray-100 text-gray-800 border-gray-200',
    success: 'bg-green-100 text-green-800 border-green-200',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    error: 'bg-red-100 text-red-800 border-red-200',
    info: 'bg-blue-100 text-blue-800 border-blue-200'
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
