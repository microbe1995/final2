'use client';

import React from 'react';
import Button from '@/atoms/Button';
import Badge from '@/atoms/Badge';
import Icon from '../atoms/Icon';

interface ProcessFlowHeaderProps {
  serviceStatus: any;
  isReadOnly: boolean;
  onToggleReadOnly: () => void;
  onExport: () => void;
  onImport: () => void;
  onSaveToBackend: () => void;
  onLoadFromBackend: () => void;
  onClearFlow: () => void;
  savedCanvases: any[];
  isLoadingCanvases: boolean;
  currentCanvasId: string | null;
  nodeCount: number;
  edgeCount: number;
  // Sub Flow 기능 추가
  onAddGroupNode?: () => void;
  onToggleGroupExpansion?: (groupId: string) => void;
  onEdgeZIndexChange?: (zIndex: number) => void;
  edgeZIndex?: number;
  expandedGroups?: Set<string>;
}

const ProcessFlowHeader: React.FC<ProcessFlowHeaderProps> = ({
  serviceStatus,
  isReadOnly,
  onToggleReadOnly,
  onExport,
  onImport,
  onSaveToBackend,
  onLoadFromBackend,
  onClearFlow,
  savedCanvases,
  isLoadingCanvases,
  currentCanvasId,
  nodeCount,
  edgeCount,
  // Sub Flow 기능 추가
  onAddGroupNode,
  onToggleGroupExpansion,
  onEdgeZIndexChange,
  edgeZIndex,
  expandedGroups,
}) => {
  return (
    <div className="bg-[#1e293b] shadow-sm border-b border-[#334155]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div>
            <h1 className="text-2xl font-bold text-white">공정도 관리</h1>
            <p className="text-sm text-[#cbd5e1]">
              MSA 기반 React Flow 인터랙티브 공정도 에디터
            </p>
            <div className="flex items-center gap-3 mt-2">
              {/* MSA 서비스 상태 */}
              <div className="flex items-center gap-1">
                <div className={`w-2 h-2 rounded-full ${
                  serviceStatus?.status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                }`} />
                <span className="text-xs text-[#94a3b8]">
                  {serviceStatus?.status === 'healthy' ? 'MSA 연결됨' : 'MSA 연결 안됨'}
                </span>
              </div>
              
              <span className="text-xs text-[#94a3b8]">
                노드: {nodeCount} | 엣지: {edgeCount}
              </span>
              
              {currentCanvasId && (
                <Badge variant="info" size="sm">
                  백엔드 동기화 ON
                </Badge>
              )}
              
              <Badge variant={isReadOnly ? 'secondary' : 'primary'} size="sm">
                {isReadOnly ? '읽기 전용' : '편집 모드'}
              </Badge>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* 모드 토글 */}
            <Button
              variant="secondary"
              size="sm"
              onClick={onToggleReadOnly}
            >
              {isReadOnly ? '편집 모드' : '읽기 전용'}
            </Button>

            {/* MSA 백엔드 관리 */}
            <Button
              variant="primary"
              size="sm"
              onClick={onSaveToBackend}
              disabled={isLoadingCanvases}
            >
              백엔드 저장
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={() => onLoadFromBackend()}
              disabled={isLoadingCanvases}
            >
              백엔드 로드
            </Button>

            {/* 파일 관리 (로컬) */}
            <Button
              variant="secondary"
              size="sm"
              onClick={onExport}
            >
              내보내기
            </Button>

            <Button
              variant="secondary"
              size="sm"
              onClick={onImport}
            >
              가져오기
            </Button>

            {/* 초기화 */}
            <Button
              variant="danger"
              size="sm"
              onClick={onClearFlow}
            >
              초기화
            </Button>

            {/* Sub Flow 컨트롤 */}
            {onAddGroupNode && (
              <Button
                variant="secondary"
                size="sm"
                onClick={onAddGroupNode}
                className="bg-purple-600 hover:bg-purple-700 text-white"
              >
                <Icon name="folder-plus" className="w-4 h-4 mr-2" />
                그룹 추가
              </Button>
            )}

            {/* Edge Z-Index 컨트롤 */}
            {onEdgeZIndexChange && (
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-300">Edge Z:</span>
                <input
                  type="range"
                  min="1"
                  max="1000"
                  value={edgeZIndex || 1}
                  onChange={(e) => onEdgeZIndexChange(Number(e.target.value))}
                  className="w-20 h-2 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                />
                <span className="text-xs text-gray-300 w-8">{edgeZIndex || 1}</span>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessFlowHeader;