import os
import cv2
import mediapipe as mp
import math
import json
import traceback

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


def classify_activity(avg_angles):
    """Decide whether movement is push-up, squat, cricket shot, or unknown."""
    elbow = avg_angles.get("elbow")
    knee = avg_angles.get("knee")
    if knee and knee < 110: return "Squat"
    if elbow and elbow < 100: return "Push-up"
    if elbow and (100 <= elbow <= 150) and (knee and knee > 120): return "Cricket_Shot"
    return "Unknown"


def check_form(activity, avg_angles):
    """Give feedback about correctness of the detected activity."""
    feedbacks, correct = [], True
    elbow, knee = avg_angles.get("elbow"), avg_angles.get("knee")
    if activity == "Push-up":
        if not elbow: correct=False; feedbacks.append("Could not detect elbow angle.")
        elif elbow > 110: correct=False; feedbacks.append("Not going low enough — bend elbows more.")
    elif activity == "Squat":
        if not knee: correct=False; feedbacks.append("Could not detect knee angle.")
        elif knee > 120: correct=False; feedbacks.append("Squat not deep enough — bend knees more.")
    elif activity == "Cricket_Shot":
        if knee and knee > 165: correct=False; feedbacks.append("Front knee not bent enough for drive.")
        if elbow and elbow > 160: correct=False; feedbacks.append("Bat arm too straight — check follow-through.")
    else:
        feedbacks.append("No form rules for detected activity.")
    return correct, feedbacks


# ----------------- MAIN PIPELINE -----------------
def analyze_video(video_path, job_id, results_dir, sample_every_n=3, max_frames=15):
    """
    Full ML pipeline:
      1. Read video
      2. Extract frames
      3. Run MediaPipe pose detection
      4. Calculate elbow & knee angles
      5. Classify activity
      6. Check correctness (form feedback)
      7. Save results to JSON
    """
    try:
        out = {"jobId": job_id, "path": video_path, "frames": [], "summary": {}}

        if not os.path.exists(video_path):
            out["error"] = "Video not found"
            json.dump(out, open(os.path.join(results_dir, f"{job_id}.json"), "w"))
            return out

        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            out["error"] = "Cannot open video"
            json.dump(out, open(os.path.join(results_dir, f"{job_id}.json"), "w"))
            return out

        pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
        frame_idx, processed = 0, 0
        angles_accum = {"elbow": [], "knee": []}
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)

        while True:
            ret, frame = cap.read()
            if not ret: break
            if sample_every_n and (frame_idx % sample_every_n != 0):
                frame_idx += 1
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)

            if res.pose_landmarks:
                lm = lambda idx: (int(res.pose_landmarks.landmark[idx].x*width),
                                  int(res.pose_landmarks.landmark[idx].y*height))
                try:
                    kp = {
                        "LEFT_SHOULDER": lm(mp_pose.PoseLandmark.LEFT_SHOULDER.value),
                        "LEFT_ELBOW": lm(mp_pose.PoseLandmark.LEFT_ELBOW.value),
                        "LEFT_WRIST": lm(mp_pose.PoseLandmark.LEFT_WRIST.value),
                        "LEFT_HIP": lm(mp_pose.PoseLandmark.LEFT_HIP.value),
                        "LEFT_KNEE": lm(mp_pose.PoseLandmark.LEFT_KNEE.value),
                        "LEFT_ANKLE": lm(mp_pose.PoseLandmark.LEFT_ANKLE.value)
                    }
                except:
                    kp = {}

                elbow_angle = calculate_angle(kp.get("LEFT_SHOULDER"), kp.get("LEFT_ELBOW"), kp.get("LEFT_WRIST")) if kp else None
                knee_angle = calculate_angle(kp.get("LEFT_HIP"), kp.get("LEFT_KNEE"), kp.get("LEFT_ANKLE")) if kp else None

                if elbow_angle: angles_accum["elbow"].append(elbow_angle)
                if knee_angle: angles_accum["knee"].append(knee_angle)

                out["frames"].append({"frame_index": frame_idx, "angles": {"elbow": elbow_angle, "knee": knee_angle}})
                processed += 1

                if max_frames and processed >= max_frames: break

            frame_idx += 1

        cap.release()
        pose.close()

        # Compute summary
        avg_angles = {k: round(sum(v)/len(v),2) if v else None for k,v in angles_accum.items()}
        activity = classify_activity(avg_angles)
        correct, feedbacks = check_form(activity, avg_angles)
        out["summary"] = {
            "frames_processed": processed,
            "avg_angles": avg_angles,
            "predicted_activity": activity,
            "is_correct": correct,
            "feedback": feedbacks
        }

        # Save result JSON
        os.makedirs(results_dir, exist_ok=True)
        result_path = os.path.join(results_dir, f"{job_id}.json")
        with open(result_path, "w") as fh:
            json.dump(out, fh)

        print(f"[INFO] Job {job_id} completed. Results at {result_path}")
        return out

    except Exception as e:
        traceback.print_exc()
        return {"jobId": job_id, "error": str(e)}
