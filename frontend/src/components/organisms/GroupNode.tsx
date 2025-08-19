'use client';

import React from 'react';
import { NodeProps, Position } from '@xyflow/react';
import ProcessFlowHandle from '../atoms/ProcessFlowHandle';
import Badge from '../atoms/Badge';

// ============================================================================
// 🎯 GroupNode Props 인터페이스 (Sub Flow 지원)
// ============================================================================

interface GroupNodeData {
  label: string;
  description?: string;
  groupType: 'process' | 'subprocess' | 'workflow';
  childCount: number;
  isExpanded: boolean;
  style?: React.CSSProperties;
  [key: string]: unknown; // 인덱스 시그니처 추가
}

interface GroupNodeProps extends NodeProps<any> {
  onToggleExpand?: (id: string) => void;
}

// ============================================================================
// 🎯 GroupNode 컴포넌트 (Sub Flow 그룹화)
// ============================================================================

const GroupNode: React.FC<GroupNodeProps> = ({ 
  data, 
  selected,
  id,
  onToggleExpand
}) => {
  // data를 GroupNodeData로 타입 단언
  const groupData = data as GroupNodeData;
  
  const handleToggleExpand = () => {
    if (onToggleExpand) {
      onToggleExpand(id as string);
    }
  };

  return (
    <div 
      className={`relative ${selected ? 'ring-2 ring-purple-500' : ''}`}
      style={{
        width: groupData.style?.width || 300,
        height: groupData.style?.height || 200,
        ...groupData.style
      }}
    >
      {/* 입력 핸들 */}
      <ProcessFlowHandle
        type="target"
        position={Position.Left}
      />

      {/* 그룹 노드 본체 */}
      <div className="bg-purple-900/20 border-2 border-purple-500/50 rounded-lg shadow-lg p-4 h-full text-white relative">
        {/* 그룹 헤더 */}
        <div className="flex items-center justify-between mb-3">
          <Badge variant="info" size="sm">
            {groupData.groupType === 'subprocess' ? 'Sub Process' : 
             groupData.groupType === 'workflow' ? 'Workflow' : 'Process Group'}
          </Badge>
          <button
            onClick={handleToggleExpand}
            className="text-purple-300 hover:text-purple-100 text-sm"
          >
            {groupData.isExpanded ? '📁' : '📂'}
          </button>
        </div>

        {/* 그룹 제목 */}
        <h3 className="text-lg font-semibold text-purple-100 mb-2">
          {groupData.label}
        </h3>

        {/* 그룹 설명 */}
        {groupData.description && (
          <p className="text-purple-200 text-sm mb-3">
            {groupData.description}
          </p>
        )}

        {/* 자식 노드 정보 */}
        <div className="absolute bottom-4 left-4 right-4">
          <div className="flex justify-between items-center text-xs text-purple-300">
            <span>자식 노드: {groupData.childCount}개</span>
            <span className={`px-2 py-1 rounded ${
              groupData.isExpanded ? 'bg-purple-600/50' : 'bg-purple-800/50'
            }`}>
              {groupData.isExpanded ? '펼침' : '접힘'}
            </span>
          </div>
        </div>

        {/* 그룹 배경 패턴 */}
        <div className="absolute inset-0 opacity-5 pointer-events-none">
          <div className="w-full h-full bg-gradient-to-br from-purple-400 to-purple-600 rounded-lg"></div>
        </div>
      </div>

      {/* 출력 핸들 */}
      <ProcessFlowHandle
        type="source"
        position={Position.Right}
      />
    </div>
  );
};

export default GroupNode;
