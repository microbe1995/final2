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

  // 최신 nodes 스냅샷을 ref에 유지하여 콜백에서 stale closure 방지
  useEffect(() => {
    prevNodesRef.current = nodes;
  }, [nodes]);

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
      console.log(`⚠️ 공정 ${process.id}의 배출량 정보가 아직 없습니다.`);
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
          product_names: relatedProducts.map(p => p.product_name).join(', ') || 'N/A',
          is_many_to_many: relatedProducts.length > 1,
          install_id: (process as any).install_id,
          current_install_id: selectedInstall?.id,
          is_readonly: (process as any).install_id !== selectedInstall?.id,
          // 배출량 정보 추가
          ...emissionData
        },
        onMatDirClick: (processData: any) => openInputModal(processData),
        // 🔴 추가: ProcessNode가 기대하는 추가 데이터
        size: 'md',
        showHandles: true,
      },
    };

    console.log('🔍 공정 노드 생성:', newNode); // 🔴 추가: 디버깅 로그

    // setNodes를 사용하여 안전하게 노드 추가
    setNodes(prev => {
      const newNodes = [...prev, newNode];
      prevNodesRef.current = newNodes;
      console.log('🔍 노드 상태 업데이트:', newNodes); // 🔴 추가: 디버깅 로그
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

  // 특정 공정 노드만 배출량 정보 새로고침
  const refreshProcessEmission = useCallback(async (processId: number) => {
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
      const totalMat = Number(data.total_matdir_emission ?? data.total_matdir ?? 0) || 0;
      const totalFuel = Number(data.total_fueldir_emission ?? data.total_fueldir ?? 0) || 0;
      const sumDirect = totalMat + totalFuel;
      const directFromDb = Number(data.attrdir_em ?? data.attrdir_emission ?? 0) || 0;
      const directFixed = sumDirect > 0 ? sumDirect : directFromDb;

      // 백그라운드 보정: DB의 attrdir_em이 합계와 다르면 재계산 트리거
      if (sumDirect > 0 && Math.abs(directFromDb - sumDirect) > 1e-6) {
        axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(processId)).catch(() => {});
      }

      const emissionData = {
        attr_em: directFixed,
        cumulative_emission: data.cumulative_emission || 0,
        total_matdir_emission: totalMat,
        total_fueldir_emission: totalFuel,
        calculation_date: data.calculation_date
      };
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
    } catch (e) {
      console.error('⚠️ 공정 배출량 새로고침 실패:', e);
    }
  }, [setNodes]);

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
    try {
      let attrEm = 0;
      try {
        const preview = await axiosClient.get(apiEndpoints.cbam.edgePropagation.productPreview(productId));
        attrEm = preview?.data?.preview_attr_em ?? 0;
      } catch {
        const response = await axiosClient.get(apiEndpoints.cbam.product.get(productId));
        const product = response?.data;
        attrEm = product?.attr_em || 0;
      }
      setNodes(prev => prev.map(node => {
        if (node.type === 'product' && node.data?.id === productId) {
          return {
            ...node,
            data: {
              ...node.data,
              attr_em: attrEm,
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
    } catch (e) {
      console.error('⚠️ 제품 배출량 새로고침 실패:', e);
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

    // 엣지 삭제 후 누적값을 원상 복구시키기 위해 서버에 전체 재계산을 요청
    // (모든 공정의 cumulative_emission을 0으로 리셋 후 현재 그래프 기준으로 재전파)
    try {
      await axiosClient.post(apiEndpoints.cbam.edgePropagation.recalcFromEdges, {});
    } catch (e) {
      console.warn('⚠️ 엣지 삭제 후 재계산 트리거 실패(무시 가능):', e);
    }
  }, [edges, baseOnEdgesChange, refreshProcessEmission, refreshProductEmission]);

  // 🔧 4방향 연결을 지원하는 Edge 생성 처리
  const handleEdgeCreate = useCallback(async (params: Connection, updateCallback: () => void = () => {}) => {
    let tempEdgeId: string | null = null;
    
    try {
      console.log('🔗 Edge 연결 시도:', params);
      
      // ✅ React Flow 공식 문서: 기본 파라미터 검증 강화
      if (!params.source || !params.target) {
        console.log('❌ source 또는 target이 없음:', params);
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
        console.log('❌ 이미 존재하는 연결:', existingEdge);
        return;
      }
      
      // Loose 모드에서는 핸들 ID가 선택적이지만, 있으면 사용
      if (!params.sourceHandle || !params.targetHandle) {
        console.log('⚠️ 핸들 ID 없음 (Loose 모드에서는 허용):', params);
        // 핸들 ID가 없어도 연결은 허용하지만, 로깅은 함
      } else {
        console.log('✅ 핸들 ID 확인됨:', {
          sourceHandle: params.sourceHandle,
          targetHandle: params.targetHandle
        });
      }
      
      console.log('🔧 4방향 연결 핸들 ID:', {
        sourceHandle: params.sourceHandle,
        targetHandle: params.targetHandle
      });
      
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
      console.log('🔗 임시 Edge 추가됨:', tempEdgeId);
      
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
      
      console.log('🔍 추출된 정보:', {
        source: sourceNodeId,
        target: targetNodeId,
        sourceId,
        targetId,
        sourceNodeType,
        targetNodeType
      });
      
      // 🔴 추가: 노드 타입 검증
      if (sourceNodeType === 'unknown' || targetNodeType === 'unknown') {
        console.warn('❌ 유효하지 않은 노드 타입:', { sourceNodeType, targetNodeType });
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
        console.warn('❌ 유효하지 않은 DB ID:', { sourceId, targetId, source: params.source, target: params.target });
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        return; // 조용히 무시하여 첫 연결 알럿 제거
      }
      
      // 🔴 추가: Edge 생성 전 최종 검증
      if (finalSourceId === finalTargetId) {
        console.error('❌ 자기 자신과는 연결할 수 없습니다.');
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
        console.error('❌ 지원되지 않는 연결 유형입니다:', { sourceNodeType, targetNodeType });
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
      
      console.log('🔗 Edge 생성 요청:', edgeData);
      
      const response = await axiosClient.post(apiEndpoints.cbam.edge.create, edgeData);
      
      if (response.status === 201) {
        const newEdge = response.data;
        console.log('✅ Edge 생성 성공:', newEdge);
        
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
            try { await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate, {}); } catch (e) { console.warn('⚠️ 전체 전파 실패:', e); }
            await refreshProcessEmission(finalSourceId);
            await refreshProcessEmission(finalTargetId);
            try {
              const productIds = (prevNodesRef.current || [])
                .filter(n => n.type === 'product' && (n.data as any)?.id)
                .map(n => (n.data as any).id as number);
              for (const id of productIds) { await refreshProductEmission(id); }
            } catch (_) {}
          } else if (edgeData.edge_kind === 'produce') {
            // 공정→제품: 누적을 확정 후 제품 프리뷰를 직렬로 갱신
            try { await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate, {}); } catch (e) { console.warn('⚠️ 전체 전파 실패:', e); }
            await refreshProcessEmission(finalSourceId);
            await refreshProductEmission(finalTargetId);
            setProductProduceFlag(finalTargetId, true);
          } else if (edgeData.edge_kind === 'consume') {
            // 제품→공정: 전체 전파 후 타겟 공정 누적을 먼저 갱신, 이후 해당 공정이 생산하는 제품을 마지막에 갱신(레이스 방지)
            try { await axiosClient.post(apiEndpoints.cbam.edgePropagation.fullPropagate, {}); } catch (e) { console.warn('⚠️ 전체 전파 실패:', e); }
            await refreshProductEmission(finalSourceId);
            await refreshProcessEmission(finalTargetId);

            // 타겟 공정(예: 압연)이 생산하는 제품들(예: 형강)도 프리뷰 갱신(순차)
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
                for (const pid of producedProductIds) { await refreshProductEmission(pid); }
              }
            } catch (_) {}
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
  };
};
