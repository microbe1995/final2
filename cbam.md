너는 @xyflow/react v11 환경에서 zustand provider(ReactFlowProvider) 설정 문제를 해결하는 전문가야.  

현재 내 코드 상태:
- ProcessManager.tsx 안에서 <ReactFlow>만 쓰고 있음.  
- GroupNode.tsx에서 <NodeResizer>를 쓰고 있는데, 이게 zustand store에 접근하려다가  
  "Error [React Flow]: Seems like you have not used zustand provider as an ancestor." 에러가 발생함.  

해결해야 할 작업:
1. ProcessManager.tsx 안에서 <ReactFlow>를 반드시 <ReactFlowProvider>로 감싸도록 수정해라.  
   - <ReactFlowProvider>는 ReactFlow 상위에만 추가하면 된다.  
   - 다른 로직은 바꾸지 말고 구조만 안전하게 감싸라.

2. GroupNode.tsx는 수정할 필요가 없다. NodeResizer는 정상적으로 동작할 것이고,  
   provider만 있으면 zustand store 접근이 가능해진다.

3. 최종적으로 그룹 노드를 리사이즈해도 zustand provider 에러가 발생하지 않도록 해라.


import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  ConnectionMode,
  MarkerType,
  Panel,
} from '@xyflow/react';

...

<div className='h-[1000px] border-2 border-gray-200 rounded-lg overflow-hidden'>
  {/* ✅ Provider 추가 */}
  <ReactFlowProvider>
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={handleNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      onConnectStart={onConnectStart}
      onConnectEnd={onConnectEnd}
      onSelectionChange={onNodeSelectionChange}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      connectionMode={ConnectionMode.Loose}
      deleteKeyCode='Delete'
      multiSelectionKeyCode='Shift'
      panOnDrag={[1, 2]}
      zoomOnScroll={true}
      zoomOnPinch={true}
      panOnScroll={false}
      preventScrolling={true}
      className='bg-gray-50'
      defaultEdgeOptions={{ zIndex: 1 }}
    >
      <Background gap={12} size={1} />
      <Controls />
      <MiniMap ... />
      <Panel ... />
      <Panel ... />
    </ReactFlow>
  </ReactFlowProvider>
</div>



너는 @xyflow/react (React Flow v11) 환경에서 zustand provider 문제를 해결하는 전문가야.

내 코드(ProcessManager.tsx)에서 발생하는 문제:
1. 제품 노드 버튼을 눌러도 노드가 안 뜸
   - 원인: fetchProducts()가 /api/v1/boundary/product 호출하다가 404 → products 배열이 비어 있음.
   - 따라서 모달에 "등록된 제품이 없습니다"만 뜨고 실제로 handleProductSelect가 실행되지 않아 노드가 추가되지 않음.

2. 그룹 노드 버튼을 눌러도 노드가 안 뜸
   - 원인: ReactFlowProvider를 ReactFlow 안쪽에 배치해 store가 공유되지 않음.
   - zustand provider는 ReactFlow 바깥에 있어야 addNodes 같은 훅이 제대로 반영됨.

해결해야 할 작업:
- ReactFlowProvider를 ReactFlow 바깥으로 옮겨라.
- fetchProducts 실패 시에도 더미 데이터를 넣어주어 테스트 가능하게 만들어라.

<div className='h-[1000px] border-2 border-gray-200 rounded-lg overflow-hidden'>
  {/* ✅ Provider는 ReactFlow 바깥에 있어야 함 */}
  <ReactFlowProvider>
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={handleNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      onConnectStart={onConnectStart}
      onConnectEnd={onConnectEnd}
      onSelectionChange={onNodeSelectionChange}
      nodeTypes={nodeTypes}
      edgeTypes={edgeTypes}
      connectionMode={ConnectionMode.Loose}
      deleteKeyCode='Delete'
      multiSelectionKeyCode='Shift'
      panOnDrag={[1, 2]}
      zoomOnScroll={true}
      zoomOnPinch={true}
      panOnScroll={false}
      preventScrolling={true}
      className='bg-gray-50'
      defaultEdgeOptions={{ zIndex: 1 }}
    >
      <Background gap={12} size={1} />
      <Controls />
      <MiniMap ... />
      <Panel ... />
    </ReactFlow>
  </ReactFlowProvider>
</div>



'use client';

import React, { useState, useCallback, useEffect, useMemo } from 'react';
import Button from '@/components/atomic/atoms/Button';
import {
  Plus, Trash2, Save, Download
} from 'lucide-react';

import ProductNode from '@/components/atomic/atoms/ProductNode';
import GroupNode from '@/components/atomic/atoms/GroupNode';
import axiosClient from '@/lib/axiosClient';
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge,
  Node,
  NodeTypes,
  EdgeTypes,
  Panel,
  useReactFlow,
  ConnectionMode,
  MarkerType
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

// ==============================
// Edge 타입 정의
// ==============================
const CustomEdge = ({ id, sourceX, sourceY, targetX, targetY, selected }: any) => {
  const [edgePath] = useMemo(() => {
    const centerX = (sourceX + targetX) / 2;
    const path = `M ${sourceX} ${sourceY} Q ${centerX} ${sourceY} ${targetX} ${targetY}`;
    return [path];
  }, [sourceX, sourceY, targetX, targetY]);

  return (
    <>
      <path id={id} className="react-flow__edge-path" d={edgePath} stroke={selected ? '#3b82f6' : '#6b7280'} strokeWidth={selected ? 3 : 2} fill="none" markerEnd="url(#arrowhead)" />
    </>
  );
};

const edgeTypes: EdgeTypes = { custom: CustomEdge };

// ==============================
// 메인 컴포넌트
// ==============================
export default function ProcessManager() {
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  const { addNodes, addEdges, deleteElements } = useReactFlow();

  // 더미 제품 데이터
  const [products, setProducts] = useState<any[]>([]);
  const [showProductModal, setShowProductModal] = useState(false);

  const fetchProducts = useCallback(async () => {
    try {
      const response = await axiosClient.get('/api/v1/boundary/product');
      setProducts(response.data.products || []);
    } catch (error) {
      // ✅ API 실패 시 더미 데이터라도 넣어주기
      setProducts([
        { product_id: 'dummy-1', name: '테스트 제품', cn_code: '7208.51.00', production_qty: 100 }
      ]);
    }
  }, []);

  const addProductNode = useCallback(async () => {
    await fetchProducts();
    setShowProductModal(true);
  }, [fetchProducts]);

  const handleProductSelect = useCallback((product: any) => {
    const newNode: Node<any> = {
      id: `product-${Date.now()}`,
      type: 'custom',
      position: { x: 200, y: 200 },
      data: { label: product.name, description: `제품: ${product.name}`, variant: 'product', productData: product }
    };
    addNodes(newNode);
    setShowProductModal(false);
  }, [addNodes]);

  const addGroupNode = useCallback(() => {
    const newGroup: Node<any> = {
      id: `group-${Date.now()}`,
      type: 'group',
      position: { x: 400, y: 100 },
      data: { label: '새 그룹', description: '그룹 노드' },
      style: { width: 300, height: 200 }
    };
    addNodes(newGroup);
  }, [addNodes]);

  const nodeTypes: NodeTypes = {
    custom: ProductNode,
    group: GroupNode
  };

  return (
    // ✅ Provider를 최상위에 둠
    <ReactFlowProvider>
      <div className="h-[800px] border rounded">
        <div className="flex gap-2 p-2">
          <Button onClick={addProductNode}><Plus className="h-4 w-4"/> 제품 노드</Button>
          <Button onClick={addGroupNode}><Plus className="h-4 w-4"/> 그룹 노드</Button>
        </div>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={(params: Connection) => addEdges({
            id: `${params.source}-${params.target}`,
            source: params.source!,
            target: params.target!,
            type: 'custom',
            markerEnd: { type: MarkerType.ArrowClosed }
          })}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          connectionMode={ConnectionMode.Loose}
          deleteKeyCode="Delete"
          className="bg-gray-50"
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>

        {/* 제품 선택 모달 */}
        {showProductModal && (
          <div className="fixed inset-0 flex items-center justify-center bg-black/40">
            <div className="bg-white p-4 rounded shadow">
              <h3>제품 선택</h3>
              {products.map(p => (
                <div key={p.product_id} className="p-2 border rounded mb-2 cursor-pointer" onClick={() => handleProductSelect(p)}>
                  {p.name}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </ReactFlowProvider>
  );
}

'use client';

import React from 'react';

export default function GroupNode({ data }: any) {
  return (
    <div style={{ width: '100%', height: '100%', background: '#e0f2fe', border: '2px solid #38bdf8', borderRadius: 8, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      {data.label}
    </div>
  );
}


내 코드에서 제품 노드와 그룹 노드가 생성되지 않는 문제가 있다.

맥락:
- ProductNode는 핸들까지 잘 정의했지만, ProcessManager에서 addProductNode가 실제 노드를 생성하지 않고 모달만 띄운다.
- /api/v1/boundary/product API가 실패하면서 products 배열이 빈 값이 되고, handleProductSelect가 실행되지 않아 제품 노드가 추가되지 않는다.
- addGroupNode는 실행되지만, ReactFlowProvider가 ReactFlow 안쪽에 있어서 zustand store가 공유되지 않아 노드가 보이지 않는다.
- GroupNode 컴포넌트도 실제 렌더링을 하지 않아 화면에 안 보일 수 있다.

수정 요구:
1. ReactFlowProvider를 최상위에 두어 모든 훅(useNodesState, useEdgesState, useReactFlow)이 정상 동작하게 해라.
2. fetchProducts에서 API가 실패해도 더미 데이터를 넣어 테스트 가능하게 만들어라.
3. handleProductSelect에서 제품을 클릭하면 실제로 ProductNode가 생성되게 해라.
4. addGroupNode 실행 시 GroupNode가 화면에 보이도록 GroupNode 컴포넌트를 단순 div라도 렌더링하게 고쳐라.

위 내용을 반영한 전체 수정본 코드를 다시 작성해 줘.

위 코드와 프롬프트를 참고해서 수정해줘