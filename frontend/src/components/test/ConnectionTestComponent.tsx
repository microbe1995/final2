'use client';

import React, { useState, useCallback } from 'react';
import { ReactFlow, ReactFlowProvider, Background, Controls, Node, Edge, Connection, ConnectionMode } from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import ProductNode from '@/components/atomic/atoms/ProductNode';
import ProcessNode from '@/components/atomic/atoms/ProcessNode';
import CustomEdge from '@/components/atomic/atoms/CustomEdge';

// 테스트용 노드 타입 정의
const nodeTypes = {
  product: ProductNode,
  process: ProcessNode,
};

const edgeTypes = {
  custom: CustomEdge,
};

// 테스트용 초기 노드들
const initialNodes: Node[] = [
  {
    id: 'product-123-test',
    type: 'product',
    position: { x: 100, y: 100 },
    data: {
      id: 123,
      nodeId: 'product-123-test',
      label: '테스트 제품',
      description: '연결 테스트용 제품',
      variant: 'product',
      showHandles: true,
      productData: { id: 123, product_name: '테스트 제품' }
    }
  },
  {
    id: 'process-456-test',
    type: 'process',
    position: { x: 400, y: 100 },
    data: {
      id: 456,
      nodeId: 'process-456-test',
      label: '테스트 공정',
      description: '연결 테스트용 공정',
      variant: 'process',
      showHandles: true,
      processData: { id: 456, process_name: '테스트 공정' }
    }
  },
  {
    id: 'group-789-test',
    type: 'product', // 그룹도 ProductNode로 렌더링
    position: { x: 250, y: 300 },
    data: {
      id: 789,
      nodeId: 'group-789-test',
      label: '테스트 그룹',
      description: '연결 테스트용 그룹',
      variant: 'default',
      showHandles: true
    }
  }
];

export default function ConnectionTestComponent() {
  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [testResults, setTestResults] = useState<string[]>([]);

  // 연결 검증 로직 (실제 ProcessManager와 동일)
  const validateConnection = useCallback((connection: Connection) => {
    console.log('🔍 연결 검증 시작:', connection);
    
    // 같은 노드 간 연결 방지
    if (connection.source === connection.target) {
      console.log('❌ 같은 노드 간 연결 시도:', connection.source);
      return { valid: false, reason: 'same_node' };
    }
    
    // 핸들 ID 존재 여부 확인
    if (!connection.sourceHandle || !connection.targetHandle) {
      console.log('❌ 핸들 ID 누락:', { sourceHandle: connection.sourceHandle, targetHandle: connection.targetHandle });
      return { valid: false, reason: 'missing_handles' };
    }
    
    // 핸들 ID 형식 확인 (새로운 형식: nodeId-direction)
    const handleIdPattern = /^[^-]+-(left|right|top|bottom)$/;
    if (!handleIdPattern.test(connection.sourceHandle) || !handleIdPattern.test(connection.targetHandle)) {
      console.log('❌ 핸들 ID 형식 불일치:', { 
        sourceHandle: connection.sourceHandle, 
        targetHandle: connection.targetHandle,
        expectedPattern: 'nodeId-(left|right|top|bottom)'
      });
      return { valid: false, reason: 'invalid_handle_format' };
    }
    
    // 이미 존재하는 연결 확인
    const existingEdge = edges.find(edge => 
      (edge.source === connection.source && edge.target === connection.target) ||
      (edge.source === connection.target && edge.target === connection.source)
    );
    
    if (existingEdge) {
      console.log('❌ 이미 존재하는 연결:', existingEdge);
      return { valid: false, reason: 'duplicate_edge' };
    }
    
    console.log('✅ 연결 검증 통과');
    return { valid: true };
  }, [edges]);

  // 연결 처리
  const handleConnect = useCallback((params: Connection) => {
    console.log('🔗 연결 시도:', params);
    
    const validation = validateConnection(params);
    if (validation.valid) {
      // 연결 성공 - Edge 추가
      const newEdge: Edge = {
        id: `e-${Date.now()}`,
        source: params.source!,
        target: params.target!,
        sourceHandle: params.sourceHandle,
        targetHandle: params.targetHandle,
        type: 'custom',
        data: { isTemporary: false },
        style: { stroke: '#3b82f6' }
      };
      
      setEdges(prev => [...prev, newEdge]);
      setTestResults(prev => [...prev, `✅ 연결 성공: ${params.source} → ${params.target}`]);
      console.log('✅ 연결 성공:', newEdge);
    } else {
      setTestResults(prev => [...prev, `❌ 연결 실패: ${validation.reason}`]);
      console.log(`❌ 연결 실패: ${validation.reason}`, params);
    }
  }, [validateConnection]);

  // 연결 시작
  const handleConnectStart = useCallback((event: any, params: any) => {
    console.log('🔗 연결 시작:', params);
    setTestResults(prev => [...prev, `🔗 연결 시작: ${params.nodeId}`]);
  }, []);

  // 연결 종료
  const handleConnectEnd = useCallback((event: any) => {
    console.log('🔗 연결 종료:', event);
    setTestResults(prev => [...prev, '🔗 연결 종료']);
  }, []);

  // 테스트 결과 초기화
  const clearTestResults = useCallback(() => {
    setTestResults([]);
    setEdges([]);
  }, []);

  // 자동 테스트 실행
  const runAutoTest = useCallback(() => {
    setTestResults(prev => [...prev, '🚀 자동 테스트 시작']);
    
    // 테스트 케이스들
    const testCases = [
      {
        name: '제품 → 공정 연결',
        source: 'product-123-test',
        target: 'process-456-test',
        sourceHandle: 'product-123-test-right',
        targetHandle: 'process-456-test-left'
      },
      {
        name: '공정 → 그룹 연결',
        source: 'process-456-test',
        target: 'group-789-test',
        sourceHandle: 'process-456-test-top',
        targetHandle: 'group-789-test-bottom'
      },
      {
        name: '같은 노드 연결 (실패 예상)',
        source: 'product-123-test',
        target: 'product-123-test',
        sourceHandle: 'product-123-test-left',
        targetHandle: 'product-123-test-right'
      }
    ];

    testCases.forEach((testCase, index) => {
      setTimeout(() => {
        setTestResults(prev => [...prev, `📋 테스트 ${index + 1}: ${testCase.name}`]);
        
        const connection: Connection = {
          source: testCase.source,
          target: testCase.target,
          sourceHandle: testCase.sourceHandle,
          targetHandle: testCase.targetHandle
        };
        
        handleConnect(connection);
      }, index * 1000);
    });
  }, [handleConnect]);

  return (
    <div className="w-full h-screen flex">
      {/* 테스트 패널 */}
      <div className="w-1/3 bg-gray-100 p-4 overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">🔧 노드 연결 테스트</h2>
        
        <div className="space-y-4">
          <div>
            <h3 className="font-semibold mb-2">테스트 컨트롤</h3>
            <div className="space-y-2">
              <button
                onClick={runAutoTest}
                className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                🚀 자동 테스트 실행
              </button>
              <button
                onClick={clearTestResults}
                className="w-full bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
              >
                🗑️ 결과 초기화
              </button>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-2">테스트 노드</h3>
            <div className="text-sm space-y-1">
              <div>📦 제품 노드: product-123-test</div>
              <div>⚙️ 공정 노드: process-456-test</div>
              <div>📁 그룹 노드: group-789-test</div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-2">연결 규칙</h3>
            <div className="text-sm space-y-1">
              <div>✅ 모든 노드 간 연결 가능</div>
              <div>❌ 같은 노드 간 연결 불가</div>
              <div>❌ 중복 연결 불가</div>
              <div>✅ 4방향 핸들 지원</div>
            </div>
          </div>

          <div>
            <h3 className="font-semibold mb-2">테스트 결과</h3>
            <div className="bg-white border rounded p-2 h-64 overflow-y-auto text-sm">
              {testResults.length === 0 ? (
                <div className="text-gray-500">테스트를 실행하거나 노드를 연결해보세요</div>
              ) : (
                testResults.map((result, index) => (
                  <div key={index} className="mb-1">
                    {result}
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* React Flow 캔버스 */}
      <div className="flex-1">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onConnect={handleConnect}
          onConnectStart={handleConnectStart}
          onConnectEnd={handleConnectEnd}
          connectionMode={ConnectionMode.Loose}
          defaultEdgeOptions={{ type: 'custom' }}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>
    </div>
  );
}
