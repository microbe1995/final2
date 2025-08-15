"""
서비스 저장소 - 서비스 정보의 데이터 접근 로직
Gateway에서 관리하는 서비스들의 정보를 저장하고 조회
"""
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from app.domain.entity.service_entity import ServiceInfo, ServiceHealth

# 로거 설정
logger = logging.getLogger(__name__)

class ServiceRepository:
    """
    서비스 정보 저장소 클래스
    - 서비스 정보 저장/조회
    - 서비스 상태 관리
    - 헬스 체크 결과 저장
    """
    
    def __init__(self):
        """서비스 저장소 초기화"""
        # 메모리 기반 저장소 (향후 데이터베이스로 확장 가능)
        self._services: Dict[str, ServiceInfo] = {}
        self._health_records: List[ServiceHealth] = []
        
        # 기본 서비스 정보 초기화
        self._initialize_default_services()
    
    def _initialize_default_services(self):
        """기본 서비스 정보 초기화"""
        import os
        
        # Auth Service
        auth_service = ServiceInfo(
            name="auth",
            url=os.getenv("AUTH_SERVICE_URL", "http://localhost:8000"),
            status="unknown",
            version="1.0.0"
        )
        self._services["auth"] = auth_service
        
        # Discovery Service (향후 구현)
        discovery_service = ServiceInfo(
            name="discovery",
            url=os.getenv("DISCOVERY_SERVICE_URL", "http://localhost:8001"),
            status="unknown",
            version="1.0.0"
        )
        self._services["discovery"] = discovery_service
        
        # User Service (향후 구현)
        user_service = ServiceInfo(
            name="user",
            url=os.getenv("USER_SERVICE_URL", "http://localhost:8002"),
            status="unknown",
            version="1.0.0"
        )
        self._services["user"] = user_service
        
        logger.info("✅ 기본 서비스 정보 초기화 완료")
    
    def get_service(self, service_name: str) -> Optional[ServiceInfo]:
        """
        서비스 정보 조회
        
        Args:
            service_name: 서비스명
            
        Returns:
            서비스 정보 (없으면 None)
        """
        return self._services.get(service_name)
    
    def get_all_services(self) -> List[ServiceInfo]:
        """
        모든 서비스 정보 조회
        
        Returns:
            서비스 정보 목록
        """
        return list(self._services.values())
    
    def update_service_status(
        self, 
        service_name: str, 
        status: str, 
        version: Optional[str] = None
    ) -> bool:
        """
        서비스 상태 업데이트
        
        Args:
            service_name: 서비스명
            status: 새로운 상태
            version: 새로운 버전 (선택사항)
            
        Returns:
            업데이트 성공 여부
        """
        if service_name not in self._services:
            logger.warning(f"⚠️  존재하지 않는 서비스: {service_name}")
            return False
        
        service = self._services[service_name]
        service.update_status(status, version)
        logger.info(f"✅ 서비스 상태 업데이트: {service_name} -> {status}")
        return True
    
    def add_health_record(self, health_record: ServiceHealth) -> bool:
        """
        헬스 체크 결과 추가
        
        Args:
            health_record: 헬스 체크 결과
            
        Returns:
            추가 성공 여부
        """
        try:
            self._health_records.append(health_record)
            
            # 서비스 상태도 함께 업데이트
            self.update_service_status(
                health_record.service_name,
                health_record.status,
                health_record.metadata.get("version") if health_record.metadata else None
            )
            
            # 최근 100개 기록만 유지
            if len(self._health_records) > 100:
                self._health_records = self._health_records[-100:]
            
            logger.info(f"✅ 헬스 체크 결과 추가: {health_record.service_name} -> {health_record.status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 헬스 체크 결과 추가 실패: {str(e)}")
            return False
    
    def get_health_records(
        self, 
        service_name: Optional[str] = None, 
        limit: int = 50
    ) -> List[ServiceHealth]:
        """
        헬스 체크 결과 조회
        
        Args:
            service_name: 서비스명 (None이면 모든 서비스)
            limit: 조회할 최대 기록 수
            
        Returns:
            헬스 체크 결과 목록
        """
        records = self._health_records
        
        # 특정 서비스 필터링
        if service_name:
            records = [r for r in records if r.service_name == service_name]
        
        # 최신 순으로 정렬하고 제한
        records.sort(key=lambda x: x.timestamp, reverse=True)
        return records[:limit]
    
    def get_service_status_summary(self) -> Dict[str, Any]:
        """
        서비스 상태 요약 정보 조회
        
        Returns:
            서비스 상태 요약
        """
        total_services = len(self._services)
        healthy_services = sum(1 for s in self._services.values() if s.is_healthy())
        unhealthy_services = sum(1 for s in self._services.values() if s.is_unhealthy())
        error_services = sum(1 for s in self._services.values() if s.is_error())
        
        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": unhealthy_services,
            "error_services": error_services,
            "health_percentage": (healthy_services / total_services * 100) if total_services > 0 else 0,
            "last_update": datetime.utcnow().isoformat()
        }
    
    def register_service(
        self, 
        name: str, 
        url: str, 
        version: Optional[str] = None
    ) -> bool:
        """
        새로운 서비스 등록
        
        Args:
            name: 서비스명
            url: 서비스 URL
            version: 서비스 버전 (선택사항)
            
        Returns:
            등록 성공 여부
        """
        try:
            if name in self._services:
                logger.warning(f"⚠️  이미 존재하는 서비스: {name}")
                return False
            
            service = ServiceInfo(
                name=name,
                url=url,
                status="unknown",
                version=version
            )
            
            self._services[name] = service
            logger.info(f"✅ 새 서비스 등록: {name} -> {url}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 서비스 등록 실패: {str(e)}")
            return False
    
    def unregister_service(self, name: str) -> bool:
        """
        서비스 등록 해제
        
        Args:
            name: 서비스명
            
        Returns:
            해제 성공 여부
        """
        try:
            if name not in self._services:
                logger.warning(f"⚠️  존재하지 않는 서비스: {name}")
                return False
            
            del self._services[name]
            
            # 관련 헬스 체크 기록도 제거
            self._health_records = [r for r in self._health_records if r.service_name != name]
            
            logger.info(f"✅ 서비스 등록 해제: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 서비스 등록 해제 실패: {str(e)}")
            return False
