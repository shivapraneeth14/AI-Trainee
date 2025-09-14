import { Router } from "express";
import { getResult, uploadVideo } from "../Controllers/Video.Controller.js";
import upload from "../Middleware/Multer.js";
const router = Router();
router.post("/upload", upload.single("video"), uploadVideo);
router.get("/result/:jobId", getResult);
export default router;