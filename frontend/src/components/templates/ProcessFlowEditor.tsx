'use client';

import React, { useState, useCallback, useMemo } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  addEdge,
  Connection,
  useNodesState,
  useEdgesState,
  Controls,
  Background,
  MiniMap,
  NodeTypes,
  EdgeTypes,
} from '@xyflow/react';
import ProcessNode from '../organisms/ProcessNode';
import ProcessEdge from '../organisms/ProcessEdge';
import ProcessFlowControls from '../organisms/ProcessFlowControls';
// API는 page.tsx에 통합되어 있음


const nodeTypes: NodeTypes = {
  processNode: ProcessNode as any,
};

const edgeTypes: EdgeTypes = {
  processEdge: ProcessEdge as any,
};

interface ProcessFlowEditorProps {
  initialNodes?: Node<any>[];
  initialEdges?: Edge<any>[];
  onFlowChange?: (nodes: Node[], edges: Edge[]) => void;
  readOnly?: boolean;
}

const ProcessFlowEditor: React.FC<ProcessFlowEditorProps> = ({
  initialNodes = [],
  initialEdges = [],
  onFlowChange,
  readOnly = false,
}) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  const onConnect = useCallback(
    (params: Connection) => {
      const newEdge: Edge<any> = {
        id: `edge-${Date.now()}`,
        source: params.source!,
        target: params.target!,
        type: 'processEdge',
        data: {
          label: '공정 흐름',
          processType: 'standard',
        },
      };
      setEdges((eds: any) => addEdge(newEdge, eds));
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
    const newNode: Node<any> = {
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
    setNodes((nds: any) => [...nds, newNode]);
  }, [setNodes]);

  const deleteSelectedElements = useCallback(() => {
    const selectedNodes = nodes.filter((node: any) => node.selected);
    const selectedEdges = edges.filter((edge: any) => edge.selected);
    
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      setNodes((nds: any) => nds.filter((node: any) => !node.selected));
      setEdges((eds: any) => eds.filter((edge: any) => !edge.selected));
    }
  }, [nodes, edges, setNodes, setEdges]);

  const saveFlow = useCallback(() => {
    // 부모 컴포넌트에서 API 호출 처리
    if (onFlowChange) {
      onFlowChange(nodes, edges);
    }
    
    // 로컬 스토리지에 백업 저장
    const flowData = {
      nodes,
      edges,
      timestamp: new Date().toISOString(),
    };
    localStorage.setItem('processFlow', JSON.stringify(flowData));
    
    console.log('✅ 공정도 로컬 저장 완료');
  }, [nodes, edges, onFlowChange]);

  const loadFlow = useCallback(() => {
    // 로컬 스토리지에서 로드
    const savedFlow = localStorage.getItem('processFlow');
    if (savedFlow) {
      try {
        const flowData = JSON.parse(savedFlow);
        setNodes(flowData.nodes || []);
        setEdges(flowData.edges || []);
        console.log('✅ 로컬 저장소에서 공정도 로드 완료');
      } catch (error) {
        console.error('로컬 저장소 로드 실패:', error);
      }
    } else {
      console.log('📝 저장된 공정도가 없습니다.');
    }
  }, [setNodes, setEdges]);

  return (
    <div className="w-full h-full min-h-[600px]">
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
      >
        <Controls />
        <Background variant={"dots" as any} />
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
        
        <ProcessFlowControls
          onAddNode={addProcessNode}
          onDeleteSelected={deleteSelectedElements}
          onSave={saveFlow}
          onLoad={loadFlow}
          readOnly={readOnly}
        />
      </ReactFlow>
    </div>
  );
};

export default ProcessFlowEditor;
