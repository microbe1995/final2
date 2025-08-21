# 🗺️ 카카오 지도 API 설정 가이드

## 📋 **개요**

GreenSteel 프로젝트에서 주소 검색 기능을 위해 카카오 지도 API를 사용합니다.

## 🚨 **중요: 즉시 해결해야 할 문제**

## **CORS 정책 오류 해결 방법**

### **문제 현상**

```
Access to script at 'https://dapi.kakao.com/v2/maps/sdk.js?appkey=...'
from origin 'https://greensteel.site' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

### **🚨 중요: 두 가지 도메인 모두 등록 필요**

#### **현재 발생하는 문제**

1. **Vercel 임시 도메인**: `https://greensteel-epxl12-*.vercel.app`
2. **사용자 커스텀 도메인**: `https://greensteel.site`

**두 도메인 모두 카카오 개발자 콘솔에 등록해야 CORS 오류가 해결됩니다!**

### **즉시 해결 방법**

#### **1단계: 카카오 개발자 콘솔 도메인 설정**

1. **카카오 개발자 콘솔 접속**
   - https://developers.kakao.com/ 접속
   - 로그인 후 해당 앱 선택

2. **플랫폼 설정 수정**
   - **플랫폼** → **Web** 선택
   - **사이트 도메인**에 다음 **모두** 추가:
     ```
     https://greensteel.site
     https://www.greensteel.site
     https://greensteel-epxl12-ppbavw4k2-smh1692-hsackrs-projects.vercel.app
     https://greensteel-epxl12-*.vercel.app
     ```

3. **JavaScript 키 확인**
   - 현재 사용 중인 JavaScript 키가 올바른지 확인

#### **2단계: Vercel 환경 변수 확인**

1. **Vercel 대시보드 접속**
2. **프로젝트 선택** → **Settings** → **Environment Variables**
3. **다음 환경 변수 확인/수정**:
   ```
   NEXT_PUBLIC_KAKAO_MAP_API_KEY=09570ff67d655dd1a9481f261a91e4b9
   NEXT_PUBLIC_GATEWAY_URL=https://api.greensteel.site
   ```

#### **3단계: 재배포 및 테스트**

1. **Vercel 재배포 실행**
2. **브라우저 캐시 삭제**
3. **새로고침 후 테스트**

### **🔍 도메인 차이점 설명**

#### **Vercel 임시 도메인**

- **형식**: `https://greensteel-epxl12-[random]-smh1692-hsackrs-projects.vercel.app`
- **용도**: 개발 및 테스트 중 사용
- **특징**: 자동 생성되며 변경될 수 있음

#### **사용자 커스텀 도메인**

- **형식**: `https://greensteel.site`
- **용도**: 프로덕션 환경에서 사용
- **특징**: 사용자가 직접 설정한 고정 도메인

**두 도메인 모두 카카오 API를 사용하므로, 카카오 개발자 콘솔에 모두 등록해야 합니다.**

---

현재 카카오 지도 API 스크립트 로드 실패가 발생하고 있습니다. 이는 API 키가 설정되지 않았기 때문입니다.

### **빠른 해결 방법**

1. **환경 변수 파일 생성**: `frontend/.env.local`
2. **API 키 설정**: `NEXT_PUBLIC_KAKAO_MAP_API_KEY=your_key_here`
3. **개발 서버 재시작**: `npm run dev`

### **🚨 CORS 오류가 지속 발생하는 경우**

#### **문제 현상**

카카오 개발자 콘솔에 도메인을 등록했음에도 CORS 오류가 계속 발생하는 경우

#### **즉시 해결 방법**

##### **1단계: 카카오 개발자 콘솔 재확인**

1. **JavaScript 키 유효성 확인**
   - 현재 사용 중인 JavaScript 키가 만료되지 않았는지 확인
   - 키가 올바르게 복사되었는지 확인

2. **도메인 등록 정확성 확인**
   - `https://greensteel.site` (http://가 아닌 https://)
   - `https://www.greensteel.site`
   - 정확한 도메인명과 프로토콜 확인

3. **앱 상태 확인**
   - 앱이 활성화 상태인지 확인
   - 앱이 일시정지되지 않았는지 확인

##### **2단계: Vercel 환경 변수 재확인**

1. **환경 변수 값 확인**

   ```
   NEXT_PUBLIC_KAKAO_MAP_API_KEY=09570ff67d655dd1a9481f261a91e4b9
   ```

2. **환경 변수 수정 후 재배포**
   - 환경 변수 수정
   - Vercel 재배포 실행
   - 배포 완료 후 5-10분 대기

##### **3단계: 브라우저 캐시 완전 삭제**

1. **Ctrl+Shift+Delete** (Windows) 또는 **Cmd+Shift+Delete** (Mac)
2. **모든 데이터 삭제** 선택
3. **새로고침** 후 재시도

##### **4단계: 도메인 등록 후 대기**

- 카카오 서버에 설정 반영까지 **5-10분** 소요
- 즉시 반영되지 않을 수 있음

##### **5단계: 최후의 수단**

1. **카카오 개발자 콘솔에서 앱 삭제**
2. **새로운 앱 생성**
3. **새로운 JavaScript 키 발급**
4. **모든 도메인 재등록**

#### **문제 진단 체크리스트**

- [ ] 카카오 개발자 콘솔에 정확한 도메인 등록
- [ ] JavaScript 키 유효성 확인
- [ ] Vercel 환경 변수 설정 확인
- [ ] Vercel 재배포 완료
- [ ] 브라우저 캐시 삭제
- [ ] 5-10분 대기 후 재시도

---

## 🔑 **1. 카카오 개발자 계정 생성**

### **1.1 카카오 개발자 사이트 접속**

- [Kakao Developers](https://developers.kakao.com/) 접속
- 카카오 계정으로 로그인

### **1.2 애플리케이션 생성**

1. **내 애플리케이션** → **애플리케이션 추가하기** 클릭
2. **앱 이름**: `GreenSteel` (또는 원하는 이름)
3. **회사명**: 회사명 입력
4. **생성** 버튼 클릭

## ⚙️ **2. 플랫폼 설정**

### **2.1 웹 플랫폼 추가**

1. **플랫폼** → **Web** → **사이트 도메인** 추가
2. **도메인 설정**:
   - **개발 환경**: `http://localhost:3000`
   - **프로덕션 환경**: `https://your-domain.vercel.app`
   - **Vercel 도메인**: `https://greensteel-epxl12-332diit70-smh1692-hsackrs-projects.vercel.app`

### **2.2 JavaScript 키 확인**

- **앱 키** → **JavaScript 키** 복사
- 이 키를 환경 변수에 설정해야 합니다

## 🔧 **3. 환경 변수 설정 (즉시 필요!)**

### **3.1 로컬 개발 환경 (권장)**

```bash
# frontend 폴더에서 .env.local 파일 생성
cd frontend
echo "NEXT_PUBLIC_KAKAO_MAP_API_KEY=your_javascript_key_here" > .env.local
```

### **3.2 Vercel 프로덕션 환경**

1. Vercel 대시보드 → 프로젝트 선택
2. **Settings** → **Environment Variables**
3. **Add New** 클릭:
   - **Name**: `NEXT_PUBLIC_KAKAO_MAP_API_KEY`
   - **Value**: 카카오 JavaScript 키
   - **Environment**: Production, Preview, Development 모두 선택

### **3.3 환경 변수 확인**

```bash
# frontend/.env.local 파일 내용 확인
cat .env.local

# 예상 출력:
# NEXT_PUBLIC_KAKAO_MAP_API_KEY=1234567890abcdef1234567890abcdef
```

## 🧪 **4. 즉시 테스트 방법**

### **4.1 로컬 테스트 (권장)**

```bash
cd frontend
npm run dev
```

- `http://localhost:3000/register` 접속
- 기업 회원가입 → 주소 검색 버튼 클릭
- 지도가 정상적으로 로드되는지 확인

### **4.2 API 키 테스트**

브라우저 콘솔에서 다음 명령어 실행:

```javascript
console.log('Kakao API Key:', process.env.NEXT_PUBLIC_KAKAO_MAP_API_KEY);
```

**예상 출력**: `Kakao API Key: 1234567890abcdef1234567890abcdef`
**오류 출력**: `Kakao API Key: undefined` (API 키가 설정되지 않음)

## 🚀 **5. API 키 보안 설정**

### **5.1 도메인 제한**

- **카카오 개발자 콘솔** → **보안** → **도메인**
- 허용할 도메인만 등록:
  - `localhost:3000`
  - `your-domain.vercel.app`
  - `greensteel-epxl12-332diit70-smh1692-hsackrs-projects.vercel.app`

### **5.2 사용량 제한**

- **보안** → **사용량 제한**
- **일일 사용량**: 적절한 제한 설정 (예: 10,000회)
- **초당 요청 수**: 적절한 제한 설정 (예: 10회)

## ❌ **6. 문제 해결**

### **6.1 CSP 오류 (해결됨)**

```
Refused to load the script 'https://dapi.kakao.com/v2/maps/sdk.js' because it violates the following Content Security Policy directive
```

**해결 방법**: `next.config.js`의 CSP 설정에 `https://dapi.kakao.com` 추가 완료 ✅

### **6.2 API 키 오류 (현재 문제)**

```
카카오 지도 API 스크립트 로드 실패
```

**해결 방법**:

1. ✅ **환경 변수 확인**: `frontend/.env.local` 파일 생성
2. ✅ **API 키 설정**: `NEXT_PUBLIC_KAKAO_MAP_API_KEY=your_key_here`
3. ✅ **개발 서버 재시작**: `npm run dev`
4. ✅ **도메인 설정 확인**: 카카오 개발자 콘솔에서 도메인 등록

### **6.3 Manifest 401 오류 (해결됨)**

```
Manifest fetch failed, code 401
```

**해결 방법**: `vercel.json`의 헤더 설정 완료 ✅

### **6.4 지도 로딩 실패**

```
지도 로딩에 실패했습니다
```

**해결 방법**:

1. 네트워크 연결 확인
2. 카카오 서비스 상태 확인
3. 브라우저 콘솔 에러 확인
4. API 키 유효성 확인

## 🔍 **7. 디버깅 방법**

### **7.1 환경 변수 확인**

```bash
# frontend 폴더에서
node -e "console.log('API Key:', process.env.NEXT_PUBLIC_KAKAO_MAP_API_KEY)"
```

### **7.2 브라우저 콘솔 확인**

```javascript
// 브라우저 콘솔에서 실행
console.log('Environment:', process.env.NODE_ENV);
console.log('API Key:', process.env.NEXT_PUBLIC_KAKAO_MAP_API_KEY);
console.log('Kakao Object:', window.kakao);
```

### **7.3 네트워크 탭 확인**

- 브라우저 개발자 도구 → Network 탭
- `dapi.kakao.com` 요청 상태 확인
- 401, 403, 404 오류 확인

## 📚 **8. 추가 리소스**

### **8.1 카카오 지도 API 문서**

- [Kakao Maps JavaScript API](https://apis.map.kakao.com/web/)
- [주소-좌표 변환 서비스](https://apis.map.kakao.com/web/sample/coord2addr/)
- [장소 검색 서비스](https://apis.map.kakao.com/web/sample/search/)

### **8.2 샘플 코드**

- [카카오 지도 API 샘플](https://apis.map.kakao.com/web/sample/)
- [주소 검색 구현 예제](https://apis.map.kakao.com/web/sample/addr2coord/)

## 🔒 **9. 보안 고려사항**

### **9.1 API 키 노출 방지**

- `NEXT_PUBLIC_` 접두사는 클라이언트에서 접근 가능
- 서버 사이드에서만 사용하는 API 키는 `NEXT_PUBLIC_` 제거

### **9.2 사용량 모니터링**

- 카카오 개발자 콘솔에서 API 사용량 모니터링
- 비정상적인 사용량 증가 시 즉시 확인

### **9.3 에러 처리**

- API 호출 실패 시 적절한 에러 메시지 표시
- 사용자에게 친화적인 에러 안내

---

## ✅ **설정 완료 체크리스트**

- [ ] 카카오 개발자 계정 생성
- [ ] 애플리케이션 생성
- [ ] 웹 플랫폼 추가
- [ ] JavaScript 키 복사
- [ ] **환경 변수 설정** ← **현재 필요!**
- [ ] 도메인 제한 설정
- [ ] 사용량 제한 설정
- [ ] 로컬 테스트 완료
- [ ] 프로덕션 테스트 완료

## 🚨 **즉시 해결해야 할 문제**

**현재 상태**: 카카오 지도 API 스크립트 로드 실패
**원인**: `NEXT_PUBLIC_KAKAO_MAP_API_KEY` 환경 변수 미설정
**해결 방법**: `frontend/.env.local` 파일에 API 키 설정

```bash
# frontend 폴더에서 실행
echo "NEXT_PUBLIC_KAKAO_MAP_API_KEY=your_actual_javascript_key_here" > .env.local
npm run dev
```

**모든 항목을 완료하면 카카오 지도 API가 정상적으로 작동합니다!** 🎉

### **🚨 CSP (Content Security Policy) 오류 해결 방법**

#### **문제 현상**

```
The source list for the Content Security Policy directive 'script-src' contains an invalid source: ''unsafe-dynamic''. It will be ignored.

Refused to load the script 'https://t1.daumcdn.net/mapjsapi/js/main/4.4.19/kakao.js'
because it violates the following Content Security Policy directive:
"script-src 'self' 'unsafe-eval' 'unsafe-inline' https://www.googletagmanager.com
https://www.google-analytics.com https://dapi.kakao.com https://greensteel.site 'unsafe-dynamic'"
```

#### **문제 원인**

1. **`'unsafe-dynamic'`**: 폐기된 CSP 옵션으로 브라우저에서 무시됨
2. **`t1.daumcdn.net` 누락**: 카카오 지도 SDK가 실제로 사용하는 CDN 도메인이 CSP에 허용되지 않음
3. **카카오 SDK 로드 경로**: `dapi.kakao.com` → 내부적으로 `t1.daumcdn.net`을 통해 로드

#### **즉시 해결 방법**

##### **1단계: CSP 헤더 수정**

`next.config.js`에서 다음 CSP 설정을 사용:

```javascript
Content-Security-Policy: script-src 'self' 'unsafe-inline' 'unsafe-eval'
https://www.googletagmanager.com https://www.google-analytics.com
https://dapi.kakao.com https://t1.daumcdn.net https://greensteel.site;
```

##### **2단계: 필요한 도메인 확인**

카카오 지도 API 사용을 위해 다음 도메인들이 CSP에 포함되어야 함:

- `https://dapi.kakao.com` (API 엔드포인트)
- `https://t1.daumcdn.net` (SDK CDN)
- `https://greensteel.site` (사용자 도메인)

##### **3단계: 보안 강화 (선택사항)**

가능하다면 다음 옵션들을 점진적으로 제거하는 것을 권장:

- `'unsafe-inline'` → `nonce` 또는 `sha256-...` 해시 기반 정책
- `'unsafe-eval'` → 동적 코드 실행 제한

#### **CSP 설정 예시**

```javascript
// next.config.js
{
  key: 'Content-Security-Policy',
  value: `default-src 'self'; script-src 'self' 'unsafe-eval' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com https://dapi.kakao.com https://t1.daumcdn.net https://greensteel.site; style-src 'self' 'unsafe-inline'; img-src 'self' data: https: https://www.google-analytics.com https://greensteel.site; connect-src 'self' ${process.env.NEXT_PUBLIC_GATEWAY_URL || 'https://api.greensteel.site'} https://www.google-analytics.com https://analytics.google.com https://dapi.kakao.com https://greensteel.site; font-src 'self' data:; frame-src 'self' https://greensteel.site;`
}
```
