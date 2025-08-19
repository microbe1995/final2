'use client';

import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

interface OutputNodeProps {
  data: {
    label: string;
    description?: string;
    [key: string]: any;
  };
  isConnectable?: boolean;
  targetPosition?: Position;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

// 🎨 스타일 변형
const variantStyles = {
  default: 'bg-gradient-to-r from-purple-500 to-purple-600 text-white',
  primary: 'bg-gradient-to-r from-blue-500 to-blue-600 text-white',
  success: 'bg-gradient-to-r from-green-500 to-green-600 text-white',
  warning: 'bg-gradient-to-r from-orange-500 to-orange-600 text-white',
  danger: 'bg-gradient-to-r from-red-500 to-red-600 text-white',
};

const sizeStyles = {
  sm: 'px-3 py-2 min-w-[100px] text-xs',
  md: 'px-4 py-3 min-w-[120px] text-sm',
  lg: 'px-6 py-4 min-w-[160px] text-base',
};

function OutputNode({ 
  data, 
  isConnectable = true,
  targetPosition = Position.Top,
  variant = 'default',
  size = 'md'
}: OutputNodeProps) {
  
  // data에서 props 추출
  const finalTargetPosition = data.targetPosition || targetPosition;
  const finalVariant = data.variant || variant;
  const finalSize = data.size || size;

  // 🎨 동적 스타일 생성
  const nodeClasses = `
    ${variantStyles[finalVariant as keyof typeof variantStyles]} 
    ${sizeStyles[finalSize as keyof typeof sizeStyles]}
    rounded-full shadow-lg relative hover:shadow-xl transition-all duration-200
    hover:scale-105 cursor-pointer font-semibold
    flex items-center justify-center
  `.trim();

  // 🎯 핸들 스타일
  const handleStyle = "!w-4 !h-4 !bg-white !border-2 !border-current transition-all hover:!scale-110";

  return (
    <div className={nodeClasses}>
      {/* 🎯 입력 핸들 */}
      <Handle
        type="target"
        position={finalTargetPosition}
        isConnectable={isConnectable}
        className={handleStyle}
      />

      {/* 📍 출력 표시 아이콘 */}
      <div className="flex items-center gap-2">
        <div className="text-center">
          <div>{data.label}</div>
          {data.description && (
            <div className="text-xs opacity-80">{data.description}</div>
          )}
        </div>
        <span className="text-lg">📤</span>
      </div>
    </div>
  );
}

export { OutputNode };
export default memo(OutputNode);
