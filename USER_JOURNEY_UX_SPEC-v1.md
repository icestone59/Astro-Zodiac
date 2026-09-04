# ASTRO-ZODIAC — USER JOURNEY & UX SPEC v1

> Status: **Milestone / Baseline v1**
>
> เอกสารนี้เป็น UX Baseline ไม่ใช่ Final Lock สามารถแก้เป็น v1.1, v1.2 หรือ v2 ได้ตามผลการพัฒนาและการทดสอบจริง โดยบันทึกการเปลี่ยนแปลงใน CHANGELOG.md

---

# 1. UX North Star

ผู้ใช้ต้องเดินผ่าน 4 ขั้น:

```text
DISCOVER
ฉันเป็นอย่างไร / มี Pattern อะไร?
        ↓
VALIDATE
Pattern นี้ตรงกับชีวิตฉันจริงไหม?
        ↓
ACT
ฉันควรทำอะไร?
        ↓
GROW
ฉันเปลี่ยนไปแค่ไหน?
```

Core Experience:

> “ระบบไม่ได้แค่บอกฉันว่าเป็นอะไร แต่ช่วยฉันรู้ว่าต้องทำอะไรต่อ”

---

# 2. Product Lines

## General User

```text
FREE — Discovery
        ↓
99 — Personal Insight
        ↓
599 — Personal Action Plan
```

## Astrology Professional

```text
1,999 — Astro Professional
```

สองเส้นทางต้องแยก UX ตั้งแต่ต้น เพราะ Customer Job-to-be-Done ต่างกัน

---

# 3. GENERAL USER — CORE JOURNEY

```text
Landing
  ↓
เลือก “ค้นหา Pattern ของฉัน”
  ↓
Birth Data
  ↓
Free Analysis
  ↓
3 Patterns
  ↓
Aha Moment
  ↓
99 Personal Insight
  ↓
Validation
  ↓
Personal Report
  ↓
AI 3 Questions
  ↓
599 Personal Action Plan
  ↓
Psychology Intervention
  ↓
Action Plan
  ↓
Worksheet
  ↓
Daily Check-in
  ↓
Progress
  ↓
Weekly Review
```

---

# 4. Screen 01 — Landing

## Objective
ทำให้ผู้ใช้เข้าใจ Product ภายในไม่กี่วินาที

## Core Message

> “คุณไม่ได้ขาดศักยภาพ คุณแค่ยังไม่เห็นสิ่งที่กำลังขวางคุณอยู่”

## Primary CTA

> ค้นหา Pattern ของฉัน

## Secondary CTA

> ฉันเป็นนักโหราศาสตร์ / กำลังศึกษาโหราศาสตร์

Secondary CTA นำเข้าสู่ Astro Professional

---

# 5. Screen 02 — Birth Data

## Input

- Date of Birth
- Exact / Approximate Birth Time
- Birth Place
- Timezone

## Requirement

ตรวจความครบถ้วนก่อนเริ่ม Calculation

## UX

ไม่ควรให้ผู้ใช้กรอกข้อมูลซับซ้อนเกินจำเป็น

---

# 6. Screen 03 — Free Analysis

## Objective

คำนวณเร็วและแสดง Progress

## Performance Target

- Chart Calculation < 1 sec
- Initial meaningful result < 3 sec
- Progressive Rendering

## UX Example

```text
กำลังค้นหา Pattern ที่เด่นที่สุดของคุณ...
✓ Birth Chart
✓ House Structure
✓ Key Aspects
✓ Pattern Analysis
```

---

# 7. Screen 04 — Free Result / 3 Patterns

## Free ต้องแสดง 3 Patterns

### Pattern 01
Top Blind Spot

### Pattern 02
Secondary Pattern

### Pattern 03
Potential Strength

ตัวอย่าง:

```text
01 🔴 Decision Avoidance
คุณอาจใช้เวลาตัดสินใจนานกว่าที่จำเป็น

02 🟡 Perfectionism
คุณอาจชะลอการลงมือเมื่อรู้สึกว่ายังไม่พร้อม

03 🟢 Strategic Thinking
คุณมีแนวโน้มมองภาพรวมและคิดเป็นระบบ
```

## Free เปิดเผย

- Pattern Name
- Short Explanation
- Limited Evidence Teaser

## Free ไม่เปิดเผย

- Full Evidence
- Full Validation
- Full Report
- Psychology Intervention
- Action Plan
- AI Personal Session

## Upgrade CTA

> “Pattern เหล่านี้ตรงกับชีวิตคุณจริงแค่ไหน?”

→ **ตรวจสอบ Pattern ของฉัน — 99 บาท**

---

# 8. Screen 05 — 99 Personal Insight

## Objective

ตรวจสอบว่า Pattern ที่ระบบค้นพบตรงกับชีวิตจริงหรือไม่

## Steps

```text
Pattern
  ↓
Self Assessment
  ↓
Behavioral Questions
  ↓
Pattern Confidence
  ↓
Personal Report
```

## Assessment

ประมาณ 5–8 คำถามต่อ Pattern Cluster / Session ตามผลการทดสอบ UX

---

# 9. Screen 06 — Validation Result

แสดง:

```text
Pattern Confidence

LOW
MODERATE
STRONG
```

พร้อมคำอธิบายภาษาคน

ตัวอย่าง:

> “จากสิ่งที่คุณตอบมา Pattern นี้มีความสอดคล้องกับประสบการณ์ของคุณในระดับ Strong”

## Safety

ไม่ใช้คำว่า:
- Diagnosis
- Disorder
- Clinical condition

---

# 10. Screen 07 — Personal Report

Report ต้องตอบ:

```text
ฉันมี Pattern อะไร?
มันแสดงออกอย่างไร?
มี Evidence อะไร?
ฉันยืนยันมันอย่างไร?
```

## Report Sections

- Core Pattern
- Strengths
- Blind Spots
- Supporting Evidence
- User Validation
- Personal Insight
- What to Explore Next

---

# 11. Screen 08 — AI Personal Insight

## 99 Package

AI Personal Insight Session:

**3 questions**

## Rule

คำถามต้องเกี่ยวกับ:
- Personal Report
- Validated Pattern
- User Assessment
- Relevant Evidence

## ห้าม

- General Astrology Chat
- AI คำนวณ Chart เอง
- AI วินิจฉัย
- AI สร้าง Evidence ที่ไม่มี

จำนวนคำถามเป็น Feature ที่แสดงให้ผู้ใช้เห็น แต่ไม่ใช่ Marketing Promise หลัก

---

# 12. Screen 09 — 599 Personal Action Plan

## Upgrade Trigger

> “ตอนนี้ฉันรู้แล้วว่า Pattern คืออะไร แต่ยังไม่รู้ว่าจะเปลี่ยนอย่างไร”

CTA:

> **สร้างแผนเปลี่ยน Pattern ของฉัน — 599 บาท**

---

# 13. Screen 10 — Psychology Intervention

ระบบเลือก Intervention จาก Knowledge Base

ตัวอย่าง:

```text
Validated Pattern:
Procrastination

Recommended:
Implementation Intention
+
Small-step Planning
+
Behavioral Activation
```

## Requirement

AI ต้องใช้ Intervention Library เป็น Source ไม่แต่ง Method เอง

---

# 14. Screen 11 — Goal Setting

```text
Current Problem
↓
Desired Change
↓
Specific Goal
↓
Target Date
```

ตัวอย่าง:

> “เริ่มงานสำคัญภายใน 10 นาทีหลังถึงโต๊ะทำงาน”

---

# 15. Screen 12 — Action Plan

สร้าง:

- 7-Day Plan
- 14-Day Plan
- 30-Day Plan

แต่ละวันมี Action ที่เล็กพอให้ทำจริง

---

# 16. Screen 13 — Worksheet

ผู้ใช้กรอกในระบบหรือ Download

ตัวอย่าง Thought Record:

```text
Situation
Automatic Thought
Emotion
Evidence For
Evidence Against
Balanced Thought
Next Action
```

ตัวอย่าง Comfort Zone Challenge:

```text
สิ่งที่ฉันกำลังหลีกเลี่ยง:
ระดับความยาก 1–10:
Action ที่เล็กที่สุด:
ผลลัพธ์:
สิ่งที่เรียนรู้:
```

---

# 17. Screen 14 — Daily Check-in

ผู้ใช้เห็น:

```text
TODAY’S ACTION

[ ] Completed
[ ] Partially completed
[ ] Not completed
```

และ:
- Difficulty 1–10
- Confidence 1–10
- Short reflection

---

# 18. Screen 15 — Progress Dashboard

```text
AWARENESS
████████░░ 80%

CONFIDENCE
██████░░░░ 60%

ACTION
███████░░░ 70%

OUTCOME
██████░░░░ 60%
```

คะแนนเหล่านี้ไม่ใช่ผลทางคลินิก

---

# 19. Screen 16 — Weekly Review

ถาม:

- อะไรทำได้ดี?
- อะไรติดขัด?
- Pattern เดิมเกิดขึ้นเมื่อไร?
- อะไรช่วยได้?
- สัปดาห์หน้าจะเปลี่ยนอะไร?

จากนั้น:

```text
Review
↓
Adjust Goal
↓
Adjust Intervention
↓
New Weekly Actions
```

---

# 20. GENERAL USER — FULL FLOW

```text
LANDING
   ↓
BIRTH DATA
   ↓
FREE ANALYSIS
   ↓
3 PATTERNS
   ↓
AHA MOMENT
   ↓
99
   ↓
VALIDATION
   ↓
PERSONAL REPORT
   ↓
AI × 3
   ↓
599
   ↓
INTERVENTION
   ↓
GOAL
   ↓
ACTION PLAN
   ↓
WORKSHEET
   ↓
DAILY CHECK-IN
   ↓
PROGRESS
   ↓
WEEKLY REVIEW
```

---

# 21. ASTRO PROFESSIONAL — CORE JOURNEY

## Target

- ผู้ศึกษาโหราศาสตร์
- Beginner Astrologer
- Aspiring Astrologer

## Flow

```text
Professional Landing
      ↓
Create Account
      ↓
Professional Dashboard
      ↓
Create Client
      ↓
Birth Data
      ↓
Full Chart
      ↓
Astrology Evidence
      ↓
House Ruler
      ↓
Aspect
      ↓
Uranian / Midpoint
      ↓
Transit
      ↓
Pattern Analysis
      ↓
AI Interpretation
      ↓
Deep Report
      ↓
Ask / Discuss
      ↓
Export
```

---

# 22. Professional Dashboard

ควรมี:

- Client List
- Create Client
- Search Client
- Client History
- Recent Reports
- Saved Charts
- Export

---

# 23. Professional Analysis Screen

ต้องเห็น Evidence ไม่ใช่แค่ Interpretation

```text
HOUSE 10
↓
RULER
↓
PLACEMENT
↓
ASPECTS
↓
URANIAN SIGNAL
↓
EVIDENCE
↓
INTERPRETATION
```

นี่คือจุดขายหลักของ Professional Product

---

# 24. AI Context Architecture

## Personal Insight

```text
Report
+
Validated Pattern
+
Assessment
+
Evidence
```

## Action Plan

```text
Report
+
Validated Pattern
+
Assessment
+
Intervention
+
Goal
+
Current Progress
```

## Professional

```text
Chart
+
Evidence
+
Analysis Layer
+
User Selected Context
```

ไม่ส่งข้อมูลทั้งหมดโดยไม่จำเป็น

---

# 25. UX Performance

เป้าหมาย:

```text
Chart Calculation       < 1 sec
Evidence Generation     < 1 sec
Initial Meaningful UI   < 3 sec
AI Response             Progressive Streaming
Cached Request          Near-instant
```

หลักการ:

> อย่าให้ผู้ใช้รอ AI ก่อนที่จะเห็นสิ่งที่ Software สามารถแสดงได้ทันที

---

# 26. Upgrade UX

## Free → 99

> “Pattern นี้ตรงกับชีวิตคุณจริงแค่ไหน?”

## 99 → 599

> “ตอนนี้คุณรู้แล้วว่าอะไรเกิดขึ้น แล้วคุณจะเปลี่ยนมันอย่างไร?”

ไม่ใช้:
- Pop-up ขายทุกหน้า
- Fake countdown
- Scarcity ปลอม
- Fear-based manipulation

---

# 27. UX Analytics Events

## General

```text
landing_view
birth_data_started
birth_data_completed
free_analysis_started
free_analysis_completed
pattern_viewed
upgrade_99_viewed
purchase_99
assessment_started
assessment_completed
report_viewed
ai_question_asked
upgrade_599_viewed
purchase_599
intervention_viewed
goal_created
plan_created
worksheet_started
checkin_completed
weekly_review_completed
```

## Professional

```text
professional_view
client_created
chart_viewed
evidence_viewed
report_generated
report_exported
```

---

# 28. UX Versioning Rule

เอกสารนี้คือ **Baseline v1**

การเปลี่ยนแปลง:

```text
v1
↓
v1.1
↓
v1.2
↓
v2
```

ห้ามลบประวัติการตัดสินใจ

ทุกการเปลี่ยนที่มีผลต่อ Product/Architecture ให้บันทึกใน `CHANGELOG.md`

ถ้าเปลี่ยนเฉพาะข้อความ/ตำแหน่ง UI และไม่มีผลต่อ Data Contract ไม่ต้องรื้อ Backend

ถ้าเปลี่ยน:
- Product entitlement
- AI quota
- Data flow
- Database
- API
- Core business rule

ต้องตรวจ `DATA_CONTRACT.md` และ `ARCHITECTURE.md` ด้วย

---

# 29. Final UX Principle

ผู้ใช้ต้องไม่หลงทาง

ทุกหน้าควรตอบคำถาม:

```text
ฉันกำลังดูอะไร?
ทำไมมันสำคัญ?
ฉันควรทำอะไรต่อ?
```

Core Experience:

> **Discover → Validate → Act → Grow**

# Pattern Access Model — v1 Amendment

All General User packages use the same Pattern Library and Pattern Engine.

## FREE
แสดง:
- 1 Primary Blind Spot
- 1 Secondary Pattern
- 1 Strength

## 99
เริ่มจาก Pattern ที่ค้นพบใน Free แล้ว Validate/อธิบายเชิงลึก

## 599
ใช้ Validated Pattern(s) และ Pattern Relationships จาก 99 เพื่อเลือก Priority Pattern/Cluster และทำ Intervention + Action Plan

```text
Free
  ↓
Top 3 Patterns
  ↓
99
  ↓
Validated Pattern + Related Patterns
  ↓
599
  ↓
Priority Pattern / Pattern Cluster
  ↓
Intervention + Action
```
