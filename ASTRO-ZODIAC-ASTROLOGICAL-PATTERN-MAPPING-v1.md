# ASTRO-ZODIAC — ASTROLOGICAL PATTERN MAPPING v1

Status: **Logic Baseline / Milestone v1**

> เอกสารนี้กำหนดว่า Astrology / Uranian จะทำหน้าที่ “ค้นหา Pattern ที่ควรสำรวจ” อย่างไร ก่อนส่งต่อให้ Validation และ Psychology Layer
>
> ไม่ใช่ระบบพิสูจน์ทางวิทยาศาสตร์ว่า Astrology เป็นสาเหตุของบุคลิกหรือพฤติกรรม และไม่ใช้เพื่อ clinical diagnosis

---

# 1. Core Principle

Astro-Zodiac ใช้ 2 กลุ่มข้อมูลเป็นแกนหลัก:

```text
WESTERN ASTROLOGY
+
URANIAN ASTROLOGY
        ↓
ASTROLOGICAL SIGNALS
        ↓
PATTERN ENGINE
        ↓
PATTERN TO EXPLORE
        ↓
VALIDATION
```

Western Astrology ให้บริบทเรื่อง:
- Signs
- Houses
- House Rulers
- Planets
- Aspects
- Angles

Uranian เพิ่ม:
- 90° dial
- hard-aspect structure
- midpoints
- planetary pictures
- symmetry / midpoint trees
- optional Trans-Neptunian Points

แหล่งอธิบายร่วมสมัยของ Uranian/Hamburg School ระบุ 90° dial, midpoint และ planetary pictures เป็นเครื่องมือหลักของแนวทางนี้ และชี้ว่าการพับ 360° ลงเหลือ 90° ทำให้ conjunction/square/opposition มารวมอยู่บนแกนเดียวเพื่อดูโครงสร้าง hard aspects ได้ชัดขึ้น citeturn913692search0turn913692search1

---

# 2. Important Boundary

Astrology Engine ไม่ควรส่งผลลัพธ์เป็น:

> “คุณเป็นคน Procrastinator”

แต่ควรส่ง:

> “Potential Pattern: Procrastination / Action Delay”

และ AI/UX ใช้ถ้อยคำ:

> “นี่คือ Pattern ที่ควรสำรวจ”

หรือ

> “ระบบพบสัญญาณที่อาจเกี่ยวข้องกับ...”

จากนั้น Validation Engine ต้องถามผู้ใช้และใช้พฤติกรรมจริงช่วยตรวจสอบ

---

# 3. Signal Hierarchy

ให้ Pattern Engine ประมวลผลจากระดับพื้นฐานไปลึก:

```text
Level 1
Planet + Sign

Level 2
Planet + House

Level 3
House + House Ruler

Level 4
Natal Aspects

Level 5
Cross-house links

Level 6
Uranian Hard-aspect / 90° structure

Level 7
Midpoint / Planetary Picture

Level 8
Transit Activation
```

ไม่ควรสรุป Pattern จาก signal เดียว หากสามารถใช้หลาย signal ที่เกี่ยวข้องร่วมกันได้

---

# 4. Western Astrology Signal Model

## 4.1 Planet

Planet คือหลักการที่กำลังทำงาน

MVP:
- Sun
- Moon
- Mercury
- Venus
- Mars
- Jupiter
- Saturn
- Uranus
- Neptune
- Pluto
- Chiron
- North Node

## 4.2 Sign

Sign เป็น style / mode ของการแสดงออกในกรอบโหราศาสตร์

## 4.3 House

House เป็น life area/context

## 4.4 House Ruler

House ruler ใช้เชื่อม:

```text
House Topic
↓
Cusp Sign
↓
Ruling Planet
↓
Ruler's Sign
↓
Ruler's House
↓
Ruler's Aspects
```

ตัวอย่างทั่วไป:

> ถ้า House 10 มี sign X และ ruler อยู่ House 6 เราจะถือว่าเป็น “possible link” ระหว่าง career/public role กับ work/routine/service ในกรอบการตีความทางโหราศาสตร์

แนวคิด house-ruler placement ถูกใช้เพื่อเชื่อมเรื่องของ house กับ house ที่ ruler ไปอยู่ citeturn913692search5turn913692search9

---

# 5. Uranian Signal Model

## 5.1 90° Dial

ใช้เพื่อหา hard-aspect structure:

- Conjunction
- Square
- Opposition

บน 90° dial ความสัมพันธ์เหล่านี้ถูกรวมเป็นตำแหน่งเดียวในโมดูล 90° citeturn913692search0turn913692search1

## 5.2 Midpoint

รูปแบบ:

```text
A/B = C
```

หมายถึง C อยู่บน midpoint axis ของ A และ B ตามกติกาของระบบ Uranian

## 5.3 Planetary Picture

Pattern Engine สามารถบันทึก:

```text
planetary_picture
A/B=C
orb
factors
```

## 5.4 TNP

รองรับเป็น optional advanced signals:

- Cupido
- Hades
- Zeus
- Kronos
- Apollon
- Admetos
- Vulkanus
- Poseidon

สถานะ:

> Symbolic / tradition-based factors

ไม่ควรนำเสนอว่าเป็น astronomical bodies ที่ได้รับการยืนยันแล้ว citeturn913692search1

---

# 6. Pattern Library Mapping

## P01 — PROCRASTINATION / ACTION DELAY

### Life Question
> “อะไรทำให้ฉันรู้ว่าต้องทำ แต่ยังไม่ลงมือ?”

### Potential Astrology Signals

Western:
- Strong Saturn/Mars themes
- Mercury/Mars stress themes
- 6th/10th/12th-house emphasis depending on interpretation
- Relevant ruler-to-house links
- Hard aspects affecting action, discipline or execution themes

Uranian:
- Tight Mars/Saturn pictures
- Relevant Mars/Saturn midpoint structures
- MC/ASC involvement when career/action is the topic

### Rule
ไม่ใช้ Mars/Saturn เดี่ยว ๆ เพื่อสรุป procrastination

ต้องมี multi-signal pattern และ Validation

### Validation Route
→ P01 questions

### Likely Interventions
→ Implementation intention
→ Small-step planning

---

# P02 — PERFECTIONISM

### Life Question
> “อะไรทำให้ฉันรู้สึกว่ายังไม่ดีพอ?”

### Potential Signals

Western:
- Saturn emphasis
- Mercury/Saturn themes
- Virgo/6th-house themes where relevant
- 10th-house / public evaluation themes where relevant
- House ruler links involving standards/work

Uranian:
- Saturn hard-aspect structures
- Saturn/Mercury
- Saturn/MC
- Saturn/Sun pictures when relevant to identity/standards

### Rule
อย่าแปล “Saturn = perfectionism” ตรง ๆ

### Validation
→ P02

### Intervention
→ CBT-informed perfectionism exercises
→ Behavioral experiment

---

# P03 — DECISION AVOIDANCE / INDECISIVENESS

### Life Question
> “อะไรทำให้ฉันลังเลหรือตัดสินใจช้า?”

### Potential Signals

Western:
- Mercury themes
- Saturn themes
- Libra/7th-house decision context where relevant
- Neptune themes where ambiguity is relevant
- House ruler patterns connected to uncertainty/choice

Uranian:
- Mercury/Saturn
- Mercury/Neptune
- Mercury/Admetos-type configurations only as tradition-based exploratory signals
- relevant MC/ASC pictures

### Validation
→ P03

### Intervention
→ Decision criteria
→ Time-boxed decisions
→ Behavioral experiments

---

# P04 — FEAR OF FAILURE

### Life Question
> “ฉันหลีกเลี่ยงอะไรเพราะกลัวพลาด?”

### Potential Signals

Western:
- Saturn pressure
- Sun/Saturn
- Mars/Saturn
- 10th-house/public evaluation themes
- Chiron themes only as exploratory context

Uranian:
- Sun/Saturn
- Mars/Saturn
- MC/Saturn
- relevant planetary pictures

### Validation
→ P04

### Intervention
→ Behavioral experiment
→ Graded challenge
→ CBT-informed reframe

---

# P05 — LOW SELF-EFFICACY / LOW CONFIDENCE

### Life Question
> “ฉันเชื่อไหมว่าตัวเองรับมือเรื่องยากได้?”

### Potential Signals

Western:
- Sun-related themes
- Saturn/Sun
- Jupiter/Sun
- House 1 / ruler of 1
- MC/10th context for competence

Uranian:
- Sun/Saturn
- Sun/Jupiter
- ASC/Sun
- MC/Sun

### Rule
ห้ามสรุป “self-efficacy ต่ำ” จาก chart อย่างเดียว

### Validation
→ P05 GSE-informed/custom items

### Intervention
→ Mastery evidence
→ Small progressive goals

---

# P06 — VALUES / DIRECTION CONFUSION

### Life Question
> “ฉันกำลังใช้ชีวิตตามสิ่งที่ตัวเองต้องการจริง ๆ หรือเปล่า?”

### Potential Signals

Western:
- Sun / North Node themes
- 9th/10th-house themes
- ruler connections involving purpose/direction
- Neptune/Jupiter themes when exploration/idealization is relevant

Uranian:
- Sun/Node
- Sun/Neptune
- MC/Node
- relevant midpoint pictures

### Validation
→ P06 Values

### Intervention
→ Values clarification
→ Committed action

---

# P07 — GOAL FAILURE

### Life Question
> “ทำไมฉันตั้งเป้าหมายได้ แต่ทำต่อไม่ได้?”

### Potential Signals

Western:
- Mars/Saturn
- Jupiter/Saturn tension
- 6th/10th-house ruler patterns
- mutable/fixed emphasis as exploratory signal, not deterministic diagnosis

Uranian:
- Mars/Saturn
- Jupiter/Saturn
- MC/Mars
- relevant hard-aspect clusters

### Validation
→ P07

### Intervention
→ Implementation intention
→ WOOP
→ Goal decomposition

---

# P08 — RUMINATION / THINKING LOOP

### Life Question
> “ทำไมฉันคิดเรื่องเดิมซ้ำ ๆ จนลงมือช้า?”

### Potential Signals

Western:
- Mercury/Neptune
- Mercury/Saturn
- Moon/Mercury
- 3rd/8th/12th-house contexts where appropriate

Uranian:
- Mercury/Neptune
- Mercury/Saturn
- Mercury/Moon
- midpoint pictures involving Mercury

### Validation
→ P08

### Intervention
→ Problem-solving conversion
→ Cognitive strategies
→ Think → Decide → Act

---

# P09 — AVOIDANCE / COMFORT ZONE

### Life Question
> “อะไรที่ฉันรู้ว่าควรเผชิญ แต่ยังหลีกเลี่ยง?”

### Potential Signals

Western:
- Saturn/Mars
- Saturn/Neptune
- strong 12th-house themes
- relevant 8th/6th/12th context

Uranian:
- Mars/Saturn
- Mars/Neptune
- ASC/Saturn
- relevant Admetos-style exploratory structures

### Validation
→ situation-specific behavioral questions

### Intervention
→ Graded challenge
→ Behavioral experiment

---

# P10 — PEOPLE-PLEASING / BOUNDARY DIFFICULTY

### Life Question
> “ฉันกำลังใช้ชีวิตตามความต้องการของคนอื่นมากกว่าของตัวเองหรือไม่?”

### Potential Signals

Western:
- Venus/Saturn
- Moon/Saturn
- Libra/7th-house themes
- 4th/7th-house ruler links
- Neptune/Venus themes where idealization is relevant

Uranian:
- Venus/Saturn
- Moon/Saturn
- Venus/Neptune
- ASC/Venus
- relationship-related pictures

### Validation
→ P10

### Intervention
→ Assertiveness
→ Boundary scripts
→ Values clarification

---

# P11 — EMOTIONAL REACTIVITY

### Life Question
> “เวลารู้สึกแรง ฉันตอบสนองก่อนคิดหรือไม่?”

### Potential Signals

Western:
- Moon/Mars
- Moon/Uranus
- Mars/Uranus
- Moon/Pluto
- 1st/4th-house context where relevant

Uranian:
- Moon/Mars
- Moon/Uranus
- Mars/Uranus
- Moon/Pluto pictures

### Validation
→ P11

### Intervention
→ Pause routine
→ Emotion labeling
→ Values-based action

---

# P12 — HABIT MAINTENANCE

### Life Question
> “ทำไมฉันเริ่มได้ แต่ทำต่อเนื่องไม่ได้?”

### Potential Signals

Western:
- 6th-house themes
- Mars/Saturn
- ruler links involving routine
- fixed/mutable patterns as exploratory context

Uranian:
- Mars/Saturn
- relevant 6th-house ruler if integrated with Western model
- midpoint pictures involving Mars/Saturn/MC

### Validation
→ P12

### Intervention
→ Environment design
→ Minimum viable action
→ Implementation intention

---

# 7. Pattern Priority Logic

Pattern Engine ไม่ควรส่ง 12 Patterns ทั้งหมดให้ AI

ให้จัด Priority:

```text
Signal Strength
+
Signal Count
+
Pattern Specificity
+
House Relevance
+
Uranian Tightness
```

เบื้องต้น:

```text
Primary Pattern
Secondary Pattern
Strength Pattern
```

Free จึงแสดง 3 อย่าง:

```text
1 × Blind Spot
1 × Secondary Pattern
1 × Strength
```

---

# 8. Evidence Weighting

MVP ไม่ควรใช้ “จำนวนดาว” อย่างเดียว

ให้แบ่ง:

### Stronger Signal
- Multiple independent factors point to same theme
- Relevant house/ruler connection
- Tight Uranian structure
- Same theme repeated across Western + Uranian

### Medium Signal
- One major factor + supporting context

### Weak Signal
- Single placement
- Generic sign placement
- Loose aspect

Weak Signal อย่างเดียว:

> ไม่ควรสร้าง High Confidence Pattern

---

# 9. House Relevance

Pattern Engine ต้องเลือก house ตามคำถาม/บริบท

ตัวอย่าง:

### Career
Priority:
- 10
- 6
- 2
- MC
- relevant rulers

### Relationship
Priority:
- 7
- 5
- 8
- Venus
- Moon
- relevant rulers

### Identity
Priority:
- 1
- Sun
- ASC
- ruler of 1

### Direction
Priority:
- 9
- 10
- Sun
- Node
- relevant rulers

---

# 10. Astrology → Question Routing

ตัวอย่าง:

```text
ASTRO SIGNAL
Mars/Saturn
+
6th/10th ruler link

↓
Pattern Candidate
Procrastination / Action Delay

↓
Question Set
P01

↓
ถ้าคะแนนต่ำ
หยุด

ถ้าคะแนนสูง
↓
ถาม Behavioral Evidence

ถ้ายังสอดคล้อง
↓
ถาม Origin/Context
```

---

# 11. Adaptive Question Routing

ต้องไม่ถาม Childhood ทุกคน

```text
Step 1 — Current Behavior
        ↓
Step 2 — Impact
        ↓
Step 3 — Trigger
        ↓
Step 4 — Origin / Context
```

Origin อาจเป็น:

- Family
- School
- Teachers
- Peers
- Important events
- Cultural/social environment

แต่ใช้คำว่า:

> “Possible Origin / Context to Explore”

ไม่ใช่:

> “สาเหตุของปัญหา”

---

# 12. Pattern Clustering

บางคนอาจมีหลาย Pattern ที่เชื่อมกัน:

```text
Perfectionism
      ↓
Fear of Failure
      ↓
Procrastination
```

หรือ:

```text
People-Pleasing
      ↓
Decision Avoidance
      ↓
Low Self-Efficacy
```

Pattern Engine ควรจัดเป็น:

### Root / Core Pattern
Pattern ที่อาจอยู่ต้นทางของหลายพฤติกรรม

### Secondary Pattern
Pattern ที่เกิดร่วม

### Consequence Pattern
Pattern ที่อาจเป็นผลตามมา

แต่ยังต้องให้ User Validation ก่อนเรียก “core”

---

# 13. Pattern Graph

Future data model ควรรองรับ:

```text
Pattern A
  ├── related_to → Pattern B
  ├── may_trigger → Pattern C
  └── may_reinforce → Pattern D
```

เพื่อให้ AI อธิบายได้ว่า:

> “สาม Pattern ของคุณอาจเกี่ยวข้องกันเป็นวงจร”

---

# 14. Transit Role

Transit ไม่ควรสร้าง Personality Pattern ใหม่

Transit ใช้เพื่อ:

```text
Natal Pattern
+
Current Transit
↓
Activation / Timing Context
```

ตัวอย่างเชิงโครงสร้าง:

```text
Natal Pattern:
Decision Avoidance

Transit Activation:
Mars / Saturn activates relevant natal structure

Output:
“ช่วงนี้อาจเป็นช่วงที่คุณรู้สึกถึง Pattern นี้ชัดขึ้น”
```

ไม่ใช้:

> “คุณจะล้มเหลวแน่นอนในเดือนหน้า”

---

# 15. Uranian Role

Uranian เป็น Advanced Pattern Detector

ใช้เพื่อ:
- sharpen signal
- identify clusters
- detect midpoint relationships
- detect hard-aspect structures
- support timing/activation analysis

แต่:

> Uranian signal = interpretive evidence within the system

ไม่ใช่ scientific proof of behavior or life outcome

---

# 16. Pattern Data Contract

Pattern Engine ควรคืน JSON โครงสร้างประมาณ:

```json
{
  "pattern_id": "P01",
  "name": "Procrastination / Action Delay",
  "status": "candidate",
  "score": {
    "western": 0,
    "uranian": 0,
    "context": 0,
    "total": 0
  },
  "signals": [
    {
      "type": "house_ruler",
      "source": "House 10 Ruler",
      "detail": "..."
    },
    {
      "type": "uranian_picture",
      "source": "Mars/Saturn",
      "orb": 0.23
    }
  ],
  "validation_route": "P01",
  "language": "pattern_to_explore"
}
```

---

# 17. What AI Receives

AI ไม่ควรได้รับ raw chart ทุกครั้ง

สำหรับ Pattern:

```text
Pattern Candidate
+
Evidence Summary
+
Relevant House/Ruler
+
Relevant Uranian Structures
```

สำหรับ Validation:

```text
Pattern Candidate
+
Questions
+
Responses
+
Behavioral Example
```

สำหรับ Action Plan:

```text
Validated Pattern
+
Intervention
+
Goal
+
Current Progress
```

---

# 18. Free Product Mapping

Free ต้องใช้ Pattern Engine เพื่อหา:

```text
Top Blind Spot
Secondary Pattern
Strength
```

แต่เปิดแค่:

- Short explanation
- Limited evidence teaser
- Pattern relationship summary

ไม่เปิด:
- Full Evidence
- Full Validation
- Confidence
- Intervention
- Action Plan
- Personal AI Session

---

# 19. 99 Product Mapping

99 ใช้:

```text
Free Pattern
↓
Validation
↓
Behavioral Evidence
↓
Optional Origin / Context
↓
Pattern Confidence
↓
Personal Report
↓
AI × 3
```

Origin exploration ต้อง adaptive และไม่จำเป็นต้องถามทุกคน

---

# 20. 599 Product Mapping

599 ใช้:

```text
Validated Pattern
↓
Intervention Selection
↓
Goal
↓
Action Plan
↓
Worksheet
↓
Check-in
↓
Progress
```

---

# 21. Professional Product Mapping

1,999 ใช้ Pattern Engine แบบเปิดรายละเอียด:

```text
Chart
↓
Western Signals
↓
House Rulers
↓
Aspects
↓
Uranian 90°
↓
Midpoints
↓
Planetary Pictures
↓
Pattern
↓
Evidence Matrix
↓
AI Interpretation
```

Professional user ต้องเห็น raw evidence ที่มากกว่าผู้ใช้ทั่วไป

---

# 22. What Must Never Happen

ห้าม:

1. Planet placement → Diagnosis
2. One aspect → Psychological conclusion
3. Astrology → दावा cause ของ childhood
4. Uranian picture → Guaranteed future event
5. AI → invent missing chart data
6. AI → invent psychological instrument validity
7. User disagreement → force Pattern to be true

ถ้า User บอก:

> “ไม่ตรงกับฉัน”

ระบบควร:

```text
Pattern = Not Confirmed
↓
Explore alternative Pattern
```

ไม่ใช่พยายามโน้มน้าวว่า:

> “จริง ๆ แล้วคุณเป็นแบบนั้น”

---

# 23. Final Pattern Pipeline

```text
BIRTH DATA
   ↓
ASTRO CALCULATION
   ↓
WESTERN SIGNALS
   ↓
URANIAN SIGNALS
   ↓
PATTERN ENGINE
   ↓
TOP PATTERN CANDIDATES
   ↓
VALIDATION ENGINE
   ↓
BEHAVIORAL EVIDENCE
   ↓
PATTERN CONFIDENCE
   ↓
PSYCHOLOGY INTERVENTION
   ↓
ACTION PLAN
   ↓
TRACKING
```

---

# 24. MVP Pattern Scope

เริ่มด้วย 6 Pattern:

1. Procrastination
2. Perfectionism
3. Decision Avoidance
4. Self-Efficacy
5. Values / Direction
6. Rumination

ค่อยเพิ่ม:

7. Fear of Failure
8. Goal Failure
9. Avoidance
10. People-Pleasing
11. Emotional Reactivity
12. Habit Maintenance

---

# 25. Final Principle

Astrology/Uranian ไม่ได้ทำหน้าที่บอก:

> “นี่คือความจริงของคุณ”

แต่ทำหน้าที่:

> **“นี่คือ Pattern ที่ระบบมองเห็นและคิดว่าน่าจะคุ้มค่าให้คุณสำรวจ”**

จากนั้นผู้ใช้เป็นคนบอกว่า:

> “ใช่ / ไม่ใช่ / บางส่วน”

แล้วระบบจึงค่อยนำไปสู่:

> **Validated Pattern → Intervention → Action → Growth**

นี่คือหลักการที่ต้องรักษาไว้ตลอดการพัฒนา Astro-Zodiac

# Pattern Library Consistency Amendment — v1

The 12 MVP Patterns are one shared Pattern Library.

Package behavior is an access-depth rule:
- Free: rank and expose Top 3
- 99: validate selected pattern(s)
- 599: analyze relationships/clusters and map to intervention
- Professional: expose deeper technical evidence and analysis tools

Pattern IDs remain stable across packages.
