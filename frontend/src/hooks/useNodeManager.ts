import { useCallback } from 'react';
import { Node } from '@xyflow/react';
import axiosClient, { apiEndpoints } from '@/lib/axiosClient';
import { Install, Product, Process } from '@/lib/types';

/**
 * 노드 관리 전용 훅
 * 단일 책임: 노드 생성, 업데이트, 데이터 동기화만 담당
 */
export const useNodeManager = () => {

  // 제품 노드 생성
  const createProductNode = useCallback((
    product: Product, 
    selectedInstall: Install | null,
    handleProductNodeClick: (product: Product) => void
  ): Node => {
    const nodeId = Math.floor(Math.random() * 1000000) + 1;
    const actualNodeId = `product-${nodeId}-${Math.random().toString(36).slice(2)}`;
    
    return {
      id: actualNodeId,
      type: 'product',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        id: product.id,
        nodeId: actualNodeId,
        label: product.product_name,
        description: `제품: ${product.product_name}`,
        variant: 'product',
        productData: product,
        attr_em: (product as any)?.attr_em || 0,
        product_amount: Number((product as any)?.product_amount ?? 0),
        product_sell: Number((product as any)?.product_sell ?? 0),
        product_eusell: Number((product as any)?.product_eusell ?? 0),
        install_id: selectedInstall?.id,
        onClick: undefined,
        onDoubleClick: () => handleProductNodeClick(product),
        size: 'md',
        showHandles: true,
      },
    };
  }, []);

  // 공정 노드 생성
  const createProcessNode = useCallback(async (
    process: Process,
    products: Product[],
    selectedInstall: Install | null,
    openInputModal: (process: Process) => void
  ): Promise<Node> => {
    // 관련 제품 정보 찾기
    const relatedProducts = products.filter((product: Product) => 
      process.products?.some(p => p.id === product.id)
    );

    // 공정별 직접귀속배출량 정보 가져오기
    let emissionData = null;
    try {
      const response = await axiosClient.get(apiEndpoints.cbam.calculation.process.attrdir(process.id));
      if (response.data) {
        emissionData = {
          attr_em: response.data.attrdir_em || 0,
          cumulative_emission: response.data.cumulative_emission || response.data.attrdir_em || 0,
          total_matdir_emission: response.data.total_matdir_emission || 0,
          total_fueldir_emission: response.data.total_fueldir_emission || 0,
          calculation_date: response.data.calculation_date
        };
      }
    } catch (error) {
      /* noop */
    }

    const nodeId = Math.floor(Math.random() * 1000000) + 1;
    const actualNodeId = `process-${nodeId}-${Math.random().toString(36).slice(2)}`;
    
    return {
      id: actualNodeId,
      type: 'process',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      data: {
        id: process.id,
        nodeId: actualNodeId,
        label: process.process_name,
        description: `공정: ${process.process_name}`,
        variant: 'process',
        install_id: (process as any).install_id,
        current_install_id: selectedInstall?.id,
        is_readonly: (process as any).install_id !== selectedInstall?.id,
        processData: {
          ...process,
          start_period: process.start_period || 'N/A',
          end_period: process.end_period || 'N/A',
          product_names: relatedProducts.map(p => p.product_name).join(', '),
          is_many_to_many: relatedProducts.length > 1,
          install_id: (process as any).install_id,
          current_install_id: selectedInstall?.id,
          is_readonly: (process as any).install_id !== selectedInstall?.id,
          ...emissionData
        },
        onClick: () => openInputModal(process),
        onMatDirClick: (processData: any) => openInputModal(processData),
        size: 'md',
        showHandles: true,
      },
    };
  }, []);

  // 그룹 노드 생성
  const createGroupNode = useCallback((): Node => {
    const nodeId = Math.floor(Math.random() * 1000000) + 1;
    const actualNodeId = `group-${nodeId}-${Math.random().toString(36).slice(2)}`;
    
    return {
      id: actualNodeId,
      type: 'group',
      position: { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
      style: { width: 200, height: 100 },
      data: { 
        nodeId: actualNodeId,
        label: '그룹',
        description: '그룹 노드',
        variant: 'default',
        size: 'md',
        showHandles: true,
      },
    };
  }, []);

  // 노드 데이터 업데이트
  const updateNodeData = useCallback((
    nodes: Node[],
    nodeId: string,
    newData: any
  ): Node[] => {
    return nodes.map(node => 
      node.id === nodeId 
        ? { ...node, data: { ...node.data, ...newData } }
        : node
    );
  }, []);

  // 제품 노드 업데이트 (ID 기준)
  const updateProductNodeByProductId = useCallback((
    nodes: Node[],
    productId: number,
    newFields: any
  ): Node[] => {
    return nodes.map(node => {
      if (node.type === 'product' && (node.data as any)?.id === productId) {
        const prevProductData = (node.data as any).productData || {};
        return {
          ...node,
          data: {
            ...node.data,
            ...newFields,
            product_amount: newFields.product_amount ?? (node.data as any).product_amount,
            productData: {
              ...prevProductData,
              production_qty: newFields.product_amount ?? prevProductData.production_qty,
              product_sell: newFields.product_sell ?? prevProductData.product_sell,
              product_eusell: newFields.product_eusell ?? prevProductData.product_eusell
            }
          }
        } as Node;
      }
      return node;
    });
  }, []);

  // 제품 produce 플래그 설정
  const setProductProduceFlag = useCallback((
    nodes: Node[],
    productId: number,
    hasProduce: boolean
  ): Node[] => {
    return nodes.map(node => {
      if (node.type === 'product' && (node.data as any)?.id === productId) {
        return {
          ...node,
          data: {
            ...node.data,
            has_produce_edge: hasProduce
          }
        } as Node;
      }
      return node;
    });
  }, []);

  // 공정 노드 업데이트 (ID 기준)
  const updateProcessNodeByProcessId = useCallback((
    nodes: Node[],
    processId: number,
    newFields: any
  ): Node[] => {
    return nodes.map(node => {
      if (node.type === 'process' && (node.data as any)?.id === processId) {
        const prevProcessData = (node.data as any).processData || {};
        return {
          ...node,
          data: {
            ...node.data,
            ...newFields,
            processData: {
              ...prevProcessData,
              ...newFields,
              // 누적 배출량이 없으면 직접귀속배출량 사용
              cumulative_emission: newFields.cumulative_emission ?? prevProcessData.cumulative_emission ?? newFields.attr_em ?? prevProcessData.attr_em
            }
          }
        } as Node;
      }
      return node;
    });
  }, []);

  // 노드 ID 정규화
  const normalizeNodeId = useCallback((id: string) => 
    id.replace(/-(left|right|top|bottom)$/i, ''), []
  );

  // 노드 찾기 (다양한 ID 패턴 지원)
  const findNodeByAnyId = useCallback((
    nodes: Node[],
    candidateId: string
  ): Node | undefined => {
    const id = normalizeNodeId(candidateId);
    return (
      nodes.find(n => n.id === id) ||
      nodes.find(n => (n.data as any)?.nodeId === id) ||
      nodes.find(n => id.startsWith(n.id)) ||
      nodes.find(n => id.startsWith(((n.data as any)?.nodeId) || '')) ||
      nodes.find(n => n.id.startsWith(id)) ||
      nodes.find(n => ((((n.data as any)?.nodeId) || '') as string).startsWith(id))
    );
  }, [normalizeNodeId]);

  return {
    createProductNode,
    createProcessNode,
    createGroupNode,
    updateNodeData,
    updateProductNodeByProductId,
    updateProcessNodeByProcessId,
    setProductProduceFlag,
    normalizeNodeId,
    findNodeByAnyId,
  };
};
