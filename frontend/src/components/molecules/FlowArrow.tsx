'use client';

import React from 'react';
import Icon from '@/atoms/Icon';
import Badge from '@/atoms/Badge';
import Tooltip from '@/atoms/Tooltip';

// ============================================================================
// 🎯 FlowArrow Props 인터페이스
// ============================================================================

export interface FlowArrowProps {
  id: string;
  type: 'straight' | 'curved' | 'bidirectional' | 'dashed';
  startX: number;
  startY: number;
  endX: number;
  endY: number;
  color: string;
  strokeWidth: number;
  isSelected?: boolean;
  flowType?: 'material' | 'energy' | 'information' | 'waste';
  flowRate?: number;
  flowUnit?: string;
  direction?: 'forward' | 'backward' | 'bidirectional';
  label?: string;
  fromShapeId?: string;
  toShapeId?: string;
  onClick?: () => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  className?: string;
}

// ============================================================================
// 🎨 FlowArrow 컴포넌트
// ============================================================================

const FlowArrow: React.FC<FlowArrowProps> = ({
  id,
  type,
  startX,
  startY,
  endX,
  endY,
  color,
  strokeWidth,
  isSelected = false,
  flowType = 'material',
  flowRate,
  flowUnit,
  direction = 'forward',
  label,
  fromShapeId,
  toShapeId,
  onClick,
  onMouseEnter,
  onMouseLeave,
  className = ''
}) => {
  // 화살표 길이와 각도 계산
  const length = Math.sqrt(
    Math.pow(endX - startX, 2) + Math.pow(endY - startY, 2)
  );
  const angle = Math.atan2(endY - startY, endX - startX) * 180 / Math.PI;

  // 화살표 타입별 스타일
  const getArrowStyle = () => {
    const baseStyle = {
      position: 'absolute' as const,
      left: startX,
      top: startY,
      width: length,
      height: strokeWidth,
      backgroundColor: color,
      transform: `rotate(${angle}deg)`,
      transformOrigin: '0 50%',
      cursor: 'pointer',
      transition: 'all 0.2s ease-in-out',
      zIndex: isSelected ? 10 : 1
    };

    switch (type) {
      case 'dashed':
        return {
          ...baseStyle,
          background: `repeating-linear-gradient(
            to right,
            ${color} 0,
            ${color} 4px,
            transparent 4px,
            transparent 8px
          )`
        };
      case 'curved':
        return {
          ...baseStyle,
          borderRadius: '50%',
          background: `linear-gradient(90deg, ${color} 0%, ${color} 100%)`
        };
      default:
        return baseStyle;
    }
  };

  // 테두리 스타일
  const getBorderStyle = () => {
    if (isSelected) return '2px solid #3B82F6';
    return 'none';
  };

  // 그림자 스타일
  const getShadowStyle = () => {
    if (isSelected) return '0 2px 8px rgba(59, 130, 246, 0.4)';
    return '0 1px 4px rgba(0,0,0,0.2)';
  };

  // 화살표 머리 렌더링
  const renderArrowHead = () => {
    const headSize = strokeWidth * 2;
    const headAngle = angle + (direction === 'bidirectional' ? 0 : 180);
    
    return (
      <div
        className="absolute"
        style={{
          right: -headSize / 2,
          top: '50%',
          transform: `translateY(-50%) rotate(${headAngle}deg)`,
          width: 0,
          height: 0,
          borderLeft: `${headSize}px solid transparent`,
          borderRight: `${headSize}px solid transparent`,
          borderBottom: `${headSize}px solid ${color}`,
          zIndex: 11
        }}
      />
    );
  };

  // 양방향 화살표인 경우 시작점에도 화살표 머리 추가
  const renderStartArrowHead = () => {
    if (direction !== 'bidirectional') return null;
    
    const headSize = strokeWidth * 2;
    const startAngle = angle + 180;
    
    return (
      <div
        className="absolute"
        style={{
          left: -headSize / 2,
          top: '50%',
          transform: `translateY(-50%) rotate(${startAngle}deg)`,
          width: 0,
          height: 0,
          borderLeft: `${headSize}px solid transparent`,
          borderRight: `${headSize}px solid transparent`,
          borderBottom: `${headSize}px solid ${color}`,
          zIndex: 11
        }}
      />
    );
  };

  const arrowStyle = getArrowStyle();
  const tooltipContent = `
    화살표 타입: ${type}
    흐름 유형: ${flowType}
    방향: ${direction}
    ${label ? `라벨: ${label}` : ''}
    ${flowRate ? `유량: ${flowRate} ${flowUnit || ''}` : ''}
    ${fromShapeId ? `시작: ${fromShapeId}` : ''}
    ${toShapeId ? `끝: ${toShapeId}` : ''}
  `.trim();

  return (
    <Tooltip content={tooltipContent} position="top">
      <div
        style={{
          ...arrowStyle,
          border: getBorderStyle(),
          boxShadow: getShadowStyle()
        }}
        onClick={onClick}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        className={className}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && onClick?.()}
        aria-label={`${flowType} 흐름 화살표`}
      >
        {/* 화살표 머리들 */}
        {renderArrowHead()}
        {renderStartArrowHead()}
        
        {/* 흐름 정보 표시 */}
        {(flowRate || label) && (
          <div 
            className="absolute -top-8 left-1/2 transform -translate-x-1/2 text-center"
            style={{ zIndex: 12 }}
          >
            {label && (
              <Badge variant="info" size="sm" className="mb-1">
                {label}
              </Badge>
            )}
            {flowRate && (
              <Badge variant="success" size="sm">
                {flowRate} {flowUnit}
              </Badge>
            )}
          </div>
        )}
      </div>
    </Tooltip>
  );
};

export default FlowArrow;
