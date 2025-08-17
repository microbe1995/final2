'use client';

import React, { useState, useEffect } from 'react';
import ProcessFlowTemplate from '@/templates/ProcessFlowTemplate';
import Toast from '@/molecules/Toast';
import axios from 'axios';

// ============================================================================
// 📝 타입 정의
// ============================================================================

interface Canvas {
  id: string;
  name: string;
  width: number;
  height: number;
  backgroundColor: string;
  shapes: any[];
  arrows: any[];
}

interface Shape {
  id: string;
  type: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  label: string;
  processType?: string;
  materialType?: string;
  energyType?: string;
}

interface Arrow {
  id: string;
  type: string;
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  color: string;
  strokeWidth: number;
  flowType?: string;
  direction?: string;
  fromShapeId?: string;
  toShapeId?: string;
}

// ============================================================================
// 🎯 CBAM 페이지 - 공정도 기반 탄소배출량 계산
// ============================================================================

export default function CBAMPage() {
  // ============================================================================
  // 📊 상태 관리
  // ============================================================================
  
  // Canvas 관련 상태
  const [canvases, setCanvases] = useState<Canvas[]>([]);
  const [selectedCanvas, setSelectedCanvas] = useState<Canvas | null>(null);
  
  // 선택된 요소 상태
  const [selectedShape, setSelectedShape] = useState<Shape | null>(null);
  const [selectedArrow, setSelectedArrow] = useState<Arrow | null>(null);
  
  // 그리기 모드 상태
  const [drawMode, setDrawMode] = useState<'select' | 'shape' | 'arrow'>('select');
  const [shapeType, setShapeType] = useState<string>('process');
  const [arrowType, setArrowType] = useState<string>('straight');
  
  // 그리드 설정 상태
  const [gridSize, setGridSize] = useState<number>(20);
  const [showGrid, setShowGrid] = useState<boolean>(true);
  const [snapToGrid, setSnapToGrid] = useState<boolean>(true);
  
  // 연결 모드 상태
  const [isConnecting, setConnecting] = useState<boolean>(false);
  const [connectionStart, setConnectionStart] = useState<Shape | null>(null);
  
  // UI 상태
  const [toast, setToast] = useState<{ type: 'success' | 'error' | 'info'; message: string } | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [apiStatus, setApiStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  // ============================================================================
  // 🌐 API 설정
  // ============================================================================
  
  const API_BASE_URL = process.env.NEXT_PUBLIC_CAL_BOUNDARY_URL || 'https://lcafinal-production.up.railway.app';
  const API_PREFIX = '/api/v1';

  // API 설정 정보를 콘솔에 출력
  useEffect(() => {
    console.log('🔧 API 설정 정보:', {
      NEXT_PUBLIC_CAL_BOUNDARY_URL: process.env.NEXT_PUBLIC_CAL_BOUNDARY_URL,
      API_BASE_URL,
      API_PREFIX,
      fullUrl: `${API_BASE_URL}${API_PREFIX}/canvas`
    });
  }, []);

  // ============================================================================
  // 🔄 데이터 로딩
  // ============================================================================
  
  useEffect(() => {
    testApiConnection();
    loadCanvases();
  }, []);

  const testApiConnection = async () => {
    try {
      setApiStatus('checking');
      console.log('🔄 API 연결 테스트 시작:', `${API_BASE_URL}/health`);
      
      const response = await axios.get(`${API_BASE_URL}/health`);
      console.log('✅ API 연결 테스트 성공:', response.data);
      setApiStatus('connected');
      
      // 연결 성공 후 공정 필드 로딩
      loadCanvases();
    } catch (error: any) {
      console.error('❌ API 연결 테스트 실패:', error);
      setApiStatus('disconnected');
      
      // 연결 실패 시 사용자에게 안내
      if (error.response?.status === 404) {
        showToast('error', '백엔드 서비스에 연결할 수 없습니다. Railway 배포 설정을 확인해주세요.');
      } else {
        showToast('error', '백엔드 서비스 연결에 실패했습니다. 서비스 상태를 확인해주세요.');
      }
    }
  };

  const loadCanvases = async () => {
    try {
      setIsLoading(true);
      console.log('🔄 공정 필드 로딩 시작:', `${API_BASE_URL}${API_PREFIX}/canvas`);
      
      const response = await axios.get(`${API_BASE_URL}${API_PREFIX}/canvas`);
      console.log('✅ API 응답:', response.data);
      
      // 응답 구조에 맞게 데이터 추출
      let canvasData = [];
      if (response.data && response.data.canvases) {
        // CanvasListResponse 구조
        canvasData = response.data.canvases;
        console.log('📋 CanvasListResponse 구조 사용:', canvasData.length, '개');
      } else if (Array.isArray(response.data)) {
        // 배열 형태로 직접 응답
        canvasData = response.data;
        console.log('📋 배열 형태 응답 사용:', canvasData.length, '개');
      } else {
        // 빈 배열로 초기화
        canvasData = [];
        console.log('📋 빈 배열로 초기화');
      }
      
      setCanvases(canvasData);
      
      if (canvasData.length > 0 && !selectedCanvas) {
        setSelectedCanvas(canvasData[0]);
        console.log('🎯 첫 번째 공정 필드 선택:', canvasData[0].name);
      }
    } catch (error: any) {
      console.error('❌ 공정 필드 로딩 실패:', error);
      
      // 에러 상세 정보 로깅
      if (error.response) {
        console.error('📡 서버 응답 에러:', {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data,
          headers: error.response.headers
        });
      } else if (error.request) {
        console.error('🌐 네트워크 에러:', error.request);
      } else {
        console.error('⚙️ 요청 설정 에러:', error.message);
      }
      
      // 사용자에게 더 구체적인 에러 메시지 표시
      let errorMessage = '공정 필드 로딩에 실패했습니다.';
      if (error.response?.status === 404) {
        errorMessage = 'API 엔드포인트를 찾을 수 없습니다. 백엔드 서비스를 확인해주세요.';
      } else if (error.response?.status === 405) {
        errorMessage = '지원하지 않는 HTTP 메서드입니다. API 엔드포인트를 확인해주세요.';
      } else if (error.code === 'ECONNREFUSED') {
        errorMessage = '백엔드 서비스에 연결할 수 없습니다. 서비스가 실행 중인지 확인해주세요.';
      }
      
      showToast('error', errorMessage);
      // 에러 시 빈 배열로 초기화
      setCanvases([]);
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // 🎨 공정 필드 관리
  // ============================================================================
  
  const handleCanvasCreate = async () => {
    try {
      const newCanvas = {
        name: `새 공정 필드 ${canvases.length + 1}`,
        width: 800,
        height: 600,
        backgroundColor: '#ffffff',
        shapes: [],
        arrows: []
      };
      
      const response = await axios.post(`${API_BASE_URL}${API_PREFIX}/canvas`, newCanvas);
      const createdCanvas: Canvas = response.data;
      
      setCanvases(prev => [...prev, createdCanvas]);
      setSelectedCanvas(createdCanvas);
      showToast('success', '새 공정 필드가 생성되었습니다.');
    } catch (error) {
      console.error('공정 필드 생성 실패:', error);
      showToast('error', '공정 필드 생성에 실패했습니다.');
    }
  };

  const handleCanvasSelect = (canvas: Canvas) => {
    setSelectedCanvas(canvas);
    setSelectedShape(null);
    setSelectedArrow(null);
    setConnecting(false);
    setConnectionStart(null);
  };

  const handleCanvasDelete = async (canvasId: string) => {
    try {
      await axios.delete(`${API_BASE_URL}${API_PREFIX}/canvas/${canvasId}`);
      setCanvases(prev => prev.filter(c => c.id !== canvasId));
      
      if (selectedCanvas?.id === canvasId) {
        setSelectedCanvas(canvases.length > 1 ? canvases.find(c => c.id !== canvasId) || null : null);
      }
      
      showToast('success', 'Canvas가 삭제되었습니다.');
    } catch (error) {
      console.error('Canvas 삭제 실패:', error);
      showToast('error', 'Canvas 삭제에 실패했습니다.');
    }
  };

  // ============================================================================
  // 🎯 도형 관리
  // ============================================================================
  
  const handleShapeCreate = async () => {
    if (!selectedCanvas) {
      showToast('error', '먼저 Canvas를 선택해주세요.');
      return;
    }

    try {
      const newShape: Shape = {
        id: `shape_${Date.now()}`,
        type: shapeType,
        x: 100,
        y: 100,
        width: 120,
        height: 80,
        color: getShapeColor(shapeType),
        label: `${shapeType.charAt(0).toUpperCase() + shapeType.slice(1)} ${(selectedCanvas?.shapes?.length || 0) + 1}`,
        processType: shapeType === 'process' ? 'manufacturing' : undefined,
        materialType: shapeType === 'material' ? 'raw' : undefined,
        energyType: shapeType === 'energy' ? 'electricity' : undefined
      };

      const updatedCanvas: Canvas = {
        ...selectedCanvas,
        shapes: [...selectedCanvas.shapes, newShape]
      };

      await axios.put(`${API_BASE_URL}${API_PREFIX}/canvas/${selectedCanvas.id}`, updatedCanvas);
      setSelectedCanvas(updatedCanvas);
      setCanvases(prev => prev.map(c => c.id === selectedCanvas.id ? updatedCanvas : c));
      
      showToast('success', '도형이 추가되었습니다.');
    } catch (error) {
      console.error('도형 생성 실패:', error);
      showToast('error', '도형 생성에 실패했습니다.');
    }
  };

  const handleShapeClick = (shape: Shape) => {
    if (isConnecting) {
      if (!connectionStart) {
        setConnectionStart(shape);
        showToast('info', '연결할 두 번째 도형을 클릭하세요.');
      } else if (connectionStart.id !== shape.id) {
        createArrow(connectionStart, shape);
        setConnectionStart(null);
        setConnecting(false);
      }
    } else {
      setSelectedShape(shape);
      setSelectedArrow(null);
    }
  };

  const handleShapeDelete = async () => {
    if (!selectedShape || !selectedCanvas) return;

    try {
      const updatedCanvas: Canvas = {
        ...selectedCanvas,
        shapes: selectedCanvas.shapes.filter(s => s.id !== selectedShape.id),
        arrows: selectedCanvas.arrows.filter(a => 
          a.fromShapeId !== selectedShape.id && a.toShapeId !== selectedShape.id
        )
      };

      await axios.put(`${API_BASE_URL}${API_PREFIX}/canvas/${selectedCanvas.id}`, updatedCanvas);
      setSelectedCanvas(updatedCanvas);
      setCanvases(prev => prev.map(c => c.id === selectedCanvas.id ? updatedCanvas : c));
      setSelectedShape(null);
      
      showToast('success', '도형이 삭제되었습니다.');
    } catch (error) {
      console.error('도형 삭제 실패:', error);
      showToast('error', '도형 삭제에 실패했습니다.');
    }
  };

  // ============================================================================
  // ➡️ 화살표 관리
  // ============================================================================
  
  const handleArrowCreate = async () => {
    if (!selectedCanvas) {
      showToast('error', '먼저 Canvas를 선택해주세요.');
      return;
    }

    try {
      const newArrow: Arrow = {
        id: `arrow_${Date.now()}`,
        type: arrowType,
        startX: 200,
        startY: 150,
        endX: 300,
        endY: 150,
        color: '#EF4444',
        strokeWidth: 3,
        flowType: 'material',
        direction: 'forward'
      };

      const updatedCanvas: Canvas = {
        ...selectedCanvas,
        arrows: [...selectedCanvas.arrows, newArrow]
      };

      await axios.put(`${API_BASE_URL}${API_PREFIX}/canvas/${selectedCanvas.id}`, updatedCanvas);
      setSelectedCanvas(updatedCanvas);
      setCanvases(prev => prev.map(c => c.id === selectedCanvas.id ? updatedCanvas : c));
      
      showToast('success', '화살표가 추가되었습니다.');
    } catch (error) {
      console.error('화살표 생성 실패:', error);
      showToast('error', '화살표 생성에 실패했습니다.');
    }
  };

  const createArrow = async (fromShape: Shape, toShape: Shape) => {
    if (!selectedCanvas) return;

    try {
      const newArrow: Arrow = {
        id: `arrow_${Date.now()}`,
        type: arrowType,
        startX: fromShape.x + fromShape.width / 2,
        startY: fromShape.y + fromShape.height / 2,
        endX: toShape.x + toShape.width / 2,
        endY: toShape.y + toShape.height / 2,
        color: '#EF4444',
        strokeWidth: 3,
        flowType: 'material',
        direction: 'forward',
        fromShapeId: fromShape.id,
        toShapeId: toShape.id
      };

      const updatedCanvas: Canvas = {
        ...selectedCanvas,
        arrows: [...selectedCanvas.arrows, newArrow]
      };

      await axios.put(`${API_BASE_URL}${API_PREFIX}/canvas/${selectedCanvas.id}`, updatedCanvas);
      setSelectedCanvas(updatedCanvas);
      setCanvases(prev => prev.map(c => c.id === selectedCanvas.id ? updatedCanvas : c));
      
      showToast('success', '도형이 연결되었습니다.');
    } catch (error) {
      console.error('화살표 생성 실패:', error);
      showToast('error', '화살표 생성에 실패했습니다.');
    }
  };

  const handleArrowClick = (arrow: Arrow) => {
    setSelectedArrow(arrow);
    setSelectedShape(null);
  };

  const handleArrowDelete = async () => {
    if (!selectedArrow || !selectedCanvas) return;

    try {
      const updatedCanvas: Canvas = {
        ...selectedCanvas,
        arrows: selectedCanvas.arrows.filter(a => a.id !== selectedArrow.id)
      };

      await axios.put(`${API_BASE_URL}${API_PREFIX}/canvas/${selectedCanvas.id}`, updatedCanvas);
      setSelectedCanvas(updatedCanvas);
      setCanvases(prev => prev.map(c => c.id === selectedCanvas.id ? updatedCanvas : c));
      setSelectedArrow(null);
      
      showToast('success', '화살표가 삭제되었습니다.');
    } catch (error) {
      console.error('화살표 삭제 실패:', error);
      showToast('error', '화살표 생성에 실패했습니다.');
    }
  };

  // ============================================================================
  // 🎨 유틸리티 함수
  // ============================================================================
  
  const getShapeColor = (type: string): string => {
    const colorMap: Record<string, string> = {
      process: '#8B5CF6',
      material: '#06B6D4',
      energy: '#F97316',
      storage: '#84CC16',
      transport: '#EF4444'
    };
    return colorMap[type] || '#6B7280';
  };

  const showToast = (type: 'success' | 'error' | 'info', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3000);
  };

  // ============================================================================
  // 🎭 이벤트 핸들러
  // ============================================================================
  
  const handleCanvasClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      setSelectedShape(null);
      setSelectedArrow(null);
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    // 드래그 앤 드롭 로직은 ProcessFlowTemplate에서 처리
  };

  const handleMouseUp = () => {
    // 드래그 앤 드롭 로직은 ProcessFlowTemplate에서 처리
  };

  const handleShapeMouseDown = (e: React.MouseEvent, shape: Shape) => {
    // 드래그 앤 드롭 로직은 ProcessFlowTemplate에서 처리
  };

  const handleShapeMouseEnter = (shape: Shape) => {
    // 호버 효과는 ProcessFlowTemplate에서 처리
  };

  const handleShapeMouseLeave = () => {
    // 호버 효과는 ProcessFlowTemplate에서 처리
  };

  const handleArrowMouseEnter = (arrow: Arrow) => {
    // 호버 효과는 ProcessFlowTemplate에서 처리
  };

  const handleArrowMouseLeave = () => {
    // 호버 효과는 ProcessFlowTemplate에서 처리
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <div className="min-h-screen bg-[#0b0c0f] text-[#0f172a]">
      {/* ProcessFlowTemplate 활용 */}
      <ProcessFlowTemplate
        // Canvas 관련
        canvases={canvases}
        selectedCanvas={selectedCanvas}
        onCanvasSelect={handleCanvasSelect}
        onCanvasDelete={handleCanvasDelete}
        
        // 상태 관리
        selectedShape={selectedShape}
        selectedArrow={selectedArrow}
        isConnecting={isConnecting}
        connectionStart={connectionStart}
        drawMode={drawMode}
        shapeType={shapeType}
        arrowType={arrowType}
        gridSize={gridSize}
        showGrid={showGrid}
        snapToGrid={snapToGrid}
        apiStatus={apiStatus}
        
        // 이벤트 핸들러
        onCanvasClick={handleCanvasClick}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onShapeClick={handleShapeClick}
        onShapeMouseDown={handleShapeMouseDown}
        onShapeMouseEnter={handleShapeMouseEnter}
        onShapeMouseLeave={handleShapeMouseLeave}
        onArrowClick={handleArrowClick}
        onArrowMouseEnter={handleArrowMouseEnter}
        onArrowMouseLeave={handleArrowMouseLeave}
        
        // 설정 변경 핸들러
        onGridSizeChange={setGridSize}
        onShowGridChange={setShowGrid}
        onSnapToGridChange={setSnapToGrid}
        onDrawModeChange={setDrawMode}
        onShapeTypeChange={setShapeType}
        onArrowTypeChange={setArrowType}
        onConnectModeToggle={() => setConnecting(!isConnecting)}
        
        // 액션 핸들러
        onCanvasCreate={handleCanvasCreate}
        onShapeCreate={handleShapeCreate}
        onArrowCreate={handleArrowCreate}
        onShapeEdit={() => showToast('info', '도형 수정 기능은 개발 중입니다.')}
        onShapeDelete={handleShapeDelete}
        onArrowEdit={() => showToast('info', '화살표 수정 기능은 개발 중입니다.')}
        onArrowDelete={handleArrowDelete}
      />

      {/* Toast 알림 */}
      {toast && (
        <Toast
          id="main-toast"
          title={toast.type === 'success' ? '성공' : toast.type === 'error' ? '오류' : '알림'}
          type={toast.type}
          message={toast.message}
          onClose={(id) => setToast(null)}
        />
      )}

      {/* 로딩 상태 */}
      {isLoading && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-[#ffffff] p-6 rounded-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-[#2563eb] mx-auto"></div>
            <p className="mt-2 text-[#0f172a]">로딩 중...</p>
          </div>
        </div>
      )}
    </div>
  );
}
