import os
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.svm import SVC
from sklearn.ensemble import IsolationForest

app = Flask(__name__)
# Enable Cross-Origin Resource Sharing so public JS websites can query this API
CORS(app)

# Global variables to store the latest evaluation data in server RAM memory
latest_logs = {
    "threat_level": "WAITING",
    "svm_decision": "NORMAL",
    "isolation_forest_decision": "NORMAL",
    "better_performing_model": "None"
}

# ==========================================================================
# 1. INITIALIZE MACHINE LEVEL ALGORITHMS (SVM & ISOLATION FOREST)
# ==========================================================================
# Training vectors layout: [elephant, bear, person, cow, cat, dog, box_size]
X_train = np.array([
    [1, 0, 0, 0, 0, 0, 0.8],  # 1 Elephant close to camera -> High Threat (1)
    [0, 1, 0, 0, 0, 0, 0.8],  # 1 Bear close to camera -> High Threat (1)
    [0, 0, 1, 2, 0, 0, 0.15],  # 1 human and 2 cows far away -> Low Threat (0)
    [0, 0, 0, 0, 1, 1, 0.1],  # 1 cat and 1 dog -> Low Threat (0)
])
y_train = np.array([1, 1, 0, 0]) # Targets matching ground truth threat rules

# Train your Boundary Builder (SVM)
svm_model = SVC(kernel='linear', probability=True, random_state=42)
svm_model.fit(X_train, y_train)

# Train your Guard Dog (Isolation Forest) exclusively on safe everyday footprints
normal_baseline = np.array([
    [0, 0, 1, 0, 0, 0, 0.1],
    [0, 0, 0, 1, 0, 0, 0.15],
    [0, 0, 0, 0, 1, 1, 0.1],
])
isolation_forest = IsolationForest(contamination=0.1, random_state=42)
isolation_forest.fit(normal_baseline)

# ==========================================================================
# 2. PUBLIC API CHANNELS (ENDPOINTS)
# ==========================================================================
@app.route('/predict', methods=['POST'])
def predict():
    global latest_logs
    try:
        data = request.json
        
        # Parse text features arriving from either laptop or JS website
        features = np.array([[
            int(data.get('elephant', 0)), int(data.get('bear', 0)),
            int(data.get('person', 0)), int(data.get('cow', 0)),
            int(data.get('cat', 0)), int(data.get('dog', 0)),
            float(data.get('avg_box_size', 0.0))
        ]])

        # Explicit threat rule requested by user
        is_actual_threat = 1 if (features[0][0] > 0 or features[0][1] > 0) else 0

        # Run Boundary Builder Classification (SVM)
        svm_pred = int(svm_model.predict(features))

        # Run Guard Dog Anomaly Check (Isolation forest maps -1 to anomalies)
        if_raw = isolation_forest.predict(features)
        if_pred = 1 if if_raw == -1 else 0

        # Evaluate performance accuracy matching your rule system
        svm_correct = (svm_pred == is_actual_threat)
        if_correct = (if_pred == is_actual_threat)

        if svm_correct and if_correct:
            winner = "Both Models Succeeded"
        elif svm_correct:
            winner = "SVM (Boundary Builder) Performed Better"
        elif if_correct:
            winner = "Isolation Forest (Guard Dog) Performed Better"
        else:
            winner = "Both Models Failed"

        # Overwrite current state log dict
        latest_logs = {
            "threat_level": "HIGH THREAT" if is_actual_threat == 1 else "LOW THREAT",
            "svm_decision": "HIGH THREAT TRIGGERED" if svm_pred == 1 else "STABLE STATUS",
            "isolation_forest_decision": "ANOMALY SPOTTED" if if_pred == 1 else "NORMAL STATUS",
            "better_performing_model": winner
        }

        return jsonify({"status": "data_logged", "threat_level": latest_logs["threat_level"]})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/get_latest', methods=['GET'])
def get_latest():
    # Returns the computed metrics back to your JS visual web dashboard
    return jsonify(latest_logs)

if __name__ == '__main__':
    # Cloud networks require binding to all public interfaces 0.0.0.0 via systemic environments
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)