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
  // 대시보드 다크톤 + 블루 악센트
  default: 'bg-gray-800 border-blue-500 text-white',
  primary: 'bg-blue-500/10 border-blue-500 text-blue-100',
  success: 'bg-green-500/10 border-green-500 text-green-100',
  warning: 'bg-yellow-500/10 border-yellow-500 text-yellow-100',
  danger: 'bg-red-500/10 border-red-500 text-red-100',
  process: 'bg-blue-600/10 border-blue-500 text-blue-100',
  readonly: 'bg-gray-700 border-gray-500 text-gray-300', // 읽기 전용 공정용 스타일
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
  // 두 값이 모두 정의된 경우에만 외부 사업장으로 판단 (undefined로 인해 클릭이 막히는 문제 방지)
  const isExternalProcess =
    typeof data.install_id === 'number' && typeof data.current_install_id === 'number'
      ? data.install_id !== data.current_install_id
      : false;
  
  // 외부 사업장의 공정이면 읽기 전용으로 설정
  const effectiveVariant = isExternalProcess ? 'readonly' : finalVariant;

  const nodeClasses = `
    ${variantStyles[effectiveVariant as keyof typeof variantStyles]}
    ${sizeStyles[finalSize as keyof typeof sizeStyles]}
    border-2 rounded-lg shadow-md relative transition-all duration-200
    ring-1 ring-blue-400/20 hover:ring-blue-400/60 hover:shadow-lg
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
      return;
    }
    // onClick이 없는 경우 투입량 입력 핸들러를 기본 동작으로 사용
    if (!data.onClick && data.onMatDirClick && data.processData) {
      data.onMatDirClick(data.processData);
      return;
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
      {finalShowHandles && renderFourDirectionHandles(isConnectable, data.nodeId || data.id)}

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
            
            {/* 직접귀속배출량 / 누적배출량 표시 */}
            {data.processData.attr_em !== undefined && (
              <div className='flex justify-between mt-1 pt-1 border-t border-gray-200'>
                <span className='text-green-600 font-medium'>직접귀속배출량:</span>
                <span className='text-green-600 font-bold'>
                  {typeof data.processData.attr_em === 'number' 
                    ? `${data.processData.attr_em.toFixed(2)} tCO2e`
                    : data.processData.attr_em || '0.00 tCO2e'
                  }
                </span>
              </div>
            )}
            {data.processData.cumulative_emission !== undefined && (
              <div className='flex justify-between'>
                <span className='text-indigo-600 font-medium'>누적 직접귀속배출량:</span>
                <span className='text-indigo-600 font-bold'>
                  {typeof data.processData.cumulative_emission === 'number'
                    ? `${data.processData.cumulative_emission.toFixed(2)} tCO2e`
                    : data.processData.cumulative_emission || '0.00 tCO2e'}
                </span>
              </div>
            )}
            
            {/* 원료/연료별 배출량 상세 정보 */}
            {data.processData.total_matdir_emission !== undefined && (
              <div className='text-xs text-blue-600 mt-1'>
                <div className='flex justify-between'>
                  <span>원료직접:</span>
                  <span>{data.processData.total_matdir_emission?.toFixed(2) || '0.00'} tCO2e</span>
                </div>
              </div>
            )}
            {data.processData.total_fueldir_emission !== undefined && (
              <div className='text-xs text-orange-600'>
                <div className='flex justify-between'>
                  <span>연료직접:</span>
                  <span>{data.processData.total_fueldir_emission?.toFixed(2) || '0.00'} tCO2e</span>
                </div>
              </div>
            )}
            
            {/* product_id는 다대다 관계에서 더 이상 사용되지 않음 */}
          </div>
        )}

        {/* 투입량 입력 버튼 */}
        {data.processData && finalVariant === 'process' && !isExternalProcess && (
          <div className='mt-2 pt-2 border-t border-gray-300'>
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (data.onMatDirClick) {
                  data.onMatDirClick(data.processData);
                }
              }}
              className='w-full px-2 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs rounded transition-colors'
            >
              📊 투입량 입력
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default memo(ProcessNode);
