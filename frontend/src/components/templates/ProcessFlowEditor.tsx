'use client';

import React, { useState, useCallback } from 'react';
import {
  ReactFlow,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  NodeTypes,
  EdgeTypes,
  type OnConnect,
  type OnNodesChange,
  type OnEdgesChange,
} from '@xyflow/react';
import ProcessNodeComponent from '../organisms/ProcessNode';
import ProcessEdgeComponent from '../organisms/ProcessEdge';
import type { AppNodeType, AppEdgeType, ProcessNode, ProcessEdge } from '@/types/reactFlow';

// ============================================================================
// 🎯 노드 및 엣지 타입 정의
// ============================================================================

const nodeTypes: NodeTypes = {
  // React Flow의 타입 시스템과 호환성을 위해 타입 단언 사용
  processNode: ProcessNodeComponent as any,
};

const edgeTypes: EdgeTypes = {
  // React Flow의 타입 시스템과 호환성을 위해 타입 단언 사용
  processEdge: ProcessEdgeComponent as any,
};

// ============================================================================
// 🎯 Props 인터페이스
// ============================================================================

interface ProcessFlowEditorProps {
  initialNodes?: AppNodeType[];
  initialEdges?: AppEdgeType[];
  onFlowChange?: (nodes: AppNodeType[], edges: AppEdgeType[]) => void;
  readOnly?: boolean;
}

// ============================================================================
// 🎯 ProcessFlowEditor 컴포넌트
// ============================================================================

const ProcessFlowEditor: React.FC<ProcessFlowEditorProps> = ({
  initialNodes = [],
  initialEdges = [],
  onFlowChange,
  readOnly = false,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState<AppNodeType>(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState<AppEdgeType>(initialEdges);

  // 외부에서 전달받은 nodes/edges가 변경되면 내부 상태도 업데이트
  React.useEffect(() => {
    console.log('🔄 ProcessFlowEditor - initialNodes 변경 감지:', initialNodes);
    if (initialNodes.length !== nodes.length || 
        JSON.stringify(initialNodes) !== JSON.stringify(nodes)) {
      console.log('✅ ProcessFlowEditor - nodes 상태 업데이트:', initialNodes);
      setNodes(initialNodes);
    }
  }, [initialNodes, nodes, setNodes]);

  React.useEffect(() => {
    console.log('🔄 ProcessFlowEditor - initialEdges 변경 감지:', initialEdges);
    if (initialEdges.length !== edges.length || 
        JSON.stringify(initialEdges) !== JSON.stringify(edges)) {
      console.log('✅ ProcessFlowEditor - edges 상태 업데이트:', initialEdges);
      setEdges(initialEdges);
    }
  }, [initialEdges, edges, setEdges]);

  // ============================================================================
  // 🎯 이벤트 핸들러들
  // ============================================================================

  const onConnect: OnConnect = useCallback(
    (params: Connection) => {
      if (!params.source || !params.target) return;
      
      const newEdge: ProcessEdge = {
        id: `edge-${Date.now()}`,
        source: params.source,
        target: params.target,
        type: 'processEdge',
        data: {
          label: '공정 흐름',
          processType: 'standard',
        },
      };
      setEdges((eds) => addEdge(newEdge, eds));
    },
    [setEdges]
  );

  const onFlowChangeHandler = useCallback(() => {
    if (onFlowChange) {
      onFlowChange(nodes, edges);
    }
  }, [nodes, edges, onFlowChange]);

  // 노드나 엣지가 변경될 때마다 콜백 호출
  React.useEffect(() => {
    onFlowChangeHandler();
  }, [nodes, edges, onFlowChangeHandler]);

  const addProcessNode = useCallback(() => {
    const newNode: ProcessNode = {
      id: `node-${Date.now()}`,
      type: 'processNode',
      position: { x: 250, y: 250 },
      data: {
        label: '새 공정 단계',
        processType: 'manufacturing',
        description: '공정 단계 설명을 입력하세요',
        parameters: {},
      },
    };
    setNodes((nds) => [...nds, newNode]);
  }, [setNodes]);

  const deleteSelectedElements = useCallback(() => {
    const selectedNodes = nodes.filter((node) => node.selected);
    const selectedEdges = edges.filter((edge) => edge.selected);
    
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      setNodes((nds) => nds.filter((node) => !node.selected));
      setEdges((eds) => eds.filter((edge) => !edge.selected));
    }
  }, [nodes, edges, setNodes, setEdges]);

  // ============================================================================
  // 💾 로컬 저장소에 공정도 저장
  // ============================================================================
  
  const saveToLocalStorage = useCallback(() => {
    try {
      const flowData = {
        nodes,
        edges,
        timestamp: new Date().toISOString(),
      };
      
      localStorage.setItem('processFlowData', JSON.stringify(flowData));
      // console.log 제거
    } catch (error) {
      console.error('❌ 로컬 저장 실패:', error);
    }
  }, [nodes, edges]);

  // ============================================================================
  // 📥 로컬 저장소에서 공정도 로드
  // ============================================================================
  
  const loadFromLocalStorage = useCallback(() => {
    try {
      const savedData = localStorage.getItem('processFlowData');
      
      if (savedData) {
        const flowData = JSON.parse(savedData);
        setNodes(flowData.nodes || []);
        setEdges(flowData.edges || []);
        // console.log 제거
      } else {
        // console.log 제거
      }
    } catch (error) {
      console.error('❌ 로컬 로드 실패:', error);
    }
  }, [setNodes, setEdges]);

  return (
    <div className="w-full h-full min-h-[600px] bg-[#0b0c0f] rounded-lg overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        attributionPosition="bottom-left"
        className="bg-[#0b0c0f]"
        style={{ backgroundColor: '#0b0c0f' }}
      >
        <Controls />
        <Background variant={"dots" as any} color="#334155" />
        <MiniMap
          nodeStrokeColor={(n) => {
            if (n.type === 'processNode') return '#1a192b';
            return '#eee';
          }}
          nodeColor={(n) => {
            if (n.selected) return '#ff0072';
            return '#fff';
          }}
        />
      </ReactFlow>
    </div>
  );
};

export default ProcessFlowEditor;
