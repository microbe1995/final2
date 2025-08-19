'use client';

import React from 'react';
import Button from '@/atoms/Button';
import Badge from '@/atoms/Badge';

interface ProcessFlowHeaderProps {
  isReadOnly: boolean;
  onToggleReadOnly: () => void;
  onExport: () => void;
  onImport: () => void;
  onClearFlow: () => void;
  nodeCount: number;
  edgeCount: number;
}

const ProcessFlowHeader: React.FC<ProcessFlowHeaderProps> = ({
  isReadOnly,
  onToggleReadOnly,
  onExport,
  onImport,
  onClearFlow,
  nodeCount,
  edgeCount,
}) => {
  return (
    <div className="bg-[#1e293b] shadow-sm border-b border-[#334155]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div>
            <h1 className="text-2xl font-bold text-white">공정도 관리</h1>
            <p className="text-sm text-[#cbd5e1]">
              React Flow 기반의 인터랙티브 공정도 에디터
            </p>
            <div className="flex items-center gap-3 mt-2">
              <span className="text-xs text-[#94a3b8]">
                노드: {nodeCount} | 엣지: {edgeCount}
              </span>
              <Badge variant={isReadOnly ? 'secondary' : 'primary'}>
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

            {/* 파일 관리 */}
            <Button
              variant="primary"
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
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessFlowHeader;