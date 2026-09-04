# Astro-Zodiac T1 — Chart Schema

ไฟล์ชุดนี้เป็น **schema-only baseline** ยังไม่แก้ `astro_calc.py`

## Files

- `chart_schema.py` — canonical chart data contract
- `tests/test_chart_schema.py` — contract tests

## Key decision

ทุก engine ต้องใช้ `degree_raw` เป็น canonical 0–360 longitude

ห้ามมี schema หลักที่สลับไปมาระหว่าง:
- `deg_dec`
- `degree_raw`
- `dms`
- `degree_total`

`deg_dec` จาก legacy code จะถูกแปลงเข้า schema กลางใน migration phase

## Next migration

1. เพิ่ม adapter ใน `astro_calc.py`
2. ให้ natal calculation คืน `NormalizedChart`
3. คำนวณ house placement ของดาว
4. สร้าง House Rulers
5. migrate `evidence_engine.py`
6. run regression tests
