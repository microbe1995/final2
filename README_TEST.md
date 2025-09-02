# 🔬 CBAM 제품 관리 기능 테스트 스크립트

이 프로젝트는 CBAM 서비스의 제품 관리 기능을 종합적으로 테스트하는 Python 스크립트입니다.

## 📋 기능

- ✅ **CRUD 테스트**: 제품 생성, 조회, 수정, 삭제
- ✅ **API 엔드포인트 테스트**: 모든 제품 관련 API 테스트
- ✅ **에러 처리 테스트**: 잘못된 데이터 및 예외 상황 처리
- ✅ **대량 작업 테스트**: 여러 제품 동시 처리
- ✅ **성능 테스트**: API 응답 시간 및 안정성 확인

## 🚀 빠른 시작

### 1. 환경 요구사항

- Python 3.8 이상 (권장: Python 3.13.5)
- pip (Python 패키지 관리자)
- CBAM 서비스 실행 중 (기본: http://localhost:8001)

### 2. 패키지 설치

```bash
# 자동 설치 (권장)
python run_tests.py --install-only

# 또는 수동 설치
pip install -r test_requirements.txt
```

### 3. 테스트 실행

```bash
# 전체 테스트 실행
python run_tests.py

# 특정 서비스 URL로 테스트
python run_tests.py --url http://localhost:8001

# 패키지 설치 없이 테스트만 실행
python run_tests.py --no-install
```

## 📁 파일 구조

```
├── test_cbam_products.py      # 메인 테스트 스크립트
├── run_tests.py               # 테스트 실행기
├── test_requirements.txt      # Python 패키지 의존성
└── README_TEST.md            # 이 파일
```

## 🔧 테스트 구성

### 테스트 대상 API

- `GET /` - 제품 목록 조회
- `GET /names` - 제품명 목록 조회
- `GET /{id}` - 단일 제품 조회
- `POST /` - 제품 생성
- `PUT /{id}` - 제품 수정
- `DELETE /{id}` - 제품 삭제

### 테스트 시나리오

1. **서비스 상태 확인**
   - Health check 엔드포인트 테스트

2. **기본 CRUD 테스트**
   - 제품 생성 → 조회 → 수정 → 삭제

3. **필터링 및 검색 테스트**
   - 설치 ID별 필터링
   - 제품명 검색

4. **대량 작업 테스트**
   - 여러 제품 동시 생성/수정/삭제

5. **에러 처리 테스트**
   - 잘못된 데이터 처리
   - 존재하지 않는 리소스 접근

## 📊 테스트 결과 예시

```
🚀 CBAM 제품 관리 기능 종합 테스트 시작
📍 테스트 대상: http://localhost:8001

📋 제품 목록 조회 테스트 시작
✅ 전체 제품 조회 성공: 15개
✅ 설치 ID별 필터링 성공: 8개
✅ 제품명 검색 성공: '테스트' - 3개

📝 제품 생성 테스트 시작: 테스트제품_기본
✅ 제품 생성 성공: ID 123

📋 단일 제품 조회 테스트 시작: ID 123
✅ 단일 제품 조회 성공: 테스트제품_기본

📝 제품 수정 테스트 시작: ID 123
✅ 제품 수정 성공: 테스트제품_기본

🗑️ 제품 삭제 테스트 시작: ID 123
✅ 제품 삭제 성공: ID 123

📦 대량 작업 테스트 시작
✅ 대량 제품 생성 완료: 3개
✅ 대량 제품 수정 완료
✅ 대량 제품 삭제 완료

🚨 에러 처리 테스트 시작
✅ 404 에러 처리 정상
✅ 유효성 검사 에러 처리 정상

============================================================
📊 테스트 결과 요약
============================================================
health_check         : ✅ 통과
get_products        : ✅ 통과
get_product_names   : ✅ 통과
create_product      : ✅ 통과
get_single_product  : ✅ 통과
update_product      : ✅ 통과
delete_product      : ✅ 통과
bulk_operations     : ✅ 통과
error_handling      : ✅ 통과
------------------------------------------------------------
전체 테스트: 9개
통과: 9개
실패: 0개
성공률: 100.0%
🎉 모든 테스트가 성공적으로 완료되었습니다!
```

## ⚙️ 고급 설정

### 환경변수

```bash
# CBAM 서비스 URL 설정
export CBAM_SERVICE_URL="http://localhost:8001"

# 로그 레벨 설정
export LOG_LEVEL="DEBUG"
```

### 커스텀 테스트

```python
# test_cbam_products.py 수정하여 특정 테스트 추가
async def test_custom_functionality(self):
    """사용자 정의 테스트"""
    # 테스트 로직 구현
    pass
```

## 🐛 문제 해결

### 일반적인 문제

1. **연결 오류**
   ```
   ❌ 서비스 상태 확인 중 오류: Cannot connect to host localhost:8001
   ```
   - CBAM 서비스가 실행 중인지 확인
   - 포트 번호 확인 (기본: 8001)

2. **패키지 설치 오류**
   ```
   ❌ 패키지 설치 실패
   ```
   - Python 버전 확인 (3.8 이상 필요)
   - pip 업그레이드: `python -m pip install --upgrade pip`

3. **권한 오류**
   ```
   ❌ 권한 거부됨
   ```
   - 관리자 권한으로 실행
   - 가상환경 사용 권장

### 디버깅

```bash
# 상세한 로그 출력
python test_cbam_products.py 2>&1 | tee test.log

# 특정 테스트만 실행
python -c "
import asyncio
from test_cbam_products import CBAMProductTester

async def debug_test():
    async with CBAMProductTester() as tester:
        await tester.test_health_check()

asyncio.run(debug_test())
"
```

## 📈 성능 모니터링

테스트 실행 시 다음 메트릭을 확인할 수 있습니다:

- **응답 시간**: 각 API 호출의 응답 시간
- **처리량**: 초당 처리 가능한 요청 수
- **에러율**: 실패한 요청의 비율
- **동시성**: 동시 처리 가능한 요청 수

## 🤝 기여하기

1. 이슈 리포트 생성
2. 기능 요청 제안
3. 코드 품질 개선 제안
4. 새로운 테스트 케이스 추가

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 지원

문제가 발생하거나 질문이 있으시면:

1. GitHub Issues 생성
2. 프로젝트 문서 확인
3. 개발팀에 문의

---

**마지막 업데이트**: 2024년 12월
**Python 버전**: 3.13.5
**테스트 대상**: CBAM 서비스 v1.0.0
