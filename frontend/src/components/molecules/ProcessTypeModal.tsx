'use client';

import React from 'react';
import Icon from '@/atoms/Icon';

interface ProcessTypeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectType: (type: 'node' | 'edge') => void;
}

const ProcessTypeModal: React.FC<ProcessTypeModalProps> = ({
  isOpen,
  onClose,
  onSelectType,
}) => {
  if (!isOpen) return null;

  const handleSelectType = (type: 'node' | 'edge') => {
    onSelectType(type);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-[#1e293b] rounded-lg shadow-xl border border-[#334155] p-6 w-96 max-w-md">
        <div className="text-center mb-6">
          <h3 className="text-xl font-bold text-white mb-2">공정 요소 추가</h3>
          <p className="text-[#cbd5e1]">추가할 요소의 유형을 선택하세요</p>
        </div>
        
        <div className="space-y-4">
          {/* 도형(노드) 선택 */}
          <button
            onClick={() => handleSelectType('node')}
            className="w-full p-4 bg-[#334155] hover:bg-[#475569] rounded-lg border border-[#475569] hover:border-[#60a5fa] transition-all duration-200 group"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center group-hover:bg-blue-500 transition-colors">
                <Icon name="square" className="w-6 h-6 text-white" />
              </div>
              <div className="text-left">
                <div className="text-white font-medium text-lg">도형 (공정 단계)</div>
                <div className="text-[#94a3b8] text-sm">제조, 검사, 포장 등의 공정 단계</div>
              </div>
              <div className="text-[#60a5fa] group-hover:text-[#93c5fd] transition-colors">
                <Icon name="arrow-right" className="w-5 h-5" />
              </div>
            </div>
          </button>

          {/* 선(엣지) 선택 */}
          <button
            onClick={() => handleSelectType('edge')}
            className="w-full p-4 bg-[#334155] hover:bg-[#475569] rounded-lg border border-[#475569] hover:border-[#60a5fa] transition-all duration-200 group"
          >
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-green-600 rounded-lg flex items-center justify-center group-hover:bg-green-500 transition-colors">
                <Icon name="arrow-right" className="w-6 h-6 text-white" />
              </div>
              <div className="text-left">
                <div className="text-white font-medium text-lg">선 (공정 연결)</div>
                <div className="text-[#94a3b8] text-sm">공정 단계 간의 흐름과 연결</div>
              </div>
              <div className="text-[#60a5fa] group-hover:text-[#93c5fd] transition-colors">
                <Icon name="arrow-right" className="w-5 h-5" />
              </div>
            </div>
          </button>
        </div>

        {/* 취소 버튼 */}
        <div className="mt-6 text-center">
          <button
            onClick={onClose}
            className="px-6 py-2 text-[#94a3b8] hover:text-white transition-colors"
          >
            취소
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProcessTypeModal;
