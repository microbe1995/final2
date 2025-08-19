'use client';

import React, { useState } from 'react';
import { Handle, Position } from '@xyflow/react';

interface ProcessFlowHandleProps {
  type: 'source' | 'target';
  position: Position;
  className?: string;
  style?: React.CSSProperties;
}

const ProcessFlowHandle: React.FC<ProcessFlowHandleProps> = ({
  type,
  position,
  className = '',
  style = {}
}) => {
  const [isHovered, setIsHovered] = useState(false);
  
  // 핸들 크기를 w-36 h-36 (144px x 144px)로 더 증가하고 더 명확한 스타일링 적용
  const baseClasses = 'w-36 h-36 border-4 border-white shadow-2xl transition-all duration-300 cursor-crosshair relative flex items-center justify-center ring-2 ring-gray-200 hover:ring-blue-300 transform hover:scale-110 active:scale-95';
  const finalClasses = `${baseClasses} ${className}`.trim();

  // 핸들 타입에 따른 색상 구분
  const getHandleStyle = () => {
    const baseStyle = {
      minWidth: '144px',
      minHeight: '144px',
      zIndex: 10,
      ...style
    };

    if (type === 'source') {
      return {
        ...baseStyle,
        backgroundColor: isHovered ? '#1d4ed8' : '#3b82f6', // 파란색
        borderColor: '#ffffff',
        boxShadow: isHovered 
          ? '0 75px 160px -45px rgba(59, 130, 246, 1.0), 0 65px 90px -35px rgba(0, 0, 0, 1.0)'
          : '0 65px 85px -20px rgba(0, 0, 0, 1.0), 0 35px 45px -18px rgba(0, 0, 0, 1.0)'
      };
    } else {
      return {
        ...baseStyle,
        backgroundColor: isHovered ? '#047857' : '#10b981', // 초록색
        borderColor: '#ffffff',
        boxShadow: isHovered 
          ? '0 75px 160px -45px rgba(16, 185, 129, 1.0), 0 65px 90px -35px rgba(0, 0, 0, 1.0)'
          : '0 65px 85px -20px rgba(0, 0, 0, 1.0), 0 35px 45px -18px rgba(0, 0, 0, 1.0)'
      };
    }
  };

  // 핸들 타입에 따른 아이콘
  const getHandleIcon = () => {
    if (type === 'source') {
      return '→'; // 출력
    } else {
      return '←'; // 입력
    }
  };

  // 핸들 타입에 따른 툴팁 텍스트
  const getTooltipText = () => {
    if (type === 'source') {
      return '출력 연결점 (다른 노드로 연결)';
    } else {
      return '입력 연결점 (다른 노드에서 연결)';
    }
  };

  // 핸들 타입에 따른 배경 색상
  const getBackgroundColor = () => {
    if (type === 'source') {
      return 'from-blue-100 to-blue-200'; // 파란색 계열
    } else {
      return 'from-green-100 to-green-200'; // 초록색 계열
    }
  };

  // 핸들 타입에 따른 테두리 색상
  const getRingColor = () => {
    if (type === 'source') {
      return 'hover:ring-blue-400 focus:ring-blue-500'; // 파란색 계열
    } else {
      return 'hover:ring-green-400 focus:ring-green-500'; // 초록색 계열
    }
  };

  return (
    <div className="relative group">
      {/* 핸들 배경 (더 큰 클릭 영역) */}
      <div 
        className={`absolute inset-0 w-48 h-48 bg-gradient-to-br ${getBackgroundColor()} rounded-full opacity-95 -z-10 transition-all duration-300 group-hover:opacity-100`}
        style={{
          left: '-44px',
          top: '-44px'
        }}
      />
      
      {/* 툴팁 */}
      <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-12 px-12 py-8 bg-gray-900 text-white text-6xl rounded-lg opacity-0 group-hover:opacity-100 transition-all duration-300 pointer-events-none whitespace-nowrap z-20 shadow-2xl">
        {getTooltipText()}
        <div className="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900"></div>
      </div>
      
      {/* 연결 가능 표시 (파동 효과) */}
      {isHovered && (
        <div className={`absolute inset-0 w-36 h-36 rounded-full border-2 ${type === 'source' ? 'border-blue-400' : 'border-green-400'} animate-ping opacity-75`}></div>
      )}
      
      {/* 핸들 타입 표시 (작은 배지) */}
      <div className={`absolute -top-9 -right-9 w-20 h-20 rounded-full text-4xl font-bold text-white flex items-center justify-center ${
        type === 'source' ? 'bg-blue-600' : 'bg-green-600'
      } shadow-xl`}>
        {type === 'source' ? 'O' : 'I'}
      </div>
      
      <Handle
        type={type}
        position={position}
        className={`${finalClasses} ${getRingColor()}`}
        style={getHandleStyle()}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        aria-label={getTooltipText()}
        role="button"
        tabIndex={0}
      >
        <span className="text-white text-9xl font-bold drop-shadow-sm transition-transform duration-200 group-hover:scale-110">
          {getHandleIcon()}
        </span>
      </Handle>
    </div>
  );
};

export default ProcessFlowHandle;
