'use client';

import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { renderFourDirectionHandles } from './HandleStyles';

interface ProductNodeProps {
  data: {
    label: string;
    description?: string;
    productData?: any; // 제품 데이터 추가
    [key: string]: any;
  };
  isConnectable?: boolean;
  // 🎯 유연한 핸들 설정
  targetPosition?: Position | Position[]; // 입력 핸들 위치(들)
  sourcePosition?: Position | Position[]; // 출력 핸들 위치(들)
  // 🎨 스타일 커스터마이징
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'product'; // product variant 추가
  size?: 'sm' | 'md' | 'lg';
  showHandles?: boolean; // 핸들 표시 여부
  // 🎯 이벤트 핸들러
  onClick?: (node: any) => void;
  onDoubleClick?: (node: any) => void;
  selected?: boolean;
}

// 🎨 스타일 변형
const variantStyles = {
  default: 'bg-white border-gray-800 text-gray-800',
  primary: 'bg-blue-50 border-blue-600 text-blue-900',
  success: 'bg-green-50 border-green-600 text-green-900',
  warning: 'bg-yellow-50 border-yellow-600 text-yellow-900',
  danger: 'bg-red-50 border-red-600 text-red-900',
  product: 'bg-purple-50 border-purple-300 text-purple-800', // 제품 노드 스타일 추가
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
  // data에서 props 추출 (React Flow 패턴)
  const finalVariant = variant || data.variant || 'default';
  const finalSize = size || data.size || 'md';
  const finalShowHandles =
    showHandles !== undefined
      ? showHandles
      : data.showHandles !== undefined
        ? data.showHandles
        : true;

  // 🎨 동적 스타일 생성
  const nodeClasses = `
    ${variantStyles[finalVariant as keyof typeof variantStyles]} 
    ${sizeStyles[finalSize as keyof typeof sizeStyles]}
    border-2 rounded-lg shadow-md relative hover:shadow-lg transition-all duration-200
    hover:scale-105 cursor-pointer
  `.trim();

  // 🎯 이벤트 핸들러
  const handleClick = () => {
    if (onClick) onClick({ data, selected });
  };

  const handleDoubleClick = () => {
    if (onDoubleClick) onDoubleClick({ data, selected });
  };

  // 🎯 핸들 이벤트 핸들러
  const handleMouseDown = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  const handleClickEvent = (e: React.MouseEvent) => {
    e.stopPropagation();
  };

  return (
    <div 
      className={`${nodeClasses} ${selected ? 'border-2 border-opacity-100 shadow-lg' : ''}`}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      style={{ cursor: data.productData ? 'pointer' : 'default' }}
    >
      {/* 🎯 4방향 모든 핸들 렌더링 (공통 스타일 사용) */}
      {finalShowHandles && (
        <>
          {/* 왼쪽 핸들들 */}
          <Handle
            type="target"
            position={Position.Left}
            id="left-target"
            isConnectable={isConnectable}
            className="!w-4 !h-4 !bg-blue-600 !border-2 !border-white hover:!bg-blue-700 hover:!scale-110 transition-all duration-200 cursor-crosshair"
            style={{ filter: 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.3))' }}
          />
          <Handle
            type="source"
            position={Position.Left}
            id="left-source"
            isConnectable={isConnectable}
            className="!w-4 !h-4 !bg-green-600 !border-2 !border-white hover:!bg-green-700 hover:!scale-110 transition-all duration-200 cursor-crosshair"
            style={{ filter: 'drop-shadow(0 0 8px rgba(34, 197, 94, 0.3))' }}
          />

          {/* 오른쪽 핸들들 */}
          <Handle
            type="target"
            position={Position.Right}
            id="right-target"
            isConnectable={isConnectable}
            className="!w-4 !h-4 !bg-blue-600 !border-2 !border-white hover:!bg-blue-700 hover:!scale-110 transition-all duration-200 cursor-crosshair"
            style={{ filter: 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.3))' }}
          />
          <Handle
            type="source"
            position={Position.Right}
            id="right-source"
            isConnectable={isConnectable}
            className="!w-4 !h-4 !bg-green-600 !border-2 !border-white hover:!bg-green-700 hover:!scale-110 transition-all duration-200 cursor-crosshair"
            style={{ filter: 'drop-shadow(0 0 8px rgba(34, 197, 94, 0.3))' }}
          />

          {/* 위쪽 핸들들 */}
          <Handle
            type="target"
            position={Position.Top}
            id="top-target"
            isConnectable={isConnectable}
            className="!w-4 !h-4 !bg-blue-600 !border-2 !border-white hover:!bg-blue-700 hover:!scale-110 transition-all duration-200 cursor-crosshair"
            style={{ filter: 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.3))' }}
          />
          <Handle
            type="source"
            position={Position.Top}
            id="top-source"
            isConnectable={isConnectable}
            className="!w-4 !h-4 !bg-green-600 !border-2 !border-white hover:!bg-green-700 hover:!scale-110 transition-all duration-200 cursor-crosshair"
            style={{ filter: 'drop-shadow(0 0 8px rgba(34, 197, 94, 0.3))' }}
          />

          {/* 아래쪽 핸들들 */}
          <Handle
            type="target"
            position={Position.Bottom}
            id="bottom-target"
            isConnectable={isConnectable}
            className="!w-4 !h-4 !bg-blue-600 !border-2 !border-white hover:!bg-blue-700 hover:!scale-110 transition-all duration-200 cursor-crosshair"
            style={{ filter: 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.3))' }}
          />
          <Handle
            type="source"
            position={Position.Bottom}
            id="bottom-source"
            isConnectable={isConnectable}
            className="!w-4 !h-4 !bg-green-600 !border-2 !border-white hover:!bg-green-700 hover:!scale-110 transition-all duration-200 cursor-crosshair"
            style={{ filter: 'drop-shadow(0 0 8px rgba(34, 197, 94, 0.3))' }}
          />
        </>
      )}

      {/* 🎯 노드 내용 */}
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

        {/* 🎯 제품 정보 미리보기 */}
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
