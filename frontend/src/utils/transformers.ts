import { Node, Edge } from '@xyflow/react';

export interface CanvasData {
  id?: string;
  name: string;
  description: string;
  nodes: any[];
  edges: any[];
  metadata?: {
    createdAt: string;
    updatedAt: string;
    nodeCount: number;
    edgeCount: number;
  };
}

export interface FlowData {
  nodes: Node[];
  edges: Edge[];
  metadata?: any;
}

export const transformCanvasToFlow = (canvas: any): FlowData => {
  if (!canvas) {
    return { nodes: [], edges: [] };
  }

  return {
    nodes: (canvas.nodes || []).map((node: any) => ({
      ...node,
      selected: false,
      dragging: false,
    })),
    edges: (canvas.edges || []).map((edge: any) => ({
      ...edge,
      selected: false,
    })),
    metadata: canvas.metadata,
  };
};

export const transformFlowToCanvas = (
  nodes: Node[],
  edges: Edge[],
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
