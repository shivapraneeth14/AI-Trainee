# train_classifier.py
import os
import cv2
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import joblib
import mediapipe as mp

mp_pose = mp.solutions.pose

DATASET_DIR = "dataset"  # your dataset folder containing subfolders for each exercis
MODEL_FILE = "exercise_model.pkl"  # will save in the same folder as this script

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

def extract_features_from_video(video_path, max_frames=30, sample_every_n=3):
    features_list = []
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[WARN] Cannot open video: {video_path}")
        return features_list

    pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5)
    frame_idx = 0
    processed = 0

    while True:
        ret, frame = cap.read()
        if not ret: break
        if frame_idx % sample_every_n != 0:
            frame_idx += 1
            continue

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = pose.process(rgb)

        if res.pose_landmarks:
            kp = res.pose_landmarks.landmark
            def get_point(lm_idx):
                lm = kp[lm_idx]
                return (lm.x * frame.shape[1], lm.y * frame.shape[0])

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

            features_list.append([
                left_elbow, right_elbow,
                left_knee, right_knee,
                left_hip, right_hip
            ])
            processed += 1
            if processed >= max_frames: break
        frame_idx += 1

    cap.release()
    pose.close()
    return np.mean(features_list, axis=0) if features_list else None

def load_dataset(dataset_dir):
    X, y = [], []
    for exercise in os.listdir(dataset_dir):
        exercise_dir = os.path.join(dataset_dir, exercise)
        if not os.path.isdir(exercise_dir): continue
        for vid_file in os.listdir(exercise_dir):
            if not vid_file.lower().endswith((".mp4", ".avi", ".mov")): continue
            video_path = os.path.join(exercise_dir, vid_file)
            features = extract_features_from_video(video_path)
            if features is not None:
                X.append(features)
                y.append(exercise)
                print(f"[INFO] Processed {video_path}")
    return np.array(X), np.array(y)

def train_and_save_model():
    X, y = load_dataset(DATASET_DIR)
    if len(X) == 0:
        print("[ERROR] No features extracted. Check dataset path.")
        return

    clf = RandomForestClassifier(n_estimators=100)
    clf.fit(X, y)
    joblib.dump(clf, MODEL_FILE)
    print(f"[INFO] Model trained and saved as {MODEL_FILE}")

if __name__ == "__main__":
    train_and_save_model()
