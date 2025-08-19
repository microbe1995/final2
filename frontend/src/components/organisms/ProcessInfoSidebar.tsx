'use client';

import React from 'react';
import { Node, Edge } from '@xyflow/react';
import Card from '@/molecules/Card';
import Button from '@/atoms/Button';
import Badge from '../atoms/Badge';
import Icon from '../atoms/Icon';

interface ProcessFlowInfoPanelProps {
  nodes: Node<any>[];
  edges: Edge<any>[];
  selectedNodes: Node<any>[];
  selectedEdges: Edge<any>[];
  savedCanvases: any[];
  currentCanvasId: string | null;
  isLoadingCanvases: boolean;
  serviceStatus: any;
  onLoadCanvas: (canvasId: string) => void;
  onDeleteCanvas: (canvasId: string) => void;
  onAddNode: () => void;
  onAddEdge: () => void;
  onDeleteSelected: () => void;
  isReadOnly: boolean;
  className?: string;
}

const ProcessFlowInfoPanel: React.FC<ProcessFlowInfoPanelProps> = ({
  nodes,
  edges,
  selectedNodes,
  selectedEdges,
  savedCanvases,
  currentCanvasId,
  isLoadingCanvases,
  serviceStatus,
  onLoadCanvas,
  onDeleteCanvas,
  onAddNode,
  onAddEdge,
  onDeleteSelected,
  isReadOnly,
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
      {/* MSA 서비스 상태 */}
      <Card className="p-4 bg-[#1e293b] border-[#334155]">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
          <Icon name="server" size="sm" />
          MSA 서비스 상태
        </h3>
        
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-[#94a3b8]">백엔드 연결</span>
            <Badge variant={serviceStatus?.status === 'healthy' ? 'success' : 'error'}>
              {serviceStatus?.status === 'healthy' ? '정상' : '오류'}
            </Badge>
          </div>
          
          <div className="flex justify-between items-center">
            <span className="text-[#94a3b8]">동기화 상태</span>
            <Badge variant={currentCanvasId ? 'success' : 'default'}>
              {currentCanvasId ? 'ON' : 'OFF'}
            </Badge>
          </div>
          
          {currentCanvasId && (
            <div className="text-xs text-[#64748b]">
              Canvas ID: {currentCanvasId.substring(0, 8)}...
            </div>
          )}
        </div>
      </Card>

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

      {/* 편집 도구 */}
      <Card className="p-4 bg-[#1e293b] border-[#334155]">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
          <Icon name="edit" size="sm" />
          편집 도구
        </h3>
        
        <div className="space-y-2">
          <Button
            variant="primary"
            size="sm"
            onClick={onAddNode}
            disabled={isReadOnly}
            className="w-full"
          >
            + 공정 노드
          </Button>
          <Button
            variant="secondary"
            size="sm"
            onClick={onAddEdge}
            disabled={isReadOnly || nodes.length < 2}
            className="w-full"
          >
            + 공정 흐름
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={onDeleteSelected}
            disabled={isReadOnly}
            className="w-full"
          >
            선택 삭제
          </Button>
        </div>
      </Card>

      {/* MSA 백엔드 저장된 Canvas 목록 */}
      <Card className="p-4 bg-[#1e293b] border-[#334155]">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
          <Icon name="database" size="sm" />
          저장된 공정도 (MSA)
        </h3>
        
        {isLoadingCanvases ? (
          <div className="text-center text-[#94a3b8] text-sm">
            🔄 불러오는 중...
          </div>
        ) : savedCanvases.length === 0 ? (
          <p className="text-[#64748b] text-sm">저장된 공정도가 없습니다.</p>
        ) : (
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {savedCanvases.map((canvas) => (
              <div key={canvas.id} className="p-3 bg-[#334155] rounded border border-[#475569]">
                <div className="flex justify-between items-start mb-2">
                  <div className="flex-1 min-w-0">
                    <p className="text-white font-medium text-sm truncate">{canvas.name}</p>
                    <p className="text-[#94a3b8] text-xs">
                      노드: {canvas.metadata?.nodeCount || 0}, 엣지: {canvas.metadata?.edgeCount || 0}
                    </p>
                    {canvas.metadata?.createdAt && (
                      <p className="text-[#64748b] text-xs">
                        {new Date(canvas.metadata.createdAt).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  <div className="flex gap-1 ml-2">
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={() => onLoadCanvas(canvas.id)}
                      className="text-xs py-1 px-2"
                    >
                      로드
                    </Button>
                    <Button
                      variant="danger"
                      size="sm"
                      onClick={() => onDeleteCanvas(canvas.id)}
                      className="text-xs py-1 px-2"
                    >
                      삭제
                    </Button>
                  </div>
                </div>
                {currentCanvasId === canvas.id && (
                  <Badge variant="success" size="sm">현재 로드됨</Badge>
                )}
              </div>
            ))}
          </div>
        )}
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
                {/* Sub Flow 정보 */}
                {node.parentId && (
                  <p className="text-purple-400 text-xs mt-1">
                    📁 그룹: {node.parentId}
                  </p>
                )}
                {node.type === 'groupNode' && (
                  <p className="text-purple-400 text-xs mt-1">
                    🗂️ 그룹 노드
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

      {/* Sub Flow 정보 */}
      <Card className="p-4 bg-[#1e293b] border-[#334155]">
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
          <Icon name="folder" size="sm" />
          Sub Flow 정보
        </h3>
        
        <div className="space-y-3">
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#94a3b8]">그룹 노드</span>
            <Badge variant="info" size="sm">
              {nodes.filter(n => n.type === 'groupNode').length}개
            </Badge>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#94a3b8]">자식 노드</span>
            <Badge variant="info" size="sm">
              {nodes.filter(n => n.parentId).length}개
            </Badge>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#94a3b8]">독립 노드</span>
            <Badge variant="info" size="sm">
              {nodes.filter(n => !n.parentId && n.type !== 'groupNode').length}개
            </Badge>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-[#94a3b8]">커스텀 노드</span>
            <Badge variant="success" size="sm">
              {nodes.filter(n => n.type === 'customNode').length}개
            </Badge>
          </div>
        </div>
      </Card>

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
           <div>• 그룹 노드로 공정 그룹화</div>
           <div>• 자식 노드는 부모와 함께 이동</div>
           <div>• Edge Z-Index로 레이어 순서 조정</div>
           <div>• Delete 키로 선택 삭제</div>
           <div>• 마우스 휠로 확대/축소</div>
           <div>• MSA 백엔드 실시간 동기화</div>
         </div>
       </Card>

       {/* 고급 기능 가이드 */}
       <Card className="p-4 bg-[#1e293b] border-[#334155]">
         <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-white">
           <Icon name="zap" size="sm" />
           고급 기능 가이드
         </h3>
         
         <div className="space-y-2 text-xs text-[#94a3b8]">
           <div>🎨 <strong>레이아웃 엔진:</strong></div>
           <div>• Dagre: 간단한 계층 구조</div>
           <div>• ELK: 고급 다이어그램</div>
           <div>• D3-Force: 물리 기반 배치</div>
           <div>• Cola: 제약 기반 레이아웃</div>
           
           <div className="mt-2">🛣️ <strong>엣지 라우팅:</strong></div>
           <div>• Smart Edge: 노드 충돌 방지</div>
           <div>• Orthogonal: 직교 다이어그램</div>
           <div>• Bezier: 부드러운 곡선</div>
           <div>• Step: 계단식 경로</div>
           
           <div className="mt-2">🖱️ <strong>뷰포트 모드:</strong></div>
           <div>• 기본: 표준 React Flow</div>
           <div>• 디자인: Figma/Sketch 스타일</div>
           <div>• 지도: 지도 네비게이션</div>
           <div>• 프레젠테이션: 읽기 전용</div>
         </div>
       </Card>
    </div>
  );
};

export default ProcessFlowInfoPanel;