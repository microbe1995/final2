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
    saveToBackend, 
    loadFromBackend, 
    checkServiceStatus,
    createNode 
  } = useProcessFlowService();

  // 컴포넌트 마운트 시 서비스 상태 확인
  useEffect(() => {
    const checkStatus = async () => {
      try {
        const status = await checkServiceStatus();
        if (status?.status === 'healthy') {
          setMessage('✅ 백엔드 서비스가 정상적으로 연결되었습니다!');
        } else {
          setMessage('⚠️ 백엔드 서비스 연결에 문제가 있습니다.');
        }
      } catch (error) {
        setMessage('❌ 백엔드 서비스에 연결할 수 없습니다.');
        console.error('서비스 상태 확인 실패:', error);
      }
    };

    checkStatus();
  }, [checkServiceStatus]);

  // 샘플 플로우 생성
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
            description: 'ReactFlow 테스트용 시작 노드',
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
            description: 'ReactFlow 테스트용 처리 노드',
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

      // 백엔드에 저장
      await saveToBackend(sampleNodes, sampleEdges, 'ReactFlow 테스트 플로우');
      
      // 프론트엔드 상태 업데이트
      setNodes(sampleNodes);
      setEdges(sampleEdges);
      
      setMessage('✅ 샘플 플로우가 성공적으로 생성되고 백엔드에 저장되었습니다!');
    } catch (error) {
      console.error('샘플 플로우 생성 실패:', error);
      setMessage('❌ 샘플 플로우 생성에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 백엔드에서 플로우 로드
  const loadFlowFromBackend = async () => {
    setLoading(true);
    try {
      const flowData = await loadFromBackend();
      
      if (flowData) {
        setNodes(flowData.nodes);
        setEdges(flowData.edges);
        setCurrentFlowId(flowData.metadata?.flow?.id || null);
        setMessage('✅ 백엔드에서 플로우를 성공적으로 로드했습니다!');
      } else {
        setMessage('⚠️ 로드할 플로우가 없습니다.');
      }
    } catch (error) {
      console.error('플로우 로드 실패:', error);
      setMessage('❌ 플로우 로드에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 새 노드 추가
  const addNewNode = async () => {
    if (!currentFlowId) {
      setMessage('⚠️ 먼저 플로우를 생성하거나 로드해주세요.');
      return;
    }

    setLoading(true);
    try {
      const newNodeData = {
        type: 'processNode',
        position: { 
          x: Math.random() * 400, 
          y: Math.random() * 300 
        },
        data: {
          label: `새 노드 ${nodes.length + 1}`,
          description: '동적으로 추가된 노드',
          processType: 'dynamic'
        },
        draggable: true,
        selectable: true,
        deletable: true
      };

      // 백엔드에 노드 생성
      const createdNode = await createNode(currentFlowId, newNodeData);
      
      // 프론트엔드 상태 업데이트
      const newNode: AppNodeType = {
        id: createdNode.id,
        type: createdNode.type,
        position: createdNode.position,
        data: createdNode.data,
        draggable: createdNode.draggable,
        selectable: createdNode.selectable,
        deletable: createdNode.deletable
      };
      
      setNodes(prev => [...prev, newNode]);
      setMessage('✅ 새 노드가 백엔드에 생성되고 화면에 추가되었습니다!');
    } catch (error) {
      console.error('노드 추가 실패:', error);
      setMessage('❌ 노드 추가에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 플로우 변경 핸들러
  const handleFlowChange = (newNodes: AppNodeType[], newEdges: AppEdgeType[]) => {
    setNodes(newNodes);
    setEdges(newEdges);
    console.log('🔄 플로우 변경:', { nodes: newNodes.length, edges: newEdges.length });
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* 헤더 */}
      <div className="bg-gray-800 p-4 border-b border-gray-700">
        <h1 className="text-2xl font-bold mb-4">🔄 ReactFlow + FastAPI 백엔드 연동 테스트</h1>
        
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
            🌊 샘플 플로우 생성
          </button>
          
          <button
            onClick={loadFlowFromBackend}
            disabled={loading}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 rounded-lg text-sm"
          >
            📥 백엔드에서 로드
          </button>
          
          <button
            onClick={addNewNode}
            disabled={loading || !currentFlowId}
            className="px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 rounded-lg text-sm"
          >
            🔵 노드 추가
          </button>
          
          {currentFlowId && (
            <span className="px-3 py-2 bg-gray-700 rounded-lg text-sm">
              플로우 ID: <strong>{currentFlowId}</strong>
            </span>
          )}
          
          {loading && (
            <span className="px-3 py-2 bg-yellow-600 rounded-lg text-sm">
              🔄 처리 중...
            </span>
          )}
        </div>
      </div>

      {/* ReactFlow 에디터 */}
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
        {currentFlowId && ` | 백엔드 동기화: ON`}
        {!currentFlowId && ` | 백엔드 동기화: OFF (플로우 ID 없음)`}
      </div>
    </div>
  );
}
