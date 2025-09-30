import User from "../Schemas/User.Schema.js"
import bcrypt from "bcrypt"
import mongoose from "mongoose";
import Result from "../Schemas/Result.Schema.js";
import jwt from "jsonwebtoken";
const saltroundes = 10;
async function generatebothtoken(userid) {
    try {
        const user = await User.findById(userid);
        if (!user) {
            console.error(`generatebothtoken: User not found for id ${userid}`);
            throw new Error("User not found");
        }

        const accessToken = user.generateAccessToken();
        const refreshToken = user.generateRefreshToken();

        console.log(`generatebothtoken: Tokens generated for user ${userid}`);
        return { accessToken, refreshToken };
    } catch (error) {
        console.error("generatebothtoken error:", error);
        throw new Error("Error generating tokens");
    }
}
const register = async (req, res) => {
    const {
        username,
        password,
        role,
        region,
        sport,
        gender,
        age,
        specialization,
        experience,
        team,
        certification
    } = req.body;
    console.log("backend", req.body);
    try {
        // Validate fields based on role
        if (role === "athlete" && (!username || !region || !password || !sport || !gender || !age)) {
            return res.status(400).json({ message: "Please provide all athlete fields" });
        }
        if (role === "coach" && (!username || !region || !password || !specialization || !experience || !team || !certification)) {
            return res.status(400).json({ message: "Please provide all coach fields" });
        }

        // Check for existing user
        const existingUser = await User.findOne({ username });
        if (existingUser) {
            return res.status(400).json({ message: "User already exists" });
        }

        // Hash password
        const hashedPassword = await bcrypt.hash(password, 10);

        // Create user
        const newUser = new User({
            username,
            password: hashedPassword,
            role,
            region,
            sport: role === "athlete" ? sport : undefined,
            gender: role === "athlete" ? gender : undefined,
            age: role === "athlete" ? age : undefined,
            specialization: role === "coach" ? specialization : undefined,
            experience: role === "coach" ? experience : undefined,
            team: role === "coach" ? team : undefined,
            certification: role === "coach" ? certification : undefined
        });

        // Generate tokens
        const accessToken = newUser.generateAccessToken();
        const refreshToken = newUser.generateRefreshToken();

        // Save refresh token in DB
        newUser.refreshtoken = refreshToken;
        await newUser.save();

        return res.status(201).json({
            message: "User created successfully",
            user: {
                _id: newUser._id,
                username: newUser.username,
                role: newUser.role
            },
            tokens: {
                accessToken,
                refreshToken
            }
        });
    } catch (error) {
        console.error(error);
        return res.status(500).json({ message: "Server error" });
    }
};


const Login = async (req, res) => {
    const { loginname, password, role } = req.body;
    console.log(loginname, password, role);

    if ([loginname, password, role].some((field) => field?.trim() === "")) {
        return res.status(400).json({ message: "Enter the credentials" });
    }   

    try {
        // Check user by loginname (username/email) + role
        const user = await User.findOne({
            $or: [{ username: loginname }, { email: loginname }],
            role: role, // role condition added
        });

        if (!user) {
            return res.status(404).json({ message: `No ${role} found with given login details` });
        }

        // Verify password
        const passwordCorrect = await user.isPasswordCorrect(password);
        if (!passwordCorrect) {
            return res.status(401).json({ message: "Incorrect password" });
        }

        // Generate tokens
        const { accessToken, refreshToken } = await generatebothtoken(user._id);
        const loggedinuser = await User.findById(user._id).select("-password");

        // Send response
        res.cookie("accessToken", accessToken, { secure: true });
        res.cookie("refreshToken", refreshToken, { secure: true });

        return res.status(200).json({
            message: `${role} logged in successfully`,
            accessToken,
            refreshToken,
            loggedinuser,
        });

    } catch (error) {
        console.error("Login error:", error);
        return res.status(500).json({ message: "Internal server error" });
    }
};

const getuserprofile = async (req, res) => {
    const { username } =req.query;
    console.log("backend", username);

    try {
        const user = await User.findOne({ username });
        if (!user) {
            return res.status(404).json({ message: "No user found" });
        }
        console.log("backend successful");
        return res.status(200).json({ user });
    } catch (error) {
        console.log(error);
        return res.status(500).json({ message: "Internal server error" });
    }
};
// Logout current user: invalidate refresh token and clear cookies
export const logout = async (req, res) => {
    try {
        const authHeader = req.headers?.authorization || "";
        if (!authHeader || !authHeader.startsWith("Bearer ")) {
            // Still clear cookies even if header is missing
            res.clearCookie("accessToken");
            res.clearCookie("refreshToken");
            return res.status(200).json({ message: "Logged out" });
        }

        const token = authHeader.split(" ")[1];
        let payload;
        try {
            payload = jwt.verify(token, process.env.ACCESS_TOKEN_SECRET);
        } catch (_err) {
            // Token invalid/expired – clear cookies and return success
            res.clearCookie("accessToken");
            res.clearCookie("refreshToken");
            return res.status(200).json({ message: "Logged out" });
        }

        const userId = payload?._id;
        if (userId && mongoose.Types.ObjectId.isValid(userId)) {
            await User.findByIdAndUpdate(userId, { $set: { refreshtoken: null } });
        }

        res.clearCookie("accessToken");
        res.clearCookie("refreshToken");
        return res.status(200).json({ message: "Logged out" });
    } catch (error) {
        console.error("logout error:", error);
        return res.status(500).json({ message: "Internal server error" });
    }
};
// Get current logged-in user's profile using Bearer token
// Get current logged-in user's profile using Bearer token
export const getCurrentUserProfile = async (req, res) => {
    console.log("getCurrentUserProfile");
    try {

        const authHeader = req.headers?.authorization || "";
        if (!authHeader || !authHeader.startsWith("Bearer ")) {
            return res.status(401).json({ message: "Authorization header missing or malformed" });
        }
        console.log("authHeader", authHeader);

        const token = authHeader.split(" ")[1];
        if (!token) {
            return res.status(401).json({ message: "Token missing" });
        }
        console.log("token", token);
        let payload;
        try {
            payload = jwt.verify(token, process.env.ACCESS_TOKEN_SECRET);
        } catch (err) {
            return res.status(401).json({ message: "Invalid or expired token" });
        }

        const userId = payload?._id;
        if (!userId || !mongoose.Types.ObjectId.isValid(userId)) {
            return res.status(400).json({ message: "Invalid user identifier in token" });
        }
console.log("userId", userId);
        const user = await User.findById(userId).select(
            "username email bio profilePicture role region sport gender age specialization experience team certification createdAt updatedAt"
        );
        if (!user) {
            return res.status(404).json({ message: "User not found" });
        }

        return res.status(200).json({
            user: {
                _id: user._id,
                username: user.username,
                email: user.email,
                bio: user.bio,
                profilePicture: user.profilePicture,
                role: user.role,
                region: user.region,
                sport: user.sport,
                gender: user.gender,
                age: user.age,
                specialization: user.specialization,
                experience: user.experience,
                team: user.team,
                certification: user.certification,
                createdAt: user.createdAt,
                updatedAt: user.updatedAt,
            },
        });
    } catch (error) {
        console.error("getCurrentUserProfile error:", error);
        return res.status(500).json({ message: "Internal server error" });
    }
};
export const getUserResults = async (req, res) => {
    const { userId } = req.query; // or from token after login
    try {
      const results = await Result.find({ userId }).sort({ createdAt: -1 });
      return res.status(200).json({ results });
    } catch (error) {
      console.error(error);
      return res.status(500).json({ message: "Failed to fetch results" });
    }
  };
export{register,Login,getuserprofile};
