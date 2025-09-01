'use client';

import React from 'react';
import { Handle, Position } from '@xyflow/react';

const color = {
  bg: '!bg-blue-600',
  hoverBg: 'hover:!bg-blue-700',
  shadow: 'drop-shadow(0 0 8px rgba(59,130,246,.3))',
};

const baseCls = '!w-4 !h-4 !border-2 !border-white pointer-events-auto';
const cls = `${baseCls} ${color.bg} ${color.hoverBg}`;
const styleBase: React.CSSProperties = { 
  filter: color.shadow, 
  zIndex: 10,
  background: '#3b82f6',
  border: '2px solid white'
};

/**
 * 4방향 핸들 배치 - React Flow 공식 문서에 따른 올바른 구현
 * 각 방향에 하나의 핸들만 생성하여 연결 가능하도록 함
 * - Left: 단일 핸들 (source/target 동적 결정)
 * - Right: 단일 핸들 (source/target 동적 결정)
 * - Top: 단일 핸들 (source/target 동적 결정)
 * - Bottom: 단일 핸들 (source/target 동적 결정)
 */
export const renderFourDirectionHandles = (isConnectable = true, nodeId?: string) => {
  const nodeIdStr = nodeId || 'node';
  
  const handleConfigs = [
    { position: Position.Left, id: `${nodeIdStr}-left` },
    { position: Position.Right, id: `${nodeIdStr}-right` },
    { position: Position.Top, id: `${nodeIdStr}-top` },
    { position: Position.Bottom, id: `${nodeIdStr}-bottom` },
  ];

  return handleConfigs.map(({ position, id }) => (
    <Handle
      key={id}
      id={id}
      type="source" // 기본적으로 source로 설정하되, 연결 시 동적으로 결정됨
      position={position}
      isConnectable={isConnectable}
      className={cls}
      style={styleBase}
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
