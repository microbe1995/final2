'use client';

import React, { createContext, useContext, ReactNode } from 'react';
import { ReactFlowProvider as XYFlowProvider } from '@xyflow/react';

// ============================================================================
// 🎯 React Flow Context 타입 정의
// ============================================================================

interface ReactFlowContextType {
  // Sub Flow 관련 상태
  expandedGroups: Set<string>;
  toggleGroupExpansion: (groupId: string) => void;
  
  // Edge Z-Index 관리
  edgeZIndex: number;
  setEdgeZIndex: (zIndex: number) => void;
  
  // Viewport 상태
  viewport: { x: number; y: number; zoom: number };
  setViewport: (viewport: { x: number; y: number; zoom: number }) => void;
}

// ============================================================================
// 🎯 React Flow Context 생성
// ============================================================================

const ReactFlowContext = createContext<ReactFlowContextType | undefined>(undefined);

// ============================================================================
// 🎯 React Flow Provider Props
// ============================================================================

interface ReactFlowProviderProps {
  children: ReactNode;
}

// ============================================================================
// 🎯 React Flow Provider 컴포넌트
// ============================================================================

export const ReactFlowProvider: React.FC<ReactFlowContextType & ReactFlowProviderProps> = ({
  children,
  expandedGroups,
  toggleGroupExpansion,
  edgeZIndex,
  setEdgeZIndex,
  viewport,
  setViewport,
  ...props
}) => {
  const contextValue: ReactFlowContextType = {
    expandedGroups,
    toggleGroupExpansion,
    edgeZIndex,
    setEdgeZIndex,
    viewport,
    setViewport,
  };

  return (
    <ReactFlowContext.Provider value={contextValue}>
      <XYFlowProvider>
        {children}
      </XYFlowProvider>
    </ReactFlowContext.Provider>
  );
};

// ============================================================================
// 🎯 React Flow Context 사용 훅
// ============================================================================

export const useReactFlowContext = (): ReactFlowContextType => {
  const context = useContext(ReactFlowContext);
  if (!context) {
    throw new Error('useReactFlowContext must be used within ReactFlowProvider');
  }
  return context;
};

// ============================================================================
// 🎯 Sub Flow 관련 훅
// ============================================================================

export const useSubFlow = () => {
  const { expandedGroups, toggleGroupExpansion } = useReactFlowContext();
  
  const isGroupExpanded = (groupId: string): boolean => {
    return expandedGroups.has(groupId);
  };
  
  const expandGroup = (groupId: string): void => {
    if (!expandedGroups.has(groupId)) {
      toggleGroupExpansion(groupId);
    }
  };
  
  const collapseGroup = (groupId: string): void => {
    if (expandedGroups.has(groupId)) {
      toggleGroupExpansion(groupId);
    }
  };
  
  return {
    expandedGroups,
    isGroupExpanded,
    expandGroup,
    collapseGroup,
    toggleGroupExpansion,
  };
};

// ============================================================================
// 🎯 Edge Z-Index 관리 훅
// ============================================================================

export const useEdgeZIndex = () => {
  const { edgeZIndex, setEdgeZIndex } = useReactFlowContext();
  
  const bringEdgesToFront = (): void => {
    setEdgeZIndex(1000);
  };
  
  const sendEdgesToBack = (): void => {
    setEdgeZIndex(1);
  };
  
  const setCustomZIndex = (zIndex: number): void => {
    setEdgeZIndex(zIndex);
  };
  
  return {
    edgeZIndex,
    bringEdgesToFront,
    sendEdgesToBack,
    setCustomZIndex,
  };
};

// ============================================================================
// 🎯 Viewport 관리 훅
// ============================================================================

export const useViewport = () => {
  const { viewport, setViewport } = useReactFlowContext();
  
  const resetViewport = (): void => {
    setViewport({ x: 0, y: 0, zoom: 1 });
  };
  
  const centerViewport = (x: number, y: number): void => {
    setViewport({ x: -x, y: -y, zoom: viewport.zoom });
  };
  
  const zoomToFit = (): void => {
    setViewport({ ...viewport, zoom: 1 });
  };
  
  return {
    viewport,
    setViewport,
    resetViewport,
    centerViewport,
    zoomToFit,
  };
};
