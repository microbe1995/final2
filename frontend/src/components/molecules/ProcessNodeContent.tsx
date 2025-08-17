'use client';

import React from 'react';
interface ProcessNodeContentProps {
  data: any; // 백엔드 API 응답을 그대로 사용
  isEditing: boolean;
  editLabel: string;
  editDescription: string;
  onLabelChange: (value: string) => void;
  onDescriptionChange: (value: string) => void;
  className?: string;
}

const ProcessNodeContent: React.FC<ProcessNodeContentProps> = ({
  data,
  isEditing,
  editLabel,
  editDescription,
  onLabelChange,
  onDescriptionChange,
  className = ''
}) => {
  const baseClasses = 'space-y-3';
  const finalClasses = `${baseClasses} ${className}`.trim();

  return (
    <div className={finalClasses}>
      {/* 라벨 */}
      {isEditing ? (
        <input
          type="text"
          value={editLabel}
          onChange={(e) => onLabelChange(e.target.value)}
          className="w-full px-2 py-1 border border-gray-300 rounded text-sm font-semibold focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          autoFocus
        />
      ) : (
        <h3 className="text-sm font-semibold text-gray-800">
          {data.label}
        </h3>
      )}

      {/* 설명 */}
      {isEditing ? (
        <textarea
          value={editDescription}
          onChange={(e) => onDescriptionChange(e.target.value)}
          className="w-full px-2 py-1 border border-gray-300 rounded text-xs resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          rows={2}
          placeholder="공정 단계 설명"
        />
      ) : (
        <p className="text-xs text-gray-600">
          {data.description}
        </p>
      )}

      {/* 파라미터 */}
      {Object.keys(data.parameters).length > 0 && (
        <div className="border-t pt-2">
          <p className="text-xs text-gray-500 mb-1">파라미터:</p>
          <div className="space-y-1">
            {Object.entries(data.parameters).map(([key, value]) => (
              <div key={key} className="flex justify-between text-xs">
                <span className="text-gray-600">{key}:</span>
                <span className="text-gray-800 font-medium">{value}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default ProcessNodeContent;
