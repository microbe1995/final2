다음 사항을 코드에서 점검하고 수정해줘:

1. Axios 요청 baseURL이 반드시 https://cafinal-production.up.railway.app 로 설정되어 있는지 확인하고, http:// 로 호출하는 부분이 있으면 모두 https:// 로 바꿔줘.

2. next.config.js 안에 Content-Security-Policy 헤더 설정(connect-src)에 
   https://cafinal-production.up.railway.app 와 https://gateway-production-22ef.up.railway.app 가 포함되어 있는지 확인하고, 없다면 추가해줘.

3. FastAPI 서버에서 CORS 미들웨어 설정이 정확히 되어 있는지 확인하고,
   allow_origins에 https://lca-final.vercel.app 과 http://localhost:3000 이 들어가 있는지 검증해.
   allow_methods, allow_headers도 모두 허용("*") 되어 있는지 확인해.

4. 변경 사항 반영 후 Vercel 배포 시, "Redeploy with cache invalidation" 옵션을 사용해서 
   캐시된 헤더가 아닌 최신 CSP 헤더가 적용되도록 해줘.
