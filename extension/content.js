console.log("🔥 Content script loaded");

// =========================
// GET TEXT (SMART)
// =========================
function getText() {
    const emailBody = document.querySelector('.a3s'); // Gmail

    if (emailBody) {
        return emailBody.innerText;
    } else {
        return document.body.innerText;
    }
}

// =========================
// CALL BACKGROUND (API)
// =========================
function getAIResult(text) {
    return new Promise((resolve) => {

        console.log("📡 Sending to background...");

        chrome.runtime.sendMessage(
            { action: "analyze", text: text },
            (response) => {

                if (!response || response.error) {
                    console.log("❌ API failed");
                    resolve(null);
                } else {
                    console.log("✅ Response received:", response);
                    resolve(response);
                }
            }
        );

    });
}

// =========================
// SHOW RESULT
// =========================
function showResult(risk) {

    let existing = document.getElementById("phishing-alert");
    if (existing) existing.remove();

    let box = document.createElement("div");
    box.id = "phishing-alert";

    box.style.position = "fixed";
    box.style.bottom = "20px";
    box.style.right = "20px";
    box.style.padding = "15px";
    box.style.borderRadius = "10px";
    box.style.color = "white";
    box.style.zIndex = "9999";
    box.style.fontWeight = "bold";

    if (risk > 75) {
        box.innerText = `🚨 High Risk (${risk.toFixed(1)}%)`;
        box.style.backgroundColor = "red";
    } else if (risk > 50) {
        box.innerText = `⚠️ Suspicious (${risk.toFixed(1)}%)`;
        box.style.backgroundColor = "orange";
    } else {
        box.innerText = `✅ Safe (${risk.toFixed(1)}%)`;
        box.style.backgroundColor = "green";
    }

    document.body.appendChild(box);

    // Auto remove after 5 sec
    setTimeout(() => {
        box.remove();
    }, 5000);
}

// =========================
// RUN DETECTION
// =========================
function runDetection() {

    const text = getText().toLowerCase();

    if (!text || text.length < 100) return;

    console.log("🧠 Running detection...");

    getAIResult(text).then(result => {
        if (!result) return;

        const risk = result.phishing_prob;
        showResult(risk);
    });
}

// =========================
// AUTO RUN ON PAGE LOAD
// =========================
window.addEventListener("load", () => {
    setTimeout(runDetection, 2000);
});

// =========================
// OBSERVER (REAL-TIME)
// =========================
let lastText = "";

const observer = new MutationObserver(() => {

    const text = getText().toLowerCase();

    if (text && text !== lastText && text.length > 100) {
        lastText = text;
        runDetection();
    }

});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

// =========================
// POPUP BUTTON LISTENER
// =========================
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    if (request.action === "scan") {

        const text = getText().toLowerCase();

        getAIResult(text).then(result => {

            if (!result) {
                sendResponse({ status: "error" });
                return;
            }

            const risk = result.phishing_prob;

            showResult(risk);

            sendResponse({
                status: "done",
                risk: risk
            });

        });

        return true;
    }
});