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

amount × 배출계수 × 산화계수 → 직접배출량

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
node_type_enum: 'process', 'product'
edge_kind_enum: 'consume', 'produce', 'continue'
🔗 테이블 관계
install ← product (1:N)
product ← process (1:N)
process ← process_input (1:N)
edge 테이블은 process와 product 간의 연결을 관리