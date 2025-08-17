'use client';

import React from 'react';
import { BaseEdge, getBezierPath, EdgeProps } from '@xyflow/react';

import ProcessEdgeLabel from '../molecules/ProcessEdgeLabel';
import type { ProcessEdgeData } from '@/types/reactFlow';

// ============================================================================
// 🎯 ProcessEdge 컴포넌트
// ============================================================================

const ProcessEdge: React.FC<EdgeProps<any>> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
}) => {
  const [edgePath, labelX, labelY] = getBezierPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const getEdgeColor = (type: string) => {
    switch (type) {
      case 'standard':
        return selected ? '#3b82f6' : '#6b7280';
      case 'conditional':
        return selected ? '#ef4444' : '#dc2626';
      case 'parallel':
        return selected ? '#10b981' : '#059669';
      case 'sequential':
        return selected ? '#f59e0b' : '#d97706';
      default:
        return selected ? '#3b82f6' : '#6b7280';
    }
  };

  const getEdgeStyle = (type: string) => {
    switch (type) {
      case 'conditional':
        return 'stroke-dasharray-5,5';
      case 'parallel':
        return 'stroke-dasharray-2,2';
      default:
        return '';
    }
  };

  const edgeData = data || { label: '공정 흐름', processType: 'standard' };

  return (
    <>
      <BaseEdge
        path={edgePath}
        className={`${getEdgeStyle(edgeData.processType)}`}
        style={{
          stroke: getEdgeColor(edgeData.processType),
          strokeWidth: selected ? 3 : 2,
        }}
      />
      
      <ProcessEdgeLabel
        labelX={labelX}
        labelY={labelY}
        data={edgeData}
      />
    </>
  );
};

export default ProcessEdge;
