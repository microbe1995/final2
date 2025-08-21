# 🚀 GreenSteel Frontend

ESG 관리 플랫폼의 프론트엔드 애플리케이션입니다.

## ✨ 주요 기능

- **LCA (Life Cycle Assessment)**: 생명주기 평가
- **CBAM**: 탄소 국경 조정 메커니즘
- **데이터 업로드**: ESG 데이터 관리
- **대시보드**: 통합 모니터링
- **PWA 지원**: Progressive Web App

## 🛠️ 기술 스택

- **Framework**: Next.js 14.2.5
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Package Manager**: pnpm
- **Deployment**: Vercel
- **PWA**: next-pwa

## 🚀 빠른 시작

### 개발 환경 설정

```bash
# 의존성 설치
pnpm install

# 개발 서버 실행
pnpm run dev

# 빌드
pnpm run build

# 프로덕션 서버 실행
pnpm run start
```

### 환경 변수 설정

```bash
# .env.local 파일 생성
NEXT_PUBLIC_APP_NAME=GreenSteel
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📱 PWA 기능

- 오프라인 지원
- 홈 화면 설치
- 푸시 알림
- 백그라운드 동기화

## 🔧 개발 도구

- **Linting**: ESLint + Prettier
- **Testing**: Jest + Testing Library
- **Type Checking**: TypeScript
- **Code Quality**: Husky + lint-staged

## 📊 배포

### Vercel 자동 배포

GitHub main 브랜치에 푸시하면 자동으로 Vercel에 배포됩니다.

### 수동 배포

```bash
# Vercel CLI 설치
npm i -g vercel

# 로그인 및 배포
vercel login
vercel --prod
```

## 🐛 문제 해결

### CI/CD 문제

CI/CD가 작동하지 않는 경우:

1. **Vercel 프로젝트 재연결**
2. **GitHub Actions 워크플로우 확인**
3. **Vercel CLI를 사용한 수동 배포**

### 빌드 오류

```bash
# 의존성 재설치
rm -rf node_modules pnpm-lock.yaml
pnpm install

# 빌드 테스트
pnpm run build
```

## 📚 문서

- [배포 가이드](./DEPLOYMENT.md)
- [PWA 설정](./PWA_README.md)
- [Kakao API 설정](./KAKAO_API_SETUP.md)
- [CI/CD 문제 해결](./CI_CD_FIX.md)

## 🤝 기여

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

---

**마지막 업데이트**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**CI/CD 상태**: 🔄 트리거 중...
