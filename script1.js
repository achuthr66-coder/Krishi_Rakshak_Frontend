// TARGET CLOUD LINK (You will change this link to match your cloud platform in step 5)
const BACKEND_URL = "http://127.0.0.1:5000";

async function fetchLatestModelAnalysis() {
    try {
        const response = await fetch(`${BACKEND_URL}/get_latest`);
        if (!response.ok) throw new Error("Cloud network error.");
        
        const data = await response.json();

        // 1. Target UI display locations
        const threatElem = document.getElementById('threatStatus');
        const svmElem = document.getElementById('svmResult');
        const ifElem = document.getElementById('ifResult');
        document.getElementById('winnerModel').innerText = data.better_performing_model;

        // 2. Inject structural metrics and dynamic UI styling classes
        threatElem.innerText = data.threat_level;
        threatElem.className = "badge " + (data.threat_level.includes("HIGH") ? "danger" : "safe");

        svmElem.innerText = data.svm_decision;
        svmElem.className = "badge " + (data.svm_decision.includes("HIGH") ? "danger" : "safe");

        ifElem.innerText = data.isolation_forest_decision;
        ifElem.className = "badge " + (data.isolation_forest_decision.includes("ANOMALY") ? "anomaly" : "safe");

    } catch (err) {
        console.error("Dashboard connection sync error:", err);
    }
}

// Automatically poll the cloud server every 1 second to update the dashboard instantly
setInterval(fetchLatestModelAnalysis, 1000);