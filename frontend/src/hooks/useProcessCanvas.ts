import { useState, useCallback, useEffect, useRef } from 'react';
import { useNodesState, useEdgesState, Node, Edge, Connection, EdgeChange } from '@xyflow/react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { Install, Product, Process } from './useProcessManager';

export const useProcessCanvas = (selectedInstall: Install | null) => {
  // ReactFlow 상태
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, baseOnEdgesChange] = useEdgesState<Edge>([]);

  // 다중 사업장 캔버스 관리
  const [installCanvases, setInstallCanvases] = useState<{[key: number]: {nodes: Node[], edges: Edge[]}}>({});
  // 서버 복원: 마지막 저장된 포지션/구성(없으면 그리드 배치)
  const fetchingRef = useRef<boolean>(false);
  // 시작은 빈 캔버스: 서버 자동 복원 비활성화(필요 시 true로 변경)
  const ENABLE_SERVER_AUTORESTORE = false;
  
  // activeInstallId를 selectedInstall에서 계산
  const activeInstallId = selectedInstall?.id || null;

  // 이전 상태를 추적하여 무한 루프 방지
  const prevInstallIdRef = useRef<number | null>(null);
  const prevNodesRef = useRef<Node[]>([]);
  const prevEdgesRef = useRef<Edge[]>([]);

  // 공용 유틸과 인플라이트/쿨다운 제어
  const normalizeNodeId = useCallback((id: string) => id.replace(/-(left|right|top|bottom)$/i, ''), []);
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
  const inFlightProcess = useRef<Set<number>>(new Set());
  const inFlightProduct = useRef<Set<number>>(new Set());
  const lastFullPropagateAtRef = useRef<number>(0);
  const shouldRunFullPropagate = useCallback(() => {
    const now = Date.now();
    if (now - lastFullPropagateAtRef.current > 800) {
      lastFullPropagateAtRef.current = now;
      return true;
    }
    return false;
  }, []);

  // 캔버스 상태 변경 시 해당 사업장의 캔버스 데이터 업데이트(+ 위치 서버 저장 훅)
  useEffect(() => {
    if (activeInstallId) {
      setInstallCanvases(prev => ({
        ...prev,
        [activeInstallId]: { nodes, edges }
      }));
      // TODO 서버에 좌표 저장 API가 준비되면 여기서 debounce하여 저장 호출
    }
  }, [nodes, edges, activeInstallId]);

  // 최신 nodes 스냅샷을 ref에 유지하여 콜백에서 stale closure 방지
  useEffect(() => {
    prevNodesRef.current = nodes;
  }, [nodes]);
  // 최신 edges 스냅샷도 유지
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

  // 페이지 이탈(새로고침/라우팅) 전에 마지막 스냅샷 저장
  useEffect(() => {
    const handler = () => {
      if (!activeInstallId) return;
      writeSnapshot(activeInstallId, prevNodesRef.current, prevEdgesRef.current);
    };
    window.addEventListener('beforeunload', handler);
    return () => window.removeEventListener('beforeunload', handler);
  }, [activeInstallId, writeSnapshot]);

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

      // 로컬 레이아웃(좌표) 보조 복원
      try {
        // 로컬 레이아웃 보조 복원은 "메모리 상태가 비어있는 경우"에만 수행한다.
        // 이미 installCanvases에 최신 데이터가 있다면 이를 우선시하여
        // 방금 갱신한 프리뷰가 과거 스냅샷으로 덮어씌워지는 것을 방지한다.
        const key = `cbam:layout:${selectedInstall.id}`;
        const raw = localStorage.getItem(key);
        if (raw && canvasData.nodes.length === 0 && canvasData.edges.length === 0) {
          const parsed = JSON.parse(raw);
          if (parsed?.nodes && parsed?.edges) {
            // 🔁 함수 유실 복구: 노드 콜백 재주입
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
                // 🔁 복원 시 현재 선택된 사업장 기준으로 읽기전용 여부 재계산
                const ownerInstallId = typeof data.install_id === 'number' ? data.install_id : (processData as any)?.install_id;
                const currentInstallId = selectedInstall?.id;
                (data as any).current_install_id = currentInstallId;
                (data as any).is_readonly = (typeof ownerInstallId === 'number' && typeof currentInstallId === 'number')
                  ? ownerInstallId !== currentInstallId
                  : false;
                (processData as any).install_id = ownerInstallId;
                (processData as any).current_install_id = currentInstallId;
                (processData as any).is_readonly = (data as any).is_readonly;

                // 클릭은 사용하지 않지만, 호환성 위해 CustomEvent 트리거 유지
                data.onClick = () => {
                  try {
                    window.dispatchEvent(new CustomEvent('cbam:node:process:input' as any, { detail: { processData } }));
                  } catch {}
                };
                // 버튼이 호출하는 onMatDirClick도 복원 (콜백 유실 방지)
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

      // 서버에서 노드/엣지 복원(옵션): 기본은 비활성화 → 빈 캔버스로 시작
      if (ENABLE_SERVER_AUTORESTORE && (!canvasData.nodes.length && !canvasData.edges.length) && !fetchingRef.current) {
        fetchingRef.current = true;
        (async () => {
          try {
            // 1) 설치의 제품/공정 목록
            const [productsResp, processesResp, edgesResp] = await Promise.all([
              axiosClient.get(`${apiEndpoints.cbam.product.list}?install_id=${selectedInstall.id}`),
              axiosClient.get(apiEndpoints.cbam.process.list),
              axiosClient.get(apiEndpoints.cbam.edge.list)
            ]);
            const products: any[] = (productsResp?.data || []).filter((p: any) => p.install_id === selectedInstall.id);
            const processes: any[] = (processesResp?.data || []).filter((pr: any) => (pr.products || []).some((p: any) => products.find(pp => pp.id === p.id)));
            const edgesAll: any[] = edgesResp?.data || [];

            // 2) 그리드 배치(간단): 제품 왼쪽, 공정 오른쪽으로 나열
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

            // 3) 엣지 복원: 설치 범위의 제품/공정만 연결 생성
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

            // 🔁 서버 복원 시에도 콜백 주입
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
                // 🔁 서버 복원 시에도 현재 사업장 기준으로 읽기전용 여부 재계산
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

  // 제품 수량 업데이트 브로드캐스트 수신 → 해당 제품 노드 프리뷰 갱신
  // (핸들러는 업데이트 함수 정의 이후에 등록되어야 하므로 아래로 이동)

  // 사업장 선택 시 캔버스 상태 복원 (이제 useEffect에서 자동 처리)
  const handleInstallSelect = useCallback((install: Install) => {
    // 이 함수는 이제 사용되지 않지만, 호환성을 위해 유지
    // 실제 캔버스 상태 복원은 useEffect에서 자동으로 처리됨
  }, []);

  // 노드 데이터 업데이트
  const updateNodeData = useCallback((nodeId: string, newData: any) => {
    setNodes(prev => prev.map(node => 
      node.id === nodeId 
        ? { ...node, data: { ...node.data, ...newData } }
        : node
    ));
  }, [setNodes]);

  // 제품 ID로 제품 노드의 수량/프리뷰 값을 업데이트
  const updateProductNodeByProductId = useCallback((productId: number, newFields: any) => {
    // 1) 활성 캔버스 갱신
    setNodes(prev => prev.map(node => {
      if (node.type === 'product' && (node.data as any)?.id === productId) {
        const prevProductData = (node.data as any).productData || {};
        return {
          ...node,
          data: {
            ...node.data,
            ...newFields,
            product_amount: newFields.product_amount ?? (node.data as any).product_amount,
            productData: {
              ...prevProductData,
              production_qty: newFields.product_amount ?? prevProductData.production_qty,
              product_sell: newFields.product_sell ?? prevProductData.product_sell,
              product_eusell: newFields.product_eusell ?? prevProductData.product_eusell
            }
          }
        } as Node;
      }
      return node;
    }));

    // 2) 모든 사업장 캔버스 갱신 + 로컬 스냅샷 동기화
    setInstallCanvases(prev => {
      const next = { ...prev } as { [key: number]: { nodes: Node[]; edges: Edge[] } };
      for (const key of Object.keys(next)) {
        const k = Number(key);
        const canvas = next[k] || { nodes: [], edges: [] };
        const updatedNodes = (canvas.nodes || []).map((n: any) => {
          if (n?.type === 'product' && (n.data as any)?.id === productId) {
            const prevProductData = (n.data as any)?.productData || {};
            return {
              ...n,
              data: {
                ...n.data,
                ...newFields,
                product_amount: newFields.product_amount ?? (n.data as any).product_amount,
                productData: {
                  ...prevProductData,
                  production_qty: newFields.product_amount ?? prevProductData.production_qty,
                  product_sell: newFields.product_sell ?? prevProductData.product_sell,
                  product_eusell: newFields.product_eusell ?? prevProductData.product_eusell
                }
              }
            } as Node;
          }
          return n as Node;
        });
        next[k] = { ...canvas, nodes: updatedNodes };
        try {
          const lsKey = `cbam:layout:${k}`;
          const payload = { nodes: updatedNodes, edges: canvas.edges };
          localStorage.setItem(lsKey, JSON.stringify(payload));
        } catch {}
      }
      return next;
    });
  }, [setNodes]);

  // 특정 제품 노드의 produce 연결 여부를 표시 (배출량 프리뷰 표시 제어용)
  const setProductProduceFlag = useCallback((productId: number, hasProduce: boolean) => {
    setNodes(prev => prev.map(node => {
      if (node.type === 'product' && (node.data as any)?.id === productId) {
        return {
          ...node,
          data: {
            ...node.data,
            has_produce_edge: hasProduce
          }
        } as Node;
      }
      return node;
    }));
  }, [setNodes]);

  // 이제 업데이트 함수가 정의되었으므로 이벤트 리스너 등록
  useEffect(() => {
    const handler = (e: any) => {
      const { productId, product_amount } = e.detail || {};
      if (!productId) return;
      updateProductNodeByProductId(productId, { product_amount });
    };
    window.addEventListener('cbam:updateProductAmount' as any, handler);
    return () => window.removeEventListener('cbam:updateProductAmount' as any, handler);
  }, [updateProductNodeByProductId]);

  

  // 엣지 연결 여부에 상관없이 직접/원료/연료 값은 항상 보이도록 유지
  // 누적 값은 연결 여부와 무관하게 현재 DB 상태를 표시
  useEffect(() => {
    setNodes(prev => prev.map(n => ({ ...n, data: { ...n.data } }) as Node));
  }, [edges, setNodes]);

  

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
        // 제품 배출량 표시용
        attr_em: (product as any)?.attr_em || 0,
        // 프리뷰 수치(생산량/판매량) 초기값을 즉시 세팅하여 0 표시를 방지
        product_amount: Number((product as any)?.product_amount ?? 0),
        product_sell: Number((product as any)?.product_sell ?? 0),
        product_eusell: Number((product as any)?.product_eusell ?? 0),
        install_id: selectedInstall?.id,
        // 클릭은 아무 동작 없음, 더블클릭 시 공정선택 모달
        onClick: undefined,
        onDoubleClick: () => handleProductNodeClick(product),
        // 🔴 추가: ProductNode가 기대하는 추가 데이터
        size: 'md',
        showHandles: true,
      },
    };

    // setNodes를 사용하여 안전하게 노드 추가
    setNodes(prev => {
      const newNodes = [...prev, newNode];
      prevNodesRef.current = newNodes;
      return newNodes;
    });
    // 위치 저장: 서버 API 없으므로 일단 로컬스토리지로 보조 저장
    try {
      const key = `cbam:layout:${selectedInstall?.id}`;
      const payload = { nodes: [...(installCanvases[selectedInstall?.id || 0]?.nodes || []), newNode], edges };
      localStorage.setItem(key, JSON.stringify(payload));
    } catch {}
  }, [setNodes, selectedInstall?.id]);

  // 공정 노드 추가 (안전한 상태 업데이트)
  const addProcessNode = useCallback(async (process: Process, products: Product[], openInputModal: (process: Process) => void, openProcessModal: (process: Process) => void) => {
    // 해당 공정이 사용되는 모든 제품 정보 찾기
    const relatedProducts = products.filter((product: Product) => 
      process.products?.some(p => p.id === product.id)
    );

    // 공정별 직접귀속배출량 정보 가져오기
    let emissionData = null;
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.calculation.process.attrdir(process.id));
      if (response.data) {
        emissionData = {
          attr_em: response.data.attrdir_em || 0,
          total_matdir_emission: response.data.total_matdir_emission || 0,
          total_fueldir_emission: response.data.total_fueldir_emission || 0,
          calculation_date: response.data.calculation_date
        };
      }
    } catch (error) {
      /* noop */
    }

    // 🔴 수정: 더 작은 ID 생성 (int32 범위 내)
    const nodeId = Math.floor(Math.random() * 1000000) + 1; // 1 ~ 1,000,000
    const actualNodeId = `process-${nodeId}-${Math.random().toString(36).slice(2)}`;
    
    const newNode: Node = {
      id: actualNodeId,
      type: 'process',  // 'process' 타입으로 설정
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        id: process.id,  // 실제 공정 ID 추가
        nodeId: actualNodeId,  // 🔴 추가: 실제 노드 ID를 data에 저장
        label: process.process_name,  // 🔴 수정: label을 올바르게 설정
        description: `공정: ${process.process_name}`,
        variant: 'process',  // 🔴 수정: variant를 'process'로 명시적 설정
        // 읽기전용/외부 사업장 판정에 사용하는 상위 레벨 메타데이터
        install_id: (process as any).install_id, // 공정 소속 사업장
        current_install_id: selectedInstall?.id, // 현재 캔버스 사업장
        is_readonly: (process as any).install_id !== selectedInstall?.id,
        processData: {
          ...process,
          start_period: process.start_period || 'N/A',
          end_period: process.end_period || 'N/A',
          // 관련 제품이 없으면 'N/A' 대신 빈 문자열로 유지하여 필터를 막지 않음
          product_names: relatedProducts.map(p => p.product_name).join(', '),
          is_many_to_many: relatedProducts.length > 1,
          install_id: (process as any).install_id,
          current_install_id: selectedInstall?.id,
          is_readonly: (process as any).install_id !== selectedInstall?.id,
          // 배출량 정보 추가
          ...emissionData
        },
        // 클릭 시 바로 투입량 입력 모달 열기
        onClick: () => openInputModal(process),
        onMatDirClick: (processData: any) => openInputModal(processData),
        // 🔴 추가: ProcessNode가 기대하는 추가 데이터
        size: 'md',
        showHandles: true,
      },
    };

    // setNodes를 사용하여 안전하게 노드 추가
    setNodes(prev => {
      const newNodes = [...prev, newNode];
      prevNodesRef.current = newNodes;
      return newNodes;
    });
    // 위치 저장 보조
    try {
      const key = `cbam:layout:${selectedInstall?.id}`;
      const payload = { nodes: [...(installCanvases[selectedInstall?.id || 0]?.nodes || []), newNode], edges };
      localStorage.setItem(key, JSON.stringify(payload));
    } catch {}
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

    // setNodes를 사용하여 안전하게 노드 추가
    setNodes(prev => {
      const newNodes = [...prev, newNode];
      prevNodesRef.current = newNodes;
      return newNodes;
    });
  }, [setNodes]);

  // 특정 공정 노드만 배출량 정보 새로고침
  const refreshProcessEmission = useCallback(async (processId: number) => {
    if (inFlightProcess.current.has(processId)) return;
    inFlightProcess.current.add(processId);
    try {
      // 우선 조회, 404라면 계산 후 다시 반영
      let data: any = null;
      try {
        // 누적/직접 동시 조회를 위해 Edge 도메인 조회 사용
        const resp = await axiosClient.get(apiEndpoints.cbam.edgePropagation.processEmission(processId));
        data = resp?.data?.data || null;
      } catch (err: any) {
        if (err?.response?.status === 404) {
          try {
            const created = await axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(processId));
            // 생성 직후 누적 포함 최신값 재조회
            const resp2 = await axiosClient.get(apiEndpoints.cbam.edgePropagation.processEmission(processId));
            data = resp2?.data?.data || created?.data;
          } catch (calcErr) {
            console.warn('⚠️ 공정 배출량 계산 실패:', calcErr);
            return;
          }
        } else {
          throw err;
        }
      }
      if (!data) return;

      // 실제 입력 테이블 기준 총합과 DB 저장값 차이를 교차검증하여 정합성 보장
      try {
        const [matTotResp, fuelTotResp] = await Promise.all([
          axiosClient.get(apiEndpoints.cbam.matdir.totalByProcess(processId)).catch(() => null),
          axiosClient.get(apiEndpoints.cbam.fueldir.totalByProcess(processId)).catch(() => null)
        ]);
        const latestMatTotal = Number(matTotResp?.data?.total_matdir_emission ?? 0) || 0;
        const latestFuelTotal = Number(fuelTotResp?.data?.total_fueldir_emission ?? 0) || 0;
        const savedMatTotal = Number(data.total_matdir_emission ?? data.total_matdir ?? 0) || 0;
        const savedFuelTotal = Number(data.total_fueldir_emission ?? data.total_fueldir ?? 0) || 0;
        const mismatch = Math.abs(latestMatTotal - savedMatTotal) > 1e-6 || Math.abs(latestFuelTotal - savedFuelTotal) > 1e-6;
        if (mismatch) {
          try {
            await axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(processId));
            const latest = await axiosClient.get(apiEndpoints.cbam.edgePropagation.processEmission(processId));
            data = latest?.data?.data || data;
          } catch (_) {}
        }
      } catch (_) {}
      // 합계가 0이어도 실제 계산 결과일 수 있으므로
      // "값 존재 여부"를 기준으로 표시값을 결정한다.
      const hasMatPart = ('total_matdir_emission' in data) || ('total_matdir' in data);
      const hasFuelPart = ('total_fueldir_emission' in data) || ('total_fueldir' in data);
      const hasDirectParts = hasMatPart || hasFuelPart;

      const totalMat = Number(data.total_matdir_emission ?? data.total_matdir ?? 0) || 0;
      const totalFuel = Number(data.total_fueldir_emission ?? data.total_fueldir ?? 0) || 0;
      const sumDirect = totalMat + totalFuel;
      const directFromDb = Number(data.attrdir_em ?? data.attrdir_emission ?? 0) || 0;
      // 부분 값이 존재하면 합계를 우선(0 포함), 없으면 DB 값을 사용
      const directFixed = hasDirectParts ? sumDirect : directFromDb;

      // 백그라운드 보정: 부분 값이 존재하고 DB와 차이가 나면 재계산 트리거
      if (hasDirectParts && Math.abs(directFromDb - sumDirect) > 1e-6) {
        axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(processId)).catch(() => {});
      }

      const emissionData = {
        attr_em: directFixed,
        cumulative_emission: data.cumulative_emission || 0,
        total_matdir_emission: totalMat,
        total_fueldir_emission: totalFuel,
        calculation_date: data.calculation_date
      };
      // 1) 현재 활성 캔버스 노드 갱신
      setNodes(prev => prev.map(node => {
        if (node.type === 'process' && node.data?.id === processId) {
          return {
            ...node,
            data: {
              ...node.data,
              processData: {
                ...(node.data as any).processData,
                ...emissionData
              }
            }
          } as Node;
        }
        return node;
      }));

      // 2) 다른 사업장 캔버스에도 동일 공정(ID 매칭) 프리뷰를 동기 반영
      setInstallCanvases(prev => {
        const next = { ...prev } as { [key: number]: { nodes: Node[]; edges: Edge[] } };
        for (const key of Object.keys(next)) {
          const k = Number(key);
          const canvas = next[k] || { nodes: [], edges: [] };
          const updatedNodes = (canvas.nodes || []).map((n: any) => {
            if (n?.type === 'process' && (n.data as any)?.id === processId) {
              return {
                ...n,
                data: {
                  ...n.data,
                  processData: {
                    ...(n.data as any)?.processData,
                    ...emissionData,
                  }
                }
              } as Node;
            }
            return n as Node;
          });
          next[k] = { ...canvas, nodes: updatedNodes };
          // 로컬 스냅샷도 동기화하여 탭 전환 시 과거 스냅샷으로 덮어씌워지지 않도록 한다.
          writeSnapshot(k, updatedNodes, canvas.edges);
        }
        return next;
      });
    } catch (e) {
      console.error('⚠️ 공정 배출량 새로고침 실패:', e);
    } finally {
      inFlightProcess.current.delete(processId);
    }
  }, [setNodes]);

  // 모든 공정 노드를 일괄 새로고침
  const refreshAllProcessEmissions = useCallback(async () => {
    try {
      const ids = Array.from(
        new Set(
          (prevNodesRef.current || [])
            .filter(n => n.type === 'process')
            .map(n => (n.data as any)?.id)
            .filter((id): id is number => typeof id === 'number')
        )
      );
      if (!ids.length) return;
      await Promise.all(ids.map(pid => refreshProcessEmission(pid)));
    } catch (e) {
      console.warn('⚠️ 전체 공정 프리뷰 새로고침 실패:', e);
    }
  }, [refreshProcessEmission]);

  // 사업장 전환 직후(복원 이후) 한 번 전체 프리뷰를 재조회하여
  // 로컬 스냅샷의 오래된 값이 화면을 덮어쓰지 않도록 한다.
  const lastRefreshedInstallIdRef = useRef<number | null>(null);
  useEffect(() => {
    if (!activeInstallId) return;
    if (lastRefreshedInstallIdRef.current === activeInstallId) return;
    // 복원 직후 렌더가 끝난 뒤 실행되도록 마이크로 딜레이
    const t = window.setTimeout(() => {
      refreshAllProcessEmissions();
      // 제품 프리뷰도 함께 새로고침
      try {
        const productIds = Array.from(
          new Set(
            (prevNodesRef.current || [])
              .filter(n => n.type === 'product')
              .map(n => (n.data as any)?.id)
              .filter((id): id is number => typeof id === 'number')
          )
        );
        productIds.forEach(pid => refreshProductEmission(pid));
      } catch {}
      lastRefreshedInstallIdRef.current = activeInstallId;
    }, 0);
    return () => window.clearTimeout(t);
  }, [activeInstallId, nodes.length, refreshAllProcessEmissions]);

  // 공정 배출량이 없으면 생성까지 보장
  const ensureProcessAttrdirComputed = useCallback(async (processId: number) => {
    try {
      await axiosClient.get(apiEndpoints.cbam.calculation.process.attrdir(processId));
    } catch (err: any) {
      if (err?.response?.status === 404) {
        await axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(processId));
      } else {
        throw err;
      }
    }
  }, []);

  // 특정 제품 노드만 배출량 정보 새로고침 (recalcFromProcess보다 먼저 선언)
  const refreshProductEmission = useCallback(async (productId: number) => {
    if (inFlightProduct.current.has(productId)) return;
    inFlightProduct.current.add(productId);
    try {
      let attrEm = 0;
      let hasProduceEdge = false;
      try {
        const preview = await axiosClient.get(apiEndpoints.cbam.edgePropagation.productPreview(productId));
        attrEm = preview?.data?.preview_attr_em ?? 0;
        hasProduceEdge = true; // 프리뷰 API가 성공하면 produce 엣지가 있다는 의미
      } catch {
        const response = await axiosClient.get(apiEndpoints.cbam.product.get(productId));
        const product = response?.data;
        attrEm = product?.attr_em || 0;
        // 제품에 직접 배출량이 있으면 produce 엣지가 있다고 간주
        hasProduceEdge = attrEm > 0;
      }
      
      // 현재 엣지 상태에서 produce 엣지와 consume 엣지 확인
      const currentEdges = prevEdgesRef.current || [];
      const hasProduceEdgeFromEdges = currentEdges.some(edge => {
        const edgeData = (edge.data as any)?.edgeData;
        return edgeData?.edge_kind === 'produce' && 
               edge.target && 
               (prevNodesRef.current || []).some(n => 
                 n.id === edge.target && 
                 n.type === 'product' && 
                 (n.data as any)?.id === productId
               );
      });
      
      const hasConsumeEdgeFromEdges = currentEdges.some(edge => {
        const edgeData = (edge.data as any)?.edgeData;
        return edgeData?.edge_kind === 'consume' && 
               edge.source && 
               (prevNodesRef.current || []).some(n => 
                 n.id === edge.source && 
                 n.type === 'product' && 
                 (n.data as any)?.id === productId
               );
      });
      
      // 최종 has_produce_edge 결정: produce 엣지가 있거나 consume 엣지가 있을 때 배출량 표시
      const finalHasProduceEdge = hasProduceEdgeFromEdges || hasConsumeEdgeFromEdges;
      
      // 1) 활성 캔버스 갱신
      setNodes(prev => prev.map(node => {
        if (node.type === 'product' && node.data?.id === productId) {
          return {
            ...node,
            data: {
              ...node.data,
              attr_em: attrEm,
              has_produce_edge: finalHasProduceEdge,
              productData: {
                ...(node.data as any).productData,
                attr_em: attrEm,
                production_qty: (node.data as any).productData?.production_qty ?? (node.data as any).product_amount ?? 0
              }
            }
          } as Node;
        }
        return node;
      }));

      // 2) 모든 사업장 캔버스 갱신 + 로컬 스냅샷 동기화
      setInstallCanvases(prev => {
        const next = { ...prev } as { [key: number]: { nodes: Node[]; edges: Edge[] } };
        for (const key of Object.keys(next)) {
          const k = Number(key);
          const canvas = next[k] || { nodes: [], edges: [] };
          const updatedNodes = (canvas.nodes || []).map((n: any) => {
            if (n?.type === 'product' && (n.data as any)?.id === productId) {
              return {
                ...n,
                data: {
                  ...n.data,
                  attr_em: attrEm,
                  has_produce_edge: finalHasProduceEdge,
                  productData: {
                    ...(n.data as any)?.productData,
                    attr_em: attrEm,
                    production_qty: (n.data as any)?.productData?.production_qty ?? (n.data as any)?.product_amount ?? 0
                  }
                }
              } as Node;
            }
            return n as Node;
          });
          next[k] = { ...canvas, nodes: updatedNodes };
          writeSnapshot(k, updatedNodes, canvas.edges);
        }
        return next;
      });

      // 3) 전역 이벤트 브로드캐스트: 리포트 등 외부 프리뷰 섹션 갱신용
      try {
        window.dispatchEvent(new CustomEvent('cbam:product:emission:update' as any, { detail: { productId, attrEm } }));
      } catch {}
    } catch (e) {
      console.error('⚠️ 제품 배출량 새로고침 실패:', e);
    } finally {
      inFlightProduct.current.delete(productId);
    }
  }, [setNodes]);

  // 제품 저장 후 강제 새로고침(제품 → 소비공정 → 하류제품까지)
  useEffect(() => {
    const handler = async (e: any) => {
      const { productId, product_amount, product_sell, product_eusell } = e.detail || {};
      if (!productId) return;
      try {
        // 0) 낙관적 갱신: 모달에서 넘어온 값이 있으면 즉시 반영
        if (typeof product_amount === 'number' || typeof product_sell === 'number' || typeof product_eusell === 'number') {
          updateProductNodeByProductId(productId, {
            ...(typeof product_amount === 'number' ? { product_amount } : {}),
            ...(typeof product_sell === 'number' ? { product_sell } : {}),
            ...(typeof product_eusell === 'number' ? { product_eusell } : {}),
          });
        }
        // 1) 제품 프리뷰(배출량) 갱신
        await refreshProductEmission(productId);
        // 2) 제품 판매량/유럽판매량 등 메타데이터 동기화(서버 확정값)
        try {
          const prodResp = await axiosClient.get(apiEndpoints.cbam.product.get(productId));
          const p = prodResp?.data || {};
          updateProductNodeByProductId(productId, {
            product_amount: Number(p.product_amount ?? product_amount ?? 0),
            product_sell: Number(p.product_sell ?? product_sell ?? 0),
            product_eusell: Number(p.product_eusell ?? product_eusell ?? 0),
          });
        } catch (_) {}
        // 이 제품을 consume하는 공정들 찾아 새로고침
        const productNode = (prevNodesRef.current || []).find(n => n.type === 'product' && (n.data as any)?.id === productId);
        if (!productNode) return;
        const normalize = (id?: string) => (id || '').replace(/-(left|right|top|bottom)$/i, '');
        const consumerProcessIds = (edges || [])
          .filter((e: any) => normalize(e.source) === productNode.id && (e.data as any)?.edgeData?.edge_kind === 'consume')
          .map((e: any) => {
            const targetNode = (prevNodesRef.current || []).find(n => normalize(n.id) === normalize(e.target));
            const pid = (targetNode?.data as any)?.id;
            return typeof pid === 'number' ? pid : undefined;
          })
          .filter((id: any): id is number => typeof id === 'number');
        if (consumerProcessIds.length) {
          await Promise.all(consumerProcessIds.map(pid => refreshProcessEmission(pid)));
        }
      } catch {}
    };
    window.addEventListener('cbam:refreshProduct' as any, handler);
    return () => window.removeEventListener('cbam:refreshProduct' as any, handler);
  }, [edges, refreshProductEmission, refreshProcessEmission]);

  // 공정 기준 재계산 트리거 + 영향 노드 부분 갱신 (refresh* 정의 이후에 위치해야 함)
  const recalcFromProcess = useCallback(async (processId: number) => {
    try {
      const resp = await axiosClient.post(
        apiEndpoints.cbam.calculation.process.recalculate(processId)
      );
      const updatedProcessIds: number[] = resp?.data?.updated_process_ids || [];
      const updatedProductIds: number[] = resp?.data?.updated_product_ids || [];

      // 입력 변경 후에는 누적 전파를 항상 한 번 수행하여 상/하류 누적치를 일관화
      try {
        await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate, {});
      } catch (e) {
        console.warn('⚠️ fullPropagate 실패(무시 가능):', e);
      }

      await Promise.all([
        ...updatedProcessIds.map(id => refreshProcessEmission(id)),
        ...updatedProductIds.map(id => refreshProductEmission(id))
      ]);

      // 보강 1: 현재 캔버스 상에서 해당 공정과 produce로 연결된 제품 프리뷰를 강제 동기화
      try {
        // 해당 공정의 리액트플로우 노드 ID 찾기
        const processNode = (prevNodesRef.current || []).find(n => n.type === 'process' && (n.data as any)?.id === processId);
        if (processNode) {
          const normalize = (id?: string) => (id || '').replace(/-(left|right|top|bottom)$/i, '');
          const producedProductIds: number[] = (edges || [])
            .filter((e: any) => normalize(e.source) === processNode.id && (e.data as any)?.edgeData?.edge_kind === 'produce')
            .map((e: any) => {
              const targetNode = (prevNodesRef.current || []).find(n => n.id === e.target);
              const pid = (targetNode?.data as any)?.id;
              return typeof pid === 'number' ? pid : undefined;
            })
            .filter((pid: any): pid is number => typeof pid === 'number');
          if (producedProductIds.length) {
            await Promise.all(producedProductIds.map(pid => refreshProductEmission(pid)));
          }

          // 보강 1.5: 이 공정이 소비하는 상류 제품 및 그 제품을 생산한 상류 공정도 동기 새로고침
          try {
            const normalize = (id?: string) => (id || '').replace(/-(left|right|top|bottom)$/i, '');
            // 이 공정으로 들어오는 consume 엣지의 source(제품 노드) 수집
            const incomingProductIds = (edges || [])
              .filter((e: any) => (e?.data?.edgeData?.edge_kind === 'consume'))
              .filter((e: any) => normalize(e.target) === processNode.id)
              .map((e: any) => {
                const srcNode = (prevNodesRef.current || []).find(n => normalize(n.id) === normalize(e.source));
                const pid = (srcNode?.data as any)?.id;
                return typeof pid === 'number' ? pid : undefined;
              })
              .filter((pid: any): pid is number => typeof pid === 'number');

            if (incomingProductIds.length) {
              // 상류 제품 프리뷰 동기화
              await Promise.all(incomingProductIds.map(pid => refreshProductEmission(pid)));

              // 해당 제품을 생산한 상류 공정들 동기화 (produce 엣지의 source가 공정)
              const incomingProductNodeIds = incomingProductIds
                .map(pid => (prevNodesRef.current || []).find(n => n.type === 'product' && (n.data as any)?.id === pid)?.id)
                .filter((nid): nid is string => typeof nid === 'string');

              const upstreamProcessIdSet = new Set<number>();
              for (const e of (edges || [])) {
                const isProduce = (e as any)?.data?.edgeData?.edge_kind === 'produce';
                if (!isProduce) continue;
                const tgtNorm = normalize(e.target);
                if (!incomingProductNodeIds.includes(tgtNorm)) continue;
                const srcNode = (prevNodesRef.current || []).find(n => normalize(n.id) === normalize(e.source));
                const upPid = (srcNode?.data as any)?.id;
                if (typeof upPid === 'number') upstreamProcessIdSet.add(upPid);
              }
              const upstreamProcessIds = Array.from(upstreamProcessIdSet);
              if (upstreamProcessIds.length) {
                await Promise.all(upstreamProcessIds.map(pid => refreshProcessEmission(pid)));
              }
            }
          } catch (_) {}

          // 보강 2: 위에서 갱신된 제품을 소비(consume)하는 공정들까지 동기화하고
          // 그 공정이 생산하는 제품(예: 형강)까지 연쇄로 동기화
          // produced products를 소비하는 공정들 추출
          const producedProductNodeIds = producedProductIds
            .map(pid => (prevNodesRef.current || []).find(n => n.type === 'product' && (n.data as any)?.id === pid)?.id)
            .filter((nid): nid is string => typeof nid === 'string');

          const consumerProcessIdSet = new Set<number>();
          for (const e of (edges || [])) {
            const isConsume = (e as any)?.data?.edgeData?.edge_kind === 'consume';
            if (!isConsume) continue;
            const srcNorm = normalize(e.source);
            if (!producedProductNodeIds.includes(srcNorm)) continue;
            const targetNode = (prevNodesRef.current || []).find(n => normalize(n.id) === normalize(e.target));
            const procId = (targetNode?.data as any)?.id;
            if (typeof procId === 'number') consumerProcessIdSet.add(procId);
          }
          const consumerProcessIds = Array.from(consumerProcessIdSet);

          if (consumerProcessIds.length) {
            await Promise.all(consumerProcessIds.map(pid => refreshProcessEmission(pid)));

            // 각 소비 공정이 produce로 연결한 제품들도 갱신 (예: 압연 → 형강)
            // 소비 공정이 생산하는 제품들(예: 압연→형강)
            const consumerProcessNodeIds = consumerProcessIds
              .map(cp => (prevNodesRef.current || []).find(n => n.type === 'process' && (n.data as any)?.id === cp)?.id)
              .filter((nid): nid is string => typeof nid === 'string');

            const downstreamProductIdSet = new Set<number>();
            for (const e of (edges || [])) {
              const isProduce = (e as any)?.data?.edgeData?.edge_kind === 'produce';
              if (!isProduce) continue;
              const srcNorm = normalize(e.source);
              if (!consumerProcessNodeIds.includes(srcNorm)) continue;
              const targetNode = (prevNodesRef.current || []).find(n => normalize(n.id) === normalize(e.target));
              const pid = (targetNode?.data as any)?.id;
              if (typeof pid === 'number') downstreamProductIdSet.add(pid);
            }
            const downstreamProductIds = Array.from(downstreamProductIdSet);

            if (downstreamProductIds.length) {
              await Promise.all(downstreamProductIds.map(pid => refreshProductEmission(pid)));
            }
          }
        }
      } catch (_) {}
    } catch (e) {
      console.error('⚠️ 재계산 트리거 실패:', e);
      await refreshProcessEmission(processId);
    }
  }, [refreshProcessEmission, refreshProductEmission]);

  // 🔄 제품 수량 변경 시 캔버스 노드 새로고침 (백엔드에서 배출량 자동 계산됨)
  const refreshAllNodesAfterProductUpdate = useCallback(async (productId: number) => {
    try {
      console.log(`🔄 제품 ${productId} 수량 변경으로 인한 전체 그래프 배출량 재계산 시작`);
      
      // 1. 전체 그래프 배출량 재계산 (제품 수량 변경으로 인한 영향 반영)
      try {
        await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate, {});
        console.log('✅ 전체 그래프 배출량 재계산 완료');
      } catch (e) {
        console.warn('⚠️ 전체 그래프 배출량 재계산 실패:', e);
      }
      
      // 2. 모든 제품 노드 새로고침 (재계산된 배출량 반영)
      const allProductNodes = nodes.filter(n => n.type === 'product');
      for (const node of allProductNodes) {
        const id = (node.data as any)?.id;
        if (id) {
          await refreshProductEmission(id);
        }
      }
      console.log('✅ 모든 제품 노드 새로고침 완료');
      
      // 3. 모든 공정 노드 새로고침 (재계산된 배출량 반영)
      const allProcessNodes = nodes.filter(n => n.type === 'process');
      for (const node of allProcessNodes) {
        const id = (node.data as any)?.id;
        if (id) {
          await refreshProcessEmission(id);
        }
      }
      console.log('✅ 모든 공정 노드 새로고침 완료');
      
      console.log('✅ 제품 수량 변경으로 인한 전체 그래프 배출량 재계산 완료');
    } catch (error) {
      console.error('❌ 제품 수량 변경으로 인한 전체 그래프 배출량 재계산 실패:', error);
    }
  }, [nodes, refreshProcessEmission, refreshProductEmission]);

  // 제품 수량 변경 시 캔버스 노드들 새로고침 이벤트 리스너
  useEffect(() => {
    const handler = async (event: CustomEvent) => {
      const { productId } = event.detail;
      if (productId) {
        await refreshAllNodesAfterProductUpdate(productId);
      }
    };
    
    window.addEventListener('cbam:refreshAllNodesAfterProductUpdate' as any, handler);
    return () => window.removeEventListener('cbam:refreshAllNodesAfterProductUpdate' as any, handler);
  }, [refreshAllNodesAfterProductUpdate]);

  // 엣지 삭제 동기화: UI에서 삭제되면 서버 edge도 삭제하고 관련 노드 새로고침
  const onEdgesChange = useCallback(async (changes: EdgeChange[]) => {
    // 기존 상태 업데이트
    baseOnEdgesChange(changes);

    // 삭제된 엣지들 수집
    const removedIds = new Set(
      changes.filter((c: any) => c.type === 'remove').map((c: any) => c.id)
    );
    if (removedIds.size === 0) return;

    // 현재 스냅샷에서 삭제된 엣지 상세 찾기
    const removedEdges = edges.filter(e => removedIds.has(e.id));

    // 유틸: 노드 탐색
    const normalizeNodeId = (id: string) => id.replace(/-(left|right|top|bottom)$/i, '');
    const getNodeByAnyId = (candidateId: string) => {
      const id = normalizeNodeId(candidateId);
      return (
        prevNodesRef.current.find(n => n.id === id) ||
        prevNodesRef.current.find(n => (n.data as any)?.nodeId === id) ||
        prevNodesRef.current.find(n => id.startsWith(n.id)) ||
        prevNodesRef.current.find(n => id.startsWith(((n.data as any)?.nodeId) || '')) ||
        prevNodesRef.current.find(n => n.id.startsWith(id)) ||
        prevNodesRef.current.find(n => ((((n.data as any)?.nodeId) || '') as string).startsWith(id))
      );
    };

    // 백엔드 삭제 + 관련 노드 갱신
    for (const edge of removedEdges) {
      try {
        const m = /^e-(\d+)/.exec(edge.id);
        if (m) {
          const edgeId = parseInt(m[1], 10);
          await axiosClient.delete(apiEndpoints.cbam.edge.delete(edgeId));
        }
      } catch (err) {
        console.warn('⚠️ 서버 엣지 삭제 실패(무시 가능):', err);
      }

      // 영향 노드 새로고침
      const sourceNode = getNodeByAnyId(edge.source);
      const targetNode = getNodeByAnyId(edge.target);
      const sourceType = sourceNode?.type;
      const targetType = targetNode?.type;
      const sourceId = (sourceNode?.data as any)?.id as number | undefined;
      const targetId = (targetNode?.data as any)?.id as number | undefined;

      try {
        if (sourceType === 'process' && targetType === 'process') {
          if (sourceId) await refreshProcessEmission(sourceId);
          if (targetId) await refreshProcessEmission(targetId);
        } else if (sourceType === 'process' && targetType === 'product') {
          if (targetId) {
            setProductProduceFlag(targetId, false);
            // 연결 잔여 여부 확인 후 프리뷰 리셋 또는 재조회
            try {
              const byNode = await axiosClient.get(apiEndpoints.cbam.edge.byNode(targetId));
              const hasProduce = Array.isArray(byNode?.data) && byNode.data.some((e: any) => e.edge_kind === 'produce' && e.target_id === targetId);
              if (!hasProduce) {
                updateProductNodeByProductId(targetId, { attr_em: 0, productData: { ...(targetNode?.data as any)?.productData, attr_em: 0 } });
              } else {
                await refreshProductEmission(targetId);
              }
            } catch {
              await refreshProductEmission(targetId);
            }
          }
        } else if (sourceType === 'product' && targetType === 'process') {
          if (sourceId) await refreshProductEmission(sourceId);
          if (targetId) await refreshProcessEmission(targetId);
        }
      } catch (e) {
        console.warn('⚠️ 엣지 삭제 후 새로고침 실패:', e);
      }
    }

    // 엣지 삭제 후 배출량 역전파 및 재계산
    try {
      console.log('🔄 엣지 삭제 후 배출량 역전파 시작');
      
      // 1. 전체 그래프 배출량 재계산 (누적값 리셋 후 재전파)
      await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate, {});
      console.log('✅ 전체 그래프 배출량 재계산 완료');
      
      // 2. 모든 제품 노드 새로고침 (삭제된 연결로 인한 배출량 변경 반영)
      const allProductNodes = prevNodesRef.current.filter(n => n.type === 'product');
      for (const node of allProductNodes) {
        const productId = (node.data as any)?.id;
        if (productId) {
          await refreshProductEmission(productId);
        }
      }
      console.log('✅ 모든 제품 노드 새로고침 완료');
      
      // 3. 모든 공정 노드 새로고침 (삭제된 연결로 인한 배출량 변경 반영)
      const allProcessNodes = prevNodesRef.current.filter(n => n.type === 'process');
      for (const node of allProcessNodes) {
        const processId = (node.data as any)?.id;
        if (processId) {
          await refreshProcessEmission(processId);
        }
      }
      console.log('✅ 모든 공정 노드 새로고침 완료');
      
      console.log('✅ 엣지 삭제 후 배출량 역전파 완료');
    } catch (e) {
      console.warn('⚠️ 엣지 삭제 후 배출량 역전파 실패:', e);
    }
  }, [edges, baseOnEdgesChange, refreshProcessEmission, refreshProductEmission]);

  // 🔧 4방향 연결을 지원하는 Edge 생성 처리
  const handleEdgeCreate = useCallback(async (params: Connection, updateCallback: () => void = () => {}) => {
    let tempEdgeId: string | null = null;
    
    try {
      // ✅ React Flow 공식 문서: 기본 파라미터 검증 강화
      if (!params.source || !params.target) {
        return;
      }
      
      // ✅ 중복 엣지 방지: 이미 존재하는 연결 확인
      const existingEdge = edges.find(edge => 
        edge.source === params.source && 
        edge.target === params.target &&
        edge.sourceHandle === params.sourceHandle &&
        edge.targetHandle === params.targetHandle
      );
      
      if (existingEdge) {
        return;
      }
      
      // Loose 모드에서는 핸들 ID가 선택적이지만, 있으면 사용
      if (!params.sourceHandle || !params.targetHandle) {
        // 핸들 ID가 없어도 연결은 허용하지만, 로깅은 함
      } else {
        // 핸들 ID 확인됨: { sourceHandle: params.sourceHandle, targetHandle: params.targetHandle }
      }
      
      // ✅ React Flow 공식 문서: 임시 Edge 생성으로 사용자 피드백 제공
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
      
      // ✅ 임시 엣지 추가
      setEdges(prev => [...prev, tempEdge]);
      
      // ✅ 실제 DB ID/타입은 노드의 data와 type에서 가져온다
      // 일부 환경에서 params.source/target에 핸들 접미사(-left/-right/-top/-bottom)가 붙는 경우가 있어 정규화
      const normalizeNodeId = (id: string) => id.replace(/-(left|right|top|bottom)$/i, '');
      const sourceNodeId = normalizeNodeId(params.source);
      const targetNodeId = normalizeNodeId(params.target);
      // 항상 최신 스냅샷에서 노드를 찾는다
      const nodesSnapshot = prevNodesRef.current;
      const getNodeByAnyId = (candidateId: string) => {
        return (
          nodesSnapshot.find(n => n.id === candidateId) ||
          nodesSnapshot.find(n => (n.data as any)?.nodeId === candidateId) ||
          nodesSnapshot.find(n => candidateId.startsWith(n.id)) ||
          nodesSnapshot.find(n => candidateId.startsWith(((n.data as any)?.nodeId) || '')) ||
          nodesSnapshot.find(n => n.id.startsWith(candidateId)) ||
          nodesSnapshot.find(n => (((n.data as any)?.nodeId) || '').startsWith(candidateId))
        );
      };

      const sourceNode = getNodeByAnyId(sourceNodeId);
      const targetNode = getNodeByAnyId(targetNodeId);
      let sourceNodeType = sourceNode?.type || 'unknown';
      let targetNodeType = targetNode?.type || 'unknown';
      // 최후 보루: ID 접두사로 타입 추정
      if (sourceNodeType === 'unknown') {
        if (/^process-/i.test(sourceNodeId)) sourceNodeType = 'process';
        if (/^product-/i.test(sourceNodeId)) sourceNodeType = 'product';
      }
      if (targetNodeType === 'unknown') {
        if (/^process-/i.test(targetNodeId)) targetNodeType = 'process';
        if (/^product-/i.test(targetNodeId)) targetNodeType = 'product';
      }
      const sourceId = (sourceNode?.data as any)?.id as number | undefined;
      const targetId = (targetNode?.data as any)?.id as number | undefined;
      
      // 🔴 추가: 노드 타입 검증
      if (sourceNodeType === 'unknown' || targetNodeType === 'unknown') {
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        return; // 초기 드래그 타이밍 이슈 시 조용히 무시
      }
      
      // DB ID 추출: 노드 data.id 우선, 실패 시 타입별 매칭으로 보완
      const ensureDbId = (nodeObj: any, fallbackId: number | undefined) => {
        const idFromData = (nodeObj?.data as any)?.id as number | undefined;
        return idFromData || fallbackId;
      };

      const finalSourceId = ensureDbId(sourceNode, sourceId);
      const finalTargetId = ensureDbId(targetNode, targetId);

      if (!finalSourceId || !finalTargetId) {
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        return; // 조용히 무시하여 첫 연결 알럿 제거
      }
      
      // 🔴 추가: Edge 생성 전 최종 검증
      if (finalSourceId === finalTargetId) {
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        alert('자기 자신과는 연결할 수 없습니다.');
        return;
      }
      
      // Edge 종류 판정
      let resolvedEdgeKind: string = 'continue';
      if (sourceNodeType === 'process' && targetNodeType === 'process') {
        resolvedEdgeKind = 'continue';
      } else if (sourceNodeType === 'process' && targetNodeType === 'product') {
        resolvedEdgeKind = 'produce';
      } else if (sourceNodeType === 'product' && targetNodeType === 'process') {
        resolvedEdgeKind = 'consume';
      } else {
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        alert('지원되지 않는 연결 유형입니다. 제품↔공정 또는 공정↔공정만 연결할 수 있습니다.');
        return;
      }

      // 엣지 생성 전에 필요한 배출량을 미리 계산하여 전파 실패 방지
      try {
        if (resolvedEdgeKind === 'continue') {
          await Promise.all([
            ensureProcessAttrdirComputed(finalSourceId),
            ensureProcessAttrdirComputed(finalTargetId)
          ]);
        } else if (resolvedEdgeKind === 'produce') {
          await ensureProcessAttrdirComputed(finalSourceId);
        } else if (resolvedEdgeKind === 'consume') {
          await ensureProcessAttrdirComputed(finalTargetId);
        }
      } catch (precalcErr) {
        console.warn('⚠️ 전처리(배출량 계산) 실패:', precalcErr);
      }

      // 백엔드에 Edge 생성 요청
      const edgeData = {
        source_node_type: sourceNodeType,
        source_id: finalSourceId,
        target_node_type: targetNodeType,
        target_id: finalTargetId,
        edge_kind: resolvedEdgeKind
      };
      
      const response = await axiosClient.post(apiEndpoints.cbam.edge.create, edgeData);
      
      if (response.status === 201) {
        const newEdge = response.data;
        
        // ✅ React Flow 공식 문서: 임시 Edge를 실제 Edge로 교체
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
        if (updateCallback) {
          updateCallback();
        }

        // 배출량 전파 및 영향 노드 갱신 (edge_kind별 분기)
        try {
          if (edgeData.edge_kind === 'continue') {
            await axiosClient.post(
              apiEndpoints.cbam.edgePropagation.continue,
              null,
              { params: { source_process_id: finalSourceId, target_process_id: finalTargetId } }
            );
            // 1) 전체 전파 → 2) 소스 갱신 → 3) 타겟 갱신 → 4) 타겟이 생산하는 제품 프리뷰 갱신(순차)
            if (shouldRunFullPropagate()) {
              try { await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate, {}); } catch (e) { console.warn('⚠️ 전체 전파 실패:', e); }
            }
            await refreshProcessEmission(finalSourceId);
            await refreshProcessEmission(finalTargetId);
            try {
              const productIds = (prevNodesRef.current || [])
                .filter(n => n.type === 'product' && (n.data as any)?.id)
                .map(n => (n.data as any).id as number);
              for (const id of productIds) { await refreshProductEmission(id); }
            } catch (_) {}
          } else if (edgeData.edge_kind === 'produce') {
            // 공정→제품: 제품 생산 시 배출량이 제품에 누적됨
            if (shouldRunFullPropagate()) {
              try { await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate, {}); } catch (e) { console.warn('⚠️ 전체 전파 실패:', e); }
            }
            await refreshProcessEmission(finalSourceId);
            await refreshProductEmission(finalTargetId);
            setProductProduceFlag(finalTargetId, true);
            
            // 제품 노드에 has_produce_edge 플래그 설정 (제품이 생산되었음을 표시)
            setNodes(prev => prev.map(node => {
              if (node.type === 'product' && (node.data as any)?.id === finalTargetId) {
                return {
                  ...node,
                  data: {
                    ...node.data,
                    has_produce_edge: true
                  }
                } as Node;
              }
              return node;
            }));
          } else if (edgeData.edge_kind === 'consume') {
            // 제품→공정: 전용 전파 API로 즉시 누적 반영 후, 전체 전파로 일관성 확보
            try {
              await axiosClient.post(
                apiEndpoints.cbam.edgePropagation.consume,
                null,
                { params: { source_product_id: finalSourceId, target_process_id: finalTargetId } }
              );
              // 전용 전파 직후 1차 반영 확인
              await refreshProcessEmission(finalTargetId);
            } catch (e) {
              console.warn('⚠️ consume 전파 실패, 전체 전파로 폴백:', e);
            }
            if (shouldRunFullPropagate()) {
              try { await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate, {}); } catch (e) { console.warn('⚠️ 전체 전파 실패:', e); }
            }
            // 제품이 다른 공정들과 연결되었으므로 배출량 새로고침
            await refreshProductEmission(finalSourceId);
            await refreshProcessEmission(finalTargetId);

            // 타겟 공정(예: 압연)이 생산하는 제품들(예: 형강)도 프리뷰 갱신(순차)
            // 연결이 새로 생성되었으므로 모든 생산 제품들을 새로고침
            try {
              const normalize = (id?: string) => (id || '').replace(/-(left|right|top|bottom)$/i, '');
              const processNode = (prevNodesRef.current || []).find(n => n.type === 'process' && (n.data as any)?.id === finalTargetId);
              if (processNode) {
                const producedProductIds: number[] = (edges || [])
                  .filter(e => normalize(e.source) === processNode.id && (e.data as any)?.edgeData?.edge_kind === 'produce')
                  .map(e => {
                    const targetNode = (prevNodesRef.current || []).find(n => n.id === e.target);
                    const pid = (targetNode?.data as any)?.id;
                    return typeof pid === 'number' ? pid : undefined;
                  })
                  .filter((pid): pid is number => typeof pid === 'number');
                
                // 연결이 새로 생성되었으므로 모든 생산 제품들을 새로고침
                for (const pid of producedProductIds) { 
                  await refreshProductEmission(pid);
                  console.log(`✅ 제품 ${pid} 배출량 새로고침 완료 (consume 엣지 생성으로 인한 영향)`);
                }
              }
            } catch (e) {
              console.warn('⚠️ 생산 제품 배출량 새로고침 실패:', e);
            }
            
            // consume 엣지 생성 후 전체 그래프 일관성 확보를 위한 추가 새로고침
            try {
              console.log('🔄 consume 엣지 생성으로 인한 전체 그래프 일관성 확보 시작');
              
              // 모든 제품 노드 새로고침 (연결 변경으로 인한 배출량 변경 반영)
              const allProductNodes = prevNodesRef.current.filter(n => n.type === 'product');
              for (const node of allProductNodes) {
                const productId = (node.data as any)?.id;
                if (productId) {
                  await refreshProductEmission(productId);
                }
              }
              console.log('✅ 모든 제품 노드 새로고침 완료');
              
              // 모든 공정 노드 새로고침 (연결 변경으로 인한 배출량 변경 반영)
              const allProcessNodes = prevNodesRef.current.filter(n => n.type === 'process');
              for (const node of allProcessNodes) {
                const processId = (node.data as any)?.id;
                if (processId) {
                  await refreshProcessEmission(processId);
                }
              }
              console.log('✅ 모든 공정 노드 새로고침 완료');
              
              console.log('✅ consume 엣지 생성으로 인한 전체 그래프 일관성 확보 완료');
            } catch (e) {
              console.warn('⚠️ 전체 그래프 일관성 확보 실패:', e);
            }
          }
        } catch (e) {
          console.error('⚠️ 배출량 전파/갱신 실패:', e);
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
      
      // ✅ React Flow 공식 문서: 에러 발생 시 임시 Edge 제거
      if (tempEdgeId) {
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
      }
      
      // 🔴 추가: 사용자에게 에러 알림
      let errorMessage = 'Edge 생성에 실패했습니다.';
      
      if (error.response?.status === 500) {
        console.error('🔴 서버 내부 오류 - Edge 생성 실패');
        errorMessage = '서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
      } else if (error.response?.status === 400) {
        console.error('🔴 잘못된 요청 - Edge 데이터 검증 실패');
        errorMessage = '잘못된 연결 정보입니다. 노드를 다시 선택해주세요.';
      } else if (error.code === 'NETWORK_ERROR') {
        console.error('🔴 네트워크 오류 - 서버 연결 실패');
        errorMessage = '네트워크 연결을 확인해주세요.';
      } else {
        console.error('🔴 알 수 없는 오류:', error);
        errorMessage = '알 수 없는 오류가 발생했습니다.';
      }
      
      // 🔴 추가: 사용자에게 에러 메시지 표시
      alert(errorMessage);
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
    updateNodeData,
    // 노출: 부분 새로고침/재계산 유틸
    refreshProcessEmission,
    refreshProductEmission,
    recalcFromProcess,
    refreshAllNodesAfterProductUpdate,
  };
};

// ============================================================================
// 🔍 유효성 검증 함수들
// ============================================================================

export const validateEdgeConnection = (sourceId: string, targetId: string, sourceType: string, targetType: string) => {
  // 1. 동일 노드 간 연결 방지
  if (sourceId === targetId) {
    return { valid: false, error: '동일한 노드 간 연결은 허용되지 않습니다.' };
  }

  // 2. 제품-제품 연결 방지
  if (sourceType === 'product' && targetType === 'product') {
    return { valid: false, error: '제품 간 직접 연결은 허용되지 않습니다.' };
  }

  // 3. 유효한 연결 규칙 검증
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