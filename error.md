[작업 지시문 — Cursor에 그대로 전달]
목표

/api/v1/cbam/, /api/v1/boundary/ 요청이 Gateway → CAL_BOUNDARY_URL로 정상 프록시

307/ERR_FAILED/CSP 경고 제거

서비스워커가 API fetch를 가로채지 않도록 예외 처리

A. gateway/app/main.py 수정

SERVICE_MAP에 별칭 추가
"boundary": CAL_BOUNDARY_URL
"cbam": CAL_BOUNDARY_URL

빈 경로와 슬래시 보정
path가 빈 문자열이면 target_url이 …/ 로 끝나도록 보정
service == "install" and path == "" 인 경우 normalized_path = "install/"

hop-by-hop 헤더 필터 추가
필터 집합: connection, keep-alive, proxy-authenticate, proxy-authorization, te, trailers, transfer-encoding, upgrade, host, content-length
요청/응답 모두 적용

httpx.AsyncClient 전역 싱글톤으로 lifespan에서 생성/종료

라우트의 OPTIONS 직접 처리 제거(이미 CORSMiddleware가 처리)

CORS allow_origins에 프론트와 게이트웨이 본인 도메인 포함
https://lca-final.vercel.app

https://gateway-production-22ef.up.railway.app

검증 로그 기대치
[PROXY] GET /api/v1/cbam/install -> https://lcafinal-production.up.railway.app/install/
 또는 /install
업스트림 200/4xx가 곧바로 반환되고 307이 반복되지 않을 것

B. frontend/axiosclient.ts 수정

baseURL이 반드시 https://gateway-production-22ef.up.railway.app
 인지 확인(하드코딩이면 그대로, 환경변수면 NEXT_PUBLIC_API_BASE_URL이 https인지 확인)

엔드포인트 경로 선택지
단기: 현재처럼 /api/v1/cbam/... 유지 가능(위 SERVICE_MAP 별칭 덕분에 동작)
장기(권장): /api/v1/install, /api/v1/product 등 실제 리소스명 기반으로 통일하여 cbam/boundary 접두사 제거

개발 모드 로그 유지, withCredentials 불필요(쿠키 미사용이면)

C. next.config.js 수정

CSP의 connect-src에 다음이 반드시 포함되어야 함(https만)
https://gateway-production-22ef.up.railway.app

https://lcafinal-production.up.railway.app

사용 중인 vercel/analytics/kakao 등 기존 항목 유지

http 목적지 제거

만약 _document.tsx에 meta http-equiv="Content-Security-Policy"가 있다면 제거(헤더 방식만 유지)

D. PWA 서비스워커(workbox) 수정 또는 임시 비활성화

개발/디버그 동안 SW 완전 해제
Application 탭에서 Unregister 후 Clear site data

SW를 유지한다면 /api/와 /health는 NetworkOnly로 예외 등록
workbox.routing.registerRoute(
({url}) => url.pathname.startsWith('/api/') || url.pathname.startsWith('/health'),
new workbox.strategies.NetworkOnly()
)

E. 환경변수 최종 점검
Vercel
NEXT_PUBLIC_API_BASE_URL=https://gateway-production-22ef.up.railway.app

NEXT_PUBLIC_CAL_BOUNDARY_URL=https://lcafinal-production.up.railway.app

Railway(Gateway)
CAL_BOUNDARY_URL=https://lcafinal-production.up.railway.app

CORS_URL에 https://lca-final.vercel.app
, https://gateway-production-22ef.up.railway.app
 포함
모두 https 스킴만 사용

F. 수동 테스트 시나리오

브라우저 캐시 삭제 및 SW Unregister 후 새로고침

Network 탭에서
요청: https://gateway-production-22ef.up.railway.app/api/v1/cbam/install

응답: 200/404/401 등 정상 코드(307 반복/ERR_FAILED 없어야 함)

Gateway 로그
[PROXY] … -> https://lcafinal-production.up.railway.app/install
 또는 /install/
Unknown service 로그가 더 이상 없어야 함

문서(HTML) 응답 헤더의 Content-Security-Policy에 connect-src로 gateway/railway 도메인이 존재하는지 확인