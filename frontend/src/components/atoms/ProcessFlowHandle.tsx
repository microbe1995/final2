'use client';

import React from 'react';
import { Handle, Position } from '@xyflow/react';

interface ProcessFlowHandleProps {
  type: 'source' | 'target';
  position: Position;
  className?: string;
  style?: React.CSSProperties;
}

const ProcessFlowHandle: React.FC<ProcessFlowHandleProps> = ({
  type,
  position,
  className = '',
  style = {}
}) => {
  const baseClasses = 'w-3 h-3 bg-gray-400 hover:bg-gray-600 transition-colors duration-200';
  const finalClasses = `${baseClasses} ${className}`.trim();

  return (
    <Handle
      type={type}
      position={position}
      className={finalClasses}
      style={style}
    />
  );
};

export default ProcessFlowHandle;
