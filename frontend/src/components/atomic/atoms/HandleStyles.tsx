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

const handleStyle: React.CSSProperties = { 
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
 * 
 * React Flow 공식 문서 권장사항:
 * - 각 방향에 하나의 핸들만 생성
 * - 연결 시 React Flow가 자동으로 source/target 결정
 * - 수동 위치 조정 금지
 */
export const renderFourDirectionHandles = (isConnectable = true, nodeId?: string) => {
  const nodeIdStr = nodeId || 'node';
  
  // React Flow 공식 문서: 각 방향에 source와 target 핸들을 모두 생성
  const handleConfigs = [
    { position: Position.Left, id: `${nodeIdStr}-left`, type: 'source' as const },
    { position: Position.Right, id: `${nodeIdStr}-right`, type: 'target' as const },
    { position: Position.Top, id: `${nodeIdStr}-top`, type: 'source' as const },
    { position: Position.Bottom, id: `${nodeIdStr}-bottom`, type: 'target' as const },
  ];

  return handleConfigs.map(({ position, id, type }) => (
    <Handle
      key={id}
      id={id}
      type={type}
      position={position}
      isConnectable={isConnectable}
      className={cls}
      style={handleStyle}
    />
  ));
};

/* 그룹 노드 등에서 쓸 기본 핸들 스타일 */
export const defaultHandleStyle = {
  background: '#3b82f6',
  width: 12,
  height: 12,
  border: '2px solid white',
  borderRadius: '50%',
};
