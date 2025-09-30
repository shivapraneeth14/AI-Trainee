import mongoose from "mongoose";

const resultSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  jobId: { type: String, required: true, unique: true },
  
  // Enhanced AI Fitness Coach fields
  exercise: { type: String },
  predictedExercise: { type: String }, // Legacy field
  confidence: { type: Number, default: 0 },
  reps: { type: Number, default: 0 },
  sets: { type: Number, default: 0 },
  angles: { type: mongoose.Schema.Types.Mixed, default: {} },
  symmetry: { type: String, default: "Unknown" },
  motion: { type: mongoose.Schema.Types.Mixed, default: {} },
  posture: { type: mongoose.Schema.Types.Mixed, default: {} },
  correction: { type: String, default: "" },
  calories: { type: Number, default: 0 },
  duration: { type: Number, default: 0 },
  suggestion: { type: String, default: "" },
  motivation: { type: String, default: "" },
  
  // Legacy fields for backward compatibility
  isCorrect: { type: Boolean },
  feedback: { type: [String], default: [] },
  keypoints: { type: Array, default: [] },
  badge: { type: String },
  cheatDetected: { type: Boolean },
  
  createdAt: { type: Date, default: Date.now },
});

const Result = mongoose.model("Result", resultSchema);
export default Result;
