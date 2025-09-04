import json
import sys
import urllib.request
import urllib.error
import urllib.parse
import os


BASE = os.environ.get("CBAM_BASE", "https://gateway-production-22ef.up.railway.app")


def _url(path: str) -> str:
    if path.startswith("http"):
        return path
    return f"{BASE}{path}"


def http_get(path: str):
    req = urllib.request.Request(_url(path), headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_put(path: str, payload: dict):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(_url(path), data=data, method="PUT", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def http_post(path: str, payload: dict | None = None):
    data = json.dumps(payload or {}).encode("utf-8")
    req = urllib.request.Request(_url(path), data=data, method="POST", headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def find_product_id_by_name(name: str) -> int | None:
    items = http_get("/api/v1/cbam/product")
    # API가 배열을 직접 반환
    for it in items:
        if (it.get("product_name") or "").strip() == name:
            return int(it["id"])  # type: ignore
    return None


def get_product(pid: int) -> dict:
    return http_get(f"/api/v1/cbam/product/{pid}")


def ensure_product_amount(pid: int, amount: float, sell: float = 0.0, eusell: float = 0.0):
    cur = get_product(pid)
    need_update = (
        float(cur.get("product_amount") or 0) != float(amount)
        or float(cur.get("product_sell") or 0) != float(sell)
        or float(cur.get("product_eusell") or 0) != float(eusell)
    )
    if need_update:
        http_put(f"/api/v1/cbam/product/{pid}", {
            "product_amount": amount,
            "product_sell": sell,
            "product_eusell": eusell,
        })
    return get_product(pid)


def find_process_id_by_name(name: str) -> int | None:
    items = http_get("/api/v1/cbam/process")
    for it in items:
        if (it.get("process_name") or "").strip() == name:
            return int(it["id"])  # type: ignore
    return None


def get_process_emission(pid: int) -> dict:
    data = http_get(f"/api/v1/cbam/edge/process-emission/{pid}")
    return data.get("data") or {}


def main():
    product_name = os.environ.get("CBAM_PRODUCT", "블룸")
    process_name = os.environ.get("CBAM_PROCESS", "압연")

    print(f"BASE={BASE}")
    print(f"찾을 제품: {product_name}, 공정: {process_name}")

    pid = find_product_id_by_name(product_name)
    if not pid:
        print("제품을 찾지 못했습니다.")
        sys.exit(2)

    print(f"제품 ID: {pid}")
    after_save = ensure_product_amount(pid, 150.0, 0.0, 0.0)
    print("제품 저장 후:", json.dumps({
        "product_amount": after_save.get("product_amount"),
        "product_sell": after_save.get("product_sell"),
        "product_eusell": after_save.get("product_eusell"),
    }, ensure_ascii=False))

    print("전체 전파 실행…")
    http_post("/api/v1/cbam/edge/propagate/full", {})

    rid = find_process_id_by_name(process_name)
    if not rid:
        print("공정을 찾지 못했습니다.")
        sys.exit(3)

    em = get_process_emission(rid)
    print("압연 배출량:", json.dumps(em, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        print("HTTPError:", e.code, e.read().decode("utf-8", errors="ignore"))
        sys.exit(1)
    except Exception as e:
        print("Error:", repr(e))
        sys.exit(1)


