"""
서비스 엔티티 - 서비스 정보를 담는 데이터 모델
Gateway에서 관리하는 서비스들의 정보를 표현
"""
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

class ServiceInfo(BaseModel):
    """
    서비스 정보 엔티티
    
    Attributes:
        name: 서비스명
        url: 서비스 URL
        status: 서비스 상태 (healthy, unhealthy, error)
        last_check: 마지막 헬스 체크 시간
        version: 서비스 버전
        metadata: 추가 메타데이터
    """
    name: str = Field(..., description="서비스명")
    url: str = Field(..., description="서비스 URL")
    status: str = Field(default="unknown", description="서비스 상태")
    last_check: Optional[datetime] = Field(default=None, description="마지막 헬스 체크 시간")
    version: Optional[str] = Field(default=None, description="서비스 버전")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="추가 메타데이터")
    
    class Config:
        """Pydantic 설정"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def is_healthy(self) -> bool:
        """서비스가 정상 상태인지 확인"""
        return self.status == "healthy"
    
    def is_unhealthy(self) -> bool:
        """서비스가 비정상 상태인지 확인"""
        return self.status == "unhealthy"
    
    def is_error(self) -> bool:
        """서비스에 오류가 있는지 확인"""
        return self.status == "error"
    
    def update_status(self, status: str, version: Optional[str] = None):
        """
        서비스 상태 업데이트
        
        Args:
            status: 새로운 상태
            version: 새로운 버전 (선택사항)
        """
        self.status = status
        self.last_check = datetime.utcnow()
        if version:
            self.version = version
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "name": self.name,
            "url": self.url,
            "status": self.status,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "version": self.version,
            "metadata": self.metadata
        }

class ServiceHealth(BaseModel):
    """
    서비스 헬스 체크 결과 엔티티
    
    Attributes:
        service_name: 서비스명
        status: 헬스 체크 상태
        response_time: 응답 시간 (밀리초)
        status_code: HTTP 상태 코드
        error_message: 오류 메시지 (있는 경우)
        timestamp: 체크 시간
    """
    service_name: str = Field(..., description="서비스명")
    status: str = Field(..., description="헬스 체크 상태")
    response_time: Optional[float] = Field(default=None, description="응답 시간 (밀리초)")
    status_code: Optional[int] = Field(default=None, description="HTTP 상태 코드")
    error_message: Optional[str] = Field(default=None, description="오류 메시지")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="체크 시간")
    
    class Config:
        """Pydantic 설정"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def is_success(self) -> bool:
        """헬스 체크가 성공했는지 확인"""
        return self.status == "healthy" and self.status_code == 200
    
    def to_dict(self) -> Dict[str, Any]:
        """엔티티를 딕셔너리로 변환"""
        return {
            "service_name": self.service_name,
            "status": self.status,
            "response_time": self.response_time,
            "status_code": self.status_code,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat()
        }
