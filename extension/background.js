chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    if (request.action === "analyze") {

        fetch("https://smart-phishing-detector-hh3z.onrender.com/predict", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: request.text })
        })
        .then(res => res.json())
        .then(data => {
            sendResponse(data);
        })
        .catch(err => {
            console.log("API ERROR:", err);
            sendResponse({ error: true });
        });

        return true;
    }
});
