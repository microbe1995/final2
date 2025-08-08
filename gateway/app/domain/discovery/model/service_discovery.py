"""
Service Discovery
"""
import httpx
from typing import Dict, Any, Optional
from .service_type import ServiceType

class ServiceDiscovery:
    def __init__(self, service_type: ServiceType):
        self.service_type = service_type
        self.service_urls = {
            ServiceType.AUTH: "http://localhost:8001",
            ServiceType.USER: "http://user-service:8002",
            ServiceType.CHATBOT: "http://chatbot-service:8002",
            ServiceType.REPORT: "http://report-service:8003",
            ServiceType.CBAM: "http://cbam-service:8004",
            ServiceType.LCA: "http://lca-service:8005",
            ServiceType.MESSAGE: "http://message-service:8006",
        }
    
    async def request(
        self,
        method: str,
        path: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[bytes] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ):
        service_url = self.service_urls.get(self.service_type)
        if not service_url:
            raise ValueError(f"Unknown service type: {self.service_type}")
        
        url = f"{service_url}/{path}"
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                content=body,
                files=files,
                params=params,
                data=data
            )
            return response 