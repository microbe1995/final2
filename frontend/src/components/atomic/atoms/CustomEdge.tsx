'use client';

import React from 'react';

interface CustomEdgeProps {
  id: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  selected?: boolean;
}

const CustomEdge: React.FC<CustomEdgeProps> = ({ 
  id, 
  sourceX, 
  sourceY, 
  targetX, 
  targetY, 
  selected 
}) => {
  const [edgePath] = React.useMemo(() => {
    const centerX = (sourceX + targetX) / 2;
    const path = `M ${sourceX} ${sourceY} Q ${centerX} ${sourceY} ${targetX} ${targetY}`;
    return [path];
  }, [sourceX, sourceY, targetX, targetY]);

  return (
    <>
      {/* ✅ markerEnd 속성 제거 (중복 방지) */}
      <path 
        id={id} 
        className="react-flow__edge-path" 
        d={edgePath} 
        stroke={selected ? '#3b82f6' : '#6b7280'} 
        strokeWidth={selected ? 3 : 2} 
        fill="none" 
      />
    </>
  );
};

export default CustomEdge;
