# Backend/Models/app.py
from flask import Flask, request, jsonify
from process_video import analyze_video
import os

app = Flask(__name__)
RESULTS_DIR = "Results"

@app.route("/process", methods=["POST"])
def process_video_route():
    data = request.get_json()
    video_path = data.get("path")
    job_id = data.get("jobId")
    if not video_path or not job_id:
        return jsonify({"error": "Missing video path or jobId"}), 400

    try:
        summary = analyze_video(video_path, job_id, RESULTS_DIR)
        return jsonify(summary)
    except Exception as e:
        return jsonify({"predicted_exercise": "error",
                        "is_correct": False,
                        "feedback": [str(e)],
                        "keypoints": []}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
