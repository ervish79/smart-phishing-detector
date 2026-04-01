document.getElementById("scanBtn").addEventListener("click", async () => {

    console.log("🟢 Button clicked");

    let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.id) {
        console.log("❌ No active tab");
        document.getElementById("result").innerText = "❌ No active tab";
        return;
    }

    chrome.tabs.sendMessage(tab.id, { action: "scan" }, (response) => {

        if (chrome.runtime.lastError) {
            console.error("❌ Runtime Error:", chrome.runtime.lastError.message);
            document.getElementById("result").innerText = "❌ Cannot connect to page";
            return;
        }

        console.log("📩 Response received:", response);

        if (!response || response.status === "error") {
            document.getElementById("result").innerText = "❌ No response from page";
            return;
        }

        let risk = response.risk;
        let resultDiv = document.getElementById("result");

        if (risk > 75) {
            resultDiv.innerHTML = `🚨 High Risk (${risk.toFixed(1)}%)`;
            resultDiv.style.color = "red";
        } else if (risk > 50) {
            resultDiv.innerHTML = `⚠️ Suspicious (${risk.toFixed(1)}%)`;
            resultDiv.style.color = "orange";
        } else {
            resultDiv.innerHTML = `✅ Safe (${risk.toFixed(1)}%)`;
            resultDiv.style.color = "green";
        }

    });

});