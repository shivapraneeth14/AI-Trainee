from flask import Flask, request, jsonify
import os
import time
import traceback
from process_video import analyze_video, MODEL_FILE
import joblib

app = Flask(__name__)

RESULTS_DIR = os.path.join(os.getcwd(), "results")
UPLOADS_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Load trained model
try:
    model = joblib.load(MODEL_FILE)
    print("[INFO] Model loaded successfully.")
except Exception as e:
    print(f"[ERROR] Could not load model: {e}")
    model = None

@app.route("/ping", methods=["GET"])
def ping():
    return "pong", 200

@app.route("/process", methods=["POST"])
def process_video_route():
    try:
        data = request.get_json(force=True)
        job_id = data.get("jobId") or str(int(time.time()))
        video_path = data.get("path")

        if not os.path.exists(video_path):
            return jsonify({"error": f"Video not found for jobId={job_id}"}), 404

        # Run processing synchronously
        summary = analyze_video(video_path, job_id, RESULTS_DIR, model=model)

        return jsonify(summary)

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
