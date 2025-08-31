'use client';

import React, { useState, useCallback, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import { Plus } from 'lucide-react';

import ProductNode from '@/components/atomic/atoms/ProductNode';
import ProcessNode from '@/components/atomic/atoms/ProcessNode';
import MatDirManager from '@/components/cbam/matdir_manager';
import FuelDirManager from '@/components/cbam/fueldir_manager';
import { InstallSelector } from '@/components/cbam/InstallSelector';
import { ProductSelector } from '@/components/cbam/ProductSelector';
import { ProcessSelector, ProductProcessModal } from '@/components/cbam/ProcessSelector';
import { IntegratedGroupsPanel } from '@/components/cbam/IntegratedGroupsPanel';

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
   커스텀 Edge
============================================================================ */
interface CustomEdgeProps {
  id: string;
  sourceX: number;
  sourceY: number;
  targetX: number;
  targetY: number;
  selected?: boolean;
}

const CustomEdge: React.FC<CustomEdgeProps> = ({ id, sourceX, sourceY, targetX, targetY, selected }) => {
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
  // 커스텀 훅 사용
  const {
    installs,
    selectedInstall,
    products,
    selectedProduct,
    processes,
    allProcesses,
    crossInstallProcesses,
    processChains,
    chainLoading,
    integratedProcessGroups,
    isDetectingChains,
    detectionStatus,
    isUpdatingProduct,
    setSelectedInstall,
    setSelectedProduct,
    fetchProcessesByProduct,
    detectIntegratedProcessGroups,
    loadIntegratedProcessGroups,
    handleProductQuantityUpdate,
  } = useProcessManager();

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
  } = useProcessCanvas(selectedInstall);

  // 모달 상태
  const [showProductModal, setShowProductModal] = useState(false);
  const [showProcessModalForProduct, setShowProcessModalForProduct] = useState(false);
  const [showProcessModal, setShowProcessModal] = useState(false);
  const [showMatDirModal, setShowMatDirModal] = useState(false);
  const [showFuelDirModal, setShowFuelDirModal] = useState(false);
  const [selectedProcessForMatDir, setSelectedProcessForMatDir] = useState<Process | null>(null);
  const [selectedProcessForFuelDir, setSelectedProcessForFuelDir] = useState<Process | null>(null);

  // Edge 생성 후 통합 공정 그룹 상태 업데이트
  const updateProcessChainsAfterEdge = useCallback(async () => {
    setTimeout(() => {
      // 여기서 processChains를 새로고침하는 로직을 추가할 수 있습니다
    }, 1000);
  }, []);

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

  // 공정 선택 처리
  const handleProcessSelect = useCallback((process: Process) => {
    addProcessNode(process, products, openMatDirModal, openFuelDirModal);
    setShowProcessModal(false);
    setShowProcessModalForProduct(false);
  }, [addProcessNode, products]);

  // 원료직접배출량 모달 열기
  const openMatDirModal = useCallback((process: Process) => {
    setSelectedProcessForMatDir(process);
    setShowMatDirModal(true);
  }, []);

  // 연료직접배출량 모달 열기
  const openFuelDirModal = useCallback((process: Process) => {
    setSelectedProcessForFuelDir(process);
    setShowFuelDirModal(true);
  }, []);

  // 통합 공정 그룹 탐지
  const handleDetectGroups = useCallback(async () => {
    await detectIntegratedProcessGroups();
  }, [detectIntegratedProcessGroups]);

  // 통합 공정 그룹 목록 로드
  const handleLoadGroups = useCallback(async () => {
    await loadIntegratedProcessGroups();
  }, [loadIntegratedProcessGroups]);

  // Edge 연결 처리
  const handleConnect = useCallback(async (params: Connection) => {
    await handleEdgeCreate(params, updateProcessChainsAfterEdge);
  }, [handleEdgeCreate, updateProcessChainsAfterEdge]);

  const nodeTypes: NodeTypes = { custom: ProductNode, process: ProcessNode };

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
          onClick={handleDetectGroups} 
          disabled={isDetectingChains || !selectedInstall}
          className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          🔗 통합 공정 그룹 탐지
        </Button>

      </div>
      
      {/* 통합 공정 그룹 패널 */}
      <IntegratedGroupsPanel
        processChains={processChains}
        integratedProcessGroups={integratedProcessGroups}
        isDetectingChains={isDetectingChains}
        detectionStatus={detectionStatus}
        onDetectGroups={handleDetectGroups}
        onLoadGroups={handleLoadGroups}
        onShowGroupsModal={() => {}} // 통합 그룹 모달은 IntegratedGroupsPanel에서 직접 관리
      />

      {/* ReactFlow 캔버스 */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={handleConnect}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          connectionMode={ConnectionMode.Loose}
          defaultEdgeOptions={{ type: 'custom', markerEnd: { type: MarkerType.ArrowClosed } }}
          deleteKeyCode="Delete"
          className="bg-gray-900"
          fitView
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

      {showMatDirModal && (
        <MatDirManager
          selectedProcess={selectedProcessForMatDir}
          onClose={() => setShowMatDirModal(false)}
        />
      )}

      {showFuelDirModal && (
        <FuelDirManager
          selectedProcess={selectedProcessForFuelDir}
          onClose={() => setShowFuelDirModal(false)}
        />
      )}

      {/* 통합 공정 그룹 모달은 IntegratedGroupsPanel에서 관리 */}
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
