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

  // 노드 데이터 업데이트
  const updateNodeData = useCallback((nodeId: string, newData: any) => {
    setNodes(prev => prev.map(node => 
      node.id === nodeId 
        ? { ...node, data: { ...node.data, ...newData } }
        : node
    ));
  }, [setNodes]);

  // 엣지 연결 여부에 따라 노드의 배출량 표시 토글
  useEffect(() => {
    const matchId = (nodeId: string, edgeEndId: string, nodeDataId?: string) => {
      if (!nodeId || !edgeEndId) return false;
      const norm = (id: string) => id.replace(/-(left|right|top|bottom)$/i, '');
      const a = norm(nodeId);
      const b = norm(edgeEndId);
      const c = nodeDataId ? norm(String(nodeDataId)) : '';
      return a === b || a.startsWith(b) || b.startsWith(a) || a === c || c === b;
    };
    setNodes(prev => prev.map(n => {
      const nodeDataId = (n.data as any)?.nodeId || (n.data as any)?.id;
      const connected = edges.some(e => matchId(n.id, e.source, nodeDataId) || matchId(n.id, e.target, nodeDataId));
      return {
        ...n,
        data: {
          ...n.data,
          showEmissions: connected
        }
      } as Node;
    }));
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
        const response = await axiosClient.get(apiEndpoints.cbam.calculation.process.attrdir(processId));
        data = response?.data;
      } catch (err: any) {
        if (err?.response?.status === 404) {
          try {
            const created = await axiosClient.post(apiEndpoints.cbam.calculation.process.attrdir(processId));
            data = created?.data;
          } catch (calcErr) {
            console.warn('⚠️ 공정 배출량 계산 실패:', calcErr);
            return;
          }
        } else {
          throw err;
        }
      }
      if (!data) return;
      const emissionData = {
        attr_em: data.attrdir_em || 0,
        total_matdir_emission: data.total_matdir_emission || 0,
        total_fueldir_emission: data.total_fueldir_emission || 0,
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

  // 특정 제품 노드만 배출량 정보 새로고침
  const refreshProductEmission = useCallback(async (productId: number) => {
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.product.get(productId));
      const product = response?.data;
      if (!product) return;
      const attrEm = product?.attr_em || 0;
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
      const getNodeByAnyId = (candidateId: string) => {
        return (
          nodes.find(n => n.id === candidateId) ||
          nodes.find(n => (n.data as any)?.nodeId === candidateId) ||
          nodes.find(n => candidateId.startsWith(n.id)) ||
          nodes.find(n => candidateId.startsWith(((n.data as any)?.nodeId) || '')) ||
          nodes.find(n => n.id.startsWith(candidateId)) ||
          nodes.find(n => (((n.data as any)?.nodeId) || '').startsWith(candidateId))
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
        console.error('❌ 유효하지 않은 노드 타입:', { sourceNodeType, targetNodeType });
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        
        // 🔴 추가: 사용자에게 오류 알림
        alert('연결할 수 없는 노드 타입입니다. 노드를 다시 선택해주세요.');
        return;
      }
      
      // DB ID 추출: 노드 data.id 우선, 실패 시 타입별 매칭으로 보완
      const ensureDbId = (nodeObj: any, fallbackId: number | undefined) => {
        const idFromData = (nodeObj?.data as any)?.id as number | undefined;
        return idFromData || fallbackId;
      };

      const finalSourceId = ensureDbId(sourceNode, sourceId);
      const finalTargetId = ensureDbId(targetNode, targetId);

      if (!finalSourceId || !finalTargetId) {
        console.error('❌ 유효하지 않은 DB ID:', { sourceId, targetId, source: params.source, target: params.target });
        setEdges(prev => prev.filter(edge => edge.id !== tempEdgeId));
        
        // 🔴 추가: 사용자에게 오류 알림
        alert('연결할 수 없는 노드입니다. 노드를 다시 선택해주세요.');
        return;
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
              { params: { source_process_id: sourceId, target_process_id: targetId } }
            );
            await Promise.all([
              refreshProcessEmission(finalSourceId),
              refreshProcessEmission(finalTargetId)
            ]);
          } else if (edgeData.edge_kind === 'produce') {
            // 공정→제품: 제품 배출량 재계산 및 노드 갱신
            try {
              const recalc = await axiosClient.post(apiEndpoints.cbam.calculation.graph.recalc, {
                trigger_edge_id: newEdge.id,
                recalculate_all: false,
                include_validation: false
              });
              console.log('🔄 그래프 부분 재계산:', recalc.data);
            } catch (e) {
              console.warn('⚠️ 그래프 재계산 실패(무시 가능):', e);
            }
            await Promise.all([
              refreshProcessEmission(finalSourceId),
              refreshProductEmission(finalTargetId)
            ]);
          } else if (edgeData.edge_kind === 'consume') {
            // 제품→공정: 타겟 공정 갱신
            try {
              const recalc = await axiosClient.post(apiEndpoints.cbam.calculation.graph.recalc, {
                trigger_edge_id: newEdge.id,
                recalculate_all: false,
                include_validation: false
              });
              console.log('🔄 그래프 부분 재계산:', recalc.data);
            } catch (e) {
              console.warn('⚠️ 그래프 재계산 실패(무시 가능):', e);
            }
            await Promise.all([
              refreshProductEmission(finalSourceId),
              refreshProcessEmission(finalTargetId)
            ]);
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
  };
};
