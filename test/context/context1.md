가능합니다. “투입량 변경 → 해당 공정 배출량 갱신 → 그래프를 따라 하류 공정/제품까지 누적값 반영” 흐름을 백엔드 계산과 프론트 상태 갱신 양쪽에서 연결해 주면 됩니다. 어디를 건드려야 하는지 정확히 짚어 드립니다.
백엔드 service/cbam-service/app/domain
핵심 계산 흐름 연결
calculation/calculation_service.py:
공정 기준 재계산 함수 추가/확인: recalculate_from_process(process_id: int) → 공정의 matdir/fueldir 합산으로 process_attrdir_emission 갱신 후,
edge를 DFS/BFS로 따라가며
continue: 공정→공정 누적 전파
produce: 공정→제품 집계
consume: 제품→다음 공정 분배
저장은 calculation_repository.py, 하류 탐색은 edge_repository.py, 제품 누적 반영은 product_repository.py 활용
calculation/calculation_controller.py:
API 노출: POST /api/v1/cbam/calculation/recalc?process_id=...
투입 변경 시 계산 트리거
matdir/matdir_service.py, fueldir/fueldir_service.py:
create/update/delete 트랜잭션 마지막에 CalculationService.recalculate_from_process(process_id) 호출
해당 컨트롤러(matdir_controller.py, fueldir_controller.py)는 서비스 호출만 유지
참고: 그래프는 edge/edge_repository.py가 소스/타깃 탐색 로직을 가지고 있으므로 여기서 하류 노드 조회 유틸을 재사용
프론트엔드 frontend/src
즉시 반영 UX
hooks/useProcessCanvas.ts:
투입량 입력 핸들러에서 저장 성공 후
1) 계산 API 호출: axios.post('/api/v1/cbam/calculation/recalc', { process_id })
2) 응답의 변경된 노드들만 setNodes(prev => ...)로 갱신(직접·누적 배출량, 원료/연료 직접값)
필요 시 디바운스(300~500ms)로 과도한 호출 방지
hooks/useReactFlowAPI.ts:
부분 업데이트 유틸 추가: 노드 id 리스트와 새 data로 최소 변경 렌더
components/cbam/ProcessManager.tsx:
“투입량 입력” 모달/패널의 onSave에서 위 흐름 실행
선택적 고도화
웹소켓(SSE)로 서버 계산 완료 푸시를 받아 useProcessCanvas에서 구독해 실시간 반영(없어도 REST로 충분)
API 경로는 반드시 게이트웨이 프록시 경유해야 합니다. axios 기반 클라이언트에서 NEXT_PUBLIC_API_BASE_URL 사용 1 2.
적용 순서(권장)
1) 백엔드: matdir_service.py/fueldir_service.py에 계산 트리거 추가 → calculation_service.py에 recalculate_from_process 구현/보강 → 컨트롤러에 재계산 API 확인.
2) 프론트: useProcessCanvas.ts 저장 흐름에 재계산 API 호출+노드 부분 업데이트 추가 → ProcessManager.tsx에서 해당 훅 사용.
3) 테스트: 투입량 변경 시 중간 공정 및 최종 제품 노드의 “직접/누적” 배출량이 즉시 갱신되는지 확인.
원하시면 위 파일들에 필요한 최소 edits를 바로 적용해 드리겠습니다.