Next.js(앱 라우터) + TypeScript

@xyflow/react v12 사용

ProductNode는 커스텀 컴포넌트, group은 내장 타입을 사용한다.

에러 증상: 제품 노드 4방향 핸들에서 연결이 되지 않거나 일부만 동작. group 노드 클릭 시 클라이언트 에러.

목표

제품 노드에 4개 핸들(좌/우/상/하)을 모두 사용 가능하게 하고, 각 핸들 간 연결이 안정적으로 동작하도록 한다.

group 노드는 내장 타입을 유지하여 클릭/리사이즈/선택 시 에러가 발생하지 않게 한다.

커스텀 엣지의 markerEnd 지정은 ReactFlow의 defaultEdgeOptions 한 곳에서만 설정한다.

작업 지시

components/atomic/atoms/ProductNode.tsx

각 Handle에 고유 id: "left", "right", "top", "bottom"을 부여한다.

type, position을 좌=target, 우=source, 상=target, 하=source로 배치한다.

isConnectable을 전달하고 pointerEvents가 막히지 않도록 wrapper에 pointerEvents: 'auto'를 준다.

app/**/ProcessManager.tsx(또는 해당 페이지 컴포넌트)

nodeTypes에서 group 매핑을 제거하고 { custom: ProductNode }만 남긴다.

ReactFlow onConnect 핸들러에서 params.sourceHandle과 params.targetHandle을 edge에 포함한다.

defaultEdgeOptions={{ type:'custom', markerEnd:{ type: MarkerType.ArrowClosed } }}를 설정한다.

group 노드는 type: 'group'으로 내장 타입을 쓰며, style로만 테두리/배경을 지정한다. pointerEvents는 'auto'.

components/**/edges/CustomEdge.tsx

path 요소에서 markerEnd 속성을 제거한다(중복 방지).

stroke, strokeWidth만 유지한다.

검증 기준

제품 노드의 4개 핸들 각각에서 드래그 시작이 가능하고, 연결 시 onConnect의 params에 sourceHandle/targetHandle이 포함된다.

동일 노드 간 상이한 핸들로 여러 엣지를 추가할 수 있다(핸들 id가 반영된 edge 구조).

group 노드 클릭/선택/리사이즈 시 클라이언트 에러가 발생하지 않는다.

MiniMap/Controls/Background가 정상 동작한다.

마이그레이션 주의

이전에 생성된 edge 데이터에 sourceHandle/targetHandle 누락분이 있으면 삭제 후 재연결한다.

만약 스타일 시트에서 .react-flow__handle에 pointer-events 관련 오버라이드가 있다면 제거한다.


'use client';

import React, { useState, useCallback } from 'react';
import Button from '@/components/atomic/atoms/Button';
import { Plus } from 'lucide-react';

import ProductNode from '@/components/atomic/atoms/ProductNode';
// import GroupNode from '@/components/atomic/atoms/GroupNode'; // 제거: 내장 group 사용
import axiosClient from '@/lib/axiosClient';

import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  Connection,
  Node,
  NodeTypes,
  EdgeTypes,
  useReactFlow,
  ConnectionMode,
  MarkerType,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

/* ============================================================================
   커스텀 Edge
   - markerEnd는 defaultEdgeOptions에서만 설정(중복 방지)
============================================================================ */
const CustomEdge = ({ id, sourceX, sourceY, targetX, targetY, selected }: any) => {
  const [edgePath] = React.useMemo(() => {
    const cx = (sourceX + targetX) / 2;
    return [`M ${sourceX} ${sourceY} Q ${cx} ${sourceY} ${targetX} ${targetY}`];
  }, [sourceX, sourceY, targetX, targetY]);

  return (
    <path
      id={id}
      className="react-flow__edge-path"
      d={edgePath}
      stroke={selected ? '#3b82f6' : '#6b7280'}
      strokeWidth={selected ? 3 : 2}
      fill="none"
    />
  );
};

const edgeTypes: EdgeTypes = { custom: CustomEdge };

/* ============================================================================
   내부 컴포넌트
============================================================================ */
function ProcessManagerInner() {
  // 상태 훅
  const [nodes, , onNodesChange] = useNodesState<any>([]);
  const [edges, , onEdgesChange] = useEdgesState<any>([]);
  const { addNodes, addEdges } = useReactFlow();

  // 제품 목록 모달 상태
  const [products, setProducts] = useState<any[]>([]);
  const [showProductModal, setShowProductModal] = useState(false);

  // 제품 불러오기
  const fetchProducts = useCallback(async () => {
    try {
      const res = await axiosClient.get('/api/v1/boundary/product');
      setProducts(res.data.products || []);
    } catch {
      setProducts([
        { product_id: 'dummy-1', name: '테스트 제품 1', cn_code: '7208.51.00', production_qty: 1000, sales_qty: 800, export_qty: 200, inventory_qty: 150, defect_rate: 0.05, period_start: '2024-01-01', period_end: '2024-12-31' },
        { product_id: 'dummy-2', name: '테스트 제품 2', cn_code: '7208.52.00', production_qty: 2000, sales_qty: 1800, export_qty: 400, inventory_qty: 300, defect_rate: 0.03, period_start: '2024-01-01', period_end: '2024-12-31' },
        { product_id: 'dummy-3', name: '테스트 제품 3', cn_code: '7208.53.00', production_qty: 1500, sales_qty: 1200, export_qty: 300, inventory_qty: 200, defect_rate: 0.07, period_start: '2024-01-01', period_end: '2024-12-31' },
      ]);
    }
  }, []);

  // 제품 노드 추가(모달 열기)
  const addProductNode = useCallback(async () => {
    await fetchProducts();
    setShowProductModal(true);
  }, [fetchProducts]);

  // 제품 선택 → 노드 추가
  const handleProductSelect = useCallback((product: any) => {
    const newNode: Node<any> = {
      id: `product-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'custom',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        label: product.name,
        description: `제품: ${product.name}`,
        variant: 'product',
        productData: product,
        name: product.name,
        type: 'output',
        parameters: {
          product_id: product.product_id,
          cn_code: product.cn_code,
          production_qty: product.production_qty,
          sales_qty: product.sales_qty,
          export_qty: product.export_qty,
          inventory_qty: product.inventory_qty,
          defect_rate: product.defect_rate,
          period_start: product.period_start,
          period_end: product.period_end,
        },
        status: 'active',
      },
    };
    addNodes(newNode);
    setShowProductModal(false);
  }, [addNodes]);

  // 그룹 노드 추가(내장 group 타입 사용)
  const addGroupNode = useCallback(() => {
    const id = `group-${Date.now()}-${Math.random().toString(36).slice(2)}`;
    addNodes({
      id,
      type: 'group', // 내장 타입. 커스텀 컴포넌트 매핑 금지
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: { label: `그룹 ${id}`, description: '산정경계' },
      style: {
        width: 420,
        height: 320,
        border: '2px solid #a78bfa',
        borderRadius: 12,
        background: '#0b1220', // 다크 배경
        pointerEvents: 'auto',
      },
      className: 'shadow-sm',
    });
  }, [addNodes]);

  // 커스텀 노드 매핑(제품만)
  const nodeTypes: NodeTypes = { custom: ProductNode };

  return (
    <div className="w-full h-full flex flex-col">
      {/* 헤더 */}
      <div className="bg-gray-900 text-white p-4">
        <h1 className="text-2xl font-bold">CBAM 프로세스 관리</h1>
        <p className="text-gray-300">CBAM 관련 프로세스 플로우를 생성하고 관리합니다.</p>
      </div>

      {/* 버튼 */}
      <div className="bg-gray-800 p-4 flex gap-2">
        <Button onClick={addProductNode} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus className="h-4 w-4" /> 제품 노드
        </Button>
        <Button onClick={addGroupNode} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus className="h-4 w-4" /> 그룹 노드
        </Button>
      </div>

      {/* ReactFlow 캔버스 */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={(params: Connection) =>
            addEdges({
              id: `e-${Date.now()}-${Math.random().toString(36).slice(2)}`,
              source: params.source!,
              target: params.target!,
              sourceHandle: params.sourceHandle ?? undefined,
              targetHandle: params.targetHandle ?? undefined,
              type: 'custom',
            })
          }
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          connectionMode={ConnectionMode.Loose}
          defaultEdgeOptions={{ type: 'custom', markerEnd: { type: MarkerType.ArrowClosed } }}
          deleteKeyCode="Delete"
          className="bg-gray-900" // 다크 캔버스
          fitView
        >
          <Background variant="dots" color="#334155" gap={24} size={1} />
          <Controls className="!bg-gray-800 !border !border-gray-700 !text-gray-200 !rounded-md" position="bottom-left" />
          <MiniMap
            className="!border !border-gray-700 !rounded-md"
            style={{ backgroundColor: '#0b1220' }}
            maskColor="rgba(17,24,39,0.6)"
            nodeColor={() => '#a78bfa'}
            nodeStrokeColor={() => '#e5e7eb'}
            pannable
            zoomable
          />
        </ReactFlow>
      </div>

      {/* 제품 선택 모달 */}
      {showProductModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/40 z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-md w-full mx-4">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">제품 선택</h3>
              <button onClick={() => setShowProductModal(false)} className="text-gray-400 hover:text-gray-600">✕</button>
            </div>
            <div className="space-y-2">
              {products.map((p) => (
                <div
                  key={p.product_id}
                  className="p-3 border rounded-lg cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-colors"
                  onClick={() => handleProductSelect(p)}
                >
                  <div className="font-medium">{p.name}</div>
                  <div className="text-sm text-gray-600">CN: {p.cn_code}</div>
                  <div className="text-sm text-gray-600">생산량: {p.production_qty}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

/* ============================================================================
   메인 컴포넌트
============================================================================ */
export default function ProcessManager() {
  return (
    <div className="w-full h-screen">
      <ReactFlowProvider>
        <ProcessManagerInner />
      </ReactFlowProvider>
    </div>
  );
}
리포의 @xyflow/react v12 기반 플로우 화면을 수정하라.
목표

group 노드는 내장 타입을 사용한다(커스텀 매핑 제거).

제품 노드는 4방향 핸들 연결이 모두 동작하도록 onConnect에 sourceHandle/targetHandle을 반영한다.

엣지 id 충돌이 없도록 고유 id를 생성한다.

다크 테마와 어울리도록 캔버스/Background/Controls/MiniMap 색상을 설정한다.
작업

ProcessManager.tsx에서 GroupNode import와 nodeTypes의 group 매핑을 삭제하고, group 노드 생성은 type: 'group'으로 유지한다.

onConnect에서 params.sourceHandle/targetHandle을 신규 엣지에 포함한다. defaultEdgeOptions로 markerEnd를 설정하고 CustomEdge의 path에는 markerEnd를 지정하지 않는다.

ReactFlow의 className을 bg-gray-900로 지정하고, <Background variant="dots" color="#334155" gap={24} size={1}/>로 설정한다. Controls/MiniMap은 다크 톤 클래스를 적용한다.

ProductNode.tsx에서 4개 Handle에 id(left/right/top/bottom)를 부여하고 isConnectable을 true로 둔다. wrapper에 pointerEvents: 'auto'를 준다.
검증

그룹 노드 클릭/리사이즈 시 예외 없음.

제품 노드의 4개 핸들로 엣지 연결이 모두 가능하고, 서로 다른 핸들 조합으로 복수 엣지가 유지된다.

캔버스·미니맵·컨트롤이 다크 테마와 조화된다.
위 프롬프트를 참고해서 현재 잇는 문제들을 해결해줘 
