# ASTRO-ZODIAC — TECHNICAL ARCHITECTURE v1

Status: Technical Baseline / Milestone v1

## 1. Objective

Technical Architecture ต้องรองรับ Product ที่ล็อกไว้:

### General User
FREE → 99 → 599

### Astrology Professional
1,999

พร้อมรองรับอนาคต:
- Human Design Engine
- Subscription
- AI Coach
- Professional Pro / Expert
- Multi-client
- Advanced Transit

หลักสำคัญ:

> **อย่าย้าย Platform ตอนนี้**
>
> ใช้ Render เป็น Infrastructure หลักในช่วง Development และ MVP/Production ระยะแรก แล้วค่อย Scale ตาม Metrics จริง

---

# 2. High-Level Architecture

```text
                 USER
                   ↓
             WEB FRONTEND
                   ↓
              Render Web
                   ↓
          ┌────────┴────────┐
          ↓                 ↓
      FAST PATH         ASYNC PATH
          ↓                 ↓
   Chart / Evidence     Worker / Queue
          ↓                 ↓
     PostgreSQL        AI / Deep Report
          ↓                 ↓
        Cache  ←───────────┘
          ↓
       Result API
```

---

# 3. Application Layers

## Layer 1 — Presentation

- HTML/CSS/JS หรือ frontend framework ในอนาคต
- Responsive
- Progressive rendering
- No astrology calculation in frontend

Frontend ทำ:
- User input
- display
- interaction
- payment state
- AI chat UI
- progress UI

Frontend ห้ามทำ:
- Astrology calculation
- House ruler calculation
- Aspect calculation
- Pattern scoring logic หลัก
- AI prompt logic

---

# 4. Layer 2 — API / Application

Current stack:
- Python
- Flask/FastAPI เลือกให้เหลือ framework เดียวใน refactor

API รับผิดชอบ:
- auth
- product entitlement
- chart requests
- report requests
- assessment
- action plan
- AI usage
- tracking

---

# 5. Layer 3 — Domain Engines

แยก module:

```text
astro_engine/
pattern_engine/
validation_engine/
psychology_engine/
action_plan_engine/
tracking_engine/
report_engine/
ai_engine/
```

แต่ละ engine ต้องมี input/output contract ชัดเจน

---

# 6. Astro Engine

หน้าที่:
- Swiss Ephemeris
- Planets
- Signs
- Houses
- ASC
- MC
- House Rulers
- Aspects
- Retrograde
- Chiron
- Node
- Uranian 90°
- Midpoints
- Planetary Pictures
- Transit

หลัก:

> **AI ห้ามคำนวณ Astro**

---

# 7. Pattern Engine

Input:

```text
Normalized Chart
+
Astrology Signals
+
Uranian Signals
```

Output:

```text
Pattern Candidates
```

Pattern Library เป็นชุดเดียวสำหรับ General User:

```text
P01–P12
```

Package ต่างกันที่ depth ไม่ใช่ Pattern คนละชุด

---

# 8. Validation Engine

Input:

```text
Pattern Candidate
+
Questions
+
User Responses
+
Behavioral Evidence
```

Output:

```text
Pattern Fit
Low / Moderate / Strong
+
Component Scores
```

Component:

```text
astrology_signal_score
self_report_score
behavioral_evidence_score
pattern_fit_score
```

MVP score ไม่ใช่ psychometric validity

---

# 9. Psychology Engine

Input:

```text
Validated Pattern
```

Output:

```text
Recommended Intervention
Worksheet
Measurement
Safety Rules
```

Psychology Knowledge Base ต้องแยก:
- instrument
- construct
- intervention
- evidence source
- license
- usage restrictions

---

# 10. Action Plan Engine

Input:

```text
Validated Pattern
+
Intervention
+
User Goal
+
Context
```

Output:

```text
7-day plan
14-day plan
30-day plan
Daily Actions
Worksheet
Check-in
```

---

# 11. Tracking Engine

เก็บ:
- daily check-in
- completion
- confidence
- difficulty
- reflection
- weekly review
- progress

ไม่ใช้เป็น clinical score

---

# 12. AI Engine

AI มีหน้าที่:
- interpretation
- explain evidence
- personalize
- answer contextual questions
- generate action wording
- summarize review

AI ห้าม:
- calculate astro
- invent evidence
- invent research
- diagnose
- create unsupported intervention
- override user responses
- silently change chart data

---

# 13. Fast Path

ทุกสิ่งที่ทำได้เร็วและ deterministic ควรอยู่ synchronous:

```text
Birth Data
↓
Chart Calculation
↓
Normalized Chart
↓
Pattern Ranking
↓
Initial Evidence
↓
Free Result
```

เป้าหมาย:

```text
Chart < 1s
Evidence < 1s
Initial meaningful UI < 3s
```

ค่าจริงต้อง benchmark บน Render environment ก่อนล็อกเป็น SLA

---

# 14. Async Path

งานหนัก/ยาว:

- Deep Report
- Large AI generation
- PDF generation
- multi-section report
- batch client analysis
- future scheduled analysis

ควรใช้ Worker/Queue

```text
API
 ↓
Create Job
 ↓
Queue
 ↓
Worker
 ↓
AI / Report
 ↓
Store Result
 ↓
Frontend polls/receives update
```

---

# 15. Streaming

AI answer ที่ User กำลังรอ:

```text
Request
↓
AI
↓
Stream tokens
↓
UI แสดงผลทันที
```

ไม่รอให้ report ทั้งก้อนเสร็จก่อนแสดง

---

# 16. Render Deployment

## Development

ใช้ Render Free ได้

เหมาะสำหรับ:
- coding
- testing
- internal demo
- low traffic

ข้อจำกัดหลัก:
- service sleep ตามเงื่อนไขของ Free
- cold start
- resource ต่ำ

ดังนั้น Free ไม่เหมาะกับ launch ที่ต้องตอบเร็วเสมอ

---

# 17. Production Render

ก่อนเปิดขายจริง:

```text
Render Web Service
+
Render Postgres
+
Worker
+
Cache
```

เริ่มจาก plan ต่ำที่เพียงพอ แล้ว benchmark

อย่า upgrade เพราะ “กลัวช้า” โดยไม่มี metrics

Upgrade เมื่อ:
- cold-start UX มีปัญหา
- CPU/RAM saturation
- latency สูง
- concurrent users เพิ่ม
- queue backlog
- revenue รองรับ

---

# 18. Database Recommendation

Primary DB:

> PostgreSQL

ไม่ใช้ SQLite เป็น primary production database

เหตุผล:
- relational
- concurrent access
- transactions
- query/indexing
- user/account/product relationships
- analytics
- future multi-client architecture

---

# 19. Proposed Database Domains

```text
Identity
Product
Astrology
Pattern
Psychology
Action
AI
Report
Analytics
```

---

# 20. Core Tables

## Identity

```text
users
sessions
consents
```

## Product

```text
products
entitlements
orders
payments
ai_usage
```

## Astrology

```text
birth_profiles
charts
chart_settings
chart_factors
house_rulers
aspects
uranian_factors
midpoints
transits
```

## Pattern

```text
patterns
pattern_signals
pattern_relationships
pattern_candidates
validated_patterns
```

## Psychology

```text
constructs
instruments
instrument_versions
intervention_methods
intervention_sources
question_bank
question_versions
question_sources
```

## Assessment

```text
assessment_sessions
assessment_questions
assessment_responses
behavioral_evidence
```

## Action

```text
goals
action_plans
action_plan_days
worksheets
worksheet_responses
checkins
weekly_reviews
progress_snapshots
```

## AI

```text
ai_sessions
ai_messages
ai_requests
ai_usage_events
```

## Report

```text
reports
report_versions
report_sections
report_evidence_links
```

## Analytics

```text
product_events
conversion_events
```

---

# 21. User vs Client Model

General User:
```text
users
```

Professional:
```text
users
  ↓
clients
```

Professional User 1 คนมี Client ได้หลายคน

Client ไม่ควรเป็น User โดยอัตโนมัติ

---

# 22. Chart Versioning

ทุก Chart ต้องเก็บ:

```text
calculation_version
astrology_settings_version
ephemeris_version
created_at
```

เพื่อ reproduce

---

# 23. Analysis Versioning

ทุก Analysis:

```text
analysis_id
chart_id
calculation_version
pattern_engine_version
prompt_version
report_version
created_at
```

Report เก่าไม่ควรถูกเปลี่ยนเพียงเพราะ Prompt ใหม่

---

# 24. Evidence Snapshot

ตอน Generate Report ต้องบันทึก Evidence snapshot

```text
report
 ↓
evidence snapshot
 ↓
chart / factor references
```

เพื่อให้เปิด Report เก่าแล้วรู้ว่าระบบใช้ Evidence อะไรตอนนั้น

---

# 25. Cache Strategy

## Cache 1 — Birth Chart

Key:

```text
hash(
birth_date,
birth_time,
birth_place,
timezone,
house_system,
zodiac_settings,
ephemeris_version
)
```

## Cache 2 — Pattern Analysis

Key:

```text
chart_hash
+
pattern_engine_version
+
pattern_settings
```

## Cache 3 — AI

Cache ได้เฉพาะ request ที่ deterministic/context stable และไม่กระทบ privacy

ไม่ควร cache personal AI response แบบกว้างโดยไม่มี user/session isolation

---

# 26. What to Store vs Recalculate

Store:
- source birth data
- normalized chart
- calculation version
- report snapshot
- user responses
- plan/check-in
- AI usage

Recalculate:
- current transit
- derived views
- temporary analytics
- current recommendation where version rules allow

---

# 27. Product Entitlement

ห้าม hard-code:

```python
if package == "99":
    ...
```

ให้ Product data-driven

ตัวอย่าง:

```text
product_id
name
price
features
ai_question_total
report_level
pattern_depth
validation_enabled
action_plan_enabled
tracking_enabled
professional_tools_enabled
```

---

# 28. AI Question Entitlement

99:

```text
3 Personal Insight Questions
```

599:

```text
10 Life Planning Questions
```

1,999:

```text
Professional AI usage
```

Quota เป็น backend entitlement

Frontend แค่แสดงสถานะ

---

# 29. Credit/Quota Rules

1 successful question = 1 usage

API error / timeout:
- ไม่หัก

Retry หลัง error:
- ไม่หักซ้ำ

Multi-part user message:
- MVP ถือ 1 message = 1 question

---

# 30. Performance Rules

1. ไม่ส่ง Raw Chart ทั้งหมดให้ AI ถ้าไม่จำเป็น
2. ส่งเฉพาะ relevant context
3. precompute deterministic evidence
4. cache expensive calculation
5. stream AI responses
6. move long jobs to worker
7. avoid duplicate calculation
8. use DB indexes
9. paginate client/report history
10. log latency per stage

---

# 31. Observability

ทุก request สำคัญต้องรู้:

```text
request_id
user_id
product_id
chart_id
analysis_id
stage
duration_ms
status
error_code
```

Latency breakdown:

```text
API
Astro Calc
Pattern
Evidence
DB
AI
Report
```

ทำให้รู้ว่า “ช้าเพราะอะไร”

---

# 32. Error Handling

Error ต้องแบ่ง:

```text
INPUT_ERROR
AUTH_ERROR
ENTITLEMENT_ERROR
CALCULATION_ERROR
DATA_ERROR
AI_ERROR
TIMEOUT_ERROR
INTERNAL_ERROR
```

User เห็นข้อความง่าย

Log ต้องมี technical detail

ห้ามส่ง stack trace ให้ User

---

# 33. Security

ขั้นต่ำ:
- secrets ใน environment variables
- HTTPS
- authenticated API
- owner-based client access
- server-side entitlement validation
- parameter validation
- rate limiting
- audit events สำหรับ professional client access
- delete/export data flows

---

# 34. AI Privacy

AI request ต้อง:
- ส่งเฉพาะ context ที่จำเป็น
- แยก User/Client
- ห้ามส่งข้อมูลของ Client A ไป context ของ Client B
- log usage แต่หลีกเลี่ยงการเก็บข้อมูลเกินจำเป็น
- เคารพ consent/data policy

---

# 35. Professional Permission Model

Owner:
```text
Professional User
```

Child resources:
```text
Clients
Charts
Reports
Notes
```

Default:
> User เห็นเฉพาะ resource ของตัวเอง

Future:
- team
- staff
- role-based access

---

# 36. API Style

แนะนำ REST สำหรับ MVP

Examples:

```text
POST /api/auth/login

POST /api/chart/calculate

GET /api/chart/{id}

GET /api/patterns/{chart_id}

POST /api/validation/session

POST /api/validation/respond

GET /api/report/{id}

POST /api/ai/insight-question

POST /api/action-plan/create

POST /api/checkin

GET /api/progress
```

Professional:

```text
POST /api/clients
GET /api/clients
GET /api/clients/{id}
POST /api/professional/analysis
POST /api/professional/report
POST /api/professional/export
```

ชื่อจริงต้องถูกล็อกใน API Contract ก่อน implementation

---

# 37. Recommended Repository Structure

```text
Astro-Zodiac/
│
├── app/
│   ├── api/
│   ├── core/
│   ├── astro/
│   ├── patterns/
│   ├── validation/
│   ├── psychology/
│   ├── action_plan/
│   ├── tracking/
│   ├── ai/
│   └── reports/
│
├── models/
├── schemas/
├── repositories/
├── services/
├── prompts/
├── tests/
│
├── frontend/
│
├── migrations/
│
├── knowledge/
│   ├── psychology/
│   ├── interventions/
│   └── patterns/
│
├── docs/
│
├── main.py
├── requirements.txt
└── ...
```

ระยะ refactor ค่อยย้ายจาก structure เดิมทีละส่วน ไม่ rewrite ทั้ง Repo พร้อมกัน

---

# 38. Migration Strategy

จาก Code เดิม:

```text
main.py
astro_calc.py
evidence_engine.py
ai_service.py
database.py
```

ไม่ลบทันที

ขั้น:

```text
Legacy
↓
Adapter
↓
New Contract
↓
Tests
↓
Switch Traffic
↓
Remove Legacy
```

---

# 39. Testing Strategy

## Unit
- astrology calculations
- house rulers
- aspects
- midpoints
- pattern scoring
- entitlement
- quota

## Integration
- API + DB
- chart → pattern
- pattern → validation
- validation → intervention
- plan → tracking

## Regression
ใช้ Golden Charts

```text
Test Chart A
Test Chart B
Test Chart C
```

ตรวจ:
- Sun
- Moon
- ASC
- MC
- Houses
- Rulers
- Aspects
- Uranian factors

---

# 40. Deployment Environments

แยก:

```text
local
staging
production
```

Production data ห้ามใช้ทดสอบโดยตรง

---

# 41. Render Environment Recommendation

Development:
```text
Render Free
```

Pre-production:
```text
Paid Web Service (เมื่อ staging ต้อง stable)
+
Postgres
```

Production:
```text
Paid Web Service
+
Postgres
+
Worker
+
Cache
```

ค่าที่เหมาะสมต้องวัดจาก actual load

---

# 42. Minimum Production Stack

```text
Render Web Service
+
Render Postgres
+
1 Worker
+
Cache layer
+
AI API
+
Monitoring
```

ไม่ต้องเพิ่ม Kubernetes/microservices ใน MVP

---

# 43. Scaling Principle

เริ่ม Modular Monolith

ไม่เริ่ม microservices

เหตุผล:
- ทีมเล็ก
- debug ง่าย
- deploy ง่าย
- transaction ง่าย
- developmentเร็ว

ค่อยแยก service เมื่อมี bottleneck จริง

---

# 44. Future Human Design

Architecture ต้องเผื่อ:

```text
Astrology Engine
   ↓
Uranian Engine
   ↓
Human Design Engine (Future)
   ↓
Unified Pattern Engine
```

Human Design ไม่ควรเอามาปนกับ psychological validation โดยอัตโนมัติ

---

# 45. Technical Definition of Done

Architecture v1 ถือว่าเพียงพอเมื่อ:

- มี Shared Pattern Library
- มี normalized Chart Contract
- มี Pattern Contract
- มี Validation Contract
- มี Intervention Contract
- มี Action Plan Contract
- มี Entitlement Model
- มี AI quota
- มี PostgreSQL model
- มี cache strategy
- มี async strategy
- มี versioning
- มี logging
- มี tests plan

---

# 46. Implementation Order

## Phase T1
Chart Schema

## Phase T2
Astro Calculation

## Phase T3
House Ruler

## Phase T4
Aspect Engine

## Phase T5
Uranian Engine

## Phase T6
Pattern Engine

## Phase T7
Validation Engine

## Phase T8
Psychology Knowledge Base

## Phase T9
Action Plan

## Phase T10
AI Service

## Phase T11
Report

## Phase T12
Frontend Integration

## Phase T13
Performance / Cache

## Phase T14
Professional Workspace

---

# 47. First Technical Task

**ห้ามเริ่มแก้ `main.py` แบบสุ่ม**

Task แรก:

> สร้าง `chart_schema.py` / normalized chart contract และเขียน tests ให้ผ่าน

จากนั้นค่อย migrate `astro_calc.py` ให้คืน schema เดียว

---

# 48. Final Architecture Principle

```text
CALCULATE ONCE
↓
NORMALIZE ONCE
↓
REUSE MANY TIMES
↓
EVIDENCE ON DEMAND
↓
AI ONLY WHEN NEEDED
↓
CACHE EXPENSIVE WORK
↓
TRACK EVERYTHING IMPORTANT
```

และ:

> **Render ไม่ใช่ตัวปัญหาหลักของความเร็วใน MVP — architecture ของ request pipeline ต่างหากที่ต้องแก้ก่อน**
