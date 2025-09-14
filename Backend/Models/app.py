from flask import Flask, request, jsonify
import threading
import os
import time
import traceback
from process_video import analyze_video   # 👈 import function from process_video.py

print("[START] Importing modules...")

app = Flask(__name__)

# Directories
RESULTS_DIR = os.path.join(os.getcwd(), "results")
UPLOADS_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)


# ----------------- API ENDPOINT -----------------
@app.route("/process", methods=["POST"])
def trigger_process():
    """
    Accepts JSON request with only jobId.
    Finds video in uploads/<jobId>.mp4
    Spawns background thread to analyze video.
    """
    try:
        data = request.get_json(force=True)
        print(f"[DEBUG] Incoming request data: {data}")

        # job_id = data.get("jobId") or str(int(time.time()))
        job_id = data.get("jobId") or str(int(time.time()))
        video_path = data.get("path")

        if not os.path.exists(video_path):
            return jsonify({"error": f"Video not found for jobId={job_id}"}), 404

        sample_every_n = int(data.get("sample_every_n") or 2)
        max_frames = int(data.get("max_frames") or 30)

        print(f"[INFO] Scheduling analysis for jobId={job_id}, video={video_path}")
        thread = threading.Thread(
            target=analyze_video,
            args=(video_path, job_id, RESULTS_DIR, sample_every_n, max_frames)
        )
        thread.daemon = True
        thread.start()

        return jsonify({"job": job_id, "status": "scheduled"})
    except Exception as e:
        print(f"[ERROR] Exception in /process endpoint: {e}")
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print("[INFO] Starting Flask ML service on port 5001...")
    app.run(host="0.0.0.0", port=5001, debug=True)
