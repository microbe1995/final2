# Frontend - Next.js PWA Application

MSA(Microservice Architecture) 구조의 프론트엔드 애플리케이션입니다.

## 🏗️ 아키텍처

### MSA 구조
- **Frontend**: Next.js + TypeScript + React
- **API Gateway**: FastAPI 기반 게이트웨이 (포트 8080)
- **Microservices**: 인증, 사용자 관리, Cal-boundary 등 개별 서비스

### API 통신 구조
```
Frontend → API Gateway (8080) → Microservices
```

## 🚀 주요 기능

### 1. 인증 시스템
- **회원가입**: 사용자명, 이메일, 비밀번호, 전체 이름
- **로그인**: 이메일/비밀번호 기반 인증
- **프로필 관리**: 사용자 정보 수정, 비밀번호 변경
- **상태 관리**: Zustand를 통한 전역 상태 관리

### 2. Process Flow Editor
- **React Flow 기반**: 인터랙티브 공정도 에디터
- **노드 관리**: 공정 단계 추가/삭제/편집
- **엣지 관리**: 공정 연결 관리
- **백엔드 연동**: Canvas 데이터 저장/로드
- **로컬 저장**: 브라우저 로컬 스토리지 백업

### 3. API 통신
- **중앙화된 API 클라이언트**: Axios 기반 통합 관리
- **인터셉터**: 요청/응답 로깅 및 오류 처리
- **타입 안전성**: TypeScript 인터페이스
- **에러 처리**: 통일된 에러 처리 로직

### 4. PWA (Progressive Web App)
- 오프라인 지원
- 설치 가능
- 푸시 알림 (향후 구현)

## 🛠️ 기술 스택

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **UI Library**: React 18
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS
- **PWA**: next-pwa
- **Flow Editor**: @xyflow/react
- **Package Manager**: pnpm

## 📁 프로젝트 구조 (리팩토링 완료)

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router
│   │   ├── login/             # 로그인 페이지
│   │   ├── register/          # 회원가입 페이지
│   │   ├── profile/           # 프로필 관리 페이지
│   │   ├── process-flow/      # Process Flow 에디터 페이지
│   │   ├── globals.css        # 전역 스타일 (다크 테마)
│   │   └── layout.tsx         # 루트 레이아웃
│   ├── api/                   # API 클라이언트 (중앙화)
│   │   ├── apiClient.ts       # Axios 인스턴스 + apiMethods
│   │   └── index.ts           # API 관련 export
│   ├── hooks/                 # 커스텀 훅들 (로직 분리)
│   │   ├── useAuthAPI.ts      # 인증 API 로직
│   │   ├── useProcessFlowAPI.ts # Process Flow API 로직
│   │   ├── useAsyncOperation.ts # 상태 관리 (로딩/에러/성공)
│   │   ├── useNavigation.ts   # 라우팅 로직
│   │   ├── useProcessFlow.ts  # Process Flow 상태 관리
│   │   ├── useNodeManagement.ts # 노드/엣지 관리
│   │   ├── useProcessTypeModal.ts # 모달 관리
│   │   └── index.ts           # 훅 export
│   ├── utils/                 # 유틸리티 함수들
│   │   ├── transformers.ts    # 데이터 변환 (Canvas ↔ Flow)
│   │   └── index.ts           # 유틸리티 export
│   ├── components/             # 아토믹 디자인 패턴 컴포넌트
│   │   ├── atoms/             # 기본 UI 컴포넌트
│   │   │   ├── Button.tsx     # 버튼 컴포넌트
│   │   │   ├── Input.tsx      # 입력 필드
│   │   │   ├── Icon.tsx       # 아이콘
│   │   │   ├── Badge.tsx      # 배지
│   │   │   ├── Tooltip.tsx    # 툴팁
│   │   │   ├── ProcessHandle.tsx # Process 핸들
│   │   │   ├── ProcessTypeBadge.tsx # Process 타입 배지
│   │   │   └── ProcessStatusIndicator.tsx # Process 상태 표시
│   │   ├── molecules/         # 복합 UI 컴포넌트
│   │   │   ├── Card.tsx       # 카드 컴포넌트
│   │   │   ├── FormField.tsx  # 폼 필드
│   │   │   ├── Modal.tsx      # 모달
│   │   │   ├── Toast.tsx      # 토스트 알림
│   │   │   ├── ProcessTypeModal.tsx # Process 타입 선택 모달
│   │   │   ├── ProcessNodeContent.tsx # Process 노드 내용
│   │   │   ├── ProcessNodeToolbar.tsx # Process 노드 툴바
│   │   │   ├── ProcessEdgeLabel.tsx # Process 엣지 라벨
│   │   │   ├── ProcessShape.tsx # Process 도형
│   │   │   ├── FlowArrow.tsx  # Flow 화살표
│   │   │   ├── ControlPanel.tsx # 제어 패널
│   │   │   ├── HeroSection.tsx # 히어로 섹션
│   │   │   ├── FeatureCard.tsx # 기능 카드
│   │   │   └── FeaturesSection.tsx # 기능 섹션
│   │   ├── organisms/         # 복합 기능 컴포넌트
│   │   │   ├── Navigation.tsx # 네비게이션 바
│   │   │   ├── AuthForm.tsx   # 인증 폼
│   │   │   ├── ProfileForm.tsx # 프로필 폼
│   │   │   ├── ProcessNode.tsx # Process 노드
│   │   │   ├── ProcessEdge.tsx # Process 엣지
│   │   │   ├── ProcessFlowControls.tsx # Process Flow 제어
│   │   │   ├── ProcessFlowInfoPanel.tsx # Process Flow 정보 패널
│   │   │   ├── ProcessFlowHeader.tsx # Process Flow 헤더
│   │   │   ├── ProcessFlowMain.tsx # Process Flow 메인
│   │   │   └── CanvasViewer.tsx # Canvas 뷰어
│   │   ├── templates/         # 페이지 레이아웃
│   │   │   ├── MainLayout.tsx # 메인 레이아웃
│   │   │   └── ProcessFlowEditor.tsx # Process Flow 에디터
│   │   └── index.ts           # 컴포넌트 export
│   ├── zustand/               # Zustand 상태 관리
│   │   ├── authStore.ts       # 인증 상태 관리
│   │   └── index.ts           # 스토어 export
│   └── README.md              # 프로젝트 문서
├── public/                    # 정적 파일 (PWA 매니페스트, 아이콘)
└── package.json               # 의존성 관리
```

## 🎯 리팩토링 결과

### ✅ 적용된 설계 원칙

#### 1. **단일 책임 원칙 (Single Responsibility Principle)**
- 각 컴포넌트와 훅이 하나의 책임만 가짐
- API 로직, 상태 관리, UI 렌더링이 명확히 분리됨

#### 2. **아토믹 디자인 패턴 (Atomic Design Pattern)**
- `atoms` → `molecules` → `organisms` → `templates` 순서로 의존성 체계
- 재사용 가능한 컴포넌트 계층 구조

#### 3. **관심사 분리 (Separation of Concerns)**
- **API 계층**: `api/` 폴더에서 중앙화된 HTTP 클라이언트 관리
- **비즈니스 로직**: `hooks/` 폴더에서 커스텀 훅으로 분리
- **UI 컴포넌트**: `components/` 폴더에서 아토믹 디자인 패턴 적용
- **유틸리티**: `utils/` 폴더에서 데이터 변환 및 헬퍼 함수 관리

### 🔧 주요 개선사항

#### 1. **API 클라이언트 중앙화**
```typescript
// 기존: 각 컴포넌트에서 개별적으로 axios 사용
// 개선: apiMethods를 통한 통일된 API 호출
import { apiMethods } from '@/api/apiClient';
await apiMethods.post('/api/v1/auth/login', data);
```

#### 2. **커스텀 훅을 통한 로직 분리**
```typescript
// 기존: 페이지 컴포넌트에 모든 로직 집중
// 개선: useAuthAPI, useProcessFlow 등으로 분리
const { login } = useAuthAPI();
const { nodes, edges, handleFlowChange } = useProcessFlow();
```

#### 3. **타입 안정성 향상**
```typescript
// 기존: any 타입 사용
// 개선: 명확한 인터페이스 정의
interface ProcessNodeData {
  label: string;
  description: string;
  processType: string;
  parameters: Record<string, any>;
}
```

#### 4. **에러 처리 통일**
```typescript
// 기존: 각 컴포넌트마다 다른 에러 처리
// 개선: useAsyncOperation을 통한 통일된 상태 관리
const { isLoading, error, success, executeAsync } = useAsyncOperation();
```

### 🧹 코드 정리 결과

#### 1. **사용되지 않는 코드 제거**
- `getAPIBaseURL`, `getAuthEndpoint` 등 사용되지 않는 유틸리티 함수
- `validateFlowData`, `normalizeFlowData` 등 사용되지 않는 검증 함수
- 개발용 `console.log` 제거

#### 2. **중복 로직 제거**
- API 에러 처리 로직 통일
- 유효성 검사 로직 단순화
- 불필요한 import 정리

## 🔧 개발 환경 설정

### 1. 의존성 설치
```bash
pnpm install
```

### 2. 개발 서버 실행
```bash
pnpm run dev
```

### 3. 빌드
```bash
pnpm run build
pnpm start
```

## 🌐 API Gateway 연동

### 환경 변수
```bash
# .env.local
NEXT_PUBLIC_API_BASE_URL=https://gateway-production-22ef.up.railway.app
```

### API 엔드포인트
- **인증**: `POST /api/v1/auth/login`, `POST /api/v1/auth/register`
- **프로필**: `PUT /api/v1/auth/profile`, `PUT /api/v1/auth/password`
- **Process Flow**: `POST /api/v1/cal-boundary/canvas`
- **헬스체크**: `GET /api/v1/gateway/services/health`

## 📱 PWA 기능

### 매니페스트
- `public/manifest.json`에서 PWA 설정
- 아이콘, 테마 색상, 표시 모드 등

### 서비스 워커
- `public/sw.js`에서 오프라인 캐싱
- 백그라운드 동기화 (향후 구현)

## 🔍 개발 도구

### TypeScript
```bash
pnpm run type-check
```

### ESLint
```bash
pnpm run lint
```

## 🚀 배포

### Vercel
- GitHub main 브랜치에 푸시하면 자동 배포
- 환경 변수는 Vercel 대시보드에서 설정

### Docker
```bash
docker build -t frontend .
docker run -p 3000:3000 frontend
```

## 🔗 연관 서비스

- **API Gateway**: `https://gateway-production-22ef.up.railway.app`
- **Auth Service**: `https://auth-service-production-d30b.up.railway.app`
- **Cal-boundary Service**: `https://lcafinal-production.up.railway.app`

## 📚 참고 문서

- [Next.js Documentation](https://nextjs.org/docs)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [PWA Documentation](https://web.dev/progressive-web-apps/)
- [React Flow Documentation](https://reactflow.dev/)
- [Atomic Design Methodology](https://bradfrost.com/blog/post/atomic-web-design/)

## 🎉 리팩토링 완료!

이제 코드가 더욱 깔끔하고 유지보수하기 쉬운 구조가 되었습니다. 각 컴포넌트와 훅이 명확한 책임을 가지고 있으며, 재사용 가능하고 테스트하기 쉬운 구조입니다.
