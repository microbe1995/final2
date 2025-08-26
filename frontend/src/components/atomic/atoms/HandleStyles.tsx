'use client';

import React from 'react';
import { Handle, Position } from '@xyflow/react';

// 🎯 핸들 타입 정의
export type HandleType = 'source' | 'target';

// 🎯 핸들 위치별 색상 매핑
export const handleColorMap = {
  source: {
    [Position.Left]: 'blue',
    [Position.Right]: 'green', 
    [Position.Top]: 'purple',
    [Position.Bottom]: 'orange'
  },
  target: {
    [Position.Left]: 'blue',
    [Position.Right]: 'green',
    [Position.Top]: 'purple', 
    [Position.Bottom]: 'orange'
  }
};

// 🎯 색상별 스타일 매핑
export const colorStyles = {
  blue: {
    bg: '!bg-blue-600',
    hoverBg: 'hover:!bg-blue-700',
    ring: 'hover:!ring-blue-300',
    shadow: 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.3))'
  },
  green: {
    bg: '!bg-green-600',
    hoverBg: 'hover:!bg-green-700', 
    ring: 'hover:!ring-green-300',
    shadow: 'drop-shadow(0 0 8px rgba(34, 197, 94, 0.3))'
  },
  purple: {
    bg: '!bg-purple-600',
    hoverBg: 'hover:!bg-purple-700',
    ring: 'hover:!ring-purple-300', 
    shadow: 'drop-shadow(0 0 8px rgba(147, 51, 234, 0.3))'
  },
  orange: {
    bg: '!bg-orange-600',
    hoverBg: 'hover:!bg-orange-700',
    ring: 'hover:!ring-orange-300',
    shadow: 'drop-shadow(0 0 8px rgba(249, 115, 22, 0.3))'
  }
};

// 🎯 공통 핸들 스타일 생성 함수
export const getHandleStyle = (type: HandleType, position: Position) => {
  const baseStyle = '!w-4 !h-4 !border-2 !border-white transition-all duration-200 cursor-crosshair hover:!scale-110 hover:!shadow-lg hover:!ring-4 hover:!ring-opacity-50 pointer-events-auto';
  
  const color = handleColorMap[type][position];
  const colorStyle = colorStyles[color as keyof typeof colorStyles];
  
  return `${baseStyle} ${colorStyle.bg} ${colorStyle.hoverBg} ${colorStyle.ring}`;
};

// 🎯 핸들 스타일 객체 생성 함수
export const getHandleStyleObject = (type: HandleType, position: Position) => {
  const color = handleColorMap[type][position];
  const colorStyle = colorStyles[color as keyof typeof colorStyles];
  
  return {
    filter: colorStyle.shadow
  };
};

// 🎯 4방향 핸들 렌더링 함수
export const renderFourDirectionHandles = (
  isConnectable: boolean = true,
) => {
  const positions = [Position.Left, Position.Right, Position.Top, Position.Bottom];
  
  return positions.map((position) => (
    <React.Fragment key={`handles-${position}`}>
      <Handle
        type='target'
        position={position}
        id={`${position}-target`}
        isConnectable={isConnectable}
        className={getHandleStyle('target', position)}
        style={getHandleStyleObject('target', position)}
      />
      <Handle
        type='source'
        position={position}
        id={`${position}-source`}
        isConnectable={isConnectable}
        className={getHandleStyle('source', position)}
        style={getHandleStyleObject('source', position)}
      />
    </React.Fragment>
  ));
};
