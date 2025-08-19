'use client';

import React, { useState } from 'react';
import ConnectedReactFlow from '@/components/templates/ConnectedReactFlow';
import ErrorBoundary from '@/components/templates/ErrorBoundary';
import '@/styles/reactflow-theme.css';

// ============================================================================
// 🎯 연결된 프로세스 플로우 페이지
// ============================================================================

export default function ProcessFlowPage() {
  const [currentFlowId, setCurrentFlowId] = useState<string | undefined>(undefined);
  const [autoSave, setAutoSave] = useState(true);

  const handleCreateNewFlow = () => {
    setCurrentFlowId(undefined); // 새 플로우 생성
  };

  const handleLoadFlow = (flowId: string) => {
    setCurrentFlowId(flowId);
  };

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white border-b border-gray-300 px-6 py-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-blue-900">
              연결된 프로세스 플로우
            </h1>
            <p className="text-sm text-blue-600 mt-1">
              백엔드와 연동된 영구 저장 가능한 React Flow 다이어그램
            </p>
          </div>
          
          {/* 컨트롤 버튼들 */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <label className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={autoSave}
                  onChange={(e) => setAutoSave(e.target.checked)}
                  className="rounded"
                />
                자동 저장
              </label>
            </div>
            
            <button
              onClick={handleCreateNewFlow}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
            >
              새 플로우
            </button>
            
            <div className="text-sm text-blue-600 font-medium">
              {currentFlowId ? `플로우 ID: ${currentFlowId}` : '새 플로우'}
            </div>
          </div>
        </div>
      </header>

      {/* 메인 플로우 영역 */}
      <main className="flex-1">
        <ErrorBoundary>
          <ConnectedReactFlow
            key={currentFlowId || 'new-flow'}
            flowId={currentFlowId}
            autoSave={autoSave}
            saveInterval={10000} // 10초마다 자동 저장
          />
        </ErrorBoundary>
      </main>
      
      {/* 하단 정보 바 */}
      <footer className="bg-white border-t border-gray-300 px-6 py-3 shadow-sm">
        <div className="flex items-center justify-between text-sm text-blue-700">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              백엔드 연동됨
            </span>
            <span className="flex items-center gap-1">
              <span className="w-2 h-2 bg-blue-500 rounded-full"></span>
              PostgreSQL 저장
            </span>
            <span className="flex items-center gap-1">
              <span className={`w-2 h-2 rounded-full ${autoSave ? 'bg-green-500' : 'bg-gray-400'}`}></span>
              자동 저장: {autoSave ? 'ON' : 'OFF'}
            </span>
          </div>
          <div className="text-blue-600 font-medium">
            React Flow + FastAPI + PostgreSQL
          </div>
        </div>
      </footer>
    </div>
  );
}