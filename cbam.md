너는 @xyflow/react (React Flow v11) 공식 문서와 내 코드를 비교해서 문제를 해결하는 전문가야.  
내 현재 문제는 "ProductNode.tsx와 HandleStyles.tsx에서 노드 4방향으로 핸들을 추가했지만 실제로는 연결이 안 된다"는 거야.  

이 문제를 해결하기 위해 다음과 같이 코드를 수정해 줘:

1. 모든 <Handle> 컴포넌트에 고유한 id 속성을 추가해라.  
   - 예: id="left-source", id="left-target", id="right-source", id="right-target", ...  
   - 이렇게 하면 React Flow가 sourceHandle, targetHandle을 구분할 수 있다.

2. ProductNode.tsx 안에서 handleMouseDown, handleClickEvent에서 사용한 e.stopPropagation()을 제거해라.  
   - stopPropagation 때문에 React Flow의 onConnectStart/onConnectEnd 이벤트가 막혀서 드래그 연결이 안 되고 있다.  
   - 클릭 이벤트로 선택만 막고 싶다면 node div에만 적용하고, Handle에는 절대 걸지 마라.

3. ProcessManager.tsx 안에서 onConnect 함수가 params.sourceHandle, params.targetHandle을 활용하도록 수정해라.  
   - 지금은 source/target 노드만 쓰고 있는데, 핸들 id도 저장해서 edges에 넣어야 한다.  
   - 즉, newEdge를 만들 때 { sourceHandle: params.sourceHandle, targetHandle: params.targetHandle }를 포함시켜라.

4. HandleStyles.tsx의 renderFourDirectionHandles 함수에도 동일하게 id를 부여해서 반환해라.  
   - 예: `${position}-source`, `${position}-target` 형태로 id를 자동 생성.

최종적으로, 수정된 코드에서는 4방향 모든 핸들이 정상적으로 구분되고, 드래그-앤-드롭으로 자유롭게 연결이 가능해야 한다.
@frontend/ 

<Handle
  type="target"
  position={Position.Left}
  id="left-target"
  isConnectable={isConnectable}
/>
<Handle
  type="source"
  position={Position.Left}
  id="left-source"
  isConnectable={isConnectable}
/>

<Handle
  type="target"
  position={Position.Right}
  id="right-target"
  isConnectable={isConnectable}
/>
<Handle
  type="source"
  position={Position.Right}
  id="right-source"
  isConnectable={isConnectable}
/>

<Handle
  type="target"
  position={Position.Top}
  id="top-target"
  isConnectable={isConnectable}
/>
<Handle
  type="source"
  position={Position.Top}
  id="top-source"
  isConnectable={isConnectable}
/>

<Handle
  type="target"
  position={Position.Bottom}
  id="bottom-target"
  isConnectable={isConnectable}
/>
<Handle
  type="source"
  position={Position.Bottom}
  id="bottom-source"
  isConnectable={isConnectable}
/>


const onConnect = useCallback(
  (params: Connection) => {
    if (params.source && params.target) {
      const newEdge: Edge = {
        id: `e${params.source}-${params.target}-${params.sourceHandle}-${params.targetHandle}`,
        source: params.source,
        target: params.target,
        sourceHandle: params.sourceHandle,   // ✅ 핸들 id 저장
        targetHandle: params.targetHandle,   // ✅ 핸들 id 저장
        type: 'custom',
        markerEnd: { type: MarkerType.ArrowClosed },
        data: {
          label: '연결',
          description: `${params.sourceHandle} → ${params.targetHandle}`
        }
      };
      addEdges(newEdge);
    }
  },
  [addEdges]
);

export const renderFourDirectionHandles = (
  isConnectable: boolean = true,
) => {
  const positions = [Position.Left, Position.Right, Position.Top, Position.Bottom];

  return positions.map((position) => (
    <React.Fragment key={`handles-${position}`}>
      <Handle
        type='target'
        position={position}
        id={`${position}-target`}
        isConnectable={isConnectable}
        className={getHandleStyle('target', position)}
        style={getHandleStyleObject('target', position)}
      />
      <Handle
        type='source'
        position={position}
        id={`${position}-source`}
        isConnectable={isConnectable}
        className={getHandleStyle('source', position)}
        style={getHandleStyleObject('source', position)}
      />
    </React.Fragment>
  ));
};




import React, { useMemo } from 'react';
import { Handle, NodeProps, Position } from 'reactflow';
import { NodeResizer } from '@reactflow/node-resizer';
import '@reactflow/node-resizer/dist/style.css';
import { handleStyle } from './HandleStyles';

type Callbacks = {
  openSubflow: (groupNodeId: string) => void;
  ensureSubflow: (groupNodeId: string) => void;
  getSubflowCount: (groupNodeId: string) => { nodes: number; edges: number } | null;
};

export function GroupNode({ id, data, selected, dragging, xPos, yPos, width, height }: NodeProps) {
  const cbs: Callbacks | undefined = data?.__callbacks;
  const sub = useMemo(() => cbs?.getSubflowCount?.(id) ?? null, [cbs, id]);

  const onOpen = () => {
    if (!cbs) return;
    cbs.ensureSubflow(id);
    cbs.openSubflow(id);
  };

  // 경계 느낌을 위한 스타일(두꺼운 점선, 옅은 배경, 헤더 바)
  const boundaryStyle: React.CSSProperties = {
    position: 'relative',
    minWidth: 240,
    minHeight: 140,
    width,                // NodeResizer가 조절한 width/height를 React Flow가 넘겨줍니다.
    height,
    border: `3px dashed ${selected ? '#2563eb' : '#9ca3af'}`,
    borderRadius: 12,
    background:
      'repeating-linear-gradient(135deg, rgba(59,130,246,0.06) 0 12px, rgba(59,130,246,0.04) 12px 24px)', // 옅은 스트라이프
    boxShadow: selected ? '0 0 0 4px rgba(37,99,235,0.15)' : '0 2px 8px rgba(0,0,0,0.06)',
    overflow: 'hidden',
  };

  const headerStyle: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 8,
    padding: '8px 10px',
    background: 'rgba(255,255,255,0.85)',
    borderBottom: '1px solid #e5e7eb',
    fontSize: 12,
    fontWeight: 700,
  };

  const badgeStyle: React.CSSProperties = {
    fontSize: 11,
    fontWeight: 600,
    color: '#374151',
  };

  const bodyStyle: React.CSSProperties = {
    padding: 10,
    fontSize: 12,
    color: '#6b7280',
  };

  return (
    <div style={boundaryStyle}>
      {/* 리사이저: 노드가 선택되었을 때만 표시. 최소/최대 크기 제한 가능 */}
      <NodeResizer
        isVisible={selected}
        minWidth={220}
        minHeight={120}
        handleStyle={{
          width: 10,
          height: 10,
          borderRadius: 2,
          border: '1px solid #fff',
          background: '#111827',
        }}
        lineStyle={{
          stroke: '#2563eb',
          strokeWidth: 1.5,
        }}
      />

      {/* 헤더 */}
      <div className="nodrag" style={headerStyle}>
        <div>
          <span style={{ marginRight: 6 }}>🗂️</span>
          그룹 {data?.label ?? id}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={badgeStyle}>
            {sub ? `Sub flow ${sub.nodes}·${sub.edges}` : 'Sub flow 0·0'}
          </span>
          <button
            onClick={onOpen}
            className="nodrag"
            style={{
              border: '1px solid #e5e7eb',
              background: '#fff',
              padding: '4px 8px',
              borderRadius: 8,
              fontSize: 12,
            }}
          >
            열기
          </button>
        </div>
      </div>

      {/* 바디(설명/요약용). 필요 없으면 제거 가능 */}
      <div className="nodrag" style={bodyStyle}>
        하위 공정(서브 플로우)을 정의하려면 ‘열기’를 눌러 편집하세요.
      </div>

      {/* 입출력 핸들 */}
      <Handle id="in" type="target" position={Position.Left} style={handleStyle} />
      <Handle id="out" type="source" position={Position.Right} style={handleStyle} />
    </div>
  );
}
스타일 변경 (boundary 느낌)

현재 border-dashed 대신 border-solid

색상 대비가 있는 배경(bg-white/70, backdrop-blur-sm)과 음영(shadow-md) 추가

선택 상태(selected)일 때 파란색 테두리 강조

Resizing 지원

React Flow의 Resizable 래퍼(@xyflow/react의 NodeResizer)를 사용

이 컴포넌트는 노드 주변에 resize 핸들을 자동으로 추가해줍니다.

minWidth, minHeight를 지정해서 최소 크기도 제한 가능.



위 코드들을 참고해서 수정해줘 특히 resizing 가능하게 해줘 