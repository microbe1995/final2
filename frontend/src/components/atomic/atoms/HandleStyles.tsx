'use client';

import React from 'react';
import { Handle, Position } from '@xyflow/react';

type HandleType = 'source' | 'target';

const color = {
  bg: '!bg-green-600',
  hoverBg: 'hover:!bg-green-700',
  shadow: 'drop-shadow(0 0 8px rgba(34,197,94,.3))',
};

const baseCls = '!w-4 !h-4 !border-2 !border-white pointer-events-auto';
const cls = `${baseCls} ${color.bg} ${color.hoverBg}`;
const styleBase: React.CSSProperties = { filter: color.shadow, zIndex: 10 };

// 🔴 수정: source와 target 핸들을 구분하는 스타일
const sourceStyle: React.CSSProperties = { 
  ...styleBase, 
  background: '#3b82f6', // 파란색 (source)
  border: '2px solid white'
};
const targetStyle: React.CSSProperties = { 
  ...styleBase, 
  background: '#10b981', // 초록색 (target)
  border: '2px solid white'
};

/**
 * 4방향 핸들 배치 - 모든 핸들을 source로 설정하고 연결 시 자동 변환
 * React Flow의 연결 시 자동으로 target으로 인식되도록 구현
 * - Left: source (연결 시 자동으로 target으로 변환 가능)
 * - Right: source (연결 시 자동으로 target으로 변환 가능)
 * - Top: source (연결 시 자동으로 target으로 변환 가능)
 * - Bottom: source (연결 시 자동으로 target으로 변환 가능)
 */
export const renderFourDirectionHandles = (isConnectable = true, nodeId?: string) => {
  // 🔴 수정: 노드 ID가 반드시 필요하도록 강제
  if (!nodeId) {
    console.warn('⚠️ renderFourDirectionHandles: nodeId가 제공되지 않았습니다.');
    return null;
  }
  
  const handles = [
    {
      position: Position.Left,
      type: 'source' as HandleType,
      id: `${nodeId}-left`,
      style: sourceStyle,
    },
    {
      position: Position.Right,
      type: 'source' as HandleType,
      id: `${nodeId}-right`,
      style: sourceStyle,
    },
    {
      position: Position.Top,
      type: 'source' as HandleType,
      id: `${nodeId}-top`,
      style: sourceStyle,
    },
    {
      position: Position.Bottom,
      type: 'source' as HandleType,
      id: `${nodeId}-bottom`,
      style: sourceStyle,
    },
  ];

  return handles.map(({ position, type, id, style }) => (
    <Handle
      key={id}
      id={id}
      type={type}
      position={position}
      isConnectable={isConnectable}
      className={cls}
      style={style}
    />
  ));
};



/* 그룹 노드 등에서 쓸 기본 핸들 스타일 */
export const handleStyle = {
  background: '#3b82f6',
  width: 12,
  height: 12,
  border: '2px solid white',
  borderRadius: '50%',
};
