'use client';

import React from 'react';
import { Handle, Position } from '@xyflow/react';

type HandleType = 'source' | 'target';

const color = {
  bg: '!bg-green-600',
  hoverBg: 'hover:!bg-green-700',
  ring: 'hover:!ring-green-300',
  shadow: 'drop-shadow(0 0 8px rgba(34,197,94,.3))',
};

const baseCls =
  '!w-4 !h-4 !border-2 !border-white transition-all duration-200 ' +
  'cursor-crosshair hover:!scale-110 hover:!shadow-lg hover:!ring-4 ' +
  'hover:!ring-opacity-50 pointer-events-auto';

const cls = `${baseCls} ${color.bg} ${color.hoverBg} ${color.ring}`;
const styleBase: React.CSSProperties = { filter: color.shadow, zIndex: 10 };

/**
 * 각 방향마다 source/target 두 개를 배치.
 * - Left/Right: 위아래로 살짝 분리
 * - Top/Bottom: 좌우로 살짝 분리
 */
export const renderFourDirectionHandles = (isConnectable = true) => {
  const gap = 10; // px 분리 간격

  const pairs: Array<{
    position: Position;
    items: Array<{ type: HandleType; idSuffix: string; style: React.CSSProperties }>;
  }> = [
    {
      position: Position.Left,
      items: [
        { type: 'target', idSuffix: 'target', style: { top: `calc(50% - ${gap}px)`, left: -8 } },
        { type: 'source', idSuffix: 'source', style: { top: `calc(50% + ${gap}px)`, left: -8 } },
      ],
    },
    {
      position: Position.Right,
      items: [
        { type: 'target', idSuffix: 'target', style: { top: `calc(50% - ${gap}px)`, right: -8 } },
        { type: 'source', idSuffix: 'source', style: { top: `calc(50% + ${gap}px)`, right: -8 } },
      ],
    },
    {
      position: Position.Top,
      items: [
        { type: 'target', idSuffix: 'target', style: { top: -8, left: `calc(50% - ${gap}px)` } },
        { type: 'source', idSuffix: 'source', style: { top: -8, left: `calc(50% + ${gap}px)` } },
      ],
    },
    {
      position: Position.Bottom,
      items: [
        { type: 'target', idSuffix: 'target', style: { bottom: -8, left: `calc(50% - ${gap}px)` } },
        { type: 'source', idSuffix: 'source', style: { bottom: -8, left: `calc(50% + ${gap}px)` } },
      ],
    },
  ];

  return pairs.flatMap(({ position, items }) =>
    items.map(({ type, idSuffix, style }) => {
      const id = `${position}-${idSuffix}`; // 예: "top-source"
      return (
        <Handle
          key={id}
          id={id}
          type={type}
          position={position}
          isConnectable={isConnectable}
          className={cls}
          style={{ ...styleBase, ...style }}
        />
      );
    })
  );
};

/* 그룹 노드 등에서 쓸 기본 핸들 스타일 */
export const handleStyle = {
  background: '#3b82f6',
  width: 12,
  height: 12,
  border: '2px solid white',
  borderRadius: '50%',
};
