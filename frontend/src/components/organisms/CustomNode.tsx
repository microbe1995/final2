'use client';

import React, { useState, useCallback, useRef } from 'react';
import { NodeProps, Position, useReactFlow } from '@xyflow/react';
import ProcessFlowHandle from '../atoms/ProcessFlowHandle';
import Badge from '../atoms/Badge';
import Icon from '../atoms/Icon';

// ============================================================================
// 🎯 Custom Node 타입 정의
// ============================================================================

interface CustomNodeData {
  label: string;
  description?: string;
  kind: 'process' | 'meter' | 'sensor' | 'valve';
  status: 'active' | 'inactive' | 'error';
  value?: number;
  unit?: string;
  [key: string]: unknown;
}

interface CustomNodeProps extends NodeProps {
  onLabelChange?: (nodeId: string, newLabel: string) => void;
}

// ============================================================================
// 🎯 Custom Node 컴포넌트
// ============================================================================

const CustomNode: React.FC<CustomNodeProps> = ({
  data,
  selected,
  id,
  onLabelChange
}) => {
  const { setNodes } = useReactFlow();
  const [isEditing, setIsEditing] = useState(false);
  const [editValue, setEditValue] = useState((data as CustomNodeData).label);
  const inputRef = useRef<HTMLInputElement>(null);
  
  // 타입 안전성을 위한 데이터 캐스팅
  const nodeData = data as CustomNodeData;

  // ============================================================================
  // 🎯 라벨 편집 시작
  // ============================================================================
  
  const handleEditStart = useCallback((e: React.MouseEvent) => {
    e.stopPropagation();
    setIsEditing(true);
    setEditValue(nodeData.label);
    setTimeout(() => inputRef.current?.focus(), 0);
  }, [nodeData.label]);

  // ============================================================================
  // 🎯 라벨 편집 완료
  // ============================================================================
  
  const handleEditComplete = useCallback(() => {
    if (editValue.trim() !== nodeData.label && editValue.trim()) {
      // 상위 컴포넌트에 변경 알림
      if (onLabelChange) {
        onLabelChange(id, editValue.trim());
      }
      
      // ReactFlow 상태 직접 업데이트
      setNodes(prev => 
        prev.map(node => 
          node.id === id 
            ? { ...node, data: { ...node.data, label: editValue.trim() } }
            : node
        )
      );
    }
    setIsEditing(false);
  }, [editValue, nodeData.label, id, onLabelChange, setNodes]);

  // ============================================================================
  // 🎯 라벨 편집 취소
  // ============================================================================
  
  const handleEditCancel = useCallback(() => {
    setEditValue(nodeData.label);
    setIsEditing(false);
  }, [nodeData.label]);

  // ============================================================================
  // 🎯 키보드 이벤트 처리
  // ============================================================================
  
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleEditComplete();
    } else if (e.key === 'Escape') {
      handleEditCancel();
    }
  }, [handleEditComplete, handleEditCancel]);

  // ============================================================================
  // 🎯 노드 타입별 스타일
  // ============================================================================
  
  const getNodeStyle = () => {
    const baseStyle: React.CSSProperties = {
      minWidth: 180,
      minHeight: 80,
      padding: '12px',
      borderRadius: '8px',
      border: selected ? '2px solid #3b82f6' : '2px solid transparent',
      backgroundColor: 'white',
      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
      cursor: 'grab'
    };

    switch (nodeData.kind) {
      case 'process':
        return {
          ...baseStyle,
          borderColor: '#10b981',
          backgroundColor: '#f0fdf4'
        };
      case 'meter':
        return {
          ...baseStyle,
          borderColor: '#3b82f6',
          backgroundColor: '#eff6ff'
        };
      case 'sensor':
        return {
          ...baseStyle,
          borderColor: '#f59e0b',
          backgroundColor: '#fffbeb'
        };
      case 'valve':
        return {
          ...baseStyle,
          borderColor: '#ef4444',
          backgroundColor: '#fef2f2'
        };
      default:
        return baseStyle;
    }
  };

  const getStatusColor = () => {
    switch (nodeData.status) {
      case 'active': return 'success';
      case 'inactive': return 'default';
      case 'error': return 'error';
      default: return 'default';
    }
  };

  const getKindIcon = () => {
    switch (nodeData.kind) {
      case 'process': return 'cog';
      case 'meter': return 'gauge';
      case 'sensor': return 'activity';
      case 'valve': return 'toggle-right';
      default: return 'box';
    }
  };

  return (
    <div 
      className={`custom-node ${selected ? 'ring-2 ring-blue-500' : ''}`}
      style={getNodeStyle()}
    >
      {/* 입력 핸들 */}
      <ProcessFlowHandle
        type="target"
        position={Position.Left}
      />

      {/* 노드 본체 */}
      <div className="space-y-2">
        {/* 헤더 */}
        <div className="flex items-center justify-between">
                     <div className="flex items-center gap-2">
             <Icon name={getKindIcon()} size="sm" className="text-gray-600" />
             <Badge variant="default" size="sm">
               {nodeData.kind}
             </Badge>
           </div>
           <Badge variant={getStatusColor()} size="sm">
             {nodeData.status}
           </Badge>
        </div>

        {/* 라벨 편집 영역 */}
        <div className="space-y-1">
          {isEditing ? (
            <div className="space-y-1">
              <input
                ref={inputRef}
                type="text"
                value={editValue}
                onChange={(e) => setEditValue(e.target.value)}
                onBlur={handleEditComplete}
                onKeyDown={handleKeyDown}
                className="w-full px-2 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="라벨 입력..."
                autoFocus
              />
              <div className="flex gap-1 text-xs text-gray-500">
                <span>Enter: 저장</span>
                <span>Esc: 취소</span>
              </div>
            </div>
          ) : (
            <div 
              className="cursor-pointer hover:bg-gray-50 px-2 py-1 rounded transition-colors"
              onClick={handleEditStart}
              title="클릭하여 편집"
            >
                           <h3 className="font-semibold text-gray-900 text-sm">
               {nodeData.label || '라벨 없음'}
             </h3>
            </div>
          )}
        </div>

                 {/* 설명 */}
         {nodeData.description && (
           <p className="text-xs text-gray-600 px-2">
             {nodeData.description}
           </p>
         )}

         {/* 값 표시 */}
         {nodeData.value !== undefined && (
           <div className="flex items-center justify-between px-2 py-1 bg-gray-50 rounded">
             <span className="text-xs text-gray-600">값:</span>
             <span className="font-mono text-sm font-semibold">
               {nodeData.value}
               {nodeData.unit && <span className="text-xs text-gray-500 ml-1">{nodeData.unit}</span>}
             </span>
           </div>
         )}
      </div>

      {/* 출력 핸들 */}
      <ProcessFlowHandle
        type="source"
        position={Position.Right}
      />
    </div>
  );
};

export default CustomNode;
