'use client';

import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

interface ProcessNodeProps {
  data: {
    label: string;
    description?: string;
    [key: string]: any;
  };
  isConnectable?: boolean;
  // 🎯 유연한 핸들 설정
  targetPosition?: Position | Position[];  // 입력 핸들 위치(들)
  sourcePosition?: Position | Position[];  // 출력 핸들 위치(들)
  // 🎨 스타일 커스터마이징
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  showHandles?: boolean;  // 핸들 표시 여부
}

// 🎨 스타일 변형
const variantStyles = {
  default: 'bg-white border-gray-800 text-gray-800',
  primary: 'bg-blue-50 border-blue-600 text-blue-900',
  success: 'bg-green-50 border-green-600 text-green-900',
  warning: 'bg-yellow-50 border-yellow-600 text-yellow-900',
  danger: 'bg-red-50 border-red-600 text-red-900',
};

const sizeStyles = {
  sm: 'px-2 py-1 min-w-[80px] text-xs',
  md: 'px-4 py-3 min-w-[120px] text-sm',
  lg: 'px-6 py-4 min-w-[160px] text-base',
};

function ProcessNode({ 
  data, 
  isConnectable = true,
  targetPosition,
  sourcePosition,
  variant,
  size,
  showHandles
}: ProcessNodeProps) {
  
  // data에서 props 추출 (React Flow 패턴)
  const finalTargetPosition = targetPosition || data.targetPosition || Position.Top;
  const finalSourcePosition = sourcePosition || data.sourcePosition || Position.Bottom;
  const finalVariant = variant || data.variant || 'default';
  const finalSize = size || data.size || 'md';
  const finalShowHandles = showHandles !== undefined ? showHandles : (data.showHandles !== undefined ? data.showHandles : true);
  
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
    const baseStyle = "!w-3 !h-3 !border-2 !border-white transition-colors";
    
    switch (finalVariant) {
      case 'primary': return `${baseStyle} !bg-blue-600 hover:!bg-blue-700`;
      case 'success': return `${baseStyle} !bg-green-600 hover:!bg-green-700`;
      case 'warning': return `${baseStyle} !bg-yellow-600 hover:!bg-yellow-700`;
      case 'danger': return `${baseStyle} !bg-red-600 hover:!bg-red-700`;
      default: return `${baseStyle} !bg-gray-600 hover:!bg-gray-700`;
    }
  };

  return (
    <div className={nodeClasses}>
      {/* 🎯 Target 핸들들 렌더링 */}
      {finalShowHandles && targetPositions.map((position, index) => (
        <Handle
          key={`target-${position}-${index}`}
          type="target"
          position={position}
          isConnectable={isConnectable}
          className={getHandleStyle('target')}
          id={targetPositions.length > 1 ? `target-${position}` : undefined}
        />
      ))}

      {/* 🎯 노드 내용 */}
      <div className="text-center">
        <div className={`font-semibold mb-1 ${finalSize === 'lg' ? 'text-lg' : finalSize === 'sm' ? 'text-xs' : 'text-sm'}`}>
          {data.label}
        </div>
        {data.description && (
          <div className={`text-opacity-70 ${finalSize === 'lg' ? 'text-sm' : 'text-xs'}`}>
            {data.description}
          </div>
        )}
      </div>

      {/* 🎯 Source 핸들들 렌더링 */}
      {finalShowHandles && sourcePositions.map((position, index) => (
        <Handle
          key={`source-${position}-${index}`}
          type="source"
          position={position}
          isConnectable={isConnectable}
          className={getHandleStyle('source')}
          id={sourcePositions.length > 1 ? `source-${position}` : undefined}
        />
      ))}
    </div>
  );
}

export { ProcessNode };
export default memo(ProcessNode);