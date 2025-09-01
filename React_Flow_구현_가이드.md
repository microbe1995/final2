# React Flow 구현 가이드 - CBAM 산정경계설정

## 📋 목차
1. [노드 타입 구성](#노드-타입-구성)
2. [핸들 시스템](#핸들-시스템)
3. [연결 시스템](#연결-시스템)
4. [연결 가능한 패턴](#연결-가능한-패턴)
5. [주요 기능](#주요-기능)
6. [사용 시나리오](#사용-시나리오)
7. [React Flow 공식 문서 준수사항](#react-flow-공식-문서-준수사항)

---

## 🎯 노드 타입 구성

### 제품 노드 (ProductNode)
- **타입**: `product`
- **스타일**: 보라색 테두리 (`bg-purple-50 border-purple-300`)
- **아이콘**: 📦
- **핸들**: 4방향 모두 지원
- **파일**: `frontend/src/components/atomic/atoms/ProductNode.tsx`

### 공정 노드 (ProcessNode)
- **타입**: `process`
- **스타일**: 주황색 테두리 (`bg-orange-50 border-orange-300`)
- **핸들**: 4방향 모두 지원
- **특별 기능**: 읽기 전용 공정 지원
- **파일**: `frontend/src/components/atomic/atoms/ProcessNode.tsx`

### 그룹 노드
- **타입**: `group`
- **렌더링**: ProductNode 컴포넌트 사용
- **핸들**: 4방향 모두 지원

---

## 🔗 핸들 시스템 (HandleStyles.tsx)

### 4방향 핸들 구성
```typescript
// 각 노드마다 4개의 핸들 생성
- Left:   `${nodeId}-left`
- Right:  `${nodeId}-right`  
- Top:    `${nodeId}-top`
- Bottom: `${nodeId}-bottom`
```

### 핸들 특성
- **타입**: `source` (연결 시작점)
- **스타일**: 파란색 원형 (`#3b82f6`)
- **효과**: hover 시 확대 (`hover:scale-125`)
- **커서**: 십자 모양 (`cursor: crosshair`)
- **그림자**: 파란색 글로우 효과

### 핸들 구현 코드
```typescript
export const renderFourDirectionHandles = (isConnectable = true, nodeId?: string) => {
  const nodeIdStr = nodeId || 'node';
  
  const handleConfigs = [
    { position: Position.Left, id: `${nodeIdStr}-left` },
    { position: Position.Right, id: `${nodeIdStr}-right` },
    { position: Position.Top, id: `${nodeIdStr}-top` },
    { position: Position.Bottom, id: `${nodeIdStr}-bottom` },
  ];

  return handleConfigs.map(({ position, id }) => (
    <Handle
      key={id}
      id={id}
      type="source"
      position={position}
      isConnectable={isConnectable}
      className={cls}
      style={handleStyle}
    />
  ));
};
```

---

## 🔧 연결 시스템

### 연결 모드
- **모드**: `ConnectionMode.Loose`
- **특징**: 유연한 연결 허용
- **파일**: `frontend/src/components/cbam/ProcessManager.tsx`

### 연결 검증 로직
```typescript
✅ 허용되는 연결:
- 다른 노드 간 연결
- 다른 핸들 간 연결
- 핸들 ID가 다른 연결

❌ 차단되는 연결:
- 같은 노드 간 연결
- 같은 핸들 간 연결
- 정확히 동일한 핸들 ID 연결
```

### React Flow 연결 검증 구현
```typescript
isValidConnection={(connection) => {
  // 같은 노드 간 연결 방지
  if (connection.source === connection.target) {
    return false;
  }
  
  // 같은 핸들 간 연결 방지 (핸들이 있는 경우에만)
  if (connection.sourceHandle && connection.targetHandle && 
      connection.sourceHandle === connection.targetHandle) {
    return false;
  }
  
  // 이미 존재하는 연결 확인 (핸들 ID까지 포함하여 정확히 같은 연결만 체크)
  const existingEdge = edges.find(edge => 
    edge.source === connection.source && 
    edge.target === connection.target &&
    edge.sourceHandle === connection.sourceHandle &&
    edge.targetHandle === connection.targetHandle
  );
  
  if (existingEdge) {
    return false;
  }
  
  return true;
}}
```

---

## 🎮 연결 가능한 패턴

### 기본 연결 패턴
```
제품 노드 ↔ 공정 노드
제품 노드 ↔ 제품 노드  
공정 노드 ↔ 공정 노드
그룹 노드 ↔ 모든 노드
```

### 4방향 연결 예시
```
철강1-left   → 압연-right   ✅
철강1-right  → 압연-left    ✅
철강1-top    → 압연-bottom  ✅
철강1-bottom → 압연-top     ✅
```

### 다중 연결 가능성
- **3개 노드 기준**: 최대 12개 연결 가능
- **4개 노드 기준**: 최대 24개 연결 가능
- **공식**: `노드 수 × 4방향 × (노드 수 - 1)`

### 연결 시나리오 예시
```
시나리오 1: 단순 연결
철강1 → 압연 → 코팅

시나리오 2: 분기 연결
철강1 → 압연
철강1 → 열처리
압연 → 코팅
열처리 → 코팅

시나리오 3: 복합 연결
철강1-left   → 압연-right
철강1-right  → 열처리-left
압연-top     → 코팅-bottom
열처리-top   → 코팅-bottom
```

---

## 🛠️ 주요 기능

### 노드 관리
- ✅ 노드 추가/삭제
- ✅ 노드 드래그 앤 드롭
- ✅ 노드 선택/해제
- ✅ 노드 크기 조절
- ✅ 노드 위치 조정

### 연결 관리
- ✅ 핸들 클릭으로 연결 시작
- ✅ 드래그로 연결선 생성
- ✅ 핸들에 가져다 대면 연결 완료
- ✅ 연결선 삭제 (Delete 키)
- ✅ 연결선 재연결

### 시각적 기능
- ✅ 커스텀 Edge 스타일
- ✅ 화살표 마커
- ✅ MiniMap
- ✅ 줌/팬 컨트롤
- ✅ 배경 그리드
- ✅ 노드 선택 하이라이트

### 데이터 연동
- ✅ 백엔드 API 연동
- ✅ 실시간 연결 저장
- ✅ 공정 체인 탐지
- ✅ 통합 공정 그룹 관리
- ✅ 사업장별 캔버스 분리

---

## 🎯 사용 시나리오

### CBAM 산정경계설정 프로세스
1. **사업장 선택** → 캔버스 초기화
2. **제품 노드 추가** → 제품 선택 모달
3. **공정 노드 추가** → 공정 선택 모달
4. **핸들 연결** → 4방향 중 원하는 방향 선택
5. **공정 체인 완성** → 복잡한 공정 흐름 구성

### 연결 제한사항
- ❌ 같은 노드 내부 연결 불가
- ❌ 정확히 동일한 핸들 간 연결 불가
- ✅ 다른 핸들 사용 시 같은 노드 간 연결 가능

### 실제 사용 예시
```
1. 철강 제품 노드 추가
2. 압연 공정 노드 추가
3. 코팅 공정 노드 추가
4. 철강1-right → 압연-left 연결
5. 압연-right → 코팅-left 연결
6. 결과: 철강1 → 압연 → 코팅 체인 완성
```

---

## 📚 React Flow 공식 문서 준수사항

### 핸들 구현
- ✅ **고유 ID**: 각 핸들마다 고유한 ID 할당
- ✅ **타입 설정**: `source` 타입으로 연결 시작점 설정
- ✅ **위치 지정**: `Position.Left`, `Position.Right` 등 명확한 위치
- ✅ **연결 가능성**: `isConnectable` 속성으로 연결 제어

### 연결 검증
- ✅ **`isValidConnection`**: React Flow 컴포넌트 레벨에서 검증
- ✅ **핸들 ID 검증**: `sourceHandle`, `targetHandle` 사용
- ✅ **중복 방지**: 정확한 핸들 ID 기반 중복 체크

### 연결 모드
- ✅ **Loose 모드**: 유연한 연결 허용
- ✅ **핸들 선택적**: 핸들 ID가 없어도 연결 가능
- ✅ **자동 타겟 인식**: React Flow가 자동으로 target 핸들로 인식

### 이벤트 처리
- ✅ **`onConnectStart`**: 연결 시작 이벤트
- ✅ **`onConnect`**: 연결 완료 이벤트
- ✅ **`onConnectEnd`**: 연결 종료 이벤트

---

## 🔍 파일 구조

```
frontend/src/
├── components/
│   ├── atomic/atoms/
│   │   ├── HandleStyles.tsx      # 핸들 스타일 및 4방향 핸들
│   │   ├── ProductNode.tsx       # 제품 노드 컴포넌트
│   │   ├── ProcessNode.tsx       # 공정 노드 컴포넌트
│   │   └── CustomEdge.tsx        # 커스텀 엣지 스타일
│   └── cbam/
│       └── ProcessManager.tsx    # 메인 프로세스 매니저
└── hooks/
    └── useProcessCanvas.ts       # React Flow 상태 관리
```

---

## 🎉 결론

현재 구현된 React Flow 시스템은 **완전한 4방향 다중 연결 시스템**으로, CBAM 산정경계설정에서 복잡한 공정 체인을 자유롭게 구성할 수 있습니다.

### 주요 특징
- 🎯 **4방향 핸들**: 각 노드마다 left, right, top, bottom 핸들
- 🔗 **다중 연결**: 같은 노드 간에도 다른 핸들로 연결 가능
- ✅ **React Flow 공식 문서 준수**: 모든 구현이 공식 권장사항을 따름
- 🛠️ **완전한 기능**: 노드 관리, 연결 관리, 시각적 기능 모두 지원

이제 CBAM 산정경계설정에서 **복잡한 공정 체인**을 직관적이고 효율적으로 구성할 수 있습니다!
