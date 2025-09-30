import mongoose from "mongoose";
import { Schema } from "mongoose";
import jwt from "jsonwebtoken"
import bcrypt from "bcrypt"

const userSchema = new mongoose.Schema({
    username: {
    type: String,
    required: true,
    unique: true,
    trim: true
  },

  password: {
    type: String,
    required: true
  },

  role: {
    type: String,
    enum: ["athlete", "coach"],
    required: true
  },

  // Athlete fields
  region: {
    type: String,
    trim: true
  },
  sport: {
    type: String,
    trim: true
  },
  gender: {
    type: String,
    enum: ["male", "female", "other"]
  },
  age: {
    type: Number
  },

  // Coach fields
  specialization: {
    type: String,
    trim: true
  },
  experience: {
    type: Number
  },
  team: {
    type: String,
    trim: true
  },
  certification: {
    type: String,
    trim: true
  },

  // Tokens
  refreshtoken: {
    type: String
  },
    
},{timestamps:true})
userSchema.methods.isPasswordCorrect = async function(password) {
    console.log("password verification completed")
    console.log(password)
    console.log(this.password)
    return await bcrypt.compare(password, this.password);
};
userSchema.methods.generateAccessToken = function () {
    return jwt.sign({
        _id: this._id,
        username: this.username,
        email: this.email
    }, process.env.ACCESS_TOKEN_SECRET);
};

userSchema.methods.generateRefreshToken = function () {
    return jwt.sign({
        _id: this._id
    }, process.env.REFRESH_TOKEN_SECRET);
};
const User = mongoose.model("User",userSchema)

export default User