import { useCallback } from 'react';
import { Edge, Connection, EdgeChange } from '@xyflow/react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';

/**
 * 엣지 관리 전용 훅
 * 단일 책임: 엣지 생성, 삭제, 전파, 유효성 검증만 담당
 */
export const useEdgeManager = () => {

  // 엣지 연결 유효성 검증
  const validateEdgeConnection = useCallback((
    sourceId: string, 
    targetId: string, 
    sourceType: string, 
    targetType: string
  ) => {
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
  }, []);

  // 엣지 종류 판정
  const determineEdgeKind = useCallback((sourceType: string, targetType: string): string => {
    if (sourceType === 'process' && targetType === 'process') {
      return 'continue';
    } else if (sourceType === 'process' && targetType === 'product') {
      return 'produce';
    } else if (sourceType === 'product' && targetType === 'process') {
      return 'consume';
    }
    return 'continue'; // 기본값
  }, []);

  // 엣지 생성
  const createEdge = useCallback(async (edgeData: {
    source_node_type: string;
    source_id: number;
    target_node_type: string;
    target_id: number;
    edge_kind: string;
  }): Promise<any> => {
    try {
      const response = await axiosClient.post(apiEndpoints.cbam.edge.create, edgeData);
      
      if (response.status === 201) {
        console.log(`✅ 엣지 생성 성공: ${edgeData.source_id} → ${edgeData.target_id} (${edgeData.edge_kind})`);
        return response.data;
      }
      
      throw new Error(`엣지 생성 실패: ${response.status}`);
    } catch (error: any) {
      console.error('❌ 엣지 생성 실패:', {
        error: error,
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        edgeData: edgeData
      });
      throw error;
    }
  }, []);

  // 엣지 삭제
  const deleteEdge = useCallback(async (edgeId: number): Promise<boolean> => {
    try {
      await axiosClient.delete(apiEndpoints.cbam.edge.delete(edgeId));
      console.log(`✅ 엣지 삭제 성공: ID ${edgeId}`);
      return true;
    } catch (error) {
      console.warn('⚠️ 엣지 삭제 실패:', error);
      return false;
    }
  }, []);

  // 배출량 전파 실행
  const propagateEmission = useCallback(async (
    edgeKind: string,
    sourceId: number,
    targetId: number
  ): Promise<boolean> => {
    try {
      if (edgeKind === 'continue') {
        await axiosClient.post(
          apiEndpoints.cbam.edgePropagation.continue,
          null,
          { params: { source_process_id: sourceId, target_process_id: targetId } }
        );
      } else if (edgeKind === 'consume') {
        await axiosClient.post(
          apiEndpoints.cbam.edgePropagation.consume,
          null,
          { params: { source_product_id: sourceId, target_process_id: targetId } }
        );
      }
      // produce는 별도 전파 없음 (제품 배출량은 실시간 계산)
      
      console.log(`✅ ${edgeKind} 전파 완료: ${sourceId} → ${targetId}`);
      return true;
    } catch (e) {
      console.warn(`⚠️ ${edgeKind} 전파 실패:`, e);
      return false;
    }
  }, []);

  // 엣지 삭제 후 처리
  const handleEdgeDeletion = useCallback(async (removedEdges: Edge[]): Promise<void> => {
    try {
      console.log('🔄 엣지 삭제 후 처리 시작');
      
      // 백엔드에서 엣지 삭제
      for (const edge of removedEdges) {
        const m = /^e-(\d+)/.exec(edge.id);
        if (m) {
          const edgeId = parseInt(m[1], 10);
          await deleteEdge(edgeId);
        }
      }

      // 즉시 전체 그래프 재계산 (대기 시간 단축)
      await new Promise(resolve => setTimeout(resolve, 100));
      
      console.log('✅ 엣지 삭제 후 처리 완료');
    } catch (e) {
      console.warn('⚠️ 엣지 삭제 후 처리 실패:', e);
    }
  }, [deleteEdge]);

  return {
    validateEdgeConnection,
    determineEdgeKind,
    createEdge,
    deleteEdge,
    propagateEmission,
    handleEdgeDeletion,
  };
};
