'use client';

import React, { useMemo } from 'react';
import { BaseEdge, EdgeLabelRenderer, getBezierPath } from '@xyflow/react';
import { EdgeProps } from '@xyflow/react';

interface SourceStreamData {
  streamType: 'material' | 'energy' | 'carbon' | 'waste';
  flowRate: number;
  unit: string;
  carbonIntensity?: number;
  description?: string;
}

const SourceStreamEdge: React.FC<EdgeProps<any>> = ({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
  selected,
  style,
}) => {
  const [edgePath, labelX, labelY] = useMemo(() => {
    return getBezierPath({
      sourceX,
      sourceY,
      sourcePosition,
      targetX,
      targetY,
      targetPosition,
    });
  }, [sourceX, sourceY, sourcePosition, targetX, targetY, targetPosition]);

  const getEdgeColor = () => {
    if (!data) return selected ? '#3b82f6' : '#6b7280';
    
    switch (data.streamType) {
      case 'material':
        return selected ? '#10b981' : '#059669';
      case 'energy':
        return selected ? '#f59e0b' : '#d97706';
      case 'carbon':
        return selected ? '#ef4444' : '#dc2626';
      case 'waste':
        return selected ? '#8b5cf6' : '#7c3aed';
      default:
        return selected ? '#3b82f6' : '#6b7280';
    }
  };

  const getEdgeWidth = () => {
    if (!data) return selected ? 3 : 2;
    
    // 흐름량에 따라 선 굵기 조정
    const flowRate = data.flowRate || 0;
    if (flowRate > 1000) return selected ? 5 : 4;
    if (flowRate > 100) return selected ? 4 : 3;
    if (flowRate > 10) return selected ? 3 : 2;
    return selected ? 2 : 1;
  };

  const getStreamIcon = () => {
    if (!data) return '→';
    
    switch (data.streamType) {
      case 'material':
        return '📦';
      case 'energy':
        return '⚡';
      case 'carbon':
        return '🌱';
      case 'waste':
        return '♻️';
      default:
        return '→';
    }
  };

  return (
    <>
      <BaseEdge
        id={id}
        path={edgePath}
        style={{
          ...style,
          stroke: getEdgeColor(),
          strokeWidth: getEdgeWidth(),
        }}
      />
      
      {/* 엣지 라벨 */}
      <EdgeLabelRenderer>
        <div
          style={{
            position: 'absolute',
            transform: `translate(-50%, -50%) translate(${labelX}px,${labelY}px)`,
            fontSize: 12,
            pointerEvents: 'all',
          }}
          className="nodrag nopan"
        >
          <div className="bg-white border border-gray-300 rounded-lg px-2 py-1 shadow-lg">
            <div className="flex items-center gap-1">
              <span>{getStreamIcon()}</span>
              <span className="font-medium">
                {data?.flowRate || 0} {data?.unit || 'unit'}
              </span>
            </div>
            {data?.description && (
              <div className="text-xs text-gray-600 mt-1">
                {data.description}
              </div>
            )}
            {data?.carbonIntensity && (
              <div className="text-xs text-red-600 mt-1">
                {data.carbonIntensity} kgCO2/t
              </div>
            )}
          </div>
        </div>
      </EdgeLabelRenderer>
      
      {/* 흐름 방향 화살표 */}
      <defs>
        <marker
          id={`arrow-${id}`}
          viewBox="0 0 10 10"
          refX="5"
          refY="3"
          markerWidth="6"
          markerHeight="6"
          orient="auto"
        >
          <path
            d="M 0 0 L 0 6 L 6 3 z"
            fill={getEdgeColor()}
          />
        </marker>
      </defs>
    </>
  );
};

export default SourceStreamEdge;
