import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import Result from "../Schemas/Result.Schema.js";

export const uploadVideo = async (req, res) => {
  console.log("route hit");
  try {
    console.log("uploadVideo", req.file);
    if (!req.file) return res.status(400).json({ message: "No file uploaded" });

    const savedPath = req.file.path;
    console.log("savedPath", savedPath);
    const jobId = uuidv4();
    const {userId }= req.body.userId; // pass userId from frontend
    console.log("userId", userId);
    // Trigger ML microservice
    const mlResponse = await axios.post(
      "http://localhost:5001/process",
      { path: savedPath, jobId },
      { timeout: 10000 }
    );

    const mlData = mlResponse.data;

    if (!mlData.summary) {
      return res.status(500).json({ message: "ML service returned no summary" });
    }

    const summary = mlData.summary;

    // Save summary directly in DB
    const newResult = new Result({
      userId,
      jobId,
      exercise: summary.predicted_exercise,
      isCorrect: summary.is_correct,
      predictedExercise: summary.predicted_exercise,
      feedback: summary.feedback || [],
    });

    await newResult.save();
    console.log("newResult", newResult);
    // ✅ Return the saved result along with jobId
    return res.status(200).json({
      message: "Video processed and result saved",
      jobId,
      result: newResult, // frontend can show it directly below the video
    });

  } catch (error) {
    console.error("Upload/Save Error:", error.message);
    return res.status(500).json({ message: "Error uploading video or saving result" });
  }
};



// import path from "path";
// import fs from "fs";
// import axios from "axios";
// import { v4 as uuidv4 } from "uuid";
// import { fileURLToPath } from "url";


// // Needed because __dirname is not available in ESM
// const __filename = fileURLToPath(import.meta.url);
// const __dirname = path.dirname(__filename);

// const UPLOAD_DIR = path.join(__dirname, "..", "uploads");
// const RESULTS_DIR = path.join(__dirname, "..", "results");

// if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });
// if (!fs.existsSync(RESULTS_DIR)) fs.mkdirSync(RESULTS_DIR, { recursive: true });

// // Upload video & trigger ML
// export const uploadVideo = async (req, res) => {
//   try {
//     if (!req.file) return res.status(400).json({ message: "No file uploaded" });

//     const savedPath = path.resolve(req.file.path);
//     const jobId = uuidv4();

//     // Trigger ML microservice
//     await axios.post(
//       "http://localhost:5001/process",
//       { path: savedPath, jobId, resultsDir: RESULTS_DIR },
//       { timeout: 5000 }
//     ).catch(err => {
//       console.warn("ML service trigger warning:", err.message);
//     });

//     return res.json({ jobId, message: "Video uploaded, processing started" });
//   } catch (error) {
//     console.error(error);
//     return res.status(500).json({ message: "Upload error" });
//   }
// };

// // Get ML result for a video
// export const getResult = (req, res) => {
//   const jobId = req.params.jobId;
//   const resultPath = path.join(RESULTS_DIR, `${jobId}.json`);

//   if (!fs.existsSync(resultPath)) {
//     return res.status(202).json({ status: "processing" });
//   }

//   try {
//     const raw = fs.readFileSync(resultPath, "utf8");
//     const data = JSON.parse(raw); // ML JSON as-is
//     return res.json({ status: "done", data });
//   } catch (e) {
//     console.error(e);
//     return res.status(500).json({ message: "Corrupt result file" });
//   }
// };
