'use client';

import React from 'react';
import { BaseEdge, getBezierPath, EdgeProps } from '@xyflow/react';

import ProcessEdgeLabel from '../molecules/ProcessEdgeLabel';

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
      case 'critical':
        return selected ? '#ef4444' : '#dc2626';
      case 'optional':
        return selected ? '#10b981' : '#059669';
      default:
        return selected ? '#3b82f6' : '#6b7280';
    }
  };

  const getEdgeStyle = (type: string) => {
    switch (type) {
      case 'critical':
        return 'stroke-dasharray-5,5';
      case 'optional':
        return 'stroke-dasharray-2,2';
      default:
        return '';
    }
  };

  return (
    <>
      <BaseEdge
        path={edgePath}
        className={`${getEdgeStyle(data?.processType || 'standard')}`}
        style={{
          stroke: getEdgeColor(data?.processType || 'standard'),
          strokeWidth: selected ? 3 : 2,
        }}
      />
      
      <ProcessEdgeLabel
        labelX={labelX}
        labelY={labelY}
        data={data || { label: '공정 흐름', processType: 'standard' }}
      />
    </>
  );
};

export default ProcessEdge;
