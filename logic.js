// logic.js - Evolutionary Astrology Engine Bridge

let currentChartData = null;
let currentReportType = 'natal_7';

// คลังเก็บ Memory Cache ฝั่ง Frontend (ป้องกันการยิง API ซ้ำ)
const reportCache = {
    client: null,
    astrologer: null
};

// ดึงโหมดปัจจุบันจาก Toggle
function getSelectedMode() {
    const toggle = document.getElementById("mode-toggle");
    return (toggle && toggle.checked) ? "astrologer" : "client";
}

// ฟังก์ชันสลับโหมดทันที (0 วินาที ไม่ยิง API หากมี Cache อยู่แล้ว)
async function handleModeToggle() {
    const mode = getSelectedMode();
    const outputTarget = document.getElementById("natal-report-content") || document.getElementById("report-content");

    // 1. เช็ก Memory Cache ฝั่ง Frontend ก่อน
    if (reportCache[mode]) {
        console.log(`[FRONTEND CACHE HIT]: Switching to ${mode} mode instantly.`);
        if (outputTarget) outputTarget.innerHTML = marked.parse(reportCache[mode]);
        return;
    }

    // 2. ถ้าใน Frontend Memory ยังไม่มี ให้เรียกประมวลผล (ซึ่ง Backend จะไปเช็ก DB Cache ต่อ)
    if (currentChartData) {
        await analyzeAI(currentReportType);
    }
}

// logic.js - Async Request with Explicit Timeout & Fallback

async function fetchWithTimeout(resource, options = {}) {
    const { timeout = 25000 } = options; // ล็อค Timeout ไว้ที่ 25 วินาที
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(resource, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        throw error;
    }
}

async function calculateChart() {
    const btn = document.getElementById("btn-calculate");
    if (btn) btn.disabled = true;

    try {
        const payload = {
            day: parseInt(document.getElementById("day").value),
            month: parseInt(document.getElementById("month").value),
            year: parseInt(document.getElementById("year").value),
            hour: parseInt(document.getElementById("hour").value),
            minute: parseInt(document.getElementById("minute").value),
            location_name: document.getElementById("location_name").value
        };

        const res = await fetchWithTimeout('/calculate_chart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
            timeout: 10000
        });

        const data = await res.json();
        if (!res.ok || data.status === "error") throw new Error(data.message || "คำนวณตำแหน่งดาวไม่สำเร็จ");

        currentChartData = data;

        // เช็กว่ามีคำถาม Transit Q&A หรือไม่
        const questionInput = document.getElementById("question");
        const userQuestion = questionInput ? questionInput.value.trim() : "";

        await analyzeAI(userQuestion !== "" ? 'transit_qa' : 'natal_7');

    } catch (error) {
        if (typeof stopQuoteRotator === 'function') stopQuoteRotator();
        const target = document.getElementById("natal-report-content") || document.getElementById("report-content");
        if (target) {
            target.innerHTML = `<div style="color:#ef4444; padding:20px;">⚠️ เกิดข้อผิดพลาด: ${error.name === 'AbortError' ? 'การเชื่อมต่อใช้เวลานานเกินกำหนด (Timeout)' : error.message}</div>`;
        }
    } finally {
        if (btn) btn.disabled = false;
    }
}

// logic.js - Debug & Error Handler Fix

// logic.js - Catch & Display Full Error Detail

async function analyzeAI(reportType) {
    const target = document.getElementById("natal-report-content") || document.getElementById("report-content");
    const statusPill = document.getElementById("status-pill");

    if (typeof startQuoteRotator === 'function' && target) {
        startQuoteRotator(target.id);
    }

    const payload = {
        user_name: document.getElementById("user_name")?.value || "คุณ",
        chart_data: currentChartData,
        report_type: reportType,
        mode: typeof getSelectedMode === 'function' ? getSelectedMode() : 'client',
        question: document.getElementById("question")?.value || ""
    };

    try {
        const res = await fetch('/analyze_ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        // เช็กสถานะข้อผิดพลาดจาก Backend
        if (!res.ok || data.status === "error") {
            throw new Error(data.message || `HTTP ${res.status}: เกิดข้อผิดพลาดไม่ทราบสาเหตุจากเซิร์ฟเวอร์`);
        }

        if (typeof stopQuoteRotator === 'function') stopQuoteRotator();
        
        const reportText = data.report || data.answer;
        if (target) target.innerHTML = marked.parse(reportText);

        if (statusPill) {
            statusPill.textContent = "Ready";
            statusPill.style.color = "#10b981";
        }

    } catch (error) {
        // หยุดคำคมเมื่อเกิด Error
        if (typeof stopQuoteRotator === 'function') stopQuoteRotator();

        // เขียนรายละเอียด Error ลงกล่องหลักทันที
        if (target) {
            target.innerHTML = `
                <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; border-radius: 12px; padding: 20px; margin: 20px 0;">
                    <h4 style="color: #ef4444; margin: 0 0 8px 0; font-size: 16px;">⚠️ ระบบประมวลผลขัดข้อง (Debug Detail)</h4>
                    <p style="color: #f87171; font-size: 13px; font-family: monospace; white-space: pre-wrap; margin: 0;">${error.message}</p>
                </div>
            `;
        }

        if (statusPill) {
            statusPill.textContent = "Error";
            statusPill.style.color = "#ef4444";
        }
    }
}
// ฟังก์ชันเรียกประมวลผล AI พร้อมส่ง Mode
async function analyzeAI(reportType) {
    if (!currentChartData) return;

    const outputTarget = document.getElementById("natal-report-content") || document.getElementById("report-content");

    // 1. เริ่มแสดงคำคมวนสลับทุก 3 วินาที
    startQuoteRotator(outputTarget.id);

    const payload = {
        user_name: document.getElementById("user_name")?.value || "คุณ",
        chart_data: currentChartData,
        report_type: reportType,
        mode: typeof getSelectedMode === 'function' ? getSelectedMode() : 'client',
        question: document.getElementById("question")?.value || ""
    };

    try {
        const res = await fetch('/analyze_ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok || data.status === "error") throw new Error(data.message);

        // 2. หยุดการแสดงคำคมเมื่อประมวลผลเสร็จสิ้น
        stopQuoteRotator();

        const reportText = data.report || data.answer;
        outputTarget.innerHTML = marked.parse(reportText);

    } catch (error) {
        stopQuoteRotator();
        outputTarget.innerHTML = `<p style="color:#ef4444;">เกิดข้อผิดพลาด: ${error.message}</p>`;
    }
}

// เมื่อกดคำนวณดวงใหม่ ให้ล้าง Memory Cache เก่าทิ้ง
function resetReportCache() {
    reportCache.client = null;
    reportCache.astrologer = null;
}

// 1. ฟังก์ชันคำนวณองศาดาวกำเนิด และ ดาวจร Real-time
async function calculateChart() {
    const btn = document.getElementById("btn-calculate");
    if (btn) btn.disabled = true;
    
    updateStatus("กำลังคำนวณตำแหน่งดาวกำเนิดและดาวจร Real-time...");

    try {
        const payload = {
            day: parseInt(document.getElementById("day").value),
            month: parseInt(document.getElementById("month").value),
            year: parseInt(document.getElementById("year").value),
            hour: parseInt(document.getElementById("hour").value),
            minute: parseInt(document.getElementById("minute").value),
            location_name: document.getElementById("location_name").value
        };

        const res = await fetch('/calculate_chart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok || data.status === "error") throw new Error(data.message || "คำนวณองศาดดาวไม่สำเร็จ");

        currentChartData = data;

        // เช็กคำถาม Transit
        const questionInput = document.getElementById("question");
        const userQuestion = questionInput ? questionInput.value.trim() : "";

        if (userQuestion !== "") {
            updateStatus("กำลังวิเคราะห์คำถามเจาะจงด้วยมุมดาวจร Real-time...");
            await analyzeAI('transit_qa');
        } else {
            updateStatus("กำลังวิเคราะห์พื้นดวงชะตา 7 หมวดหมู่...");
            await analyzeAI('natal_7');
        }

    } catch (error) {
        updateStatus(`เกิดข้อผิดพลาด: ${error.message}`, true);
    } finally {
        if (btn) btn.disabled = false;
    }
}

// 2. ฟังก์ชันวิเคราะห์ AI (Natal 7 และ Transit Q&A)
async function analyzeAI(reportType) {
    if (!currentChartData) {
        alert("กรุณากรอกข้อมูลวันเวลาเกิดแล้วกด 'คำนวณตำแหน่งดาว' ก่อนครับ");
        return;
    }

    const outputTarget = document.getElementById("report-content") || document.getElementById("natal-report-content");
    const defaultMsg = document.getElementById("default-message");
    
    if (defaultMsg) defaultMsg.style.display = "none";
    if (outputTarget) outputTarget.innerHTML = "<p style='color:#a78bfa;'>กำลังประมวลผลบทวิเคราะห์โหราศาสตร์...</p>";

    const payload = {
        user_name: document.getElementById("user_name").value,
        chart_data: currentChartData,
        report_type: reportType,
        question: document.getElementById("question") ? document.getElementById("question").value : ""
    };

    try {
        const res = await fetch('/analyze_ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();
        if (!res.ok || data.status === "error") throw new Error(data.message || "การประมวลผล AI ขัดข้อง");

        let reportText = data.report || data.answer;
        if (outputTarget) outputTarget.innerHTML = marked.parse(reportText);

        updateStatus("การวิเคราะห์เสร็จสมบูรณ์");
    } catch (error) {
        updateStatus(`วิเคราะห์ไม่สำเร็จ: ${error.message}`, true);
    }
}

// 3. ฟังก์ชันสำหรับปุ่มสีส้ม "กดดูชะตาของคุณ" (เปิดหน้า deepreport.html แยกระบบ)
function openDeepReportPage() {
    if (!currentChartData) {
        alert("กรุณากด 'คำนวณตำแหน่งดาวและวิเคราะห์' ที่แถบซ้ายมือก่อนเปิดดูรายงานปมลึกครับ");
        return;
    }

    const payload = {
        user_name: document.getElementById("user_name").value,
        chart_data: currentChartData,
        question: document.getElementById("question") ? document.getElementById("question").value : ""
    };

    // ฝาก payload ลง localStorage แล้วเปิดแท็บใหม่
    localStorage.setItem("deep_report_payload", JSON.stringify(payload));
    window.open('/deepreport', '_blank');
}

function updateStatus(message, isError = false) {
    const statusText = document.getElementById("status-text");
    const statusPill = document.getElementById("status-pill");
    if (statusText) {
        statusText.textContent = message;
        statusText.style.color = isError ? "#ef4444" : "#c084fc";
    }
    if (statusPill) {
        statusPill.textContent = isError ? "Error" : "Ready";
        statusPill.style.color = isError ? "#ef4444" : "#10b981";
    }
}
