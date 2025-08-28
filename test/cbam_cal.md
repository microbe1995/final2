------------------------------------------------------
cbam 제품당 내재배출량 산정 로직을 구상할꺼야

이제부터 몇가지 규칙을 줄꺼야 이것을 무조건 따라야해 

1. 먼저 DB 를 먼저 만들고 DB 컬럼명을 기준으로 모든 스키마 부터 차례대로 작업이 이루어져야해 기억해

2. () 안의 영문명은 railway 상 DB 의 해당 테이블의 컬럼 명으로 지정해

3. postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway
이건 railway 상 DB 주소야

4. 아래와 같이 CBAM 계산에 대한 로직과  각각의 지칭하는 명을 미리 숙지해

4.1 재품당 내재배출량(see) = 직접귀속배출량(attrdir_em) + 간접귀속배출량(attrindir_em) 로 이루어 진다

4.2 직접귀속배출량(attrdir_em) = 연료직접배출량(fueldir_em) + 원료직접배출량(matdir_em) + 열유입배출량(heatimp_em) - 열유출배출량(heatexp_em) + 폐가스유입배출량(gasimp_em) - 폐가스유출배출량(gasexp_em) - 전력생산에따른배출량(genelec_em)

4.3 간접귀속배출량(attrindir_em) = 전력소비에따른배출량(comelec_em)


먼저 5. 부터 구현할꺼야 

5. 원료직접배출량(matdir_em) =  원료량(mat_amount) * 원료배출계수(mat_factor) + 산화계수(oxyfactor) 

이렇게 해서 원료직접배출량이 구해 지도록 만들고 싶어 

원료직접배출량관련 table 은 matdir으로 만들면 될까? 

6. 한공정에 여러 종류의 원료 연료가 들어 갈수 있게 해야해
    즉 공정과 원료 연료는 1:N 관계야