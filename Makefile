# 모든 명령어 앞에 'make' 를 붙여서 실행해야 함
# 🔧 공통 명령어
up:
	docker-compose up -d --build

down:
	docker-compose down

logs:
	docker-compose logs -f

restart:
	docker-compose down && docker-compose up -d --build

ps:
	docker-compose ps

# 🚀 마이크로서비스별 명령어

## gateway
build-gateway:
	docker-compose build gateway

up-gateway:
	docker-compose up -d gateway

down-gateway:
	docker-compose stop gateway

logs-gateway:
	docker-compose logs -f gateway

restart-gateway:
	docker-compose stop gateway && docker-compose up -d gateway

## auth-service
build-auth:
	docker-compose build auth-service

up-auth:
	docker-compose up -d auth-service

down-auth:
	docker-compose stop auth-service

logs-auth:
	docker-compose logs -f auth-service

restart-auth:
	docker-compose stop auth-service && docker-compose up -d auth-service

## chatbot-service
build-chatbot:
	docker-compose build chatbot-service

up-chatbot:
	docker-compose up -d chatbot-service

down-chatbot:
	docker-compose stop chatbot-service

logs-chatbot:
	docker-compose logs -f chatbot-service

restart-chatbot:
	docker-compose stop chatbot-service && docker-compose up -d chatbot-service

## report-service
build-report:
	docker-compose build report-service

up-report:
	docker-compose up -d report-service

down-report:
	docker-compose stop report-service

logs-report:
	docker-compose logs -f report-service

restart-report:
	docker-compose stop report-service && docker-compose up -d report-service

## cbam-service
build-cbam:
	docker-compose build cbam-service

up-cbam:
	docker-compose up -d cbam-service

down-cbam:
	docker-compose stop cbam-service

logs-cbam:
	docker-compose logs -f cbam-service

restart-cbam:
	docker-compose stop cbam-service && docker-compose up -d cbam-service

## lca-service
build-lca:
	docker-compose build lca-service

up-lca:
	docker-compose up -d lca-service

down-lca:
	docker-compose stop lca-service

logs-lca:
	docker-compose logs -f lca-service

restart-lca:
	docker-compose stop lca-service && docker-compose up -d lca-service

## message-service
build-message:
	docker-compose build message-service

up-message:
	docker-compose up -d message-service

down-message:
	docker-compose stop message-service

logs-message:
	docker-compose logs -f message-service

restart-message:
	docker-compose stop message-service && docker-compose up -d message-service

## frontend
build-frontend:
	docker-compose build frontend

up-frontend:
	docker-compose up -d frontend

down-frontend:
	docker-compose stop frontend

logs-frontend:
	docker-compose logs -f frontend

restart-frontend:
	docker-compose stop frontend && docker-compose up -d frontend

## postgres
up-postgres:
	docker-compose up -d postgres

down-postgres:
	docker-compose stop postgres

logs-postgres:
	docker-compose logs -f postgres

restart-postgres:
	docker-compose stop postgres && docker-compose up -d postgres

## redis
up-redis:
	docker-compose up -d redis

down-redis:
	docker-compose stop redis

logs-redis:
	docker-compose logs -f redis

restart-redis:
	docker-compose stop redis && docker-compose up -d redis

# 🛠️ 유틸리티 명령어
clean:
	docker-compose down -v --remove-orphans

clean-all:
	docker-compose down -v --remove-orphans && docker system prune -f

status:
	docker-compose ps && echo "\n=== 서비스 상태 ===" && docker-compose logs --tail=10

help:
	@echo "🔧 GreenSteel MSA Makefile 명령어"
	@echo ""
	@echo "📋 공통 명령어:"
	@echo "  make up      - 전체 시스템 시작"
	@echo "  make down    - 전체 시스템 중지"
	@echo "  make logs    - 전체 로그 확인"
	@echo "  make restart - 전체 시스템 재시작"
	@echo "  make ps      - 서비스 상태 확인"
	@echo ""
	@echo "🚀 서비스별 명령어:"
	@echo "  make up-gateway    - Gateway 시작"
	@echo "  make up-auth       - Auth Service 시작"
	@echo "  make up-chatbot    - Chatbot Service 시작"
	@echo "  make up-report     - Report Service 시작"
	@echo "  make up-cbam       - CBAM Service 시작"
	@echo "  make up-lca        - LCA Service 시작"
	@echo "  make up-frontend   - Frontend 시작"
	@echo ""
	@echo "🛠️ 유틸리티:"
	@echo "  make clean     - 볼륨 삭제 및 정리"
	@echo "  make clean-all - 전체 정리"
	@echo "  make status    - 상태 및 로그 확인"
