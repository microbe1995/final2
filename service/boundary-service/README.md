# Cal_boundary 서비스 (ReactFlow 전용)

## 🚀 서비스 개요

Cal_boundary 서비스는 **ReactFlow 기반 Canvas** 및 **CBAM 산정경계 설정 기능**을 제공하는 FastAPI 애플리케이션입니다.

## 🏗️ 주요 기능

### 1. ReactFlow 기반 Canvas 관리
- Canvas 생성, 수정, 삭제
- **ReactFlow 노드/엣지 관리**
- **실시간 ReactFlow 상태 동기화**
- **ReactFlow 이벤트 핸들러 지원** (onNodesChange, onEdgesChange, onConnect)
- **Panning & Zooming 완전 지원**
- **Connection 관리 및 자동 엣지 생성**
- Canvas 템플릿 및 가져오기/내보내기
- Canvas 병합 및 복제

### 2. 🆕 CBAM 산정경계 설정 (CBAM Boundary)
- **산정경계 설정**: CBAM 대상 제품 생산을 위한 경계 설정
- **경계 유형 관리**: 개별/통합 경계 설정 및 관리
- **공정 포함/제외**: 산정경계에 포함되거나 제외되는 공정 관리
- **할당 방법 설정**: 공유 자원의 할당 방법론 설정

## 📁 프로젝트 구조

```
app/
├── domain/
│   ├── canvas/              # ReactFlow 기반 Canvas 도메인
│   │   ├── canvas_controller.py    # Canvas HTTP API
│   │   ├── canvas_entity.py        # Canvas 엔티티 (ReactFlow 통합)
│   │   ├── canvas_schema.py        # Canvas 스키마 (ReactFlow 통합)
│   │   ├── canvas_service.py       # Canvas 비즈니스 로직
│   │   └── canvas_repository.py    # Canvas 데이터 접근
│   └── boundary/            # CBAM 산정경계 도메인
│       ├── boundary_controller.py  # 산정경계 HTTP API
│       ├── boundary_entity.py      # 산정경계 엔티티
│       ├── boundary_schema.py      # 산정경계 스키마
│       ├── boundary_service.py     # 산정경계 비즈니스 로직
│       └── boundary_repository.py  # 산정경계 데이터 접근
├── common/                  # 공통 유틸리티
└── main.py                 # 메인 애플리케이션
```

## 🔌 API 엔드포인트

### 기본 API
- `GET /health` - 서비스 상태 확인
- `GET /docs` - Swagger API 문서 (개발 모드)

### Canvas API (ReactFlow 전용)
- `POST /canvas` - Canvas 생성
- `GET /canvas` - Canvas 목록 조회
- `PUT /canvas/{id}` - Canvas 수정
- `DELETE /canvas/{id}` - Canvas 삭제

#### 🔄 **ReactFlow 전용 API**
- `POST /canvas/reactflow/initialize` - ReactFlow 캔버스 초기화
- `GET /canvas/reactflow/{canvas_id}/state` - ReactFlow 상태 조회
- `PUT /canvas/reactflow/{canvas_id}/state` - ReactFlow 상태 업데이트
- `POST /canvas/reactflow/{canvas_id}/nodes` - ReactFlow 노드 추가
- `DELETE /canvas/reactflow/{canvas_id}/nodes/{node_id}` - ReactFlow 노드 제거
- `POST /canvas/reactflow/{canvas_id}/edges` - ReactFlow 엣지 추가
- `DELETE /canvas/reactflow/{canvas_id}/edges/{edge_id}` - ReactFlow 엣지 제거
- `POST /canvas/reactflow/{canvas_id}/changes/nodes` - ReactFlow 노드 변경사항 적용
- `POST /canvas/reactflow/{canvas_id}/changes/edges` - ReactFlow 엣지 변경사항 적용
- `GET /canvas/reactflow/examples/initial` - ReactFlow 초기 예제 반환

#### 🔗 **Connection 관련 API (onConnect 핸들러 지원)**
- `POST /canvas/reactflow/{canvas_id}/connect` - ReactFlow 연결 생성 (onConnect 핸들러)
- `POST /canvas/reactflow/{canvas_id}/connection-events` - ReactFlow 연결 이벤트 배치 처리
- `GET /canvas/reactflow/examples/onconnect` - onConnect 핸들러 사용 예제 반환

#### 🎯 **Panning & Zooming API (완전한 뷰포트 제어)**
- `POST /canvas/reactflow/{canvas_id}/viewport` - ReactFlow 뷰포트 변경 (onViewportChange)
- `POST /canvas/reactflow/{canvas_id}/fit-view` - ReactFlow fitView 자동 화면 맞춤
- `GET /canvas/reactflow/{canvas_id}/interaction-config` - 인터랙션 설정 조회
- `PUT /canvas/reactflow/{canvas_id}/interaction-config` - 인터랙션 설정 업데이트
- `GET /canvas/reactflow/examples/panning-zooming` - Panning & Zooming 완전 구현 예제

### CBAM 산정경계 설정 API
- `POST /boundary/boundary/create` - 산정경계 설정 생성
- `GET /boundary/boundary/{boundary_id}` - 산정경계 설정 조회
- `GET /boundary/health` - 서비스 상태 확인
- `GET /boundary/info` - 서비스 정보 조회

## 🛠️ 기술 스택

- **Framework**: FastAPI
- **Language**: Python 3.11+
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **Validation**: Pydantic
- **Logging**: Loguru
- **Documentation**: OpenAPI/Swagger
- **Frontend Integration**: ReactFlow (@xyflow/react)

## 🔄 ReactFlow 사용법

### 1. 기본 설정 (Frontend)

```javascript
// 필수 import
import { useState, useCallback } from 'react';
import { ReactFlow, applyEdgeChanges, applyNodeChanges } from '@xyflow/react';

// 초기 노드/엣지 설정 (API에서 가져오기)
const response = await fetch('/canvas/reactflow/examples/initial');
const { initialNodes, initialEdges } = await response.json();

// 상태 초기화
export default function App() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);
  
  return (
    <div style={{ height: '100%', width: '100%' }}>
      <ReactFlow>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
```

### 2. 이벤트 핸들러 설정

```javascript
// 필수 import 추가
import { addEdge } from '@xyflow/react';

// 노드/엣지 변경사항 처리
const onNodesChange = useCallback(
  (changes) => setNodes((nodesSnapshot) => applyNodeChanges(changes, nodesSnapshot)),
  [],
);
const onEdgesChange = useCallback(
  (changes) => setEdges((edgesSnapshot) => applyEdgeChanges(changes, edgesSnapshot)),
  [],
);

// 🔗 onConnect 핸들러 (새로운 연결 생성)
const onConnect = useCallback(
  (params) => setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot)),
  [],
);

// ReactFlow에 전달
<ReactFlow
  nodes={nodes}
  edges={edges}
  onNodesChange={onNodesChange}
  onEdgesChange={onEdgesChange}
  onConnect={onConnect}
  fitView
>
  <Background />
  <Controls />
</ReactFlow>
```

### 3. 백엔드 동기화

```javascript
// 상태를 백엔드에 저장
const saveToBackend = async (canvasId) => {
  await fetch(`/canvas/reactflow/${canvasId}/state`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      nodes,
      edges,
      viewport: { x: 0, y: 0, zoom: 1 }
    })
  });
};

// 백엔드에서 상태 로드
const loadFromBackend = async (canvasId) => {
  const response = await fetch(`/canvas/reactflow/${canvasId}/state`);
  const state = await response.json();
  setNodes(state.nodes);
  setEdges(state.edges);
};

// 🔗 onConnect 핸들러 + 백엔드 동기화
const onConnect = useCallback(
  async (params) => {
    // 로컬 상태 즉시 업데이트 (사용자 경험 향상)
    setEdges((edgesSnapshot) => addEdge(params, edgesSnapshot));
    
    // 백엔드 동기화 (비동기)
    try {
      await fetch(`/canvas/reactflow/${canvasId}/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          canvas_id: canvasId,
          connection: params,
          edge_options: { 
            animated: false, 
            style: { stroke: '#b1b1b7' } 
          }
        })
      });
    } catch (error) {
      console.error('연결 저장 실패:', error);
      // 실패 시 사용자에게 알림 또는 롤백 로직 추가
    }
  },
  [canvasId],
);
```

### 4. 🎯 완전한 Panning & Zooming 구현

```javascript
// ReactFlow 공식 문서와 동일한 완전한 구현
import React, { useState, useCallback } from 'react';
import { 
  ReactFlow, 
  Background, 
  Controls, 
  applyNodeChanges, 
  applyEdgeChanges, 
  addEdge 
} from '@xyflow/react';

function ReactFlowComplete() {
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);
  const [viewport, setViewport] = useState({ x: 0, y: 0, zoom: 1 });

  // 🔄 기본 이벤트 핸들러들
  const onNodesChange = useCallback(
    (changes) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );

  const onEdgesChange = useCallback(
    (changes) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  // 📐 뷰포트 변경 핸들러 (백엔드 동기화)
  const onViewportChange = useCallback(
    async (newViewport) => {
      setViewport(newViewport);
      
      // 백엔드 동기화 (디바운스 권장)
      try {
        await fetch(`/canvas/reactflow/${canvasId}/viewport`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            canvas_id: canvasId,
            viewport: newViewport,
            type: 'viewport'
          })
        });
      } catch (error) {
        console.error('뷰포트 저장 실패:', error);
      }
    },
    [canvasId]
  );

  // 🎯 fitView 버튼 핸들러
  const handleFitView = async () => {
    try {
      const response = await fetch(`/canvas/reactflow/${canvasId}/fit-view`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          padding: 0.1,
          includeHiddenNodes: false,
          duration: 800
        })
      });
      
      const result = await response.json();
      setViewport(result.viewport);
    } catch (error) {
      console.error('fitView 실패:', error);
    }
  };

  return (
    <div style={{ height: '100vh', width: '100vw' }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        
        // 🎯 완전한 Panning & Zooming 설정
        panOnDrag={true}              // 드래그로 패닝
        panOnScroll={false}           // 스크롤로 패닝 (기본: false)
        panActivationKeyCode="Space"  // Space키로 패닝 모드
        
        zoomOnScroll={true}           // 스크롤로 줌
        zoomOnPinch={true}            // 핀치로 줌
        zoomOnDoubleClick={true}      // 더블클릭 줌
        zoomActivationKeyCode="Control" // Ctrl키로 줌 모드
        minZoom={0.1}                 // 최소 줌
        maxZoom={5}                   // 최대 줌
        
        // 📐 Viewport 완전 제어
        viewport={viewport}
        onViewportChange={onViewportChange}
        fitView                       // 초기 화면 맞춤
        
        // 🎮 인터랙션 설정
        elementsSelectable={true}
        nodesDraggable={true}
        nodesConnectable={true}
        selectNodesOnDrag={false}
        preventScrolling={true}       // 기본 스크롤 방지
        
        // 🎹 키보드 단축키
        selectionKeyCode="Shift"      // Shift로 선택 모드
        multiSelectionKeyCode="Control" // Ctrl로 다중 선택
        deleteKeyCode="Delete"        // Delete로 삭제
      >
        <Background />
        <Controls />
      </ReactFlow>
      
      {/* 🎯 fitView 버튼 */}
      <button 
        onClick={handleFitView}
        style={{ position: 'absolute', top: 10, right: 10 }}
      >
        Fit View
      </button>
    </div>
  );
}
```

## 🚀 실행 방법

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. 서비스 실행
```bash
# 개발 모드
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 프로덕션 모드
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### 3. Docker 실행
```bash
docker build -t cal-boundary .
docker run -p 8001:8001 cal-boundary
```

## 📊 CBAM 산정경계 설정 워크플로우

### 단계 1: 기업 정보 입력 및 검증
1. 기업명, 사업장 주소, 사업자등록번호 등 기본 정보 입력
2. 입력된 정보의 유효성 검증
3. 검증 오류 시 수정 요청

### 단계 2: CBAM 대상 제품 확인
1. 수출 제품의 HS 코드 및 CN 코드 입력
2. CBAM 대상 품목 여부 자동 확인
3. 대상 제품 목록 작성

### 단계 3: 생산 공정 정보 입력
1. 사업장 내 모든 생산 공정 리스트 작성
2. 각 공정별 투입 원료, 연료, 에너지 흐름 정의
3. 공동 사용 유틸리티 설비 식별
4. CBAM 대상/비대상 제품 생산 여부 표시

### 단계 4: 보고 기간 설정
1. 역년, 회계연도, 국내제도 중 선택
2. 12개월 기준 보고 기간 설정
3. 시작일/종료일 및 기간 길이 검증

### 단계 5: 산정경계 설정
1. CBAM 대상 제품 생산 공정 중심으로 경계 설정
2. 개별/통합 경계 유형 선택
3. 포함/제외 공정 명확히 구분
4. 공동 사용 유틸리티 가상 분할 계획

### 단계 6: 배출원 및 소스 스트림 식별
1. CO2 배출원 자동 식별 (연소설비, 화학반응 등)
2. 탄소 함유 물질 (연료, 원료) 식별
3. 전구물질 여부 확인 및 내재 배출량 고려

### 단계 7: 데이터 할당 계획 수립
1. 공유 자원 사용 공정 식별
2. 가동시간, 전력사용량 등 기준 할당 방법 선택
3. 공정별 할당 비율 계산

### 단계 8: 종합 분석 및 권장사항
1. 전체 과정 검증 결과 요약
2. 산정경계 설정 결과 제공
3. 다음 단계 및 권장사항 제시

## 🔍 CBAM 규정 준수 사항

### 철강 부문 특화 기능
- **온실가스 종류**: CO2만 고려 (N2O, PFCs 제외)
- **HS 코드**: 7208-7216 (철강 제품)
- **전구물질**: 소결광, 펠릿, 선철, 용강 등
- **복합제품**: 전구물질 내재 배출량 포함 계산

### 데이터 할당 우선순위
1. **법정계량기** - 가장 높은 신뢰도
2. **자체계량기** - 중간 신뢰도
3. **대체 방법** - 가동시간, 정격용량, 화학양론식 등

### 보고 기간 요구사항
- **최소 기간**: 3개월
- **기본 기간**: 12개월 (역년/회계연도/국내제도)
- **계절적 변동성**: 사업장 운영 특성 반영

## 📈 향후 개발 계획

### 단기 계획 (1-3개월)
- [ ] 데이터베이스 연동 및 영속성 구현
- [ ] 사용자 인증 및 권한 관리
- [ ] API 응답 캐싱 및 성능 최적화

### 중기 계획 (3-6개월)
- [ ] 배출량 계산 엔진 연동
- [ ] 보고서 생성 및 내보내기 기능
- [ ] 다국어 지원 (한국어/영어)

### 장기 계획 (6개월 이상)
- [ ] AI 기반 자동 경계 설정 제안
- [ ] 실시간 모니터링 및 알림 시스템
- [ ] EU CBAM 시스템과의 직접 연동

## 🤝 기여 방법

1. 이슈 생성 또는 기존 이슈 확인
2. 기능 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 코드 작성 및 테스트
4. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

- **개발팀**: Cal_boundary Development Team
- **이메일**: dev@cal-boundary.com
- **문서**: `/docs` 엔드포인트에서 API 문서 확인 가능
