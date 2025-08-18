'use client';

import React from 'react';
import { Node, Edge } from '@xyflow/react';

import Badge from '../atoms/Badge';
import Icon from '../atoms/Icon';

interface ProcessFlowInfoPanelProps {
  nodes: Node<any>[];
  edges: Edge<any>[];
  selectedNodes: Node<any>[];
  selectedEdges: Edge<any>[];
  savedCanvases: any[];
  currentCanvasId: string | null;
  className?: string;
}

const ProcessFlowInfoPanel: React.FC<ProcessFlowInfoPanelProps> = ({
  nodes,
  edges,
  selectedNodes,
  selectedEdges,
  savedCanvases,
  currentCanvasId,
  className = ''
}) => {
  // ✅ desing.json의 다크 테마에 맞는 색상
  const baseClasses = 'bg-[#1e293b] border border-[#334155] rounded-lg shadow-lg p-4 text-white';
  const finalClasses = `${baseClasses} ${className}`.trim();

  // 공정 타입별 노드 수 계산
  const processTypeCounts = nodes.reduce((acc, node) => {
    const type = node.data.processType;
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // 엣지 타입별 수 계산
  const edgeTypeCounts = edges.reduce((acc, edge) => {
    const type = edge.data?.processType || 'standard';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className={finalClasses}>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
        <Icon name="info" size="sm" />
        공정도 정보
      </h3>
      
      {/* 저장된 Canvas 정보 */}
      {savedCanvases.length > 0 && (
        <div className="mb-4 p-3 bg-[#0f172a] border border-[#334155] rounded-lg">
          <h4 className="text-sm font-medium text-green-400 mb-2">저장된 Canvas</h4>
          <div className="space-y-2">
            {savedCanvases.map((canvas) => (
              <div 
                key={canvas.id} 
                className={`text-sm p-2 rounded ${
                  currentCanvasId === canvas.id 
                    ? 'bg-green-900/30 border border-green-500 text-green-300' 
                    : 'bg-[#334155] text-gray-200'
                }`}
              >
                <div className="font-medium">{canvas.name}</div>
                <div className="text-xs text-gray-400">
                  노드: {canvas.metadata?.nodeCount || 0}개, 
                  연결: {canvas.metadata?.edgeCount || 0}개
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* 기본 통계 */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="text-center">
          <div className="text-2xl font-bold text-blue-400">{nodes.length}</div>
          <div className="text-xs text-gray-300">공정 단계</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-400">{edges.length}</div>
          <div className="text-xs text-gray-300">공정 연결</div>
        </div>
      </div>

      {/* 선택된 요소 정보 */}
      {(selectedNodes.length > 0 || selectedEdges.length > 0) && (
        <div className="mb-4 p-3 bg-blue-900/30 border border-blue-500 rounded-lg">
          <h4 className="text-sm font-medium text-blue-300 mb-2">선택된 요소</h4>
          {selectedNodes.length > 0 && (
            <Badge variant="info" size="sm" className="mr-2">
              노드: {selectedNodes.length}개
            </Badge>
          )}
          {selectedEdges.length > 0 && (
            <Badge variant="info" size="sm">
              연결: {selectedEdges.length}개
            </Badge>
          )}
        </div>
      )}

      {/* 공정 타입별 분포 */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-200 mb-2">공정 타입별 분포</h4>
        <div className="space-y-2">
          {Object.entries(processTypeCounts).map(([type, count]) => (
            <div key={type} className="flex justify-between items-center text-sm">
              <span className="text-gray-300 capitalize">{type}</span>
              <Badge variant="default" size="sm">{count}</Badge>
            </div>
          ))}
        </div>
      </div>

      {/* 연결 타입별 분포 */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-200 mb-2">연결 타입별 분포</h4>
        <div className="space-y-2">
          {Object.entries(edgeTypeCounts).map(([type, count]) => (
            <div key={type} className="flex justify-between items-center text-sm">
              <span className="text-gray-300 capitalize">{type}</span>
              <Badge variant="default" size="sm">{count}</Badge>
            </div>
          ))}
        </div>
      </div>

      {/* 상태 정보 */}
      <div className="text-xs text-gray-400 space-y-1">
        <div>• 드래그로 노드 이동</div>
        <div>• 핸들로 노드 연결</div>
        <div>• 더블클릭으로 편집</div>
        <div>• Ctrl+클릭으로 다중 선택</div>
      </div>
    </div>
  );
};

export default ProcessFlowInfoPanel;
