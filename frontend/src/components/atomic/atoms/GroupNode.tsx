'use client';

import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { renderFourDirectionHandles } from './HandleStyles';

interface GroupNodeProps {
  data: {
    label: string;
    description?: string;
    width?: number;
    height?: number;
    [key: string]: any;
  };
  isConnectable?: boolean;
  selected?: boolean;
  children?: React.ReactNode;
}

function GroupNode({
  data,
  isConnectable = true,
  selected,
  children,
}: GroupNodeProps) {
  const width = data.width || 300;
  const height = data.height || 200;

  return (
    <div
      className={`
        bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg
        ${selected ? 'border-blue-500 bg-blue-50' : ''}
        transition-all duration-200
      `}
      style={{
        width: `${width}px`,
        height: `${height}px`,
        position: 'relative',
      }}
    >
      {/* 그룹 노드 자체의 핸들 (외부 연결용) */}
      {renderFourDirectionHandles(isConnectable)}

      {/* 그룹 헤더 */}
      <div className="absolute top-0 left-0 right-0 bg-gray-100 px-3 py-2 rounded-t-lg border-b border-gray-300">
        <div className="flex items-center justify-between">
          <span className="font-semibold text-sm text-gray-700">
            📁 {data.label}
          </span>
          <span className="text-xs text-gray-500">
            {data.description}
          </span>
        </div>
      </div>

      {/* 자식 노드들이 렌더링될 영역 */}
      <div className="absolute top-12 left-0 right-0 bottom-0 p-4">
        {children}
      </div>
    </div>
  );
}

export { GroupNode };
export default memo(GroupNode);
