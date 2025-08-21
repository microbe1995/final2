# GreenSteel PWA (Progressive Web App)

Amazon 스타일을 참조하여 구현된 고도화된 Progressive Web App입니다.

## 🚀 주요 기능

### 1. **오프라인 지원**

- Service Worker를 통한 캐싱 전략
- IndexedDB를 활용한 오프라인 데이터 저장
- 네트워크 상태 실시간 모니터링
- 오프라인 전용 페이지 제공

### 2. **앱 설치 배너**

- 홈 화면 추가 유도
- 스마트한 설치 프롬프트
- 설치 상태 추적 및 관리

### 3. **푸시 알림**

- 실시간 업데이트 알림
- 사용자 맞춤 알림 설정

### 4. **성능 최적화**

- 이미지 지연 로딩
- 코드 스플리팅
- 성능 메트릭 수집
- Google Analytics 연동

### 5. **캐싱 전략**

- **정적 리소스**: Cache First (이미지, CSS, JS)
- **API 요청**: Network First (데이터)
- **HTML 페이지**: Network First (콘텐츠)

## 📱 PWA 매니페스트

```json
{
  "name": "GreenSteel - ESG Management Platform",
  "short_name": "GreenSteel",
  "display": "standalone",
  "theme_color": "#3b82f6",
  "background_color": "#0f172a",
  "orientation": "portrait-primary"
}
```

## 🛠️ 설치 및 설정

### 1. **환경 변수 설정**

`.env.local` 파일을 생성하고 다음 변수들을 설정하세요:

```bash
# PWA Configuration
NEXT_PUBLIC_PWA_ENABLED=true

# Feature Flags
NEXT_PUBLIC_ENABLE_PUSH_NOTIFICATIONS=true
NEXT_PUBLIC_ENABLE_OFFLINE_SUPPORT=true
NEXT_PUBLIC_ENABLE_INSTALL_PROMPT=true

# Cache Configuration
NEXT_PUBLIC_CACHE_DURATION=86400
NEXT_PUBLIC_MAX_CACHE_ENTRIES=100
```

### 2. **의존성 설치**

```bash
pnpm install
```

## 🔧 사용법

### 1. **PWA 설치 배너**

```tsx
import PWAInstallBanner from '@/components/PWAInstallBanner';

// 자동으로 표시되며, 사용자가 앱을 설치할 수 있도록 유도
```

### 2. **오프라인 상태 표시**

```tsx
import OfflineIndicator from '@/components/OfflineIndicator';

// 네트워크 상태를 실시간으로 모니터링하고 표시
```

### 3. **푸시 알림 서비스**

```tsx
import { pushNotificationService } from '@/lib/pushNotification';

// 푸시 알림 초기화
await pushNotificationService.initialize();

// 알림 표시
await pushNotificationService.showNotification('제목', {
  body: '내용',
  icon: '/icon-192x192.png',
});
```

### 4. **오프라인 저장소**

```tsx
import { OfflineStorage } from '@/lib/pwaUtils';

const storage = new OfflineStorage();
await storage.init();

// 오프라인 작업 저장
const taskId = await storage.saveOfflineTask('data_upload', {
  file: 'data.csv',
  timestamp: Date.now(),
});

// 캐시된 데이터 저장
await storage.cacheData('user_profile', userData, 24);
```

### 5. **성능 메트릭**

```tsx
import { PerformanceMetrics } from '@/lib/pwaUtils';

// 페이지 로드 성능 측정
PerformanceMetrics.measurePageLoad();

// 상호작용 성능 측정
PerformanceMetrics.measureInteraction('button_click', () => {
  // 버튼 클릭 처리
});
```

## 📊 캐싱 전략

### 1. **정적 리소스 (Cache First)**

- 이미지, CSS, JavaScript 파일
- 즉시 캐시에서 로드
- 오프라인에서도 사용 가능

### 2. **API 요청 (Network First)**

- 데이터베이스 쿼리 결과
- 네트워크 우선, 실패 시 캐시 사용
- 최신 데이터 보장

### 3. **HTML 페이지 (Network First)**

- 동적 콘텐츠
- 실시간 업데이트 우선
- 오프라인 시 캐시된 버전 제공

## 🔔 푸시 알림

### 1. **알림 권한 요청**

- 사용자 상호작용 시 자동 요청
- 권한 상태 추적 및 관리

### 2. **알림 타입**

- **정보성 알림**: 업데이트, 공지사항
- **작업 알림**: 데이터 처리 완료, 오류 발생
- **리마인더**: 정기 보고서, 마감일

### 3. **알림 액션**

- 알림 클릭 시 앱 열기
- 액션 버튼으로 빠른 작업 실행

## 📱 앱 설치

### 1. **설치 조건**

- HTTPS 환경
- 유효한 매니페스트
- Service Worker 등록
- 사용자 상호작용

### 2. **설치 프로세스**

1. 설치 배너 표시
2. 사용자 선택 (설치/나중에)
3. 앱 다운로드 및 설치
4. 홈 화면에 아이콘 추가

### 3. **설치 후 기능**

- 독립 실행 모드
- 전체 화면 경험
- 네이티브 앱과 유사한 UX

## 🚨 오프라인 지원

### 1. **오프라인 감지**

- `navigator.onLine` 이벤트
- Service Worker 상태 모니터링
- 네트워크 요청 실패 감지

### 2. **오프라인 작업**

- 데이터 입력 및 저장
- 작업 큐 관리
- 네트워크 복구 시 자동 동기화

### 3. **오프라인 페이지**

- 사용자 친화적 오프라인 화면
- 사용 가능한 기능 안내
- 네트워크 상태 실시간 표시

## 📈 성능 최적화

### 1. **이미지 최적화**

- WebP, AVIF 포맷 지원
- 지연 로딩 (Intersection Observer)
- 적응형 이미지 크기

### 2. **코드 최적화**

- 동적 임포트 (Code Splitting)
- Tree Shaking
- 번들 크기 최적화

### 3. **캐싱 최적화**

- 스마트 캐시 전략
- 캐시 만료 관리
- 백그라운드 업데이트

## 🔒 보안

### 1. **HTTPS 필수**

- 모든 PWA 기능은 HTTPS에서만 작동
- 보안 헤더 설정

### 2. **권한 관리**

- 사용자 명시적 권한 요청
- 최소 권한 원칙
- 권한 상태 추적

### 3. **데이터 보호**

- 로컬 저장소 암호화
- 민감 정보 보호
- 안전한 API 통신

## 🧪 테스트

### 1. **PWA 감사**

```bash
# Lighthouse PWA 감사
npx lighthouse --only-categories=pwa

# PWA Builder 테스트
https://www.pwabuilder.com/
```

### 2. **오프라인 테스트**

- 개발자 도구 > Network 탭에서 Offline 체크
- Service Worker 상태 확인
- 캐싱 동작 검증

### 3. **설치 테스트**

- 다양한 브라우저에서 테스트
- 모바일 디바이스 테스트
- 설치 프로세스 검증

## 🚀 배포

### 1. **빌드**

```bash
pnpm build
```

### 2. **배포 전 확인사항**

- [ ] HTTPS 설정 완료
- [ ] 매니페스트 파일 유효성 검증
- [ ] Service Worker 등록 확인
- [ ] 푸시 알림 테스트
- [ ] 오프라인 기능 테스트

### 3. **모니터링**

- Google Analytics 성능 추적
- 오류 로깅 및 모니터링
- 사용자 행동 분석

## 📚 참고 자료

- [PWA 공식 문서](https://web.dev/progressive-web-apps/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://developer.mozilla.org/en-US/docs/Web/Manifest)
- [Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)

## 🤝 기여

PWA 기능 개선을 위한 제안이나 버그 리포트는 언제든 환영합니다!

---

**GreenSteel PWA** - 지속 가능한 미래를 위한 ESG 관리 플랫폼
