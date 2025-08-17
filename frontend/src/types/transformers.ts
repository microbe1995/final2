import type { AppNodeType, AppEdgeType, CanvasData, FlowData } from './reactFlow';

// ============================================================================
// 🔄 React Flow 데이터 변환 유틸리티
// ============================================================================

// Flow → Canvas 변환 (노드/엣지 배열을 Canvas 형식으로)
export const transformFlowToCanvas = (
  nodes: AppNodeType[],
  edges: AppEdgeType[],
  name?: string
): CanvasData => {
  const canvasName = name || `공정도_${new Date().toISOString().split('T')[0]}`;
  
  return {
    name: canvasName,
    description: 'React Flow 공정도',
    nodes: nodes.map(node => ({
      id: node.id,
      type: node.type,
      position: node.position,
      data: node.data,
      style: node.style,
    })),
    edges: edges.map(edge => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      type: edge.type,
      data: edge.data,
      style: edge.style,
    })),
    metadata: {
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      nodeCount: nodes.length,
      edgeCount: edges.length,
    },
  };
};

// Canvas → Flow 변환 (Canvas 데이터를 Flow 형식으로)
export const transformCanvasToFlow = (canvas: CanvasData): FlowData => {
  if (!canvas) {
    return { nodes: [], edges: [] };
  }

  return {
    nodes: (canvas.nodes || []).map((node) => ({
      ...node,
      selected: false,
      dragging: false,
    })),
    edges: (canvas.edges || []).map((edge) => ({
      ...edge,
      selected: false,
    })),
    metadata: canvas.metadata,
  };
};
