'use client';

import React from 'react';

interface CustomEdgeProps {
  id: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  sourceHandle?: string;
  targetHandle?: string;
  selected?: boolean;
  data?: any;
}

const CustomEdge: React.FC<CustomEdgeProps> = ({ 
  id, 
  sourceX, 
  sourceY, 
  targetX, 
  targetY, 
  sourceHandle,
  targetHandle,
  selected,
  data
}) => {
  const [edgePath] = React.useMemo(() => {
    // 4방향 연결을 위한 더 부드러운 곡선 생성
    const centerX = (sourceX + targetX) / 2;
    const centerY = (sourceY + targetY) / 2;
    
    // 거리에 따라 곡선 강도 조절
    const distance = Math.sqrt(Math.pow(targetX - sourceX, 2) + Math.pow(targetY - sourceY, 2));
    const curveStrength = Math.min(distance * 0.3, 50);
    
    const path = `M ${sourceX} ${sourceY} Q ${centerX} ${sourceY + curveStrength} ${targetX} ${targetY}`;
    return [path];
  }, [sourceX, sourceY, targetX, targetY]);

  // 임시 Edge인지 확인
  const isTemporary = data?.isTemporary || false;

  return (
    <>
      <path 
        id={id} 
        className="react-flow__edge-path" 
        d={edgePath} 
        stroke={selected ? '#3b82f6' : isTemporary ? '#6b7280' : '#3b82f6'} 
        strokeWidth={selected ? 3 : isTemporary ? 2 : 2} 
        strokeDasharray={isTemporary ? '5,5' : 'none'}
        fill="none" 
        style={{
          transition: 'stroke 0.2s ease-in-out, stroke-width 0.2s ease-in-out'
        }}
      />
    </>
  );
};

export default CustomEdge;
