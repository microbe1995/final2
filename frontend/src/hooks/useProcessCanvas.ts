import { useState, useCallback, useEffect } from 'react';
import { useNodesState, useEdgesState, Node, Edge, Connection } from '@xyflow/react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { Install, Product, Process } from './useProcessManager';

export const useProcessCanvas = (selectedInstall: Install | null) => {
  // ReactFlow 상태
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  // 다중 사업장 캔버스 관리
  const [installCanvases, setInstallCanvases] = useState<{[key: number]: {nodes: Node[], edges: Edge[]}}>({});
  
  // activeInstallId를 selectedInstall에서 계산
  const activeInstallId = selectedInstall?.id || null;

  // 캔버스 상태 변경 시 해당 사업장의 캔버스 데이터 업데이트
  useEffect(() => {
    if (activeInstallId) {
      setInstallCanvases(prev => ({
        ...prev,
        [activeInstallId]: { nodes, edges }
      }));
    }
  }, [nodes, edges, activeInstallId]);

  // selectedInstall 변경 시 캔버스 상태 복원
  useEffect(() => {
    if (selectedInstall) {
      const canvasData = installCanvases[selectedInstall.id] || { nodes: [], edges: [] };
      // 상태 업데이트를 안전하게 처리
      setNodes(prev => {
        // 이전 상태와 동일하면 업데이트하지 않음
        if (JSON.stringify(prev) === JSON.stringify(canvasData.nodes)) {
          return prev;
        }
        return canvasData.nodes;
      });
      setEdges(prev => {
        // 이전 상태와 동일하면 업데이트하지 않음
        if (JSON.stringify(prev) === JSON.stringify(canvasData.edges)) {
          return prev;
        }
        return canvasData.edges;
      });
    }
  }, [selectedInstall?.id, installCanvases, setNodes, setEdges]);

  // 사업장 선택 시 캔버스 상태 복원 (이제 useEffect에서 자동 처리)
  const handleInstallSelect = useCallback((install: Install) => {
    // 이 함수는 이제 사용되지 않지만, 호환성을 위해 유지
    // 실제 캔버스 상태 복원은 useEffect에서 자동으로 처리됨
  }, []);

  // 제품 노드 추가
  const addProductNode = useCallback((product: Product, handleProductNodeClick: (product: Product) => void) => {
    const newNode: Node = {
      id: `product-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'custom',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        label: product.product_name,
        description: `제품: ${product.product_name}`,
        variant: 'product',
        productData: product,
        install_id: selectedInstall?.id,
        onClick: () => handleProductNodeClick(product),
      },
    };

    // setNodes를 사용하여 안전하게 노드 추가
    setNodes(prev => [...prev, newNode]);
  }, [setNodes, selectedInstall?.id]);

  // 공정 노드 추가
  const addProcessNode = useCallback((process: Process, products: Product[], openMatDirModal: (process: Process) => void, openFuelDirModal: (process: Process) => void) => {
    // 해당 공정이 사용되는 모든 제품 정보 찾기
    const relatedProducts = products.filter((product: Product) => 
      process.products && process.products.some((p: Product) => p.id === product.id)
    );
    const productNames = relatedProducts.map((product: Product) => product.product_name).join(', ');
    
    // 외부 사업장의 공정인지 확인
    const isExternalProcess = process.products && 
      process.products.some((p: Product) => p.install_id !== selectedInstall?.id);
    
    const newNode: Node = {
      id: `process-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'process',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        label: process.process_name,
        description: `공정: ${process.process_name}`,
        variant: 'process',
        processData: process,
        product_names: productNames || '알 수 없음',
        install_id: selectedInstall?.id,
        current_install_id: selectedInstall?.id,
        is_readonly: isExternalProcess,
        related_products: relatedProducts,
        is_many_to_many: true,
        onMatDirClick: openMatDirModal,
        onFuelDirClick: openFuelDirModal,
      },
    };

    // setNodes를 사용하여 안전하게 노드 추가
    setNodes(prev => [...prev, newNode]);
  }, [setNodes, selectedInstall?.id]);

  // 그룹 노드 추가
  const addGroupNode = useCallback(() => {
    const newNode: Node<any> = {
      id: `group-${Date.now()}-${Math.random().toString(36).slice(2)}`,
      type: 'group',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      style: { width: 200, height: 100 },
      data: { label: '그룹' },
    };

    // setNodes를 사용하여 안전하게 노드 추가
    setNodes(prev => [...prev, newNode]);
  }, [setNodes]);

  // Edge 생성 처리
  const handleEdgeCreate = useCallback(async (params: Connection, updateProcessChainsAfterEdge: () => void) => {
    try {
      // 백엔드에 Edge 생성 요청
      const edgeData = {
        source_id: parseInt(params.source!),
        target_id: parseInt(params.target!),
        edge_kind: 'continue'
      };
      
      const response = await axiosClient.post(apiEndpoints.cbam.edge.create, edgeData);
      
      if (response.status === 201) {
        const newEdge = response.data;
        
        // ReactFlow 상태에 Edge 추가 (setEdges 사용)
        const edgeToAdd = {
          id: `e-${newEdge.id}`,
          source: params.source!,
          target: params.target!,
          type: 'custom',
          data: { edgeData: newEdge }
        };
        
        setEdges(prev => [...prev, edgeToAdd]);
        
        // 콜백 실행
        if (updateProcessChainsAfterEdge) {
          updateProcessChainsAfterEdge();
        }
      }
    } catch (error) {
      console.error('Edge 생성 실패:', error);
    }
  }, [setEdges]);

  return {
    // 상태
    nodes,
    edges,
    installCanvases,
    activeInstallId,

    // 이벤트 핸들러
    onNodesChange,
    onEdgesChange,
    handleEdgeCreate,

    // 액션
    handleInstallSelect,
    addProductNode,
    addProcessNode,
    addGroupNode,
  };
};
