'use client';

import React from 'react';

// ============================================================================
// 🎯 Icon Props 인터페이스
// ============================================================================

export interface IconProps {
  name: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: string;
  className?: string;
  onClick?: () => void;
}

// ============================================================================
// 🎨 Icon 컴포넌트
// ============================================================================

const Icon: React.FC<IconProps> = ({ 
  name, 
  size = 'md', 
  color = 'currentColor', 
  className = '',
  onClick 
}) => {
  // 공정도 특화 아이콘 매핑
  const iconMap: Record<string, string> = {
    // 공정 관련
    'process': '⚙️',
    'manufacturing': '🏭',
    'assembly': '🔧',
    'packaging': '📦',
    'transport': '🚚',
    'storage': '🏪',
    
    // 자재 관련
    'material': '📦',
    'raw': '🌱',
    'intermediate': '🔗',
    'final': '✅',
    'waste': '🗑️',
    
    // 에너지 관련
    'energy': '⚡',
    'electricity': '💡',
    'gas': '🔥',
    'steam': '💨',
    'fuel': '⛽',
    
    // 화살표 관련
    'arrow-right': '➡️',
    'arrow-left': '⬅️',
    'arrow-up': '⬆️',
    'arrow-down': '⬇️',
    'arrow-bidirectional': '↔️',
    'arrow-curved': '🔄',
    
    // 기본 도형
    'rectangle': '⬜',
    'circle': '⭕',
    'triangle': '🔺',
    'square': '⬜',
    
    // 액션
    'add': '➕',
    'edit': '✏️',
    'delete': '🗑️',
    'connect': '🔗',
    'grid': '⊞',
    'snap': '🎯',
    'select': '👆',
    
    // 상태
    'success': '✅',
    'error': '❌',
    'warning': '⚠️',
    'info': 'ℹ️',
    'loading': '⏳'
  };

  // 크기별 스타일 매핑
  const sizeMap = {
    sm: 'w-4 h-4 text-sm',
    md: 'w-6 h-6 text-base',
    lg: 'w-8 h-8 text-lg',
    xl: 'w-12 h-12 text-2xl'
  };

  const icon = iconMap[name] || '❓';
  const sizeClass = sizeMap[size];

  return (
    <span
      className={`inline-flex items-center justify-center ${sizeClass} ${className}`}
      style={{ color }}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onKeyDown={onClick ? (e) => e.key === 'Enter' && onClick() : undefined}
    >
      {icon}
    </span>
  );
};

export default Icon;
