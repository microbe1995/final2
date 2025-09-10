import { useState, useCallback, useEffect, useRef } from 'react';
import { useNodesState, useEdgesState, Node, Edge, Connection, EdgeChange } from '@xyflow/react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { Install, Product, Process } from './useProcessManager';
import { useEmissionManager } from './useEmissionManager';
import { useEdgeManager } from './useEdgeManager';
import { useNodeManager } from './useNodeManager';

/**
 * 프로세스 캔버스 메인 훅 (리팩토링됨)
 * 단일 책임: 각 전용 훅들을 조합하여 캔버스 상태 관리만 담당
 */
export const useProcessCanvas = (selectedInstall: Install | null) => {
  // ReactFlow 상태
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, baseOnEdgesChange] = useEdgesState<Edge>([]);

  // 다중 사업장 캔버스 관리
  const [installCanvases, setInstallCanvases] = useState<{[key: number]: {nodes: Node[], edges: Edge[]}}>({});
  
  // 서버 복원 관련
  const fetchingRef = useRef<boolean>(false);
  const ENABLE_SERVER_AUTORESTORE = false;
  
  // activeInstallId를 selectedInstall에서 계산
  const activeInstallId = selectedInstall?.id || null;

  // 이전 상태를 추적하여 무한 루프 방지
  const prevInstallIdRef = useRef<number | null>(null);
  const prevNodesRef = useRef<Node[]>([]);
  const prevEdgesRef = useRef<Edge[]>([]);

  // 전용 훅들 사용
  const emissionManager = useEmissionManager();
  const edgeManager = useEdgeManager();
  const nodeManager = useNodeManager();

  // 로컬스토리지 관리
  const writeSnapshot = useCallback((installId: number | null | undefined, nodesToSave: Node[], edgesToSave: Edge[]) => {
    if (!installId) return;
    try {
      const key = `cbam:layout:${installId}`;
      const payload = { nodes: nodesToSave, edges: edgesToSave };
      const prev = localStorage.getItem(key);
      const prevStr = prev || '';
      const nextStr = JSON.stringify(payload);
      if (prevStr !== nextStr) {
        localStorage.setItem(key, nextStr);
      }
    } catch {}
  }, []);

  // 캔버스 상태 변경 시 해당 사업장의 캔버스 데이터 업데이트
  useEffect(() => {
    if (activeInstallId) {
      setInstallCanvases(prev => ({
        ...prev,
        [activeInstallId]: { nodes, edges }
      }));
    }
  }, [nodes, edges, activeInstallId]);

  // 최신 nodes/edges 스냅샷을 ref에 유지
  useEffect(() => {
    prevNodesRef.current = nodes;
  }, [nodes]);
  
  useEffect(() => {
    prevEdgesRef.current = edges;
  }, [edges]);

  // 노드/엣지 변경 시 레이아웃을 로컬스토리지에 보조 저장(디바운스)
  const saveTimerRef = useRef<number | null>(null);
  useEffect(() => {
    if (!activeInstallId) return;
    try {
      if (saveTimerRef.current) {
        window.clearTimeout(saveTimerRef.current);
      }
      saveTimerRef.current = window.setTimeout(() => {
        writeSnapshot(activeInstallId, nodes, edges);
      }, 300);
    } catch {}
  }, [nodes, edges, activeInstallId, writeSnapshot]);

  // 페이지 이탈 전에 마지막 스냅샷 저장
  useEffect(() => {
    const handler = () => {
      if (!activeInstallId) return;
      writeSnapshot(activeInstallId, prevNodesRef.current, prevEdgesRef.current);
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [activeInstallId, writeSnapshot]);

  // selectedInstall 변경 시 캔버스 상태 복원
  useEffect(() => {
    if (selectedInstall && selectedInstall.id !== prevInstallIdRef.current) {
      const canvasData = installCanvases[selectedInstall.id] || { nodes: [], edges: [] };
      
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

      // 로컬 레이아웃 보조 복원
      try {
        const key = `cbam:layout:${selectedInstall.id}`;
        const raw = localStorage.getItem(key);
        if (raw && canvasData.nodes.length === 0 && canvasData.edges.length === 0) {
          const parsed = JSON.parse(raw);
          if (parsed?.nodes && parsed?.edges) {
            // 콜백 재주입 로직 (기존과 동일)
            const rehydratedNodes: Node[] = (parsed.nodes as Node[]).map((n: any) => {
              const data = { ...(n.data || {}) } as any;
              if (n.type === 'product') {
                const productId = data?.id;
                data.onClick = undefined;
                data.onDoubleClick = () => {
                  try {
                    window.dispatchEvent(new CustomEvent('cbam:node:product:open' as any, { detail: { productId, productData: data?.productData || null } }));
                  } catch {}
                };
                return { ...n, data } as Node;
              }
              if (n.type === 'process') {
                const processData = data?.processData || { id: data?.id, process_name: data?.label, start_period: data?.start_period, end_period: data?.end_period, product_names: data?.product_names };
                const ownerInstallId = typeof data.install_id === 'number' ? data.install_id : (processData as any)?.install_id;
                const currentInstallId = selectedInstall?.id;
                (data as any).current_install_id = currentInstallId;
                (data as any).is_readonly = (typeof ownerInstallId === 'number' && typeof currentInstallId === 'number')
                  ? ownerInstallId !== currentInstallId
                  : false;
                (processData as any).install_id = ownerInstallId;
                (processData as any).current_install_id = currentInstallId;
                (processData as any).is_readonly = (data as any).is_readonly;

                data.onClick = () => {
                  try {
                    window.dispatchEvent(new CustomEvent('cbam:node:process:input' as any, { detail: { processData } }));
                  } catch {}
                };
                data.onMatDirClick = (_pd?: any) => {
                  try {
                    window.dispatchEvent(new CustomEvent('cbam:node:process:input' as any, { detail: { processData } }));
                  } catch {}
                };
                return { ...n, data } as Node;
              }
              return n as Node;
            });
            setNodes(rehydratedNodes);
            setEdges(parsed.edges);
            prevNodesRef.current = rehydratedNodes;
            prevEdgesRef.current = parsed.edges;
            setInstallCanvases(prev => ({ ...prev, [selectedInstall.id]: { nodes: parsed.nodes, edges: parsed.edges } }));
            return;
          }
        }
      } catch {}

      // 서버에서 노드/엣지 복원(옵션)
      if (ENABLE_SERVER_AUTORESTORE && (!canvasData.nodes.length && !canvasData.edges.length) && !fetchingRef.current) {
        fetchingRef.current = true;
        (async () => {
          try {
            const [productsResp, processesResp, edgesResp] = await Promise.all([
              axiosClient.get(`${apiEndpoints.cbam.product.list}?install_id=${selectedInstall.id}`),
              axiosClient.get(apiEndpoints.cbam.process.list),
              axiosClient.get(apiEndpoints.cbam.edge.list)
            ]);
            const products: any[] = (productsResp?.data || []).filter((p: any) => p.install_id === selectedInstall.id);
            const processes: any[] = (processesResp?.data || []).filter((pr: any) => (pr.products || []).some((p: any) => products.find(pp => pp.id === p.id)));
            const edgesAll: any[] = edgesResp?.data || [];

            // 그리드 배치
            const baseX = 200; const baseY = 300; const gapX = 420; const gapY = 180;
            const productNodes: Node[] = products.map((p, idx) => ({
              id: `product-${p.id}-${idx}`,
              type: 'product',
              position: { x: baseX, y: baseY + idx * gapY },
              data: {
                id: p.id,
                nodeId: `product-${p.id}-${idx}`,
                label: p.product_name,
                description: `제품: ${p.product_name}`,
                variant: 'product',
                productData: p,
                product_amount: p.product_amount,
                product_sell: p.product_sell,
                product_eusell: p.product_eusell,
                attr_em: p.attr_em || 0,
                install_id: selectedInstall.id,
              }
            }));
            const processNodes: Node[] = processes.map((pr, idx) => ({
              id: `process-${pr.id}-${idx}`,
              type: 'process',
              position: { x: baseX + gapX, y: baseY + idx * gapY },
              data: {
                id: pr.id,
                nodeId: `process-${pr.id}-${idx}`,
                label: pr.process_name,
                description: `공정: ${pr.process_name}`,
                variant: 'default',
                processData: pr,
              }
            }));

            // 엣지 복원
            const nodeIdBy = (type: 'product'|'process', id: number) => {
              const list = type === 'product' ? productNodes : processNodes;
              const found = list.find(n => (n.data as any)?.id === id);
              return found?.id;
            };
            const edgesRestored: Edge[] = edgesAll
              .filter((e: any) => ['continue','produce','consume'].includes(e.edge_kind))
              .map((e: any, i: number) => {
                const sType = e.source_node_type as 'process'|'product';
                const tType = e.target_node_type as 'process'|'product';
                const sid = nodeIdBy(sType, e.source_id);
                const tid = nodeIdBy(tType, e.target_id);
                if (!sid || !tid) return null as any;
                return {
                  id: `edge-${e.id}-${i}`,
                  source: sid,
                  target: tid,
                  type: 'custom',
                  data: { edgeData: e },
                } as Edge;
              })
              .filter(Boolean) as Edge[];

            // 콜백 주입
            const restoredNodes: Node[] = [...productNodes, ...processNodes].map((n: any) => {
              const data = { ...(n.data || {}) } as any;
              if (n.type === 'product') {
                const productId = data?.id;
                data.onClick = undefined;
                data.onDoubleClick = () => {
                  try { window.dispatchEvent(new CustomEvent('cbam:node:product:open' as any, { detail: { productId, productData: data?.productData || null } })); } catch {}
                };
                return { ...n, data } as Node;
              }
              if (n.type === 'process') {
                const processData = data?.processData || { id: data?.id, process_name: data?.label, start_period: data?.start_period, end_period: data?.end_period, product_names: data?.product_names };
                const ownerInstallId = typeof data.install_id === 'number' ? data.install_id : (processData as any)?.install_id;
                const currentInstallId = selectedInstall?.id;
                (data as any).current_install_id = currentInstallId;
                (data as any).is_readonly = (typeof ownerInstallId === 'number' && typeof currentInstallId === 'number')
                  ? ownerInstallId !== currentInstallId
                  : false;
                (processData as any).install_id = ownerInstallId;
                (processData as any).current_install_id = currentInstallId;
                (processData as any).is_readonly = (data as any).is_readonly;

                data.onClick = () => { try { window.dispatchEvent(new CustomEvent('cbam:node:process:input' as any, { detail: { processData } })); } catch {} };
                data.onMatDirClick = (_pd?: any) => { try { window.dispatchEvent(new CustomEvent('cbam:node:process:input' as any, { detail: { processData } })); } catch {} };
                return { ...n, data } as Node;
              }
              return n as Node;
            });
            setNodes(restoredNodes);
            setEdges(edgesRestored);
            prevNodesRef.current = restoredNodes;
            prevEdgesRef.current = edgesRestored;
            setInstallCanvases(prev => ({ ...prev, [selectedInstall.id]: { nodes: restoredNodes, edges: edgesRestored } }));
          } catch (e) {
            console.warn('⚠️ 서버 복원 실패:', e);
          } finally {
            fetchingRef.current = false;
          }
        })();
      }
    }
  }, [selectedInstall?.id, installCanvases, setNodes, setEdges]);

  // 노드 추가 함수들
  const addProductNode = useCallback((product: Product, handleProductNodeClick: (product: Product) => void) => {
    const newNode = nodeManager.createProductNode(product, selectedInstall, handleProductNodeClick);
    setNodes(prev => {
      const newNodes = [...prev, newNode];
      prevNodesRef.current = newNodes;
      return newNodes;
    });
    
    try {
      const key = `cbam:layout:${selectedInstall?.id}`;
      const payload = { nodes: [...(installCanvases[selectedInstall?.id || 0]?.nodes || []), newNode], edges };
      localStorage.setItem(key, JSON.stringify(payload));
    } catch {}
  }, [setNodes, selectedInstall?.id, nodeManager, installCanvases, edges]);

  const addProcessNode = useCallback(async (process: Process, products: Product[], openInputModal: (process: Process) => void, openProcessModal: (process: Process) => void) => {
    const newNode = await nodeManager.createProcessNode(process, products, selectedInstall, openInputModal);
    setNodes(prev => {
      const newNodes = [...prev, newNode];
      prevNodesRef.current = newNodes;
      return newNodes;
    });
    
    try {
      const key = `cbam:layout:${selectedInstall?.id}`;
      const payload = { nodes: [...(installCanvases[selectedInstall?.id || 0]?.nodes || []), newNode], edges };
      localStorage.setItem(key, JSON.stringify(payload));
    } catch {}
  }, [setNodes, selectedInstall?.id, nodeManager, installCanvases, edges]);

  const addGroupNode = useCallback(() => {
    const newNode = nodeManager.createGroupNode();
    setNodes(prev => {
      const newNodes = [...prev, newNode];
      prevNodesRef.current = newNodes;
      return newNodes;
    });
  }, [setNodes, nodeManager]);

  // 엣지 변경 처리
  const onEdgesChange = useCallback(async (changes: EdgeChange[]) => {
    baseOnEdgesChange(changes);

    const removedIds = new Set(
      changes.filter((c: any) => c.type === 'remove').map((c: any) => c.id)
    );
    if (removedIds.size === 0) return;

    const removedEdges = edges.filter(e => removedIds.has(e.id));

    // 엣지 삭제 후 처리
    await edgeManager.handleEdgeDeletion(removedEdges);

    // 전체 그래프 재계산 후 노드 새로고침
    try {
      const success = await emissionManager.recalculateEntireGraph();
      if (success) {
        // 모든 노드 새로고침
      const allProductNodes = prevNodesRef.current.filter(n => n.type === 'product');
      for (const node of allProductNodes) {
        const productId = (node.data as any)?.id;
        if (productId) {
            const emissionData = await emissionManager.refreshProductEmission(productId);
            if (emissionData) {
              setNodes(prev => nodeManager.updateProductNodeByProductId(prev, productId, emissionData));
        }
      }
        }
      
      const allProcessNodes = prevNodesRef.current.filter(n => n.type === 'process');
      for (const node of allProcessNodes) {
        const processId = (node.data as any)?.id;
        if (processId) {
            const emissionData = await emissionManager.refreshProcessEmission(processId);
            if (emissionData) {
              setNodes(prev => prev.map(n => {
                if (n.type === 'process' && n.data?.id === processId) {
                  return {
                    ...n,
                    data: {
                      ...n.data,
                      processData: {
                        ...(n.data as any).processData,
                        ...emissionData
                      }
                    }
                  } as Node;
                }
                return n;
              }));
            }
          }
        }
        console.log('✅ 모든 노드 새로고침 완료');
      }
    } catch (error) {
      console.warn('⚠️ 엣지 삭제 후 처리 실패:', error);
    }
  }, [edges, baseOnEdgesChange, edgeManager, emissionManager, nodeManager]);

  // 엣지 생성 처리
  const handleEdgeCreate = useCallback(async (params: Connection, updateCallback: () => void = () => {}) => {
    let tempEdgeId: string | null = null;
    
    try {
      if (!params.source || !params.target) return;
      
      const existingEdge = edges.find(edge => 
        edge.source === params.source && 
        edge.target === params.target &&
        edge.sourceHandle === params.sourceHandle &&
        edge.targetHandle === params.targetHandle
      );
      
      if (existingEdge) return;
      
      // 임시 엣지 생성
      tempEdgeId = `temp-${Date.now()}-${Math.random().toString(36).slice(2)}`;
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
      
      // 노드 정보 추출
      const sourceNode = nodeManager.findNodeByAnyId(prevNodesRef.current, params.source);
      const targetNode = nodeManager.findNodeByAnyId(prevNodesRef.current, params.target);
      
      if (!sourceNode || !targetNode) {
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        return;
      }

      const sourceType = sourceNode.type || 'unknown';
      const targetType = targetNode.type || 'unknown';
      const sourceId = (sourceNode.data as any)?.id as number | undefined;
      const targetId = (targetNode.data as any)?.id as number | undefined;

      if (!sourceId || !targetId) {
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        return;
      }
      
      // 엣지 종류 판정
      const edgeKind = edgeManager.determineEdgeKind(sourceType, targetType);
      
      // 유효성 검증
      const validation = edgeManager.validateEdgeConnection(
        params.source, params.target, sourceType, targetType
      );
      
      if (!validation.valid) {
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        alert(validation.error);
        return;
      }

      // 엣지 생성
      const edgeData = {
        source_node_type: sourceType,
        source_id: sourceId,
        target_node_type: targetType,
        target_id: targetId,
        edge_kind: edgeKind
      };
      
      const newEdge = await edgeManager.createEdge(edgeData);
      
      // 임시 엣지를 실제 엣지로 교체
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
        
        if (updateCallback) {
          updateCallback();
        }

      // 배출량 전파
      await edgeManager.propagateEmission(edgeKind, sourceId, targetId);

      // 관련 노드 새로고침
      if (edgeKind === 'continue') {
        const sourceEmission = await emissionManager.refreshProcessEmission(sourceId);
        const targetEmission = await emissionManager.refreshProcessEmission(targetId);
        // 노드 업데이트 로직...
      } else if (edgeKind === 'produce') {
        const sourceEmission = await emissionManager.refreshProcessEmission(sourceId);
        const targetEmission = await emissionManager.refreshProductEmission(targetId);
        if (targetEmission) {
          setNodes(prev => nodeManager.updateProductNodeByProductId(prev, targetId, targetEmission));
          setNodes(prev => nodeManager.setProductProduceFlag(prev, targetId, true));
        }
      } else if (edgeKind === 'consume') {
        const sourceEmission = await emissionManager.refreshProductEmission(sourceId);
        const targetEmission = await emissionManager.refreshProcessEmission(targetId);
        // 노드 업데이트 로직...
      }

    } catch (error: any) {
      console.error('❌ Edge 생성 실패:', error);
      
      if (tempEdgeId) {
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
      }
      
      let errorMessage = 'Edge 생성에 실패했습니다.';
      if (error.response?.status === 500) {
        errorMessage = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
      } else if (error.response?.status === 400) {
        errorMessage = '잘못된 연결 정보입니다. 노드를 다시 선택해주세요.';
      } else if (error.code === 'NETWORK_ERROR') {
        errorMessage = '네트워크 연결을 확인해주세요.';
      }
      
      alert(errorMessage);
    }
  }, [setEdges, edges, nodeManager, edgeManager, emissionManager]);

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
    addProductNode,
    addProcessNode,
    addGroupNode,
    updateNodeData: nodeManager.updateNodeData,
    refreshProcessEmission: emissionManager.refreshProcessEmission,
    refreshProductEmission: emissionManager.refreshProductEmission,
    recalcFromProcess: emissionManager.recalculateFromProcess,
  };
};

// 유효성 검증 함수 (기존과 동일)
export const validateEdgeConnection = (sourceId: string, targetId: string, sourceType: string, targetType: string) => {
  if (sourceId === targetId) {
    return { valid: false, error: '동일한 노드 간 연결은 허용되지 않습니다.' };
  }

  if (sourceType === 'product' && targetType === 'product') {
    return { valid: false, error: '제품 간 직접 연결은 허용되지 않습니다.' };
  }

  const validConnections = [
    { source: 'process', target: 'process', description: '공정 → 공정 (연속)' },
    { source: 'process', target: 'product', description: '공정 → 제품 (생산)' },
    { source: 'product', target: 'process', description: '제품 → 공정 (소비)' }
  ];

  const isValidConnection = validConnections.some(
    conn => conn.source === sourceType && conn.target === targetType
  );

  if (!isValidConnection) {
    return { 
      valid: false, 
      error: `유효하지 않은 연결입니다. 허용된 연결: ${validConnections.map(c => c.description).join(', ')}` 
    };
  }

  return { valid: true, error: null };
};
