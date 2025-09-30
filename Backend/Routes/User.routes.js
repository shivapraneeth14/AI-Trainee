import { Router } from "express";
// import { getResult, uploadVideo } from "../Controllers/Video.Controller.js";
import upload from "../Middleware/Multer.js";
import {register,Login,getuserprofile, getCurrentUserProfile, getUserResults, logout} from "../Controllers/User.Controller.js";
import { uploadVideo, testFitnessCoach } from "../Controllers/Video.Controller.js";

const router = Router();
router.route("/register").post(register);
router.route("/Login").post(Login);
router.route("/profile").get(getuserprofile);
router.route("/me").get(getCurrentUserProfile);
router.route("/results").get(getUserResults);
router.route("/logout").post(logout);
router.post("/upload",upload.single("video"),uploadVideo);
router.post("/test-fitness-coach", testFitnessCoach);

// router.post("/upload", upload.single("video"), uploadVideo);
// router.get("/result/:jobId", getResult);
export default router;