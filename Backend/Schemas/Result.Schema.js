import mongoose from "mongoose";

const resultSchema = new mongoose.Schema({
  userId: { type: mongoose.Schema.Types.ObjectId, ref: "User", required: true },
  jobId: { type: String, required: true, unique: true },
  exercise: { type: String },
  predictedExercise: { type: String },
  isCorrect: { type: Boolean },
  feedback: { type: [String], default: [] },
  createdAt: { type: Date, default: Date.now },
});

const Result = mongoose.model("Result", resultSchema);
export default Result;
