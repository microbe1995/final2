# LCA_final - PWA Next.js 애플리케이션

React, Zustand, Axios, TypeScript로 구축된 Progressive Web App (PWA)입니다.

## 🚀 주요 기능

- **PWA 지원**: 오프라인 지원, 홈 화면 설치, 네이티브 앱과 같은 경험
- **JWT 인증**: 안전한 토큰 기반 사용자 인증
- **반응형 디자인**: 모든 디바이스에서 최적화된 사용자 경험
- **TypeScript**: 타입 안전성과 개발자 경험 향상
- **Zustand**: 가벼운 상태 관리
- **Tailwind CSS**: 유틸리티 기반 CSS 프레임워크

## 📋 기술 스택

- **Frontend**: Next.js 14, React 18, TypeScript
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS
- **PWA**: next-pwa
- **Authentication**: JWT
- **Deployment**: Vercel
- **CI/CD**: GitHub Actions

## 🛠️ 설치 및 실행

### 필수 요구사항

- Node.js 18.x 이상
- npm 또는 yarn

### 로컬 개발 환경 설정

1. **저장소 클론**
   ```bash
   git clone https://github.com/Microbe95/LCA_final.git
   cd LCA_final
   ```

2. **의존성 설치**
   ```bash
   npm install
   ```

3. **환경 변수 설정**
   ```bash
   cp .env.example .env.local
   ```
   
   `.env.local` 파일을 편집하여 필요한 환경 변수를 설정하세요:
   ```env
   JWT_SECRET=your-super-secret-jwt-key-here
   NEXT_PUBLIC_API_URL=http://localhost:3000/api
   ```

4. **개발 서버 실행**
   ```bash
   npm run dev
   ```

5. **브라우저에서 확인**
   ```
   http://localhost:3000
   ```

## 📁 프로젝트 구조

```
├── src/
│   ├── app/                 # Next.js App Router
│   │   ├── dashboard/       # 대시보드 페이지
│   │   ├── login/          # 로그인 페이지
│   │   ├── register/       # 회원가입 페이지
│   │   ├── globals.css     # 글로벌 스타일
│   │   ├── layout.tsx      # 루트 레이아웃
│   │   └── page.tsx        # 홈페이지
│   ├── components/         # 재사용 가능한 컴포넌트
│   ├── lib/               # 유틸리티 함수
│   │   ├── api.ts         # API 클라이언트
│   │   └── auth.ts        # 인증 유틸리티
│   ├── store/             # Zustand 스토어
│   │   └── authStore.ts   # 인증 상태 관리
│   └── types/             # TypeScript 타입 정의
│       └── index.ts
├── public/                # 정적 파일
│   ├── manifest.json      # PWA 매니페스트
│   └── icons/            # PWA 아이콘
├── .github/              # GitHub Actions
│   └── workflows/
├── package.json
├── next.config.js
├── tailwind.config.js
├── tsconfig.json
└── vercel.json
```

## 🔧 사용 가능한 스크립트

```bash
# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 서버 실행
npm run start

# 린팅 실행
npm run lint

# 타입 체크
npm run type-check
```

## 🚀 배포

### Vercel 배포

1. **Vercel CLI 설치**
   ```bash
   npm i -g vercel
   ```

2. **Vercel 로그인**
   ```bash
   vercel login
   ```

3. **프로젝트 배포**
   ```bash
   vercel
   ```

### 환경 변수 설정

Vercel 대시보드에서 다음 환경 변수를 설정하세요:

- `JWT_SECRET`: JWT 서명에 사용할 비밀키
- `NEXT_PUBLIC_API_URL`: API 서버 URL

## 🔄 CI/CD

GitHub Actions를 통한 자동화된 CI/CD 파이프라인이 구성되어 있습니다:

- **develop 브랜치**: 스테이징 환경에 자동 배포
- **main 브랜치**: 프로덕션 환경에 자동 배포

### GitHub Secrets 설정

다음 시크릿을 GitHub 저장소에 설정하세요:

- `JWT_SECRET`: JWT 서명 키
- `NEXT_PUBLIC_API_URL`: API URL
- `VERCEL_TOKEN`: Vercel API 토큰
- `VERCEL_ORG_ID`: Vercel 조직 ID
- `VERCEL_PROJECT_ID`: Vercel 프로젝트 ID

## 📱 PWA 기능

### 설치 방법

1. 브라우저에서 앱에 접속
2. 주소창 옆의 설치 아이콘 클릭
3. "설치" 버튼 클릭

### 지원 브라우저

- Chrome 67+
- Firefox 67+
- Safari 11.1+
- Edge 79+

## 🔐 인증 시스템

- JWT 토큰 기반 인증
- 자동 토큰 갱신
- 보안된 라우트 보호
- 로그아웃 시 토큰 삭제

## 🎨 UI/UX

- Tailwind CSS를 사용한 모던한 디자인
- 반응형 레이아웃
- 다크 모드 지원 (준비 중)
- 접근성 고려

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 지원

문제가 있거나 질문이 있으시면 이슈를 생성해 주세요.

---

**개발자**: Microbe95  
**버전**: 1.0.0  
**최종 업데이트**: 2024년 1월
