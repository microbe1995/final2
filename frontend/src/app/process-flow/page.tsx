'use client';

import React, { useState } from 'react';
import ConnectedReactFlow from '@/components/templates/ConnectedReactFlow';
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
    <div className="h-screen flex flex-col bg-gray-100">
      {/* 헤더 */}
      <header className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              연결된 프로세스 플로우
            </h1>
            <p className="text-sm text-gray-600 mt-1">
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
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            >
              새 플로우
            </button>
            
            <div className="text-sm text-gray-500">
              {currentFlowId ? `플로우 ID: ${currentFlowId}` : '새 플로우'}
            </div>
          </div>
        </div>
      </header>

      {/* 메인 플로우 영역 */}
      <main className="flex-1">
        <ConnectedReactFlow
          flowId={currentFlowId}
          autoSave={autoSave}
          saveInterval={10000} // 10초마다 자동 저장
        />
      </main>
      
      {/* 하단 정보 바 */}
      <footer className="bg-white border-t border-gray-200 px-6 py-2">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <div className="flex items-center gap-4">
            <span>🔗 백엔드 연동됨</span>
            <span>💾 PostgreSQL 저장</span>
            <span>⚡ 자동 저장: {autoSave ? 'ON' : 'OFF'}</span>
          </div>
          <div>
            React Flow + FastAPI + PostgreSQL
          </div>
        </div>
      </footer>
    </div>
  );
}