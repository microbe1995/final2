'use client';

import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

interface InputNodeProps {
  data: {
    label: string;
    description?: string;
    variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
    [key: string]: any;
  };
  isConnectable?: boolean;
}

const variantStyles = {
  default: 'bg-blue-50 border-blue-300 text-blue-800',
  primary: 'bg-blue-100 border-blue-500 text-blue-900',
  success: 'bg-green-50 border-green-300 text-green-800',
  warning: 'bg-yellow-50 border-yellow-300 text-yellow-800',
  danger: 'bg-red-50 border-red-300 text-red-800',
};

function InputNode({ data, isConnectable = true }: InputNodeProps) {
  const variant = data.variant || 'default';
  const variantStyle = variantStyles[variant as keyof typeof variantStyles];

  return (
    <div
      className={`p-3 rounded-lg border-2 ${variantStyle} min-w-[120px] text-center`}
    >
      <Handle
        type='source'
        position={Position.Right}
        isConnectable={isConnectable}
        className='!w-3 !h-3 !bg-blue-500 !border-2 !border-white hover:!bg-blue-600'
      />
      <div className='font-semibold text-sm mb-1'>📥 {data.label}</div>
      {data.description && (
        <div className='text-xs opacity-80'>{data.description}</div>
      )}
    </div>
  );
}

export { InputNode };
export default memo(InputNode);
