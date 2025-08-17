'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import Card from '@/molecules/Card';
import Button from '@/atoms/Button';
import Input from '@/atoms/Input';
import FormField from '@/molecules/FormField';
import Modal from '@/molecules/Modal';
import Toast from '@/molecules/Toast';

// ============================================================================
// 🎨 Canvas 도형 타입 정의
// ============================================================================

interface Shape {
  id: string;
  type: 'rectangle' | 'circle' | 'triangle';
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  rotation: number;
}

interface Arrow {
  id: string;
  type: 'straight' | 'curved';
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  color: string;
  strokeWidth: number;
  fromShapeId?: string;
  toShapeId?: string;
}

interface Canvas {
  id: string;
  name: string;
  width: number;
  height: number;
  backgroundColor: string;
  zoom: number;
  shapes: Shape[];
  arrows: Arrow[];
}

// ============================================================================
// 🚀 Cal_boundary 메인 페이지
// ============================================================================

export default function CalBoundaryPage() {
  // 상태 관리
  const [canvases, setCanvases] = useState<Canvas[]>([]);
  const [selectedCanvas, setSelectedCanvas] = useState<Canvas | null>(null);
  const [selectedShape, setSelectedShape] = useState<Shape | null>(null);
  const [selectedArrow, setSelectedArrow] = useState<Arrow | null>(null);
  const [isDrawing, setIsDrawing] = useState(false);
  const [drawMode, setDrawMode] = useState<'shape' | 'arrow' | 'select'>('select');
  const [shapeType, setShapeType] = useState<Shape['type']>('rectangle');
  const [arrowType, setArrowType] = useState<Arrow['type']>('straight');
  const [showShapeModal, setShowShapeModal] = useState(false);
  const [showArrowModal, setShowArrowModal] = useState(false);
  const [showCanvasModal, setShowCanvasModal] = useState(false);
  const [toast, setToast] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // API 기본 URL
  const API_BASE_URL = process.env.NEXT_PUBLIC_CAL_BOUNDARY_URL || 'http://localhost:8001';

  // ============================================================================
  // 🔧 유틸리티 함수들
  // ============================================================================

  const showToast = (type: 'success' | 'error', message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3000);
  };

  const generateId = () => Math.random().toString(36).substr(2, 9);

  // ============================================================================
  // 🌐 API 호출 함수들
  // ============================================================================

  // Canvas 관련 API
  const fetchCanvases = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/canvas`);
      setCanvases(response.data.canvases || []);
    } catch (error) {
      console.error('Canvas 조회 실패:', error);
      showToast('error', 'Canvas 목록을 불러오는데 실패했습니다.');
    }
  };

  // Canvas 삭제 API
  const deleteCanvas = async (canvasId: string) => {
    try {
      await axios.delete(`${API_BASE_URL}/api/v1/canvas/${canvasId}`);
      setCanvases(prev => prev.filter(c => c.id !== canvasId));
      if (selectedCanvas?.id === canvasId) {
        setSelectedCanvas(null);
        setSelectedShape(null);
        setSelectedArrow(null);
      }
      showToast('success', 'Canvas가 삭제되었습니다.');
    } catch (error) {
      console.error('Canvas 삭제 실패:', error);
      showToast('error', 'Canvas 삭제에 실패했습니다.');
    }
  };

  const createCanvas = async (canvasData: Partial<Canvas>) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/canvas`, {
        name: canvasData.name || '새 Canvas',
        width: canvasData.width || 800,
        height: canvasData.height || 600,
        backgroundColor: canvasData.backgroundColor || '#ffffff'
      });

      const newCanvas = response.data;
      setCanvases(prev => [...prev, newCanvas]);
      setSelectedCanvas(newCanvas);
      showToast('success', 'Canvas가 생성되었습니다.');
      setShowCanvasModal(false);
    } catch (error) {
      console.error('Canvas 생성 실패:', error);
      showToast('error', 'Canvas 생성에 실패했습니다.');
    }
  };

  // Shape 관련 API
  const createShape = async (shapeData: Partial<Shape>) => {
    if (!selectedCanvas) return;

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/shapes`, {
        type: shapeData.type || 'rectangle',
        x: shapeData.x || 100,
        y: shapeData.y || 100,
        width: shapeData.width || 100,
        height: shapeData.height || 100,
        color: shapeData.color || '#3B82F6',
        rotation: shapeData.rotation || 0,
        canvas_id: selectedCanvas.id
      });

      const newShape = response.data;
      setSelectedCanvas(prev => prev ? {
        ...prev,
        shapes: [...prev.shapes, newShape]
      } : null);
      showToast('success', '도형이 생성되었습니다.');
      setShowShapeModal(false);
    } catch (error) {
      console.error('도형 생성 실패:', error);
      showToast('error', '도형 생성에 실패했습니다.');
    }
  };

  // Arrow 관련 API
  const createArrow = async (arrowData: Partial<Arrow>) => {
    if (!selectedCanvas) return;

    try {
      const response = await axios.post(`${API_BASE_URL}/api/v1/arrows`, {
        type: arrowData.type || 'straight',
        startX: arrowData.startX || 100,
        startY: arrowData.startY || 100,
        endX: arrowData.endX || 200,
        endY: arrowData.endY || 100,
        color: arrowData.color || '#EF4444',
        strokeWidth: arrowData.strokeWidth || 2,
        canvas_id: selectedCanvas.id
      });

      const newArrow = response.data;
      setSelectedCanvas(prev => prev ? {
        ...prev,
        arrows: [...prev.arrows, newArrow]
      } : null);
      showToast('success', '화살표가 생성되었습니다.');
      setShowArrowModal(false);
    } catch (error) {
      console.error('화살표 생성 실패:', error);
      showToast('error', '화살표 생성에 실패했습니다.');
    }
  };

  // 도형 수정 API
  const updateShape = async (shapeId: string, shapeData: Partial<Shape>) => {
    if (!selectedCanvas) return;

    try {
      const response = await axios.put(`${API_BASE_URL}/api/v1/shapes/${shapeId}`, shapeData);
      const updatedShape = response.data;
      setSelectedCanvas(prev => prev ? {
        ...prev,
        shapes: prev.shapes.map(s => s.id === shapeId ? updatedShape : s)
      } : null);
      showToast('success', '도형이 수정되었습니다.');
    } catch (error) {
      console.error('도형 수정 실패:', error);
      showToast('error', '도형 수정에 실패했습니다.');
    }
  };

  // 도형 삭제 API
  const deleteShape = async (shapeId: string) => {
    if (!selectedCanvas) return;

    try {
      await axios.delete(`${API_BASE_URL}/api/v1/shapes/${shapeId}`);
      setSelectedCanvas(prev => prev ? {
        ...prev,
        shapes: prev.shapes.filter(s => s.id !== shapeId)
      } : null);
      setSelectedShape(null);
      showToast('success', '도형이 삭제되었습니다.');
    } catch (error) {
      console.error('도형 삭제 실패:', error);
      showToast('error', '도형 삭제에 실패했습니다.');
    }
  };

  // 화살표 수정 API
  const updateArrow = async (arrowId: string, arrowData: Partial<Arrow>) => {
    if (!selectedCanvas) return;

    try {
      const response = await axios.put(`${API_BASE_URL}/api/v1/arrows/${arrowId}`, arrowData);
      const updatedArrow = response.data;
      setSelectedCanvas(prev => prev ? {
        ...prev,
        arrows: prev.arrows.map(a => a.id === arrowId ? updatedArrow : a)
      } : null);
      showToast('success', '화살표가 수정되었습니다.');
    } catch (error) {
      console.error('화살표 수정 실패:', error);
      showToast('error', '화살표 수정에 실패했습니다.');
    }
  };

  // 화살표 삭제 API
  const deleteArrow = async (arrowId: string) => {
    if (!selectedCanvas) return;

    try {
      await axios.delete(`${API_BASE_URL}/api/v1/arrows/${arrowId}`);
      setSelectedCanvas(prev => prev ? {
        ...prev,
        arrows: prev.arrows.filter(a => a.id !== arrowId)
      } : null);
      setSelectedArrow(null);
      showToast('success', '화살표가 삭제되었습니다.');
    } catch (error) {
      console.error('화살표 삭제 실패:', error);
      showToast('error', '화살표 삭제에 실패했습니다.');
    }
  };

  // ============================================================================
  // 🎨 Canvas 렌더링 함수들
  // ============================================================================

  const renderShape = (shape: Shape) => {
    const style = {
      position: 'absolute' as const,
      left: shape.x,
      top: shape.y,
      width: shape.width,
      height: shape.height,
      backgroundColor: shape.color,
      transform: `rotate(${shape.rotation}deg)`,
      cursor: 'pointer',
      border: selectedShape?.id === shape.id ? '2px solid #3B82F6' : '1px solid #ccc'
    };

    switch (shape.type) {
      case 'rectangle':
        return <div key={shape.id} style={style} onClick={() => setSelectedShape(shape)} />;
      case 'circle':
        return (
          <div
            key={shape.id}
            style={{
              ...style,
              borderRadius: '50%',
              width: shape.width,
              height: shape.height
            }}
            onClick={() => setSelectedShape(shape)}
          />
        );
      case 'triangle':
        return (
          <div
            key={shape.id}
            style={{
              ...style,
              width: 0,
              height: 0,
              borderLeft: `${shape.width / 2}px solid transparent`,
              borderRight: `${shape.width / 2}px solid transparent`,
              borderBottom: `${shape.height}px solid ${shape.color}`,
              backgroundColor: 'transparent'
            }}
            onClick={() => setSelectedShape(shape)}
          />
        );
      default:
        return null;
    }
  };

  const renderArrow = (arrow: Arrow) => {
    const length = Math.sqrt(
      Math.pow(arrow.endX - arrow.startX, 2) + Math.pow(arrow.endY - arrow.startY, 2)
    );
    const angle = Math.atan2(arrow.endY - arrow.startY, arrow.endX - arrow.startX) * 180 / Math.PI;

    const style = {
      position: 'absolute' as const,
      left: arrow.startX,
      top: arrow.startY,
      width: length,
      height: arrow.strokeWidth,
      backgroundColor: arrow.color,
      transform: `rotate(${angle}deg)`,
      transformOrigin: '0 50%',
      cursor: 'pointer',
      border: selectedArrow?.id === arrow.id ? '2px solid #3B82F6' : 'none'
    };

    return (
      <div
        key={arrow.id}
        style={style}
        onClick={() => setSelectedArrow(arrow)}
      />
    );
  };

  // ============================================================================
  // 🎯 이벤트 핸들러들
  // ============================================================================

  const handleCanvasClick = (e: React.MouseEvent) => {
    if (drawMode === 'shape') {
      const rect = e.currentTarget.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      createShape({
        type: shapeType,
        x,
        y,
        width: 100,
        height: 100,
        color: '#3B82F6'
      });
    } else if (drawMode === 'arrow') {
      // 화살표 그리기 로직
      setIsDrawing(true);
    }
  };

  const handleCanvasCreate = () => {
    setShowCanvasModal(true);
  };

  const handleShapeCreate = () => {
    setShowShapeModal(true);
  };

  const handleArrowCreate = () => {
    setShowArrowModal(true);
  };

  // ============================================================================
  // 🔄 useEffect
  // ============================================================================

  useEffect(() => {
    fetchCanvases();
  }, []);

  // ============================================================================
  // 🎨 렌더링
  // ============================================================================

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            🎨 Cal_boundary - Canvas 기반 도형 관리
          </h1>
          <p className="text-gray-600">
            도형과 화살표를 자유롭게 그리고 관리할 수 있는 Canvas 서비스입니다.
          </p>
        </div>

                 {/* 컨트롤 패널 */}
         <Card className="mb-6 p-4">
           <div className="flex flex-wrap gap-4 items-center">
             <Button onClick={handleCanvasCreate} variant="primary">
               🖼️ 새 Canvas
             </Button>
             <Button onClick={handleShapeCreate} variant="success">
               🎨 도형 추가
             </Button>
             <Button onClick={handleArrowCreate} variant="warning">
               ➡️ 화살표 추가
             </Button>
             
             {/* 선택된 요소 수정/삭제 버튼 */}
             {selectedShape && (
               <div className="flex gap-2">
                 <Button 
                   onClick={() => setShowShapeModal(true)} 
                   variant="info"
                   size="sm"
                 >
                   ✏️ 도형 수정
                 </Button>
                 <Button 
                   onClick={() => deleteShape(selectedShape.id)} 
                   variant="danger"
                   size="sm"
                 >
                   🗑️ 도형 삭제
                 </Button>
               </div>
             )}
             
             {selectedArrow && (
               <div className="flex gap-2">
                 <Button 
                   onClick={() => setShowArrowModal(true)} 
                   variant="info"
                   size="sm"
                 >
                   ✏️ 화살표 수정
                 </Button>
                 <Button 
                   onClick={() => deleteArrow(selectedArrow.id)} 
                   variant="danger"
                   size="sm"
                 >
                   🗑️ 화살표 삭제
                 </Button>
               </div>
             )}
             
             <div className="flex items-center gap-2">
               <span className="text-sm font-medium text-gray-700">그리기 모드:</span>
               <select
                 value={drawMode}
                 onChange={(e) => setDrawMode(e.target.value as any)}
                 className="border border-gray-300 rounded px-3 py-1 text-sm"
               >
                 <option value="select">선택</option>
                 <option value="shape">도형</option>
                 <option value="arrow">화살표</option>
               </select>
             </div>

             {drawMode === 'shape' && (
               <div className="flex items-center gap-2">
                 <span className="text-sm font-medium text-gray-700">도형 타입:</span>
                 <select
                   value={shapeType}
                   onChange={(e) => setShapeType(e.target.value as Shape['type'])}
                   className="border border-gray-300 rounded px-3 py-1 text-sm"
                 >
                   <option value="rectangle">사각형</option>
                   <option value="circle">원</option>
                   <option value="triangle">삼각형</option>
                 </select>
               </div>
             )}
           </div>
         </Card>

        {/* Canvas 영역 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Canvas 목록 */}
          <div className="lg:col-span-1">
            <Card className="p-4">
              <h3 className="text-lg font-semibold mb-4">Canvas 목록</h3>
              {canvases.length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  생성된 Canvas가 없습니다.
                </p>
              ) : (
                <div className="space-y-2">
                                     {canvases.map((canvas) => (
                     <div
                       key={canvas.id}
                       className={`p-3 border rounded transition-colors ${
                         selectedCanvas?.id === canvas.id
                           ? 'border-blue-500 bg-blue-50'
                           : 'border-gray-200 hover:border-gray-300'
                       }`}
                     >
                       <div 
                         className="cursor-pointer"
                         onClick={() => setSelectedCanvas(canvas)}
                       >
                         <h4 className="font-medium text-gray-900">{canvas.name}</h4>
                         <p className="text-sm text-gray-600">
                           {canvas.width} × {canvas.height} • {canvas.shapes.length}개 도형 • {canvas.arrows.length}개 화살표
                         </p>
                       </div>
                       
                       {/* Canvas 삭제 버튼 */}
                       <div className="mt-2 flex justify-end">
                         <Button
                           onClick={(e) => {
                             e.stopPropagation();
                             if (confirm('정말로 이 Canvas를 삭제하시겠습니까?')) {
                               deleteCanvas(canvas.id);
                             }
                           }}
                           variant="danger"
                           size="sm"
                         >
                           🗑️ 삭제
                         </Button>
                       </div>
                     </div>
                   ))}
                </div>
              )}
            </Card>
          </div>

          {/* Canvas 뷰어 */}
          <div className="lg:col-span-2">
            <Card className="p-4">
              <h3 className="text-lg font-semibold mb-4">
                {selectedCanvas ? selectedCanvas.name : 'Canvas 선택'}
              </h3>
              
              {selectedCanvas ? (
                <div
                  className="relative border-2 border-gray-300 bg-white overflow-hidden"
                  style={{
                    width: selectedCanvas.width,
                    height: selectedCanvas.height,
                    backgroundColor: selectedCanvas.backgroundColor
                  }}
                  onClick={handleCanvasClick}
                >
                  {/* 도형들 렌더링 */}
                  {selectedCanvas.shapes.map(renderShape)}
                  
                  {/* 화살표들 렌더링 */}
                  {selectedCanvas.arrows.map(renderArrow)}
                  
                  {/* 선택된 요소 정보 */}
                  {selectedShape && (
                    <div className="absolute top-2 right-2 bg-white p-3 border rounded shadow-lg">
                      <h4 className="font-medium text-sm">선택된 도형</h4>
                      <p className="text-xs text-gray-600">
                        타입: {selectedShape.type}<br/>
                        위치: ({selectedShape.x}, {selectedShape.y})<br/>
                        크기: {selectedShape.width} × {selectedShape.height}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-16 text-gray-500">
                  Canvas를 선택하거나 새로 생성해주세요.
                </div>
              )}
            </Card>
          </div>
        </div>

        {/* 모달들 */}
        <Modal
          isOpen={showCanvasModal}
          onClose={() => setShowCanvasModal(false)}
          title="새 Canvas 생성"
        >
          <CanvasCreateForm onSubmit={createCanvas} onCancel={() => setShowCanvasModal(false)} />
        </Modal>

        <Modal
          isOpen={showShapeModal}
          onClose={() => setShowShapeModal(false)}
          title="도형 생성"
        >
          <ShapeCreateForm onSubmit={createShape} onCancel={() => setShowShapeModal(false)} />
        </Modal>

        <Modal
          isOpen={showArrowModal}
          onClose={() => setShowArrowModal(false)}
          title="화살표 생성"
        >
          <ArrowCreateForm onSubmit={createArrow} onCancel={() => setShowArrowModal(false)} />
        </Modal>

        {/* 토스트 */}
        {toast && (
          <Toast
            id="main-toast"
            type={toast.type}
            title={toast.type === 'success' ? '성공' : '오류'}
            message={toast.message}
            onClose={(id) => setToast(null)}
          />
        )}
      </div>
    </div>
  );
}

// ============================================================================
// 📝 폼 컴포넌트들
// ============================================================================

function CanvasCreateForm({ onSubmit, onCancel }: { 
  onSubmit: (data: Partial<Canvas>) => void; 
  onCancel: () => void; 
}) {
  const [formData, setFormData] = useState({
    name: '',
    width: 800,
    height: 600,
    backgroundColor: '#ffffff'
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <FormField label="Canvas 이름">
        <Input
          value={formData.name}
          onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
          placeholder="Canvas 이름을 입력하세요"
          required
        />
      </FormField>
      
      <div className="grid grid-cols-2 gap-4">
        <FormField label="너비">
          <Input
            type="number"
            value={formData.width}
            onChange={(e) => setFormData(prev => ({ ...prev, width: parseInt(e.target.value) }))}
            min="100"
            max="2000"
            required
          />
        </FormField>
        
        <FormField label="높이">
          <Input
            type="number"
            value={formData.height}
            onChange={(e) => setFormData(prev => ({ ...prev, height: parseInt(e.target.value) }))}
            min="100"
            max="2000"
            required
          />
        </FormField>
      </div>
      
      <FormField label="배경색">
        <Input
          type="color"
          value={formData.backgroundColor}
          onChange={(e) => setFormData(prev => ({ ...prev, backgroundColor: e.target.value }))}
        />
      </FormField>
      
      <div className="flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          취소
        </Button>
        <Button type="submit" variant="primary">
          생성
        </Button>
      </div>
    </form>
  );
}

function ShapeCreateForm({ onSubmit, onCancel }: { 
  onSubmit: (data: Partial<Shape>) => void; 
  onCancel: () => void; 
}) {
  const [formData, setFormData] = useState({
    type: 'rectangle' as Shape['type'],
    x: 100,
    y: 100,
    width: 100,
    height: 100,
    color: '#3B82F6',
    rotation: 0
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <FormField label="도형 타입">
        <select
          value={formData.type}
          onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as Shape['type'] }))}
          className="w-full border border-gray-300 rounded px-3 py-2"
        >
          <option value="rectangle">사각형</option>
          <option value="circle">원</option>
          <option value="triangle">삼각형</option>
        </select>
      </FormField>
      
      <div className="grid grid-cols-2 gap-4">
        <FormField label="X 좌표">
          <Input
            type="number"
            value={formData.x}
            onChange={(e) => setFormData(prev => ({ ...prev, x: parseInt(e.target.value) }))}
            required
          />
        </FormField>
        
        <FormField label="Y 좌표">
          <Input
            type="number"
            value={formData.y}
            onChange={(e) => setFormData(prev => ({ ...prev, y: parseInt(e.target.value) }))}
            required
          />
        </FormField>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <FormField label="너비">
          <Input
            type="number"
            value={formData.width}
            onChange={(e) => setFormData(prev => ({ ...prev, width: parseInt(e.target.value) }))}
            min="1"
            required
          />
        </FormField>
        
        <FormField label="높이">
          <Input
            type="number"
            value={formData.height}
            onChange={(e) => setFormData(prev => ({ ...prev, height: parseInt(e.target.value) }))}
            min="1"
            required
          />
        </FormField>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <FormField label="색상">
          <Input
            type="color"
            value={formData.color}
            onChange={(e) => setFormData(prev => ({ ...prev, color: e.target.value }))}
          />
        </FormField>
        
        <FormField label="회전 (도)">
          <Input
            type="number"
            value={formData.rotation}
            onChange={(e) => setFormData(prev => ({ ...prev, rotation: parseInt(e.target.value) }))}
            min="-360"
            max="360"
          />
        </FormField>
      </div>
      
      <div className="flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          취소
        </Button>
        <Button type="submit" variant="primary">
          생성
        </Button>
      </div>
    </form>
  );
}

function ArrowCreateForm({ onSubmit, onCancel }: { 
  onSubmit: (data: Partial<Arrow>) => void; 
  onCancel: () => void; 
}) {
  const [formData, setFormData] = useState({
    type: 'straight' as Arrow['type'],
    startX: 100,
    startY: 100,
    endX: 200,
    endY: 100,
    color: '#EF4444',
    strokeWidth: 2
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <FormField label="화살표 타입">
        <select
          value={formData.type}
          onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as Arrow['type'] }))}
          className="w-full border border-gray-300 rounded px-3 py-2"
        >
          <option value="straight">직선</option>
          <option value="curved">곡선</option>
        </select>
      </FormField>
      
      <div className="grid grid-cols-2 gap-4">
        <FormField label="시작점 X">
          <Input
            type="number"
            value={formData.startX}
            onChange={(e) => setFormData(prev => ({ ...prev, startX: parseInt(e.target.value) }))}
            required
          />
        </FormField>
        
        <FormField label="시작점 Y">
          <Input
            type="number"
            value={formData.startY}
            onChange={(e) => setFormData(prev => ({ ...prev, startY: parseInt(e.target.value) }))}
            required
          />
        </FormField>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <FormField label="끝점 X">
          <Input
            type="number"
            value={formData.endX}
            onChange={(e) => setFormData(prev => ({ ...prev, endX: parseInt(e.target.value) }))}
            required
          />
        </FormField>
        
        <FormField label="끝점 Y">
          <Input
            type="number"
            value={formData.endY}
            onChange={(e) => setFormData(prev => ({ ...prev, endY: parseInt(e.target.value) }))}
            required
          />
        </FormField>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <FormField label="색상">
          <Input
            type="color"
            value={formData.color}
            onChange={(e) => setFormData(prev => ({ ...prev, color: e.target.value }))}
          />
        </FormField>
        
        <FormField label="선 굵기">
          <Input
            type="number"
            value={formData.strokeWidth}
            onChange={(e) => setFormData(prev => ({ ...prev, strokeWidth: parseInt(e.target.value) }))}
            min="1"
            max="10"
            required
          />
        </FormField>
      </div>
      
      <div className="flex justify-end gap-2">
        <Button type="button" variant="secondary" onClick={onCancel}>
          취소
        </Button>
        <Button type="submit" variant="primary">
          생성
        </Button>
      </div>
    </form>
  );
}
