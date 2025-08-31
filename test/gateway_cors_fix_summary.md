# Gateway CORS 문제 해결 요약

## 🔍 문제 분석
- `/api/v1/cbam/`, `/api/v1/boundary/` 요청이 Gateway → CAL_BOUNDARY_URL로 정상 프록시되지 않음
- 307/ERR_FAILED/CSP 경고 발생
- 서비스워커가 API fetch를 가로채는 문제

## ✅ 해결된 항목

### A. Gateway 수정 완료
- [x] SERVICE_MAP에 "boundary" 별칭 추가
- [x] hop-by-hop 헤더 필터링 강화 (connection, keep-alive, proxy-authenticate, proxy-authorization, te, trailers, transfer-encoding, upgrade, host, content-length)
- [x] CORS 설정에 Gateway 본인 도메인 포함
- [x] OPTIONS 요청 처리 제거 (CORSMiddleware가 처리)

### B. Frontend axiosClient.ts 수정 완료
- [x] baseURL 환경변수 검증 강화
- [x] withCredentials 제거 (쿠키 미사용)
- [x] 개발 모드 로그 유지

### C. next.config.js 수정 완료
- [x] CSP connect-src에 Gateway/Railway 도메인 포함 확인
- [x] http 목적지 제거 확인

### D. PWA 서비스워커 완전 비활성화 완료
- [x] PWAServiceWorker.tsx 완전 비활성화
- [x] PWAInstallBanner.tsx 완전 비활성화
- [x] 개발/디버그 동안 SW 해제 안내 추가

## 🔧 환경변수 확인
```
# Vercel
NEXT_PUBLIC_API_BASE_URL=https://gateway-production-22ef.up.railway.app
NEXT_PUBLIC_CAL_BOUNDARY_URL=https://lcafinal-production.up.railway.app

# Railway (Gateway)
CAL_BOUNDARY_URL=https://lcafinal-production.up.railway.app
CORS_URL=https://lca-final.vercel.app,https://gateway-production-22ef.up.railway.app
```

## 🧪 테스트 방법

### 1. 수동 테스트
```bash
# 브라우저에서
1. 브라우저 캐시 삭제
2. DevTools → Application → Service Workers → Unregister
3. Storage → Clear site data
4. 새로고침
```

### 2. 자동 테스트
```bash
# Python 스크립트 실행
cd test
python test_gateway_proxy.py
```

### 3. 예상 결과
- 요청: `https://gateway-production-22ef.up.railway.app/api/v1/cbam/install`
- 응답: 200/404/401 등 정상 코드 (307 반복/ERR_FAILED 없어야 함)
- Gateway 로그: `[PROXY] GET /api/v1/cbam/install -> https://lcafinal-production.up.railway.app/install`

## 🚀 배포 후 확인사항

### Gateway 로그 확인
```
✅ [PROXY] GET /api/v1/cbam/install -> https://lcafinal-production.up.railway.app/install
✅ 프록시 응답: GET https://lcafinal-production.up.railway.app/install -> 200
❌ Unknown service 로그가 더 이상 없어야 함
```

### 브라우저 Network 탭 확인
```
요청: https://gateway-production-22ef.up.railway.app/api/v1/cbam/install
응답: 200/404/401 등 정상 코드
CSP 경고 없음
```

## 🔄 다음 단계
1. Gateway 재배포
2. 프론트엔드 재배포
3. 테스트 실행
4. 문제 해결 확인 후 PWA 재활성화

## 📝 참고사항
- 모든 API 요청은 Gateway를 통해야 함 (MSA 원칙)
- CORS는 Gateway에서만 설정
- PWA는 CORS 문제 해결 후 재활성화
- 환경변수는 https 스킴만 사용
