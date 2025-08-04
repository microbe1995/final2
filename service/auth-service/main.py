from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(
    title="Auth Service",
    description="GreenSteel MSA 시스템의 인증 서비스",
    version="1.0.0"
)

# 회원가입
@app.post("/auth/register/")
async def register(request: Request):
    data = await request.json()
    # 실제 회원가입 로직 필요
    return {"message": "회원가입 완료", "user": data, "success": True}

# 로그인
@app.post("/auth/login/")
async def login(request: Request):
    data = await request.json()
    # 실제 로그인 로직 필요
    return {"message": "로그인 성공", "user": data, "success": True}

# 로그아웃
@app.post("/auth/logout/")
async def logout():
    # 실제 로그아웃 로직 필요
    return {"message": "로그아웃 되었습니다.", "success": True}

# ID 중복확인
@app.post("/auth/check-id/")
async def check_id(request: Request):
    data = await request.json()
    # 실제 중복확인 로직 필요
    return {"available": True, "message": "사용 가능한 ID입니다."}

# 내 정보 조회
@app.get("/user/me/")
async def get_me():
    # 실제 사용자 정보 조회 로직 필요
    return {"user": {"id": "demo", "name": "데모 사용자"}}

# 내 정보 수정
@app.put("/user/update/")
async def update_me(request: Request):
    data = await request.json()
    # 실제 정보 수정 로직 필요
    return {"message": "사용자 정보가 업데이트되었습니다.", "success": True}

# 사용자 정보 조회 (info)
@app.get("/user/info/")
async def get_user_info():
    # 실제 사용자 정보 조회 로직 필요
    return {"user": {"id": "demo", "name": "데모 사용자"}}

# 특정 사용자 정보 조회
@app.get("/user/{user_id}/")
async def get_user_by_id(user_id: str):
    # 실제 사용자 정보 조회 로직 필요
    return {"user": {"id": user_id, "name": "특정 사용자"}}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "auth-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001) 