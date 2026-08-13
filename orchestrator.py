import requests
import openai

RENDER_API_URL = "https://astro-zodiac.onrender.com"
OPENAI_API_KEY = "your-openai-api-key"

client = openai.OpenAI(api_key=OPENAI_API_KEY)

def fetch_astro_data(birth_info: dict):
    """ดึงข้อมูล Natal และ Transit จาก Render Engine"""
    natal_res = requests.post(f"{RENDER_API_URL}/natal", json=birth_info).json()
    transit_res = requests.get(f"{RENDER_API_URL}/transit").json()
    return natal_res, transit_res

def generate_astrology_report(birth_info: dict, user_question: str = None):
    natal_data, transit_data = fetch_astro_data(birth_info)
    
    system_prompt = """
    คุณคือนักโหราศาสตร์สากลเชิงพัฒนาศักยภาพ (Psychological & Evolutionary Astrologer)
    หน้าที่ของคุณคือประมวลผลข้อมูลองศาดาวเพื่อแนะนำแนวทางพัฒนาชีวิต
    โทนเสียง: ผู้เชี่ยวชาญ มีหลักการ ตรงประเด็น ไม่อ้อมค้อม ไม่เพ้อเจ้อ

    [กรณีที่ 1: ไม่ระบุคำถามเฉพาะเจาะจง]
    วิเคราะห์พื้นดวงจาก Birth Chart โดยแบ่งตาม 7 หัวข้อนี้อย่างเคร่งครัด:
    1. นิสัย บุคลิกภาพ (ประมวลผล ASC, Sun, Moon, House 1)
    2. การเงิน (ประมวลผล House 2, House 8, Venus)
    3. การงาน อาชีพ ที่ตรงกับดวง (ประมวลผล MC/House 10, House 6, Saturn)
    4. ความรัก (ประมวลผล House 7, House 5, Venus, Mars)
    5. จุดเด่น จุดด้อย และการแก้จุดด้อย (วิเคราะห์ดาวเข้มแข็ง vs มุมขัดแย้ง 90°/180° และ Chiron)
    6. ศักยภาพที่มี และวิธีการพัฒนา (วิเคราะห์ North Node vs South Node, Jupiter)
    7. ปัญหาที่ต้องปรับปรุง เพื่อความก้าวหน้า (วิเคราะห์ Saturn, House 12, Self-Limiting Beliefs)

    [กรณีที่ 2: มีคำถามเฉพาะเจาะจง]
    สแกนมุมสัมพันธ์ (Aspects: 0°, 60°, 90°, 120°, 180° | Orb <= 4°) ระหว่าง Transit และ Birth Chart:
    - หากถามเรื่องงาน: สแกน T-Jupiter/T-Saturn กับ House 10, 6, 2 หรือ MC เพื่อระบุช่วงเดือนและแอ็กชันเชิงรุก
    - หากถามเรื่องวิธีแก้ปัญหา: สแกนดาวจรตึงเครียด (T-Saturn, T-Pluto, T-Uranus) เพื่อหาต้นตอ แล้วหาดาวจร/ดาวเดิมที่ทำมุม 60°/120° ช่วยเหลือเพื่อระบุ "ทางออกเชิงพฤติกรรม"
    """

    user_payload = f"""
    [Birth Chart Data]
    {natal_data}

    [Real-time Transit Data]
    {transit_data}

    [User Question]
    {user_question if user_question else "ขอการวิเคราะห์พื้นดวง 7 หัวข้อ"}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_payload}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content

# --- ตัวอย่างการใช้งาน ---
user_birth_input = {
    "year": 1995, "month": 5, "day": 15,
    "hour": 14, "minute": 30,
    "lat": 13.7563, "lon": 100.5018,
    "timezone": "Asia/Bangkok"
}

# 1. พยากรณ์พื้นดวง 7 หัวข้อ
# print(generate_astrology_report(user_birth_input))

# 2. ตอบคำถามด้วย Transit + Natal
# print(generate_astrology_report(user_birth_input, user_question="ผมจะได้งานใหม่เมื่อไหร่?"))
