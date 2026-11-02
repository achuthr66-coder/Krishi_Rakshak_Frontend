from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables cross-origin requests for the web dashboard

# In-memory storage for active farm metrics
latest_farm_metrics = {
    "status": "SECURE",
    "high_count": 0,
    "med_count": 0,
    "low_count": 0,
    "last_animal": "NONE"
}

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Krishi Rakshak Cloud API Gateway Online"}), 200

@app.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Endpoint for your Javascript website to read current stats"""
    return jsonify(latest_farm_metrics), 200

@app.route('/api/update', methods=['POST'])
def update_metrics():
    """Endpoint for your local Laptop ML script to push telemetry updates"""
    global latest_farm_metrics
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON data package"}), 400
            
        # Update our global memory map coordinates
        latest_farm_metrics["status"] = data.get("status", "SECURE")
        latest_farm_metrics["high_count"] = int(data.get("high_count", 0))
        latest_farm_metrics["med_count"] = int(data.get("med_count", 0))
        latest_farm_metrics["low_count"] = int(data.get("low_count", 0))
        latest_farm_metrics["last_animal"] = data.get("last_animal", "NONE").upper()
        
        return jsonify({"message": "Cloud synchronized successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
