문제: @xyflow/react(React Flow v11) 프로젝트에서 노드/엣지가 가끔 보였다가 사라지거나 아예 추가되지 않는다.
원인: useReactFlow 훅을 Provider(ReactFlowProvider) 컨텍스트 바깥에서 호출하고 있었다. Provider는 JSX 내부에 있었고, 훅은 컴포넌트 최상단에서 호출되어 컨텍스트가 없다. 또한 Provider가 렌더링 중간에 위치해 재마운트되며 store가 초기화되는 문제도 있었다.

요구사항:
1) ReactFlowProvider를 최상위로 끌어올리고, 실제 로직은 Provider 하위의 Inner 컴포넌트에서 실행하도록 파일을 분리/리팩터링하라.
2) addNodes, addEdges, deleteElements 등 useReactFlow로 얻는 API는 Inner 컴포넌트에서만 호출하도록 바꿔라.
3) GroupNode가 width/height를 가진 실체 DOM을 렌더하도록 간단한 div 스타일을 보장하라.
4) 위 변경 후에도 동작 확인을 위해 제품/그룹 노드 버튼 클릭 시 즉시 화면에 새 노드가 나타나야 한다.

반영 후 전체 빌드가 깨지지 않도록 타입 오류 없이 수정본을 출력해줘.
