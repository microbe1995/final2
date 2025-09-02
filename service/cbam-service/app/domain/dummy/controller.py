"""
Dummy 데이터 컨트롤러
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.domain.dummy.service import DummyService
from app.domain.dummy.entity import DummyData
from app.common.database import get_async_db

router = APIRouter(tags=["dummy"])


@router.get("/", response_model=List[DummyData])
async def get_all_dummy_data(db: AsyncSession = Depends(get_async_db)):
    """모든 dummy 데이터 조회"""
    try:
        # 동기 세션으로 변환 (기존 Repository와 호환성)
        from sqlalchemy.orm import Session
        sync_db = Session(db.bind)
        
        service = DummyService(sync_db)
        data = service.get_all_dummy_data()
        
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
    finally:
        if 'sync_db' in locals():
            sync_db.close()


@router.get("/{dummy_id}", response_model=DummyData)
async def get_dummy_data_by_id(dummy_id: int, db: AsyncSession = Depends(get_async_db)):
    """ID로 dummy 데이터 조회"""
    try:
        # 동기 세션으로 변환 (기존 Repository와 호환성)
        from sqlalchemy.orm import Session
        sync_db = Session(db.bind)
        
        service = DummyService(sync_db)
        data = service.get_dummy_data_by_id(dummy_id)
        
        if not data:
            raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다")
        
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"데이터 조회 실패: {str(e)}")
    finally:
        if 'sync_db' in locals():
            sync_db.close()
