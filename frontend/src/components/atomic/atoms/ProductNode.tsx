'use client';

import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { renderFourDirectionHandles } from './HandleStyles';

interface ProductNodeProps {
  data: {
    label: string;
    description?: string;
    productData?: any;
    [key: string]: any;
  };
  isConnectable?: boolean;
  targetPosition?: Position | Position[];
  sourcePosition?: Position | Position[];
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'product';
  size?: 'sm' | 'md' | 'lg';
  showHandles?: boolean;
  onClick?: (node: any) => void;
  onDoubleClick?: (node: any) => void;
  selected?: boolean;
}

const variantStyles = {
  default: 'bg-white border-gray-800 text-gray-800',
  primary: 'bg-blue-50 border-blue-600 text-blue-900',
  success: 'bg-green-50 border-green-600 text-green-900',
  warning: 'bg-yellow-50 border-yellow-600 text-yellow-900',
  danger: 'bg-red-50 border-red-600 text-red-900',
  product: 'bg-purple-50 border-purple-300 text-purple-800',
};

const sizeStyles = {
  sm: 'px-2 py-1 min-w-[80px] text-xs',
  md: 'px-4 py-3 min-w-[120px] text-sm',
  lg: 'px-6 py-4 min-w-[160px] text-base',
};

function ProductNode({
  data,
  isConnectable = true,
  targetPosition,
  sourcePosition,
  variant,
  size,
  showHandles,
  onClick,
  onDoubleClick,
  selected,
}: ProductNodeProps) {
  const finalVariant = variant || data.variant || 'default';
  const finalSize = size || data.size || 'md';
  const finalShowHandles =
    showHandles !== undefined
      ? showHandles
      : data.showHandles !== undefined
        ? data.showHandles
        : true;

  const nodeClasses = `
    ${variantStyles[finalVariant as keyof typeof variantStyles]} 
    ${sizeStyles[finalSize as keyof typeof sizeStyles]}
    border-2 rounded-lg shadow-md relative hover:shadow-lg transition-all duration-200
    hover:scale-105 cursor-pointer
  `.trim();

  const handleClick = () => {
    if (onClick) onClick({ data, selected });
  };

  const handleDoubleClick = () => {
    if (onDoubleClick) onDoubleClick({ data, selected });
  };

  return (
    <div 
      className={`${nodeClasses} ${selected ? 'border-2 border-opacity-100 shadow-lg' : ''}`}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      style={{ 
        cursor: data.productData ? 'pointer' : 'default',
        pointerEvents: 'auto' // ✅ pointerEvents 문제 해결
      }}
    >
      {/* 🎯 4방향 핸들 - HandleStyles.tsx 함수 사용 */}
      {finalShowHandles && renderFourDirectionHandles(isConnectable)}

      {/* 노드 내용 */}
      <div className='text-center'>
        <div
          className={`font-semibold mb-1 ${finalSize === 'lg' ? 'text-lg' : finalSize === 'sm' ? 'text-xs' : 'text-sm'}`}
        >
          {finalVariant === 'product' ? '📦 ' : ''}{data.label}
        </div>
        {data.description && (
          <div
            className={`text-opacity-70 ${finalSize === 'lg' ? 'text-sm' : 'text-xs'}`}
          >
            {data.description}
          </div>
        )}

        {/* 제품 정보 미리보기 */}
        {data.productData && finalVariant === 'product' && (
          <div className='text-xs opacity-60 mt-2'>
            <div className='flex justify-between'>
              <span>생산량:</span>
              <span className='font-medium'>{data.productData.production_qty || 0}</span>
            </div>
            <div className='flex justify-between'>
              <span>수출량:</span>
              <span className='font-medium'>{data.productData.export_qty || 0}</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default memo(ProductNode);
