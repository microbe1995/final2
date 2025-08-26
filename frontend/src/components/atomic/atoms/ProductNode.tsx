'use client';

import React, { memo } from 'react';
import { NodeProps } from '@xyflow/react';
import { renderFourDirectionHandles } from './HandleStyles';

interface ProductNodeProps extends NodeProps {
  data: {
    label: string;
    description?: string;
    variant?: 'product';
    productData?: any;
    name?: string;
    type?: string;
    parameters?: Record<string, any>;
    status?: string;
    [key: string]: any;
  };
  onClick?: (node: any) => void;
  onDoubleClick?: (node: any) => void;
}

function ProductNode({ data, onClick, onDoubleClick, ...props }: ProductNodeProps) {
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onClick) {
      onClick(props);
    }
  };

  const handleDoubleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onDoubleClick) {
      onDoubleClick(props);
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  const handleClickEvent = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div
      className="bg-purple-50 border-2 border-purple-300 text-purple-800 px-4 py-3 rounded-lg shadow-md relative hover:shadow-lg transition-all duration-200 hover:scale-105 cursor-pointer min-w-[150px]"
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
    >
      {/* 4방향 핸들 렌더링 */}
      {renderFourDirectionHandles(true, handleMouseDown, handleClickEvent)}
      
      {/* 노드 내용 */}
      <div className="text-center">
        <div className="flex items-center justify-center mb-2">
          <span className="text-lg mr-2">📦</span>
          <h3 className="font-semibold text-sm">{data.label || data.name}</h3>
        </div>
        
        {data.description && (
          <p className="text-xs text-purple-600 mb-2">{data.description}</p>
        )}
        
        {/* 제품 데이터 표시 */}
        {data.productData && (
          <div className="text-xs space-y-1">
            <div className="flex justify-between">
              <span>생산량:</span>
              <span className="font-medium">{data.productData.production_qty || 0}</span>
            </div>
            <div className="flex justify-between">
              <span>수출량:</span>
              <span className="font-medium">{data.productData.export_qty || 0}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export { ProductNode };
export default memo(ProductNode);
