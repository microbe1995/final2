# Context

이 코드는 CBAM EdgeService의 제품→공정(consumption) 배출량 전파 로직입니다.
현재 구조는 프리뷰와 DB 저장을 분리해서, 연결이 끊기면 프리뷰가 0으로 떨어지고 DB에는 저장되지 않도록 되어 있습니다.
이 동작은 유지해야 합니다.

# Problem

1. 분배 비율이 잘못 구현되어 있습니다.
현재는 to_next_process 대비 allocated_amount 비율을 사용하지만,
내가 원하는 것은 (생산량 - 판매량 - EU판매량)/생산량 비율을 기준으로 하는 것입니다.
2. 누적 배출량 업데이트가 덮어쓰기 방식(attrdir_em + 귀속배출)이라,
다른 경로에서 누적된 배출량이 있으면 지워지는 문제가 있습니다.

# Requirement

1. 분배 비율을 다음과 같이 수정:
process_ratio = allocated_amount / product_amount
(product_amount이 0일 경우는 안전하게 처리)
2. consume에서 공정 누적 배출량 업데이트 시 덮어쓰기 대신 가산하도록 수정:
total_process_emission = (process_data['cumulative_emission'] or process_data['attrdir_em']) + process_emission
3. 프리뷰/저장 분리 로직은 절대 바꾸지 말 것.
연결이 끊기면 프리뷰=0으로 보이는 동작은 그대로 유지.

# Task

위 두 가지 문제를 반영하여 EdgeService.propagate_emissions_consume 메서드 코드를 수정하라.