import os
import sys
import json
import time
from datetime import date

import requests


def main():
    # 게이트웨이 베이스 URL: 환경변수 GATEWAY_URL 우선, 없으면 기본값
    gateway_url = os.getenv("GATEWAY_URL", "https://gateway-production-22ef.up.railway.app")
    endpoint = f"{gateway_url}/api/v1/cbam/process"

    # 테스트용 데이터 (사용자가 보고 계신 install_id 14 가정)
    # 필요 시 환경변수 INSTALL_ID 로 조정 가능
    install_id = int(os.getenv("INSTALL_ID", "14"))
    process_name = os.getenv("PROCESS_NAME", "중복테스트공정-AI")

    payload = {
        "process_name": process_name,
        "install_id": install_id,
        # 날짜는 생략 가능(None 허용), 예시로 오늘 날짜 사용 가능
        # "start_period": str(date.today()),
        # "end_period": str(date.today()),
        "product_ids": []
    }

    headers = {"Content-Type": "application/json"}

    print("[1] 최초 생성 시도...", endpoint)
    r1 = requests.post(endpoint, data=json.dumps(payload), headers=headers, timeout=20)
    print(" -> status:", r1.status_code)
    print(" -> body:", r1.text)

    # 2차 요청 (중복 시도)
    time.sleep(1)
    print("[2] 동일 데이터로 재생성 시도(중복 기대, 409)...")
    r2 = requests.post(endpoint, data=json.dumps(payload), headers=headers, timeout=20)
    print(" -> status:", r2.status_code)
    print(" -> body:", r2.text)

    # 가능하면 생성된 ID를 사용해 정리(delete)
    created_id = None
    try:
        if r1.ok:
            body = r1.json()
            created_id = body.get("id")
    except Exception:
        created_id = None

    if created_id:
        delete_url = f"{endpoint}/{created_id}"
        print(f"[3] 정리: 생성된 공정 삭제 시도 -> {delete_url}")
        r3 = requests.delete(delete_url, timeout=20)
        print(" -> status:", r3.status_code)
        print(" -> body:", r3.text)
    else:
        print("[3] 정리 스킵: 생성 ID를 확인할 수 없음")

    # 간단 판정 출력
    ok_first = r1.status_code in (200, 201)
    ok_conflict = r2.status_code == 409
    print("\n결과 요약:")
    print(" - 최초 생성 성공:", ok_first)
    print(" - 중복 시 409 확인:", ok_conflict)

    # 종료 코드
    if ok_first and ok_conflict:
        sys.exit(0)
    sys.exit(1)


if __name__ == "__main__":
    main()


