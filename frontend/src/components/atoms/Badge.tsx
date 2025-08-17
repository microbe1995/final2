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
    default: 'bg-[#f1f5f9] text-[#0f172a] border-[#e2e8f0]',
    success: 'bg-[#16a34a]/10 text-[#16a34a] border-[#16a34a]/20',
    warning: 'bg-[#d97706]/10 text-[#d97706] border-[#d97706]/20',
    error: 'bg-[#dc2626]/10 text-[#dc2626] border-[#dc2626]/20',
    info: 'bg-[#2563eb]/10 text-[#2563eb] border-[#2563eb]/20'
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
