'use client';

import React from 'react';
import { Handle, Position } from '@xyflow/react';

const color = {
  source: {
    bg: '!bg-blue-600',
    hoverBg: 'hover:!bg-blue-700',
    shadow: 'drop-shadow(0 0 8px rgba(59,130,246,.3))',
  },
  target: {
    bg: '!bg-green-600',
    hoverBg: 'hover:!bg-green-700',
    shadow: 'drop-shadow(0 0 8px rgba(34,197,94,.3))',
  }
};

const baseCls = '!w-4 !h-4 !border-2 !border-white pointer-events-auto';
const sourceCls = `${baseCls} ${color.source.bg} ${color.source.hoverBg}`;
const targetCls = `${baseCls} ${color.target.bg} ${color.target.hoverBg}`;

const sourceStyle: React.CSSProperties = { 
  filter: color.source.shadow, 
  zIndex: 10,
  background: '#3b82f6',
  border: '2px solid white'
};

const targetStyle: React.CSSProperties = { 
  filter: color.target.shadow, 
  zIndex: 10,
  background: '#10b981',
  border: '2px solid white'
};

/**
 * 4방향 핸들 배치 - React Flow 공식 문서에 따른 올바른 구현
 * 각 방향에 source와 target 핸들을 모두 생성하여 연결 가능하도록 함
 * - Left: source + target (겹치지 않도록 위치 조정)
 * - Right: source + target (겹치지 않도록 위치 조정)
 * - Top: source + target (겹치지 않도록 위치 조정)
 * - Bottom: source + target (겹치지 않도록 위치 조정)
 */
export const renderFourDirectionHandles = (isConnectable = true, nodeId?: string) => {
  const nodeIdStr = nodeId || 'node';
  
  const handleConfigs = [
    { 
      position: Position.Left, 
      sourceId: `${nodeIdStr}-left-source`,
      targetId: `${nodeIdStr}-left-target`,
      sourceStyle: { ...sourceStyle, left: -8 },
      targetStyle: { ...targetStyle, left: -8, top: 20 }
    },
    { 
      position: Position.Right, 
      sourceId: `${nodeIdStr}-right-source`,
      targetId: `${nodeIdStr}-right-target`,
      sourceStyle: { ...sourceStyle, right: -8 },
      targetStyle: { ...targetStyle, right: -8, top: 20 }
    },
    { 
      position: Position.Top, 
      sourceId: `${nodeIdStr}-top-source`,
      targetId: `${nodeIdStr}-top-target`,
      sourceStyle: { ...sourceStyle, top: -8 },
      targetStyle: { ...targetStyle, top: -8, left: 20 }
    },
    { 
      position: Position.Bottom, 
      sourceId: `${nodeIdStr}-bottom-source`,
      targetId: `${nodeIdStr}-bottom-target`,
      sourceStyle: { ...sourceStyle, bottom: -8 },
      targetStyle: { ...targetStyle, bottom: -8, left: 20 }
    },
  ];

  return handleConfigs.flatMap(({ position, sourceId, targetId, sourceStyle, targetStyle }) => [
    // Source 핸들
    <Handle
      key={sourceId}
      id={sourceId}
      type="source"
      position={position}
      isConnectable={isConnectable}
      className={sourceCls}
      style={sourceStyle}
    />,
    // Target 핸들
    <Handle
      key={targetId}
      id={targetId}
      type="target"
      position={position}
      isConnectable={isConnectable}
      className={targetCls}
      style={targetStyle}
    />
  ]);
};

/* 그룹 노드 등에서 쓸 기본 핸들 스타일 */
export const handleStyle = {
  background: '#3b82f6',
  width: 12,
  height: 12,
  border: '2px solid white',
  borderRadius: '50%',
};
