import multer from "multer";
import fs from "fs";

const uploadDir = "./Public/Temp";
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });

const storage = multer.diskStorage({
  
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => cb(null, file.originalname)
});

const upload = multer({ storage });

export default upload;
