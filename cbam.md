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

'use client';

import React from 'react';
import { Handle, Position } from '@xyflow/react';

type HandleType = 'source' | 'target';

const color = {
  bg: '!bg-green-600',
  hoverBg: 'hover:!bg-green-700',
  ring: 'hover:!ring-green-300',
  shadow: 'drop-shadow(0 0 8px rgba(34,197,94,.3))',
};

const baseCls =
  '!w-4 !h-4 !border-2 !border-white transition-all duration-200 ' +
  'cursor-crosshair hover:!scale-110 hover:!shadow-lg hover:!ring-4 ' +
  'hover:!ring-opacity-50 pointer-events-auto';

const cls = `${baseCls} ${color.bg} ${color.hoverBg} ${color.ring}`;
const styleBase: React.CSSProperties = { filter: color.shadow, zIndex: 10 };

/**
 * 각 방향마다 source/target 두 개를 배치.
 * - Left/Right: 위아래로 살짝 분리
 * - Top/Bottom: 좌우로 살짝 분리
 */
export const renderFourDirectionHandles = (isConnectable = true) => {
  const gap = 10; // px 분리 간격

  const pairs: Array<{
    position: Position;
    items: Array<{ type: HandleType; idSuffix: string; style: React.CSSProperties }>;
  }> = [
    {
      position: Position.Left,
      items: [
        { type: 'target', idSuffix: 'target', style: { top: `calc(50% - ${gap}px)`, left: -8 } },
        { type: 'source', idSuffix: 'source', style: { top: `calc(50% + ${gap}px)`, left: -8 } },
      ],
    },
    {
      position: Position.Right,
      items: [
        { type: 'target', idSuffix: 'target', style: { top: `calc(50% - ${gap}px)`, right: -8 } },
        { type: 'source', idSuffix: 'source', style: { top: `calc(50% + ${gap}px)`, right: -8 } },
      ],
    },
    {
      position: Position.Top,
      items: [
        { type: 'target', idSuffix: 'target', style: { top: -8, left: `calc(50% - ${gap}px)` } },
        { type: 'source', idSuffix: 'source', style: { top: -8, left: `calc(50% + ${gap}px)` } },
      ],
    },
    {
      position: Position.Bottom,
      items: [
        { type: 'target', idSuffix: 'target', style: { bottom: -8, left: `calc(50% - ${gap}px)` } },
        { type: 'source', idSuffix: 'source', style: { bottom: -8, left: `calc(50% + ${gap}px)` } },
      ],
    },
  ];

  return pairs.flatMap(({ position, items }) =>
    items.map(({ type, idSuffix, style }) => {
      const id = `${position}-${idSuffix}`; // 예: "top-source"
      return (
        <Handle
          key={id}
          id={id}
          type={type}
          position={position}
          isConnectable={isConnectable}
          className={cls}
          style={{ ...styleBase, ...style }}
        />
      );
    })
  );
};

/* 그룹 노드 등에서 쓸 기본 핸들 스타일 */
export const handleStyle = {
  background: '#3b82f6',
  width: 12,
  height: 12,
  border: '2px solid white',
  borderRadius: '50%',
};
프로젝트의 HandleStyles.tsx 파일을 수정해줘.
목표:
- 각 방향(좌/우/상/하)에 source와 target 핸들을 모두 배치할 수 있어야 한다.
- 두 핸들이 같은 좌표에 겹치지 않도록 몇 px씩 어긋나게 배치한다.
- 모든 방향에서 드래그 시작과 드롭이 가능해야 하며, source → target 연결이 정상적으로 동작해야 한다.
작업:
1. renderFourDirectionHandles 함수에서 각 Position(Left, Right, Top, Bottom)에 대해 source/target 두 개씩 렌더링한다.
2. Left/Right는 세로 방향으로 10px 간격, Top/Bottom은 가로 방향으로 10px 간격을 둔다.
3. 각 핸들에는 `${position}-${type}` 형태의 고유 id를 부여한다. (예: top-source, left-target)
4. 스타일에는 zIndex: 10을 줘서 노드 위에서 항상 클릭 가능하게 한다.
5. 기존 handleColorMap, colorStyles는 제거하고, 위 코드처럼 통합된 green 스타일을 사용한다.
검증:
- 제품 노드의 위/아래/좌/우 모든 방향에서 엣지가 생성되고 서로 연결 가능해야 한다.
- source→source, target→target 연결은 무시된다(React Flow 기본 동작).


위 프롬프트와 코드들을 참고하라