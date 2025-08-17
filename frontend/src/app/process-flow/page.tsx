'use client';

import React, { useState, useCallback } from 'react';
import ProcessFlowEditor from '@/templates/ProcessFlowEditor';
import ProcessFlowInfoPanel from '@/organisms/ProcessFlowInfoPanel';
import { Node, Edge } from '@xyflow/react';
import axios from 'axios';

// ============================================================================
// 🔗 API 설정
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080';

// API 클라이언트 설정
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 응답 인터셉터 - 에러 처리
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API 호출 실패:', error);
    return Promise.reject(error);
  }
);

// ============================================================================
// 🎯 Process Flow 페이지 컴포넌트
// ============================================================================

export default function ProcessFlowPage() {
  const [nodes, setNodes] = useState<Node<any>[]>([]);
  const [edges, setEdges] = useState<Edge<any>[]>([]);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState<Node<any>[]>([]);
  const [selectedEdges, setSelectedEdges] = useState<Edge<any>[]>([]);
  
  // 백엔드 관련 상태
  const [savedCanvases, setSavedCanvases] = useState<any[]>([]);
  const [isLoadingCanvases, setIsLoadingCanvases] = useState(false);
  const [serviceStatus, setServiceStatus] = useState<any>(null);

  // ============================================================================
  // 🔄 이벤트 핸들러
  // ============================================================================

  const handleFlowChange = useCallback((newNodes: Node[], newEdges: Edge[]) => {
    setNodes(newNodes);
    setEdges(newEdges);
    
    // 선택된 요소들 업데이트
    setSelectedNodes(newNodes.filter(node => node.selected));
    setSelectedEdges(newEdges.filter(edge => edge.selected));
  }, []);

  const exportFlow = useCallback(() => {
    const flowData = {
      nodes,
      edges,
      timestamp: new Date().toISOString(),
    };
    
    const dataStr = JSON.stringify(flowData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    
    const link = document.createElement('a');
    link.href = URL.createObjectURL(dataBlob);
    link.download = `process-flow-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
  }, [nodes, edges]);

  // ============================================================================
  // 🔗 백엔드 기능 (axios 직접 사용)
  // ============================================================================

  // Canvas 목록 조회
  const loadSavedCanvases = useCallback(async () => {
    try {
      setIsLoadingCanvases(true);
      const response = await apiClient.get('/api/v1/cal-boundary/canvas');
      setSavedCanvases(response.data || []);
    } catch (error) {
      console.error('저장된 Canvas 목록 조회 실패:', error);
      setSavedCanvases([]);
    } finally {
      setIsLoadingCanvases(false);
    }
  }, []);

  // 백엔드 저장 기능
  const saveToBackend = useCallback(async () => {
    try {
      const canvasName = `공정도_${new Date().toISOString().split('T')[0]}`;
      const canvasData = {
        name: canvasName,
        description: 'React Flow 공정도',
        nodes: nodes.map(node => ({
          id: node.id,
          type: node.type,
          position: node.position,
          data: node.data,
          style: node.style,
        })),
        edges: edges.map(edge => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          type: edge.type,
          data: edge.data,
          style: edge.style,
        })),
        metadata: {
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          nodeCount: nodes.length,
          edgeCount: edges.length,
        },
      };

      const response = await apiClient.post('/api/v1/cal-boundary/canvas', canvasData);
      console.log('✅ 백엔드 저장 완료:', response.data);
      alert('공정도가 성공적으로 저장되었습니다!');
      
      // 저장된 Canvas 목록 새로고침
      loadSavedCanvases();
      
    } catch (error) {
      console.error('❌ 백엔드 저장 실패:', error);
      alert('백엔드 저장에 실패했습니다. 다시 시도해주세요.');
    }
  }, [nodes, edges, loadSavedCanvases]);

  // 백엔드에서 로드 기능
  const loadFromBackend = useCallback(async (canvasId?: string) => {
    try {
      if (canvasId) {
        // 특정 Canvas 로드
        const response = await apiClient.get(`/api/v1/cal-boundary/canvas/${canvasId}`);
        const canvas = response.data;
        
        // React Flow 형식으로 변환
        const flowData = {
          nodes: canvas.nodes.map((node: any) => ({
            ...node,
            selected: false,
            dragging: false,
          })),
          edges: canvas.edges.map((edge: any) => ({
            ...edge,
            selected: false,
          })),
          metadata: canvas.metadata,
        };
        
        setNodes(flowData.nodes || []);
        setEdges(flowData.edges || []);
        console.log('✅ 백엔드에서 공정도 로드 완료');
      } else {
        // 최신 Canvas 로드
        const canvases = await apiClient.get('/api/v1/cal-boundary/canvas');
        if (canvases.data && canvases.data.length > 0) {
          const latestCanvas = canvases.data[0];
          const flowResponse = await apiClient.get(`/api/v1/cal-boundary/canvas/${latestCanvas.id}`);
          const canvas = flowResponse.data;
          
          const flowData = {
            nodes: canvas.nodes.map((node: any) => ({
              ...node,
              selected: false,
              dragging: false,
            })),
            edges: canvas.edges.map((edge: any) => ({
              ...edge,
              selected: false,
            })),
            metadata: canvas.metadata,
          };
          
          setNodes(flowData.nodes || []);
          setEdges(flowData.edges || []);
          
          console.log('✅ 백엔드에서 공정도 로드 완료:', latestCanvas.name);
          alert(`"${latestCanvas.name}" 공정도를 불러왔습니다.`);
        } else {
          alert('저장된 공정도가 없습니다. 새로 만들어보세요!');
        }
      }
    } catch (error) {
      console.error('❌ 백엔드 로드 실패:', error);
      alert('백엔드 로드에 실패했습니다. 다시 시도해주세요.');
    }
  }, [setNodes, setEdges]);

  // 서비스 상태 확인
  const checkServiceStatus = useCallback(async () => {
    try {
      const response = await apiClient.get('/api/v1/gateway/services/health');
      setServiceStatus(response.data);
    } catch (error) {
      console.error('서비스 상태 확인 실패:', error);
      setServiceStatus(null);
    }
  }, []);

  // 공정 단계 추가 함수
  const addProcessNode = useCallback(() => {
    const newNode: Node<any> = {
      id: `node-${Date.now()}`,
      type: 'processNode',
      position: { x: 250, y: 250 },
      data: {
        label: '새 공정 단계',
        processType: 'manufacturing',
        description: '공정 단계 설명을 입력하세요',
        parameters: {},
      },
    };
    setNodes((prevNodes) => [...prevNodes, newNode]);
    console.log('✅ 공정 단계 추가됨:', newNode);
  }, [setNodes]);

  // 선택된 요소 삭제 함수
  const deleteSelectedElements = useCallback(() => {
    const selectedNodes = nodes.filter((node) => node.selected);
    const selectedEdges = edges.filter((edge) => edge.selected);
    
    if (selectedNodes.length > 0 || selectedEdges.length > 0) {
      setNodes((prevNodes) => prevNodes.filter((node) => !node.selected));
      setEdges((prevEdges) => prevEdges.filter((edge) => !edge.selected));
      console.log('✅ 선택된 요소 삭제됨');
    } else {
      alert('삭제할 요소를 선택해주세요.');
    }
  }, [nodes, edges, setNodes, setEdges]);

  // 컴포넌트 마운트 시 실행
  React.useEffect(() => {
    loadSavedCanvases();
    checkServiceStatus();
  }, [loadSavedCanvases, checkServiceStatus]);

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================

  return (
    <div className="min-h-screen bg-[#0b0c0f]">
      {/* 헤더 */}
      <div className="bg-[#1e293b] shadow-sm border-b border-[#334155]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-white">공정도 관리</h1>
              <p className="text-sm text-[#cbd5e1]">
                React Flow 기반의 인터랙티브 공정도 에디터
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              {/* 서비스 상태 표시 */}
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${
                  serviceStatus ? 'bg-green-500' : 'bg-red-500'
                }`} title={serviceStatus ? '서비스 정상' : '서비스 오류'} />
                <span className="text-xs text-white">
                  {serviceStatus ? '연결됨' : '연결 안됨'}
                </span>
              </div>
              
              <button
                onClick={() => setIsReadOnly(!isReadOnly)}
                className={`px-4 py-2 rounded-lg text-sm font-medium ${
                  isReadOnly
                    ? 'bg-blue-500 text-white hover:bg-blue-600'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                {isReadOnly ? '편집 모드' : '읽기 전용'}
              </button>
              
              <button
                onClick={exportFlow}
                className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm font-medium"
              >
                내보내기
              </button>
              
              <button
                onClick={saveToBackend}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
              >
                백엔드 저장
              </button>
              
              <button
                onClick={() => loadFromBackend()}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
              >
                백엔드 로드
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 왼쪽 사이드바 - 정보 패널 */}
          <div className="lg:col-span-1">
            <ProcessFlowInfoPanel
              nodes={nodes}
              edges={edges}
              selectedNodes={selectedNodes}
              selectedEdges={selectedEdges}
            />
          </div>

          {/* 메인 공정도 에디터 */}
          <div className="lg:col-span-3">
            <div className="bg-[#1e293b] rounded-lg shadow-lg p-6 border border-[#334155]">
              <ProcessFlowEditor
                initialNodes={nodes}
                initialEdges={edges}
                onFlowChange={handleFlowChange}
                readOnly={isReadOnly}
              />
              
              {/* 하단 컨트롤 버튼들 */}
              <div className="flex justify-center space-x-4 mt-4">
                <button
                  onClick={addProcessNode}
                  className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium transition-colors"
                >
                  공정 단계 추가
                </button>
                <button
                  onClick={deleteSelectedElements}
                  className="px-6 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 font-medium transition-colors"
                >
                  선택 삭제
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
