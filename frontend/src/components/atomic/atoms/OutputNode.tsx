'use client';

import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

interface OutputNodeProps {
  data: {
    label: string;
    description?: string;
    variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
    [key: string]: any;
  };
  isConnectable?: boolean;
}

const variantStyles = {
  default: 'bg-purple-50 border-purple-300 text-purple-800',
  primary: 'bg-purple-100 border-purple-500 text-purple-900',
  success: 'bg-green-50 border-green-300 text-green-800',
  warning: 'bg-yellow-50 border-yellow-300 text-yellow-800',
  danger: 'bg-red-50 border-red-300 text-red-800',
};

function OutputNode({ data, isConnectable = true }: OutputNodeProps) {
  const variant = data.variant || 'default';
  const variantStyle = variantStyles[variant as keyof typeof variantStyles];

  return (
    <div
      className={`p-3 rounded-lg border-2 ${variantStyle} min-w-[120px] text-center`}
    >
      <Handle
        type='target'
        position={Position.Left}
        isConnectable={isConnectable}
        className='!w-3 !h-3 !bg-purple-500 !border-2 !border-white hover:!bg-purple-600'
      />
      <div className='font-semibold text-sm mb-1'>📤 {data.label}</div>
      {data.description && (
        <div className='text-xs opacity-80'>{data.description}</div>
      )}
    </div>
  );
}

export { OutputNode };
export default memo(OutputNode);
