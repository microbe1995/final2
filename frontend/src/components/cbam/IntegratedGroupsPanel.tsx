'use client';

import React, { useState } from 'react';
import { ProcessChain } from '@/hooks/useProcessManager';

interface IntegratedGroupsPanelProps {
  processChains: ProcessChain[];
  integratedProcessGroups: ProcessChain[];
  isDetectingChains: boolean;
  detectionStatus: string;
  onDetectGroups: () => void;
  onLoadGroups: () => void;
  onShowGroupsModal: () => void;
}

export const IntegratedGroupsPanel: React.FC<IntegratedGroupsPanelProps> = ({
  processChains,
  integratedProcessGroups,
  isDetectingChains,
  detectionStatus,
  onDetectGroups,
  onLoadGroups,
  onShowGroupsModal,
}) => {
  const [showGroupsModal, setShowGroupsModal] = useState(false);
  return (
    <>
      {/* 탐지 상태 표시 */}
      {detectionStatus && (
        <div className="bg-gray-800 px-4 py-2 border-l-4 border-blue-500">
          <div className="text-sm text-blue-300">{detectionStatus}</div>
        </div>
      )}

      {/* 통합 공정 그룹 상태 표시 */}
      {processChains.length > 0 && (
        <div className="absolute top-4 right-4 bg-gray-800 p-4 rounded-lg border border-gray-600 max-w-sm z-10">
          <div className="flex justify-between items-center mb-2">
            <h3 className="text-white font-semibold">🔗 통합 공정 그룹</h3>
            <button
              onClick={() => setShowGroupsModal(true)}
              className="text-blue-400 hover:text-blue-300 text-sm"
            >
              📊 전체보기
            </button>
          </div>
          <div className="space-y-2">
            {processChains.map((chain) => (
              <div key={chain.id} className="bg-gray-700 p-3 rounded border border-gray-600">
                <div className="text-white font-medium">{chain.chain_name}</div>
                <div className="text-gray-300 text-sm">
                  공정 {chain.chain_length}개 | 총 배출량: {chain.total_emission || '계산중...'}
                </div>
                <div className="text-gray-400 text-xs mt-1">
                  시작: {chain.start_process_id} → 종료: {chain.end_process_id}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 통합 공정 그룹 모달 */}
      {showGroupsModal && (
        <IntegratedGroupsModal
          integratedProcessGroups={integratedProcessGroups}
          isDetectingChains={isDetectingChains}
          onDetectGroups={onDetectGroups}
          onLoadGroups={onLoadGroups}
          onClose={() => setShowGroupsModal(false)}
        />
      )}
    </>
  );
};

// 통합 공정 그룹 모달
interface IntegratedGroupsModalProps {
  integratedProcessGroups: ProcessChain[];
  isDetectingChains: boolean;
  onDetectGroups: () => void;
  onLoadGroups: () => void;
  onClose: () => void;
}

const IntegratedGroupsModal: React.FC<IntegratedGroupsModalProps> = ({
  integratedProcessGroups,
  isDetectingChains,
  onDetectGroups,
  onLoadGroups,
  onClose,
}) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-gray-800 rounded-lg p-6 w-full max-w-4xl max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-white">📊 통합 공정 그룹 목록</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-2xl"
          >
            ×
          </button>
        </div>

        <div className="mb-4 flex gap-2">
          <button
            onClick={onLoadGroups}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
          >
            🔄 목록 새로고침
          </button>
          <button
            onClick={onDetectGroups}
            disabled={isDetectingChains}
            className="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-600 text-white rounded-lg"
          >
            {isDetectingChains ? '🔍 탐지 중...' : '🔗 새로 탐지'}
          </button>
        </div>

        {integratedProcessGroups.length === 0 ? (
          <div className="text-center py-8 text-gray-400">
            <div className="text-4xl mb-4">🔍</div>
            <div className="text-lg mb-2">통합 공정 그룹이 없습니다</div>
            <div className="text-sm">&ldquo;🔗 새로 탐지&rdquo; 버튼을 클릭하여 연결된 공정들을 찾아보세요</div>
          </div>
        ) : (
          <div className="grid gap-4">
            {integratedProcessGroups.map((group: ProcessChain) => (
              <div key={group.id} className="bg-gray-700 rounded-lg p-4 border border-gray-600">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="text-lg font-semibold text-white mb-1">
                      🔗 {group.chain_name}
                    </h3>
                    <div className="text-sm text-gray-300">
                      그룹 ID: {group.id} | 공정 수: {group.chain_length}개
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-gray-400">상태</div>
                    <div className={`text-sm font-medium ${group.is_active ? 'text-green-400' : 'text-red-400'}`}>
                      {group.is_active ? '활성' : '비활성'}
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-400 mb-1">시작 공정 ID</div>
                    <div className="text-white font-medium">{group.start_process_id}</div>
                  </div>
                  <div>
                    <div className="text-gray-400 mb-1">종료 공정 ID</div>
                    <div className="text-white font-medium">{group.end_process_id}</div>
                  </div>
                </div>
                
                <div className="mt-3 text-xs text-gray-400">
                  생성일: {new Date(group.created_at).toLocaleString()}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
