'use client';

import React, { useState, useCallback } from 'react';
import { NodeProps } from '@xyflow/react';

import ProcessHandle from '../atoms/ProcessHandle';
import ProcessTypeBadge from '../atoms/ProcessTypeBadge';
import ProcessStatusIndicator from '../atoms/ProcessStatusIndicator';
import ProcessNodeContent from '../molecules/ProcessNodeContent';
import ProcessNodeToolbar from '../molecules/ProcessNodeToolbar';

const ProcessNode: React.FC<NodeProps<any>> = ({ 
  data, 
  selected,
  id 
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
    // 노드 삭제 로직은 부모 컴포넌트에서 처리
    console.log('노드 삭제:', id);
  }, [id]);

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
        position="left"
      />

      {/* 노드 본체 */}
      <div className="bg-white border-2 border-gray-300 rounded-lg shadow-lg p-4 min-w-[200px]">
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
        position="right"
      />
    </div>
  );
};

export default ProcessNode;
