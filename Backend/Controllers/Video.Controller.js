import path from "path";
import fs from "fs";
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import { fileURLToPath } from "url";

// Needed because __dirname is not available in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const UPLOAD_DIR = path.join(__dirname, "..", "uploads");
const RESULTS_DIR = path.join(__dirname, "..", "results");

if (!fs.existsSync(UPLOAD_DIR)) fs.mkdirSync(UPLOAD_DIR, { recursive: true });
if (!fs.existsSync(RESULTS_DIR)) fs.mkdirSync(RESULTS_DIR, { recursive: true });

// @desc    Upload video & trigger ML processing
// @route   POST /api/videos/upload
export const uploadVideo = async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ message: "No file uploaded" });
    }

    const savedPath = path.resolve(req.file.path);
    const jobId = uuidv4();

    // Trigger ML microservice
    console.log(savedPath);
    console.log(jobId);
    console.log(RESULTS_DIR);

    await axios.post(
      "http://localhost:5001/process",
      { path: savedPath, jobId, resultsDir: RESULTS_DIR },
      { timeout: 5000 }
    ).catch(err => {
      console.warn("ML service trigger warning:", err.message);
    });

    return res.json({ jobId, message: "Video uploaded, processing started" });
  } catch (error) {
    console.error(error);
    return res.status(500).json({ message: "Upload error" });
  }
};

// @desc    Get ML results for a video
// @route   GET /api/videos/result/:jobId
export const getResult = (req, res) => {
  const jobId = req.params.jobId;
  const resultPath = path.join(RESULTS_DIR, `${jobId}.json`);

  if (!fs.existsSync(resultPath)) {
    return res.status(202).json({ status: "processing" });
  }

  try {
    const raw = fs.readFileSync(resultPath, "utf8");
    const data = JSON.parse(raw);
    return res.json({ status: "done", data });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ message: "Corrupt result file" });
  }
};
