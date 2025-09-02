#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔧 Dummy 테이블 스키마 업데이트 스크립트
생산수량, 수량 컬럼을 numeric에서 integer로 변경
"""

import os
import asyncio
import asyncpg
import logging
from typing import Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DummySchemaUpdater:
    """Dummy 테이블 스키마 업데이트 클래스"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.pool: Optional[asyncpg.Pool] = None
    
    async def initialize(self):
        """데이터베이스 연결 풀 초기화"""
        if not self.database_url:
            logger.error("❌ DATABASE_URL 환경변수가 설정되지 않았습니다.")
            return False
        
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=1,
                max_size=5,
                command_timeout=60
            )
            logger.info("✅ 데이터베이스 연결 성공")
            return True
        except Exception as e:
            logger.error(f"❌ 데이터베이스 연결 실패: {e}")
            return False
    
    async def backup_table(self):
        """기존 테이블 백업"""
        try:
            # 백업 테이블이 이미 존재하는지 확인
            exists = await self.pool.fetchval("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'dummy_backup'
                );
            """)
            
            if exists:
                logger.info("⚠️ dummy_backup 테이블이 이미 존재합니다. 삭제 후 재생성합니다.")
                await self.pool.execute("DROP TABLE dummy_backup")
            
            # 백업 테이블 생성
            await self.pool.execute("CREATE TABLE dummy_backup AS SELECT * FROM dummy")
            count = await self.pool.fetchval("SELECT COUNT(*) FROM dummy_backup")
            logger.info(f"✅ 테이블 백업 완료: {count}개 행")
            return True
            
        except Exception as e:
            logger.error(f"❌ 테이블 백업 실패: {e}")
            return False
    
    async def update_schema(self):
        """스키마 업데이트 실행"""
        try:
            # 1. 생산수량 컬럼을 integer로 변경
            logger.info("🔄 생산수량 컬럼을 integer로 변경 중...")
            await self.pool.execute("""
                ALTER TABLE dummy 
                ALTER COLUMN 생산수량 TYPE integer 
                USING ROUND(생산수량::numeric)
            """)
            logger.info("✅ 생산수량 컬럼 변경 완료")
            
            # 2. 수량 컬럼을 integer로 변경
            logger.info("🔄 수량 컬럼을 integer로 변경 중...")
            await self.pool.execute("""
                ALTER TABLE dummy 
                ALTER COLUMN 수량 TYPE integer 
                USING ROUND(수량::numeric)
            """)
            logger.info("✅ 수량 컬럼 변경 완료")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 스키마 업데이트 실패: {e}")
            return False
    
    async def verify_schema(self):
        """스키마 변경 확인"""
        try:
            # 컬럼 타입 확인
            columns = await self.pool.fetch("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'dummy' 
                AND column_name IN ('생산수량', '수량')
                ORDER BY column_name
            """)
            
            logger.info("📊 스키마 변경 결과:")
            for col in columns:
                logger.info(f"  - {col['column_name']}: {col['data_type']} (NULL: {col['is_nullable']})")
            
            # 데이터 샘플 확인
            sample_data = await self.pool.fetch("SELECT id, 생산수량, 수량 FROM dummy LIMIT 3")
            logger.info("📋 데이터 샘플:")
            for row in sample_data:
                logger.info(f"  - ID {row['id']}: 생산수량={row['생산수량']} ({type(row['생산수량'])}), 수량={row['수량']} ({type(row['수량'])})")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 스키마 확인 실패: {e}")
            return False
    
    async def cleanup_backup(self):
        """백업 테이블 정리"""
        try:
            await self.pool.execute("DROP TABLE dummy_backup")
            logger.info("✅ 백업 테이블 정리 완료")
            return True
        except Exception as e:
            logger.error(f"❌ 백업 테이블 정리 실패: {e}")
            return False
    
    async def run_update(self):
        """전체 업데이트 프로세스 실행"""
        try:
            logger.info("🚀 Dummy 테이블 스키마 업데이트 시작")
            
            # 1. 초기화
            if not await self.initialize():
                return False
            
            # 2. 백업
            if not await self.backup_table():
                return False
            
            # 3. 스키마 업데이트
            if not await self.update_schema():
                logger.error("❌ 스키마 업데이트 실패. 백업 테이블에서 복원이 필요할 수 있습니다.")
                return False
            
            # 4. 확인
            if not await self.verify_schema():
                return False
            
            # 5. 백업 정리 (선택사항)
            # await self.cleanup_backup()
            
            logger.info("🎉 스키마 업데이트 완료!")
            return True
            
        except Exception as e:
            logger.error(f"❌ 업데이트 프로세스 실패: {e}")
            return False
        finally:
            if self.pool:
                await self.pool.close()

async def main():
    """메인 함수"""
    updater = DummySchemaUpdater()
    success = await updater.run_update()
    
    if success:
        logger.info("✅ 스키마 업데이트가 성공적으로 완료되었습니다.")
        logger.info("💡 백업 테이블(dummy_backup)은 안전을 위해 유지됩니다.")
        logger.info("💡 필요시 'DROP TABLE dummy_backup;' 명령으로 삭제할 수 있습니다.")
    else:
        logger.error("❌ 스키마 업데이트에 실패했습니다.")
        logger.error("💡 백업 테이블(dummy_backup)에서 데이터를 복원할 수 있습니다.")

if __name__ == "__main__":
    asyncio.run(main())
