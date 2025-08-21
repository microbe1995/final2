'use client';

import { memo } from 'react';
import { Handle, Position } from '@xyflow/react';

interface AnnotationNodeProps {
  data: {
    label: string;
    arrowStyle?: string;
    [key: string]: any;
  };
  isConnectable?: boolean;
}

function AnnotationNode({ data, isConnectable = false }: AnnotationNodeProps) {
  return (
    <div className='annotation-content'>
      <Handle
        type='target'
        position={Position.Top}
        isConnectable={isConnectable}
        className='!w-2 !h-2 !bg-yellow-400 !border-2 !border-white'
      />
      <div className='text-center'>
        <div className='font-medium text-sm'>{data.label}</div>
      </div>
      {data.arrowStyle && (
        <div className={`annotation-arrow ${data.arrowStyle}`}>→</div>
      )}
    </div>
  );
}

export { AnnotationNode };
export default memo(AnnotationNode);
