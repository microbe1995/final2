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
  const handlePrefix = nodeId ? `${nodeId}-` : '';
  
  const handles = [
    {
      position: Position.Left,
      type: 'source' as HandleType,
      id: `${handlePrefix}left`,
      style: sourceStyle,
    },
    {
      position: Position.Right,
      type: 'source' as HandleType,
      id: `${handlePrefix}right`,
      style: sourceStyle,
    },
    {
      position: Position.Top,
      type: 'source' as HandleType,
      id: `${handlePrefix}top`,
      style: sourceStyle,
    },
    {
      position: Position.Bottom,
      type: 'source' as HandleType,
      id: `${handlePrefix}bottom`,
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

/**
 * 🔴 추가: 양방향 연결을 위한 8방향 핸들 (선택적 사용)
 * 각 방향에 source와 target 핸들을 모두 배치하여 양방향 연결 가능
 */
export const renderEightDirectionHandles = (isConnectable = true) => {
  const handles = [
    // Left 방향
    {
      position: Position.Left,
      type: 'source' as HandleType,
      id: 'left-source',
      style: sourceStyle,
    },
    {
      position: Position.Left,
      type: 'target' as HandleType,
      id: 'left-target',
      style: targetStyle,
    },
    // Right 방향
    {
      position: Position.Right,
      type: 'source' as HandleType,
      id: 'right-source',
      style: sourceStyle,
    },
    {
      position: Position.Right,
      type: 'target' as HandleType,
      id: 'right-target',
      style: targetStyle,
    },
    // Top 방향
    {
      position: Position.Top,
      type: 'source' as HandleType,
      id: 'top-source',
      style: sourceStyle,
    },
    {
      position: Position.Top,
      type: 'target' as HandleType,
      id: 'top-target',
      style: targetStyle,
    },
    // Bottom 방향
    {
      position: Position.Bottom,
      type: 'source' as HandleType,
      id: 'bottom-source',
      style: sourceStyle,
    },
    {
      position: Position.Bottom,
      type: 'target' as HandleType,
      id: 'bottom-target',
      style: targetStyle,
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
