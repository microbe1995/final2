'use client';

import React from 'react';
import Card from '@/molecules/Card';
import ProcessShape from '@/molecules/ProcessShape';
import FlowArrow from '@/molecules/FlowArrow';
import Badge from '@/atoms/Badge';
import Icon from '@/atoms/Icon';

// ============================================================================
// 🎯 CanvasViewer Props 인터페이스
// ============================================================================

export interface CanvasViewerProps {
  canvas: any;
  selectedShape?: any;
  selectedArrow?: any;
  isConnecting: boolean;
  connectionStart?: any;
  showGrid: boolean;
  gridSize: number;
  snapToGrid: boolean;
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
  className?: string;
}

// ============================================================================
// 🎨 CanvasViewer 컴포넌트
// ============================================================================

const CanvasViewer: React.FC<CanvasViewerProps> = ({
  canvas,
  selectedShape,
  selectedArrow,
  isConnecting,
  connectionStart,
  showGrid,
  gridSize,
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
  className = ''
}) => {
  // 그리드 렌더링
  const renderGrid = () => {
    if (!showGrid || !canvas) return null;

    const gridLines = [];
    const { width, height } = canvas;

    // 세로선
    for (let x = 0; x <= width; x += gridSize) {
      gridLines.push(
        <div
          key={`v-${x}`}
          style={{
            position: 'absolute',
            left: x,
            top: 0,
            width: 1,
            height: height,
            backgroundColor: '#E5E7EB',
            opacity: 0.3,
            pointerEvents: 'none'
          }}
        />
      );
    }

    // 가로선
    for (let y = 0; y <= height; y += gridSize) {
      gridLines.push(
        <div
          key={`h-${y}`}
          style={{
            position: 'absolute',
            left: 0,
            top: y,
            width: width,
            height: 1,
            backgroundColor: '#E5E7EB',
            opacity: 0.3,
            pointerEvents: 'none'
          }}
        />
      );
    }

    return gridLines;
  };

  // 선택된 요소 정보 패널
  const renderSelectionInfo = () => {
    if (!selectedShape && !selectedArrow) return null;

    const element = selectedShape || selectedArrow;
    const isShape = !!selectedShape;

    return (
      <div className="absolute top-2 right-2 bg-white p-4 border rounded-lg shadow-lg max-w-xs z-20">
        <h4 className="font-medium text-sm mb-3 flex items-center gap-2">
          <Icon name={isShape ? 'select' : 'connect'} size="sm" />
          선택된 {isShape ? '공정' : '화살표'}
        </h4>
        
        <div className="text-xs text-gray-600 space-y-2">
          <div className="flex justify-between">
            <span className="font-medium">타입:</span>
            <Badge variant="info" size="sm">
              {element.type}
            </Badge>
          </div>
          
          {element.label && (
            <div className="flex justify-between">
              <span className="font-medium">라벨:</span>
              <span>{element.label}</span>
            </div>
          )}
          
          {isShape && (
            <>
              <div className="flex justify-between">
                <span className="font-medium">위치:</span>
                <span>({element.x}, {element.y})</span>
              </div>
              <div className="flex justify-between">
                <span className="font-medium">크기:</span>
                <span>{element.width} × {element.height}</span>
              </div>
              {element.processType && (
                <div className="flex justify-between">
                  <span className="font-medium">공정 유형:</span>
                  <Badge variant="success" size="sm">
                    {element.processType}
                  </Badge>
                </div>
              )}
              {element.materialType && (
                <div className="flex justify-between">
                  <span className="font-medium">자재 유형:</span>
                  <Badge variant="warning" size="sm">
                    {element.materialType}
                  </Badge>
                </div>
              )}
              {element.energyType && (
                <div className="flex justify-between">
                  <span className="font-medium">에너지 유형:</span>
                  <Badge variant="error" size="sm">
                    {element.energyType}
                  </Badge>
                </div>
              )}
              {element.capacity && (
                <div className="flex justify-between">
                  <span className="font-medium">용량:</span>
                  <span>{element.capacity} {element.unit || ''}</span>
                </div>
              )}
              {element.efficiency && (
                <div className="flex justify-between">
                  <span className="font-medium">효율:</span>
                  <Badge variant="success" size="sm">
                    {element.efficiency}%
                  </Badge>
                </div>
              )}
            </>
          )}
          
          {!isShape && (
            <>
              <div className="flex justify-between">
                <span className="font-medium">흐름 유형:</span>
                <Badge variant="info" size="sm">
                  {element.flowType || 'material'}
                </Badge>
              </div>
              {element.flowRate && (
                <div className="flex justify-between">
                  <span className="font-medium">유량:</span>
                  <span>{element.flowRate} {element.flowUnit || ''}</span>
                </div>
              )}
              {element.direction && (
                <div className="flex justify-between">
                  <span className="font-medium">방향:</span>
                  <Badge variant="warning" size="sm">
                    {element.direction}
                  </Badge>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    );
  };

  // 연결 모드 안내
  const renderConnectionGuide = () => {
    if (!isConnecting) return null;

    return (
      <div className="absolute top-2 left-2 z-20">
        {!connectionStart ? (
          <div className="bg-green-100 text-green-800 px-4 py-3 rounded-lg text-sm font-medium flex items-center gap-2">
            <Icon name="connect" size="sm" />
            연결할 첫 번째 공정을 클릭하세요
          </div>
        ) : (
          <div className="bg-blue-100 text-blue-800 px-4 py-3 rounded-lg text-sm font-medium flex items-center gap-2">
            <Icon name="connect" size="sm" />
            연결할 두 번째 공정을 클릭하세요
          </div>
        )}
      </div>
    );
  };

  // 그리드 정보
  const renderGridInfo = () => {
    return (
      <div className="absolute bottom-2 left-2 bg-gray-100 text-gray-600 px-3 py-2 rounded-lg text-xs font-medium flex items-center gap-2">
        <Icon name="grid" size="sm" />
        그리드: {gridSize}px | 스냅: {snapToGrid ? 'ON' : 'OFF'}
      </div>
    );
  };

  if (!canvas) {
    return (
      <Card className={`p-8 text-center ${className}`}>
        <div className="py-16 text-gray-500">
          <Icon name="select" size="xl" className="mx-auto mb-4 text-gray-400" />
          <p className="text-lg font-medium">Canvas를 선택하거나 새로 생성해주세요</p>
          <p className="text-sm text-gray-400 mt-2">
            공정도를 그리기 위한 Canvas가 필요합니다
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card className={`p-4 ${className}`}>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <Icon name="select" size="sm" />
        {canvas.name}
      </h3>
      
      <div
        className="relative border-2 border-gray-300 bg-white overflow-hidden"
        style={{
          width: canvas.width,
          height: canvas.height,
          backgroundColor: canvas.backgroundColor
        }}
        onClick={onCanvasClick}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
      >
        {/* 도형들 렌더링 */}
        {canvas.shapes.map((shape: any) => (
          <ProcessShape
            key={shape.id}
            {...shape}
            isSelected={selectedShape?.id === shape.id}
            isConnectionStart={connectionStart?.id === shape.id}
            isConnecting={isConnecting}
            onClick={() => onShapeClick(shape)}
            onMouseDown={(e) => onShapeMouseDown(e, shape)}
            onMouseEnter={() => onShapeMouseEnter(shape)}
            onMouseLeave={onShapeMouseLeave}
          />
        ))}
        
        {/* 화살표들 렌더링 */}
        {canvas.arrows.map((arrow: any) => (
          <FlowArrow
            key={arrow.id}
            {...arrow}
            isSelected={selectedArrow?.id === arrow.id}
            onClick={() => onArrowClick(arrow)}
            onMouseEnter={() => onArrowMouseEnter(arrow)}
            onMouseLeave={onArrowMouseLeave}
          />
        ))}
        
        {/* 그리드 렌더링 */}
        {renderGrid()}
        
        {/* 선택된 요소 정보 */}
        {renderSelectionInfo()}
        
        {/* 연결 모드 안내 */}
        {renderConnectionGuide()}
        
        {/* 그리드 정보 */}
        {renderGridInfo()}
      </div>
    </Card>
  );
};

export default CanvasViewer;
