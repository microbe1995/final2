# Next.js 애플리케이션을 위한 Dockerfile (pnpm 사용)
FROM node:18-alpine

# pnpm 설치
RUN npm install -g pnpm

# 작업 디렉토리 설정
WORKDIR /app

# package.json과 pnpm-lock.yaml 복사
COPY package.json pnpm-lock.yaml* ./

# 의존성 설치
RUN pnpm install --frozen-lockfile

# 소스 코드 복사 (node_modules 제외)
COPY src/ ./src/
COPY public/ ./public/
COPY next.config.js ./
COPY tailwind.config.js ./
COPY postcss.config.js ./
COPY tsconfig.json ./

# Next.js 애플리케이션 빌드
RUN pnpm build

# 포트 노출
EXPOSE 3000

# 애플리케이션 실행
CMD ["pnpm", "start"]
