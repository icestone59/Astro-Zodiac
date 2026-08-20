// logic.js - Core Engine สำหรับเชื่อมต่อ Backend และจัดการ UI

let currentChartData = null;
let radarChartInstance = null;
let barChartInstance = null;

// 1. ฟังก์ชันเชื่อมต่อ Backend แบบป้องกัน Error ข้ามโดเมน/เซิร์ฟเวอร์ล่ม
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

// 2. ฟังก์ชันอัปเดตข้อความสถานะบนหน้าจอ (ให้ตรงกับ Theme ปัจจุบัน)
function showStatus(message, state = "loading") {
    const statusText = document.getElementById("status-text");
    const statusPill = document.getElementById("status-pill");

    if (statusText) statusText.textContent = message;
    
    if (statusPill) {
        if (state === "loading") {
            statusPill.textContent = "Processing...";
            statusPill.style.color = "#f59e0b"; // สีส้ม
        } else if (state === "error") {
            statusPill.textContent = "Error";
            statusPill.style.color = "#ef4444"; // สีแดง
            if (statusText) statusText.style.color = "#ef4444";
        } else if (state === "success") {
            statusPill.textContent = "Ready";
            statusPill.style.color = "#10b981"; // สีเขียว
            if (statusText) statusText.style.color = "#c084fc"; // กลับเป็นสีม่วง
        }
    }
}

// 3. ฟังก์ชันคำนวณองศาดาว (ผูกกับปุ่ม "คำนวณตำแหน่งดาวและวิเคราะห์")
async function calculateChart() {
    showStatus("กำลังคำนวณองศาดาวกำเนิดและดาวจร (Real-time)...", "loading");
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

        // ยิง API ไปที่ Flask Backend
        currentChartData = await safeFetchJson('/calculate_chart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        showStatus("ผูกดวงชะตาสำเร็จ! กรุณากดปุ่ม 'กดดูชะตาของคุณ' ด้านล่าง", "success");
    } catch (error) {
        showStatus(error.message, "error");
    } finally {
        if (btn) btn.disabled = false;
    }
}

// 4. ฟังก์ชันเรียก AI วิเคราะห์ (Deep Report หรือ Transit)
async function analyzeAI(reportType) {
    if (!currentChartData) {
        alert("กรุณากด 'คำนวณตำแหน่งดาวและวิเคราะห์' ก่อนครับ");
        return;
    }

    showStatus("AI กำลังวิเคราะห์รากฐานดวงชะตา... (อาจใช้เวลา 15-30 วินาที)", "loading");
    
    // ซ่อนไอคอน Default และเตรียมพื้นที่แสดงผล
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

        // หากเป็น Deep Report ให้แสดงกราฟ
        if (reportType === 'deep_report' && data.radar_data) {
            document.getElementById("charts-wrapper").style.display = "flex";
            renderCharts(data.radar_data, data.bar_data);
        }

        // แปลงข้อความจาก AI เป็น HTML
        let reportText = data.report || data.answer;
        document.getElementById("report-content").innerHTML = marked.parse(reportText);
        showStatus("การวิเคราะห์เสร็จสมบูรณ์!", "success");
    } catch (error) {
        showStatus(error.message, "error");
    }
}

// 5. ระบบวาดกราฟ Chart.js (ปรับสีให้เข้ากับ Theme สีม่วง)
function renderCharts(radarData, barData) {
    if (radarChartInstance) radarChartInstance.destroy();
    if (barChartInstance) barChartInstance.destroy();

    const chartConfig = {
        color: '#e2e8f0', // Text color
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
