#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PostgreSQL 데이터베이스 스키마 인벤토리 스크립트

용도
- DATABASE_URL 또는 --url 인자로 전달된 연결 문자열로 접속해 스키마/테이블/컬럼/키/인덱스를 Markdown으로 출력

사용 예
- 환경변수 사용:  setx DATABASE_URL "postgresql://user:pass@host:port/db" 후 실행
- URL 직접:      python inspect_db_schema.py --url postgresql://...
- 파일 저장:      python inspect_db_schema.py --out schema.md

주의
- 읽기 전용 조회만 수행
"""

import asyncio
import os
import sys
import argparse
from typing import Dict, List, Any, Tuple

try:
    import asyncpg
except ImportError:  # 친절한 메시지 제공
    print("asyncpg가 필요합니다. 설치: pip install asyncpg", file=sys.stderr)
    raise


EXCLUDED_SCHEMAS = {
    "pg_catalog",
    "information_schema",
    "pg_toast",
}


async def fetch_schemas(conn: "asyncpg.Connection") -> List[str]:
    rows = await conn.fetch(
        """
        SELECT nspname AS schema_name
        FROM pg_namespace
        WHERE nspname NOT IN (SELECT unnest($1::text[]))
        ORDER BY nspname
        """,
        list(EXCLUDED_SCHEMAS),
    )
    return [r["schema_name"] for r in rows]


async def fetch_tables(conn: "asyncpg.Connection", schema: str) -> List[Dict[str, Any]]:
    rows = await conn.fetch(
        """
        SELECT
            c.relname                          AS table_name,
            c.relkind                          AS relkind,
            pg_total_relation_size(c.oid)      AS total_bytes
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = $1
          AND c.relkind IN ('r','v','m','f','p')  -- table, view, matview, foreign, partitioned
        ORDER BY c.relname
        """,
        schema,
    )
    result: List[Dict[str, Any]] = []
    for r in rows:
        result.append(
            {
                "table_name": r["table_name"],
                "relkind": r["relkind"],
                "total_bytes": int(r["total_bytes"] or 0),
            }
        )
    return result


async def fetch_columns(conn: "asyncpg.Connection", schema: str, table: str) -> List[Dict[str, Any]]:
    rows = await conn.fetch(
        """
        SELECT
            column_name,
            data_type,
            is_nullable,
            column_default,
            ordinal_position
        FROM information_schema.columns
        WHERE table_schema = $1 AND table_name = $2
        ORDER BY ordinal_position
        """,
        schema,
        table,
    )
    return [
        {
            "column_name": r["column_name"],
            "data_type": r["data_type"],
            "is_nullable": r["is_nullable"],
            "column_default": r["column_default"],
            "ordinal_position": int(r["ordinal_position"]),
        }
        for r in rows
    ]


async def fetch_primary_keys(conn: "asyncpg.Connection", schema: str, table: str) -> List[str]:
    rows = await conn.fetch(
        """
        SELECT a.attname AS column_name
        FROM pg_index i
        JOIN pg_class c ON c.oid = i.indrelid
        JOIN pg_namespace n ON n.oid = c.relnamespace
        JOIN pg_attribute a ON a.attrelid = c.oid AND a.attnum = ANY(i.indkey)
        WHERE n.nspname = $1 AND c.relname = $2 AND i.indisprimary
        ORDER BY a.attnum
        """,
        schema,
        table,
    )
    return [r["column_name"] for r in rows]


async def fetch_foreign_keys(
    conn: "asyncpg.Connection", schema: str, table: str
) -> List[Dict[str, Any]]:
    rows = await conn.fetch(
        """
        SELECT
            tc.constraint_name,
            kcu.column_name,
            ccu.table_schema AS foreign_table_schema,
            ccu.table_name   AS foreign_table_name,
            ccu.column_name  AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
         AND tc.table_schema   = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
         AND ccu.table_schema   = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
          AND tc.table_schema    = $1
          AND tc.table_name      = $2
        ORDER BY tc.constraint_name, kcu.ordinal_position
        """,
        schema,
        table,
    )
    fks: Dict[str, Dict[str, Any]] = {}
    for r in rows:
        name = r["constraint_name"]
        if name not in fks:
            fks[name] = {
                "name": name,
                "columns": [],
                "ref": (
                    r["foreign_table_schema"],
                    r["foreign_table_name"],
                    r["foreign_column_name"],
                ),
            }
        fks[name]["columns"].append(r["column_name"])
    return list(fks.values())


async def fetch_indexes(conn: "asyncpg.Connection", schema: str, table: str) -> List[Dict[str, Any]]:
    rows = await conn.fetch(
        """
        SELECT
            ci.relname AS index_name,
            i.indisunique AS is_unique,
            array_agg(a.attname ORDER BY a.attnum) AS columns
        FROM pg_index i
        JOIN pg_class ct ON ct.oid = i.indrelid
        JOIN pg_class ci ON ci.oid = i.indexrelid
        JOIN pg_namespace n ON n.oid = ct.relnamespace
        JOIN LATERAL unnest(i.indkey) WITH ORDINALITY AS k(attnum, ord) ON true
        JOIN pg_attribute a ON a.attrelid = ct.oid AND a.attnum = k.attnum
        WHERE n.nspname = $1 AND ct.relname = $2
        GROUP BY ci.relname, i.indisunique
        ORDER BY ci.relname
        """,
        schema,
        table,
    )
    result: List[Dict[str, Any]] = []
    for r in rows:
        cols = list(r["columns"]) if r["columns"] is not None else []
        result.append(
            {
                "index_name": r["index_name"],
                "is_unique": bool(r["is_unique"]),
                "columns": cols,
            }
        )
    return result


def format_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for u in units:
        if size < 1024.0:
            return f"{size:.1f}{u}"
        size /= 1024.0
    return f"{size:.1f}PB"


async def inventory_database(conn: "asyncpg.Connection") -> str:
    md_lines: List[str] = []
    schemas = await fetch_schemas(conn)
    if not schemas:
        md_lines.append("## 스키마 없음")
        return "\n".join(md_lines)

    for schema in schemas:
        md_lines.append(f"## 스키마: {schema}")
        tables = await fetch_tables(conn, schema)
        if not tables:
            md_lines.append("- (테이블 없음)")
            md_lines.append("")
            continue

        for t in tables:
            tname = t["table_name"]
            relkind = t["relkind"]
            size_fmt = format_size(t["total_bytes"]) if t["total_bytes"] else "0B"
            kind_label = {
                "r": "table",
                "v": "view",
                "m": "matview",
                "f": "foreign",
                "p": "partitioned",
            }.get(relkind, relkind)

            md_lines.append(f"### {schema}.{tname} ({kind_label}, {size_fmt})")

            # Columns
            cols = await fetch_columns(conn, schema, tname)
            if cols:
                md_lines.append("- 컬럼:")
                for c in cols:
                    nullable = "NULL" if c["is_nullable"] == "YES" else "NOT NULL"
                    default = f" default={c['column_default']}" if c["column_default"] else ""
                    md_lines.append(
                        f"  - {c['column_name']}: {c['data_type']} ({nullable}){default}"
                    )
            else:
                md_lines.append("- 컬럼: (없음)")

            # Primary Keys
            pks = await fetch_primary_keys(conn, schema, tname)
            if pks:
                md_lines.append(f"- 기본키: {', '.join(pks)}")
            else:
                md_lines.append("- 기본키: (없음)")

            # Foreign Keys
            fks = await fetch_foreign_keys(conn, schema, tname)
            if fks:
                md_lines.append("- 외래키:")
                for fk in fks:
                    ref_schema, ref_table, ref_col = fk["ref"]
                    md_lines.append(
                        f"  - {fk['name']}: ({', '.join(fk['columns'])}) -> {ref_schema}.{ref_table}({ref_col})"
                    )
            else:
                md_lines.append("- 외래키: (없음)")

            # Indexes
            idxs = await fetch_indexes(conn, schema, tname)
            if idxs:
                md_lines.append("- 인덱스:")
                for idx in idxs:
                    uniq = "UNIQUE" if idx["is_unique"] else "NONUNIQUE"
                    cols = ", ".join(idx["columns"]) if idx["columns"] else ""
                    md_lines.append(f"  - {idx['index_name']} ({uniq}) on ({cols})")
            else:
                md_lines.append("- 인덱스: (없음)")

            md_lines.append("")

    return "\n".join(md_lines)


async def run(url: str, out_path: str | None) -> None:
    conn = await asyncpg.connect(url)
    try:
        md = await inventory_database(conn)
    finally:
        await conn.close()

    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(md)
        print(f"✅ 스키마 인벤토리를 '{out_path}'에 저장했습니다.")
    else:
        print(md)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PostgreSQL 스키마 인벤토리 출력")
    parser.add_argument(
        "--url",
        dest="url",
        help="PostgreSQL 연결 문자열(postgresql://user:pass@host:port/db)",
    )
    parser.add_argument(
        "--out",
        dest="out",
        help="Markdown 출력 파일 경로 (지정하지 않으면 표준출력)",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> None:
    args = parse_args(argv)
    url = args.url or os.environ.get("DATABASE_URL")
    if not url:
        print(
            "DATABASE_URL 환경변수 또는 --url 인자를 제공하세요.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Windows PowerShell에서도 잘 보이도록 UTF-8 강제
    try:
        import colorama  # noqa: F401
    except Exception:
        pass

    asyncio.run(run(url, args.out))


if __name__ == "__main__":
    main(sys.argv[1:])


