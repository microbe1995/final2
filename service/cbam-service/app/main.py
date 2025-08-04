"""
CBAM Service
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging
import os
import json
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="CBAM Service",
    description="Carbon Border Adjustment Mechanism Service",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CBAM 데이터 모델
class CBAMCalculationRequest(BaseModel):
    product_name: str
    quantity: float
    unit: str = "ton"
    country_of_origin: str
    carbon_intensity: float  # kg CO2/ton
    electricity_emission_factor: Optional[float] = 0.5  # kg CO2/kWh
    transport_distance: Optional[float] = 0  # km
    transport_mode: Optional[str] = "ship"  # ship, truck, air

class CBAMCalculationResponse(BaseModel):
    product_name: str
    quantity: float
    unit: str
    country_of_origin: str
    carbon_footprint: float  # kg CO2
    cbam_tax_rate: float  # EUR/ton CO2
    cbam_tax_amount: float  # EUR
    calculation_date: datetime
    details: Dict

# CBAM 세율 (2023-2026년 기준)
CBAM_TAX_RATES = {
    "cement": 0.376,      # EUR/ton CO2
    "iron_steel": 0.376,  # EUR/ton CO2
    "aluminium": 0.376,   # EUR/ton CO2
    "fertilisers": 0.376, # EUR/ton CO2
    "electricity": 0.376, # EUR/ton CO2
    "hydrogen": 0.376,    # EUR/ton CO2
    "default": 0.376      # 기본 세율
}

# 운송 모드별 배출 계수 (kg CO2/ton-km)
TRANSPORT_EMISSION_FACTORS = {
    "ship": 0.015,
    "truck": 0.1,
    "air": 0.8,
    "train": 0.03
}

def calculate_cbam_tax(product_name: str, carbon_footprint: float) -> float:
    """CBAM 세금 계산"""
    tax_rate = CBAM_TAX_RATES.get(product_name.lower(), CBAM_TAX_RATES["default"])
    return carbon_footprint * tax_rate

def calculate_transport_emissions(distance: float, mode: str, quantity: float) -> float:
    """운송 배출량 계산"""
    emission_factor = TRANSPORT_EMISSION_FACTORS.get(mode, TRANSPORT_EMISSION_FACTORS["ship"])
    return distance * emission_factor * quantity

@app.get("/")
async def root():
    return {
        "service": "CBAM Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    logger.info("🔍 CBAM Service Health Check")
    return {"status": "CBAM Service Healthy"}

@app.post("/calculate")
async def calculate_cbam(request: CBAMCalculationRequest):
    try:
        logger.info(f"🧮 CBAM calculation request received for {request.product_name}")
        
        # 1. 제품 생산 배출량 계산
        production_emissions = request.quantity * request.carbon_intensity
        
        # 2. 운송 배출량 계산
        transport_emissions = calculate_transport_emissions(
            request.transport_distance, 
            request.transport_mode, 
            request.quantity
        )
        
        # 3. 총 탄소 발자국 계산
        total_carbon_footprint = production_emissions + transport_emissions
        
        # 4. CBAM 세금 계산
        cbam_tax_amount = calculate_cbam_tax(request.product_name, total_carbon_footprint)
        
        # 5. 응답 생성
        response = CBAMCalculationResponse(
            product_name=request.product_name,
            quantity=request.quantity,
            unit=request.unit,
            country_of_origin=request.country_of_origin,
            carbon_footprint=total_carbon_footprint,
            cbam_tax_rate=CBAM_TAX_RATES.get(request.product_name.lower(), CBAM_TAX_RATES["default"]),
            cbam_tax_amount=cbam_tax_amount,
            calculation_date=datetime.now(),
            details={
                "production_emissions": production_emissions,
                "transport_emissions": transport_emissions,
                "carbon_intensity": request.carbon_intensity,
                "transport_distance": request.transport_distance,
                "transport_mode": request.transport_mode
            }
        )
        
        logger.info(f"✅ CBAM calculation completed: {total_carbon_footprint:.2f} kg CO2, Tax: €{cbam_tax_amount:.2f}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ CBAM calculation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"CBAM calculation error: {str(e)}")

@app.post("/upload")
async def upload_data(file: UploadFile = File(...)):
    logger.info(f"📄 CBAM data upload request received: {file.filename}")
    return {"message": "CBAM data upload endpoint", "filename": file.filename, "status": "success"}

@app.get("/reports")
async def get_cbam_reports():
    logger.info("📋 CBAM reports list request received")
    return {"message": "CBAM reports endpoint", "status": "success"}

@app.get("/standards")
async def get_cbam_standards():
    logger.info("📏 CBAM standards request received")
    return {
        "cbam_tax_rates": CBAM_TAX_RATES,
        "transport_emission_factors": TRANSPORT_EMISSION_FACTORS,
        "description": "CBAM 세율 및 운송 배출 계수"
    }

@app.get("/products")
async def get_supported_products():
    """지원되는 제품 목록 반환"""
    return {
        "supported_products": list(CBAM_TAX_RATES.keys()),
        "description": "CBAM 적용 대상 제품 목록"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", 8004))
    uvicorn.run(app, host="0.0.0.0", port=port) 