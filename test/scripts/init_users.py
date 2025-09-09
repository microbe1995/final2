import os
import sys
import uuid
from datetime import datetime

import psycopg2


def get_conn_url() -> str:
    # Prefer env var, fallback to provided Railway URL
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:eQGfytQNhXYAZxsJYlFhYagpJAgstrni@shortline.proxy.rlwy.net:46071/railway",
    )


DDL = r"""
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS countries CASCADE;
DROP TABLE IF EXISTS companies CASCADE;

CREATE TABLE users (
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

CREATE TRIGGER users_set_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
"""


def main() -> int:
    url = get_conn_url()
    print(f"Connecting to: {url}")
    try:
        with psycopg2.connect(url) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                cur.execute(DDL)
                print("Schema initialized: dropped users/countries/companies and created users table.")
        return 0
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())


