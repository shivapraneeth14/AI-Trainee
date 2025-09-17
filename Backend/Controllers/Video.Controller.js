import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import Result from "../Schemas/Result.Schema.js";

export const uploadVideo = async (req, res) => {
  try {
    if (!req.file) return res.status(400).json({ message: "No file uploaded" });

    const savedPath = req.file.path;
    const jobId = uuidv4();
    const userId = req.body.userId;

    // Call Flask synchronously
    const mlResponse = await axios.post(
      "http://localhost:5001/process",
      { path: savedPath, jobId },
      { timeout: 60000 }
    );

    const summary = mlResponse.data;
    console.log(summary);
    // Save full result
    const newResult = new Result({
      userId,
      jobId,
      exercise: summary.predicted_exercise,
      predictedExercise: summary.predicted_exercise,
      isCorrect: summary.is_correct,
      feedback: summary.feedback || [],
    });

    await newResult.save();

    return res.status(200).json({
      message: "Video processed and result saved",
      jobId,
      result: newResult,
    });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: "Error processing video", error: err.message });
  }
};
