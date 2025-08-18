# ============================================================================
# 🎨 Cal_boundary Schema Package
# ============================================================================

"""
API 스키마 패키지

요청/응답 데이터 검증을 위한 Pydantic 모델들을 포함합니다.
"""

from .shape_schema import (
    ShapeTypeEnum,
    ShapeCreateRequest,
    ShapeUpdateRequest,
    ShapeResponse,
    ShapeListResponse,
    ShapeSearchRequest,
    ShapeStatsResponse
)

from .arrow_schema import (
    ArrowTypeEnum,
    ArrowCreateRequest,
    ArrowUpdateRequest,
    ArrowResponse,
    ArrowListResponse,
    ArrowSearchRequest,
    ArrowStatsResponse,
    ArrowConnectionRequest,
    ArrowBatchCreateRequest
)

from .canvas_schema import (
    CanvasCreateRequest,
    CanvasUpdateRequest,
    CanvasResponse,
    CanvasListResponse,
    CanvasSearchRequest,
    CanvasStatsResponse,
    CanvasExportRequest,
    CanvasImportRequest,
    CanvasDuplicateRequest,
    CanvasMergeRequest,
    CanvasBulkOperationRequest,
    CanvasTemplateRequest
)

from .cbam_schema import (
    CompanyInfo,
    CBAMProduct,
    ProductionProcess,
    CalculationBoundary,
    EmissionSource,
    SourceStream,
    ReportingPeriod,
    DataAllocation,
    CBAMBoundaryRequest,
    CBAMBoundaryResponse
)

__all__ = [
    # Shape schemas
    "ShapeTypeEnum",
    "ShapeCreateRequest",
    "ShapeUpdateRequest", 
    "ShapeResponse",
    "ShapeListResponse",
    "ShapeSearchRequest",
    "ShapeStatsResponse",
    
    # Arrow schemas
    "ArrowTypeEnum",
    "ArrowCreateRequest",
    "ArrowUpdateRequest",
    "ArrowResponse",
    "ArrowListResponse",
    "ArrowSearchRequest",
    "ArrowStatsResponse",
    "ArrowConnectionRequest",
    "ArrowBatchCreateRequest",
    
    # Canvas schemas
    "CanvasCreateRequest",
    "CanvasUpdateRequest",
    "CanvasResponse",
    "CanvasListResponse",
    "CanvasSearchRequest",
    "CanvasStatsResponse",
    "CanvasExportRequest",
    "CanvasImportRequest",
    "CanvasDuplicateRequest",
    "CanvasMergeRequest",
    "CanvasBulkOperationRequest",
    "CanvasTemplateRequest",
    
    # CBAM schemas
    "CompanyInfo",
    "CBAMProduct",
    "ProductionProcess",
    "CalculationBoundary",
    "EmissionSource",
    "SourceStream",
    "ReportingPeriod",
    "DataAllocation",
    "CBAMBoundaryRequest",
    "CBAMBoundaryResponse"
]
