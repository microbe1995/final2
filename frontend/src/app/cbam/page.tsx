'use client';

import React, { useState, useEffect } from 'react';
import ProcessFlowTemplate from '@/templates/ProcessFlowTemplate';
import Toast from '@/molecules/Toast';
import axios from 'axios';

// ============================================================================
// 🎯 CBAM 페이지 - 공정도 기반 탄소배출량 계산
// ============================================================================

export default function CBAMPage() {
  // ============================================================================
  // 📊 상태 관리
  // ============================================================================
  
  // Canvas 관련 상태
  const [canvases, setCanvases] = useState([]);
  const [selectedCanvas, setSelectedCanvas] = useState(null);
  
  // 선택된 요소 상태
  const [selectedShape, setSelectedShape] = useState(null);
  const [selectedArrow, setSelectedArrow] = useState(null);
  
  // 그리기 모드 상태
  const [drawMode, setDrawMode] = useState('select');
  const [shapeType, setShapeType] = useState('process');
  const [arrowType, setArrowType] = useState('straight');
  
  // 그리드 설정 상태
  const [gridSize, setGridSize] = useState(20);
  const [showGrid, setShowGrid] = useState(true);
  const [snapToGrid, setSnapToGrid] = useState(true);
  
  // 연결 모드 상태
  const [isConnecting, setConnecting] = useState(false);
  const [connectionStart, setConnectionStart] = useState(null);
  
  // UI 상태
  const [toast, setToast] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  // ============================================================================
  // 🌐 API 설정
  // ============================================================================
  
  const API_BASE_URL = process.env.NEXT_PUBLIC_CAL_BOUNDARY_URL || 'https://lcafinal-production.up.railway.app';

  // ============================================================================
  // 🔄 데이터 로딩
  // ============================================================================
  
  useEffect(() => {
    loadCanvases();
  }, []);

  const loadCanvases = async () => {
    try {
      setIsLoading(true);
      const response = await axios.get(`${API_BASE_URL}/canvases`);
      setCanvases(response.data);
      
      if (response.data.length > 0 && !selectedCanvas) {
        setSelectedCanvas(response.data[0]);
      }
    } catch (error) {
      console.error('Canvas 로딩 실패:', error);
      showToast('error', 'Canvas 로딩에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  // ============================================================================
  // 🎨 Canvas 관리
  // ============================================================================
  
  const handleCanvasCreate = async () => {
    try {
      const newCanvas = {
        name: `새 Canvas ${canvases.length + 1}`,
        width: 800,
        height: 600,
        backgroundColor: '#ffffff',
        shapes: [],
        arrows: []
      };
      
      const response = await axios.post(`${API_BASE_URL}/canvases`, newCanvas);
      const createdCanvas = response.data;
      
      setCanvases(prev => [...prev, createdCanvas]);
      setSelectedCanvas(createdCanvas);
      showToast('success', '새 Canvas가 생성되었습니다.');
    } catch (error) {
      console.error('Canvas 생성 실패:', error);
      showToast('error', 'Canvas 생성에 실패했습니다.');
    }
  };

  const handleCanvasSelect = (canvas) => {
    setSelectedCanvas(canvas);
    setSelectedShape(null);
    setSelectedArrow(null);
    setConnecting(false);
    setConnectionStart(null);
  };

  const handleCanvasDelete = async (canvasId) => {
    try {
      await axios.delete(`${API_BASE_URL}/canvases/${canvasId}`);
      setCanvases(prev => prev.filter(c => c.id !== canvasId));
      
      if (selectedCanvas?.id === canvasId) {
        setSelectedCanvas(canvases.length > 1 ? canvases.find(c => c.id !== canvasId) : null);
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
      const newShape = {
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

      const updatedCanvas = {
        ...selectedCanvas,
        shapes: [...selectedCanvas.shapes, newShape]
      };

      await axios.put(`${API_BASE_URL}/canvases/${selectedCanvas.id}`, updatedCanvas);
      setSelectedCanvas(updatedCanvas);
      setCanvases(prev => prev.map(c => c.id === selectedCanvas.id ? updatedCanvas : c));
      
      showToast('success', '도형이 추가되었습니다.');
    } catch (error) {
      console.error('도형 생성 실패:', error);
      showToast('error', '도형 생성에 실패했습니다.');
    }
  };

  const handleShapeClick = (shape) => {
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
      const updatedCanvas = {
        ...selectedCanvas,
        shapes: selectedCanvas.shapes.filter(s => s.id !== selectedShape.id),
        arrows: selectedCanvas.arrows.filter(a => 
          a.fromShapeId !== selectedShape.id && a.toShapeId !== selectedShape.id
        )
      };

      await axios.put(`${API_BASE_URL}/canvases/${selectedCanvas.id}`, updatedCanvas);
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
      const newArrow = {
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

      const updatedCanvas = {
        ...selectedCanvas,
        arrows: [...selectedCanvas.arrows, newArrow]
      };

      await axios.put(`${API_BASE_URL}/canvases/${selectedCanvas.id}`, updatedCanvas);
      setSelectedCanvas(updatedCanvas);
      setCanvases(prev => prev.map(c => c.id === selectedCanvas.id ? updatedCanvas : c));
      
      showToast('success', '화살표가 추가되었습니다.');
    } catch (error) {
      console.error('화살표 생성 실패:', error);
      showToast('error', '화살표 생성에 실패했습니다.');
    }
  };

  const createArrow = async (fromShape, toShape) => {
    if (!selectedCanvas) return;

    try {
      const newArrow = {
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

      const updatedCanvas = {
        ...selectedCanvas,
        arrows: [...selectedCanvas.arrows, newArrow]
      };

      await axios.put(`${API_BASE_URL}/canvases/${selectedCanvas.id}`, updatedCanvas);
      setSelectedCanvas(updatedCanvas);
      setCanvases(prev => prev.map(c => c.id === selectedCanvas.id ? updatedCanvas : c));
      
      showToast('success', '도형이 연결되었습니다.');
    } catch (error) {
      console.error('화살표 생성 실패:', error);
      showToast('error', '화살표 생성에 실패했습니다.');
    }
  };

  const handleArrowClick = (arrow) => {
    setSelectedArrow(arrow);
    setSelectedShape(null);
  };

  const handleArrowDelete = async () => {
    if (!selectedArrow || !selectedCanvas) return;

    try {
      const updatedCanvas = {
        ...selectedCanvas,
        arrows: selectedCanvas.arrows.filter(a => a.id !== selectedArrow.id)
      };

      await axios.put(`${API_BASE_URL}/canvases/${selectedCanvas.id}`, updatedCanvas);
      setSelectedCanvas(updatedCanvas);
      setCanvases(prev => prev.map(c => c.id === selectedCanvas.id ? updatedCanvas : c));
      setSelectedArrow(null);
      
      showToast('success', '화살표가 삭제되었습니다.');
    } catch (error) {
      console.error('화살표 삭제 실패:', error);
      showToast('error', '화살표 삭제에 실패했습니다.');
    }
  };

  // ============================================================================
  // 🎨 유틸리티 함수
  // ============================================================================
  
  const getShapeColor = (type) => {
    const colorMap = {
      process: '#8B5CF6',
      material: '#06B6D4',
      energy: '#F97316',
      storage: '#84CC16',
      transport: '#EF4444'
    };
    return colorMap[type] || '#6B7280';
  };

  const showToast = (type, message) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3000);
  };

  // ============================================================================
  // 🎭 이벤트 핸들러
  // ============================================================================
  
  const handleCanvasClick = (e) => {
    if (e.target === e.currentTarget) {
      setSelectedShape(null);
      setSelectedArrow(null);
    }
  };

  const handleMouseMove = (e) => {
    // 드래그 앤 드롭 로직은 ProcessFlowTemplate에서 처리
  };

  const handleMouseUp = () => {
    // 드래그 앤 드롭 로직은 ProcessFlowTemplate에서 처리
  };

  const handleShapeMouseDown = (e, shape) => {
    // 드래그 앤 드롭 로직은 ProcessFlowTemplate에서 처리
  };

  const handleShapeMouseEnter = (shape) => {
    // 호버 효과는 ProcessFlowTemplate에서 처리
  };

  const handleShapeMouseLeave = () => {
    // 호버 효과는 ProcessFlowTemplate에서 처리
  };

  const handleArrowMouseEnter = (arrow) => {
    // 호버 효과는 ProcessFlowTemplate에서 처리
  };

  const handleArrowMouseLeave = () => {
    // 호버 효과는 ProcessFlowTemplate에서 처리
  };

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================
  
  return (
    <div className="min-h-screen bg-gray-50">
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
          <div className="bg-white p-6 rounded-lg">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">로딩 중...</p>
          </div>
        </div>
      )}
    </div>
  );
}
