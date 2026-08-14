@app.post("/analyze")
def analyze_chart(req: AnalysisRequest):
    """
    3. Endpoint ประมวลผลหลัก:
       - คำนวณ Birth Chart + Real-time Transit
       - หากไม่มีคำถาม: คืนค่าผลพยากรณ์พื้นดวง 7 หมวดหมู่ (Local DB -> Fallback AI)
       - หากมีคำถาม: ประมวลผล Transit vs Natal ตอบคำถามเจาะจง
    """
    try:
        # Step A: พิกัดและเวลาเกิด
        loc = geolocator.geocode(req.location_name, timeout=10)
        if not loc:
            raise HTTPException(status_code=400, detail="ไม่พบพิกัดสถานที่เกิดที่ระบุ")
        
        lat, lon = loc.latitude, loc.longitude
        tz_str = tf.timezone_at(lng=lon, lat=lat) or "UTC"
        local_tz = pytz.timezone(tz_str)
        local_dt = local_tz.localize(datetime(req.year, req.month, req.day, req.hour, req.minute))
        utc_dt = local_dt.astimezone(pytz.utc)

        # Step B: คำนวณ Birth Chart และ Real-time Transit
        natal_planets, natal_houses = _calculate_chart_data(utc_dt, lat, lon)
        now_utc = datetime.now(pytz.utc)
        transit_planets, _ = _calculate_chart_data(now_utc, lat, lon)

        # --- สร้างรูป Birth Chart SVG สไตล์ Astro-Seek ---
        # กรองเฉพาะดาวหลัก 12 ดวงเพื่อส่งไปวาด
        target_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto', 'North_Node', 'Chiron']
        simple_planets = {p: natal_planets[p]['absolute_degree'] for p in target_planets}
        simple_houses = [natal_houses[f'House_{i+1}']['absolute_degree'] for i in range(12)]
        asc_deg = natal_planets['ASC']['absolute_degree']
        
        chart_svg = generate_astroseek_svg(simple_planets, simple_houses, asc_deg)

        # --------------------------------------------------------------
        # CASE 1: พยากรณ์พื้นดวง 7 หมวดหมู่ (ไม่มีคำถาม)
        # --------------------------------------------------------------
        if not req.question:
            local_db_res = execute_7_modules_analysis(natal_planets, natal_houses)

            # หากข้อมูลใน Local DB สมบูรณ์ ส่งกลับทันที
            if local_db_res["is_complete"]:
                return {
                    "source": "local_db",
                    "cost_baht": 0.0,
                    "location_info": {"address": loc.address, "timezone": tz_str},
                    "birth_chart_degrees": natal_planets,
                    "report": local_db_res["report"],
                    "chart_svg": chart_svg
                }

            # Fallback ไปที่ OpenAI API หาก Local DB ข้อมูลยังไม่ครบ 100%
            if not client:
                return {
                    "source": "local_db_partial",
                    "location_info": {"address": loc.address, "timezone": tz_str},
                    "birth_chart_degrees": natal_planets,
                    "report": local_db_res["report"],
                    "chart_svg": chart_svg
                }

            system_prompt = """
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Psychological & Evolutionary Astrologer)
หน้าที่: วิเคราะห์พื้นดวงชะตาเพื่อแนะนำการพัฒนาตนเอง ทลายข้อจำกัดทางจิตวิทยา และปลดล็อกศักยภาพ

ข้อกำหนดเรื่องโทนเสียงและรูปแบบอย่างเคร่งครัด:
1. โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น กระชับ ไม่อ้อมค้อม ไม่เพ้อเจ้อ
2. ห้ามใช้คำทักทาย อารัมภบท หรือคำอวยพรเด็ดขาด
3. แบ่งเนื้อหาออกเป็น 7 หัวข้อหลักอย่างชัดเจน:
   1. นิสัย บุคลิกภาพ
   2. การเงิน
   3. การงาน อาชีพ ที่ตรงกับดวง
   4. ความรัก
   5. จุดเด่น จุดด้อย และการแก้จุดด้อย
   6. ศักยภาพที่มี และวิธีการพัฒนา
   7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า
"""
            user_content = f"[Birth Chart Data]\n{natal_planets}"

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.2
            )

            return {
                "source": "openai_api_fallback",
                "location_info": {"address": loc.address, "timezone": tz_str},
                "birth_chart_degrees": natal_planets,
                "report": response.choices[0].message.content,
                "chart_svg": chart_svg
            }

        # --------------------------------------------------------------
        # CASE 2: พยากรณ์ตามคำถามเจาะจง (Transit + Birth Chart)
        # --------------------------------------------------------------
        else:
            # ตรวจสอบคำตอบจาก Local Transit DB ก่อน
            conn = sqlite3.connect("astro_rules.db") if os.path.exists("astro_rules.db") else None
            db_answer = None
            if conn:
                cursor = conn.cursor()
                if "งาน" in req.question:
                    cursor.execute("SELECT solution_text FROM transit_interpretations WHERE question_type = 'career_timing'")
                elif "ปัญหา" in req.question:
                    cursor.execute("SELECT solution_text FROM transit_interpretations WHERE question_type = 'problem_solving'")
                row = cursor.fetchone()
                if row:
                    db_answer = row[0]
                conn.close()

            if db_answer:
                return {
                    "source": "local_db",
                    "cost_baht": 0.0,
                    "question": req.question,
                    "answer": db_answer,
                    "chart_svg": chart_svg
                }

            # Fallback ไปที่ OpenAI API ประมวลผลมุมสัมพันธ์ Transit vs Natal (Orb <= 4°)
            if not client:
                raise HTTPException(status_code=500, detail="OPENAI_API_KEY is not configured on server")

            qa_system_prompt = """
คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ
หน้าที่: คำนวณระยะมุมสัมพันธ์ (Orb <= 4°) ระหว่าง Transit (T) และ Birth Chart (N) เพื่อตอบคำถามผู้ใช้

ข้อกำหนดการตอบ:
1. โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น กระชับ ไม่อ้อมค้อม ตัดคำทักทายออกทั้งหมด
2. ระบุช่วงเวลา/เดือนที่องศาดาวจรทำมุมส่งผลชัดเจน
3. ชี้สาเหตุปัญหาทางจิตวิทยา/พฤติกรรม และกำหนดทางออกเชิงพฤติกรรม (Actionable Steps) ทันที
"""
            qa_user_content = f"คำถาม: \"{req.question}\"\n\n[Birth Chart]\n{natal_planets}\n\n[Real-time Transit]\n{transit_planets}"

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": qa_system_prompt},
                    {"role": "user", "content": qa_user_content}
                ],
                temperature=0.2
            )

            return {
                "source": "openai_api_qa",
                "question": req.question,
                "answer": response.choices[0].message.content,
                "chart_svg": chart_svg
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis Error: {str(e)}")
