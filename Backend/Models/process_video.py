import os
import cv2
import numpy as np
import joblib
import mediapipe as mp
import json

mp_pose = mp.solutions.pose
MODEL_FILE = "exercise_model.pkl"

def analyze_video(video_path, job_id, results_dir, sample_every_n=3, max_frames=30, model=None):
    print(f"[INFO] Starting analysis for jobId={job_id}, video={video_path}")

    # Load model if not provided
    if model is None:
        if not os.path.exists(MODEL_FILE):
            raise FileNotFoundError(f"[ERROR] Trained model not found: {MODEL_FILE}")
        model = joblib.load(MODEL_FILE)
        print("[INFO] ML model loaded successfully")

    # Helper function to calculate joint angles
    def calculate_angle(a, b, c):
        try:
            ax, ay = a; bx, by = b; cx, cy = c
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

    # Extract features from video frames
    def extract_features(video_path, max_frames=30, sample_every_n=3):
        features_list = []
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"[WARN] Cannot open video: {video_path}")
            return None

        pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
        frame_idx, processed = 0, 0

        while True:
            ret, frame = cap.read()
            if not ret: 
                break
            if frame_idx % sample_every_n != 0:
                frame_idx += 1
                continue

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = pose.process(rgb)

            if res.pose_landmarks:
                kp = res.pose_landmarks.landmark
                def get_point(i): return (kp[i].x * frame.shape[1], kp[i].y * frame.shape[0])

                left_elbow = calculate_angle(get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value),
                                             get_point(mp_pose.PoseLandmark.LEFT_ELBOW.value),
                                             get_point(mp_pose.PoseLandmark.LEFT_WRIST.value))
                right_elbow = calculate_angle(get_point(mp_pose.PoseLandmark.RIGHT_SHOULDER.value),
                                              get_point(mp_pose.PoseLandmark.RIGHT_ELBOW.value),
                                              get_point(mp_pose.PoseLandmark.RIGHT_WRIST.value))
                left_knee = calculate_angle(get_point(mp_pose.PoseLandmark.LEFT_HIP.value),
                                            get_point(mp_pose.PoseLandmark.LEFT_KNEE.value),
                                            get_point(mp_pose.PoseLandmark.LEFT_ANKLE.value))
                right_knee = calculate_angle(get_point(mp_pose.PoseLandmark.RIGHT_HIP.value),
                                             get_point(mp_pose.PoseLandmark.RIGHT_KNEE.value),
                                             get_point(mp_pose.PoseLandmark.RIGHT_ANKLE.value))
                left_hip = calculate_angle(get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value),
                                           get_point(mp_pose.PoseLandmark.LEFT_HIP.value),
                                           get_point(mp_pose.PoseLandmark.LEFT_KNEE.value))
                right_hip = calculate_angle(get_point(mp_pose.PoseLandmark.RIGHT_SHOULDER.value),
                                            get_point(mp_pose.PoseLandmark.RIGHT_HIP.value),
                                            get_point(mp_pose.PoseLandmark.RIGHT_KNEE.value))

                frame_features = [left_elbow, right_elbow, left_knee, right_knee, left_hip, right_hip]
                features_list.append(frame_features)
                processed += 1

                print(f"[DEBUG] Frame {frame_idx}: Features={frame_features}")

                if processed >= max_frames:
                    break
            frame_idx += 1

        cap.release()
        pose.close()
        if features_list:
            avg_features = np.mean(features_list, axis=0)
            print(f"[INFO] Average features from {processed} frames: {avg_features}")
            return avg_features
        else:
            print("[WARN] No features extracted from video")
            return None

    # Main analysis logic
    try:
        features = extract_features(video_path, max_frames, sample_every_n)
        if features is None:
            summary = {"predicted_exercise": "unknown", "is_correct": False, "feedback": ["No pose detected"]}
        else:
            prediction = model.predict([features])[0]
            summary = {
                "predicted_exercise": str(prediction),
                "is_correct": True,
                "feedback": [f"Good {prediction}!"]
            }
            print(f"[INFO] Model prediction: {prediction}")

        # Save summary to file
        os.makedirs(results_dir, exist_ok=True)
        result_path = os.path.join(results_dir, f"{job_id}.json")
        with open(result_path, "w") as f:
            json.dump(summary, f, indent=2)
        print(f"[INFO] Result saved to {result_path}")

        return summary

    except Exception as e:
        print(f"[ERROR] Video analysis failed: {e}")
        return {"predicted_exercise": "error", "is_correct": False, "feedback": [f"Processing failed: {str(e)}"]}
