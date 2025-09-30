#!/usr/bin/env python3
"""
AI Fitness Coach - Comprehensive Example Usage

This script demonstrates how to use the enhanced AI fitness coach system
that analyzes 33 pose landmarks and provides complete exercise guidance.
"""

import json
import time
import random
from train_classifier import predict_activity_and_reps, load_model, EXERCISE_CONFIG
from process_video import reset_session, get_session_summary

def create_sample_mediapipe_data(exercise_type="squat", num_frames=10):
    """Create sample MediaPipe JSON data for testing"""
    sample_data = []
    
    # Exercise-specific angle patterns
    angle_patterns = {
        "squat": {
            "knee_range": (60, 160),
            "hip_range": (80, 180),
            "base_knee": 120,
            "base_hip": 150
        },
        "pushup": {
            "elbow_range": (60, 170),
            "shoulder_range": (90, 180),
            "base_elbow": 140,
            "base_shoulder": 160
        },
        "plank": {
            "shoulder_range": (90, 180),
            "hip_range": (170, 180),
            "base_shoulder": 160,
            "base_hip": 175
        }
    }
    
    pattern = angle_patterns.get(exercise_type, angle_patterns["squat"])
    
    for frame_idx in range(num_frames):
        # Simulate movement cycle
        cycle_progress = (frame_idx / num_frames) * 2 * 3.14159  # Full cycle
        movement_factor = abs(0.5 * (1 + np.sin(cycle_progress)))
        
        # Generate 33 landmarks (MediaPipe format)
        landmarks = []
        for i in range(33):
            # Create realistic 3D coordinates
            x = random.uniform(0.2, 0.8)
            y = random.uniform(0.2, 0.8)
            z = random.uniform(-0.5, 0.5)
            
            # Adjust key landmarks for exercise type
            if exercise_type == "squat":
                if i in [23, 24]:  # Hip landmarks
                    y += movement_factor * 0.1
                elif i in [25, 26]:  # Knee landmarks
                    y += movement_factor * 0.2
            elif exercise_type == "pushup":
                if i in [11, 12]:  # Shoulder landmarks
                    y -= movement_factor * 0.1
                elif i in [13, 14]:  # Elbow landmarks
                    y -= movement_factor * 0.15
            
            landmarks.append({
                "x": x,
                "y": y,
                "z": z,
                "visibility": random.uniform(0.8, 1.0)
            })
        
        sample_data.append({
            "landmarks": landmarks,
            "timestamp": frame_idx * 0.1  # 10 FPS
        })
    
    return sample_data

def demonstrate_fitness_coach():
    """Demonstrate the comprehensive AI fitness coach capabilities"""
    print("🤖 AI Fitness Coach - Comprehensive Analysis Demo")
    print("=" * 60)
    
    # Load the model
    print("Loading AI model...")
    clf = load_model()
    
    # Reset session for clean start
    reset_session()
    
    # Test different exercises
    exercises_to_test = ["squat", "pushup", "plank", "lunge", "jumping_jack", "bicep_curl", "pullup"]
    
    for exercise in exercises_to_test:
        print(f"\n🏋️ Testing Exercise: {exercise.upper()}")
        print("-" * 40)
        
        # Create sample data for this exercise
        sample_data = create_sample_mediapipe_data(exercise, num_frames=15)
        
        # Analyze with AI fitness coach
        try:
            result = predict_activity_and_reps(sample_data, clf)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            # Display comprehensive results
            print(f"✅ Exercise Detected: {result['exercise']}")
            print(f"🎯 Confidence: {result['confidence']}%")
            print(f"🔢 Repetitions: {result['reps']}")
            print(f"📊 Sets: {result['sets']}")
            print(f"⚖️ Symmetry: {result['symmetry']}")
            print(f"🏃 Motion: {result['motion']['speed']} speed, {result['motion']['smoothness']} movement")
            print(f"📐 Posture: {result['posture']['status']} - {result['posture']['reason']}")
            print(f"💡 Correction: {result['correction']}")
            print(f"🔥 Calories: {result['calories']}")
            print(f"⏱️ Duration: {result['duration']}s")
            print(f"🎯 Suggestion: {result['suggestion']}")
            print(f"💪 Motivation: {result['motivation']}")
            
            # Display angle analysis
            if result['angles']:
                print(f"\n📐 Angle Analysis:")
                for joint, data in result['angles'].items():
                    status_icon = "✅" if data['in_ideal'] else "⚠️" if data['in_full_range'] else "❌"
                    print(f"  {status_icon} {joint.capitalize()}: {data['value']}° (ideal: {data['ideal_range']})")
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
        
        # Small delay between exercises
        time.sleep(1)
    
    # Display session summary
    print(f"\n📊 Session Summary:")
    print("-" * 40)
    session_summary = get_session_summary()
    for key, value in session_summary.items():
        print(f"  {key.capitalize()}: {value}")

def demonstrate_real_time_analysis():
    """Demonstrate real-time analysis capabilities"""
    print(f"\n🔄 Real-Time Analysis Demo")
    print("=" * 60)
    
    clf = load_model()
    reset_session()
    
    # Simulate real-time analysis with progressive data
    exercise = "squat"
    print(f"Simulating real-time {exercise} analysis...")
    
    for set_num in range(3):  # 3 sets
        print(f"\n🏋️ Set {set_num + 1}")
        print("-" * 20)
        
        for rep in range(5):  # 5 reps per set
            # Create data for this rep
            sample_data = create_sample_mediapipe_data(exercise, num_frames=8)
            
            # Analyze
            result = predict_activity_and_reps(sample_data, clf)
            
            if "error" not in result:
                print(f"Rep {rep + 1}: {result['reps']} reps | {result['posture']['status']} form | {result['correction']}")
                
                # Show fatigue progression
                if rep == 4:  # Last rep
                    print(f"  💤 Fatigue signals detected: {result['motion']['smoothness']} movement")
        
        # Rest between sets
        if set_num < 2:
            print("  😴 Rest period...")
            time.sleep(0.5)

def show_exercise_configurations():
    """Display all supported exercise configurations"""
    print(f"\n📋 Supported Exercise Configurations")
    print("=" * 60)
    
    for exercise, config in EXERCISE_CONFIG.items():
        print(f"\n🏋️ {exercise.upper()}")
        print(f"  Joints monitored: {', '.join(config['joints'])}")
        print(f"  Key angles: {', '.join(config['key_angles'].keys())}")
        print(f"  Calories/rep: {config['calories_per_rep']}")
        print(f"  Rest time: {config['rest_time']}s")
        print(f"  Progression: {' → '.join(config['difficulty_progression'])}")
        
        # Show common mistakes
        print(f"  Common mistakes:")
        for mistake, tip in config['common_mistakes'].items():
            print(f"    • {tip}")

if __name__ == "__main__":
    import numpy as np
    
    print("🚀 Starting AI Fitness Coach Demo...")
    
    try:
        # Show exercise configurations
        show_exercise_configurations()
        
        # Demonstrate comprehensive analysis
        demonstrate_fitness_coach()
        
        # Demonstrate real-time capabilities
        demonstrate_real_time_analysis()
        
        print(f"\n✅ Demo completed successfully!")
        print(f"\n💡 The AI Fitness Coach is ready to analyze your exercises!")
        print(f"   Just provide MediaPipe JSON data with 33 landmarks per frame.")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
