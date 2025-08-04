from fastapi import FastAPI, Request, Form
from fastapi.responses import JSONResponse
import os
import base64
import uvicorn

app = FastAPI(
    title="Report Service",
    description="GreenSteel MSA 시스템의 리포트 서비스",
    version="1.0.0"
)

@app.post("/report/upload/")
async def upload_report(filename: str = Form(...), pdfBase64: str = Form(...)):
    try:
        # public/reports 폴더 생성
        reports_dir = os.path.join(os.getcwd(), 'public', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        file_path = os.path.join(reports_dir, filename)
        base64_data = pdfBase64.replace('data:application/pdf;base64,', '')
        with open(file_path, "wb") as f:
            f.write(base64.b64decode(base64_data))
        return {"url": f"/reports/{filename}", "message": "리포트 업로드 성공"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "파일 저장 실패", "error": str(e)})

@app.get("/report/list/")
async def list_reports():
    try:
        reports_dir = os.path.join(os.getcwd(), 'public', 'reports')
        if not os.path.exists(reports_dir):
            return {"reports": []}
        
        files = [f for f in os.listdir(reports_dir) if f.endswith('.pdf')]
        return {"reports": files}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "리포트 목록 조회 실패", "error": str(e)})

@app.get("/report/{filename}")
async def get_report(filename: str):
    try:
        reports_dir = os.path.join(os.getcwd(), 'public', 'reports')
        file_path = os.path.join(reports_dir, filename)
        
        if not os.path.exists(file_path):
            return JSONResponse(status_code=404, content={"message": "파일을 찾을 수 없습니다"})
        
        return {"filename": filename, "path": file_path, "size": os.path.getsize(file_path)}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": "리포트 조회 실패", "error": str(e)})

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "report-service"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8003) 