'use client';

import React from 'react';
import { NodeToolbar, Position } from '@xyflow/react';
import Button from '../atoms/Button';

interface ProcessNodeToolbarProps {
  isEditing: boolean;
  onEditToggle: () => void;
  onDelete: () => void;
  className?: string;
}

const ProcessNodeToolbar: React.FC<ProcessNodeToolbarProps> = ({
  isEditing,
  onEditToggle,
  onDelete,
  className = ''
}) => {
  const baseClasses = 'bg-[#1e293b] border border-[#334155] p-2 rounded-lg shadow-lg text-white';
  const finalClasses = `${baseClasses} ${className}`.trim();

  return (
    <NodeToolbar
      position={Position.Top}
      className={finalClasses}
    >
      <div className="flex gap-2">
        <Button
          onClick={onEditToggle}
          variant="primary"
          size="sm"
          className="px-3 py-1"
        >
          {isEditing ? '저장' : '편집'}
        </Button>
        <Button
          onClick={onDelete}
          variant="danger"
          size="sm"
          className="px-3 py-1"
        >
          삭제
        </Button>
      </div>
    </NodeToolbar>
  );
};

export default ProcessNodeToolbar;
