# Backend/Models/process_video.py
import os
import cv2
import numpy as np
import joblib
import json
import openpifpaf

MODEL_FILE = "exercise_model.pkl"

# Rule-based feedback function
def generate_feedback(predicted_exercise, keypoints):
    feedback = []
    if predicted_exercise.lower() == "pushup":
        # Example: check elbow angle
        left_elbow = keypoints.get("left_elbow", 0)
        right_elbow = keypoints.get("right_elbow", 0)
        if left_elbow < 70 or right_elbow < 70:
            feedback.append("Try bending elbows more during pushup")
        else:
            feedback.append("Good pushup form!")
    else:
        feedback.append("No specific form rules for detected exercise.")
    return feedback

# Calculate angle between 3 points
def calculate_angle(a, b, c):
    try:
        ax, ay = a
        bx, by = b
        cx, cy = c
    except:
        return None
    ab = (ax - bx, ay - by)
    cb = (cx - bx, cy - by)
    dot = ab[0]*cb[0] + ab[1]*cb[1]
    ab_len = np.hypot(*ab)
    cb_len = np.hypot(*cb)
    if ab_len == 0 or cb_len == 0: return None
    cosang = np.clip(dot / (ab_len*cb_len), -1.0, 1.0)
    return np.degrees(np.arccos(cosang))

def analyze_video(video_path, job_id, results_dir, model=None):
    print(f"[INFO] Starting analysis for jobId={job_id}, video={video_path}")

    # Load classifier
    if model is None:
        if not os.path.exists(MODEL_FILE):
            raise FileNotFoundError(f"[ERROR] Trained model not found: {MODEL_FILE}")
        model = joblib.load(MODEL_FILE)
        print("[INFO] ML model loaded successfully")

    # Load OpenPifPaf predictor
    predictor = openpifpaf.Predictor(checkpoint='resnet50')
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError("Cannot open video")

    keypoints_list = []
    max_frames = 30
    frame_count = 0

    while frame_count < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        predictions, _, _ = predictor.numpy_image(frame_rgb)

        if not predictions:
            frame_count += 1
            continue

        # Take first detected person for simplicity
        pred = predictions[0]
        person_keypoints = {}
        for kpt_name, kpt_idx in openpifpaf.Coco.keypoints.items():
            if kpt_idx < len(pred.data):
                x, y, v = pred.data[kpt_idx]
                person_keypoints[kpt_name] = float(x)
        keypoints_list.append(person_keypoints)
        frame_count += 1

    cap.release()

    if not keypoints_list:
        summary = {"predicted_exercise": "unknown",
                   "is_correct": False,
                   "feedback": ["No pose detected"],
                   "keypoints": []}
    else:
        # Average keypoints across frames
        avg_keypoints = {}
        for k in keypoints_list[0].keys():
            avg_keypoints[k] = float(np.mean([kp.get(k, 0) for kp in keypoints_list]))

        # Example: calculate joint angles if needed
        features = [v for v in avg_keypoints.values()]

        # Predict exercise
        predicted_exercise = model.predict([features])[0]

        feedback = generate_feedback(predicted_exercise, avg_keypoints)

        summary = {
            "predicted_exercise": str(predicted_exercise),
            "is_correct": True,
            "feedback": feedback,
            "keypoints": avg_keypoints
        }

    # Save result to JSON
    os.makedirs(results_dir, exist_ok=True)
    result_path = os.path.join(results_dir, f"{job_id}.json")
    with open(result_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[INFO] Result saved to {result_path}")

    return summary
