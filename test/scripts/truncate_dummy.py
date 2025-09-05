#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Railway PostgreSQL public.dummy 테이블 전체 비우기 스크립트 (멱등)

사용:
  $env:DATABASE_URL='postgresql://...'; python truncate_dummy.py
  또는
  python truncate_dummy.py --database-url postgresql://...
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from typing import Optional


async def truncate_dummy(database_url: str) -> None:
    import asyncpg  # lazy import

    conn: Optional["asyncpg.Connection"] = None
    try:
        conn = await asyncpg.connect(database_url)
        before = await conn.fetchval('SELECT COUNT(*) FROM public."dummy";')
        await conn.execute('TRUNCATE TABLE public."dummy" RESTART IDENTITY;')
        after = await conn.fetchval('SELECT COUNT(*) FROM public."dummy";')
        print(f'OK: truncated dummy (before={before}, after={after})')
    finally:
        if conn is not None:
            await conn.close()


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description='Truncate public.dummy table (restart identity).')
    parser.add_argument('--database-url', default=os.getenv('DATABASE_URL'), help='PostgreSQL URL')
    args = parser.parse_args(argv)

    if not args.database_url:
        print('ERROR: DATABASE_URL not provided or set in env', file=sys.stderr)
        return 2

    asyncio.run(truncate_dummy(args.database_url))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))


