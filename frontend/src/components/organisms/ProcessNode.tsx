'use client';

import React, { useState, useCallback } from 'react';
import { NodeProps, Position } from '@xyflow/react';

import ProcessHandle from '../atoms/ProcessHandle';
import ProcessTypeBadge from '../atoms/ProcessTypeBadge';
import ProcessStatusIndicator from '../atoms/ProcessStatusIndicator';
import ProcessNodeContent from '../molecules/ProcessNodeContent';
import ProcessNodeToolbar from '../molecules/ProcessNodeToolbar';
import type { ProcessNodeData } from '@/types/reactFlow';

// ============================================================================
// 🎯 ProcessNode Props 인터페이스
// ============================================================================

interface ProcessNodeProps extends NodeProps<ProcessNodeData> {
  onDelete?: (id: string) => void;
}

// ============================================================================
// 🎯 ProcessNode 컴포넌트
// ============================================================================

const ProcessNode: React.FC<ProcessNodeProps> = ({ 
  data, 
  selected,
  id,
  onDelete
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editLabel, setEditLabel] = useState(data.label);
  const [editDescription, setEditDescription] = useState(data.description);

  const handleLabelEdit = useCallback(() => {
    if (isEditing) {
      // 편집 완료 시 데이터 업데이트
      data.label = editLabel;
      data.description = editDescription;
    }
    setIsEditing(!isEditing);
  }, [isEditing, editLabel, editDescription, data]);

  const handleDelete = useCallback(() => {
    if (onDelete) {
      onDelete(id);
    }
  }, [id, onDelete]);

  return (
    <div className={`relative ${selected ? 'ring-2 ring-blue-500' : ''}`}>
      <ProcessNodeToolbar
        isEditing={isEditing}
        onEditToggle={handleLabelEdit}
        onDelete={handleDelete}
      />

      {/* 입력 핸들 */}
      <ProcessHandle
        type="target"
        position={Position.Left}
      />

      {/* 노드 본체 */}
      <div className="bg-[#1e293b] border-2 border-[#334155] rounded-lg shadow-lg p-4 min-w-[200px] text-white">
        {/* 공정 타입 및 상태 표시 */}
        <div className="flex items-center justify-between mb-3">
          <ProcessTypeBadge
            processType={data.processType}
            size="sm"
          />
          <ProcessStatusIndicator
            status="active"
            size="sm"
          />
        </div>

        {/* 노드 내용 */}
        <ProcessNodeContent
          data={data}
          isEditing={isEditing}
          editLabel={editLabel}
          editDescription={editDescription}
          onLabelChange={setEditLabel}
          onDescriptionChange={setEditDescription}
        />

        {/* 추가 정보 */}
        <div className="mt-3 pt-2 border-t border-gray-200">
          <div className="flex justify-between text-xs text-gray-500">
            <span>ID: {id}</span>
            <span>타입: {data.processType}</span>
          </div>
        </div>
      </div>

      {/* 출력 핸들 */}
      <ProcessHandle
        type="source"
        position={Position.Right}
      />
    </div>
  );
};

export default ProcessNode;
