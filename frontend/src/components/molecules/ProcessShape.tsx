'use client';

import React from 'react';
import Icon from '@/atoms/Icon';
import Badge from '@/atoms/Badge';
import Tooltip from '@/atoms/Tooltip';

// ============================================================================
// 🎯 ProcessShape Props 인터페이스
// ============================================================================

export interface ProcessShapeProps {
  id: string;
  type: 'process' | 'material' | 'energy' | 'storage' | 'transport';
  label: string;
  x: number;
  y: number;
  width: number;
  height: number;
  color: string;
  isSelected?: boolean;
  isConnectionStart?: boolean;
  isConnecting?: boolean;
  processType?: 'manufacturing' | 'assembly' | 'packaging' | 'transport' | 'storage';
  materialType?: 'raw' | 'intermediate' | 'final' | 'waste';
  energyType?: 'electricity' | 'gas' | 'steam' | 'fuel';
  capacity?: number;
  unit?: string;
  efficiency?: number;
  onClick?: () => void;
  onMouseDown?: (e: React.MouseEvent) => void;
  onMouseEnter?: () => void;
  onMouseLeave?: () => void;
  className?: string;
}

// ============================================================================
// 🎨 ProcessShape 컴포넌트
// ============================================================================

const ProcessShape: React.FC<ProcessShapeProps> = ({
  id,
  type,
  label,
  x,
  y,
  width,
  height,
  color,
  isSelected = false,
  isConnectionStart = false,
  isConnecting = false,
  processType,
  materialType,
  energyType,
  capacity,
  unit,
  efficiency,
  onClick,
  onMouseDown,
  onMouseEnter,
  onMouseLeave,
  className = ''
}) => {
  // 타입별 아이콘 매핑
  const getTypeIcon = () => {
    switch (type) {
      case 'process': return processType || 'process';
      case 'material': return materialType || 'material';
      case 'energy': return energyType || 'energy';
      case 'storage': return 'storage';
      case 'transport': return 'transport';
      default: return 'process';
    }
  };

  // 타입별 배경색 매핑
  const getTypeColor = () => {
    const colorMap: Record<string, string> = {
      process: '#8B5CF6',
      material: '#06B6D4',
      energy: '#F97316',
      storage: '#84CC16',
      transport: '#EF4444'
    };
    return colorMap[type] || color;
  };

  // 상태별 테두리 스타일
  const getBorderStyle = () => {
    if (isSelected) return '3px solid #3B82F6';
    if (isConnectionStart) return '3px solid #10B981';
    return '2px solid #374151';
  };

  // 커서 스타일
  const getCursorStyle = () => {
    if (isConnecting) return 'crosshair';
    return 'pointer';
  };

  // 그림자 스타일
  const getShadowStyle = () => {
    if (isSelected) return '0 4px 12px rgba(59, 130, 246, 0.4)';
    return '0 2px 8px rgba(0,0,0,0.2)';
  };

  const baseStyle = {
    position: 'absolute' as const,
    left: x,
    top: y,
    width,
    height,
    backgroundColor: getTypeColor(),
    border: getBorderStyle(),
    borderRadius: '8px',
    cursor: getCursorStyle(),
    boxShadow: getShadowStyle(),
    display: 'flex',
    flexDirection: 'column' as const,
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s ease-in-out',
    zIndex: isSelected ? 10 : 1
  };

  const tooltipContent = `
    타입: ${type}
    라벨: ${label}
    ${processType ? `공정 유형: ${processType}` : ''}
    ${materialType ? `자재 유형: ${materialType}` : ''}
    ${energyType ? `에너지 유형: ${energyType}` : ''}
    ${capacity ? `용량: ${capacity} ${unit || ''}` : ''}
    ${efficiency ? `효율: ${efficiency}%` : ''}
  `.trim();

  return (
    <Tooltip content={tooltipContent} position="top">
      <div
        style={baseStyle}
        onClick={onClick}
        onMouseDown={onMouseDown}
        onMouseEnter={onMouseEnter}
        onMouseLeave={onMouseLeave}
        className={className}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && onClick?.()}
        aria-label={`${type} 공정: ${label}`}
      >
        {/* 메인 아이콘 */}
        <Icon 
          name={getTypeIcon()} 
          size="lg" 
          color="#FFFFFF"
          className="mb-2"
        />
        
        {/* 라벨 */}
        <div className="text-center">
          <div className="text-white text-xs font-bold leading-tight mb-1">
            {label}
          </div>
          
          {/* 타입 배지 */}
          <Badge 
            variant="default" 
            size="sm"
            className="bg-white/20 text-white border-white/30"
          >
            {type}
          </Badge>
        </div>

        {/* 추가 정보 표시 */}
        {(capacity || efficiency) && (
          <div className="absolute -bottom-6 left-0 right-0 text-center">
            {capacity && (
              <Badge variant="info" size="sm" className="mr-1">
                {capacity} {unit}
              </Badge>
            )}
            {efficiency && (
              <Badge variant="success" size="sm">
                {efficiency}%
              </Badge>
            )}
          </div>
        )}
      </div>
    </Tooltip>
  );
};

export default ProcessShape;
