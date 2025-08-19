'use client';

import React, { useState, useEffect } from 'react';
import ProcessFlowEditor from '@/components/templates/ProcessFlowEditor';
import { useProcessFlowService } from '@/hooks/useProcessFlowAPI';
import type { AppNodeType, AppEdgeType } from '@/types/reactFlow';

export default function ReactFlowTestPage() {
  const [currentFlowId, setCurrentFlowId] = useState<string | null>(null);
  const [nodes, setNodes] = useState<AppNodeType[]>([]);
  const [edges, setEdges] = useState<AppEdgeType[]>([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<string>('');

  const { 
    saveReactFlowToBackend, 
    loadReactFlowFromBackend, 
    checkServiceStatus,
    syncReactFlowChanges 
  } = useProcessFlowService();

  // 컴포넌트 마운트 시 MSA 서비스 상태 확인
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await checkServiceStatus();
        if (status?.status === 'healthy') {
          setMessage('✅ MSA 백엔드 서비스가 정상적으로 연결되었습니다!');
        } else {
          setMessage('⚠️ MSA 백엔드 서비스 연결에 문제가 있습니다.');
        }
      } catch (error) {
        setMessage('❌ MSA 백엔드 서비스에 연결할 수 없습니다.');
        console.error('서비스 상태 확인 실패:', error);
      }
    };

    checkStatus();
  }, [checkServiceStatus]);

  // 샘플 React Flow 생성
  const createSampleFlow = async () => {
    setLoading(true);
    try {
      const sampleNodes: AppNodeType[] = [
        {
          id: 'node_1',
          type: 'processNode',
          position: { x: 100, y: 100 },
          data: { 
            label: '시작 노드',
            description: 'React Flow MSA 테스트용 시작 노드',
            processType: 'start'
          },
          draggable: true,
          selectable: true,
          deletable: true
        },
        {
          id: 'node_2', 
          type: 'processNode',
          position: { x: 300, y: 100 },
          data: { 
            label: '처리 노드',
            description: 'React Flow MSA 테스트용 처리 노드',
            processType: 'process'
          },
          draggable: true,
          selectable: true,
          deletable: true
        }
      ];

      const sampleEdges: AppEdgeType[] = [
        {
          id: 'edge_1',
          source: 'node_1',
          target: 'node_2',
          type: 'processEdge',
          data: {
            label: '테스트 연결',
            processType: 'standard'
          }
        }
      ];

      // MSA 백엔드에 React Flow 저장
      const result = await saveReactFlowToBackend(sampleNodes, sampleEdges, 'React Flow MSA 테스트');
      
      if (result.success) {
        // 프론트엔드 상태 업데이트
        setNodes(sampleNodes);
        setEdges(sampleEdges);
        setCurrentFlowId(result.flowId || null);
        
        setMessage('✅ 샘플 React Flow가 성공적으로 생성되고 MSA 백엔드에 저장되었습니다!');
      } else {
        setMessage('❌ 샘플 Flow 저장에 실패했습니다.');
      }
    } catch (error) {
      console.error('샘플 Flow 생성 실패:', error);
      setMessage('❌ 샘플 Flow 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // MSA 백엔드에서 React Flow 로드
  const loadFlowFromBackend = async () => {
    setLoading(true);
    try {
      const flowData = await loadReactFlowFromBackend();
      
      if (flowData) {
        setNodes(flowData.nodes);
        setEdges(flowData.edges);
        setCurrentFlowId(flowData.metadata?.flow?.id || null);
        setMessage('✅ MSA 백엔드에서 React Flow를 성공적으로 로드했습니다!');
      } else {
        setMessage('⚠️ 로드할 React Flow가 없습니다.');
      }
    } catch (error) {
      console.error('Flow 로드 실패:', error);
      setMessage('❌ React Flow 로드에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // React Flow 변경 핸들러 (MSA 실시간 동기화)
  const handleFlowChange = async (newNodes: AppNodeType[], newEdges: AppEdgeType[]) => {
    setNodes(newNodes);
    setEdges(newEdges);
    
    // MSA 실시간 동기화
    if (currentFlowId) {
      try {
        await syncReactFlowChanges(currentFlowId, newNodes, newEdges);
        console.log('🔄 MSA 실시간 동기화 완료');
      } catch (error) {
        console.warn('⚠️ MSA 실시간 동기화 실패:', error);
      }
    }
    
    console.log('🔄 React Flow 변경:', { nodes: newNodes.length, edges: newEdges.length });
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* 헤더 */}
      <div className="bg-gray-800 p-4 border-b border-gray-700">
        <h1 className="text-2xl font-bold mb-4">🔄 React Flow + MSA 백엔드 연동 테스트</h1>
        
        {/* 상태 메시지 */}
        <div className="mb-4 p-3 rounded-lg bg-gray-700">
          <p className="text-sm">{message}</p>
        </div>

        {/* 컨트롤 버튼들 */}
        <div className="flex gap-3 flex-wrap">
          <button
            onClick={createSampleFlow}
            disabled={loading}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 rounded-lg text-sm"
          >
            🌊 샘플 React Flow 생성
          </button>
          
          <button
            onClick={loadFlowFromBackend}
            disabled={loading}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg text-sm"
          >
            📥 MSA 백엔드에서 로드
          </button>
          
          {currentFlowId && (
            <span className="px-3 py-2 bg-gray-700 rounded-lg text-sm">
              Flow ID: <strong>{currentFlowId.substring(0, 8)}...</strong>
            </span>
          )}
          
          {loading && (
            <span className="px-3 py-2 bg-yellow-600 rounded-lg text-sm">
              🔄 처리 중...
            </span>
          )}
        </div>
      </div>

      {/* React Flow 에디터 (MSA 동기화) */}
      <div className="h-[calc(100vh-140px)]">
        <ProcessFlowEditor
          initialNodes={nodes}
          initialEdges={edges}
          onFlowChange={handleFlowChange}
          readOnly={false}
          flowId={currentFlowId || undefined}
        />
      </div>

      {/* 상태 정보 */}
      <div className="bg-gray-800 p-3 border-t border-gray-700 text-sm text-gray-300">
        📊 현재 상태: 노드 {nodes.length}개, 엣지 {edges.length}개
        {currentFlowId && ` | MSA 실시간 동기화: ON`}
        {!currentFlowId && ` | MSA 동기화: OFF (Flow ID 없음)`}
      </div>
    </div>
  );
}