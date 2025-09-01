import { useState, useCallback, useEffect, useRef } from 'react';
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

  // 이전 상태를 추적하여 무한 루프 방지
  const prevInstallIdRef = useRef<number | null>(null);
  const prevNodesRef = useRef<Node[]>([]);
  const prevEdgesRef = useRef<Edge[]>([]);

  // 캔버스 상태 변경 시 해당 사업장의 캔버스 데이터 업데이트
  useEffect(() => {
    if (activeInstallId) {
      setInstallCanvases(prev => ({
        ...prev,
        [activeInstallId]: { nodes, edges }
      }));
    }
  }, [nodes, edges, activeInstallId]);

  // selectedInstall 변경 시 캔버스 상태 복원 (안전한 상태 업데이트)
  useEffect(() => {
    if (selectedInstall && selectedInstall.id !== prevInstallIdRef.current) {
      const canvasData = installCanvases[selectedInstall.id] || { nodes: [], edges: [] };
      
      // 이전 상태와 동일한지 확인하여 불필요한 업데이트 방지
      const nodesChanged = JSON.stringify(prevNodesRef.current) !== JSON.stringify(canvasData.nodes);
      const edgesChanged = JSON.stringify(prevEdgesRef.current) !== JSON.stringify(canvasData.edges);
      
      if (nodesChanged) {
        setNodes(canvasData.nodes);
        prevNodesRef.current = canvasData.nodes;
      }
      
      if (edgesChanged) {
        setEdges(canvasData.edges);
        prevEdgesRef.current = canvasData.edges;
      }
      
      prevInstallIdRef.current = selectedInstall.id;
    }
  }, [selectedInstall?.id, installCanvases, setNodes, setEdges]);

  // 사업장 선택 시 캔버스 상태 복원 (이제 useEffect에서 자동 처리)
  const handleInstallSelect = useCallback((install: Install) => {
    // 이 함수는 이제 사용되지 않지만, 호환성을 위해 유지
    // 실제 캔버스 상태 복원은 useEffect에서 자동으로 처리됨
  }, []);

  // 제품 노드 추가 (안전한 상태 업데이트)
  const addProductNode = useCallback((product: Product, handleProductNodeClick: (product: Product) => void) => {
    // 🔴 수정: 더 작은 ID 생성 (int32 범위 내)
    const nodeId = Math.floor(Math.random() * 1000000) + 1; // 1 ~ 1,000,000
    const actualNodeId = `product-${nodeId}-${Math.random().toString(36).slice(2)}`;
    
    const newNode: Node = {
      id: actualNodeId,
      type: 'product',  // 'product' 타입으로 설정
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        id: product.id,  // 실제 제품 ID 추가
        nodeId: actualNodeId,  // 🔴 추가: 실제 노드 ID를 data에 저장
        label: product.product_name,  // 🔴 수정: label을 올바르게 설정
        description: `제품: ${product.product_name}`,
        variant: 'product',  // 🔴 수정: variant를 'product'로 명시적 설정
        productData: product,  // 🔴 수정: productData를 올바르게 설정
        install_id: selectedInstall?.id,
        onClick: () => handleProductNodeClick(product),
        // 🔴 추가: ProductNode가 기대하는 추가 데이터
        size: 'md',
        showHandles: true,
      },
    };

    console.log('🔍 제품 노드 생성:', newNode); // 🔴 추가: 디버깅 로그

    // setNodes를 사용하여 안전하게 노드 추가
    setNodes(prev => {
      const newNodes = [...prev, newNode];
      prevNodesRef.current = newNodes;
      console.log('🔍 노드 상태 업데이트:', newNodes); // 🔴 추가: 디버깅 로그
      return newNodes;
    });
  }, [setNodes, selectedInstall?.id]);

  // 공정 노드 추가 (안전한 상태 업데이트)
  const addProcessNode = useCallback((process: Process, products: Product[], openMatDirModal: (process: Process) => void, openFuelDirModal: (process: Process) => void) => {
    // 해당 공정이 사용되는 모든 제품 정보 찾기
    const relatedProducts = products.filter((product: Product) => 
      process.products && process.products.some((p: Product) => p.id === product.id)
    );
    const productNames = relatedProducts.map((product: Product) => product.product_name).join(', ');
    
    // 외부 사업장의 공정인지 확인
    const isExternalProcess = process.products && 
      process.products.some((p: Product) => p.install_id !== selectedInstall?.id);
    
    // 🔴 수정: 더 작은 ID 생성 (int32 범위 내)
    const nodeId = Math.floor(Math.random() * 1000000) + 1; // 1 ~ 1,000,000
    const actualNodeId = `process-${nodeId}-${Math.random().toString(36).slice(2)}`;
    
    const newNode: Node = {
      id: actualNodeId,
      type: 'process',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        id: process.id,  // 실제 공정 ID 추가
        nodeId: actualNodeId,  // 🔴 추가: 실제 노드 ID를 data에 저장
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
    setNodes(prev => {
      const newNodes = [...prev, newNode];
      prevNodesRef.current = newNodes;
      return newNodes;
    });
  }, [setNodes, selectedInstall?.id]);

  // 그룹 노드 추가 (안전한 상태 업데이트)
  const addGroupNode = useCallback(() => {
    // 🔴 수정: 더 작은 ID 생성 (int32 범위 내)
    const nodeId = Math.floor(Math.random() * 1000000) + 1; // 1 ~ 1,000,000
    const actualNodeId = `group-${nodeId}-${Math.random().toString(36).slice(2)}`;
    
    const newNode: Node<any> = {
      id: actualNodeId,
      type: 'group',  // 🔴 수정: 'group' 타입으로 설정
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      style: { width: 200, height: 100 },
      data: { 
        nodeId: actualNodeId,  // 🔴 추가: 실제 노드 ID를 data에 저장
        label: '그룹',  // 🔴 수정: label을 올바르게 설정
        description: '그룹 노드',
        variant: 'default',  // 🔴 추가: variant 설정
        size: 'md',  // 🔴 추가: size 설정
        showHandles: true,  // 🔴 추가: showHandles 설정
      },
    };

    console.log('🔍 그룹 노드 생성:', newNode); // 🔴 추가: 디버깅 로그

    // setNodes를 사용하여 안전하게 노드 추가
    setNodes(prev => {
      const newNodes = [...prev, newNode];
      prevNodesRef.current = newNodes;
      console.log('🔍 노드 상태 업데이트:', newNodes); // 🔴 추가: 디버깅 로그
      return newNodes;
    });
  }, [setNodes]);

  // 🔧 4방향 연결을 지원하는 Edge 생성 처리
  const handleEdgeCreate = useCallback(async (params: Connection, updateProcessChainsAfterEdge: () => void) => {
    let tempEdgeId: string | null = null;
    
    try {
      console.log('🔗 Edge 연결 시도:', params);
      
      // 기본 파라미터 검증
      if (!params.source || !params.target) {
        console.log('❌ source 또는 target이 없음:', params);
        return;
      }
      
      // 핸들 ID 검증 (ConnectionMode.Strict에서는 필수)
      if (!params.sourceHandle || !params.targetHandle) {
        console.log('❌ 핸들 ID 누락 - 연결 불가:', params);
        return;
      }
      
      console.log('🔧 4방향 연결 핸들 ID:', {
        sourceHandle: params.sourceHandle,
        targetHandle: params.targetHandle
      });
      
              // 🔧 4방향 연결 임시 Edge 생성
        tempEdgeId = `temp-${Date.now()}`;
        const tempEdge = {
          id: tempEdgeId,
          source: params.source,
          target: params.target,
          sourceHandle: params.sourceHandle,
          targetHandle: params.targetHandle,
          type: 'custom',
          data: { isTemporary: true },
          style: { strokeDasharray: '5,5', stroke: '#6b7280' }
        };
      
      setEdges(prev => [...prev, tempEdge]);
      console.log('🔗 임시 Edge 추가됨:', tempEdgeId);
      
      // 노드 ID에서 숫자 부분만 추출 (예: "product-123-abc" → 123)
      const extractNodeId = (nodeId: string): number => {
        const match = nodeId.match(/(?:product|process|group)-(\d+)/);
        const extractedId = match ? parseInt(match[1]) : 0;
        
        // 🔴 추가: int32 범위 검증
        if (extractedId > 2147483647 || extractedId < -2147483648) {
          console.error('❌ 노드 ID가 int32 범위를 초과:', extractedId);
          return 0;
        }
        
        return extractedId;
      };
      
      // 노드 타입 추출
      const extractNodeType = (nodeId: string): string => {
        if (nodeId.startsWith('product-')) return 'product';
        if (nodeId.startsWith('process-')) return 'process';
        if (nodeId.startsWith('group-')) return 'group';
        return 'unknown';
      };
      
      const sourceId = extractNodeId(params.source);
      const targetId = extractNodeId(params.target);
      const sourceNodeType = extractNodeType(params.source);
      const targetNodeType = extractNodeType(params.target);
      
      console.log('🔍 추출된 정보:', {
        source: params.source,
        target: params.target,
        sourceId,
        targetId,
        sourceNodeType,
        targetNodeType
      });
      
      if (sourceId === 0 || targetId === 0) {
        console.error('유효하지 않은 노드 ID:', { source: params.source, target: params.target });
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        return;
      }
      
      // 백엔드에 Edge 생성 요청
      const edgeData = {
        source_node_type: sourceNodeType,
        source_id: sourceId,
        target_node_type: targetNodeType,
        target_id: targetId,
        edge_kind: 'continue'
      };
      
      console.log('🔗 Edge 생성 요청:', edgeData);
      
      const response = await axiosClient.post(apiEndpoints.cbam.edge.create, edgeData);
      
      if (response.status === 201) {
        const newEdge = response.data;
        console.log('✅ Edge 생성 성공:', newEdge);
        
        // 🔧 임시 Edge를 실제 Edge로 교체
        setEdges(prev => prev.map(edge => 
          edge.id === tempEdgeId 
            ? {
                id: `e-${newEdge.id}`,
                source: params.source,
                target: params.target,
                sourceHandle: params.sourceHandle,
                targetHandle: params.targetHandle,
                type: 'custom',
                data: { edgeData: newEdge, isTemporary: false },
                style: { stroke: '#3b82f6' }
              }
            : edge
        ));
        
        // 콜백 실행
        if (updateProcessChainsAfterEdge) {
          updateProcessChainsAfterEdge();
        }
      }
    } catch (error: any) {
      // 🔴 개선: 더 자세한 에러 로깅
      console.error('❌ Edge 생성 실패:', {
        error: error,
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        params: params
      });
      
      // 🔧 에러 발생 시 임시 Edge 제거
      if (tempEdgeId) {
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
      }
      
      // 🔴 추가: 사용자에게 에러 알림 (Toast 등으로 표시 가능)
      if (error.response?.status === 500) {
        console.error('🔴 서버 내부 오류 - Edge 생성 실패');
      } else if (error.response?.status === 400) {
        console.error('🔴 잘못된 요청 - Edge 데이터 검증 실패');
      } else if (error.code === 'NETWORK_ERROR') {
        console.error('🔴 네트워크 오류 - 서버 연결 실패');
      } else {
        console.error('🔴 알 수 없는 오류:', error);
      }
    }
  }, [setEdges, edges]);

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
