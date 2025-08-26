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


위 코드들을 참고해서 수정
