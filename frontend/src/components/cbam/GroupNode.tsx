'use client';

import React, { useState, useCallback } from 'react';
import { Handle, Position, NodeProps, useReactFlow } from '@xyflow/react';
import { ChevronDown, ChevronRight, Package, Settings, Plus } from 'lucide-react';

interface GroupNodeData extends Record<string, unknown> {
  label: string;
  type: 'product' | 'process';
  nodes: string[];
  isCollapsed: boolean;
  boundaryType: 'input' | 'output' | 'internal';
  cbamData?: {
    carbonIntensity: number;
    materialFlow: number;
    energyConsumption: number;
  };
}

const GroupNode: React.FC<NodeProps<any>> = ({ data, selected, id }) => {
  const [isCollapsed, setIsCollapsed] = useState(data.isCollapsed);
  const [isDragOver, setIsDragOver] = useState(false);
  const { setNodes } = useReactFlow();

  const getGroupStyle = () => {
    const baseStyle = 'border-2 rounded-lg p-4 min-w-[200px] transition-all';
    
    switch (data.type) {
      case 'product':
        return `${baseStyle} bg-purple-50 border-purple-300 ${
          selected ? 'border-purple-500 shadow-lg' : ''
        }`;
      case 'process':
        return `${baseStyle} bg-green-50 border-green-300 ${
          selected ? 'border-green-500 shadow-lg' : ''
        }`;
      default:
        return `${baseStyle} bg-gray-50 border-gray-300 ${
          selected ? 'border-gray-500 shadow-lg' : ''
        }`;
    }
  };

  const getBoundaryColor = () => {
    switch (data.boundaryType) {
      case 'input':
        return 'bg-blue-500';
      case 'output':
        return 'bg-red-500';
      case 'internal':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getIcon = () => {
    switch (data.type) {
      case 'product':
        return <Package className="h-4 w-4" />;
      case 'process':
        return <Settings className="h-4 w-4" />;
      default:
        return <Package className="h-4 w-4" />;
    }
  };

  // 드래그 앤 드롭 핸들러
  const handleDragOver = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback((event: React.DragEvent) => {
    event.preventDefault();
    setIsDragOver(false);
    
    const draggedNodeId = event.dataTransfer.getData('application/reactflow');
    if (draggedNodeId && draggedNodeId !== id) {
      // 그룹에 노드 추가
      setNodes((nodes) =>
        nodes.map((node) => {
          if (node.id === id && node.data.nodes && Array.isArray(node.data.nodes)) {
            // 이미 그룹에 있는 노드인지 확인
            if (!node.data.nodes.includes(draggedNodeId)) {
              return {
                ...node,
                data: {
                  ...node.data,
                  nodes: [...node.data.nodes, draggedNodeId]
                }
              };
            }
          }
          return node;
        })
      );
    }
  }, [id, setNodes]);

  return (
    <div 
      className={`${getGroupStyle()} ${isDragOver ? 'ring-2 ring-blue-500 bg-blue-50' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {/* 그룹 헤더 */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${getBoundaryColor()}`} />
          {getIcon()}
          <span className="font-semibold text-sm">{data.label}</span>
          <span className="text-xs bg-gray-200 px-2 py-1 rounded">
            {data.nodes.length}개 노드
          </span>
        </div>
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1 hover:bg-white/50 rounded"
        >
          {isCollapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <ChevronDown className="h-4 w-4" />
          )}
        </button>
      </div>

      {/* 그룹 내용 */}
      {!isCollapsed && (
        <div className="space-y-2">
          {/* CBAM 데이터 표시 */}
          {data.cbamData && (
            <div className="bg-white/50 rounded p-2 text-xs">
              <div className="font-medium mb-1">CBAM 데이터</div>
              <div className="grid grid-cols-3 gap-2">
                <div>
                  <div className="text-gray-600">탄소강도</div>
                  <div className="font-medium">{data.cbamData.carbonIntensity} kgCO2/t</div>
                </div>
                <div>
                  <div className="text-gray-600">물질흐름</div>
                  <div className="font-medium">{data.cbamData.materialFlow} t</div>
                </div>
                <div>
                  <div className="text-gray-600">에너지소비</div>
                  <div className="font-medium">{data.cbamData.energyConsumption} GJ</div>
                </div>
              </div>
            </div>
          )}

          {/* 포함된 노드 목록 */}
          <div className="bg-white/30 rounded p-2">
            <div className="font-medium text-xs mb-1">포함된 노드</div>
            <div className="text-xs text-gray-600">
              {data.nodes && Array.isArray(data.nodes) && data.nodes.length > 0 ? (
                data.nodes.slice(0, 3).map((nodeId: any, index: number) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full" />
                      {nodeId}
                    </div>
                    <button
                      onClick={() => {
                        setNodes((nodes) =>
                          nodes.map((node) => {
                            if (node.id === id && node.data.nodes && Array.isArray(node.data.nodes)) {
                              return {
                                ...node,
                                data: {
                                  ...node.data,
                                  nodes: node.data.nodes.filter((n: string) => n !== nodeId)
                                }
                              };
                            }
                            return node;
                          })
                        );
                      }}
                      className="text-red-500 hover:text-red-700 text-xs"
                      title="노드 제거"
                    >
                      ✕
                    </button>
                  </div>
                ))
              ) : (
                <div className="text-gray-500">노드가 없습니다</div>
              )}
              {data.nodes && Array.isArray(data.nodes) && data.nodes.length > 3 && (
                <div className="text-gray-500 text-xs">
                  +{data.nodes.length - 3}개 더...
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 연결 핸들들 */}
      <Handle
        type="target"
        position={Position.Left}
        className="!w-4 !h-4 !bg-blue-600 !border-2 !border-white"
        isConnectable={true}
      />
      <Handle
        type="source"
        position={Position.Right}
        className="!w-4 !h-4 !bg-green-600 !border-2 !border-white"
        isConnectable={true}
      />
      <Handle
        type="target"
        position={Position.Top}
        className="!w-4 !h-4 !bg-purple-600 !border-2 !border-white"
        isConnectable={true}
      />
      <Handle
        type="source"
        position={Position.Bottom}
        className="!w-4 !h-4 !bg-orange-600 !border-2 !border-white"
        isConnectable={true}
      />
    </div>
  );
};

export default GroupNode;
