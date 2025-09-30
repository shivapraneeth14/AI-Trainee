import os
import json
from train_classifier import predict_activity_and_reps, load_model, session_data

clf = load_model()

def analyze_video(mediapipe_json, job_id, results_dir="results"):
    """Process MediaPipe JSON and save comprehensive AI fitness coach results"""
    summary = predict_activity_and_reps(mediapipe_json, clf)
    summary["keypoints"] = mediapipe_json
    summary["session_data"] = dict(session_data)  # Include session tracking data

    os.makedirs(results_dir, exist_ok=True)
    result_path = os.path.join(results_dir, f"{job_id}.json")
    with open(result_path, "w") as f:
        json.dump(summary, f, indent=2)
    return summary

def reset_session():
    """Reset the fitness coach session data"""
    global session_data
    session_data["start_time"] = None
    session_data["current_exercise"] = None
    session_data["rep_count"] = 0
    session_data["set_count"] = 0
    session_data["last_rep_time"] = None
    session_data["fatigue_signals"] = []
    session_data["motion_history"].clear()

def get_session_summary():
    """Get current session summary"""
    return {
        "exercise": session_data["current_exercise"],
        "reps": session_data["rep_count"],
        "sets": session_data["set_count"],
        "duration": session_data.get("duration", 0)
    }
