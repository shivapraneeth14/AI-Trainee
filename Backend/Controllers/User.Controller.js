import User from "../Schemas/User.Schema.js"
import bcrypt from "bcrypt"
import mongoose from "mongoose";
import Result from "../Schemas/Result.Schema.js";
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
    const { username, email, password } = req.body;
    console.log("Back end start",username)
    try {
        if (!username || !email || !password) {
            return res.status(400).json({ message: "Credentials not provided" });
        }
        const user = await User.findOne({ 
            $or: [
                { username },
                {  email }
            ]
        });
        if (user) {
            console.log(user)
            return res.status(400).json({ message: "User already exists" });

        }
        const hashedpassword = await bcrypt.hash(password,saltroundes)
        if(!hashedpassword){
            return res.status(400).json({message:"password is not hashed"})
        }
        console.log("hased password",hashedpassword)
        const newUser = new User({
            username,
            password: hashedpassword,
            email
        });
        console.log("newuser",newUser)
        const savedUser = await newUser.save();
        if (savedUser) {
            return res.status(201).json({ message: "User created successfully" });
        } else {
            return res.status(500).json({ message: "User not created" });
        }
        console.log("saved",savedUser)
    } catch (error) {
        console.error(error);
        return res.status(500).json({ message: "Server error" });
    }
};

const Login = async (req, res) => {
    const {loginname , password } = req.body;
    console.log(loginname,password)
    if ([loginname, password].some((field) => 
        field?.trim() === ""))
     {
        return res.status(400).json({ message: "Enter the credentials" });
    }
    try {
        const user = await User.findOne({ $or: [{ username: loginname }, { email: loginname }]})
        if (!user) {
            return res.status(404).json({ message: "No user found" });
        }
        console.log("user",user)

        const passwordCorrect = await user.isPasswordCorrect(password);
        if (!passwordCorrect) {
            return res.status(401).json({ message: "Incorrect password" });
        }
        console.log("correct password")

        const {accessToken,refreshToken} = await generatebothtoken(user._id)
        const loggedinuser = await User.findById(user._id).select("-password")
        console.log("accestoken:",accessToken)
        console.log("refreshtoken:",refreshToken)
        console.log(loggedinuser)
        console.log("login successfull")
       

        res.cookie("accessToken", accessToken, {  secure: true });
        res.cookie("refreshToken", refreshToken, {  secure: true });
        res.status(200).json({ message: "Logged in successfully", accessToken, refreshToken, loggedinuser });
    } catch (error) {
        console.error("Login error:", error);
        res.status(500).json({ message: "Internal server error" });
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
