'use client';

import React from 'react';
import { EdgeLabelRenderer } from '@xyflow/react';
interface ProcessEdgeLabelProps {
  labelX: number;
  labelY: number;
  data: any; // 백엔드 API 응답을 그대로 사용
  className?: string;
}

const ProcessEdgeLabel: React.FC<ProcessEdgeLabelProps> = ({
  labelX,
  labelY,
  data,
  className = ''
}) => {
  const baseClasses = 'bg-[#1e293b] border border-[#334155] px-2 py-1 rounded shadow-sm text-white';
  const finalClasses = `${baseClasses} ${className}`.trim();

  const getProcessTypeIcon = (type: string) => {
    switch (type) {
      case 'critical':
        return '⚠️ 중요';
      case 'optional':
        return '⚪ 선택';
      case 'standard':
        return '➡️ 표준';
      default:
        return '➡️ 표준';
    }
  };

  return (
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
        <div className={finalClasses}>
          <span className="text-xs text-gray-700">
            {data?.label || '공정 흐름'}
          </span>
          {data?.processType && (
            <div className="text-xs text-gray-500">
              {getProcessTypeIcon(data.processType)}
            </div>
          )}
        </div>
      </div>
    </EdgeLabelRenderer>
  );
};

export default ProcessEdgeLabel;
