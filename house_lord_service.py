from __future__ import annotations
import json
from typing import Any
from house_lord_schema import HouseLordItem, HouseLordSearchResponse
from postgres_connection import connection

def _row_to_item(row: Any) -> HouseLordItem:
    return HouseLordItem(
        key=row[0], lord_house=row[1], destination_house=row[2],
        title=row[3], bullets=row[4],
    )

def search_house_lord(query: str, limit: int = 12) -> HouseLordSearchResponse:
    q = query.strip()
    if not q:
        return HouseLordSearchResponse(total=0, query=q, items=[])
    pair = None
    import re
    m = re.fullmatch(r"(\d{1,2})in(\d{1,2})", q.lower())
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        if 1 <= a <= 12 and 1 <= b <= 12:
            pair = (a, b)
    with connection() as conn:
        with conn.cursor() as cur:
            if pair:
                cur.execute(
                    """SELECT item_key,lord_house,destination_house,title,bullets
                       FROM house_lord_knowledge
                       WHERE lord_house=%s AND destination_house=%s
                       LIMIT 1""", pair)
            else:
                term = f"%{q}%"
                cur.execute(
                    """SELECT item_key,lord_house,destination_house,title,bullets
                       FROM house_lord_knowledge
                       WHERE title ILIKE %s OR EXISTS (
                         SELECT 1 FROM jsonb_array_elements_text(bullets) b
                         WHERE b ILIKE %s
                       )
                       ORDER BY item_key
                       LIMIT %s""", (term, term, limit))
            rows = cur.fetchall()
    return HouseLordSearchResponse(total=len(rows), query=q, items=[_row_to_item(r) for r in rows])
