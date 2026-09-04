# ASTRO-ZODIAC — 1,999 ASTRO PROFESSIONAL UX v1

Status: Milestone / Baseline v1

## 1. Product Role

1,999 บาท = **Astro Professional**

กลุ่มเป้าหมาย:
- ผู้ศึกษาโหราศาสตร์
- Beginner Astrologer
- Aspiring Astrologer
- ผู้ที่ต้องการระบบช่วยวิเคราะห์ดวงอย่างเป็นระบบ

ไม่ใช่ Product สำหรับลูกค้าทั่วไปที่ต้องการ Personal Action Plan

Core Question:

> “ระบบช่วยฉันวิเคราะห์ดวงอย่างเป็นระบบ พร้อมเห็น Evidence ที่อยู่เบื้องหลังการตีความได้อย่างไร?”

---

# 2. Product Promise

เมื่อจบการใช้งาน ผู้ใช้ควรสามารถ:

1. สร้าง/จัดเก็บ Chart ของ Client
2. ตรวจ Natal Chart ได้อย่างเป็นระบบ
3. ตรวจ House + House Ruler ได้
4. ตรวจ Aspect ได้
5. ตรวจ Uranian / 90° / Midpoint ได้
6. ตรวจ Transit / Timing ได้
7. เห็น Evidence ที่ระบบใช้
8. ขอ AI ช่วย Interpretation
9. สร้าง Deep Report
10. Export รายงานให้ Client

Product ไม่ควรขายว่า:

> “AI ทำนายแม่นกว่านักโหร”

แต่ขายว่า:

> **“AI Astrology Analysis Assistant ที่ช่วยจัดระบบข้อมูลและ Evidence ก่อนการตีความ”**

---

# 3. Professional User Journey

```text
Professional Landing
        ↓
Create Account / Login
        ↓
Professional Dashboard
        ↓
Create Client
        ↓
Birth Data
        ↓
Chart Calculation
        ↓
Natal Analysis
        ↓
House Ruler
        ↓
Aspect
        ↓
Uranian / Midpoint
        ↓
Pattern Analysis
        ↓
Evidence Matrix
        ↓
Transit / Timing
        ↓
AI Interpretation
        ↓
Deep Report
        ↓
Review / Edit
        ↓
Export
```

---

# 4. Screen 01 — Professional Landing

## Headline

> วิเคราะห์ดวงอย่างเป็นระบบ ไม่ต้องไล่จำทุกจุดเอง

## Supporting

> Astro-Zodiac ช่วยคำนวณ จัดโครงสร้าง และเชื่อม Evidence ทางโหราศาสตร์ เพื่อให้คุณใช้เวลามากขึ้นกับการตีความ

## CTA

> เริ่มใช้งาน Astro Professional

Secondary:

> ดูตัวอย่าง Analysis

---

# 5. Screen 02 — Professional Dashboard

Dashboard ต้องเน้น “งานของนักโหร”

แสดง:

```text
MY CLIENTS
-----------------
Client A
Client B
Client C

RECENT CHARTS
-----------------
Recent Chart 1
Recent Chart 2

RECENT REPORTS
-----------------
Report 1
Report 2
```

Actions:

- New Client
- Open Client
- Create Report
- Search Client

---

# 6. Screen 03 — Client Management

## Client Record

```text
Client Name
Birth Date
Birth Time
Birth Place
Timezone
Notes
Charts
Reports
History
```

## Requirement

แยก Client Data ออกจาก User Account

ผู้ใช้คนเดียวอาจมี Client หลายคน

---

# 7. Screen 04 — Birth Data

Input:

- Date
- Time
- Place
- Timezone
- Birth Time Accuracy

Birth Time Accuracy:

```text
Exact
Approximate
Unknown
```

สำคัญ:
ระบบต้องบันทึก accuracy เพราะ House/ASC/MC confidence อาจขึ้นกับความแม่นของเวลาเกิด

หากเวลาเกิดไม่แน่นอน:
> ห้ามแสดง House-based analysis ว่าแม่นยำเท่ากับ Exact Time โดยไม่มีคำเตือน

---

# 8. Screen 05 — Chart Overview

แสดง:

- Natal Wheel
- Planets
- Signs
- Houses
- ASC
- MC
- Retrograde
- Chiron
- Node

และ:

> **Open Evidence**

เพื่อเข้าสู่รายละเอียด

---

# 9. Screen 06 — House Ruler Analysis

นี่คือ Feature สำคัญ

ตัวอย่าง:

```text
HOUSE 10
Cusp Sign: X
Ruler: Planet Y

Planet Y
Sign: Z
House: 6

Major Aspects:
- ...
- ...

Interpretive Links:
10 → 6
```

ระบบต้องสามารถกดดู chain:

```text
House
↓
Cusp Sign
↓
Ruler
↓
Ruler Sign
↓
Ruler House
↓
Ruler Aspects
```

---

# 10. Screen 07 — Aspect Analysis

แสดง:

- Planet A
- Aspect
- Planet B
- Orb
- Applying / Separating (เมื่อมี calculation support)
- Relevant Houses
- Relevant Rulers

ตัวอย่าง:

```text
Mars □ Saturn
Orb: 1°12'

Mars:
House 9

Saturn:
House 12
```

---

# 11. Screen 08 — Uranian Analysis

## 90° Dial

แสดงตำแหน่งตาม 90° framework

## Midpoint

```text
A/B = C
```

## Planetary Picture

แสดง:

```text
Picture
Factors
Orb
Type
```

### User Controls

- Orb settings
- Factor selection
- Include/Exclude factors
- Exact / Wide

ต้องแสดง clearly ว่าการตั้งค่าใดมีผลต่อผลลัพธ์

---

# 12. Screen 09 — Pattern Analysis

Pattern Engine ใช้ Pattern Library กลางชุดเดียวกับ User Products

แต่ Professional เห็นรายละเอียดมากกว่า:

```text
Pattern
↓
Western Signals
↓
House/Ruler
↓
Aspects
↓
Uranian Signals
↓
Midpoint / Picture
↓
Transit if relevant
↓
Evidence
```

---

# 13. Screen 10 — Evidence Matrix

นี่ควรเป็นหนึ่งใน Feature เด่นที่สุด

ตัวอย่าง:

| Pattern | Evidence | Source | Strength |
|---|---|---|---|
| Procrastination | Mars/Saturn | Uranian | Strong |
| Procrastination | House 6 Ruler → Saturn | Western | Medium |
| Procrastination | MC-related signal | Western/Uranian | Medium |

User สามารถกดแต่ละ row เพื่อดูรายละเอียด

---

# 14. Evidence Detail

เมื่อกด Evidence:

```text
WHAT
Pattern: Procrastination

WHY
Mars/Saturn structure

WHERE
Natal / House / Aspect

ORBIT
0°xx'

RELATED FACTORS
...

INTERPRETIVE ROLE
Primary / Supporting
```

สำคัญ:

> Evidence ≠ scientific proof

เป็น Evidence ภายในกรอบระบบโหราศาสตร์ที่ใช้เป็นฐานสำหรับการตีความ

---

# 15. Screen 11 — Transit / Timing

Professional สามารถเลือก:

- Current Transit
- Date Range
- Planet
- Natal Target
- Orb

Flow:

```text
Transit Planet
↓
Natal Factor
↓
Aspect
↓
Orb
↓
Activation Window
↓
Relevant House / Ruler
```

ไม่ให้ AI คำนวณเอง

---

# 16. Screen 12 — Interpretation Workspace

หน้าหลักสำหรับ AI/นักโหร

แบ่ง:

### LEFT
Chart / Evidence

### CENTER
Interpretation

### RIGHT
Selected Factors / Notes

ตัวอย่าง:

```text
SELECTED EVIDENCE
✓ House 10 Ruler
✓ Mars/Saturn
✓ MC midpoint
```

AI ใช้เฉพาะ Selected Evidence + Relevant Chart Context

---

# 17. AI Interpretation

AI ทำ:

- สรุป Evidence
- เชื่อมปัจจัย
- เขียน Interpretation
- อธิบาย Alternative Reading
- เขียน report sections

AI ห้าม:

- เปลี่ยน Chart
- สร้าง factor ที่ไม่มี
- เติม missing degree
- invent aspect
- claim scientific proof
- hide uncertainty

---

# 18. Ask AI

Professional User สามารถถาม:

> “ทำไมคุณจึงมองว่า Career เป็น Theme หลัก?”

AI ต้องตอบ:

```text
Because:

1. House 10...
2. Ruler...
3. Aspect...
4. Uranian...
```

พร้อมแสดง Evidence ที่เกี่ยวข้อง

---

# 19. Professional AI Context

AI Context:

```text
Chart
+
User Selected Evidence
+
Pattern
+
House/Ruler
+
Aspect
+
Uranian
+
Transit
+
Astrologer Notes
```

ไม่ต้องส่งข้อมูลทั้ง Database

---

# 20. Deep Report

Report Structure:

### 1. Chart Overview
### 2. Core Patterns
### 3. Identity
### 4. Career
### 5. Money
### 6. Relationship
### 7. Strengths
### 8. Blind Spots
### 9. Uranian Deep Analysis
### 10. Transit / Timing
### 11. Evidence Summary
### 12. Astrologer's Notes
### 13. Final Interpretation

Professional User ต้องสามารถ:
- เลือก section
- เรียง section
- แก้ข้อความ
- ซ่อน section
- เพิ่ม Note

---

# 21. Report Editing

AI ไม่ควรเป็น final authority

User ต้องแก้:

```text
AI Draft
↓
Edit
↓
Approve
↓
Final Report
```

และต้องแยก:

> AI Generated

กับ

> Astrologer Edited

เพื่อให้ Professional User ควบคุมผลลัพธ์สุดท้าย

---

# 22. Report Export

MVP:
- PDF
- Print

Future:
- DOCX
- Branded report
- Logo
- Professional cover
- Client-facing version

---

# 23. Professional vs General User

Professional ได้:

```text
DEEP TECHNICAL EVIDENCE
+
CONFIGURABLE CHART ANALYSIS
+
CLIENT MANAGEMENT
+
EDITABLE REPORT
+
EXPORT
```

General User ไม่ควรเห็น technical layer นี้ทั้งหมด

---

# 24. AI Question / Usage Model

สำหรับ MVP 1,999 ไม่ควรสื่อเป็น “ดูดวงได้ X คำถาม”

ใช้:

> **Professional AI Analysis Usage**

เพราะ User ต้องการทำงานจริงมากกว่าการสนทนา

ระบบสามารถเก็บ usage เป็น backend quota แต่ UX ควรแสดงเป็น:

> Analysis usage remaining

รายละเอียด quota สามารถกำหนดหลังจากวัดต้นทุนจริง

---

# 25. Professional Analytics

เก็บ:

```text
client_created
chart_calculated
evidence_viewed
house_ruler_viewed
aspect_viewed
uranian_viewed
transit_viewed
ai_interpretation_requested
report_generated
report_edited
report_exported
```

ใช้เพื่อดู:

- Feature usage
- AI cost
- Time per client
- Report completion
- Retention

---

# 26. Data Privacy

Client astrology data เป็นข้อมูลส่วนบุคคล

ระบบต้อง:
- แยก account owner กับ client
- จำกัดสิทธิ์ตาม owner
- Encrypt sensitive data where appropriate
- มี Delete Client
- มี Export/Delete policy
- ไม่ใช้ข้อมูล Client เพื่อ training โดยไม่ได้รับสิทธิ์ที่เหมาะสม

---

# 27. Accuracy / Uncertainty UX

ถ้า Birth Time:

### Exact
แสดง standard house/angle confidence

### Approximate
แสดง warning:

> House-based interpretation may be sensitive to birth time.

### Unknown
ลด/ปิด feature ที่ต้องพึ่ง ASC/MC/Houses ตามความเหมาะสม

นี่สำคัญมากสำหรับ Professional Trust

---

# 28. Professional Settings

ต้องรองรับ:

### Astrology Settings
- Zodiac
- House System
- Ayanamsha if supported
- Aspect Orbs
- Uranian settings
- 90° settings
- Midpoint settings

### Report Settings
- Language
- Tone
- Length
- Sections
- Branding

ทุก setting ที่เปลี่ยน calculation ต้องถูกเก็บกับ Chart/Analysis Version

---

# 29. Versioning

ทุก Analysis ต้องรู้ว่าใช้:

```text
Calculation Version
Astrology Settings Version
Pattern Engine Version
Prompt Version
Report Version
```

ตัวอย่าง:

```text
Analysis ID: A-20260904-001
Calculation: v1.2
Pattern Engine: v1.0
Prompt: v1.3
```

นี่ช่วยให้ Professional สามารถเปิด Report เก่าแล้วรู้ว่าระบบใช้ logic ไหน

---

# 30. Reproducibility

เมื่อเปิด Analysis เดิม:

> ต้องสามารถ reproduce output จาก Chart + Settings + Engine Version + Evidence snapshot

ไม่ควรให้ Report เก่าเปลี่ยนตาม Prompt ใหม่โดยอัตโนมัติ

---

# 31. Recommended Navigation

```text
Dashboard
├── Clients
├── Charts
├── Evidence
├── Analysis
├── Reports
└── Settings
```

Client:

```text
Client
├── Overview
├── Natal
├── House Rulers
├── Aspects
├── Uranian
├── Transit
├── Patterns
├── Evidence
└── Reports
```

---

# 32. Professional UX Principle

Professional User ต้องรู้สึกว่า:

> “AI ช่วยฉันวิเคราะห์เร็วขึ้น แต่ฉันยังเป็นคนอ่านดวง”

ไม่ใช่:

> “AI เป็นนักโหร แล้วฉันแค่กด Generate”

---

# 33. Key Differentiator

Professional Product ต้องเน้น:

### TRACEABILITY

ทุก Interpretation ที่สำคัญต้องย้อนกลับไปได้ว่า:

```text
Interpretation
↓
Evidence
↓
Astrological Factors
↓
Chart
```

นี่เป็นความแตกต่างหลักจาก AI Astrology Chatbot ทั่วไป

---

# 34. Definition of Done

1,999 พร้อมเมื่อ:

- Create Client
- Save Birth Data
- Calculate Chart
- House Ruler
- Aspect
- Uranian / Midpoint
- Pattern Analysis
- Evidence Matrix
- Transit
- AI Interpretation
- Ask AI
- Deep Report
- Edit Report
- Export
- Client History
- Versioning
- Reproducibility
- Privacy controls

ทำงานได้โดยไม่ทำให้ General User Flow ซับซ้อนขึ้น

---

# 35. Future Roadmap

## Professional Pro

- Client CRM
- Advanced Transit
- Batch reports
- Templates
- Saved Interpretive Rules
- Custom Pattern Library
- Team accounts

## Professional Expert

- Multi-astrologer team
- White label
- Client portal
- API
- Advanced analytics
- Custom AI model/context

---

# 36. Final Experience

Professional User ควรรู้สึก:

> **“ระบบช่วยฉันเห็นสิ่งที่อาจพลาด และแสดงให้ฉันเห็นว่ามันมาจากไหน”**

Core workflow:

```text
CALCULATE
↓
ORGANIZE
↓
CONNECT
↓
EVIDENCE
↓
INTERPRET
↓
EDIT
↓
REPORT
```

Astro-Zodiac Professional จึงเป็น:

> **Astrology Analysis Assistant**

ไม่ใช่:

> **Automated Fortune Teller**
