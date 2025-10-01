from flask import Flask, request, jsonify
from train_classifier import load_model, predict_activity_and_reps
from process_video import analyze_video

app = Flask(__name__)
clf = load_model()

@app.get("/")
def health():
    return jsonify({"status": "ok", "service": "ml", "version": "1"}), 200

@app.route("/predict_activity", methods=["POST"])
def predict_activity():
    """
    Expects JSON: { "userId": "...", "keypoints": [...] }
    """
    try:
        data = request.get_json()
        print(f"Received data keys: {list(data.keys()) if data else 'None'}")
        
        keypoints = data.get("keypoints")
        if not keypoints:
            return jsonify({"error": "Missing keypoints"}), 400

        print(f"Processing {len(keypoints)} frames of keypoints")
        result = predict_activity_and_reps(keypoints, clf)
        
        print(f"Result keys: {list(result.keys()) if result else 'None'}")
        return jsonify(result), 200
        
    except Exception as e:
        print(f"Error in predict_activity: {str(e)}")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route("/process_video", methods=["POST"])
def process_video_route():
    """
    Expects JSON: { "videoPath": "file.json", "jobId": "..." }
    """
    data = request.get_json()
    video_path = data.get("videoPath")
    job_id = data.get("jobId")
    if not video_path or not job_id:
        return jsonify({"error": "Missing videoPath or jobId"}), 400

    summary = analyze_video(video_path, job_id)
    return jsonify({
        "message": "Result processed and saved",
        "jobId": job_id,
        "result": summary
    }), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=False)
