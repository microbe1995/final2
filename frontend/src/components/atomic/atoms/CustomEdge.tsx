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
    // 부드러운 곡선 생성
    const centerX = (sourceX + targetX) / 2;
    const centerY = (sourceY + targetY) / 2;
    
    // 거리에 따라 곡선 강도 조절
    const distance = Math.sqrt(Math.pow(targetX - sourceX, 2) + Math.pow(targetY - sourceY, 2));
    const curveStrength = Math.min(distance * 0.3, 60);
    
    const path = `M ${sourceX} ${sourceY} Q ${centerX} ${sourceY + curveStrength} ${targetX} ${targetY}`;
    
    // 화살표 생성 (target 쪽에 위치)
    const arrowLength = 14;
    const arrowWidth = 10;
    
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

  // ✅ React Flow 공식 문서: 임시 엣지와 실제 엣지 구분
  const isTemporary = data?.isTemporary || false;
  const isRealEdge = data?.edgeData && !isTemporary;

  // ✅ 중복 렌더링 방지: 실제 엣지만 표시
  if (!isRealEdge && !isTemporary) {
    return null;
  }

  // 색상 설정
  const strokeColor = selected ? '#3b82f6' : isTemporary ? '#6b7280' : '#64748b';
  const strokeWidth = selected ? 8 : isTemporary ? 6 : 6;

  return (
    <>
      {/* 메인 엣지 경로 */}
      <path 
        id={id} 
        className="react-flow__edge-path" 
        d={edgePath} 
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeLinecap="round"
        strokeDasharray={isTemporary ? '8,8' : 'none'}
        fill="none" 
        style={{
          transition: 'all 0.2s ease-in-out',
          filter: selected ? 'drop-shadow(0 0 6px rgba(59, 130, 246, 0.6))' : 'none'
        }}
      />
      
      {/* 화살표 */}
      <path
        d={arrowPath}
        fill={strokeColor}
        stroke="none"
        style={{
          transition: 'all 0.2s ease-in-out'
        }}
      />
    </>
  );
};

export default CustomEdge;
