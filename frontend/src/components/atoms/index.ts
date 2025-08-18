// ============================================================================
// 🧩 Atoms - DDD 도메인별 기본 UI 컴포넌트
// ============================================================================

// 🌐 공통/범용 컴포넌트
export { default as Button } from './Button';
export { default as Input } from './Input';
export { default as Icon } from './Icon';
export { default as Badge } from './Badge';
export { default as Tooltip } from './Tooltip';

// 🎨 Canvas 도메인 컴포넌트
export { default as CustomBackground } from './CustomBackground';

// 🏭 ProcessFlow 도메인 컴포넌트
export { default as ProcessFlowHandle } from './ProcessFlowHandle';
export { default as ProcessFlowTypeBadge } from './ProcessFlowTypeBadge';
export { default as ProcessFlowStatusIndicator } from './ProcessFlowStatusIndicator';

// ============================================================================
// 📝 Atoms 타입 정의
// ============================================================================

export type { ButtonProps } from './Button';
export type { InputProps } from './Input';
export type { IconProps } from './Icon';
export type { BadgeProps } from './Badge';
export type { TooltipProps } from './Tooltip';

