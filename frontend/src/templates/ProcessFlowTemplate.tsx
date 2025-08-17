'use client';

import React from 'react';
import ControlPanel from '@/molecules/ControlPanel';
import CanvasViewer from '@/organisms/CanvasViewer';
import Card from '@/molecules/Card';
import Icon from '@/atoms/Icon';
import Badge from '@/atoms/Badge';

// ============================================================================
// 🎯 ProcessFlowTemplate Props 인터페이스
// ============================================================================

export interface ProcessFlowTemplateProps {
  // Canvas 관련
  canvases: any[];
  selectedCanvas: any;
  onCanvasSelect: (canvas: any) => void;
  onCanvasDelete: (canvasId: string) => void;
  
  // 상태 관리
  selectedShape?: any;
  selectedArrow?: any;
  isConnecting: boolean;
  connectionStart?: any;
  drawMode: 'shape' | 'arrow' | 'select';
  shapeType: string;
  arrowType: string;
  gridSize: number;
  showGrid: boolean;
  snapToGrid: boolean;
  
  // 이벤트 핸들러
  onCanvasClick: (e: React.MouseEvent) => void;
  onMouseMove: (e: React.MouseEvent) => void;
  onMouseUp: () => void;
  onShapeClick: (shape: any) => void;
  onShapeMouseDown: (e: React.MouseEvent, shape: any) => void;
  onShapeMouseEnter: (shape: any) => void;
  onShapeMouseLeave: () => void;
  onArrowClick: (arrow: any) => void;
  onArrowMouseEnter: (arrow: any) => void;
  onArrowMouseLeave: () => void;
  
  // 설정 변경 핸들러
  onGridSizeChange: (size: number) => void;
  onShowGridChange: (show: boolean) => void;
  onSnapToGridChange: (snap: boolean) => void;
  onDrawModeChange: (mode: 'shape' | 'arrow' | 'select') => void;
  onShapeTypeChange: (type: string) => void;
  onArrowTypeChange: (type: string) => void;
  onConnectModeToggle: () => void;
  
  // 액션 핸들러
  onCanvasCreate: () => void;
  onShapeCreate: () => void;
  onArrowCreate: () => void;
  onShapeEdit?: () => void;
  onShapeDelete?: () => void;
  onArrowEdit?: () => void;
  onArrowDelete?: () => void;
  
  className?: string;
}

// ============================================================================
// 🎨 ProcessFlowTemplate 컴포넌트
// ============================================================================

const ProcessFlowTemplate: React.FC<ProcessFlowTemplateProps> = ({
  canvases,
  selectedCanvas,
  onCanvasSelect,
  onCanvasDelete,
  selectedShape,
  selectedArrow,
  isConnecting,
  connectionStart,
  drawMode,
  shapeType,
  arrowType,
  gridSize,
  showGrid,
  snapToGrid,
  onCanvasClick,
  onMouseMove,
  onMouseUp,
  onShapeClick,
  onShapeMouseDown,
  onShapeMouseEnter,
  onShapeMouseLeave,
  onArrowClick,
  onArrowMouseEnter,
  onArrowMouseLeave,
  onGridSizeChange,
  onShowGridChange,
  onSnapToGridChange,
  onDrawModeChange,
  onShapeTypeChange,
  onArrowTypeChange,
  onConnectModeToggle,
  onCanvasCreate,
  onShapeCreate,
  onArrowCreate,
  onShapeEdit,
  onShapeDelete,
  onArrowEdit,
  onArrowDelete,
  className = ''
}) => {
  return (
    <div className={`min-h-screen bg-gray-50 text-gray-900 p-6 ${className}`}>
      <div className="max-w-7xl mx-auto">
        {/* 헤더 */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2 flex items-center gap-3">
            <Icon name="process" size="lg" />
            Cal_boundary - 공정도 기반 탄소배출량 계산
          </h1>
          <p className="text-lg text-gray-600">
            공정도를 그리고 산정경계를 설정하여 탄소배출량을 계산할 수 있는 전문 도구입니다.
          </p>
          
          {/* 상태 표시 */}
          <div className="mt-6 flex flex-wrap gap-3">
            <Badge variant="info" size="sm">
              공정 필드: {canvases.length}개
            </Badge>
            {selectedCanvas && (
              <Badge variant="default" size="sm">
                선택된 공정 필드: {selectedCanvas.name}
              </Badge>
            )}
            {selectedShape && (
              <Badge variant="success" size="sm">
                선택된 도형: {selectedShape.label}
              </Badge>
            )}
            {selectedArrow && (
              <Badge variant="warning" size="sm">
                선택된 화살표: {selectedArrow.label || selectedArrow.id}
              </Badge>
            )}
            {isConnecting && (
              <Badge variant="warning" size="sm">
                연결 모드
              </Badge>
            )}
            <Badge variant="default" size="sm">
              그리드: {gridSize}px
            </Badge>
          </div>
        </div>

        {/* 메인 레이아웃 */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* 왼쪽 사이드바 - 컨트롤 패널 */}
          <div className="lg:col-span-1">
            <ControlPanel
              gridSize={gridSize}
              showGrid={showGrid}
              snapToGrid={snapToGrid}
              onGridSizeChange={onGridSizeChange}
              onShowGridChange={onShowGridChange}
              onSnapToGridChange={onSnapToGridChange}
              drawMode={drawMode}
              shapeType={shapeType}
              arrowType={arrowType}
              onDrawModeChange={onDrawModeChange}
              onShapeTypeChange={onShapeTypeChange}
              onArrowTypeChange={onArrowTypeChange}
              isConnecting={isConnecting}
              onConnectModeToggle={onConnectModeToggle}
              selectedShape={selectedShape}
              selectedArrow={selectedArrow}
              onShapeEdit={onShapeEdit}
              onShapeDelete={onShapeDelete}
              onArrowEdit={onArrowEdit}
              onArrowDelete={onArrowDelete}
              onCanvasCreate={onCanvasCreate}
              onShapeCreate={onShapeCreate}
              onArrowCreate={onArrowCreate}
            />
          </div>

          {/* 메인 콘텐츠 영역 */}
          <div className="lg:col-span-3">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Canvas 목록 */}
              <div className="lg:col-span-1">
                <Card className="p-4">
                  <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                    <Icon name="select" size="sm" />
                    공정 필드 목록
                  </h3>
                  
                  {canvases.length === 0 ? (
                    <div className="text-center py-8 text-gray-500">
                      <Icon name="add" size="xl" className="mx-auto mb-3 text-gray-400" />
                      <p className="text-sm">생성된 공정 필드가 없습니다.</p>
                      <p className="text-xs text-gray-400 mt-1">
                        새 공정 필드를 생성하여 공정도를 시작하세요
                      </p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {canvases.map((canvas) => (
                        <div
                          key={canvas.id}
                          className={`p-3 border rounded-lg transition-all cursor-pointer ${
                            selectedCanvas?.id === canvas.id
                              ? 'border-blue-500 bg-blue-50 shadow-md'
                              : 'border-gray-200 hover:border-gray-400 hover:shadow-sm'
                          }`}
                          onClick={() => onCanvasSelect(canvas)}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <h4 className="font-medium text-gray-900 mb-1 text-sm">
                                {canvas.name}
                              </h4>
                              <div className="text-xs text-gray-500 space-y-1">
                                <p>{canvas.width} × {canvas.height}</p>
                                <div className="flex gap-2">
                                  <Badge variant="default" size="sm">도형: {canvas.shapes.length}</Badge>
                                  <Badge variant="default" size="sm">화살표: {canvas.arrows.length}</Badge>
                                </div>
                              </div>
                            </div>
                            
                            {/* Canvas 삭제 버튼 */}
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                if (window.confirm(`'${canvas.name}' 공정 필드를 삭제하시겠습니까?`)) {
                                  onCanvasDelete(canvas.id);
                                }
                              }}
                              className="text-red-600 hover:text-red-800 p-1 rounded hover:bg-red-50 transition-all"
                              title="공정 필드 삭제"
                            >
                              <Icon name="delete" size="sm" />
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </Card>
              </div>

              {/* Canvas 뷰어 */}
              <div className="lg:col-span-2">
                <CanvasViewer
                  canvas={selectedCanvas}
                  selectedShape={selectedShape}
                  selectedArrow={selectedArrow}
                  isConnecting={isConnecting}
                  connectionStart={connectionStart}
                  showGrid={showGrid}
                  gridSize={gridSize}
                  snapToGrid={snapToGrid}
                  onCanvasClick={onCanvasClick}
                  onMouseMove={onMouseMove}
                  onMouseUp={onMouseUp}
                  onShapeClick={onShapeClick}
                  onShapeMouseDown={onShapeMouseDown}
                  onShapeMouseEnter={onShapeMouseEnter}
                  onShapeMouseLeave={onShapeMouseLeave}
                  onArrowClick={onArrowClick}
                  onArrowMouseEnter={onArrowMouseEnter}
                  onArrowMouseLeave={onArrowMouseLeave}
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessFlowTemplate;
