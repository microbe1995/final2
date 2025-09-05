#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ensure extra columns exist on public.dummy (주문처명, 오더번호, 투입물_단위)."""

import argparse
import asyncio
import os
import sys


async def run(url: str) -> None:
    import asyncpg
    conn = await asyncpg.connect(url)
    try:
        await conn.execute('ALTER TABLE public."dummy" ADD COLUMN IF NOT EXISTS "주문처명" text;')
        await conn.execute('ALTER TABLE public."dummy" ADD COLUMN IF NOT EXISTS "오더번호" integer;')
        await conn.execute('ALTER TABLE public."dummy" ADD COLUMN IF NOT EXISTS "투입물_단위" text;')
        print('OK: ensured columns (주문처명, 오더번호, 투입물_단위)')
    finally:
        await conn.close()


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument('--database-url', default=os.getenv('DATABASE_URL'))
    args = p.parse_args(argv)
    if not args.database_url:
        print('DATABASE_URL required', file=sys.stderr)
        return 2
    asyncio.run(run(args.database_url))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))


