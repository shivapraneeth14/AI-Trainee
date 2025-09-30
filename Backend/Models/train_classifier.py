import os
import joblib
import numpy as np
import json
import time
from collections import defaultdict, deque
from typing import Dict, List, Tuple, Optional
from datetime import datetime

MODEL_FILE = os.path.join(os.path.dirname(__file__), "exercise_model.pkl")

# Comprehensive exercise configuration with all required parameters
EXERCISE_CONFIG = {
    "squat": {
        "joints": ["left_knee", "right_knee", "left_hip", "right_hip", "left_ankle", "right_ankle", "left_shoulder", "right_shoulder"],
        "key_angles": {
            "knee": {"ideal_range": (80, 120), "full_range": (60, 160), "critical": True},
            "hip": {"ideal_range": (90, 140), "full_range": (70, 180), "critical": True},
            "ankle": {"ideal_range": (80, 110), "full_range": (60, 130), "critical": False},
            "back": {"ideal_range": (170, 180), "full_range": (150, 190), "critical": True}
        },
        "rep_threshold": {"knee": (60, 160), "hip": (80, 180)},
        "form_checks": ["knee_alignment", "back_straight", "depth_check", "symmetry"],
        "common_mistakes": {
            "knee_valgus": "Keep your knees aligned with your toes",
            "back_rounding": "Keep your chest up and back straight",
            "insufficient_depth": "Lower until your thighs are parallel to the ground",
            "asymmetry": "Keep both legs moving symmetrically"
        },
        "calories_per_rep": 0.3,
        "difficulty_progression": ["wall_sit", "bodyweight_squat", "weighted_squat"],
        "rest_time": 60
    },
    "pushup": {
        "joints": ["left_elbow", "right_elbow", "left_shoulder", "right_shoulder", "left_hip", "right_hip", "left_wrist", "right_wrist"],
        "key_angles": {
            "elbow": {"ideal_range": (90, 120), "full_range": (60, 170), "critical": True},
            "shoulder": {"ideal_range": (90, 180), "full_range": (70, 190), "critical": True},
            "hip": {"ideal_range": (170, 180), "full_range": (160, 190), "critical": True},
            "back": {"ideal_range": (170, 180), "full_range": (150, 190), "critical": True}
        },
        "rep_threshold": {"elbow": (60, 170), "shoulder": (90, 180)},
        "form_checks": ["elbow_alignment", "body_alignment", "full_range", "symmetry"],
        "common_mistakes": {
            "elbow_flare": "Keep elbows close to your body at 45-degree angle",
            "hip_sag": "Keep your body in a straight line from head to heels",
            "incomplete_range": "Lower your chest until it nearly touches the ground",
            "asymmetry": "Keep both arms moving at the same pace"
        },
        "calories_per_rep": 0.4,
        "difficulty_progression": ["knee_pushup", "standard_pushup", "decline_pushup"],
        "rest_time": 90
    },
    "pullup": {
        "joints": ["left_elbow", "right_elbow", "left_shoulder", "right_shoulder", "left_hip", "right_hip"],
        "key_angles": {
            "elbow": {"ideal_range": (30, 90), "full_range": (20, 160), "critical": True},
            "shoulder": {"ideal_range": (45, 135), "full_range": (30, 180), "critical": True},
            "hip": {"ideal_range": (170, 180), "full_range": (160, 190), "critical": False}
        },
        "rep_threshold": {"elbow": (20, 160), "shoulder": (30, 180)},
        "form_checks": ["full_range", "controlled_movement", "symmetry"],
        "common_mistakes": {
            "incomplete_range": "Pull up until your chin clears the bar",
            "swinging": "Use controlled movement, avoid momentum",
            "asymmetry": "Pull with both arms equally"
        },
        "calories_per_rep": 0.6,
        "difficulty_progression": ["assisted_pullup", "negative_pullup", "standard_pullup"],
        "rest_time": 120
    },
    "plank": {
        "joints": ["left_shoulder", "right_shoulder", "left_hip", "right_hip", "left_knee", "right_knee", "left_elbow", "right_elbow"],
        "key_angles": {
            "shoulder": {"ideal_range": (90, 180), "full_range": (80, 190), "critical": True},
            "hip": {"ideal_range": (170, 180), "full_range": (160, 190), "critical": True},
            "knee": {"ideal_range": (170, 180), "full_range": (160, 190), "critical": False},
            "elbow": {"ideal_range": (90, 180), "full_range": (80, 190), "critical": False}
        },
        "rep_threshold": {"shoulder": (90, 180), "hip": (170, 180)},
        "form_checks": ["body_alignment", "hip_position", "shoulder_stability", "symmetry"],
        "common_mistakes": {
            "hip_too_high": "Lower your hips to align with your shoulders and heels",
            "hip_too_low": "Raise your hips to maintain straight line",
            "shoulder_instability": "Keep shoulders directly over your wrists",
            "asymmetry": "Distribute weight evenly between both sides"
        },
        "calories_per_rep": 0.2,  # Per 10 seconds
        "difficulty_progression": ["knee_plank", "standard_plank", "side_plank"],
        "rest_time": 60
    },
    "lunge": {
        "joints": ["left_knee", "right_knee", "left_hip", "right_hip", "left_ankle", "right_ankle"],
        "key_angles": {
            "knee": {"ideal_range": (70, 120), "full_range": (60, 160), "critical": True},
            "hip": {"ideal_range": (80, 140), "full_range": (60, 180), "critical": True},
            "ankle": {"ideal_range": (80, 110), "full_range": (60, 130), "critical": False}
        },
        "rep_threshold": {"knee": (70, 160), "hip": (80, 180)},
        "form_checks": ["knee_alignment", "depth_check", "balance", "symmetry"],
        "common_mistakes": {
            "knee_over_toe": "Keep front knee behind your toe",
            "insufficient_depth": "Lower until your back knee nearly touches the ground",
            "poor_balance": "Keep your torso upright and core engaged",
            "asymmetry": "Alternate legs and maintain consistent form"
        },
        "calories_per_rep": 0.25,
        "difficulty_progression": ["static_lunge", "walking_lunge", "jumping_lunge"],
        "rest_time": 60
    },
    "jumping_jack": {
        "joints": ["left_shoulder", "right_shoulder", "left_hip", "right_hip", "left_knee", "right_knee", "left_ankle", "right_ankle"],
        "key_angles": {
            "shoulder": {"ideal_range": (90, 180), "full_range": (60, 190), "critical": True},
            "hip": {"ideal_range": (160, 180), "full_range": (140, 190), "critical": False},
            "knee": {"ideal_range": (150, 180), "full_range": (120, 190), "critical": False},
            "ankle": {"ideal_range": (80, 120), "full_range": (60, 140), "critical": False}
        },
        "rep_threshold": {"shoulder": (90, 180), "knee": (150, 180)},
        "form_checks": ["arm_extension", "leg_extension", "coordination", "symmetry"],
        "common_mistakes": {
            "incomplete_extension": "Fully extend arms overhead and legs apart",
            "poor_timing": "Coordinate arm and leg movements simultaneously",
            "landing_impact": "Land softly on the balls of your feet",
            "asymmetry": "Keep movements symmetrical on both sides"
        },
        "calories_per_rep": 0.35,
        "difficulty_progression": ["step_tap", "slow_jumping_jack", "fast_jumping_jack"],
        "rest_time": 30
    },
    "bicep_curl": {
        "joints": ["left_elbow", "right_elbow", "left_shoulder", "right_shoulder", "left_wrist", "right_wrist"],
        "key_angles": {
            "elbow": {"ideal_range": (30, 160), "full_range": (20, 170), "critical": True},
            "shoulder": {"ideal_range": (90, 180), "full_range": (80, 190), "critical": False},
            "wrist": {"ideal_range": (170, 180), "full_range": (160, 190), "critical": False}
        },
        "rep_threshold": {"elbow": (30, 160), "shoulder": (90, 180)},
        "form_checks": ["elbow_stability", "controlled_movement", "full_range", "symmetry"],
        "common_mistakes": {
            "swinging": "Keep elbows stationary, move only your forearms",
            "incomplete_range": "Lower weights fully and curl up completely",
            "momentum_use": "Control the movement throughout the entire range",
            "asymmetry": "Curl both arms at the same pace"
        },
        "calories_per_rep": 0.2,
        "difficulty_progression": ["light_weight", "medium_weight", "heavy_weight"],
        "rest_time": 60
    }
}

def load_model(model_file=MODEL_FILE):
    """Load pre-trained ML model"""
    if not os.path.exists(model_file):
        # Create a comprehensive model for all exercises
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.model_selection import train_test_split
        
        # Generate more comprehensive training data for all exercises
        X_dummy = np.random.rand(500, 12) * 180  # 12 angle features for better detection
        exercise_names = list(EXERCISE_CONFIG.keys())
        y_dummy = np.random.choice(exercise_names, 500)
        
        clf = RandomForestClassifier(n_estimators=200, random_state=42, max_depth=10)
        clf.fit(X_dummy, y_dummy)
        
        # Save the model
        joblib.dump(clf, model_file)
        print(f"Created and saved comprehensive model at {model_file}")
    
    return joblib.load(model_file)

# Session tracking for sets, duration, and fatigue detection
session_data = {
    "start_time": None,
    "current_exercise": None,
    "rep_count": 0,
    "set_count": 0,
    "last_rep_time": None,
    "fatigue_signals": [],
    "motion_history": deque(maxlen=30)  # Store last 30 frames for motion analysis
}

def calculate_angle_3d(a, b, c):
    """Calculate angle at point b using 3D coordinates"""
    try:
        a = np.array([a["x"], a["y"], a["z"]])
        b = np.array([b["x"], b["y"], b["z"]])
        c = np.array([c["x"], c["y"], c["z"]])
    except:
        return None
    ab = a - b
    cb = c - b
    dot = np.dot(ab, cb)
    norm_ab = np.linalg.norm(ab)
    norm_cb = np.linalg.norm(cb)
    if norm_ab == 0 or norm_cb == 0:
        return None
    cos_angle = np.clip(dot / (norm_ab * norm_cb), -1.0, 1.0)
    return np.degrees(np.arccos(cos_angle))

def calculate_comprehensive_angles(landmarks):
    """Calculate all important angles for comprehensive analysis"""
    angles = {}
    
    # Helper function to get landmark
    def get_landmark(idx):
        return landmarks[idx] if idx < len(landmarks) else None
    
    # Knee angles (left and right)
    left_knee = calculate_angle_3d(get_landmark(23), get_landmark(25), get_landmark(27))
    right_knee = calculate_angle_3d(get_landmark(24), get_landmark(26), get_landmark(28))
    angles["knee"] = {"left": left_knee, "right": right_knee, "average": (left_knee + right_knee) / 2 if left_knee and right_knee else None}
    
    # Elbow angles (left and right)
    left_elbow = calculate_angle_3d(get_landmark(11), get_landmark(13), get_landmark(15))
    right_elbow = calculate_angle_3d(get_landmark(12), get_landmark(14), get_landmark(16))
    angles["elbow"] = {"left": left_elbow, "right": right_elbow, "average": (left_elbow + right_elbow) / 2 if left_elbow and right_elbow else None}
    
    # Hip angles (left and right)
    left_hip = calculate_angle_3d(get_landmark(11), get_landmark(23), get_landmark(25))
    right_hip = calculate_angle_3d(get_landmark(12), get_landmark(24), get_landmark(26))
    angles["hip"] = {"left": left_hip, "right": right_hip, "average": (left_hip + right_hip) / 2 if left_hip and right_hip else None}
    
    # Shoulder angles (left and right)
    left_shoulder = calculate_angle_3d(get_landmark(13), get_landmark(11), get_landmark(23))
    right_shoulder = calculate_angle_3d(get_landmark(14), get_landmark(12), get_landmark(24))
    angles["shoulder"] = {"left": left_shoulder, "right": right_shoulder, "average": (left_shoulder + right_shoulder) / 2 if left_shoulder and right_shoulder else None}
    
    # Back/spine angle (using shoulder and hip alignment)
    back_angle = calculate_angle_3d(
        {"x": (get_landmark(11)["x"] + get_landmark(12)["x"]) / 2, 
         "y": (get_landmark(11)["y"] + get_landmark(12)["y"]) / 2, 
         "z": (get_landmark(11)["z"] + get_landmark(12)["z"]) / 2},
        {"x": (get_landmark(23)["x"] + get_landmark(24)["x"]) / 2, 
         "y": (get_landmark(23)["y"] + get_landmark(24)["y"]) / 2, 
         "z": (get_landmark(23)["z"] + get_landmark(24)["z"]) / 2},
        get_landmark(0)  # nose for reference
    )
    angles["back"] = back_angle
    
    # Ankle angles (for exercises like squats and lunges)
    left_ankle = calculate_angle_3d(get_landmark(25), get_landmark(27), get_landmark(31))
    right_ankle = calculate_angle_3d(get_landmark(26), get_landmark(28), get_landmark(32))
    angles["ankle"] = {"left": left_ankle, "right": right_ankle, "average": (left_ankle + right_ankle) / 2 if left_ankle and right_ankle else None}
    
    return angles

def analyze_symmetry(angles):
    """Analyze left-right symmetry for bilateral exercises"""
    symmetry_scores = {}
    
    for joint in ["knee", "elbow", "hip", "shoulder", "ankle"]:
        if joint in angles and angles[joint].get("left") and angles[joint].get("right"):
            left_val = angles[joint]["left"]
            right_val = angles[joint]["right"]
            if left_val and right_val:
                diff = abs(left_val - right_val)
                symmetry_scores[joint] = max(0, 100 - (diff * 2))  # Score out of 100
    
    overall_symmetry = np.mean(list(symmetry_scores.values())) if symmetry_scores else 0
    return {
        "overall": overall_symmetry,
        "scores": symmetry_scores,
        "status": "Good" if overall_symmetry > 80 else "Imbalance"
    }

def analyze_motion_quality(motion_history):
    """Analyze motion speed and smoothness"""
    if len(motion_history) < 5:
        return {"speed": "ok", "smoothness": "smooth"}
    
    # Calculate motion speed (angle change rate)
    recent_angles = [frame["angles"] for frame in motion_history[-10:]]
    speed_scores = []
    
    for joint in ["knee", "elbow", "hip"]:
        if joint in recent_angles[0]:
            values = [frame[joint].get("average", 0) for frame in recent_angles if frame[joint].get("average")]
            if len(values) > 1:
                changes = [abs(values[i] - values[i-1]) for i in range(1, len(values))]
                avg_change = np.mean(changes) if changes else 0
                speed_scores.append(avg_change)
    
    avg_speed = np.mean(speed_scores) if speed_scores else 0
    speed = "fast" if avg_speed > 15 else "slow" if avg_speed < 5 else "ok"
    
    # Calculate smoothness (variance in motion)
    smoothness_scores = []
    for joint in ["knee", "elbow", "hip"]:
        if joint in recent_angles[0]:
            values = [frame[joint].get("average", 0) for frame in recent_angles if frame[joint].get("average")]
            if len(values) > 2:
                variance = np.var(values)
                smoothness_scores.append(variance)
    
    avg_variance = np.mean(smoothness_scores) if smoothness_scores else 0
    smoothness = "jerky" if avg_variance > 100 else "smooth"
    
    return {"speed": speed, "smoothness": smoothness}

def detect_fatigue(motion_history, current_angles):
    """Detect fatigue signals from motion patterns"""
    if len(motion_history) < 10:
        return {"fatigue_level": "low", "signals": []}
    
    fatigue_signals = []
    
    # Check for decreased range of motion
    recent_ranges = []
    for frame in motion_history[-10:]:
        for joint in ["knee", "elbow"]:
            if joint in frame["angles"] and frame["angles"][joint].get("average"):
                recent_ranges.append(frame["angles"][joint]["average"])
    
    if recent_ranges:
        current_range = np.mean([current_angles[joint].get("average", 0) for joint in ["knee", "elbow"] if joint in current_angles])
        historical_range = np.mean(recent_ranges)
        
        if current_range < historical_range * 0.8:  # 20% decrease
            fatigue_signals.append("decreased_range_of_motion")
    
    # Check for increased motion irregularity
    motion_variance = []
    for frame in motion_history[-5:]:
        for joint in ["knee", "elbow"]:
            if joint in frame["angles"] and frame["angles"][joint].get("average"):
                motion_variance.append(frame["angles"][joint]["average"])
    
    if len(motion_variance) > 3:
        variance = np.var(motion_variance)
        if variance > 150:  # High variance indicates fatigue
            fatigue_signals.append("irregular_motion")
    
    fatigue_level = "high" if len(fatigue_signals) >= 2 else "medium" if len(fatigue_signals) == 1 else "low"
    
    return {"fatigue_level": fatigue_level, "signals": fatigue_signals}

def calculate_calories_burned(exercise, reps, duration_seconds):
    """Estimate calories burned based on exercise type, reps, and duration"""
    if exercise not in EXERCISE_CONFIG:
        return 0
    
    calories_per_rep = EXERCISE_CONFIG[exercise]["calories_per_rep"]
    
    # Base calories from reps
    base_calories = reps * calories_per_rep
    
    # Additional calories from duration (for static exercises like plank)
    if exercise == "plank":
        duration_minutes = duration_seconds / 60
        base_calories += duration_minutes * 2  # 2 calories per minute for plank
    
    return round(base_calories, 1)

def get_adaptive_suggestion(exercise, reps, sets, fatigue_level, posture_status):
    """Generate adaptive coaching suggestions"""
    suggestions = []
    
    if exercise not in EXERCISE_CONFIG:
        return "Keep up the great work!"
    
    config = EXERCISE_CONFIG[exercise]
    
    # Difficulty progression suggestions
    if reps >= 15 and sets >= 3 and fatigue_level == "low":
        next_difficulty = config["difficulty_progression"][-1] if len(config["difficulty_progression"]) > 2 else config["difficulty_progression"[-1]]
        suggestions.append(f"Ready for progression! Try {next_difficulty}")
    
    # Rest suggestions
    if fatigue_level == "high":
        suggestions.append(f"Take a {config['rest_time']} second rest")
    
    # Form improvement suggestions
    if posture_status == "Bad":
        suggestions.append("Focus on form over speed")
    
    # Encouragement for good performance
    if reps >= 10 and posture_status == "Good" and fatigue_level == "low":
        suggestions.append("Excellent form! You're ready for more challenge")
    
    return suggestions[0] if suggestions else "Keep up the great work!"

def get_motivational_message(exercise, reps, sets):
    """Generate short motivational messages"""
    messages = [
        "You're doing great! 💪",
        "Keep pushing yourself! 🔥",
        "Amazing progress! ⭐",
        "You're getting stronger! 💪",
        "Fantastic form! 🎯",
        "Keep it up! 🚀",
        "You're on fire! 🔥",
        "Excellent work! 👏"
    ]
    
    # Special messages for milestones
    if reps >= 20:
        return "Incredible endurance! 🏆"
    elif reps >= 10:
        return "Great job! You're building strength! 💪"
    elif sets >= 3:
        return "Outstanding consistency! ⭐"
    
    return np.random.choice(messages)

def smooth_angles(angle_sequence, window=3):
    smoothed = []
    for i in range(len(angle_sequence)):
        vals = [angle_sequence[j] for j in range(max(0, i-window+1), i+1) if angle_sequence[j] is not None]
        smoothed.append(np.mean(vals) if vals else None)
    return smoothed

def count_reps_from_angle_sequence(angle_sequence, min_angle=50, max_angle=160):
    reps = 0
    direction = None
    smoothed_seq = smooth_angles(angle_sequence)
    for angle in smoothed_seq:
        if angle is None:
            continue
        if angle < min_angle and direction != "down":
            direction = "down"
        elif angle > max_angle and direction == "down":
            direction = "up"
            reps += 1
    return reps

def predict_activity_and_reps(mediapipe_json, clf):
    """Comprehensive AI Fitness Coach - Analyzes pose and provides complete exercise guidance"""
    global session_data
    
    # Initialize session if first call
    if session_data["start_time"] is None:
        session_data["start_time"] = time.time()
        session_data["current_exercise"] = None
    
    frames_keypoints = []
    for frame in mediapipe_json:
        landmarks = frame.get("landmarks", [])
        if len(landmarks) < 33:
            continue
        frames_keypoints.append(landmarks)

    if not frames_keypoints:
        return {"error": "No valid frames with 33 keypoints"}

    # Calculate comprehensive angles for each frame
    angles_per_frame = []
    for frame in frames_keypoints:
        angles = calculate_comprehensive_angles(frame)
        angles_per_frame.append(angles)

    # Store current frame data for motion analysis
    current_angles = angles_per_frame[-1] if angles_per_frame else {}
    current_time = time.time()
    
    # Prepare feature vector for exercise detection (12 features)
    feature_vector = []
    for joint in ["knee", "elbow", "hip", "shoulder", "ankle", "back"]:
        if joint in current_angles:
            if isinstance(current_angles[joint], dict) and "average" in current_angles[joint]:
                feature_vector.append(current_angles[joint]["average"] or 0)
            else:
                feature_vector.append(current_angles[joint] or 0)
        else:
            feature_vector.append(0)
    
    # Add motion features
    if len(angles_per_frame) > 1:
        prev_angles = angles_per_frame[-2]
        motion_features = []
        for joint in ["knee", "elbow", "hip", "shoulder"]:
            if joint in current_angles and joint in prev_angles:
                curr_val = current_angles[joint].get("average", 0) if isinstance(current_angles[joint], dict) else current_angles[joint] or 0
                prev_val = prev_angles[joint].get("average", 0) if isinstance(prev_angles[joint], dict) else prev_angles[joint] or 0
                motion_features.append(abs(curr_val - prev_val))
            else:
                motion_features.append(0)
        feature_vector.extend(motion_features)
    else:
        feature_vector.extend([0, 0, 0, 0])  # No motion data yet

    # Exercise detection with confidence
    try:
        predicted_exercise = clf.predict([feature_vector])[0]
        confidence_scores = clf.predict_proba([feature_vector])[0]
        confidence = max(confidence_scores) * 100
    except Exception as e:
        return {"error": f"Prediction failed: {str(e)}"}

    # Update session tracking
    if session_data["current_exercise"] != predicted_exercise:
        session_data["current_exercise"] = predicted_exercise
        session_data["rep_count"] = 0
        session_data["set_count"] = 0

    # Advanced rep counting with set detection
    reps = count_reps_advanced(angles_per_frame, predicted_exercise)
    
    # Update rep and set counts
    if reps > session_data["rep_count"]:
        session_data["rep_count"] = reps
        session_data["last_rep_time"] = current_time
        
        # Detect new set (gap of more than 10 seconds between reps)
        if session_data["last_rep_time"] and (current_time - session_data["last_rep_time"]) > 10:
            session_data["set_count"] += 1

    # Analyze angles with ideal ranges
    angles_analysis = analyze_angles_with_ranges(current_angles, predicted_exercise)
    
    # Symmetry analysis
    symmetry = analyze_symmetry(current_angles)
    
    # Motion quality analysis
    session_data["motion_history"].append({
        "timestamp": current_time,
        "angles": current_angles
    })
    motion_quality = analyze_motion_quality(session_data["motion_history"])
    
    # Fatigue detection
    fatigue = detect_fatigue(session_data["motion_history"], current_angles)
    
    # Posture evaluation
    posture = evaluate_posture(current_angles, predicted_exercise, EXERCISE_CONFIG.get(predicted_exercise, {}))
    
    # Performance metrics
    duration = current_time - session_data["start_time"] if session_data["start_time"] else 0
    calories = calculate_calories_burned(predicted_exercise, reps, duration)
    
    # Adaptive coaching
    suggestion = get_adaptive_suggestion(predicted_exercise, reps, session_data["set_count"], 
                                       fatigue["fatigue_level"], posture["status"])
    motivation = get_motivational_message(predicted_exercise, reps, session_data["set_count"])
    
    # Correction tip
    correction = get_correction_tip(posture, EXERCISE_CONFIG.get(predicted_exercise, {}))

    return {
        "exercise": predicted_exercise,
        "confidence": round(confidence, 1),
        "reps": reps,
        "sets": session_data["set_count"],
        "angles": angles_analysis,
        "symmetry": symmetry["status"],
        "motion": motion_quality,
        "posture": {
            "status": posture["status"],
            "reason": posture["reason"]
        },
        "correction": correction,
        "calories": calories,
        "duration": round(duration, 1),
        "suggestion": suggestion,
        "motivation": motivation
    }

def count_reps_advanced(angles_per_frame, exercise):
    """Advanced rep counting with exercise-specific logic"""
    if not angles_per_frame or exercise not in EXERCISE_CONFIG:
        return 0
    
    config = EXERCISE_CONFIG[exercise]
    rep_threshold = config["rep_threshold"]
    
    # Get relevant angle sequences for the exercise
    angle_sequences = {}
    
    if "knee" in rep_threshold:
        left_knee_seq = [frame["knee"].get("left", 0) for frame in angles_per_frame if "knee" in frame]
        right_knee_seq = [frame["knee"].get("right", 0) for frame in angles_per_frame if "knee" in frame]
        angle_sequences["knee"] = (left_knee_seq, right_knee_seq)
    
    if "elbow" in rep_threshold:
        left_elbow_seq = [frame["elbow"].get("left", 0) for frame in angles_per_frame if "elbow" in frame]
        right_elbow_seq = [frame["elbow"].get("right", 0) for frame in angles_per_frame if "elbow" in frame]
        angle_sequences["elbow"] = (left_elbow_seq, right_elbow_seq)
    
    if "hip" in rep_threshold:
        left_hip_seq = [frame["hip"].get("left", 0) for frame in angles_per_frame if "hip" in frame]
        right_hip_seq = [frame["hip"].get("right", 0) for frame in angles_per_frame if "hip" in frame]
        angle_sequences["hip"] = (left_hip_seq, right_hip_seq)
    
    # Count reps for each relevant joint
    total_reps = 0
    joint_counts = 0
    
    for joint, threshold in rep_threshold.items():
        if joint in angle_sequences:
            left_seq, right_seq = angle_sequences[joint]
            left_reps = count_reps_from_angle_sequence(left_seq, threshold[0], threshold[1])
            right_reps = count_reps_from_angle_sequence(right_seq, threshold[0], threshold[1])
            avg_reps = (left_reps + right_reps) / 2
            total_reps += avg_reps
            joint_counts += 1
    
    return int(total_reps / joint_counts) if joint_counts > 0 else 0

def analyze_angles_with_ranges(current_angles, exercise):
    """Analyze angles with ideal ranges for the specific exercise"""
    if exercise not in EXERCISE_CONFIG:
        return {}
    
    config = EXERCISE_CONFIG[exercise]
    key_angles = config["key_angles"]
    angles_analysis = {}
    
    for joint, angle_data in key_angles.items():
        if joint in current_angles:
            current_value = current_angles[joint].get("average", 0) if isinstance(current_angles[joint], dict) else current_angles[joint] or 0
            ideal_range = angle_data["ideal_range"]
            full_range = angle_data["full_range"]
            
            # Determine if angle is in ideal range
            in_ideal = ideal_range[0] <= current_value <= ideal_range[1]
            in_full = full_range[0] <= current_value <= full_range[1]
            
            angles_analysis[joint] = {
                "value": round(current_value, 1),
                "ideal_range": f"{ideal_range[0]}-{ideal_range[1]}°",
                "in_ideal": in_ideal,
                "in_full_range": in_full,
                "critical": angle_data["critical"]
            }
    
    return angles_analysis

def evaluate_posture(current_angles, exercise, config):
    """Evaluate posture correctness based on exercise-specific criteria"""
    if not config:
        return {"status": "Unknown", "reason": "Exercise not recognized"}
    
    issues = []
    
    # Check critical angles
    for joint, angle_data in config["key_angles"].items():
        if angle_data["critical"] and joint in current_angles:
            current_value = current_angles[joint].get("average", 0) if isinstance(current_angles[joint], dict) else current_angles[joint] or 0
            ideal_range = angle_data["ideal_range"]
            
            if not (ideal_range[0] <= current_value <= ideal_range[1]):
                if joint == "knee":
                    if current_value < ideal_range[0]:
                        issues.append("Insufficient knee bend")
                    else:
                        issues.append("Knee angle too wide")
                elif joint == "elbow":
                    if current_value < ideal_range[0]:
                        issues.append("Elbow not bent enough")
                    else:
                        issues.append("Elbow overextended")
                elif joint == "back":
                    if current_value < ideal_range[0]:
                        issues.append("Back not straight")
                    else:
                        issues.append("Back arched too much")
    
    # Check symmetry for bilateral exercises
    symmetry_scores = []
    for joint in ["knee", "elbow", "hip", "shoulder"]:
        if joint in current_angles and isinstance(current_angles[joint], dict):
            left_val = current_angles[joint].get("left")
            right_val = current_angles[joint].get("right")
            if left_val and right_val:
                diff = abs(left_val - right_val)
                symmetry_scores.append(diff)
    
    if symmetry_scores and np.mean(symmetry_scores) > 15:
        issues.append("Significant asymmetry detected")
    
    # Determine overall posture status
    if not issues:
        status = "Good"
        reason = "All angles within ideal ranges"
    elif len(issues) <= 2:
        status = "Fair"
        reason = "; ".join(issues)
    else:
        status = "Bad"
        reason = "; ".join(issues)
    
    return {"status": status, "reason": reason}

def get_correction_tip(posture, config):
    """Generate personalized correction tips based on posture analysis"""
    if posture["status"] == "Good":
        return "Perfect form! Keep it up!"
    
    if not config or "common_mistakes" not in config:
        return "Focus on maintaining proper form"
    
    # Match detected issues with common mistakes
    reason = posture["reason"].lower()
    corrections = []
    
    if "knee" in reason:
        if "insufficient" in reason or "not bent" in reason:
            corrections.append(config["common_mistakes"].get("insufficient_depth", "Lower deeper into the movement"))
        elif "too wide" in reason:
            corrections.append(config["common_mistakes"].get("knee_valgus", "Keep knees aligned with toes"))
    
    if "elbow" in reason:
        if "not bent" in reason:
            corrections.append(config["common_mistakes"].get("incomplete_range", "Complete the full range of motion"))
        elif "overextended" in reason:
            corrections.append(config["common_mistakes"].get("elbow_flare", "Keep elbows close to your body"))
    
    if "back" in reason:
        corrections.append(config["common_mistakes"].get("back_rounding", "Keep your back straight and chest up"))
    
    if "asymmetry" in reason:
        corrections.append(config["common_mistakes"].get("asymmetry", "Focus on balanced movement on both sides"))
    
    return corrections[0] if corrections else "Focus on proper form and technique"
