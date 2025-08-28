너는 FastAPI + SQLAlchemy를 사용해서 API를 작성한다.
이미 PostgreSQL DB에 hs_cn_mapping 테이블이 생성되어 있다. 테이블 구조는 다음과 같다:

CREATE TABLE hs_cn_mapping (
    id SERIAL PRIMARY KEY,
    hscode CHAR(6) NOT NULL,            -- HS 코드 (앞 6자리)
    aggregoods_name TEXT,               -- 제품 대분류(한글)
    aggregoods_engname TEXT,            -- 제품 대분류(영문)
    cncode_total CHAR(8) NOT NULL,      -- CN 코드 (8자리)
    goods_name TEXT,                    -- 상세 품명(한글)
    goods_engname TEXT                  -- 상세 품명(영문)
);

요구사항:
1. 사용자가 HS 코드(10자리)를 입력하면, 앞 6자리를 추출한다.
2. DB에서 hscode = 앞 6자리인 레코드를 조회한다.
3. 결과가 여러 개일 경우 모두 반환한다.
4. 응답에는 반드시 아래 정보가 포함되어야 한다:
   - cncode_total (CN 코드 8자리)
   - goods_name (품목명 한글)
   - goods_engname (품목명 영문)
   - aggregoods_name (품목군 한글)
   - aggregoods_engname (품목군 영문)

API 스펙:
- GET /api/v1/cncode/lookup/{hs_code_10}
- Path Parameter: hs_code_10 (문자열, 10자리)
- Response: JSON 배열

예시 입력:
  GET /api/v1/cncode/lookup/7208510000

예시 응답:
[
  {
    "cncode_total": "72085100",
    "goods_name": "철이나 비합금강의 평판압연제품...",
    "goods_engname": "Flat-rolled products of iron or non-alloy steel...",
    "aggregoods_name": "철및철강제품",
    "aggregoods_engname": "IronAndSteelProducts"
  }
]
