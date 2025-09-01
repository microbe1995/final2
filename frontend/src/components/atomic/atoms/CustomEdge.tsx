'use client';

import React from 'react';

interface CustomEdgeProps {
  id: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  selected?: boolean;
  data?: any;
}

const CustomEdge: React.FC<CustomEdgeProps> = ({ 
  id, 
  sourceX, 
  sourceY, 
  targetX, 
  targetY, 
  selected,
  data
}) => {
  const [edgePath, arrowPath] = React.useMemo(() => {
    // React Flow 공식 문서에 따른 부드러운 곡선 생성
    const centerX = (sourceX + targetX) / 2;
    const centerY = (sourceY + targetY) / 2;
    
    // 거리에 따라 곡선 강도 조절
    const distance = Math.sqrt(Math.pow(targetX - sourceX, 2) + Math.pow(targetY - sourceY, 2));
    const curveStrength = Math.min(distance * 0.3, 50);
    
    const path = `M ${sourceX} ${sourceY} Q ${centerX} ${sourceY + curveStrength} ${targetX} ${targetY}`;
    
    // 화살표 생성 (target 쪽에 위치)
    const arrowLength = 12; // 화살표 길이
    const arrowWidth = 8;   // 화살표 너비
    
    // target에서 약간 뒤로 이동한 지점 계산
    const dx = targetX - centerX;
    const dy = targetY - centerY;
    const angle = Math.atan2(dy, dx);
    
    // 화살표 위치 (target에서 약간 뒤로)
    const arrowX = targetX - arrowLength * Math.cos(angle);
    const arrowY = targetY - arrowLength * Math.sin(angle);
    
    // 화살표 경로
    const arrowPath = `M ${arrowX - arrowWidth * Math.cos(angle - Math.PI/6)} ${arrowY - arrowWidth * Math.sin(angle - Math.PI/6)} 
                       L ${targetX} ${targetY} 
                       L ${arrowX - arrowWidth * Math.cos(angle + Math.PI/6)} ${arrowY - arrowWidth * Math.sin(angle + Math.PI/6)} Z`;
    
    return [path, arrowPath];
  }, [sourceX, sourceY, targetX, targetY]);

  // 임시 Edge인지 확인
  const isTemporary = data?.isTemporary || false;

  return (
    <g>
      {/* 메인 엣지 경로 */}
      <path 
        id={id} 
        className="react-flow__edge-path" 
        d={edgePath} 
        stroke={selected ? '#3b82f6' : isTemporary ? '#6b7280' : '#64748b'} 
        strokeWidth={selected ? 9 : isTemporary ? 6 : 6} // 3배 증가: 2-3 → 6-9
        strokeDasharray={isTemporary ? '5,5' : 'none'}
        fill="none" 
        style={{
          transition: 'stroke 0.2s ease-in-out, stroke-width 0.2s ease-in-out'
        }}
      />
      
      {/* 화살표 (단방향 흐름 표시) */}
      <path
        d={arrowPath}
        fill={selected ? '#3b82f6' : isTemporary ? '#6b7280' : '#64748b'}
        stroke="none"
        style={{
          transition: 'fill 0.2s ease-in-out'
        }}
      />
    </g>
  );
};

export default CustomEdge;
