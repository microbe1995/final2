"""
프록시 스키마 - 데이터 검증 및 직렬화
Gateway의 프록시 기능에서 사용되는 데이터 모델 정의
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime

class ProxyRequest(BaseModel):
    """
    프록시 요청 스키마
    
    Attributes:
        service: 대상 서비스명
        path: 요청 경로
        method: HTTP 메서드
        headers: 요청 헤더
        body: 요청 본문
        params: 쿼리 파라미터
    """
    service: str = Field(..., description="대상 서비스명", min_length=1)
    path: str = Field(..., description="요청 경로", min_length=1)
    method: str = Field(..., description="HTTP 메서드", regex="^(GET|POST|PUT|DELETE|PATCH)$")
    headers: Optional[Dict[str, str]] = Field(default_factory=dict, description="요청 헤더")
    body: Optional[bytes] = Field(default=None, description="요청 본문")
    params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="쿼리 파라미터")
    
    @validator('service')
    def validate_service(cls, v):
        """서비스명 검증"""
        allowed_services = ['auth', 'discovery', 'user']
        if v not in allowed_services:
            raise ValueError(f'지원하지 않는 서비스: {v}. 지원 서비스: {allowed_services}')
        return v
    
    @validator('method')
    def validate_method(cls, v):
        """HTTP 메서드 검증"""
        return v.upper()
    
    class Config:
        """Pydantic 설정"""
        json_encoders = {
            bytes: lambda v: v.decode('utf-8') if v else None
        }

class ProxyResponse(BaseModel):
    """
    프록시 응답 스키마
    
    Attributes:
        status_code: HTTP 상태 코드
        headers: 응답 헤더
        body: 응답 본문
        service: 응답한 서비스명
        response_time: 응답 시간 (밀리초)
        timestamp: 응답 시간
    """
    status_code: int = Field(..., description="HTTP 상태 코드", ge=100, le=599)
    headers: Dict[str, str] = Field(default_factory=dict, description="응답 헤더")
    body: Optional[Any] = Field(default=None, description="응답 본문")
    service: str = Field(..., description="응답한 서비스명")
    response_time: Optional[float] = Field(default=None, description="응답 시간 (밀리초)", ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="응답 시간")
    
    @validator('status_code')
    def validate_status_code(cls, v):
        """상태 코드 검증"""
        if v < 100 or v > 599:
            raise ValueError('HTTP 상태 코드는 100-599 범위여야 합니다')
        return v
    
    class Config:
        """Pydantic 설정"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ServiceHealthRequest(BaseModel):
    """
    서비스 헬스 체크 요청 스키마
    
    Attributes:
        service_name: 서비스명
        timeout: 타임아웃 시간 (초)
    """
    service_name: str = Field(..., description="서비스명", min_length=1)
    timeout: Optional[float] = Field(default=30.0, description="타임아웃 시간 (초)", gt=0, le=300)
    
    @validator('service_name')
    def validate_service_name(cls, v):
        """서비스명 검증"""
        allowed_services = ['auth', 'discovery', 'user']
        if v not in allowed_services:
            raise ValueError(f'지원하지 않는 서비스: {v}. 지원 서비스: {allowed_services}')
        return v

class ServiceHealthResponse(BaseModel):
    """
    서비스 헬스 체크 응답 스키마
    
    Attributes:
        service_name: 서비스명
        status: 서비스 상태
        response_time: 응답 시간 (밀리초)
        status_code: HTTP 상태 코드
        error_message: 오류 메시지 (있는 경우)
        timestamp: 체크 시간
    """
    service_name: str = Field(..., description="서비스명")
    status: str = Field(..., description="서비스 상태", regex="^(healthy|unhealthy|error|unknown)$")
    response_time: Optional[float] = Field(default=None, description="응답 시간 (밀리초)", ge=0)
    status_code: Optional[int] = Field(default=None, description="HTTP 상태 코드", ge=100, le=599)
    error_message: Optional[str] = Field(default=None, description="오류 메시지")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="체크 시간")
    
    class Config:
        """Pydantic 설정"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class GatewayStatusResponse(BaseModel):
    """
    Gateway 상태 응답 스키마
    
    Attributes:
        status: Gateway 상태
        version: Gateway 버전
        uptime: 가동 시간 (초)
        services_count: 등록된 서비스 수
        timestamp: 상태 확인 시간
    """
    status: str = Field(..., description="Gateway 상태", regex="^(healthy|unhealthy|error)$")
    version: str = Field(..., description="Gateway 버전")
    uptime: Optional[float] = Field(default=None, description="가동 시간 (초)", ge=0)
    services_count: int = Field(..., description="등록된 서비스 수", ge=0)
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="상태 확인 시간")
    
    class Config:
        """Pydantic 설정"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ErrorResponse(BaseModel):
    """
    오류 응답 스키마
    
    Attributes:
        error: 오류 메시지
        detail: 상세 오류 정보
        status_code: HTTP 상태 코드
        timestamp: 오류 발생 시간
    """
    error: str = Field(..., description="오류 메시지")
    detail: Optional[str] = Field(default=None, description="상세 오류 정보")
    status_code: int = Field(..., description="HTTP 상태 코드", ge=400, le=599)
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="오류 발생 시간")
    
    class Config:
        """Pydantic 설정"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
