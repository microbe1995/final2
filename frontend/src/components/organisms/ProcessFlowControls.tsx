'use client';

import React from 'react';
import { Panel } from '@xyflow/react';
import Button from '../atoms/Button';

interface ProcessFlowControlsProps {
  onAddNode: () => void;
  onDeleteSelected: () => void;
  onSave: () => void;
  onLoad: () => void;
  readOnly?: boolean;
  className?: string;
}

const ProcessFlowControls: React.FC<ProcessFlowControlsProps> = ({
  onAddNode,
  onDeleteSelected,
  onSave,
  onLoad,
  readOnly = false,
  className = ''
}) => {
  const baseClasses = 'bg-[#1e293b] border border-[#334155] p-4 rounded-lg shadow-lg text-white';
  const finalClasses = `${baseClasses} ${className}`.trim();

  return (
    <Panel position="top-left" className={finalClasses}>
      <div className="flex flex-col gap-2">
        <Button
          onClick={onAddNode}
          disabled={readOnly}
          variant="primary"
          size="sm"
          className="w-full"
        >
          공정 단계 추가
        </Button>
        
        <Button
          onClick={onDeleteSelected}
          disabled={readOnly}
          variant="danger"
          size="sm"
          className="w-full"
        >
          선택 삭제
        </Button>
        
        <Button
          onClick={onSave}
          variant="success"
          size="sm"
          className="w-full"
        >
          저장
        </Button>
        
        <Button
          onClick={onLoad}
          variant="secondary"
          size="sm"
          className="w-full"
        >
          불러오기
        </Button>
      </div>
    </Panel>
  );
};

export default ProcessFlowControls;
