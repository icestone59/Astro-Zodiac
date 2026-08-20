// logic.js - Core Engine สำหรับเชื่อมต่อ Backend และจัดการ UI

let currentChartData = null;
let radarChartInstance = null;
let barChartInstance = null;

// 1. ฟังก์ชันเชื่อมต่อ Backend แบบป้องกัน Error
async function safeFetchJson(url, options) {
    const res = await fetch(url, options);
    const contentType = res.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
        throw new Error(`Backend Error (HTTP ${res.status}): เซิร์ฟเวอร์ไม่ตอบสนองเป็น JSON`);
    }
    const data = await res.json();
    if (!res.ok || data.status === "error") throw new Error(data.message || "เกิดข้อผิดพลาดในการประมวลผล");
    return data;
}

// 2. ฟังก์ชันอัปเดตข้อความสถานะบนหน้าจอ (UI State)
function showStatus(message, state = "loading") {
    const statusText = document.getElementById("status-text");
    const statusPill = document.getElementById("status-pill");

    if (statusText) statusText.textContent = message;
    
    if (statusPill) {
        if (state === "loading") {
            statusPill.textContent = "Processing...";
            statusPill.style.color = "#f59e0b";
        } else if (state === "error") {
            statusPill.textContent = "Error";
            statusPill.style.color = "#ef4444";
            if (statusText) statusText.style.color = "#ef4444";
        } else if (state === "success") {
            statusPill.textContent = "Ready";
            statusPill.style.color = "#10b981";
            if (statusText) statusText.style.color = "#c084fc";
        }
    }
}

// 3. ฟังก์ชันคำนวณและวิเคราะห์อัตโนมัติ (Intelligent Flow)
async function calculateChart() {
    showStatus("กำลังดึงตำแหน่งดาวกำเนิดและดาวจร (Real-time)...", "loading");
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

        // 3.1 คำนวณองศาดาว
        currentChartData = await safeFetchJson('/calculate_chart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        // 3.2 ตรวจสอบว่ามีคำถาม Transit หรือไม่
        const questionEl = document.getElementById("question");
        const question = questionEl ? questionEl.value.trim() : "";

        // 3.3 สั่งรัน AI ทันทีตามเงื่อนไข (ไม่ต้องรอให้ผู้ใช้กดปุ่มซ้ำ)
        if (question !== "") {
            showStatus("กำลังวิเคราะห์คำถามเจาะจงผ่านดาวจร (Transit)...", "loading");
            await analyzeAI('transit_qa');
        } else {
            showStatus("กำลังวิเคราะห์พื้นดวงชะตา 7 หมวดหมู่...", "loading");
            await analyzeAI('natal_7');
        }

    } catch (error) {
        showStatus(error.message, "error");
    } finally {
        if (btn) btn.disabled = false;
    }
}

// 4. ฟังก์ชันส่งข้อมูลให้ AI วิเคราะห์
async function analyzeAI(reportType) {
    if (!currentChartData) {
        alert("ข้อมูลดวงชะตายังไม่ถูกคำนวณ กรุณากดคำนวณตำแหน่งดาวก่อน");
        return;
    }

    if (reportType === 'deep_report') {
        showStatus("กำลังสกัดโครงสร้างจิตวิทยาระดับลึก (Deep Report)...", "loading");
    }
    
    if(document.getElementById("default-message")) document.getElementById("default-message").style.display = "none";
    document.getElementById("report-content").innerHTML = "";
    document.getElementById("charts-wrapper").style.display = "none";

    const payload = {
        user_name: document.getElementById("user_name").value,
        chart_data: currentChartData,
        report_type: reportType,
        question: document.getElementById("question") ? document.getElementById("question").value : ""
    };

    try {
        const data = await safeFetchJson('/analyze_ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        // สร้างกราฟเฉพาะเมื่อเป็น Deep Report
        if (reportType === 'deep_report' && data.radar_data) {
            document.getElementById("charts-wrapper").style.display = "flex";
            renderCharts(data.radar_data, data.bar_data);
        }

        // แสดงผลลัพธ์
        let reportText = data.report || data.answer;
        document.getElementById("report-content").innerHTML = marked.parse(reportText);
        showStatus("การประมวลผลเสร็จสมบูรณ์", "success");
    } catch (error) {
        showStatus(error.message, "error");
    }
}

// 5. ระบบวาดกราฟศักยภาพ (Dark Uranian Style)
function renderCharts(radarData, barData) {
    if (radarChartInstance) radarChartInstance.destroy();
    if (barChartInstance) barChartInstance.destroy();

    const chartConfig = {
        color: '#e2e8f0', 
        gridColor: 'rgba(255, 255, 255, 0.05)',
        primary: '#a78bfa',
        primaryBg: 'rgba(167, 139, 250, 0.2)'
    };

    if (radarData && radarData.length > 0) {
        const ctxRadar = document.getElementById('potentialRadarChart').getContext('2d');
        radarChartInstance = new Chart(ctxRadar, {
            type: 'radar',
            data: {
                labels: radarData.map(item => item.name),
                datasets: [{
                    label: 'Potential Map',
                    data: radarData.map(item => item.score),
                    backgroundColor: chartConfig.primaryBg,
                    borderColor: chartConfig.primary,
                    pointBackgroundColor: chartConfig.primary
                }]
            },
            options: {
                scales: { 
                    r: { 
                        min: 0, max: 100, 
                        grid: { color: chartConfig.gridColor }, 
                        ticks: { display: false }, 
                        pointLabels: { color: chartConfig.color, font: { family: 'Sarabun' } } 
                    } 
                },
                plugins: { legend: { display: false } }
            }
        });
    }

    if (barData && barData.length > 0) {
        const ctxBar = document.getElementById('potentialBarChart').getContext('2d');
        barChartInstance = new Chart(ctxBar, {
            type: 'bar',
            data: {
                labels: barData.map(item => item.name),
                datasets: [
                    { label: 'ศักยภาพ (Potential)', data: barData.map(item => item.potential), backgroundColor: '#3b82f6' },
                    { label: 'ใช้งานจริง (Activation)', data: barData.map(item => item.activation), backgroundColor: '#10b981' },
                    { label: 'แรงต้าน (Block)', data: barData.map(item => item.block), backgroundColor: '#ef4444' }
                ]
            },
            options: {
                responsive: true,
                scales: { 
                    y: { min: 0, max: 100, grid: { color: chartConfig.gridColor }, ticks: { color: chartConfig.color } },
                    x: { grid: { display: false }, ticks: { color: chartConfig.color, font: { family: 'Sarabun' } } }
                },
                plugins: { legend: { labels: { color: chartConfig.color, font: { family: 'Sarabun' } } } }
            }
        });
    }
}
