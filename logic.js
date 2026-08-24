// logic.js - Evolutionary Astrology Engine Bridge

let currentChartData = null;

// ฟังก์ชันยิง API แบบตรวจสอบข้อผิดพลาดรัดกุม
async function safeFetchJson(url, options) {
    try {
        const res = await fetch(url, options);
        const contentType = res.headers.get("content-type") || "";
        
        if (!contentType.includes("application/json")) {
            throw new Error(`Server Response Error (HTTP ${res.status}): ไม่ได้รับข้อมูล JSON`);
        }
        
        const data = await res.json();
        if (!res.ok || data.status === "error") {
            throw new Error(data.message || "เกิดข้อผิดพลาดในการประมวลผลข้อมูล");
        }
        return data;
    } catch (err) {
        console.error("[API Error]:", err);
        throw err;
    }
}

// ฟังก์ชันอัปเดตสถานะบนหน้าจอ
function updateStatus(message, isError = false) {
    const statusText = document.getElementById("status-text");
    const statusPill = document.getElementById("status-pill");
    
    if (statusText) {
        statusText.textContent = message;
        statusText.style.color = isError ? "#ef4444" : "#c084fc";
    }
    if (statusPill) {
        statusPill.textContent = isError ? "Error" : "Processing";
        statusPill.style.color = isError ? "#ef4444" : "#f59e0b";
    }
}

// 1. คำนวณองศาดาวกำเนิด และ ดาวจร Real-time
async function calculateChart() {
    const btn = document.getElementById("btn-calculate");
    if (btn) btn.disabled = true;
    
    updateStatus("กำลังคำนวณตำแหน่งดาวกำเนิดและดาวจร Real-time...");

    try {
        // ดึงค่าจากฟอร์มพร้อมตรวจทานประเภทข้อมูล
        const payload = {
            day: parseInt(document.getElementById("day")?.value || "1"),
            month: parseInt(document.getElementById("month")?.value || "1"),
            year: parseInt(document.getElementById("year")?.value || "2000"),
            hour: parseInt(document.getElementById("hour")?.value || "0"),
            minute: parseInt(document.getElementById("minute")?.value || "0"),
            location_name: document.getElementById("location_name")?.value || "กรุงเทพมหานคร"
        };

        // ยิงคำนวณ Swisseph ดาราศาสตร์
        currentChartData = await safeFetchJson('/calculate_chart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        // สลับแสดงผลตามคำถาม (Transit Q&A หรือ Natal 7)
        const questionInput = document.getElementById("question");
        const userQuestion = questionInput ? questionInput.value.trim() : "";

        if (userQuestion !== "") {
            updateStatus("กำลังวิเคราะห์คำถามผ่านมุมดาวจร Real-time (Transit)...");
            await analyzeAI('transit_qa');
        } else {
            updateStatus("กำลังประมวลผลวิเคราะห์พื้นดวงชะตา 7 หมวดหมู่...");
            await analyzeAI('natal_7');
        }

    } catch (error) {
        updateStatus(`ขัดข้อง: ${error.message}`, true);
    } finally {
        if (btn) btn.disabled = false;
    }
}

// 2. วิเคราะห์ AI สำหรับ 7 หมวดหมู่พื้นดวง และ Transit Q&A
async function analyzeAI(reportType) {
    if (!currentChartData) {
        alert("กรุณากรอกข้อมูลวันเวลาเกิดแล้วกดคำนวณก่อนครับ");
        return;
    }

    const defaultMsg = document.getElementById("default-message");
    const outputTarget = document.getElementById("natal-report-content") || document.getElementById("report-content");
    
    if (defaultMsg) defaultMsg.style.display = "none";
    if (outputTarget) outputTarget.innerHTML = "<p style='color:#a78bfa;'>กำลังสกัดโครงสร้างดวงดาวและประมวลผลบทวิเคราะห์...</p>";

    const payload = {
        user_name: document.getElementById("user_name")?.value || "คุณ",
        chart_data: currentChartData,
        report_type: reportType,
        question: document.getElementById("question")?.value || ""
    };

    try {
        const data = await safeFetchJson('/analyze_ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const reportMarkdown = data.report || data.answer || "ไม่พบผลการวิเคราะห์";
        
        if (outputTarget) {
            outputTarget.innerHTML = marked.parse(reportMarkdown);
        }

        const statusPill = document.getElementById("status-pill");
        if (statusPill) {
            statusPill.textContent = "Ready";
            statusPill.style.color = "#10b981";
        }
        updateStatus("การวิเคราะห์เสร็จสมบูรณ์");

    } catch (error) {
        updateStatus(`วิเคราะห์ไม่สำเร็จ: ${error.message}`, true);
    }
}
