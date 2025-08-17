'use client';

import React, { useState, useCallback } from 'react';
import ProcessFlowEditor from '@/templates/ProcessFlowEditor';
import ProcessFlowInfoPanel from '@/organisms/ProcessFlowInfoPanel';
import { Node, Edge } from '@xyflow/react';
import axios from 'axios';

// ============================================================================
// 🔗 Cal_boundary API 서비스 - Process Flow 전용
// ============================================================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8080';
const CAL_BOUNDARY_URL = process.env.NEXT_PUBLIC_CAL_BOUNDARY_URL || 'http://localhost:8001';

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
// 🎨 도형 관련 API
// ============================================================================

interface ShapeData {
  id?: string;
  type: string;
  position: { x: number; y: number };
  data: any;
  style?: any;
}

const shapeApi = {
  // 모든 도형 조회
  getAll: async () => {
    const response = await apiClient.get('/cal-boundary/shapes');
    return response.data;
  },

  // 도형 생성
  create: async (shape: ShapeData) => {
    const response = await apiClient.post('/cal-boundary/shapes', shape);
    return response.data;
  },

  // 도형 수정
  update: async (id: string, shape: Partial<ShapeData>) => {
    const response = await apiClient.put(`/cal-boundary/shapes/${id}`, shape);
    return response.data;
  },

  // 도형 삭제
  delete: async (id: string) => {
    const response = await apiClient.delete(`/cal-boundary/shapes/${id}`);
    return response.data;
  },
};

// ============================================================================
// ➡️ 화살표 관련 API
// ============================================================================

interface ArrowData {
  id?: string;
  source: string;
  target: string;
  type: string;
  data: any;
  style?: any;
}

const arrowApi = {
  // 모든 화살표 조회
  getAll: async () => {
    const response = await apiClient.get('/cal-boundary/arrows');
    return response.data;
  },

  // 화살표 생성
  create: async (arrow: ArrowData) => {
    const response = await apiClient.post('/cal-boundary/arrows', arrow);
    return response.data;
  },

  // 화살표 수정
  update: async (id: string, arrow: Partial<ArrowData>) => {
    const response = await apiClient.put(`/cal-boundary/arrows/${id}`, arrow);
    return response.data;
  },

  // 화살표 삭제
  delete: async (id: string) => {
    const response = await apiClient.delete(`/cal-boundary/arrows/${id}`);
    return response.data;
  },
};

// ============================================================================
// 🖼️ Canvas 관련 API
// ============================================================================

interface CanvasData {
  id?: string;
  name: string;
  description?: string;
  nodes: ShapeData[];
  edges: ArrowData[];
  metadata?: any;
}

const canvasApi = {
  // 모든 Canvas 조회
  getAll: async () => {
    const response = await apiClient.get('/cal-boundary/canvas');
    return response.data;
  },

  // Canvas 생성
  create: async (canvas: CanvasData) => {
    const response = await apiClient.post('/cal-boundary/canvas', canvas);
    return response.data;
  },

  // Canvas 수정
  update: async (id: string, canvas: Partial<CanvasData>) => {
    const response = await apiClient.put(`/cal-boundary/canvas/${id}`, canvas);
    return response.data;
  },

  // Canvas 삭제
  delete: async (id: string) => {
    const response = await apiClient.delete(`/cal-boundary/canvas/${id}`);
    return response.data;
  },

  // Canvas 저장 (React Flow 데이터)
  saveFlow: async (name: string, nodes: any[], edges: any[], description?: string) => {
    const canvasData: CanvasData = {
      name,
      description,
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

    const response = await apiClient.post('/cal-boundary/canvas', canvasData);
    return response.data;
  },

  // Canvas 로드 (React Flow 데이터로 변환)
  loadFlow: async (id: string) => {
    const response = await apiClient.get(`/cal-boundary/canvas/${id}`);
    const canvas = response.data;
    
    // React Flow 형식으로 변환
    return {
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
  },
};

// ============================================================================
// 🔍 헬스 체크
// ============================================================================

const healthApi = {
  // 게이트웨이 헬스 체크
  gateway: async () => {
    const response = await apiClient.get('/gateway/health');
    return response.data;
  },

  // Cal_boundary 서비스 헬스 체크
  calBoundary: async () => {
    try {
      const response = await axios.get(`${CAL_BOUNDARY_URL}/health`);
      return response.data;
    } catch (error) {
      console.error('Cal_boundary 서비스 헬스 체크 실패:', error);
      throw error;
    }
  },

  // 모든 서비스 헬스 체크
  all: async () => {
    const response = await apiClient.get('/gateway/services/health');
    return response.data;
  },
};
// 샘플 공정도 데이터
const sampleNodes: Node<any>[] = [
  {
    id: 'node-1',
    type: 'processNode',
    position: { x: 100, y: 100 },
    data: {
      label: '원료 투입',
      processType: 'manufacturing',
      description: '제품 생산을 위한 원료를 투입합니다',
      parameters: {
        '원료량': '100kg',
        '온도': '25°C'
      }
    }
  },
  {
    id: 'node-2',
    type: 'processNode',
    position: { x: 400, y: 100 },
    data: {
      label: '혼합 공정',
      processType: 'manufacturing',
      description: '원료를 균일하게 혼합합니다',
      parameters: {
        '혼합시간': '30분',
        '회전속도': '500rpm'
      }
    }
  },
  {
    id: 'node-3',
    type: 'processNode',
    position: { x: 700, y: 100 },
    data: {
      label: '품질 검사',
      processType: 'quality',
      description: '혼합된 원료의 품질을 검사합니다',
      parameters: {
        '검사항목': '균질성, 수분함량',
        '허용기준': '±5%'
      }
    }
  },
  {
    id: 'node-4',
    type: 'processNode',
    position: { x: 700, y: 300 },
    data: {
      label: '포장',
      processType: 'packaging',
      description: '검사 완료된 제품을 포장합니다',
      parameters: {
        '포장재': 'PE백',
        '단위': '25kg'
      }
    }
  },
  {
    id: 'node-5',
    type: 'processNode',
    position: { x: 1000, y: 300 },
    data: {
      label: '출하',
      processType: 'shipping',
      description: '포장된 제품을 출하합니다',
      parameters: {
        '출하량': '1000kg/일',
        '운송수단': '트럭'
      }
    }
  }
];

const sampleEdges: Edge<any>[] = [
  {
    id: 'edge-1',
    source: 'node-1',
    target: 'node-2',
    type: 'processEdge',
    data: {
      label: '원료 전달',
      processType: 'standard'
    }
  },
  {
    id: 'edge-2',
    source: 'node-2',
    target: 'node-3',
    type: 'processEdge',
    data: {
      label: '혼합 완료',
      processType: 'critical'
    }
  },
  {
    id: 'edge-3',
    source: 'node-3',
    target: 'node-4',
    type: 'processEdge',
    data: {
      label: '품질 합격',
      processType: 'standard'
    }
  },
  {
    id: 'edge-4',
    source: 'node-4',
    target: 'node-5',
    type: 'processEdge',
    data: {
      label: '포장 완료',
      processType: 'standard'
    }
  }
];

export default function ProcessFlowPage() {
  const [nodes, setNodes] = useState<Node<any>[]>(sampleNodes);
  const [edges, setEdges] = useState<Edge<any>[]>(sampleEdges);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [selectedNodes, setSelectedNodes] = useState<Node<any>[]>([]);
  const [selectedEdges, setSelectedEdges] = useState<Edge<any>[]>([]);

  const handleFlowChange = useCallback((newNodes: Node[], newEdges: Edge[]) => {
    setNodes(newNodes);
    setEdges(newEdges);
    
    // 선택된 요소들 업데이트
    setSelectedNodes(newNodes.filter(node => node.selected));
    setSelectedEdges(newEdges.filter(edge => edge.selected));
  }, []);

  const resetToSample = useCallback(() => {
    setNodes(sampleNodes);
    setEdges(sampleEdges);
    setSelectedNodes([]);
    setSelectedEdges([]);
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

  // Canvas 목록 조회
  const [savedCanvases, setSavedCanvases] = useState<any[]>([]);
  const [isLoadingCanvases, setIsLoadingCanvases] = useState(false);

  const loadSavedCanvases = useCallback(async () => {
    try {
      setIsLoadingCanvases(true);
      const canvases = await canvasApi.getAll();
      setSavedCanvases(canvases || []);
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
      const result = await canvasApi.saveFlow(canvasName, nodes, edges, 'React Flow 공정도');
      
      console.log('✅ 백엔드 저장 완료:', result);
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
        const flowData = await canvasApi.loadFlow(canvasId);
        setNodes(flowData.nodes || []);
        setEdges(flowData.edges || []);
        console.log('✅ 백엔드에서 공정도 로드 완료');
      } else {
        // 최신 Canvas 로드
        const canvases = await canvasApi.getAll();
        if (canvases && canvases.length > 0) {
          const latestCanvas = canvases[0];
          const flowData = await canvasApi.loadFlow(latestCanvas.id);
          
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
  const [serviceStatus, setServiceStatus] = useState<any>(null);

  const checkServiceStatus = useCallback(async () => {
    try {
      const status = await healthApi.all();
      setServiceStatus(status);
    } catch (error) {
      console.error('서비스 상태 확인 실패:', error);
      setServiceStatus(null);
    }
  }, []);

  // 컴포넌트 마운트 시 실행
  React.useEffect(() => {
    loadSavedCanvases();
    checkServiceStatus();
  }, [loadSavedCanvases, checkServiceStatus]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">공정도 관리</h1>
              <p className="text-sm text-gray-600">
                React Flow 기반의 인터랙티브 공정도 에디터
              </p>
            </div>
            
                         <div className="flex items-center space-x-3">
               {/* 서비스 상태 표시 */}
               <div className="flex items-center space-x-2">
                 <div className={`w-3 h-3 rounded-full ${
                   serviceStatus ? 'bg-green-500' : 'bg-red-500'
                 }`} title={serviceStatus ? '서비스 정상' : '서비스 오류'} />
                 <span className="text-xs text-gray-600">
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
                 onClick={resetToSample}
                 className="px-4 py-2 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 text-sm font-medium"
               >
                 샘플 복원
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
            <div className="bg-white rounded-lg shadow-lg p-6">
              <ProcessFlowEditor
                initialNodes={nodes}
                initialEdges={edges}
                onFlowChange={handleFlowChange}
                readOnly={isReadOnly}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
