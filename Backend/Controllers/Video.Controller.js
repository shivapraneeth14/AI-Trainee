import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import Result from "../Schemas/Result.Schema.js";

// ML service base URL (deployed or local)
const ML_BASE_URL = process.env.ML_SERVICE_URL || "https://ai-trainee-2.onrender.com";

export const uploadVideo = async (req, res) => {
  try {
    const { keypoints, userId } = req.body;

    if (!userId || !keypoints) {
      return res.status(400).json({ message: "Missing keypoints or userId" });
    }

    const jobId = uuidv4();

    // Call Flask ML service to process keypoints with enhanced AI fitness coach
    const mlResponse = await axios.post(
      `${ML_BASE_URL}/predict_activity`,
      { keypoints },
      { timeout: 30000 }
    );

    const summary = mlResponse.data;

    // Save comprehensive result in MongoDB
    const newResult = new Result({
      userId,
      jobId,
      // Enhanced AI Fitness Coach data
      exercise: summary.exercise || summary.predictedExercise,
      predictedExercise: summary.exercise || summary.predictedExercise,
      confidence: summary.confidence || 0,
      reps: summary.reps || 0,
      sets: summary.sets || 0,
      angles: summary.angles || {},
      symmetry: summary.symmetry || "Unknown",
      motion: summary.motion || {},
      posture: summary.posture || {},
      correction: summary.correction || "",
      calories: summary.calories || 0,
      duration: summary.duration || 0,
      suggestion: summary.suggestion || "",
      motivation: summary.motivation || "",
      // Legacy fields for backward compatibility
      isCorrect: summary.posture?.status === "Good" || summary.isCorrect || true,
      feedback: summary.posture?.reason ? [summary.posture.reason] : summary.feedback || [],
      keypoints: summary.keypoints,
      badge: summary.confidence > 90 ? "Gold" : summary.confidence > 70 ? "Silver" : "Bronze",
      cheatDetected: summary.posture?.status === "Bad" || summary.cheatDetected || false
    });

    await newResult.save();

    res.status(200).json({
      message: "AI Fitness Coach analysis completed and saved",
      jobId,
      result: {
        // Enhanced response with comprehensive analysis
        exercise: newResult.exercise,
        confidence: newResult.confidence,
        reps: newResult.reps,
        sets: newResult.sets,
        angles: newResult.angles,
        symmetry: newResult.symmetry,
        motion: newResult.motion,
        posture: newResult.posture,
        correction: newResult.correction,
        calories: newResult.calories,
        duration: newResult.duration,
        suggestion: newResult.suggestion,
        motivation: newResult.motivation,
        // Legacy fields
        predictedExercise: newResult.predictedExercise,
        isCorrect: newResult.isCorrect,
        feedback: newResult.feedback,
        badge: newResult.badge,
        cheatDetected: newResult.cheatDetected
      }
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Error processing keypoints with AI Fitness Coach", error: err.message });
  }
};

// Test endpoint for AI Fitness Coach
export const testFitnessCoach = async (req, res) => {
  try {
    const { userId } = req.body;
    
    if (!userId) {
      return res.status(400).json({ message: "Missing userId" });
    }

    // Create realistic sample keypoints for testing (squat movement)
    const sampleKeypoints = [];
    for (let i = 0; i < 15; i++) { // 15 frames for better detection
      const landmarks = [];
      
      // Simulate squat movement
      const squatProgress = Math.sin((i / 15) * Math.PI * 2); // Full squat cycle
      
      for (let j = 0; j < 33; j++) {
        let x, y, z;
        
        if (j === 23 || j === 24) { // Hip landmarks
          x = 0.5;
          y = 0.6 + squatProgress * 0.1;
          z = 0.0;
        } else if (j === 25 || j === 26) { // Knee landmarks
          x = 0.5;
          y = 0.7 + squatProgress * 0.15;
          z = 0.0;
        } else if (j === 11 || j === 12) { // Shoulder landmarks
          x = 0.5;
          y = 0.3;
          z = 0.0;
        } else {
          // Other landmarks
          x = 0.5 + (Math.random() - 0.5) * 0.1;
          y = 0.5 + (Math.random() - 0.5) * 0.1;
          z = (Math.random() - 0.5) * 0.1;
        }
        
        landmarks.push({
          x: x,
          y: y,
          z: z,
          visibility: 0.9
        });
      }
      sampleKeypoints.push({ landmarks });
    }

    const jobId = uuidv4();

    // Call Flask ML service
    const mlResponse = await axios.post(
      `${ML_BASE_URL}/predict_activity`,
      { keypoints: sampleKeypoints },
      { timeout: 30000 }
    );

    const summary = mlResponse.data;

    res.status(200).json({
      message: "AI Fitness Coach test completed",
      jobId,
      testData: {
        exercise: summary.exercise,
        confidence: summary.confidence,
        reps: summary.reps,
        sets: summary.sets,
        angles: summary.angles,
        symmetry: summary.symmetry,
        motion: summary.motion,
        posture: summary.posture,
        correction: summary.correction,
        calories: summary.calories,
        duration: summary.duration,
        suggestion: summary.suggestion,
        motivation: summary.motivation
      }
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: "Error testing AI Fitness Coach", error: err.message });
  }
};
