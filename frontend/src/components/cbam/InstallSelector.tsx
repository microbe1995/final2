'use client';

import React, { useState } from 'react';
import { Install } from '@/hooks/useProcessManager';
import { Node, Edge } from '@xyflow/react';

interface InstallSelectorProps {
  installs: Install[];
  selectedInstall: Install | null;
  installCanvases: {[key: number]: {nodes: Node[], edges: Edge[]}};
  activeInstallId: number | null;
  onInstallSelect: (install: Install) => void;
  onAddInstall: () => void;
}

export const InstallSelector: React.FC<InstallSelectorProps> = ({
  installs,
  selectedInstall,
  installCanvases,
  activeInstallId,
  onInstallSelect,
  onAddInstall,
}) => {
  const [showInstallModal, setShowInstallModal] = useState(false);

  return (
    <>
      {/* 사업장 선택 카드 */}
      <div className="bg-gray-800 p-4">
        <div className="flex items-center gap-4">
          {/* 사업장 추가 카드 */}
          <div 
            className="w-48 h-24 bg-gray-700 border-2 border-dashed border-gray-500 rounded-lg flex flex-col items-center justify-center cursor-pointer hover:border-blue-400 hover:bg-gray-600 transition-colors"
            onClick={onAddInstall}
          >
            <div className="text-4xl text-gray-400 mb-1">+</div>
            <div className="text-sm text-gray-300">사업장 추가</div>
          </div>
          
          {/* 모든 사업장 카드들 */}
          {installs.map((install) => {
            const isActive = activeInstallId === install.id;
            const canvasData = installCanvases[install.id];
            const nodeCount = canvasData?.nodes?.length || 0;
            const hasCanvas = !!canvasData;
            
            return (
              <div
                key={install.id}
                className={`w-48 h-24 rounded-lg flex flex-col justify-center p-3 cursor-pointer transition-all ${
                  isActive 
                    ? 'bg-blue-600 border-2 border-blue-400 shadow-lg' 
                    : hasCanvas
                    ? 'bg-gray-700 border-2 border-gray-600 hover:border-gray-500'
                    : 'bg-gray-600 border-2 border-gray-500 hover:border-gray-400 opacity-75'
                }`}
                onClick={() => onInstallSelect(install)}
              >
                <div className="flex items-center justify-between mb-1">
                  <div className="font-semibold text-white text-sm">{install.install_name}</div>
                  <div className="text-xs text-gray-300">
                    {hasCanvas ? `${nodeCount}개 노드` : '새 캔버스'}
                  </div>
                </div>
                <div className="text-xs text-gray-300">
                  {install.reporting_year && `${install.reporting_year}년`}
                </div>
                {isActive && (
                  <div className="text-xs text-blue-200 mt-1">활성</div>
                )}
                {!hasCanvas && (
                  <div className="text-xs text-gray-400 mt-1">미사용</div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* 사업장 선택 모달 */}
      {showInstallModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black/60 z-50">
          <div className="bg-gray-800 p-6 rounded-lg shadow-lg max-w-md w-full mx-4 border border-gray-700">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-white">사업장 선택</h3>
              <button onClick={() => setShowInstallModal(false)} className="text-gray-400 hover:text-gray-200">✕</button>
            </div>
            <div className="space-y-2">
              {installs.length > 0 ? (
                installs.map((install) => (
                  <div
                    key={install.id}
                    className="p-3 border border-gray-600 rounded-lg cursor-pointer hover:bg-gray-700 hover:border-blue-400 transition-colors"
                    onClick={() => {
                      onInstallSelect(install);
                      setShowInstallModal(false);
                    }}
                  >
                    <div className="font-medium text-white">{install.install_name}</div>
                    <div className="text-sm text-gray-300">ID: {install.id}</div>
                    {install.reporting_year && (
                      <div className="text-sm text-gray-300">보고기간: {install.reporting_year}년</div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center py-4 text-gray-400">
                  등록된 사업장이 없습니다.
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};
