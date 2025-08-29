'use client';

import React, { useState, useCallback, useEffect } from 'react';
import Button from '@/components/atomic/atoms/Button';
import {
  Plus, Trash2, Save, Download, Building
} from 'lucide-react';

import ProductNode from '@/components/atomic/atoms/ProductNode';
import ProcessNode from '@/components/atomic/atoms/ProcessNode';
// import GroupNode from '@/components/atomic/atoms/GroupNode'; // ✅ 제거: 내장 group 사용
import MatDirManager from '@/components/cbam/matdir_manager';
import FuelDirManager from '@/components/cbam/fueldir_manager';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
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
  const [nodes, setNodes, onNodesChange] = useNodesState<any>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<any>([]);
  const { addNodes, addEdges } = useReactFlow();

  // 사업장 관련 상태
  const [installs, setInstalls] = useState<any[]>([]);
  const [selectedInstall, setSelectedInstall] = useState<any>(null);
  const [showInstallModal, setShowInstallModal] = useState(false);
  
  // 다중 사업장 캔버스 관리
  const [installCanvases, setInstallCanvases] = useState<{[key: number]: {nodes: any[], edges: any[]}}>({});
  const [activeInstallId, setActiveInstallId] = useState<number | null>(null);

  // 제품 목록 모달 상태
  const [products, setProducts] = useState<any[]>([]);
  const [showProductModal, setShowProductModal] = useState(false);

  // 공정 목록 모달 상태
  const [processes, setProcesses] = useState<any[]>([]);
  
  // 제품별 공정 선택을 위한 상태
  const [selectedProduct, setSelectedProduct] = useState<any>(null);
  const [showProcessModalForProduct, setShowProcessModalForProduct] = useState(false);
  
  // 복잡한 다대다 관계 처리를 위한 상태
  const [allProcesses, setAllProcesses] = useState<any[]>([]);
  const [processFilterMode, setProcessFilterMode] = useState<'all' | 'product'>('all');
  const [showProcessModal, setShowProcessModal] = useState(false);
  
  // 제품 모달 탭 상태
  const [productModalTab, setProductModalTab] = useState<'process' | 'quantity'>('process');
  
  // 제품 수량 입력 폼 상태
  const [productQuantityForm, setProductQuantityForm] = useState({
    product_amount: 0,
    product_sell: 0,
    product_eusell: 0
  });
  const [isUpdatingProduct, setIsUpdatingProduct] = useState(false);
  
  // 원료직접배출량 모달 상태
  const [showMatDirModal, setShowMatDirModal] = useState(false);
  const [selectedProcessForMatDir, setSelectedProcessForMatDir] = useState<any>(null);
  
  // 연료직접배출량 모달 상태
  const [showFuelDirModal, setShowFuelDirModal] = useState(false);
  const [selectedProcessForFuelDir, setSelectedProcessForFuelDir] = useState<any>(null);
  
  // 통합 공정 그룹 관련 상태
  const [integratedProcessGroups, setIntegratedProcessGroups] = useState<any[]>([]);
  const [showIntegratedGroupsModal, setShowIntegratedGroupsModal] = useState(false);
  const [isDetectingChains, setIsDetectingChains] = useState(false);
  const [detectionStatus, setDetectionStatus] = useState<string>('');
  
  // 크로스 사업장 공정 처리를 위한 상태
  const [crossInstallProcesses, setCrossInstallProcesses] = useState<any[]>([]);
  const [showCrossInstallModal, setShowCrossInstallModal] = useState(false);

  // 사업장 목록 불러오기
  const fetchInstalls = useCallback(async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.install.list);
      setInstalls(response.data);
    } catch (error) {
      console.error('사업장 목록 조회 실패:', error);
      setInstalls([]);
    }
  }, []);

  // 선택된 사업장의 제품 목록 불러오기
  const fetchProductsByInstall = useCallback(async (installId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.product.list);
      // 선택된 사업장의 제품만 필터링
      const filteredProducts = response.data.filter((product: any) => product.install_id === installId);
      setProducts(filteredProducts);
    } catch (error) {
      console.error('제품 목록 조회 실패:', error);
      setProducts([]);
    }
  }, []);

  // 선택된 사업장의 공정 목록 불러오기
  const fetchProcessesByInstall = useCallback(async (installId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      // 선택된 사업장의 제품에 속한 모든 공정을 가져옴 (다대다 관계)
      const installProducts = products.filter((product: any) => product.install_id === installId);
      const productIds = installProducts.map((product: any) => product.id);
      const installProcesses = response.data.filter((process: any) => 
        process.products && process.products.some((p: any) => productIds.includes(p.id))
      );
      setProcesses(installProcesses);
      console.log('🔍 사업장의 공정들:', installProcesses);
    } catch (error) {
      console.error('공정 목록 조회 실패:', error);
      setProcesses([]);
    }
  }, [products]);

  // 선택된 사업장의 모든 공정 목록 불러오기 (다대다 관계 처리용)
  const fetchAllProcessesByInstall = useCallback(async (installId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      // 선택된 사업장의 제품에 속한 모든 공정을 가져옴 (다대다 관계)
      const installProducts = products.filter((product: any) => product.install_id === installId);
      const productIds = installProducts.map((product: any) => product.id);
      const allProcesses = response.data.filter((process: any) => 
        process.products && process.products.some((p: any) => productIds.includes(p.id))
      );
      setAllProcesses(allProcesses);
      console.log('🔍 사업장의 모든 공정들:', allProcesses);
    } catch (error) {
      console.error('전체 공정 목록 조회 실패:', error);
      setAllProcesses([]);
    }
  }, [products]);

  // 모든 사업장의 공정 목록 불러오기 (크로스 사업장 처리용)
  const fetchAllCrossInstallProcesses = useCallback(async () => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      // 현재 사업장의 제품과 관련된 모든 공정을 가져옴 (다른 사업장 포함, 다대다 관계)
      const currentInstallProducts = products.filter((product: any) => product.install_id === selectedInstall?.id);
      const productIds = currentInstallProducts.map((product: any) => product.id);
      const allCrossProcesses = response.data.filter((process: any) => 
        process.products && process.products.some((p: any) => productIds.includes(p.id))
      );
      setCrossInstallProcesses(allCrossProcesses);
      console.log('🔍 크로스 사업장 공정들:', allCrossProcesses);
    } catch (error) {
      console.error('크로스 사업장 공정 목록 조회 실패:', error);
      setCrossInstallProcesses([]);
    }
  }, [products, selectedInstall]);

  // 선택된 제품의 공정 목록 불러오기 (다대다 관계)
  const fetchProcessesByProduct = useCallback(async (productId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.process.list);
      // 해당 제품과 연결된 모든 공정을 가져옴 (다대다 관계)
      const productProcesses = response.data.filter((process: any) => 
        process.products && process.products.some((p: any) => p.id === productId)
      );
      setProcesses(productProcesses);
      console.log('🔍 제품의 공정들:', productProcesses);
    } catch (error) {
      console.error('제품별 공정 목록 조회 실패:', error);
      setProcesses([]);
    }
  }, []);

  // 사업장 선택 시 제품과 공정 목록 업데이트
  useEffect(() => {
    if (selectedInstall) {
      fetchProductsByInstall(selectedInstall.id);
    }
  }, [selectedInstall, fetchProductsByInstall]);

  useEffect(() => {
    if (selectedInstall && products.length > 0) {
      // products가 업데이트된 후에 공정 목록을 가져옴
      const timer = setTimeout(() => {
        fetchProcessesByInstall(selectedInstall.id);
        fetchAllProcessesByInstall(selectedInstall.id); // 모든 공정도 함께 불러오기
        fetchAllCrossInstallProcesses(); // 크로스 사업장 공정도 불러오기
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [selectedInstall, products, fetchProcessesByInstall, fetchAllProcessesByInstall, fetchAllCrossInstallProcesses]);

  // 컴포넌트 마운트 시 사업장 목록 불러오기
  useEffect(() => {
    fetchInstalls();
  }, [fetchInstalls]);



  // 캔버스 상태 변경 시 해당 사업장의 캔버스 데이터 업데이트
  useEffect(() => {
    if (activeInstallId) {
      setInstallCanvases(prev => ({
        ...prev,
        [activeInstallId]: { nodes, edges }
      }));
    }
  }, [nodes, edges, activeInstallId]);

  // 사업장 선택 모달 열기
  const openInstallModal = useCallback(() => {
    setShowInstallModal(true);
  }, []);

  // 사업장 선택 - 캔버스 상태 관리 개선
  const handleInstallSelect = useCallback((install: any) => {
    console.log('🏭 사업장 선택:', install);
    
    // 현재 활성 사업장의 캔버스 상태 저장
    if (activeInstallId) {
      setInstallCanvases(prev => ({
        ...prev,
        [activeInstallId]: { nodes, edges }
      }));
    }
    
    // 새로운 사업장 설정
    setSelectedInstall(install);
    setActiveInstallId(install.id);
    setShowInstallModal(false);
    
    // 해당 사업장의 캔버스 데이터 가져오기
    const canvasData = installCanvases[install.id] || { nodes: [], edges: [] };
    console.log('📊 캔버스 데이터 복원:', canvasData);
    
    // React Flow 상태 업데이트
    setNodes(canvasData.nodes);
    setEdges(canvasData.edges);
  }, [activeInstallId, nodes, edges, installCanvases, setNodes, setEdges]);

  // 제품 노드 추가(모달 열기)
  const addProductNode = useCallback(async () => {
    if (!selectedInstall) {
      alert('먼저 사업장을 선택해주세요.');
      return;
    }
    setShowProductModal(true);
  }, [selectedInstall]);

  // 제품 노드 클릭 시 해당 제품의 공정 선택 모달 열기
  const handleProductNodeClick = useCallback((productData: any) => {
    setSelectedProduct(productData);
    fetchProcessesByProduct(productData.id);
    setShowProcessModalForProduct(true);
  }, [fetchProcessesByProduct]);

  // 제품 노드 클릭 시 복잡한 다대다 관계 공정 선택 모달 열기
  const handleProductNodeClickComplex = useCallback((productData: any) => {
    setSelectedProduct(productData);
    setProcessFilterMode('product'); // 기본적으로 제품별 필터링
    setProductModalTab('process'); // 기본 탭을 공정 선택으로 설정
    setProductQuantityForm({
      product_amount: productData.product_amount || 0,
      product_sell: productData.product_sell || 0,
      product_eusell: productData.product_eusell || 0
    });
    setShowProcessModal(true);
  }, []);



  // 제품별 공정 선택 모달 열기
  const openProcessModalForProduct = useCallback((product: any) => {
    setSelectedProduct(product);
    fetchProcessesByProduct(product.id);
    setShowProcessModalForProduct(true);
  }, [fetchProcessesByProduct]);

  // 제품 선택 → 노드 추가
  const handleProductSelect = useCallback((product: any) => {
    const newNode: Node<any> = {
      id: `product-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'custom',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        label: product.product_name,
        description: `제품: ${product.product_name}`,
        variant: 'product',
        productData: product,
        install_id: selectedInstall?.id, // 사업장 ID 추가
        onClick: () => handleProductNodeClickComplex(product), // 복잡한 다대다 관계 처리용 클릭 핸들러
      },
    };

    addNodes(newNode);
    setShowProductModal(false);
  }, [addNodes, selectedInstall, handleProductNodeClickComplex]);

  // 통합 공정 그룹 자동 탐지 및 계산
  const detectIntegratedProcessGroups = useCallback(async () => {
    try {
      setIsDetectingChains(true);
      setDetectionStatus('🔍 연결된 공정들을 탐지 중...');
      
      const response = await axiosClient.post('/api/v1/boundary/sourcestream/auto-detect-and-calculate', {
        max_chain_length: 10,
        include_inactive: false,
        recalculate_existing: false
      });
      
      if (response.status === 200) {
        const result = response.data;
        setDetectionStatus(`✅ 탐지 완료: ${result.detected_chains}개 그룹, 총 배출량: ${result.total_integrated_emission}`);
        
        // 탐지된 그룹 목록 가져오기
        const groupsResponse = await axiosClient.get('/api/v1/boundary/sourcestream/chain');
        if (groupsResponse.status === 200) {
          setIntegratedProcessGroups(groupsResponse.data);
        }
      }
    } catch (error) {
      console.error('통합 공정 그룹 탐지 오류:', error);
      setDetectionStatus('❌ 탐지 실패: ' + (error as any).message);
    } finally {
      setIsDetectingChains(false);
    }
  }, []);

  // 통합 공정 그룹 목록 조회
  const loadIntegratedProcessGroups = useCallback(async () => {
    try {
      const response = await axiosClient.get('/api/v1/boundary/sourcestream/chain');
      if (response.status === 200) {
        setIntegratedProcessGroups(response.data);
      }
    } catch (error) {
      console.error('통합 공정 그룹 조회 오류:', error);
    }
  }, []);

  // 제품 수량 업데이트
  const handleProductQuantityUpdate = useCallback(async () => {
    if (!selectedProduct) return;
    
    setIsUpdatingProduct(true);
    try {
      const response = await axiosClient.put(apiEndpoints.cbam.product.update(selectedProduct.id), productQuantityForm);
      console.log('✅ 제품 수량 업데이트 성공:', response.data);
      
      // 성공 메시지 표시 (간단한 알림)
      alert('제품 수량이 성공적으로 업데이트되었습니다!');
      
      // 선택된 제품 정보 업데이트
      setSelectedProduct({
        ...selectedProduct,
        ...productQuantityForm
      });
      
    } catch (error: any) {
      console.error('❌ 제품 수량 업데이트 실패:', error);
      alert(`제품 수량 업데이트에 실패했습니다: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsUpdatingProduct(false);
    }
  }, [selectedProduct, productQuantityForm]);

  // 원료직접배출량 모달 열기
  const openMatDirModal = useCallback((process: any) => {
    setSelectedProcessForMatDir(process);
    setShowMatDirModal(true);
  }, []);

  // 연료직접배출량 모달 열기
  const openFuelDirModal = useCallback((process: any) => {
    setSelectedProcessForFuelDir(process);
    setShowFuelDirModal(true);
  }, []);

  // 공정 선택 → 노드 추가
  const handleProcessSelect = useCallback((process: any) => {
    // 해당 공정이 사용되는 모든 제품 정보 찾기 (다대다 관계)
    const relatedProducts = products.filter((product: any) => 
      process.products && process.products.some((p: any) => p.id === product.id)
    );
    const productNames = relatedProducts.map((product: any) => product.product_name).join(', ');
    
    // 외부 사업장의 공정인지 확인 (공정이 속한 사업장 중 하나라도 현재 사업장이 아니면 외부)
    const isExternalProcess = process.products && 
      process.products.some((p: any) => p.install_id !== selectedInstall?.id);
    
    const newNode: Node<any> = {
      id: `process-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'process',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        label: process.process_name,
        description: `공정: ${process.process_name}`,
        variant: 'process',
        processData: process,
        product_names: productNames || '알 수 없음', // 사용되는 모든 제품명
        install_id: selectedInstall?.id, // 현재 캔버스 사업장 ID
        current_install_id: selectedInstall?.id, // 현재 캔버스 사업장 ID
        is_readonly: isExternalProcess, // 외부 사업장 공정이면 읽기 전용
        related_products: relatedProducts, // 관련된 모든 제품 정보
        is_many_to_many: true, // 다대다 관계 표시
        onMatDirClick: openMatDirModal, // 원료직접배출량 모달 열기 함수
        onFuelDirClick: openFuelDirModal, // 연료직접배출량 모달 열기 함수
      },
    };

    addNodes(newNode);
    setShowProcessModal(false);
    setShowProcessModalForProduct(false); // 제품별 공정 모달도 닫기
  }, [addNodes, products, selectedInstall, openMatDirModal, openFuelDirModal]);

  // 그룹 노드 추가
  const addGroupNode = useCallback(() => {
    const newNode: Node<any> = {
      id: `group-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'group',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      style: { width: 200, height: 100 },
      data: { label: '그룹' },
    };

    addNodes(newNode);
  }, [addNodes]);

  // 컴포넌트 마운트 시 통합 공정 그룹 목록 불러오기
  useEffect(() => {
    loadIntegratedProcessGroups();
  }, [loadIntegratedProcessGroups]);

  const nodeTypes: NodeTypes = { custom: ProductNode, process: ProcessNode };

  return (
    <div className="w-full h-full flex flex-col">
      {/* 헤더 */}
      <div className="bg-gray-900 text-white p-4">
        <h1 className="text-2xl font-bold">CBAM 산정경계설정</h1>
        <p className="text-gray-300">CBAM 배출량 산정을 위한 경계를 설정하고 노드를 생성합니다.</p>
      </div>

      {/* 사업장 선택 카드 */}
      <div className="bg-gray-800 p-4">
        <div className="flex items-center gap-4">
          {/* 사업장 추가 카드 */}
          <div 
            className="w-48 h-24 bg-gray-700 border-2 border-dashed border-gray-500 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:border-blue-400 hover:bg-gray-600 transition-colors"
            onClick={openInstallModal}
          >
            <div className="text-4xl text-gray-400 mb-1">+</div>
            <div className="text-sm text-gray-300">사업장 추가</div>
          </div>
          
          {/* 선택된 사업장 카드들 */}
          {Object.keys(installCanvases).map((installId) => {
            const install = installs.find(i => i.id === parseInt(installId));
            if (!install) return null;
            
            const isActive = activeInstallId === parseInt(installId);
            const canvasData = installCanvases[parseInt(installId)];
            const nodeCount = canvasData?.nodes?.length || 0;
            
            return (
              <div
                key={installId}
                className={`w-48 h-24 rounded-lg flex flex-col justify-center p-3 cursor-pointer transition-all ${
                  isActive 
                    ? 'bg-blue-600 border-2 border-blue-400 shadow-lg' 
                    : 'bg-gray-700 border-2 border-gray-600 hover:border-gray-500'
                }`}
                onClick={() => handleInstallSelect(install)}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="font-semibold text-white text-sm">{install.install_name}</div>
                  <div className="text-xs text-gray-300">{nodeCount}개 노드</div>
                </div>
                <div className="text-xs text-gray-300">
                  {install.reporting_year && `${install.reporting_year}년`}
                </div>
                {isActive && (
                  <div className="text-xs text-blue-200 mt-1">활성</div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 버튼 */}
      <div className="bg-gray-800 p-4 flex gap-2">
        <Button onClick={addProductNode} disabled={!selectedInstall} className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus className="h-4 w-4" /> 제품 노드
        </Button>
        <Button onClick={addGroupNode} className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center gap-2">
          <Plus className="h-4 w-4" /> 그룹 노드
        </Button>
        <Button 
          onClick={detectIntegratedProcessGroups} 
          disabled={isDetectingChains || !selectedInstall}
          className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          🔗 통합 공정 그룹 탐지
        </Button>
        <Button 
          onClick={() => setShowIntegratedGroupsModal(true)} 
          className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg flex items-center gap-2"
        >
          📊 통합 그룹 목록
        </Button>
      </div>
      
      {/* 탐지 상태 표시 */}
      {detectionStatus && (
        <div className="bg-gray-800 px-4 py-2 border-l-4 border-blue-500">
          <div className="text-sm text-blue-300">{detectionStatus}</div>
        </div>
      )}

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
          className="bg-gray-900" // ✅ 다크 캔버스
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

      {/* 사업장 선택 모달 */}
      {showInstallModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full mx-4 border border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">사업장 선택</h3>
              <button onClick={() => setShowInstallModal(false)} className="text-gray-400 hover:text-gray-200">✕</button>
            </div>
            <div className="space-y-2">
              {installs.length > 0 ? (
                installs.map((install) => (
                  <div
                    key={install.id}
                    className="p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700 hover:border-blue-400 transition-colors"
                    onClick={() => handleInstallSelect(install)}
                  >
                    <div className="font-medium text-white">{install.install_name}</div>
                    <div className="text-sm text-gray-300">ID: {install.id}</div>
                    {install.reporting_year && (
                      <div className="text-sm text-gray-300">보고기간: {install.reporting_year}년</div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-400">
                  등록된 사업장이 없습니다.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 제품 선택 모달 */}
      {showProductModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full mx-4 border border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">제품 선택</h3>
              <button onClick={() => setShowProductModal(false)} className="text-gray-400 hover:text-gray-200">✕</button>
            </div>
            <div className="space-y-2">
              {products.length > 0 ? (
                products.map((product) => (
                  <div
                    key={product.id}
                    className="p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700 hover:border-blue-400 transition-colors"
                    onClick={() => handleProductSelect(product)}
                  >
                    <div className="font-medium text-white">{product.product_name}</div>
                    <div className="text-sm text-gray-300">카테고리: {product.product_category}</div>
                    <div className="text-sm text-gray-300">수량: {product.product_amount}</div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-400">
                  선택된 사업장에 등록된 제품이 없습니다.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 제품별 공정 선택 모달 */}
      {showProcessModalForProduct && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full mx-4 border border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">
                공정 선택 - {selectedProduct?.product_name}
              </h3>
              <button onClick={() => setShowProcessModalForProduct(false)} className="text-gray-400 hover:text-gray-200">✕</button>
            </div>
            <div className="space-y-2">
              {processes.length > 0 ? (
                processes.map((process) => (
                  <div
                    key={process.id}
                    className="p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700 hover:border-purple-400 transition-colors"
                    onClick={() => handleProcessSelect(process)}
                  >
                    <div className="font-medium text-white">{process.process_name}</div>
                    <div className="text-sm text-gray-300">시작일: {process.start_period || 'N/A'}</div>
                    <div className="text-sm text-gray-300">종료일: {process.end_period || 'N/A'}</div>
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-400">
                  {selectedProduct?.product_name}에 등록된 공정이 없습니다.
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* 제품 관리 모달 (탭 포함) */}
      {showProcessModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-4xl w-full mx-4 border border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">
                {selectedProduct?.product_name} 관리
              </h3>
              <button onClick={() => setShowProcessModal(false)} className="text-gray-400 hover:text-gray-200">✕</button>
            </div>
            
            {/* 탭 네비게이션 */}
            <div className="mb-6 flex gap-2 border-b border-gray-700">
              <button
                onClick={() => setProductModalTab('process')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  productModalTab === 'process'
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                🔄 공정 선택
              </button>
              <button
                onClick={() => setProductModalTab('quantity')}
                className={`px-4 py-2 text-sm font-medium transition-colors ${
                  productModalTab === 'quantity'
                    ? 'text-blue-400 border-b-2 border-blue-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                📊 수량/판매량
              </button>
            </div>
            
            {/* 탭 컨텐츠 */}
            {productModalTab === 'process' && (
              <div>
                {/* 필터링 옵션 */}
                <div className="mb-4 flex gap-2">
                  <button
                    onClick={() => setProcessFilterMode('all')}
                    className={`px-3 py-1 rounded text-sm transition-colors ${
                      processFilterMode === 'all'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    전체 공정
                  </button>
                  {selectedProduct && (
                    <button
                      onClick={() => setProcessFilterMode('product')}
                      className={`px-3 py-1 rounded text-sm transition-colors ${
                        processFilterMode === 'product'
                          ? 'bg-purple-600 text-white'
                          : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                      }`}
                    >
                      {selectedProduct.product_name} 공정만
                    </button>
                  )}
                </div>
                
                <div className="space-y-2 max-h-96 overflow-y-auto">
                  {(() => {
                    const displayProcesses = processFilterMode === 'product' 
                      ? allProcesses.filter((process: any) => 
                          process.products && process.products.some((p: any) => p.id === selectedProduct?.id)
                        )
                      : allProcesses;
                    
                    return displayProcesses.length > 0 ? (
                      displayProcesses.map((process: any) => {
                        // 해당 공정이 사용되는 모든 제품 정보 찾기 (다대다 관계)
                        const relatedProducts = products.filter((product: any) => 
                          process.products && process.products.some((p: any) => p.id === product.id)
                        );
                        const productNames = relatedProducts.map((product: any) => product.product_name).join(', ');
                        
                        // 외부 사업장의 공정인지 확인 (공정이 속한 사업장 중 하나라도 현재 사업장이 아니면 외부)
                        const isExternalProcess = process.products && 
                          process.products.some((p: any) => p.install_id !== selectedInstall?.id);
                        const processInstall = installs.find((install: any) => 
                          process.products && process.products.some((p: any) => p.install_id === install.id)
                        );
                        
                        return (
                          <div
                            key={process.id}
                            className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                              isExternalProcess 
                                ? 'border-gray-500 bg-gray-700 hover:bg-gray-600' 
                                : 'border-gray-600 hover:bg-gray-700 hover:border-purple-400'
                            }`}
                            onClick={() => handleProcessSelect(process)}
                          >
                            <div className="font-medium text-white">{process.process_name}</div>
                            <div className="text-sm text-gray-300">사용 제품: {productNames || 'N/A'}</div>
                            {isExternalProcess && (
                              <div className="text-sm text-gray-400">
                                외부 사업장: {processInstall?.install_name || '알 수 없음'} (읽기 전용)
                              </div>
                            )}
                            <div className="text-sm text-gray-300">시작일: {process.start_period || 'N/A'}</div>
                            <div className="text-sm text-gray-300">종료일: {process.end_period || 'N/A'}</div>
                          </div>
                        );
                      })
                    ) : (
                      <div className="text-center py-4 text-gray-400">
                        {processFilterMode === 'product' 
                          ? `${selectedProduct?.product_name}에 등록된 공정이 없습니다.`
                          : '등록된 공정이 없습니다.'
                        }
                      </div>
                    );
                  })()}
                </div>
              </div>
            )}
            
            {productModalTab === 'quantity' && (
              <div>
                {/* 제품 정보 표시 */}
                <div className="mb-6 p-4 bg-gray-700 rounded-lg">
                  <h4 className="text-white font-medium mb-2">제품 정보</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-300">제품명:</span>
                      <span className="text-white ml-2">{selectedProduct?.product_name}</span>
                    </div>
                    {selectedProduct?.cncode_total && (
                      <div>
                        <span className="text-gray-300">CN 코드:</span>
                        <span className="text-blue-300 ml-2">{selectedProduct.cncode_total}</span>
                      </div>
                    )}
                    {selectedProduct?.goods_name && (
                      <div>
                        <span className="text-gray-300">품목명:</span>
                        <span className="text-white ml-2">{selectedProduct.goods_name}</span>
                      </div>
                    )}
                    {selectedProduct?.aggrgoods_name && (
                      <div>
                        <span className="text-gray-300">품목군명:</span>
                        <span className="text-white ml-2">{selectedProduct.aggrgoods_name}</span>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* 수량/판매량 입력 폼 */}
                <div className="space-y-4">
                  <h4 className="text-white font-medium">수량 및 판매량 입력</h4>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        제품 수량 (ton) *
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={productQuantityForm.product_amount}
                        onChange={(e) => setProductQuantityForm(prev => ({
                          ...prev,
                          product_amount: parseFloat(e.target.value) || 0
                        }))}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        제품 판매량 (ton) *
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={productQuantityForm.product_sell}
                        onChange={(e) => setProductQuantityForm(prev => ({
                          ...prev,
                          product_sell: parseFloat(e.target.value) || 0
                        }))}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        제품 EU 판매량 (ton) *
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        min="0"
                        value={productQuantityForm.product_eusell}
                        onChange={(e) => setProductQuantityForm(prev => ({
                          ...prev,
                          product_eusell: parseFloat(e.target.value) || 0
                        }))}
                        className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-md text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                        required
                      />
                    </div>
                  </div>
                  
                  {/* 현재 입력된 값 표시 */}
                  <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
                      <div className="text-sm text-blue-300 mb-1">제품 수량</div>
                      <div className="text-2xl font-bold text-white">{productQuantityForm.product_amount.toLocaleString()} ton</div>
                    </div>
                    <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                      <div className="text-sm text-green-300 mb-1">제품 판매량</div>
                      <div className="text-2xl font-bold text-white">{productQuantityForm.product_sell.toLocaleString()} ton</div>
                    </div>
                    <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                      <div className="text-sm text-purple-300 mb-1">EU 판매량</div>
                      <div className="text-2xl font-bold text-white">{productQuantityForm.product_eusell.toLocaleString()} ton</div>
                    </div>
                  </div>
                  
                  {/* 저장 버튼 */}
                  <div className="flex justify-end pt-4">
                    <button
                      onClick={handleProductQuantityUpdate}
                      disabled={isUpdatingProduct}
                      className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200 disabled:opacity-50"
                    >
                      {isUpdatingProduct ? '저장 중...' : '📊 수량/판매량 저장'}
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* 원료직접배출량 모달 */}
      {showMatDirModal && (
        <MatDirManager
          selectedProcess={selectedProcessForMatDir}
          onClose={() => setShowMatDirModal(false)}
        />
      )}

      {/* 연료직접배출량 모달 */}
      {showFuelDirModal && (
        <FuelDirManager
          selectedProcess={selectedProcessForFuelDir}
          onClose={() => setShowFuelDirModal(false)}
        />
      )}

      {/* 통합 공정 그룹 모달 */}
      {showIntegratedGroupsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-white">📊 통합 공정 그룹 목록</h2>
              <button
                onClick={() => setShowIntegratedGroupsModal(false)}
                className="text-gray-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>

            <div className="mb-4 flex gap-2">
              <button
                onClick={loadIntegratedProcessGroups}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
              >
                🔄 목록 새로고침
              </button>
              <button
                onClick={detectIntegratedProcessGroups}
                disabled={isDetectingChains}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-lg"
              >
                {isDetectingChains ? '🔍 탐지 중...' : '🔗 새로 탐지'}
              </button>
            </div>

            {integratedProcessGroups.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <div className="text-4xl mb-4">🔍</div>
                <div className="text-lg mb-2">통합 공정 그룹이 없습니다</div>
                <div className="text-sm">&ldquo;🔗 새로 탐지&rdquo; 버튼을 클릭하여 연결된 공정들을 찾아보세요</div>
              </div>
            ) : (
              <div className="grid gap-4">
                {integratedProcessGroups.map((group: any) => (
                  <div key={group.id} className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                    <div className="flex justify-between items-start mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-white mb-1">
                          🔗 {group.chain_name}
                        </h3>
                        <div className="text-sm text-gray-300">
                          그룹 ID: {group.id} | 공정 수: {group.chain_length}개
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-sm text-gray-400">상태</div>
                        <div className={`text-sm font-medium ${group.is_active ? 'text-green-400' : 'text-red-400'}`}>
                          {group.is_active ? '활성' : '비활성'}
                        </div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-gray-400 mb-1">시작 공정 ID</div>
                        <div className="text-white font-medium">{group.start_process_id}</div>
                      </div>
                      <div>
                        <div className="text-gray-400 mb-1">종료 공정 ID</div>
                        <div className="text-white font-medium">{group.end_process_id}</div>
                      </div>
                    </div>
                    
                    <div className="mt-3 text-xs text-gray-400">
                      생성일: {new Date(group.created_at).toLocaleString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
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
