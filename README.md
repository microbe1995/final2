# LCA_final

Next.js 기반 PWA (Progressive Web App) 프로젝트

## 🚀 주요 기능

- **Next.js 14** (App Router)
- **React 18** + **TypeScript**
- **Zustand** (상태 관리)
- **Axios** (HTTP 클라이언트)
- **JWT** 기반 인증
- **PWA** (Progressive Web App)
- **Tailwind CSS** (스타일링)
- **Vercel** 배포
- **GitHub Actions** CI/CD

## 📦 설치 및 실행

```bash
# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build

# 프로덕션 서버 실행
npm start
```

## 🔧 환경 변수

`.env.local` 파일을 생성하고 다음 변수들을 설정하세요:

```env
JWT_SECRET=your_jwt_secret_here
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

## 🚀 배포

이 프로젝트는 Vercel에 자동 배포됩니다:

- **Staging**: `develop` 브랜치에 푸시
- **Production**: `main` 브랜치에 푸시

## 📱 PWA 기능

- 오프라인 지원
- 홈 화면에 추가 가능
- 네이티브 앱과 유사한 경험

## 🔐 인증

JWT 기반 인증 시스템이 구현되어 있습니다:

- 사용자 등록
- 로그인/로그아웃
- 토큰 기반 인증

## 🎨 UI/UX

- 모던하고 반응형 디자인
- Tailwind CSS를 활용한 스타일링
- 사용자 친화적인 인터페이스

## 🤝 기여

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**개발자**: Microbe95  
**최종 업데이트**: 2024년 12월
