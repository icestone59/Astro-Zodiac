// logic.js - Evolutionary & Uranian Astrology Engine Controller

// Global State
window.currentChartData = null;

/**
 * 1. จัดการสิทธิ์และการเปิด/ปิด UI ตาม Package ที่เลือก
 */
function handlePackageChange() {
    const selectedPkg = document.getElementById("dev-pkg-select")?.value || "pkg1";
    const questionInput = document.getElementById("question");
    const btnDeep = document.getElementById("btn-deep-report");

    // ควบคุมการใช้งานช่องคำถามดาวจร (Transit Q&A)
    if (questionInput) {
        if (selectedPkg === "pkg1") {
            questionInput.value = "";
            questionInput.disabled = true;
            questionInput.placeholder = "🔒 ถามคำถามดาวจร (Transit Q&A) เฉพาะ Package 2 ขึ้นไป";
            questionInput.style.opacity = "0.4";
            questionInput.style.cursor = "not-allowed";
            questionInput.style.background = "rgba(0, 0, 0, 0.8)";
        } else {
            questionInput.disabled = false;
            questionInput.placeholder = "เช่น ผมจะได้งานเมื่อไหร่";
            questionInput.style.opacity = "1";
            questionInput.style.cursor = "text";
            questionInput.style.background = "rgba(0, 0, 0, 0.5)";
        }
    }

    // ควบคุมความโปร่งใสปุ่ม Deep Report (Package 3 ขึ้นไป)
    if (btnDeep) {
        btnDeep.style.opacity = (selectedPkg === "pkg1" || selectedPkg === "pkg2") ? "0.5" : "1";
    }

    // หากมีข้อมูลดวงชะตาคำนวณไว้แล้ว ให้ส่งวิเคราะห์ตาม Package ใหม่ทันที
    if (window.currentChartData) {
        calculateAIAnalysis();
    }
}

/**
 * 2. จัดการสลับโหมดการแปลผล (เวอร์ชั่นลูกค้า vs เวอร์ชั่นโหร)
 */
function handleModeToggle() {
    if (window.currentChartData) {
        calculateAIAnalysis();
    }
}

/**
 * 3. ตรวจสอบสิทธิ์และเปิดรายงานปมจิตวิทยาเชิงลึก (Deep Report)
 */
function handleDeepReportClick() {
    const currentPkg = document.getElementById("dev-pkg-select")?.value || "pkg1";

    // สิทธิ์ Package 1 และ 2 ไม่อนุญาตให้เข้าถึง Deep Report
    if (currentPkg === "pkg1" || currentPkg === "pkg2") {
        const modal = document.getElementById("pkg-hint-modal");
        if (modal) modal.style.display = "flex";
        return;
    }

    // Package 3 ขึ้นไป อนุญาตให้ไปยังหน้า deepreport.html
    window.location.href = "/deepreport";
}

function closePkgModal() {
    const modal = document.getElementById("pkg-hint-modal");
    if (modal) modal.style.display = "none";
}

/**
 * 4. คำนวณตำแหน่งองศาดาวกำเนิดและดาวจร (Backend Calculation)
 */
async function calculateChart() {
    const statusPill = document.getElementById("status-pill");
    const reportArea = document.getElementById("natal-report-content");

    const payload = {
        user_name: document.getElementById("user_name")?.value || "คุณไอซ์",
        day: parseInt(document.getElementById("day")?.value || 1),
        month: parseInt(document.getElementById("month")?.value || 1),
        year: parseInt(document.getElementById("year")?.value || 2538),
        hour: parseInt(document.getElementById("hour")?.value || 0),
        minute: parseInt(document.getElementById("minute")?.value || 0),
        location_name: document.getElementById("location_name")?.value || "กรุงเทพมหานคร"
    };

    if (statusPill) {
        statusPill.textContent = "Calculating Stars...";
        statusPill.style.color = "#f59e0b";
    }

    if (reportArea) {
        reportArea.innerHTML = `<p style="color: #94a3b8; text-align: center; margin-top: 120px;">⏳ กำลังคำนวณตำแหน่งดวงดาวดาราศาสตร์และสกัดมุมสัมพันธ์...</p>`;
    }

    try {
        const response = await fetch('/calculate_chart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.status === "success") {
            window.currentChartData = data;
            // ประมวลผล AI ต่อทันที
            await calculateAIAnalysis();
        } else {
            throw new Error(data.message || "เกิดข้อผิดพลาดในการคำนวณตำแหน่งดาว");
        }
    } catch (error) {
        console.error("Calculate Chart Error:", error);
        if (statusPill) {
            statusPill.textContent = "Error";
            statusPill.style.color = "#ef4444";
        }
        if (reportArea) {
            reportArea.innerHTML = `<p style="color: #ef4444; text-align: center; margin-top: 120px;">❌ เกิดข้อผิดพลาด: ${error.message}</p>`;
        }
    }
}

/**
 * 5. ส่งข้อมูลดวงชะตาให้ AI ประมวลผลพยากรณ์ (Natal 7 / Transit Q&A)
 */
async function calculateAIAnalysis() {
    if (!window.currentChartData) return;

    const statusPill = document.getElementById("status-pill");
    const reportArea = document.getElementById("natal-report-content");

    const selectedPkg = document.getElementById("dev-pkg-select")?.value || "pkg1";
    const isAstrologerMode = document.getElementById("mode-toggle")?.checked || false;
    const isBypassCache = document.getElementById("bypass-cache")?.checked || false;
    const questionText = document.getElementById("question")?.value?.trim() || "";

    // กำหนดประเภทรายงาน: Package 2 ขึ้นไป และมีการพิมพ์คำถาม จะใช้ transit_qa
    let reportType = "natal_7";
    if (selectedPkg !== "pkg1" && questionText.length > 0) {
        reportType = "transit_qa";
    }

    const payload = {
        user_name: document.getElementById("user_name")?.value || "คุณไอซ์",
        report_type: reportType,
        chart_data: window.currentChartData,
        question: questionText,
        mode: isAstrologerMode ? "astrologer" : "client",
        package_level: selectedPkg,
        bypass_cache: isBypassCache
    };

    if (statusPill) {
        statusPill.textContent = "Analyzing AI...";
        statusPill.style.color = "#3b82f6";
    }

    if (reportArea) {
        reportArea.innerHTML = `<p style="color: #94a3b8; text-align: center; margin-top: 120px;">🔮 กำลังประมวลผลคำทำนายเชิงพัฒนาศักยภาพ...</p>`;
    }

    try {
        const response = await fetch('/analyze_ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.status === "success") {
            if (statusPill) {
                statusPill.textContent = "Ready";
                statusPill.style.color = "#10b981";
            }

            const markdownText = (data.type === "transit_qa") ? data.answer : data.report;
            
            // แปลง Markdown เป็น HTML สวยงาม
            if (reportArea) {
                if (typeof marked !== 'undefined') {
                    reportArea.innerHTML = marked.parse(markdownText);
                } else {
                    reportArea.innerText = markdownText;
                }
            }
        } else {
            throw new Error(data.message || "เกิดข้อผิดพลาดในการวิเคราะห์ AI");
        }
    } catch (error) {
        console.error("AI Analysis Error:", error);
        if (statusPill) {
            statusPill.textContent = "Error";
            statusPill.style.color = "#ef4444";
        }
        if (reportArea) {
            reportArea.innerHTML = `<p style="color: #ef4444; text-align: center; margin-top: 120px;">❌ เกิดข้อผิดพลาดในการดึงคำทำนาย: ${error.message}</p>`;
        }
    }
}

// ผูก Event Listener เมื่อ DOM โหลดเสร็จสิ้น
document.addEventListener("DOMContentLoaded", () => {
    handlePackageChange();
});
