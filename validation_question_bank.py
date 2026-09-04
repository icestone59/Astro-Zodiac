"""Astro-Zodiac T8 — custom MVP validation question bank.

Questions are custom Astro-Zodiac items informed by the project's psychology
reference library. They are not the original items from named instruments.
"""
from __future__ import annotations

from typing import Dict, Tuple
from validation_schema import ValidationQuestion

QUESTION_BANK: Dict[str, Tuple[ValidationQuestion, ...]] = {
    "P01": tuple(
        ValidationQuestion(question_id=f"P01-Q{i}", pattern_id="P01", text=text, response_type="frequency")
        for i, text in enumerate(
            [
                "ฉันเลื่อนงานสำคัญแม้รู้ว่าควรเริ่ม",
                "ฉันมักเริ่มงานเมื่อใกล้ถึงกำหนด",
                "เมื่อเจองานที่ยาก ฉันมักไปทำอย่างอื่นก่อน",
                "ฉันมักบอกตัวเองว่า “ไว้พร้อมกว่านี้ค่อยทำ”",
                "ฉันตั้งใจจะทำ แต่เริ่มจริงช้ากว่าที่วางแผน",
            ], 1)
    ),
    "P02": tuple(
        ValidationQuestion(question_id=f"P02-Q{i}", pattern_id="P02", text=text, response_type="agreement")
        for i, text in enumerate(
            [
                "ฉันรู้สึกว่างานยังไม่ดีพอแม้คนอื่นจะบอกว่าดีแล้ว",
                "ฉันใช้เวลานานกับการแก้งานเพื่อให้สมบูรณ์ขึ้น",
                "ฉันไม่ค่อยอยากส่งงานถ้ายังเห็นข้อผิดพลาด",
                "ฉันบางครั้งไม่เริ่มเพราะกลัวทำออกมาไม่ดี",
                "ความผิดพลาดเล็ก ๆ ทำให้ฉันคิดถึงเรื่องนั้นนาน",
            ], 1)
    ),
    "P03": tuple(
        ValidationQuestion(question_id=f"P03-Q{i}", pattern_id="P03", text=text, response_type="agreement")
        for i, text in enumerate(
            [
                "ฉันใช้เวลานานกับการตัดสินใจแม้เป็นเรื่องเล็ก",
                "ฉันมักหาข้อมูลเพิ่มแม้มีข้อมูลเพียงพอแล้ว",
                "ฉันกังวลว่าจะเสียใจหลังตัดสินใจ",
                "ฉันมักขอความเห็นจากหลายคนก่อนตัดสินใจ",
                "ฉันเคยปล่อยเรื่องสำคัญไว้นานเพราะไม่กล้าเลือก",
            ], 1)
    ),
    "P05": (
        ValidationQuestion(question_id="P05-Q1", pattern_id="P05", text="เมื่อเจอปัญหา ฉันมักเชื่อว่าตัวเองหาทางแก้ได้", response_type="agreement", reverse_scored=True),
        ValidationQuestion(question_id="P05-Q2", pattern_id="P05", text="เมื่อเจอเรื่องใหม่ ฉันเชื่อว่าฉันเรียนรู้ได้", response_type="agreement", reverse_scored=True),
        ValidationQuestion(question_id="P05-Q3", pattern_id="P05", text="อุปสรรคทำให้ฉันหมดความมั่นใจง่าย", response_type="agreement"),
        ValidationQuestion(question_id="P05-Q4", pattern_id="P05", text="ฉันมักคิดว่าคนอื่นทำได้ แต่ฉันทำไม่ได้", response_type="agreement"),
        ValidationQuestion(question_id="P05-Q5", pattern_id="P05", text="ฉันเชื่อว่าตัวเองสามารถรับมือกับเรื่องยากได้", response_type="agreement", reverse_scored=True),
    ),
    "P06": (
        ValidationQuestion(question_id="P06-Q1", pattern_id="P06", text="ฉันรู้ว่าอะไรสำคัญกับชีวิตของฉัน", response_type="agreement", reverse_scored=True),
        ValidationQuestion(question_id="P06-Q2", pattern_id="P06", text="เป้าหมายที่ฉันทำอยู่สอดคล้องกับสิ่งที่ฉันให้คุณค่าหรือไม่", response_type="agreement", reverse_scored=True),
        ValidationQuestion(question_id="P06-Q3", pattern_id="P06", text="ฉันเคยทำสิ่งที่คนอื่นคาดหวังแม้ไม่ใช่สิ่งที่ฉันต้องการ", response_type="agreement"),
        ValidationQuestion(question_id="P06-Q4", pattern_id="P06", text="เมื่อมีหลายทางเลือก ฉันรู้ว่าอะไรสำคัญที่สุด", response_type="agreement", reverse_scored=True),
        ValidationQuestion(question_id="P06-Q5", pattern_id="P06", text="ช่วงนี้ฉันรู้สึกว่าชีวิตกำลังไปในทิศทางที่มีความหมาย", response_type="agreement", reverse_scored=True),
    ),
    "P08": tuple(
        ValidationQuestion(question_id=f"P08-Q{i}", pattern_id="P08", text=text, response_type="agreement")
        for i, text in enumerate(
            [
                "ฉันคิดเรื่องเดิมซ้ำ ๆ แม้ยังหาทางออกไม่ได้",
                "ฉันย้อนคิดถึงสิ่งที่เกิดขึ้นหลายครั้ง",
                "ฉันใช้เวลามากในการคิดว่า “ทำไมมันถึงเกิดขึ้น”",
                "การคิดมากทำให้ฉันลงมือแก้ปัญหาช้าลง",
                "ฉันพบว่าการคิดต่อไม่ได้ทำให้สถานการณ์ดีขึ้น แต่หยุดคิดยาก",
            ], 1)
    ),
}


def get_questions(pattern_id: str, *, limit: int = 8) -> Tuple[ValidationQuestion, ...]:
    """Return the MVP question route for one supported pattern."""
    if pattern_id not in QUESTION_BANK:
        raise KeyError(f"Unsupported validation pattern: {pattern_id}")
    if limit < 1:
        raise ValueError("limit must be >= 1")
    return QUESTION_BANK[pattern_id][:limit]
