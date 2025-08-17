'use client';

import React from 'react';

interface ProcessFlowHeaderProps {
  serviceStatus: any;
  isReadOnly: boolean;
  onToggleReadOnly: () => void;
  onExport: () => void;
  onSaveToBackend: () => void;
  onLoadFromBackend: () => void;
  onClearFlow: () => void;
  savedCanvases: any[];
  isLoadingCanvases: boolean;
  currentCanvasId: string | null;
}

const ProcessFlowHeader: React.FC<ProcessFlowHeaderProps> = ({
  serviceStatus,
  isReadOnly,
  onToggleReadOnly,
  onExport,
  onSaveToBackend,
  onLoadFromBackend,
  onClearFlow,
  savedCanvases,
  isLoadingCanvases,
  currentCanvasId,
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
              onClick={onToggleReadOnly}
              className={`px-4 py-2 rounded-lg text-sm font-medium ${
                isReadOnly
                  ? 'bg-blue-500 text-white hover:bg-blue-600'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {isReadOnly ? '편집 모드' : '읽기 전용'}
            </button>
            
            <button
              onClick={onExport}
              className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 text-sm font-medium"
            >
              내보내기
            </button>
            
            <button
              onClick={onSaveToBackend}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
            >
              백엔드 저장
            </button>
            
            <button
              onClick={onLoadFromBackend}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 text-sm font-medium"
            >
              백엔드 로드
            </button>
            
            <button
              onClick={onClearFlow}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium"
            >
              초기화
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProcessFlowHeader;
