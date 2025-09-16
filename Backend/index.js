import express from "express";
import mongoose from "mongoose";
import dotenv from "dotenv";
import cors from "cors";
import router from "./Routes/User.routes.js";

dotenv.config();

const app = express();

// Middleware
app.use(
  cors({
    origin: "http://localhost:5173", // React app URL
    credentials: true,              // allow cookies/auth
  })
);
app.use(express.json());
app.use("/api",router);
// Test Route
app.get("/", (req, res) => {
  res.send("Backend is running 🚀");
});
app.post("/api/test", (req, res) => {
  console.log("Route hit!");
  res.json({ message: "Test route works" });
});
// MongoDB Connectio
mongoose
  .connect(process.env.MONGO_URI)
  .then(() => {
    console.log("✅ MongoDB connected");
    app.listen(process.env.PORT || 5000, () => {
      console.log(`🚀 Server running on port ${process.env.PORT || 5000}`);
    });
  })
  .catch((err) => console.error(err));
