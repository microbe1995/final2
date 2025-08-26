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

위 코드와 프롬프트를 참고해서 수정해줘