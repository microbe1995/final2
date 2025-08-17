'use client';

import React from 'react';

// ============================================================================
// 🎯 커스텀 Background Props 인터페이스
// ============================================================================

interface CustomBackgroundProps {
  color?: string;
  size?: number;
  gap?: number;
  className?: string;
}

// ============================================================================
// 🎨 커스텀 Background 컴포넌트
// ============================================================================

const CustomBackground: React.FC<CustomBackgroundProps> = ({
  color = '#475569',
  size = 2,
  gap = 20,
  className = '',
}) => {
  const patternId = `dots-pattern-${Math.random().toString(36).substr(2, 9)}`;
  
  return (
    <div className={`absolute inset-0 pointer-events-none ${className}`}>
      <svg
        width="100%"
        height="100%"
        xmlns="http://www.w3.org/2000/svg"
        style={{ position: 'absolute', top: 0, left: 0 }}
      >
        <defs>
          <pattern
            id={patternId}
            patternUnits="userSpaceOnUse"
            width={gap}
            height={gap}
          >
            <circle
              cx={gap / 2}
              cy={gap / 2}
              r={size}
              fill={color}
              opacity="0.3"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill={`url(#${patternId})`} />
      </svg>
    </div>
  );
};

export default CustomBackground;
