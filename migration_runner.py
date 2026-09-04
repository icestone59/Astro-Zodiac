from __future__ import annotations
import os
from pathlib import Path
import psycopg

ROOT = Path(__file__).resolve().parent
MIGRATIONS = ROOT / 'migrations'

def get_database_url() -> str:
    url = os.getenv('DATABASE_URL', '').strip()
    if not url:
        raise RuntimeError('DATABASE_URL is not configured')
    return url

def migrate() -> list[str]:
    files = sorted(MIGRATIONS.glob('*.sql'))
    if not files:
        raise RuntimeError('No SQL migrations found')
    applied: list[str] = []
    with psycopg.connect(get_database_url()) as conn:
        with conn.cursor() as cur:
            cur.execute('CREATE TABLE IF NOT EXISTS schema_migrations (version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW())')
            for path in files:
                version = path.stem
                cur.execute('SELECT 1 FROM schema_migrations WHERE version=%s', (version,))
                if cur.fetchone():
                    continue
                cur.execute(path.read_text(encoding='utf-8'))
                cur.execute('INSERT INTO schema_migrations(version) VALUES (%s)', (version,))
                applied.append(version)
    return applied

if __name__ == '__main__':
    print({'applied': migrate()})
