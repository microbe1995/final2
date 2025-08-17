'use client';

import React from 'react';
import ProcessFlowEditor from '@/templates/ProcessFlowEditor';
import type { AppNodeType, AppEdgeType } from '@/types/reactFlow';

interface ProcessFlowMainProps {
  nodes: AppNodeType[];
  edges: AppEdgeType[];
  isReadOnly: boolean;
  onFlowChange: (nodes: AppNodeType[], edges: AppEdgeType[]) => void;
  onAddElement: () => void;
  onDeleteSelected: () => void;
}

const ProcessFlowMain: React.FC<ProcessFlowMainProps> = ({
  nodes,
  edges,
  isReadOnly,
  onFlowChange,
  onAddElement,
  onDeleteSelected,
}) => {
  return (
    <div className="lg:col-span-3">
      <div className="bg-[#1e293b] rounded-lg shadow-lg p-6 border border-[#334155]">
        <ProcessFlowEditor
          initialNodes={nodes}
          initialEdges={edges}
          onFlowChange={onFlowChange}
          readOnly={isReadOnly}
        />
        
        {/* 하단 컨트롤 버튼들 */}
        <div className="flex justify-center space-x-4 mt-4">
          <button
            onClick={onAddElement}
            className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
          >
            공정 요소 추가
          </button>
          <button
            onClick={onDeleteSelected}
            className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors"
          >
            선택 삭제
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProcessFlowMain;
