// logic.js - จัดการ API และ Chart.js ล้วนๆ ไม่ยุ่งกับ CSS

let currentChartData = null;
let radarChartInstance = null;
let barChartInstance = null;

// 1. HTTP Utility
async function safeFetchJson(url, options) {
    const res = await fetch(url, options);
    const contentType = res.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
        throw new Error(`Server Error (HTTP ${res.status}): ระบบหลังบ้านขัดข้อง`);
    }
    const data = await res.json();
    if (!res.ok || data.status === "error") throw new Error(data.message || "API Error");
    return data;
}

// 2. UI Helper
function showStatus(message, isError = false) {
    const el = document.getElementById("status-message");
    el.style.display = "block";
    el.textContent = message;
    el.className = isError ? "error-text" : "";
}

// 3. ฟังก์ชันคำนวณตำแหน่งดาว (ส่งข้อมูลไปให้ astro_calc.py)
async function calculateChart() {
    showStatus("กำลังคำนวณองศาดาวกำเนิดและดาวจร (Real-time)...");
    document.getElementById("btn-calculate").disabled = true;

    try {
        const payload = {
            day: parseInt(document.getElementById("day").value),
            month: parseInt(document.getElementById("month").value),
            year: parseInt(document.getElementById("year").value),
            hour: parseInt(document.getElementById("hour").value),
            minute: parseInt(document.getElementById("minute").value),
            location_name: document.getElementById("location_name").value
        };

        currentChartData = await safeFetchJson('/calculate_chart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        showStatus("ดึงข้อมูลดาวจรและผูกดวงชะตาสำเร็จ! เลือกหมวดหมู่การวิเคราะห์ได้เลย");
    } catch (error) {
        showStatus(error.message, true);
    } finally {
        document.getElementById("btn-calculate").disabled = false;
    }
}

// 4. ฟังก์ชันเรียก AI วิเคราะห์
async function analyzeAI(reportType) {
    if (!currentChartData) return alert("กรุณากด 'คำนวณองศาดาว' ก่อนครับ");

    showStatus("AI กำลังวิเคราะห์เจาะลึก (อาจใช้เวลา 15-30 วินาที)...");
    document.getElementById("result-panel").style.display = "block";
    document.getElementById("report-content").innerHTML = "";
    document.getElementById("charts-wrapper").style.display = "none";

    const payload = {
        user_name: document.getElementById("user_name").value,
        chart_data: currentChartData,
        report_type: reportType,
        question: document.getElementById("question").value
    };

    try {
        const data = await safeFetchJson('/analyze_ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        // ถ้าเป็นโหมด Deep Report และมีข้อมูลกราฟ ให้วาดกราฟ
        if (reportType === 'deep_report' && data.radar_data) {
            document.getElementById("charts-wrapper").style.display = "flex";
            renderCharts(data.radar_data, data.bar_data);
        }

        // แสดงผล Report เป็น Markdown HTML
        let reportText = data.report || data.answer;
        document.getElementById("report-content").innerHTML = marked.parse(reportText);
        showStatus("การวิเคราะห์เสร็จสมบูรณ์!");
    } catch (error) {
        showStatus(error.message, true);
    }
}

// 5. ระบบวาดกราฟ Chart.js (Dark Uranian Data)
function renderCharts(radarData, barData) {
    if (radarChartInstance) radarChartInstance.destroy();
    if (barChartInstance) barChartInstance.destroy();

    const chartConfig = {
        color: '#94a3b8',
        gridColor: 'rgba(255, 255, 255, 0.05)',
        primary: 'rgba(139, 92, 246, 1)',   // Purple
        primaryBg: 'rgba(139, 92, 246, 0.2)'
    };

    if (radarData && radarData.length > 0) {
        const ctxRadar = document.getElementById('potentialRadarChart').getContext('2d');
        radarChartInstance = new Chart(ctxRadar, {
            type: 'radar',
            data: {
                labels: radarData.map(item => item.name),
                datasets: [{
                    label: 'Astrological Potential',
                    data: radarData.map(item => item.score),
                    backgroundColor: chartConfig.primaryBg,
                    borderColor: chartConfig.primary,
                    pointBackgroundColor: chartConfig.primary
                }]
            },
            options: {
                scales: { r: { min: 0, max: 100, grid: { color: chartConfig.gridColor }, ticks: { display: false }, pointLabels: { color: chartConfig.color } } },
                plugins: { legend: { labels: { color: chartConfig.color } } }
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
                    { label: 'Potential', data: barData.map(item => item.potential), backgroundColor: '#3b82f6' },
                    { label: 'Activation', data: barData.map(item => item.activation), backgroundColor: '#10b981' },
                    { label: 'Block', data: barData.map(item => item.block), backgroundColor: '#ef4444' }
                ]
            },
            options: {
                scales: { 
                    y: { min: 0, max: 100, grid: { color: chartConfig.gridColor }, ticks: { color: chartConfig.color } },
                    x: { grid: { display: false }, ticks: { color: chartConfig.color } }
                },
                plugins: { legend: { labels: { color: chartConfig.color } } }
            }
        });
    }
}
