'use client';

import React, { useState, useCallback, useRef } from 'react';
import { NodeProps, Position, useReactFlow } from '@xyflow/react';
import Card from '@/components/molecules/Card';
import Badge from '@/components/atoms/Badge';
import Icon from '@/components/atoms/Icon';

// ============================================================================
// 🎯 Group Node 타입 정의
// ============================================================================

interface GroupNodeData {
  label: string;
  description?: string;
  groupType: 'process' | 'subprocess' | 'workflow' | 'facility';
  childCount: number;
  isExpanded: boolean;
  style?: React.CSSProperties;
  minWidth?: number;
  minHeight?: number;
  [key: string]: unknown;
}

interface GroupNodeProps extends NodeProps<any> {
  onToggleExpand?: (id: string) => void;
  onResize?: (id: string, width: number, height: number) => void;
}

// ============================================================================
// 🎯 Group Node 컴포넌트
// ============================================================================

const GroupNode: React.FC<GroupNodeProps> = ({
  data,
  selected,
  id,
  onToggleExpand,
  onResize
}) => {
  const groupData = data as GroupNodeData;
  const { getNodes, setNodes } = useReactFlow();
  
  // 상태 관리
  const [isResizing, setIsResizing] = useState(false);
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  // 참조
  const nodeRef = useRef<HTMLDivElement>(null);
  const resizeHandleRef = useRef<HTMLDivElement>(null);

  // ============================================================================
  // 🔄 그룹 확장/축소 토글
  // ============================================================================
  
  const handleToggleExpand = useCallback(() => {
    if (onToggleExpand) {
      onToggleExpand(id as string);
    }
  }, [onToggleExpand, id]);

  // ============================================================================
  // 📏 리사이즈 시작
  // ============================================================================
  
  const handleResizeStart = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!nodeRef.current) return;
    
    const rect = nodeRef.current.getBoundingClientRect();
    const currentWidth = rect.width;
    const currentHeight = rect.height;
    
    setIsResizing(true);
    setResizeStart({
      x: e.clientX,
      y: e.clientY,
      width: currentWidth,
      height: currentHeight
    });
  }, []);

  // ============================================================================
  // 📏 리사이즈 중
  // ============================================================================
  
  const handleResizeMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;
    
    const deltaX = e.clientX - resizeStart.x;
    const deltaY = e.clientY - resizeStart.y;
    
    const newWidth = Math.max(
      (groupData.minWidth || 300),
      resizeStart.width + deltaX
    );
    const newHeight = Math.max(
      (groupData.minHeight || 200),
      resizeStart.height + deltaY
    );
    
    // 노드 크기 업데이트
    if (onResize) {
      onResize(id as string, newWidth, newHeight);
    }
    
    // ReactFlow 노드 크기 업데이트
    setNodes((nodes) =>
      nodes.map((node) => {
        if (node.id === id) {
          return {
            ...node,
            style: {
              ...node.style,
              width: newWidth,
              height: newHeight
            }
          };
        }
        return node;
      })
    );
  }, [isResizing, resizeStart, groupData.minWidth, groupData.minHeight, onResize, id, setNodes]);

  // ============================================================================
  // 📏 리사이즈 종료
  // ============================================================================
  
  const handleResizeEnd = useCallback(() => {
    setIsResizing(false);
  }, []);

  // ============================================================================
  // 🖱️ 드래그 시작
  // ============================================================================
  
  const handleDragStart = useCallback((e: React.MouseEvent) => {
    if (e.target !== nodeRef.current) return;
    
    setIsDragging(true);
    setDragStart({
      x: e.clientX,
      y: e.clientY
    });
  }, []);

  // ============================================================================
  // 🖱️ 드래그 중
  // ============================================================================
  
  const handleDragMove = useCallback((e: MouseEvent) => {
    if (!isDragging) return;
    
    const deltaX = e.clientX - dragStart.x;
    const deltaY = e.clientY - dragStart.y;
    
    // 그룹 내부의 모든 노드들을 함께 이동
    setNodes((nodes) =>
      nodes.map((node) => {
        if (node.parentId === id) {
          return {
            ...node,
            position: {
              x: node.position.x + deltaX,
              y: node.position.y + deltaY
            }
          };
        }
        return node;
      })
    );
    
    setDragStart({
      x: e.clientX,
      y: e.clientY
    });
  }, [isDragging, dragStart, id, setNodes]);

  // ============================================================================
  // 🖱️ 드래그 종료
  // ============================================================================
  
  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
  }, []);

  // ============================================================================
  // 🎯 이벤트 리스너 등록/해제
  // ============================================================================
  
  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleResizeMove);
      document.addEventListener('mouseup', handleResizeEnd);
      return () => {
        document.removeEventListener('mousemove', handleResizeMove);
        document.removeEventListener('mouseup', handleResizeEnd);
      };
    }
  }, [isResizing, handleResizeMove, handleResizeEnd]);

  React.useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleDragMove);
      document.addEventListener('mouseup', handleDragEnd);
      return () => {
        document.removeEventListener('mousemove', handleDragMove);
        document.removeEventListener('mouseup', handleDragEnd);
      };
    }
  }, [isDragging, handleDragMove, handleDragEnd]);

  // ============================================================================
  // 🎨 그룹 타입별 스타일
  // ============================================================================
  
  const getGroupStyle = () => {
    const baseStyle: React.CSSProperties = {
      width: groupData.style?.width || 400,
      height: groupData.style?.height || 300,
      minWidth: groupData.minWidth || 300,
      minHeight: groupData.minHeight || 200,
      position: 'relative',
      cursor: isDragging ? 'grabbing' : 'grab'
    };

    switch (groupData.groupType) {
      case 'facility':
        return {
          ...baseStyle,
          border: '2px solid #3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.05)',
          borderRadius: '12px'
        };
      case 'process':
        return {
          ...baseStyle,
          border: '2px solid #10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.05)',
          borderRadius: '8px'
        };
      case 'subprocess':
        return {
          ...baseStyle,
          border: '2px solid #f59e0b',
          backgroundColor: 'rgba(245, 158, 11, 0.05)',
          borderRadius: '10px'
        };
      default:
        return {
          ...baseStyle,
          border: '2px solid #6b7280',
          backgroundColor: 'rgba(107, 114, 128, 0.05)',
          borderRadius: '6px'
        };
    }
  };

  const getGroupIcon = () => {
    switch (groupData.groupType) {
      case 'facility': return 'building';
      case 'process': return 'cog';
      case 'subprocess': return 'layers';
      default: return 'box';
    }
  };

  const getGroupColor = () => {
    switch (groupData.groupType) {
      case 'facility': return 'primary';
      case 'process': return 'success';
      case 'subprocess': return 'warning';
      default: return 'default';
    }
  };

  return (
    <div
      ref={nodeRef}
      className={`group-node ${selected ? 'ring-2 ring-blue-500' : ''}`}
      style={getGroupStyle()}
      onMouseDown={handleDragStart}
    >
      {/* 그룹 헤더 */}
      <div className="absolute top-0 left-0 right-0 p-3 bg-white/80 backdrop-blur-sm border-b border-gray-200 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Icon name={getGroupIcon()} size="sm" className={`text-${getGroupColor()}-600`} />
            <div>
              <h3 className="font-semibold text-gray-900 text-sm">{groupData.label}</h3>
              {groupData.description && (
                <p className="text-xs text-gray-600">{groupData.description}</p>
              )}
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge variant={getGroupColor()} size="sm">
              {groupData.groupType}
            </Badge>
                         <Badge variant="default" size="sm">
               {groupData.childCount}개 노드
             </Badge>
            <button
              onClick={handleToggleExpand}
              className="p-1 hover:bg-gray-100 rounded transition-colors"
              title={groupData.isExpanded ? '축소' : '확장'}
            >
                             <Icon 
                 name={groupData.isExpanded ? 'chevron-up' : 'chevron-down'} 
                 size="sm" 
                 className="text-gray-600" 
               />
            </button>
          </div>
        </div>
      </div>

      {/* 그룹 내용 영역 */}
      <div className="absolute top-16 left-0 right-0 bottom-0 p-4">
        <div className="text-center text-gray-500 text-sm">
          {groupData.isExpanded ? (
            <div className="flex items-center justify-center h-full">
              <Icon name="nodes" size="lg" className="text-gray-300" />
              <span className="ml-2">노드들을 여기에 배치하세요</span>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full">
              <Icon name="eye-off" size="lg" className="text-gray-300" />
              <span className="ml-2">그룹을 확장하여 내용을 보세요</span>
            </div>
          )}
        </div>
      </div>

      {/* 리사이즈 핸들 (우하단 모서리) */}
      <div
        ref={resizeHandleRef}
        className="absolute bottom-0 right-0 w-6 h-6 cursor-se-resize flex items-center justify-center"
        onMouseDown={handleResizeStart}
        title="크기 조절"
      >
        <div className="w-4 h-4 border-r-2 border-b-2 border-gray-400 rounded-br-sm" />
      </div>

      {/* 그룹 테두리 강조 */}
      <div className="absolute inset-0 border-2 border-transparent group-hover:border-blue-300 transition-colors duration-200 pointer-events-none" />
    </div>
  );
};

export default GroupNode;
