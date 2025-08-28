------------------------------------------------------
cbam 제품당 내재배출량 산정 로직을 구상할꺼야

이제부터 몇가지 규칙을 줄꺼야 이것을 무조건 따라야해 

1. 먼저 DB 를 먼저 만들고 DB 컬럼명을 기준으로 모든 스키마 부터 차례대로 작업이 이루어져야해 기억해

2. () 안의 영문명은 railway 상 DB 의 해당 테이블의 컬럼 명으로 지정해

3. postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway
이건 railway 상 DB 주소야

Calculation 도메인 (정상 작동):
CalculationRepository는 직접 psycopg2로 PostgreSQL 연결
환경변수 DATABASE_URL을 직접 사용
비동기(async/await) 방식

위 방식을 참고해서 프론트에서 입력하면 게이트웨이를 거쳐 서비스 그리고 db 까지 데이터가 흐르고 db 에 저장되도록 해줘

4. 아래와 같이 CBAM 계산에 대한 로직과  각각의 지칭하는 명을 미리 숙지해

4.1 재품고유내재배출량(attr_em) = 직접귀속배출량(attrdir_em) + 간접귀속배출량(attrindir_em) 로 이루어 진다

4.2 직접귀속배출량(attrdir_em) = 연료직접배출량(fueldir_em) + 원료직접배출량(matdir_em) + 열유입배출량(heatimp_em) - 열유출배출량(heatexp_em) + 폐가스유입배출량(gasimp_em) - 폐가스유출배출량(gasexp_em) - 전력생산에따른배출량(genelec_em)

4.3 간접귀속배출량(attrindir_em) = 전력소비에따른배출량(comelec_em)


먼저 5. 부터 구현할꺼야 

5. 원료직접배출량(matdir_em) =  원료량(mat_amount) * 원료배출계수(mat_factor) + 산화계수(oxyfactor) 

이렇게 해서 원료직접배출량이 구해 지도록 만들고 싶어 

원료직접배출량관련 table 은 matdir으로 만들면 될까? 

6. 한공정에 여러 종류의 원료 연료가 들어 갈수 있게 해야해
    즉 공정과 원료 연료는 1:N 관계야

7. 그리고 각 원료직접배출량, 연료직접배출량, 열유입배출량, 열유출배출량, 폐가스유입배출량, 폐가스유출배출량, 전력생산에 따른 배출량은 직접귀속배출량(attrdir_em) 이고 이건 각 공정에 귀속이 되어야 해 이렇게 지금 process table 이 짜여져 있는지 살펴봐줘

8. 연료직접배출량(fueldir_em) = 연료량(fuel_amount) * 연료배출계수(fuel_factor) * fueloxy_factor(산화계수)

형태로 계산되는 것도 원료직접배출량 패턴을 참고해서 만들어줘 무조건 railway db에 테이블 부터 만들고 그거릉 기준으로 스키마 레포지토리 서비스 모델 컨트롤러 이렇게 만들어줘 엔드포인트 경로까지

id	process_id	fuel_name	fuel_factor	fuel_amount	fuel_oxyfactor	fueldir_em	created_at	updated_at

위 형태로 fueldir 테이블을 만들어줘 