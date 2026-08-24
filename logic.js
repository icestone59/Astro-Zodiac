// logic.js - Evolutionary Astrology Engine Bridge

let currentChartData = null;

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
