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
  // 대시보드 다크톤 + 블루 악센트
  default: 'bg-gray-800 border-blue-500 text-white',
  primary: 'bg-blue-500/10 border-blue-500 text-blue-100',
  success: 'bg-green-500/10 border-green-500 text-green-100',
  warning: 'bg-yellow-500/10 border-yellow-500 text-yellow-100',
  danger: 'bg-red-500/10 border-red-500 text-red-100',
  product: 'bg-purple-500/10 border-purple-400 text-purple-100',
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
    border-2 rounded-lg shadow-md relative transition-all duration-200
    ring-1 ring-blue-400/20 hover:ring-blue-400/60 hover:shadow-lg
    hover:scale-105 cursor-pointer
  `.trim();

  const handleClick = () => {
    // data에 onClick 함수가 있으면 먼저 실행
    if (data.onClick) {
      data.onClick();
      return;
    }
    // onClick이 없는 경우 기본 동작 없음 (향후 필요 시 확장)
    if (onClick) onClick({ data, selected });
  };

  const handleDoubleClick = () => {
    // data에 onDoubleClick 콜백이 존재하면 우선 실행 (공정 선택 모달 등)
    if (data.onDoubleClick) {
      data.onDoubleClick();
      return;
    }
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
      {finalShowHandles && renderFourDirectionHandles(isConnectable, data.nodeId || data.id)}

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
              <span className='font-medium'>{Number(data.product_amount ?? data.productData?.production_qty ?? 0).toLocaleString()} ton</span>
            </div>
            <div className='flex justify-between'>
              <span>제품 판매량:</span>
              <span className='font-medium'>{Number(data.product_sell ?? data.productData?.product_sell ?? 0).toLocaleString()} ton</span>
            </div>
            <div className='flex justify-between'>
              <span>EU 판매량:</span>
              <span className='font-medium'>{Number(data.product_eusell ?? data.productData?.product_eusell ?? 0).toLocaleString()} ton</span>
            </div>
            {data.has_produce_edge && typeof data.attr_em !== 'undefined' && (
              <div className='flex justify-between'>
                <span>배출량:</span>
                <span className='font-medium'>{Number(data.attr_em).toFixed(2)} tCO2e</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default memo(ProductNode);
