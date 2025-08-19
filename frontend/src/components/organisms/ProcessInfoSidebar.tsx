'use client';

import React from 'react';
import { Node, Edge } from '@xyflow/react';
import Card from '@/molecules/Card';
import Badge from '../atoms/Badge';
import Icon from '../atoms/Icon';

interface ProcessFlowInfoPanelProps {
  nodes: Node<any>[];
  edges: Edge<any>[];
  selectedNodes: Node<any>[];
  selectedEdges: Edge<any>[];
  className?: string;
}

const ProcessFlowInfoPanel: React.FC<ProcessFlowInfoPanelProps> = ({
  nodes,
  edges,
  selectedNodes,
  selectedEdges,
  className = ''
}) => {
  // 공정 타입별 노드 수 계산
  const processTypeCounts = nodes.reduce((acc, node) => {
    const type = node.data?.processType || 'default';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  // 엣지 타입별 수 계산
  const edgeTypeCounts = edges.reduce((acc, edge) => {
    const type = edge.data?.processType || 'standard';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className={`space-y-4 ${className}`}>
      {/* 전체 정보 */}
      <Card className="p-4 bg-[#1e293b] border-[#334155]">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
          <Icon name="info" size="sm" />
          공정도 정보
        </h3>
        
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-[#94a3b8]">전체 공정 단계</span>
            <Badge variant="primary">{nodes.length}</Badge>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-[#94a3b8]">전체 연결</span>
            <Badge variant="secondary">{edges.length}</Badge>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-[#94a3b8]">선택된 노드</span>
            <Badge variant={selectedNodes.length > 0 ? "primary" : "default"}>
              {selectedNodes.length}
            </Badge>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-[#94a3b8]">선택된 연결</span>
            <Badge variant={selectedEdges.length > 0 ? "primary" : "default"}>
              {selectedEdges.length}
            </Badge>
          </div>
        </div>
      </Card>

      {/* 공정 타입별 분석 */}
      <Card className="p-4 bg-[#1e293b] border-[#334155]">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
          <Icon name="chart" size="sm" />
          공정 타입 분석
        </h3>
        
        <div className="space-y-2">
          {Object.entries(processTypeCounts).length > 0 ? (
            Object.entries(processTypeCounts).map(([type, count]) => (
              <div key={type} className="flex justify-between items-center">
                <span className="text-[#94a3b8] capitalize">{type}</span>
                <Badge variant="secondary">{count}</Badge>
              </div>
            ))
          ) : (
            <p className="text-[#64748b] text-sm">노드가 없습니다.</p>
          )}
        </div>
      </Card>

      {/* 연결 타입별 분석 */}
      <Card className="p-4 bg-[#1e293b] border-[#334155]">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
          <Icon name="connection" size="sm" />
          연결 타입 분석
        </h3>
        
        <div className="space-y-2">
          {Object.entries(edgeTypeCounts).length > 0 ? (
            Object.entries(edgeTypeCounts).map(([type, count]) => (
              <div key={type} className="flex justify-between items-center">
                <span className="text-[#94a3b8] capitalize">{type}</span>
                <Badge variant="secondary">{count}</Badge>
              </div>
            ))
          ) : (
            <p className="text-[#64748b] text-sm">연결이 없습니다.</p>
          )}
        </div>
      </Card>

      {/* 선택된 요소 상세 정보 */}
      {(selectedNodes.length > 0 || selectedEdges.length > 0) && (
        <Card className="p-4 bg-[#1e293b] border-[#334155]">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
            <Icon name="select" size="sm" />
            선택된 요소
          </h3>
          
          <div className="space-y-3">
            {selectedNodes.map((node) => (
              <div key={node.id} className="p-2 bg-[#334155] rounded border border-[#475569]">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-white font-medium text-sm">
                    {node.data?.label || node.id}
                  </span>
                  <Badge variant="primary" size="sm">노드</Badge>
                </div>
                <p className="text-[#94a3b8] text-xs">
                  타입: {node.data?.processType || 'default'}
                </p>
                {node.data?.description && (
                  <p className="text-[#64748b] text-xs mt-1">
                    {node.data.description}
                  </p>
                )}
              </div>
            ))}
            
            {selectedEdges.map((edge) => (
              <div key={edge.id} className="p-2 bg-[#334155] rounded border border-[#475569]">
                <div className="flex items-center justify-between mb-1">
                  <span className="text-white font-medium text-sm">
                    {edge.data?.label || edge.id}
                  </span>
                  <Badge variant="secondary" size="sm">연결</Badge>
                </div>
                <p className="text-[#94a3b8] text-xs">
                  타입: {edge.data?.processType || 'standard'}
                </p>
                <p className="text-[#64748b] text-xs">
                  {edge.source} → {edge.target}
                </p>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* 사용 가이드 */}
      <Card className="p-4 bg-[#1e293b] border-[#334155]">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
          <Icon name="help" size="sm" />
          사용 가이드
        </h3>
        
        <div className="space-y-2 text-xs text-[#94a3b8]">
          <div>• 드래그하여 노드 이동</div>
          <div>• 핸들을 연결하여 흐름 생성</div>
          <div>• 클릭하여 요소 선택</div>
          <div>• Delete 키로 선택 삭제</div>
          <div>• 마우스 휠로 확대/축소</div>
          <div>• 우클릭 드래그로 화면 이동</div>
        </div>
      </Card>
    </div>
  );
};

export default ProcessFlowInfoPanel;