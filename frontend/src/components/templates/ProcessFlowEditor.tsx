'use client';

import React, { useState, useCallback } from 'react';
import {
  ReactFlow,
  addEdge,
  Connection,
  applyNodeChanges,
  applyEdgeChanges,
  Controls,
  MiniMap,
  type OnConnect,
  type OnNodesChange,
  type OnEdgesChange,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import ProcessNodeComponent from '../organisms/ProcessNode';
import ProcessEdgeComponent from '../organisms/ProcessEdge';
import CustomBackground from '../atoms/CustomBackground';
import type { AppNodeType, AppEdgeType, ProcessNode, ProcessEdge } from '@/types/reactFlow';

// ============================================================================
// 🎯 노드 및 엣지 타입 정의
// ============================================================================

const nodeTypes = {
  processNode: ProcessNodeComponent as any,
};

const edgeTypes = {
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
  // ✅ 공식 문서 방식: useState 사용
  const [nodes, setNodes] = useState<AppNodeType[]>(initialNodes);
  const [edges, setEdges] = useState<AppEdgeType[]>(initialEdges);

  // ✅ 공식 문서 방식: applyNodeChanges, applyEdgeChanges 사용
  const onNodesChange: OnNodesChange = useCallback(
    (changes) => {
      const newNodes = applyNodeChanges(changes, nodes) as AppNodeType[];
      setNodes(newNodes);
      
      // 부모에게 변경사항 알림
      if (onFlowChange) {
        onFlowChange(newNodes, edges);
      }
    },
    [nodes, edges, onFlowChange]
  );

  const onEdgesChange: OnEdgesChange = useCallback(
    (changes) => {
      const newEdges = applyEdgeChanges(changes, edges) as AppEdgeType[];
      setEdges(newEdges);
      
      // 부모에게 변경사항 알림
      if (onFlowChange) {
        onFlowChange(nodes, newEdges);
      }
    },
    [nodes, edges, onFlowChange]
  );

  // ✅ 공식 문서 방식: addEdge 사용
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
      
      const newEdges = addEdge(newEdge, edges);
      setEdges(newEdges);
      
      // 부모에게 변경사항 알림
      if (onFlowChange) {
        onFlowChange(nodes, newEdges);
      }
    },
    [edges, nodes, onFlowChange]
  );

  // 외부에서 전달받은 nodes/edges가 변경되면 내부 상태도 업데이트
  React.useEffect(() => {
    console.log('🔄 ProcessFlowEditor - initialNodes 변경 감지:', initialNodes);
    setNodes(initialNodes);
  }, [initialNodes]);

  React.useEffect(() => {
    console.log('🔄 ProcessFlowEditor - initialEdges 변경 감지:', initialEdges);
    setEdges(initialEdges);
  }, [initialEdges]);

  // 렌더링 시점에 현재 상태 로그
  React.useEffect(() => {
    console.log('🎨 ProcessFlowEditor 렌더링:', { nodes: nodes.length, edges: edges.length });
  }, [nodes, edges]);

  return (
    <div className="w-full h-full">
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
        <CustomBackground />
        <Controls />
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
