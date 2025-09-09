#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway PostgreSQL의 users 스키마를 초기화하는 스크립트.

수행 내용(멱등):
- DROP TABLE IF EXISTS users, countries, companies CASCADE
- CREATE TABLE "user" (...)  -- service/auth-service/app/domain/user/user_schema.py 의 Company 모델 기준
- updated_at 자동 갱신 트리거 생성

사용 예:
  python init_users_schema.py --database-url postgresql://...

환경변수 DATABASE_URL 이 설정되어 있으면 --database-url 생략 가능
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Optional


DDL = r"""
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS countries CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

CREATE TABLE IF NOT EXISTS "user" (
  id SERIAL PRIMARY KEY,
  uuid TEXT UNIQUE NOT NULL,
  company_id TEXT UNIQUE NOT NULL,
  hashed_password TEXT NOT NULL,
  "Installation" TEXT NOT NULL,
  "Installation_en" TEXT,
  economic_activity TEXT,
  economic_activity_en TEXT,
  representative TEXT,
  representative_en TEXT,
  email TEXT,
  telephone TEXT,
  street TEXT,
  street_en TEXT,
  number TEXT,
  number_en TEXT,
  postcode TEXT,
  city TEXT,
  city_en TEXT,
  country TEXT,
  country_en TEXT,
  unlocode TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS user_set_updated_at ON "user";
CREATE TRIGGER user_set_updated_at
BEFORE UPDATE ON "user"
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
"""


async def init(database_url: str) -> None:
    import asyncpg  # lazy import

    async def _connect_with_retry(url: str, retries: int = 20, delay: float = 3.0):
        last_err: Optional[Exception] = None
        for _ in range(retries):
            try:
                return await asyncpg.connect(url)
            except asyncpg.TooManyConnectionsError as e:
                last_err = e
                await asyncio.sleep(delay)
            except Exception as e:
                last_err = e
                await asyncio.sleep(delay)
        if last_err:
            raise last_err

    conn: Optional["asyncpg.Connection"] = None
    try:
        conn = await _connect_with_retry(database_url)
        async with conn.transaction():
            await conn.execute(DDL)
    finally:
        if conn is not None:
            await conn.close()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description='Initialize users schema (idempotent).')
    parser.add_argument('--database-url', default=os.getenv('DATABASE_URL'), help='PostgreSQL URL')
    args = parser.parse_args(argv)

    if not args.database_url:
        print('ERROR: DATABASE_URL not provided or set in env', file=sys.stderr)
        return 2

    asyncio.run(init(args.database_url))
    print('OK: users schema initialized successfully')
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))


