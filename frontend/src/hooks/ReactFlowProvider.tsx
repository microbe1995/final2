'use client';

import React, { ReactNode } from 'react';
import { ReactFlowProvider as XYFlowProvider } from '@xyflow/react';

// ============================================================================
// 🎯 간소화된 React Flow Provider
// ============================================================================

interface SimpleReactFlowProviderProps {
  children: ReactNode;
}

export const ReactFlowProvider: React.FC<SimpleReactFlowProviderProps> = ({
  children,
}) => {
  return (
    <XYFlowProvider>
      {children}
    </XYFlowProvider>
  );
};

export default ReactFlowProvider;
