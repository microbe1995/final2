// ============================================================================
// 🪝 Hooks - React Flow 및 비즈니스 로직 훅들
// ============================================================================

// ============================================================================
// 🔧 공통 훅들 (재사용 가능한 유틸리티)
// ============================================================================
export { useAsync, useAPI, useForm, useToast } from './common';
export type { AsyncState, AsyncOperationOptions, APIOptions, FormOptions } from './common';

// ============================================================================
// 🔐 인증 및 사용자 관리 훅들
// ============================================================================
export { useAuthAPI } from './useAuthAPI';
export { useAppNavigation } from './useNavigation';

// ============================================================================
// 🌊 React Flow 핵심 훅들
// ============================================================================
export { useProcessFlowDomain } from './useProcessFlow';
export { useProcessFlowService } from './useProcessFlowAPI';

// ============================================================================
// 🎯 React Flow 고급 기능 훅들
// ============================================================================
// 🎨 Layout Engine (ELK)
export { useLayoutEngine } from './useLayoutEngine';
// 🛣️ Edge Routing (Smart Edge, Orthogonal, Bezier, Step)
export { useEdgeRouting } from './useEdgeRouting';
// 🖱️ Advanced Viewport Controls (Design Tool, Map, Presentation)
export { useAdvancedViewport } from './useAdvancedViewport';

// ============================================================================
// 🔄 비동기 작업 관리 훅들 (레거시 - 새 프로젝트는 useAsync 사용 권장)
// ============================================================================
export { useAsyncOperationHelper } from './useAsyncOperation';

// ============================================================================
// 🧩 React Flow Context Provider
// ============================================================================
export { ReactFlowProvider, useReactFlowContext, useSubFlow, useEdgeZIndex, useViewport } from './providers/ReactFlowProvider';