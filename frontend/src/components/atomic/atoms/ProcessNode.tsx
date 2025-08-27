'use client';

import React, { memo } from 'react';
import { Handle, Position } from '@xyflow/react';
import { renderFourDirectionHandles } from './HandleStyles';

interface ProcessNodeProps {
  data: {
    label: string;
    description?: string;
    processData?: any;
    [key: string]: any;
  };
  isConnectable?: boolean;
  targetPosition?: Position | Position[];
  sourcePosition?: Position | Position[];
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger' | 'process';
  size?: 'sm' | 'md' | 'lg';
  showHandles?: boolean;
  onClick?: (node: any) => void;
  onDoubleClick?: (node: any) => void;
  selected?: boolean;
}

const variantStyles = {
  default: 'bg-white border-gray-800 text-gray-800',
  primary: 'bg-blue-50 border-blue-600 text-blue-900',
  success: 'bg-green-50 border-green-600 text-green-900',
  warning: 'bg-yellow-50 border-yellow-600 text-yellow-900',
  danger: 'bg-red-50 border-red-600 text-red-900',
  process: 'bg-orange-50 border-orange-300 text-orange-800',
  readonly: 'bg-gray-100 border-gray-400 text-gray-600', // 읽기 전용 공정용 스타일
};

const sizeStyles = {
  sm: 'px-2 py-1 min-w-[80px] text-xs',
  md: 'px-4 py-3 min-w-[120px] text-sm',
  lg: 'px-6 py-4 min-w-[160px] text-base',
};

function ProcessNode({
  data,
  isConnectable = true,
  targetPosition,
  sourcePosition,
  variant,
  size,
  showHandles,
  onClick,
  onDoubleClick,
  selected,
}: ProcessNodeProps) {
  const finalVariant = variant || data.variant || 'default';
  const finalSize = size || data.size || 'md';
  const finalShowHandles =
    showHandles !== undefined
      ? showHandles
      : data.showHandles !== undefined
        ? data.showHandles
        : true;

  // 읽기 전용 공정인지 확인
  const isReadOnly = data.is_readonly || false;
  const isExternalProcess = data.install_id !== data.current_install_id;
  
  // 외부 사업장의 공정이면 읽기 전용으로 설정
  const effectiveVariant = isExternalProcess ? 'readonly' : finalVariant;

  const nodeClasses = `
    ${variantStyles[effectiveVariant as keyof typeof variantStyles]} 
    ${sizeStyles[finalSize as keyof typeof sizeStyles]}
    border-2 rounded-lg shadow-md relative hover:shadow-lg transition-all duration-200
    ${isReadOnly || isExternalProcess ? 'opacity-75' : 'hover:scale-105'}
  `.trim();

  const handleClick = () => {
    // 읽기 전용이거나 외부 사업장 공정이면 클릭 이벤트 무시
    if (isReadOnly || isExternalProcess) {
      return;
    }
    
    // data에 onClick 함수가 있으면 먼저 실행
    if (data.onClick) {
      data.onClick();
    }
    // 그 다음 일반적인 onClick 핸들러 실행
    if (onClick) onClick({ data, selected });
  };

  const handleDoubleClick = () => {
    // 읽기 전용이거나 외부 사업장 공정이면 더블클릭 이벤트 무시
    if (isReadOnly || isExternalProcess) {
      return;
    }
    
    if (onDoubleClick) onDoubleClick({ data, selected });
  };

  return (
    <div 
      className={`${nodeClasses} ${selected ? 'border-2 border-opacity-100 shadow-lg' : ''}`}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      style={{ 
        cursor: data.processData ? 'pointer' : 'default',
        pointerEvents: 'auto' // ✅ pointerEvents 문제 해결
      }}
    >
      {/* 🎯 4방향 핸들 - HandleStyles.tsx 함수 사용 */}
      {finalShowHandles && renderFourDirectionHandles(isConnectable)}

      {/* 노드 내용 */}
      <div className='text-center'>
        <div
          className={`font-semibold mb-1 ${finalSize === 'lg' ? 'text-lg' : finalSize === 'sm' ? 'text-xs' : 'text-sm'}`}
        >
          {finalVariant === 'process' ? '⚙️ ' : ''}{data.label}
        </div>
        {data.description && (
          <div
            className={`text-opacity-70 ${finalSize === 'lg' ? 'text-sm' : 'text-xs'}`}
          >
            {data.description}
          </div>
        )}

        {/* 공정 정보 미리보기 */}
        {data.processData && finalVariant === 'process' && (
          <div className='text-xs opacity-60 mt-2'>
            {data.product_names && (
              <div className='flex justify-between'>
                <span>사용 제품:</span>
                <span className='font-medium'>{data.product_names}</span>
              </div>
            )}
            {data.is_many_to_many && (
              <div className='flex justify-between text-blue-400'>
                <span>관계:</span>
                <span className='font-medium'>다대다</span>
              </div>
            )}
            {isExternalProcess && (
              <div className='flex justify-between text-gray-500'>
                <span>외부 사업장:</span>
                <span className='font-medium'>이동 가능, 편집 불가</span>
              </div>
            )}
            <div className='flex justify-between'>
              <span>시작일:</span>
              <span className='font-medium'>{data.processData.start_period || 'N/A'}</span>
            </div>
            <div className='flex justify-between'>
              <span>종료일:</span>
              <span className='font-medium'>{data.processData.end_period || 'N/A'}</span>
            </div>
            {/* product_id는 다대다 관계에서 더 이상 사용되지 않음 */}
          </div>
        )}
      </div>
    </div>
  );
}

export default memo(ProcessNode);
