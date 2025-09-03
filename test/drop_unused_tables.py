#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
운영에 불필요한 테이블 정리 스크립트

대상
- public.dummy_backup
- public.dummy_data

특징
- 존재 여부 확인 후에만 DROP
- 트랜잭션으로 안전하게 처리
- DATABASE_URL 또는 --url로 접속
"""

import asyncio
import os
import sys
import argparse

try:
    import asyncpg
except ImportError:
    print("asyncpg가 필요합니다. 설치: pip install asyncpg", file=sys.stderr)
    raise


TABLES_TO_DROP = [
    ("public", "dummy_backup"),
    ("public", "dummy_data"),
]


async def table_exists(conn: "asyncpg.Connection", schema: str, table: str) -> bool:
    return await conn.fetchval(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = $1 AND table_name = $2
        );
        """,
        schema,
        table,
    )


async def drop_table(conn: "asyncpg.Connection", schema: str, table: str) -> bool:
    if not await table_exists(conn, schema, table):
        print(f"⚠️ {schema}.{table} 테이블이 존재하지 않습니다. 건너뜀")
        return False

    await conn.execute(f'DROP TABLE IF EXISTS {schema}.{table} CASCADE;')
    print(f"✅ 드롭 완료: {schema}.{table}")
    return True


async def run(url: str) -> None:
    conn = await asyncpg.connect(url)
    try:
        tr = conn.transaction()
        await tr.start()
        try:
            any_dropped = False
            for schema, table in TABLES_TO_DROP:
                dropped = await drop_table(conn, schema, table)
                any_dropped = any_dropped or dropped
            await tr.commit()
            if any_dropped:
                print("🎯 선택된 테이블 드롭이 완료되었습니다.")
            else:
                print("ℹ️ 드롭할 테이블이 없었습니다.")
        except Exception:
            await tr.rollback()
            raise
    finally:
        await conn.close()


def parse_args(argv):
    parser = argparse.ArgumentParser(description="불필요 테이블 드롭 스크립트")
    parser.add_argument("--url", dest="url", help="PostgreSQL 연결 문자열")
    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv)
    url = args.url or os.environ.get("DATABASE_URL")
    if not url:
        print("DATABASE_URL 환경변수 또는 --url 인자를 제공하세요.", file=sys.stderr)
        sys.exit(1)
    asyncio.run(run(url))


if __name__ == "__main__":
    main(sys.argv[1:])


