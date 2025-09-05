#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Drop column 생산수량_단위 from public.dummy (if exists)."""

import argparse
import asyncio
import os
import sys


async def run(url: str) -> None:
    import asyncpg
    conn = await asyncpg.connect(url)
    try:
        await conn.execute('ALTER TABLE public."dummy" DROP COLUMN IF EXISTS "생산수량_단위";')
        print('OK: column dropped (if existed)')
    finally:
        await conn.close()


def main(argv):
    p = argparse.ArgumentParser()
    p.add_argument('--database-url', default=os.getenv('DATABASE_URL'))
    args = p.parse_args(argv)
    if not args.database_url:
        print('DATABASE_URL is required', file=sys.stderr)
        return 2
    asyncio.run(run(args.database_url))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))


