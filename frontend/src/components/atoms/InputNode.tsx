'use client';

import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

interface InputNodeProps {
  data: {
    label: string;
    description?: string;
    [key: string]: any;
  };
  isConnectable?: boolean;
  sourcePosition?: Position;
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  size?: 'sm' | 'md' | 'lg';
}

// 🎨 스타일 변형
const variantStyles = {
  default: 'bg-gradient-to-r from-blue-500 to-blue-600 text-white',
  primary: 'bg-gradient-to-r from-indigo-500 to-indigo-600 text-white',
  success: 'bg-gradient-to-r from-green-500 to-green-600 text-white',
  warning: 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-white',
  danger: 'bg-gradient-to-r from-red-500 to-red-600 text-white',
};

const sizeStyles = {
  sm: 'px-3 py-2 min-w-[100px] text-xs',
  md: 'px-4 py-3 min-w-[120px] text-sm',
  lg: 'px-6 py-4 min-w-[160px] text-base',
};

function InputNode({ 
  data, 
  isConnectable = true,
  sourcePosition = Position.Bottom,
  variant = 'default',
  size = 'md'
}: InputNodeProps) {
  
  // data에서 props 추출
  const finalSourcePosition = data.sourcePosition || sourcePosition;
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
      {/* 📍 입력 표시 아이콘 */}
      <div className="flex items-center gap-2">
        <span className="text-lg">📥</span>
        <div className="text-center">
          <div>{data.label}</div>
          {data.description && (
            <div className="text-xs opacity-80">{data.description}</div>
          )}
        </div>
      </div>

      {/* 🎯 출력 핸들 */}
      <Handle
        type="source"
        position={finalSourcePosition}
        isConnectable={isConnectable}
        className={handleStyle}
      />
    </div>
  );
}

export { InputNode };
export default memo(InputNode);
