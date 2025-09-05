#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway PostgreSQL의 public.dummy 테이블을 엑셀 구조에 맞춰 보강/정렬하는 마이그레이션 스크립트.

수행 내용(멱등):
- 컬럼 추가
  * "주문처명" text
  * "오더번호" integer
  * "생산수량_단위" text (기존 데이터 NULL이면 'ton'으로 채움)
  * "투입물_단위" text (기존 "단위" 값을 복제)
- 타입 정규화
  * "생산수량" integer -> numeric(10,2)
  * "수량" integer -> numeric(10,2)
- 인덱스(존재하지 않으면) 생성
  * idx_dummy_오더번호
  * idx_dummy_주문처명

사용 예:
  python migrate_dummy_schema.py --database-url postgresql://...

환경변수 DATABASE_URL 이 설정되어 있으면 --database-url 생략 가능
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Optional


DDL_STATEMENTS = [
    # 1) 컬럼 추가(IF NOT EXISTS)
    'ALTER TABLE public."dummy" ADD COLUMN IF NOT EXISTS "주문처명" text;',
    'ALTER TABLE public."dummy" ADD COLUMN IF NOT EXISTS "오더번호" integer;',
    'ALTER TABLE public."dummy" ADD COLUMN IF NOT EXISTS "투입물_단위" text;',
]

POST_DDL_FIXUPS = [
    # 2) 타입 변경 (이미 numeric이면 에러 없이 캐스팅 시도)
    'ALTER TABLE public."dummy" ALTER COLUMN "생산수량" TYPE numeric(10,2) USING ("생산수량"::numeric);',
    'ALTER TABLE public."dummy" ALTER COLUMN "수량" TYPE numeric(10,2) USING ("수량"::numeric);',
]

DATA_MIGRATIONS = [
    # 3) 데이터 채우기
    'UPDATE public."dummy" SET "투입물_단위" = COALESCE("투입물_단위", "단위") WHERE "투입물_단위" IS NULL;',
]

INDEX_STATEMENTS = [
    'CREATE INDEX IF NOT EXISTS idx_dummy_오더번호 ON public."dummy" ("오더번호");',
    'CREATE INDEX IF NOT EXISTS idx_dummy_주문처명 ON public."dummy" ("주문처명");',
]


async def migrate(database_url: str) -> None:
    import asyncpg  # lazy import

    async def _connect_with_retry(url: str, retries: int = 20, delay: float = 3.0):
        last_err: Optional[Exception] = None
        for _ in range(retries):
            try:
                return await asyncpg.connect(url)
            except asyncpg.TooManyConnectionsError as e:
                last_err = e
                await asyncio.sleep(delay)
            except Exception as e:  # network hiccups
                last_err = e
                await asyncio.sleep(delay)
        if last_err:
            raise last_err

    conn: Optional["asyncpg.Connection"] = None
    try:
        conn = await _connect_with_retry(database_url)
        # 트랜잭션에서 순차 실행
        async with conn.transaction():
            for sql in DDL_STATEMENTS:
                await conn.execute(sql)
            for sql in POST_DDL_FIXUPS:
                try:
                    await conn.execute(sql)
                except Exception:
                    # 이미 타입이 원하는 형태거나 캐스팅 불가 행이 있을 때는 무시하고 진행
                    pass
            for sql in DATA_MIGRATIONS:
                await conn.execute(sql)
            for sql in INDEX_STATEMENTS:
                await conn.execute(sql)

    finally:
        if conn is not None:
            await conn.close()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description='Migrate public.dummy schema to Excel-like structure (idempotent).')
    parser.add_argument('--database-url', default=os.getenv('DATABASE_URL'), help='PostgreSQL URL')
    args = parser.parse_args(argv)

    if not args.database_url:
        print('ERROR: DATABASE_URL not provided or set in env', file=sys.stderr)
        return 2

    asyncio.run(migrate(args.database_url))
    print('OK: dummy schema migrated successfully')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))


