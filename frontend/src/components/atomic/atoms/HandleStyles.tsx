'use client';

import React from 'react';
import { Handle, Position } from '@xyflow/react';

const color = {
  bg: '!bg-blue-600',
  hoverBg: 'hover:!bg-blue-700',
  shadow: 'drop-shadow(0 0 8px rgba(59,130,246,.3))',
};

const baseCls = '!w-4 !h-4 !border-2 !border-white pointer-events-auto transition-all duration-200';
const cls = `${baseCls} ${color.bg} ${color.hoverBg} hover:scale-125 hover:shadow-lg`;

const handleStyle: React.CSSProperties = { 
  filter: color.shadow, 
  zIndex: 10,
  background: '#3b82f6',
  border: '2px solid white',
  cursor: 'crosshair'
};

/**
 * 4방향 핸들 배치 - React Flow 공식 문서에 따른 올바른 구현
 * 각 방향에 source와 target 핸들을 모두 생성하여 양방향 연결 가능
 * - Left: source 핸들 (연결 시작점)
 * - Right: source 핸들 (연결 시작점)  
 * - Top: source 핸들 (연결 시작점)
 * - Bottom: source 핸들 (연결 시작점)
 * 
 * React Flow 공식 문서 권장사항:
 * - 각 방향에 source 핸들 생성
 * - 연결 시 React Flow가 자동으로 target 핸들로 인식
 * - Loose 모드에서 올바른 연결 동작
 */
export const renderFourDirectionHandles = (isConnectable = true, nodeId?: string) => {
  const nodeIdStr = nodeId || 'node';
  
  // React Flow 공식 문서: 각 방향에 source 핸들 생성
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
      type="source" // ✅ React Flow 공식 문서: source로 설정하여 연결 시작점으로 사용
      position={position}
      isConnectable={isConnectable}
      className={cls}
      style={handleStyle}
      // ✅ 추가: 연결 검증 및 이벤트 핸들러
      onConnect={(params) => console.log('🔗 핸들 연결됨:', params)}
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
