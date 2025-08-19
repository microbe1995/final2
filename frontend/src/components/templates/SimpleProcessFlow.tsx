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
// 🎯 기본 노드/엣지 타입 정의
// ============================================================================

interface SimpleNode extends Node {
  data: {
    label: string;
  };
}

interface SimpleEdge extends Edge {
  data?: {
    label?: string;
  };
}

// ============================================================================
// 🎯 Props 인터페이스
// ============================================================================

interface SimpleProcessFlowProps {
  initialNodes?: SimpleNode[];
  initialEdges?: SimpleEdge[];
  onFlowChange?: (nodes: SimpleNode[], edges: SimpleEdge[]) => void;
  readOnly?: boolean;
}

// ============================================================================
// 🎯 간단한 Process Flow 컴포넌트
// ============================================================================

const SimpleProcessFlow: React.FC<SimpleProcessFlowProps> = ({
  initialNodes = [],
  initialEdges = [],
  onFlowChange,
  readOnly = false,
}) => {
  const [nodes, setNodes] = useState<SimpleNode[]>(initialNodes);
  const [edges, setEdges] = useState<SimpleEdge[]>(initialEdges);

  // ============================================================================
  // 🎯 노드 변경 핸들러
  // ============================================================================

  const onNodesChange: OnNodesChange = useCallback(
    (changes) => {
      const newNodes = applyNodeChanges(changes, nodes) as SimpleNode[];
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
      const newEdges = applyEdgeChanges(changes, edges) as SimpleEdge[];
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
      const newEdge: SimpleEdge = {
        id: `edge-${Date.now()}`,
        source: connection.source!,
        target: connection.target!,
        sourceHandle: connection.sourceHandle,
        targetHandle: connection.targetHandle,
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
    const newNode: SimpleNode = {
      id: `node-${Date.now()}`,
      type: 'default',
      position: { 
        x: Math.random() * 400 + 100, 
        y: Math.random() * 300 + 100 
      },
      data: { 
        label: `노드 ${nodes.length + 1}` 
      },
    };
    
    const newNodes = [...nodes, newNode];
    setNodes(newNodes);
    onFlowChange?.(newNodes, edges);
  }, [nodes, edges, onFlowChange]);

  return (
    <div className="w-full h-full bg-gray-50">
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
        
        {/* 간단한 컨트롤 패널 */}
        {!readOnly && (
          <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-md border">
            <div className="flex flex-col gap-2">
              <button 
                onClick={addNode}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
              >
                + 노드 추가
              </button>
              <div className="text-xs text-gray-600">
                노드: {nodes.length}개 | 연결: {edges.length}개
              </div>
            </div>
          </div>
        )}
      </ReactFlow>
    </div>
  );
};

export default SimpleProcessFlow;
