// logic.js - Evolutionary & Uranian Astrology Controller (Clean State Version)

window.currentChartData = null;
let quoteIntervalId = null;
// logic.js - เพิ่มระบบจัดการโควตา Package 2
// logic.js
let pkg2Quota = 3;

function updateQuotaDisplay() {
    const quotaBadge = document.getElementById("quota-badge");
    const selectedPkg = document.getElementById("dev-pkg-select")?.value || "pkg1";

    if (!quotaBadge) return;

    if (selectedPkg === "pkg2") {
        quotaBadge.style.display = "inline-block";
        quotaBadge.textContent = `โควตาคงเหลือ: ${pkg2Quota}/3 คำถาม`;
        quotaBadge.style.color = (pkg2Quota <= 0) ? "#ef4444" : "#c084fc";
        quotaBadge.style.borderColor = (pkg2Quota <= 0) ? "#ef4444" : "rgba(139, 92, 246, 0.4)";
    } else {
        quotaBadge.style.display = "none";
    }
}

function handlePackageChange() {
    const selectedPkg = document.getElementById("dev-pkg-select")?.value || "pkg1";
    const questionInput = document.getElementById("question");
    const btnDeep = document.getElementById("btn-deep-report");

    if (questionInput) {
        if (selectedPkg === "pkg1") {
            questionInput.value = "";
            questionInput.disabled = true;
            questionInput.placeholder = "🔒 ถามคำถามดาวจร (Transit Q&A) เฉพาะ Package 2 ขึ้นไป";
            questionInput.style.opacity = "0.4";
            questionInput.style.cursor = "not-allowed";
        } else {
            questionInput.disabled = false;
            questionInput.placeholder = "เช่น ผมจะได้งานเมื่อไหร่[cite: 1]";
            questionInput.style.opacity = "1";
            questionInput.style.cursor = "text";
        }
    }

    if (btnDeep) {
        btnDeep.style.opacity = (selectedPkg === "pkg1" || selectedPkg === "pkg2") ? "0.5" : "1";
    }

    updateQuotaDisplay();

    if (window.currentChartData && selectedPkg !== "pkg1") {
        calculateAIAnalysis();
    }
}

// ผูกการยิงคำถามด้วยปุ่ม Enter
document.addEventListener("DOMContentLoaded", () => {
    handlePackageChange();

    const questionInput = document.getElementById("question");
    if (questionInput) {
        questionInput.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                event.preventDefault();
                
                const selectedPkg = document.getElementById("dev-pkg-select")?.value || "pkg1";
                if (selectedPkg === "pkg2" && pkg2Quota <= 0) {
                    alert("❌ คุณใช้โควตาคำถามของ Package 2 ครบแล้ว (3/3 คำถาม)");
                    return;
                }

                if (window.currentChartData) {
                    calculateAIAnalysis();
                } else {
                    calculateChart();
                }
            }
        });
    }
});

// ปรับปรุงฟังก์ชันสั่งวิเคราะห์ AI ให้ตัดโควตา
async function calculateAIAnalysis() {
    if (!window.currentChartData) return;

    const selectedPkg = document.getElementById("dev-pkg-select")?.value || "pkg1";
    const questionText = document.getElementById("question")?.value?.trim() || "";

    // เช็กโควตาสำหรับ Package 2 เมื่อมีการถามคำถาม
    if (selectedPkg === "pkg2" && questionText.length > 0) {
        if (pkg2Quota <= 0) {
            alert("❌ คุณใช้โควตาคำถามของ Package 2 ครบแล้ว (3/3 คำถาม)");
            return;
        }
    }

    // [โค้ดส่วนยิง Fetch API เดิม...]

    // เมื่อยิงสำเร็จให้ลดจำนวนโควตาลง 1
    if (selectedPkg === "pkg2" && questionText.length > 0) {
        pkg2Quota -= 1;
        updateQuotaDisplay();
    }
}

// ผูกให้ทำงานเมื่อเปลี่ยน Package
function handlePackageChange() {
    // [โค้ดสลับ Package เดิม...]
    updateQuotaDisplay();
}

const LOADING_QUOTES = [
    "“ดวงชะตาคือพิมพ์เขียว แต่การตัดสินใจของคุณคือผู้เขียนสคริปต์จริง”",
    "“ดาวจรที่ท้าทาย ไม่ใช่เรื่องโชคร้าย แต่คือแบบฝึกหัดขยายขีดความสามารถ”",
    "“ดวงดาวไม่ได้บังคับชะตาชีวิต เพียงแต่นำเสนอจังหวะเวลาที่เหมาะสม”",
    "“การตระหนักรู้ปมในจิตใต้สำนึก คือก้าวแรกของการปลดล็อกศักยภาพซ่อนเร้น”",
    "“พลังงานดาวจรจะไร้ผล หากขาดการลงมือทำอย่างมีวินัยในโลกจริง”",
    "“เปลี่ยนอุปสรรคให้เป็นกลยุทธ์ ดึงพลังงานดาวจรมาปรับใช้กับเป้าหมาย”"
];

function startLoadingQuotes() {
    const reportArea = document.getElementById("natal-report-content");
    if (!reportArea) return;

    let index = 0;
    reportArea.innerHTML = `
        <div style="text-align: center; margin-top: 100px; padding: 0 20px;">
            <div style="font-size: 24px; margin-bottom: 16px;">🔮</div>
            <p style="color: #cbd5e1; font-size: 15px; font-style: italic; min-height: 48px; transition: opacity 0.5s ease-in-out;" id="quote-text">
                ${LOADING_QUOTES[index]}
            </p>
            <p style="color: #94a3b8; font-size: 12px; margin-top: 12px;">กำลังประมวลผลคณิตศาสตร์ดาราศาสตร์และ AI พยากรณ์...</p>
        </div>
    `;

    quoteIntervalId = setInterval(() => {
        index = (index + 1) % LOADING_QUOTES.length;
        const quoteElem = document.getElementById("quote-text");
        if (quoteElem) {
            quoteElem.style.opacity = 0;
            setTimeout(() => {
                quoteElem.innerText = LOADING_QUOTES[index];
                quoteElem.style.opacity = 1;
            }, 300);
        }
    }, 3500);
}

function stopLoadingQuotes() {
    if (quoteIntervalId) {
        clearInterval(quoteIntervalId);
        quoteIntervalId = null;
    }
}

function handlePackageChange() {
    const selectedPkg = document.getElementById("dev-pkg-select")?.value || "pkg1";
    const questionInput = document.getElementById("question");
    const btnDeep = document.getElementById("btn-deep-report");

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

    if (btnDeep) {
        btnDeep.style.opacity = (selectedPkg === "pkg1" || selectedPkg === "pkg2") ? "0.5" : "1";
    }

    if (window.currentChartData) {
        calculateAIAnalysis();
    }
}

function handleDeepReportClick() {
    const currentPkg = document.getElementById("dev-pkg-select")?.value || "pkg1";
    if (currentPkg === "pkg1" || currentPkg === "pkg2") {
        const modal = document.getElementById("pkg-hint-modal");
        if (modal) modal.style.display = "flex";
        return;
    }
    window.location.href = "/deepreport";
}

function closePkgModal() {
    const modal = document.getElementById("pkg-hint-modal");
    if (modal) modal.style.display = "none";
}

async function calculateChart() {
    const statusPill = document.getElementById("status-pill");

    const payload = {
        user_name: document.getElementById("user_name")?.value || "คุณไอซ์",
        day: parseInt(document.getElementById("day")?.value || 1),
        month: parseInt(document.getElementById("month")?.value || 1),
        year: parseInt(document.getElementById("year")?.value || 2520),
        hour: parseInt(document.getElementById("hour")?.value || 0),
        minute: parseInt(document.getElementById("minute")?.value || 0),
        location_name: document.getElementById("location_name")?.value || "กรุงเทพมหานคร"
    };

    if (statusPill) {
        statusPill.textContent = "Calculating Stars...";
        statusPill.style.color = "#f59e0b";
    }

    startLoadingQuotes();

    try {
        const response = await fetch('/calculate_chart', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (data.status === "success") {
            window.currentChartData = data;
            await calculateAIAnalysis();
        } else {
            throw new Error(data.message || "เกิดข้อผิดพลาดในการคำนวณตำแหน่งดาว");
        }
    } catch (error) {
        stopLoadingQuotes();
        console.error("Calculate Chart Error:", error);
        if (statusPill) {
            statusPill.textContent = "Error";
            statusPill.style.color = "#ef4444";
        }
        const reportArea = document.getElementById("natal-report-content");
        if (reportArea) {
            reportArea.innerHTML = `<p style="color: #ef4444; text-align: center; margin-top: 120px;">❌ เกิดข้อผิดพลาด: ${error.message}</p>`;
        }
    }
}

async function calculateAIAnalysis() {
    if (!window.currentChartData) return;

    const statusPill = document.getElementById("status-pill");
    const reportArea = document.getElementById("natal-report-content");

    const selectedPkg = document.getElementById("dev-pkg-select")?.value || "pkg1";
    const isBypassCache = document.getElementById("bypass-cache")?.checked || false;
    const questionText = document.getElementById("question")?.value?.trim() || "";

    // กำหนดโหมดภาษา: Package 4 ใช้โหร (astrologer), Package 1-3 ใช้ลูกค้า (client)
    const mode = (selectedPkg === "pkg4") ? "astrologer" : "client";

    let reportType = "natal_7";
    if (selectedPkg !== "pkg1" && questionText.length > 0) {
        reportType = "transit_qa";
    }

    const payload = {
        user_name: document.getElementById("user_name")?.value || "คุณไอซ์",
        report_type: reportType,
        chart_data: window.currentChartData,
        question: questionText,
        mode: mode,
        package_level: selectedPkg,
        bypass_cache: isBypassCache
    };

    if (statusPill) {
        statusPill.textContent = "Analyzing AI...";
        statusPill.style.color = "#3b82f6";
    }

    if (!quoteIntervalId) {
        startLoadingQuotes();
    }

    try {
        const response = await fetch('/analyze_ai', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        stopLoadingQuotes();

        if (data.status === "success") {
            if (statusPill) {
                statusPill.textContent = "Ready";
                statusPill.style.color = "#10b981";
            }

            const markdownText = (data.type === "transit_qa") ? data.answer : data.report;
            
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
        stopLoadingQuotes();
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

document.addEventListener("DOMContentLoaded", () => {
    handlePackageChange();

    const questionInput = document.getElementById("question");
    if (questionInput) {
        questionInput.addEventListener("keydown", (event) => {
            if (event.key === "Enter") {
                event.preventDefault();
                if (window.currentChartData) {
                    calculateAIAnalysis();
                } else {
                    calculateChart();
                }
            }
        });
    }
});
