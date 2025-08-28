✅ 당신이 원하는 최종 결과 (Expected Behavior)
1. CBAM 기준에 맞는 '제품별 내재배출량 산정' 결과를 도출하는 것

즉,
제품 하나하나에 대해 정확한 탄소배출량(직접 + 간접)을 자동 계산하고, 보고서용으로 산출 가능한 상태로 만드는 것이 최종 목표입니다.


✅ Railway + React Flow + FastAPI 기반 시스템에서 동작 시나리오
① Railway DB에 위 ERD대로 테이블 생성

install, product, process, process_input, edge 등 실제 테이블 생성

생성 후 FastAPI로 REST API 연결

② React Flow로 제품 노드 / 공정 노드 생성 + 연결 (엣지 생성)

사용자: 드래그 & 드롭으로 제품/공정 노드 생성

노드 더블 클릭 → 입력창 팝업

제품 노드 → 생산량, 수출량, 판매량 등 입력

공정 노드 → 원료/연료/전력 등 입력

노드 간 연결

공정 → 제품 : produce 엣지

제품 → 공정 : consume 엣지

공정 → 공정 : continue 엣지

연결 시 엣지 테이블에 자동 저장 (edge 테이블)

③ FastAPI에서 배출량 자동 계산 로직 작동

각 process_input에서:

input_amount × 배출계수 × 산화계수 → 직접배출량

공정별 전체 배출량 합산

공정 간 continue일 경우, 배출량 누적

공정 → 제품 연결 시, 해당 공정의 배출량을 제품에 귀속

④ 제품별 최종 내재배출량 자동 산출

제품 노드에는 다음이 자동으로 귀속됨:

⬩ 해당 제품을 산출한 모든 공정의 누적 직접배출량

⬩ 전력 등 간접배출량도 포함

즉, 한 제품에 귀속된 총 탄소배출량 = 최종 결과


product_category_enum: '단순제품', '복합제품'
input_type_enum: 'material', 'fuel', 'electricity'
edge_kind_enum: 'consume', 'produce', 'continue'
🔗 테이블 관계
install ← product (1:N)
product ← process (1:N)
process ← process_input (1:N)
edge 테이블은 process와 product 간의 연결을 관리

- 사업장명 입력시 DB 내 이름과 중복이 되지않도록 할것 
- 데이터 입력값이 누적과 중복이 되지 않도록 할것



로트번호	생산품명	생산수량	투입일	종료일	공정	투입물명	수량	단위
1	코크스 	100	2025-08-01	2025-08-04	코크스 생산	점결탄		
2	소결광	100	2025-08-02	2025-08-03	소결	광석		
2	소결광	100	2025-08-02	2025-08-03	소결	정립광		
2	소결광	100	2025-08-02	2025-08-03	소결	석회		
2	소결광	100	2025-08-02	2025-08-03	소결	코크스 오븐 코크스		
3	블룸	100	2025-08-03	2025-08-04	제선	철ㄹ		
3	블룸	100	2025-08-03	2025-08-04	제선	Coke		
3	블룸	100	2025-08-04	2025-08-06	제강	열유입		
3	블룸	100	2025-08-06	2025-08-09	주조	열유입		
3	블룸	100	2025-08-06	2025-08-09	주조	냉각수		
3	블룸	100	2025-08-06	2025-08-09	주조	윤활제		
3	블룸	100	2025-08-06	2025-08-09	주조	ㅎ놘철		
4	빌렛	100	2025-08-03	2025-08-06	제선	환ㅇ웣널		
4	빌렛	100	2025-08-03	2025-08-06	제선	EAF 탄소 전극		
4	빌렛	100	2025-08-08	2025-08-11	주조	물		
4	빌렛	100	2025-08-08	2025-08-11	주조	모래		
5	형강	100	2025-08-12	2025-08-15	압연	블룸		
5	형강	100	2025-08-12	2025-08-15	압연	열유입		
5	형강	100	2025-08-15	2025-08-18	압연	요소수		
5	형강	100	2025-08-15	2025-08-18	포장	형강		
5	형강	100	2025-08-15	2025-08-18	포장	포장재		


데이터 수집단은 이런식으로 위에 처럼 이루어져있을꺼야 이런식으로 공정별로 투입일 투입종료일이 나오니까 공정 인풋입력할때 참고해줘


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
