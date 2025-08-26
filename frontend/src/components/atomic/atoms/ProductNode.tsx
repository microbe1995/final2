'use client';

import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

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
  const finalTargetPosition =
    targetPosition || data.targetPosition || Position.Top;
  const finalSourcePosition =
    sourcePosition || data.sourcePosition || Position.Bottom;
  const finalVariant = variant || data.variant || 'default';
  const finalSize = size || data.size || 'md';
  const finalShowHandles =
    showHandles !== undefined
      ? showHandles
      : data.showHandles !== undefined
        ? data.showHandles
        : true;

  // 🔧 핸들 위치를 배열로 정규화
  const normalizePositions = (pos: Position | Position[]): Position[] => {
    return Array.isArray(pos) ? pos : [pos];
  };

  const targetPositions = normalizePositions(finalTargetPosition);
  const sourcePositions = normalizePositions(finalSourcePosition);

  // 🎨 동적 스타일 생성
  const nodeClasses = `
    ${variantStyles[finalVariant as keyof typeof variantStyles]} 
    ${sizeStyles[finalSize as keyof typeof sizeStyles]}
    border-2 rounded-lg shadow-md relative hover:shadow-lg transition-all duration-200
    hover:scale-105 cursor-pointer
  `.trim();

  // 🎯 핸들 스타일 (variant에 따라 색상 변경)
  const getHandleStyle = (type: 'source' | 'target') => {
    const baseStyle = '!w-4 !h-4 !border-2 !border-white transition-all duration-200 cursor-crosshair hover:!scale-110 hover:!shadow-lg hover:!ring-4 hover:!ring-opacity-50 pointer-events-auto';

    switch (finalVariant) {
      case 'primary':
        return `${baseStyle} !bg-blue-600 hover:!bg-blue-700 hover:!ring-blue-300`;
      case 'success':
        return `${baseStyle} !bg-green-600 hover:!bg-green-700 hover:!ring-green-300`;
      case 'warning':
        return `${baseStyle} !bg-yellow-600 hover:!bg-yellow-700 hover:!ring-yellow-300`;
      case 'danger':
        return `${baseStyle} !bg-red-600 hover:!bg-red-700 hover:!ring-red-300`;
      case 'product':
        return `${baseStyle} !bg-purple-600 hover:!bg-purple-700 hover:!ring-purple-300`;
      default:
        return `${baseStyle} !bg-gray-600 hover:!bg-gray-700 hover:!ring-gray-300`;
    }
  };

  // 🎯 이벤트 핸들러
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
      style={{ cursor: data.productData ? 'pointer' : 'default' }}
    >
      {/* 🎯 Target 핸들들 렌더링 */}
      {finalShowHandles &&
        targetPositions.map((position, index) => (
          <Handle
            key={`target-${position}-${index}`}
            type='target'
            position={position}
            isConnectable={isConnectable}
            className={getHandleStyle('target')}
            style={{ filter: 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.3))' }}
            onMouseDown={(e) => e.stopPropagation()}
            onClick={(e) => e.stopPropagation()}
            id={targetPositions.length > 1 ? `target-${position}` : undefined}
          />
        ))}

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

      {/* 🎯 Source 핸들들 렌더링 */}
      {finalShowHandles &&
        sourcePositions.map((position, index) => (
          <Handle
            key={`source-${position}-${index}`}
            type='source'
            position={position}
            isConnectable={isConnectable}
            className={getHandleStyle('source')}
            style={{ filter: 'drop-shadow(0 0 8px rgba(34, 197, 94, 0.3))' }}
            onMouseDown={(e) => e.stopPropagation()}
            onClick={(e) => e.stopPropagation()}
            id={sourcePositions.length > 1 ? `source-${position}` : undefined}
          />
        ))}
    </div>
  );
}

export { ProductNode };
export default memo(ProductNode);
