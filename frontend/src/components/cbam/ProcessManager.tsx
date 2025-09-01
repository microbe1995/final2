'use client';

import React, { useState, useCallback, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import { Plus } from 'lucide-react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

import ProductNode from '@/components/atomic/atoms/ProductNode';
import ProcessNode from '@/components/atomic/atoms/ProcessNode';
import InputManager from '@/components/cbam/InputManager';
import { InstallSelector } from '@/components/cbam/InstallSelector';
import { ProductSelector } from '@/components/cbam/ProductSelector';
import { ProcessSelector, ProductProcessModal } from '@/components/cbam/ProcessSelector';


import { useProcessManager, Process, Install, Product } from '@/hooks/useProcessManager';
import { useProcessCanvas } from '@/hooks/useProcessCanvas';

import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  NodeTypes,
  EdgeTypes,
  ConnectionMode,
  MarkerType,
  Connection
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

/* ============================================================================
   커스텀 Edge 타입 정의
============================================================================ */
import CustomEdge from '@/components/atomic/atoms/CustomEdge';
const edgeTypes: EdgeTypes = { custom: CustomEdge };

/* ============================================================================
   내부 컴포넌트
============================================================================ */
function ProcessManagerInner() {
  // 커스텀 훅 사용
  const {
    installs,
    selectedInstall,
    products,
    selectedProduct,
    processes,
    allProcesses,
    crossInstallProcesses,
    isDetectingChains,
    detectionStatus,
    isUpdatingProduct,
    setSelectedInstall,
    setSelectedProduct,
    fetchProcessesByProduct,
    handleProductQuantityUpdate,
  } = useProcessManager();

  // React Flow 컨텍스트 내에서만 useProcessCanvas 사용
  const {
    nodes,
    edges,
    installCanvases,
    activeInstallId,
    onNodesChange,
    onEdgesChange,
    handleEdgeCreate,
    handleInstallSelect: handleCanvasInstallSelect,
    addProductNode,
    addProcessNode,
    addGroupNode,
    updateNodeData,
  } = useProcessCanvas(selectedInstall);

  // 공정별 직접귀속배출량 정보 가져오기
  const fetchProcessEmissionData = useCallback(async (processId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.calculation.process.attrdir(processId));
      if (response.data) {
        return {
          attr_em: response.data.attrdir_em || 0,
          total_matdir_emission: response.data.total_matdir_emission || 0,
          total_fueldir_emission: response.data.total_fueldir_emission || 0,
          calculation_date: response.data.calculation_date
        };
      }
    } catch (error) {
      console.log(`⚠️ 공정 ${processId}의 배출량 정보가 아직 없습니다.`);
    }
    return null;
  }, []);

  // 모든 공정 노드의 배출량 정보 새로고침
  const refreshAllProcessEmissions = useCallback(async () => {
    const processNodes = nodes.filter(node => node.type === 'process');
    
    for (const node of processNodes) {
      const processId = node.data.id;
      if (processId && typeof processId === 'number') {
        const emissionData = await fetchProcessEmissionData(processId);
        if (emissionData && node.data.processData) {
          // 노드 데이터 업데이트
          updateNodeData(node.id, {
            processData: {
              ...node.data.processData,
              ...emissionData
            }
          });
        }
      }
    }
  }, [nodes, fetchProcessEmissionData, updateNodeData]);

  // 모달 상태
  const [showProductModal, setShowProductModal] = useState(false);
  const [showProcessModalForProduct, setShowProcessModalForProduct] = useState(false);
  const [showProcessModal, setShowProcessModal] = useState(false);
  const [showInputModal, setShowInputModal] = useState(false);
  const [selectedProcessForInput, setSelectedProcessForInput] = useState<Process | null>(null);



  // 사업장 선택 처리
  const handleInstallSelect = useCallback((install: Install) => {
    setSelectedInstall(install);
    // 캔버스 상태는 useProcessCanvas에서 자동으로 처리됨
  }, [setSelectedInstall]);

  // 제품 노드 추가
  const handleAddProductNode = useCallback(async () => {
    if (!selectedInstall) {
      alert('먼저 사업장을 선택해주세요.');
      return;
    }
    setShowProductModal(true);
  }, [selectedInstall]);

  // 제품 선택 처리
  const handleProductSelect = useCallback((product: Product) => {
    addProductNode(product, handleProductNodeClickComplex);
    setShowProductModal(false);
  }, [addProductNode]);

  // 제품 노드 클릭 시 복잡한 다대다 관계 공정 선택 모달 열기
  const handleProductNodeClickComplex = useCallback((productData: Product) => {
    setSelectedProduct(productData);
    setShowProcessModal(true);
  }, []);

  // 투입량 입력 모달 열기
  const openInputModal = useCallback((process: Process) => {
    setSelectedProcessForInput(process);
    setShowInputModal(true);
  }, []);

  // 공정 선택 처리
  const handleProcessSelect = useCallback(async (process: Process) => {
    await addProcessNode(process, products, openInputModal, openInputModal);
    setShowProcessModal(false);
    setShowProcessModalForProduct(false);
  }, [addProcessNode, products, openInputModal]);



  // Edge 연결 처리
  const handleConnect = useCallback(async (params: Connection) => {
    try {
      console.log('🔗 연결 시도:', params);
      console.log('📍 연결 정보:', {
        source: params.source,
        target: params.target,
        sourceHandle: params.sourceHandle,
        targetHandle: params.targetHandle
      });
      
      // 연결 처리
      await handleEdgeCreate(params, () => {});
      
      console.log('✅ 연결 처리 완료');
      alert(`연결이 성공적으로 생성되었습니다!\n${params.source} → ${params.target}`);
      
    } catch (error) {
      console.error('❌ 연결 처리 실패:', error);
      alert(`연결 처리에 실패했습니다: ${error}`);
    }
  }, [handleEdgeCreate]);

  // 🔧 React Flow 공식 문서에 따른 단순화된 연결 검증 로직
  const validateConnection = useCallback((connection: Connection) => {
    console.log('🔍 연결 검증 시작:', connection);
    console.log('📍 검증 대상:', {
      source: connection.source,
      target: connection.target,
      sourceHandle: connection.sourceHandle,
      targetHandle: connection.targetHandle
    });
    
    // ✅ React Flow 공식 문서: 같은 노드 간 연결 방지
    if (connection.source === connection.target) {
      console.log('❌ 같은 노드 간 연결 시도');
      return { valid: false, reason: '같은 노드 간 연결은 불가능합니다' };
    }
    
    // ✅ React Flow 공식 문서: 같은 핸들 간 연결 방지
    if (connection.sourceHandle && connection.targetHandle && 
        connection.sourceHandle === connection.targetHandle) {
      console.log('❌ 같은 핸들 간 연결 시도');
      return { valid: false, reason: '같은 핸들 간 연결은 불가능합니다' };
    }
    
    // ✅ React Flow 공식 문서: 이미 존재하는 연결 확인 (핸들 ID까지 포함하여 정확히 같은 연결만 체크)
    const existingEdge = edges.find(edge => 
      edge.source === connection.source && 
      edge.target === connection.target &&
      edge.sourceHandle === connection.sourceHandle &&
      edge.targetHandle === connection.targetHandle
    );
    
    if (existingEdge) {
      console.log('❌ 이미 존재하는 연결 (핸들 ID 포함):', existingEdge);
      return { valid: false, reason: '이미 존재하는 연결입니다' };
    }
    
    // ✅ React Flow 공식 문서: 추가 검증 - 임시 엣지와의 중복 방지
    const tempEdgeExists = edges.find(edge => 
      edge.data?.isTemporary &&
      edge.source === connection.source && 
      edge.target === connection.target &&
      edge.sourceHandle === connection.sourceHandle &&
      edge.targetHandle === connection.targetHandle
    );
    
    if (tempEdgeExists) {
      console.log('❌ 임시 엣지와 중복:', tempEdgeExists);
      return { valid: false, reason: '연결 처리 중입니다. 잠시 기다려주세요.' };
    }
    
    console.log('✅ React Flow 연결 검증 통과');
    return { valid: true, reason: '연결이 유효합니다' };
  }, [edges]);

  // 🔧 단순화된 연결 이벤트 핸들러
  const handleConnectStart = useCallback((event: any, params: any) => {
    console.log('🔗 연결 시작:', params);
  }, []);

  const handleConnectEnd = useCallback((event: any) => {
    console.log('🔗 연결 종료:', event);
  }, []);

  const nodeTypes: NodeTypes = { 
    product: ProductNode,  // 🔴 수정: 'product' 타입 추가
    process: ProcessNode,  // 🔴 수정: 'process' 타입으로 변경
    group: ProductNode     // 🔴 추가: 그룹 노드도 ProductNode로 렌더링
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* 헤더 */}
      <div className="bg-gray-900 text-white p-4">
        <h1 className="text-2xl font-bold">CBAM 산정경계설정</h1>
        <p className="text-gray-300">CBAM 배출량 산정을 위한 경계를 설정하고 노드를 생성합니다.</p>
      </div>

      {/* 사업장 선택 */}
      <InstallSelector
        installs={installs}
        selectedInstall={selectedInstall}
        installCanvases={installCanvases}
        activeInstallId={activeInstallId}
        onInstallSelect={handleInstallSelect}
        onAddInstall={() => {}} // 사업장 추가 기능은 별도로 구현 필요
      />

      {/* 버튼 */}
      <div className="bg-gray-800 p-4 flex gap-2">
        <Button 
          onClick={handleAddProductNode} 
          disabled={!selectedInstall} 
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus className="h-4 w-4" /> 제품 노드
        </Button>
        <Button 
          onClick={addGroupNode} 
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          <Plus className="h-4 w-4" /> 그룹 노드
        </Button>

        
        <Button 
          onClick={refreshAllProcessEmissions} 
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          📊 배출량 정보 새로고침
        </Button>

      </div>
      


      {/* ReactFlow 캔버스 */}
      <div className="flex-1 relative">
                 {/* 디버깅 정보 */}
         <div className="absolute top-2 right-2 bg-black bg-opacity-75 text-white p-2 rounded text-xs z-10">
           <div>노드 수: {nodes.length}</div>
           <div>연결 수: {edges.length}</div>
           <div>사업장: {selectedInstall?.install_name || '선택 안됨'}</div>
           <div>모드: Loose (다중 핸들 연결 가능)</div>
           <div>핸들 수: {nodes.reduce((acc, node) => acc + (node.data?.showHandles ? 4 : 0), 0)}</div>
           <div>최대 연결 가능: {nodes.length * 4}</div>
           <div className="mt-2 pt-2 border-t border-gray-600">
             <div className="text-yellow-400">🔗 연결 테스트</div>
             <div>노드 간 드래그하여 연결</div>
             <div>콘솔에서 이벤트 확인</div>
           </div>
         </div>
                 <ReactFlow
           nodes={nodes}
           edges={edges}
           onNodesChange={onNodesChange}
           onEdgesChange={onEdgesChange}
           nodeTypes={nodeTypes}
           edgeTypes={edgeTypes}
           connectionMode={ConnectionMode.Loose}
           defaultEdgeOptions={{ type: 'custom', markerEnd: { type: MarkerType.ArrowClosed } }}
           deleteKeyCode="Delete"
           className="bg-gray-900"
           fitView
           onConnectStart={(event, params) => {
             console.log('🔗 4방향 연결 시작:', params);
             handleConnectStart(event, params);
           }}
           onConnect={(params) => {
             console.log('🔗 4방향 연결 완료:', params);
             const validation = validateConnection(params);
             if (validation.valid) {
               console.log('✅ 연결 검증 통과, 연결 처리 시작');
               handleConnect(params);
             } else {
               console.log(`❌ 연결 검증 실패: ${validation.reason}`, params);
               alert(`연결이 유효하지 않습니다: ${validation.reason}`);
             }
           }}
           onConnectEnd={handleConnectEnd}
           isValidConnection={(connection) => {
             const validation = validateConnection(connection as Connection);
             return validation.valid;
           }}
         >
          <Background color="#334155" gap={24} size={1} />
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

      {/* 모달들 */}
      {showProductModal && (
        <ProductSelector
          products={products}
          onProductSelect={handleProductSelect}
          onClose={() => setShowProductModal(false)}
        />
      )}

      {showProcessModalForProduct && (
        <ProcessSelector
          processes={processes}
          allProcesses={allProcesses}
          products={products}
          installs={installs}
          selectedProduct={selectedProduct}
          selectedInstall={selectedInstall}
          onProcessSelect={handleProcessSelect}
          onClose={() => setShowProcessModalForProduct(false)}
        />
      )}

      {showProcessModal && (
        <ProductProcessModal
          selectedProduct={selectedProduct}
          allProcesses={allProcesses}
          products={products}
          installs={installs}
          selectedInstall={selectedInstall}
          onProcessSelect={handleProcessSelect}
          onClose={() => setShowProcessModal(false)}
        />
      )}

      {showInputModal && selectedProcessForInput && (
        <InputManager
          selectedProcess={selectedProcessForInput}
          onClose={() => setShowInputModal(false)}
          onDataSaved={refreshAllProcessEmissions} // 데이터 저장 후 배출량 정보 새로고침
        />
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
