'use client';

import React from 'react';
import Button from '@/atoms/Button';
import Icon from '@/atoms/Icon';
import Badge from '@/atoms/Badge';
import Card from './Card';

// ============================================================================
// 🎯 ControlPanel Props 인터페이스
// ============================================================================

export interface ControlPanelProps {
  // 그리드 설정
  gridSize: number;
  showGrid: boolean;
  snapToGrid: boolean;
  onGridSizeChange: (size: number) => void;
  onShowGridChange: (show: boolean) => void;
  onSnapToGridChange: (snap: boolean) => void;
  
  // 그리기 모드
  drawMode: 'shape' | 'arrow' | 'select';
  shapeType: string;
  arrowType: string;
  onDrawModeChange: (mode: 'shape' | 'arrow' | 'select') => void;
  onShapeTypeChange: (type: string) => void;
  onArrowTypeChange: (type: string) => void;
  
  // 연결 모드
  isConnecting: boolean;
  onConnectModeToggle: () => void;
  
  // 선택된 요소
  selectedShape?: any;
  selectedArrow?: any;
  onShapeEdit?: () => void;
  onShapeDelete?: () => void;
  onArrowEdit?: () => void;
  onArrowDelete?: () => void;
  
  // 액션 핸들러
  onCanvasCreate: () => void;
  onShapeCreate: () => void;
  onArrowCreate: () => void;
  
  className?: string;
}

// ============================================================================
// 🎨 ControlPanel 컴포넌트
// ============================================================================

const ControlPanel: React.FC<ControlPanelProps> = ({
  gridSize,
  showGrid,
  snapToGrid,
  onGridSizeChange,
  onShowGridChange,
  onSnapToGridChange,
  drawMode,
  shapeType,
  arrowType,
  onDrawModeChange,
  onShapeTypeChange,
  onArrowTypeChange,
  isConnecting,
  onConnectModeToggle,
  selectedShape,
  selectedArrow,
  onShapeEdit,
  onShapeDelete,
  onArrowEdit,
  onArrowDelete,
  onCanvasCreate,
  onShapeCreate,
  onArrowCreate,
  className = ''
}) => {
  // 그리드 크기 옵션
  const gridSizeOptions = [10, 20, 50, 100];
  
  // 도형 타입 옵션
  const shapeTypeOptions = [
    { value: 'process', label: '⚙️ 공정', color: '#8B5CF6' },
    { value: 'material', label: '📦 자재', color: '#06B6D4' },
    { value: 'energy', label: '⚡ 에너지', color: '#F97316' },
    { value: 'storage', label: '🏭 저장소', color: '#84CC16' },
    { value: 'transport', label: '🚚 운송', color: '#EF4444' }
  ];
  
  // 화살표 타입 옵션
  const arrowTypeOptions = [
    { value: 'straight', label: '➡️ 직선', color: '#EF4444' },
    { value: 'curved', label: '🔄 곡선', color: '#8B5CF6' },
    { value: 'bidirectional', label: '↔️ 양방향', color: '#F59E0B' },
    { value: 'dashed', label: '➖ 점선', color: '#6B7280' }
  ];

  return (
    <Card className={`p-6 ${className}`}>
      <div className="space-y-6">
        {/* 메인 액션 버튼들 */}
        <div className="flex flex-wrap gap-3">
          <Button 
            onClick={onCanvasCreate} 
            variant="primary"
            className="flex items-center gap-2"
          >
            <Icon name="add" size="sm" />
            새 Canvas
          </Button>
          
          <Button 
            onClick={onShapeCreate} 
            variant="success"
            className="flex items-center gap-2"
          >
            <Icon name="add" size="sm" />
            도형 추가
          </Button>
          
          <Button 
            onClick={onArrowCreate} 
            variant="warning"
            className="flex items-center gap-2"
          >
            <Icon name="add" size="sm" />
            화살표 추가
          </Button>
          
          <Button 
            onClick={onConnectModeToggle} 
            variant={isConnecting ? "success" : "info"}
            className="flex items-center gap-2"
          >
            <Icon name="connect" size="sm" />
            {isConnecting ? '연결 모드' : '연결 모드'}
          </Button>
        </div>

        {/* 그리드 설정 */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Icon name="grid" size="sm" />
            그리드 설정
          </h4>
          
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={showGrid}
                onChange={(e) => onShowGridChange(e.target.checked)}
                className="rounded border-gray-300"
                id="show-grid"
              />
              <label htmlFor="show-grid" className="text-sm text-gray-600">
                그리드 표시
              </label>
            </div>
            
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={snapToGrid}
                onChange={(e) => onSnapToGridChange(e.target.checked)}
                className="rounded border-gray-300"
                id="snap-grid"
              />
              <label htmlFor="snap-grid" className="text-sm text-gray-600">
                그리드 스냅
              </label>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">크기:</span>
              <select
                value={gridSize}
                onChange={(e) => onGridSizeChange(Number(e.target.value))}
                className="border border-gray-300 rounded px-2 py-1 text-xs w-16"
              >
                {gridSizeOptions.map(size => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* 그리기 모드 설정 */}
        <div className="border-t pt-4">
          <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Icon name="select" size="sm" />
            그리기 모드
          </h4>
          
          <div className="flex flex-wrap gap-2">
            {[
              { mode: 'select', label: '선택', icon: 'select' },
              { mode: 'shape', label: '도형', icon: 'add' },
              { mode: 'arrow', label: '화살표', icon: 'add' }
            ].map(({ mode, label, icon }) => (
              <Button
                key={mode}
                variant={drawMode === mode ? 'primary' : 'secondary'}
                size="sm"
                onClick={() => onDrawModeChange(mode as any)}
                className="flex items-center gap-1"
              >
                <Icon name={icon} size="sm" />
                {label}
              </Button>
            ))}
          </div>
        </div>

        {/* 도형 타입 선택 */}
        {drawMode === 'shape' && (
          <div className="border-t pt-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">도형 타입</h4>
            <div className="flex flex-wrap gap-2">
              {shapeTypeOptions.map(({ value, label, color }) => (
                <Button
                  key={value}
                  variant={shapeType === value ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => onShapeTypeChange(value)}
                  className="flex items-center gap-2"
                  style={{ 
                    backgroundColor: shapeType === value ? color : undefined,
                    borderColor: color
                  }}
                >
                  {label}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* 화살표 타입 선택 */}
        {drawMode === 'arrow' && (
          <div className="border-t pt-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">화살표 타입</h4>
            <div className="flex flex-wrap gap-2">
              {arrowTypeOptions.map(({ value, label, color }) => (
                <Button
                  key={value}
                  variant={arrowType === value ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => onArrowTypeChange(value)}
                  className="flex items-center gap-2"
                  style={{ 
                    backgroundColor: arrowType === value ? color : undefined,
                    borderColor: color
                  }}
                >
                  {label}
                </Button>
              ))}
            </div>
          </div>
        )}

        {/* 선택된 요소 수정/삭제 */}
        {(selectedShape || selectedArrow) && (
          <div className="border-t pt-4">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">선택된 요소</h4>
            <div className="flex flex-wrap gap-2">
              {selectedShape && (
                <>
                  <Button 
                    onClick={onShapeEdit} 
                    variant="info"
                    size="sm"
                    className="flex items-center gap-1"
                  >
                    <Icon name="edit" size="sm" />
                    도형 수정
                  </Button>
                  <Button 
                    onClick={onShapeDelete} 
                    variant="danger"
                    size="sm"
                    className="flex items-center gap-1"
                  >
                    <Icon name="delete" size="sm" />
                    도형 삭제
                  </Button>
                </>
              )}
              
              {selectedArrow && (
                <>
                  <Button 
                    onClick={onArrowEdit} 
                    variant="info"
                    size="sm"
                    className="flex items-center gap-1"
                  >
                    <Icon name="edit" size="sm" />
                    화살표 수정
                  </Button>
                  <Button 
                    onClick={onArrowDelete} 
                    variant="danger"
                    size="sm"
                    className="flex items-center gap-1"
                  >
                    <Icon name="delete" size="sm" />
                    화살표 삭제
                  </Button>
                </>
              )}
            </div>
          </div>
        )}

        {/* 연결 모드 상태 표시 */}
        {isConnecting && (
          <div className="border-t pt-4">
            <div className="flex items-center gap-2 px-3 py-2 bg-green-100 text-green-800 rounded-lg">
              <Icon name="connect" size="sm" />
              <span className="text-sm font-medium">연결 모드 활성화</span>
              <Badge variant="success" size="sm">
                연결 중
              </Badge>
            </div>
          </div>
        )}
      </div>
    </Card>
  );
};

export default ControlPanel;
