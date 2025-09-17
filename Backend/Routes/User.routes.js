import { Router } from "express";
// import { getResult, uploadVideo } from "../Controllers/Video.Controller.js";
import upload from "../Middleware/Multer.js";
import {register,Login,getuserprofile} from "../Controllers/User.Controller.js";
import { uploadVideo } from "../Controllers/Video.Controller.js";

const router = Router();
router.route("/register").post(register);
router.route("/Login").post(Login);
router.route("/profile").get(getuserprofile);
router.post("/upload",upload.single("video"),uploadVideo);

// router.post("/upload", upload.single("video"), uploadVideo);
// router.get("/result/:jobId", getResult);
export default router;