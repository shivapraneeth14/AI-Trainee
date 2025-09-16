import os
import cv2
import mediapipe as mp
import math
import json
import traceback
import joblib  # For loading the trained classifier

mp_pose = mp.solutions.pose

# ----------------- UTILITIES -----------------
def calculate_angle(a, b, c):
    """Calculate angle between three keypoints."""
    try:
        ax, ay = a; bx, by = b; cx, cy = c
    except:
        return None
    ab = (ax - bx, ay - by)
    cb = (cx - bx, cy - by)
    dot = ab[0]*cb[0] + ab[1]*cb[1]
    ab_len = math.hypot(*ab)
    cb_len = math.hypot(*cb)
    if ab_len == 0 or cb_len == 0: return None
    cosang = max(min(dot / (ab_len*cb_len), 1.0), -1.0)
    return round(math.degrees(math.acos(cosang)), 2)

# ----------------- LOAD CLASSIFIER -----------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "exercise_model.pkl")
classifier = joblib.load(MODEL_PATH)
print("[INFO] Exercise classifier loaded.")

# ----------------- FORM CHECK -----------------
def check_form(exercise, features):
    """Rule-based form feedback for each exercise."""
    feedbacks = []
    correct = True

    left_elbow = features.get("left_elbow")
    right_elbow = features.get("right_elbow")
    left_knee = features.get("left_knee")
    right_knee = features.get("right_knee")
    left_hip = features.get("left_hip")
    right_hip = features.get("right_hip")

    if exercise == "Push-up":
        if left_elbow is None or right_elbow is None:
            correct = False; feedbacks.append("Cannot detect elbows.")
        else:
            if left_elbow > 110 or right_elbow > 110:
                correct = False; feedbacks.append("Elbows not bent enough.")
    elif exercise == "Squat":
        if left_knee is None or right_knee is None:
            correct = False; feedbacks.append("Cannot detect knees.")
        else:
            if left_knee > 120 or right_knee > 120:
                correct = False; feedbacks.append("Knees not bent enough.")
    elif exercise == "Lunge":
        if left_knee and right_knee:
            if not ((left_knee < 110 and right_knee > 140) or (right_knee < 110 and left_knee > 140)):
                correct = False; feedbacks.append("Incorrect lunge form.")
    elif exercise == "Plank":
        if left_elbow and right_elbow and (left_elbow < 150 or right_elbow < 150):
            correct = False; feedbacks.append("Elbows should be straighter.")
    elif exercise == "Jumping Jack":
        if left_elbow and right_elbow and (left_elbow < 160 or right_elbow < 160):
            correct = False; feedbacks.append("Arms not fully raised.")
    else:
        feedbacks.append("No specific form rules for detected exercise.")

    return correct, feedbacks

# ----------------- MAIN PIPELINE -----------------
def analyze_video(video_path, job_id, results_dir, sample_every_n=3, max_frames=30):
    """Full pipeline: pose extraction → classify → form check → save JSON."""
    try:
        out = {"jobId": job_id, "path": video_path, "frames": [], "summary": {}}

        if not os.path.exists(video_path):
            out["error"] = "Video not found"
            return out

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            out["error"] = "Cannot open video"
            return out

        pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
        frame_idx, processed = 0, 0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)

        angles_accum = {
            "left_elbow": [], "right_elbow": [],
            "left_knee": [], "right_knee": [],
            "left_hip": [], "right_hip": []
        }

        while True:
            ret, frame = cap.read()
            if not ret: break
            if frame_idx % sample_every_n != 0:
                frame_idx += 1
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)

            if res.pose_landmarks:
                kp = {}
                for lm in mp_pose.PoseLandmark:
                    landmark = res.pose_landmarks.landmark[lm.value]
                    kp[lm.name] = {
                        "x": round(landmark.x * width, 2),
                        "y": round(landmark.y * height, 2),
                        "z": round(landmark.z, 2),
                        "visibility": round(landmark.visibility, 2)
                    }

                # Compute angles
                left_elbow = calculate_angle(
                    (kp["LEFT_SHOULDER"]["x"], kp["LEFT_SHOULDER"]["y"]),
                    (kp["LEFT_ELBOW"]["x"], kp["LEFT_ELBOW"]["y"]),
                    (kp["LEFT_WRIST"]["x"], kp["LEFT_WRIST"]["y"])
                )
                right_elbow = calculate_angle(
                    (kp["RIGHT_SHOULDER"]["x"], kp["RIGHT_SHOULDER"]["y"]),
                    (kp["RIGHT_ELBOW"]["x"], kp["RIGHT_ELBOW"]["y"]),
                    (kp["RIGHT_WRIST"]["x"], kp["RIGHT_WRIST"]["y"])
                )
                left_knee = calculate_angle(
                    (kp["LEFT_HIP"]["x"], kp["LEFT_HIP"]["y"]),
                    (kp["LEFT_KNEE"]["x"], kp["LEFT_KNEE"]["y"]),
                    (kp["LEFT_ANKLE"]["x"], kp["LEFT_ANKLE"]["y"])
                )
                right_knee = calculate_angle(
                    (kp["RIGHT_HIP"]["x"], kp["RIGHT_HIP"]["y"]),
                    (kp["RIGHT_KNEE"]["x"], kp["RIGHT_KNEE"]["y"]),
                    (kp["RIGHT_ANKLE"]["x"], kp["RIGHT_ANKLE"]["y"])
                )
                left_hip = calculate_angle(
                    (kp["LEFT_SHOULDER"]["x"], kp["LEFT_SHOULDER"]["y"]),
                    (kp["LEFT_HIP"]["x"], kp["LEFT_HIP"]["y"]),
                    (kp["LEFT_KNEE"]["x"], kp["LEFT_KNEE"]["y"])
                )
                right_hip = calculate_angle(
                    (kp["RIGHT_SHOULDER"]["x"], kp["RIGHT_SHOULDER"]["y"]),
                    (kp["RIGHT_HIP"]["x"], kp["RIGHT_HIP"]["y"]),
                    (kp["RIGHT_KNEE"]["x"], kp["RIGHT_KNEE"]["y"])
                )

                # Accumulate angles
                angles_accum["left_elbow"].append(left_elbow)
                angles_accum["right_elbow"].append(right_elbow)
                angles_accum["left_knee"].append(left_knee)
                angles_accum["right_knee"].append(right_knee)
                angles_accum["left_hip"].append(left_hip)
                angles_accum["right_hip"].append(right_hip)

                # Store frame data
                out["frames"].append({
                    "frame_index": frame_idx,
                    "keypoints": kp,
                    "angles": {
                        "left_elbow": left_elbow,
                        "right_elbow": right_elbow,
                        "left_knee": left_knee,
                        "right_knee": right_knee,
                        "left_hip": left_hip,
                        "right_hip": right_hip
                    }
                })

                processed += 1
                if max_frames and processed >= max_frames: break

            frame_idx += 1

        cap.release()
        pose.close()

        # Average angles across frames
        avg_angles = {k: round(sum(v)/len(v),2) if v else 0 for k,v in angles_accum.items()}

        # Convert to features vector for classifier
        features_vector = [
            avg_angles["left_elbow"], avg_angles["right_elbow"],
            avg_angles["left_knee"], avg_angles["right_knee"],
            avg_angles["left_hip"], avg_angles["right_hip"]
        ]

        # Predict exercise using trained model
        predicted_exercise = classifier.predict([features_vector])[0]

        # Check form
        correct, feedbacks = check_form(predicted_exercise, avg_angles)

        out["summary"] = {
            "frames_processed": processed,
            "avg_angles": avg_angles,
            "predicted_exercise": predicted_exercise,
            "is_correct": correct,
            "feedback": feedbacks
        }

        # Save JSON
        os.makedirs(results_dir, exist_ok=True)
        result_path = os.path.join(results_dir, f"{job_id}.json")
        with open(result_path, "w") as fh:
            json.dump(out, fh, indent=2)

        print(f"[INFO] Job {job_id} completed. Results at {result_path}")
        return out

    except Exception as e:
        traceback.print_exc()
        return {"jobId": job_id, "error": str(e)}
