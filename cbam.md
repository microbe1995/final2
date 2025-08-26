Next.js(앱 라우터) + TypeScript

@xyflow/react v12 사용

ProductNode는 커스텀 컴포넌트, group은 내장 타입을 사용한다.

에러 증상: 제품 노드 4방향 핸들에서 연결이 되지 않거나 일부만 동작. group 노드 클릭 시 클라이언트 에러.

목표

제품 노드에 4개 핸들(좌/우/상/하)을 모두 사용 가능하게 하고, 각 핸들 간 연결이 안정적으로 동작하도록 한다.

group 노드는 내장 타입을 유지하여 클릭/리사이즈/선택 시 에러가 발생하지 않게 한다.

커스텀 엣지의 markerEnd 지정은 ReactFlow의 defaultEdgeOptions 한 곳에서만 설정한다.

작업 지시

components/atomic/atoms/ProductNode.tsx

각 Handle에 고유 id: "left", "right", "top", "bottom"을 부여한다.

type, position을 좌=target, 우=source, 상=target, 하=source로 배치한다.

isConnectable을 전달하고 pointerEvents가 막히지 않도록 wrapper에 pointerEvents: 'auto'를 준다.

app/**/ProcessManager.tsx(또는 해당 페이지 컴포넌트)

nodeTypes에서 group 매핑을 제거하고 { custom: ProductNode }만 남긴다.

ReactFlow onConnect 핸들러에서 params.sourceHandle과 params.targetHandle을 edge에 포함한다.

defaultEdgeOptions={{ type:'custom', markerEnd:{ type: MarkerType.ArrowClosed } }}를 설정한다.

group 노드는 type: 'group'으로 내장 타입을 쓰며, style로만 테두리/배경을 지정한다. pointerEvents는 'auto'.

components/**/edges/CustomEdge.tsx

path 요소에서 markerEnd 속성을 제거한다(중복 방지).

stroke, strokeWidth만 유지한다.

검증 기준

제품 노드의 4개 핸들 각각에서 드래그 시작이 가능하고, 연결 시 onConnect의 params에 sourceHandle/targetHandle이 포함된다.

동일 노드 간 상이한 핸들로 여러 엣지를 추가할 수 있다(핸들 id가 반영된 edge 구조).

group 노드 클릭/선택/리사이즈 시 클라이언트 에러가 발생하지 않는다.

MiniMap/Controls/Background가 정상 동작한다.

마이그레이션 주의

이전에 생성된 edge 데이터에 sourceHandle/targetHandle 누락분이 있으면 삭제 후 재연결한다.

만약 스타일 시트에서 .react-flow__handle에 pointer-events 관련 오버라이드가 있다면 제거한다.

위 프롬프트를 참고해서 현재 잇는 문제들을 해결해줘 