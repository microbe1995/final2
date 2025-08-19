'use client';

import React, { useState, useCallback } from 'react';
import {
  ReactFlow,
  Controls,
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  addEdge,
  type Node,
  type Edge,
  type OnNodesChange,
  type OnEdgesChange,
  type OnConnect,
  type Connection,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// ============================================================================
// 🎯 간단한 노드/엣지 타입 정의
// ============================================================================

interface FlowNode extends Node {
  data: {
    label: string;
  };
}

interface FlowEdge extends Edge {
  data?: {
    label?: string;
  };
}

// ============================================================================
// 🎯 Props 인터페이스
// ============================================================================

interface ReactFlowCanvasProps {
  initialNodes?: FlowNode[];
  initialEdges?: FlowEdge[];
  onFlowChange?: (nodes: FlowNode[], edges: FlowEdge[]) => void;
  readOnly?: boolean;
  className?: string;
}

// ============================================================================
// 🎯 React Flow Canvas 컴포넌트
// ============================================================================

const ReactFlowCanvas: React.FC<ReactFlowCanvasProps> = ({
  initialNodes = [],
  initialEdges = [],
  onFlowChange,
  readOnly = false,
  className = "",
}) => {
  const [nodes, setNodes] = useState<FlowNode[]>(initialNodes);
  const [edges, setEdges] = useState<FlowEdge[]>(initialEdges);

  // ============================================================================
  // 🎯 노드 변경 핸들러
  // ============================================================================

  const onNodesChange: OnNodesChange = useCallback(
    (changes) => {
      const newNodes = applyNodeChanges(changes, nodes) as FlowNode[];
      setNodes(newNodes);
      onFlowChange?.(newNodes, edges);
    },
    [nodes, edges, onFlowChange]
  );

  // ============================================================================
  // 🎯 엣지 변경 핸들러
  // ============================================================================

  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => {
      const newEdges = applyEdgeChanges(changes, edges) as FlowEdge[];
      setEdges(newEdges);
      onFlowChange?.(nodes, newEdges);
    },
    [edges, nodes, onFlowChange]
  );

  // ============================================================================
  // 🎯 연결 핸들러
  // ============================================================================

  const onConnect: OnConnect = useCallback(
    (connection: Connection) => {
      const newEdge: FlowEdge = {
        id: `edge-${Date.now()}`,
        source: connection.source!,
        target: connection.target!,
        sourceHandle: connection.sourceHandle,
        targetHandle: connection.targetHandle,
        type: 'default',
      };
      
      const newEdges = addEdge(newEdge, edges);
      setEdges(newEdges);
      onFlowChange?.(nodes, newEdges);
    },
    [edges, nodes, onFlowChange]
  );

  // ============================================================================
  // 🎯 새 노드 추가
  // ============================================================================

  const addNode = useCallback(() => {
    const newNode: FlowNode = {
      id: `node-${Date.now()}`,
      type: 'default',
      position: { 
        x: Math.random() * 300 + 50, 
        y: Math.random() * 200 + 50 
      },
      data: { 
        label: `노드 ${nodes.length + 1}` 
      },
    };
    
    const newNodes = [...nodes, newNode];
    setNodes(newNodes);
    onFlowChange?.(newNodes, edges);
  }, [nodes, edges, onFlowChange]);

  // ============================================================================
  // 🎯 전체 초기화
  // ============================================================================

  const clearAll = useCallback(() => {
    setNodes([]);
    setEdges([]);
    onFlowChange?.([], []);
  }, [onFlowChange]);

  return (
    <div className={`w-full h-full relative ${className}`}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        
        // 기본 설정
        nodesDraggable={!readOnly}
        nodesConnectable={!readOnly}
        elementsSelectable={true}
        
        fitView
        className="bg-gray-50"
      >
        {/* 배경 */}
        <Background 
          color="#e5e7eb" 
          gap={20} 
          variant="dots" 
        />
        
        {/* 기본 컨트롤 */}
        <Controls 
          position="top-left"
          showZoom={true}
          showFitView={true}
          showInteractive={true}
        />
      </ReactFlow>
      
      {/* 간단한 컨트롤 패널 */}
      {!readOnly && (
        <div className="absolute top-4 right-4 bg-white p-4 rounded-lg shadow-lg border border-gray-200">
          <div className="flex flex-col gap-3">
            <h3 className="text-sm font-semibold text-gray-700">컨트롤</h3>
            
            <button 
              onClick={addNode}
              className="px-3 py-2 bg-blue-500 text-white rounded text-sm hover:bg-blue-600 transition-colors"
            >
              + 노드 추가
            </button>
            
            <button 
              onClick={clearAll}
              className="px-3 py-2 bg-red-500 text-white rounded text-sm hover:bg-red-600 transition-colors"
            >
              전체 삭제
            </button>
            
            <div className="text-xs text-gray-500 pt-2 border-t border-gray-200">
              <div>노드: {nodes.length}개</div>
              <div>연결: {edges.length}개</div>
            </div>
            
            <div className="text-xs text-gray-400">
              • 노드를 드래그하여 이동
              • 핸들을 드래그하여 연결
              • Delete 키로 삭제
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReactFlowCanvas;
