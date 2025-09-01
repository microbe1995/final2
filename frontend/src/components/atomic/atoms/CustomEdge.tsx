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
  const [edgePath, arrowPath, glowPath] = React.useMemo(() => {
    // React Flow 공식 문서에 따른 부드러운 곡선 생성
    const centerX = (sourceX + targetX) / 2;
    const centerY = (sourceY + targetY) / 2;
    
    // 거리에 따라 곡선 강도 조절
    const distance = Math.sqrt(Math.pow(targetX - sourceX, 2) + Math.pow(targetY - sourceY, 2));
    const curveStrength = Math.min(distance * 0.4, 80); // 곡선 강도 증가
    
    const path = `M ${sourceX} ${sourceY} Q ${centerX} ${sourceY + curveStrength} ${targetX} ${targetY}`;
    
    // 화살표 생성 (target 쪽에 위치)
    const arrowLength = 16; // 화살표 길이 증가
    const arrowWidth = 12;  // 화살표 너비 증가
    
    // target에서 약간 뒤로 이동한 지점 계산
    const dx = targetX - centerX;
    const dy = targetY - centerY;
    const angle = Math.atan2(dy, dx);
    
    // 화살표 위치 (target에서 약간 뒤로)
    const arrowX = targetX - arrowLength * Math.cos(angle);
    const arrowY = targetY - arrowLength * Math.sin(angle);
    
    // 화살표 경로 (더 부드러운 곡선)
    const arrowPath = `M ${arrowX - arrowWidth * Math.cos(angle - Math.PI/6)} ${arrowY - arrowWidth * Math.sin(angle - Math.PI/6)} 
                       Q ${arrowX} ${arrowY} ${targetX} ${targetY}
                       Q ${arrowX} ${arrowY} ${arrowX - arrowWidth * Math.cos(angle + Math.PI/6)} ${arrowY - arrowWidth * Math.sin(angle + Math.PI/6)} Z`;
    
    // 글로우 효과를 위한 더 굵은 경로
    const glowPath = `M ${sourceX} ${sourceY} Q ${centerX} ${sourceY + curveStrength} ${targetX} ${targetY}`;
    
    return [path, arrowPath, glowPath];
  }, [sourceX, sourceY, targetX, targetY]);

  // 임시 Edge인지 확인
  const isTemporary = data?.isTemporary || false;

  // 고급스러운 색상 팔레트
  const colors = {
    primary: selected ? '#60a5fa' : '#3b82f6',
    secondary: selected ? '#93c5fd' : '#64748b',
    accent: selected ? '#dbeafe' : '#e2e8f0',
    glow: selected ? '#3b82f6' : '#64748b'
  };

  return (
    <g>
      {/* 글로우 효과 (그림자) */}
      <defs>
        <filter id={`glow-${id}`} x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="4" result="coloredBlur"/>
          <feMerge> 
            <feMergeNode in="coloredBlur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
        
        {/* 그라데이션 정의 */}
        <linearGradient id={`gradient-${id}`} x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={colors.primary} stopOpacity="0.8"/>
          <stop offset="50%" stopColor={colors.secondary} stopOpacity="1"/>
          <stop offset="100%" stopColor={colors.accent} stopOpacity="0.8"/>
        </linearGradient>
      </defs>

      {/* 글로우 효과 (배경) */}
      <path 
        d={glowPath}
        stroke={colors.glow}
        strokeWidth={selected ? 16 : 12} // 글로우 효과
        strokeOpacity="0.3"
        fill="none"
        filter={`url(#glow-${id})`}
      />

      {/* 메인 엣지 경로 (그라데이션) */}
      <path 
        id={id} 
        className="react-flow__edge-path" 
        d={edgePath} 
        stroke={`url(#gradient-${id})`}
        strokeWidth={selected ? 10 : 8} // 굵기 증가
        strokeLinecap="round"
        strokeDasharray={isTemporary ? '8,8' : 'none'}
        fill="none" 
        style={{
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          filter: selected ? 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.6))' : 'none'
        }}
      />
      
      {/* 화살표 (고급스러운 디자인) */}
      <path
        d={arrowPath}
        fill={`url(#gradient-${id})`}
        stroke={colors.primary}
        strokeWidth="1"
        style={{
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          filter: selected ? 'drop-shadow(0 0 4px rgba(59, 130, 246, 0.8))' : 'none'
        }}
      />

      {/* 선택 상태일 때 추가 하이라이트 */}
      {selected && (
        <path
          d={edgePath}
          stroke={colors.primary}
          strokeWidth="2"
          strokeOpacity="0.6"
          fill="none"
          strokeDasharray="4,4"
          style={{
            animation: 'dash 2s linear infinite',
            transition: 'all 0.3s ease'
          }}
        />
      )}
    </g>
  );
};

export default CustomEdge;
