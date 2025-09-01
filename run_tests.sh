#!/bin/bash

# MatDir 테스트 실행 스크립트

echo "🧪 MatDir 기능 테스트 시작"
echo "================================"

# 환경변수 확인
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL 환경변수가 설정되지 않았습니다."
    echo "Railway 환경변수를 확인하거나 .env 파일을 설정하세요."
    exit 1
fi

echo "✅ DATABASE_URL 환경변수 확인됨"
echo "🔧 DATABASE_URL: ${DATABASE_URL:0:50}..."

# Python 가상환경 확인 및 활성화
if [ -d "venv" ]; then
    echo "🐍 가상환경 활성화 중..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "🐍 가상환경 활성화 중..."
    source .venv/bin/activate
else
    echo "⚠️ 가상환경을 찾을 수 없습니다. 시스템 Python을 사용합니다."
fi

# Python 버전 확인
echo "🐍 Python 버전 확인 중..."
python --version

# 필요한 패키지 설치 확인
echo "📦 필요한 패키지 설치 확인 중..."
pip install asyncpg

# 테스트 실행
echo ""
echo "🚀 테스트 실행 중..."
echo "================================"

# 1. 연결 테스트만 실행
echo "1️⃣ 데이터베이스 연결 테스트"
python test_matdir_functionality.py --connection-only

if [ $? -eq 0 ]; then
    echo "✅ 연결 테스트 성공"
    echo ""
    
    # 2. 간단한 기능 테스트
    echo "2️⃣ 간단한 기능 테스트"
    python test_matdir_simple.py
    
    if [ $? -eq 0 ]; then
        echo "✅ 간단한 기능 테스트 성공"
        echo ""
        
        # 3. 전체 기능 테스트
        echo "3️⃣ 전체 기능 테스트"
        python test_matdir_functionality.py
        
        if [ $? -eq 0 ]; then
            echo "🎉 모든 테스트 통과!"
            exit 0
        else
            echo "❌ 전체 기능 테스트 실패"
            exit 1
        fi
    else
        echo "❌ 간단한 기능 테스트 실패"
        exit 1
    fi
else
    echo "❌ 연결 테스트 실패"
    exit 1
fi
