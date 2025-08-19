// ============================================================================
// 🧬 Organisms - DDD 도메인별 복합 기능 컴포넌트
// ============================================================================

// 🌐 공통/네비게이션 컴포넌트 (실제 화면 요소명 반영)
export { default as AppTopNavigation } from './AppTopNavigation';

// 🔐 Auth 도메인 컴포넌트 (실제 화면 요소명 반영)
export { default as LoginSignupCard } from './LoginSignupCard';
export { default as ProfileForm } from './ProfileForm';

// 🎨 Canvas 도메인 컴포넌트 (삭제됨)

// 🏭 ProcessFlow 도메인 컴포넌트 (실제 화면 요소명 반영)
export { default as ProcessNode } from './ProcessNode';
export { default as ProcessEdge } from './ProcessEdge';
export { default as ProcessFlowControls } from './ProcessFlowControls';
export { default as ProcessInfoSidebar } from './ProcessInfoSidebar';
export { default as ProcessControlHeader } from './ProcessControlHeader';
export { default as GroupNode } from './GroupNode';
// ProcessDiagramEditor 삭제됨 - ProcessFlowEditor.tsx 사용

// ============================================================================
// 📝 Organisms 타입 정의
// ============================================================================

// 삭제된 컴포넌트 타입들


