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
 * 4방향 핸들 배치 - React Flow 공식 문서에 따른 올바른 구현
 * 각 방향에 source와 target 핸들을 모두 생성하여 연결 가능하도록 함
 * - Left: source + target
 * - Right: source + target  
 * - Top: source + target
 * - Bottom: source + target
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
    <React.Fragment key={id}>
      {/* Source 핸들 */}
      <Handle
        id={`${id}-source`}
        type="source"
        position={position}
        isConnectable={isConnectable}
        className={cls}
        style={sourceStyle}
      />
      {/* Target 핸들 */}
      <Handle
        id={`${id}-target`}
        type="target"
        position={position}
        isConnectable={isConnectable}
        className={cls}
        style={targetStyle}
      />
    </React.Fragment>
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
