const express = require("express");
const app = express();
const path = require("path");
const ejs = require("ejs");
const ejsMate = require("ejs-mate");
const methodOverride = require("method-override");
const session = require("express-session");
const mongoose = require("mongoose")
const passport = require("passport")
const LocalStrategy = require("passport-local");
const passportLocalMongoose = require('passport-local-mongoose');

//File requirement
const DetectionData = require("./Models/detectionDataSchema");
const User = require("./Models/userSchema");
const wrapAsync = require("./Utils/wrapAsync");
const ExpressError = require("./Utils/ExpressError");
const { isLoggedin, saveRedirectUrl } = require("./Middlewares/middleware");

// Custome Middlewares
app.set("view engine", "ejs");
app.set("Views", path.join(__dirname, "Views"));
app.use(express.urlencoded({ extended: true }));
app.use(express.static(path.join(__dirname, "/Public")));
app.use(methodOverride("_method"));
app.engine("ejs", ejsMate);

dbConnect().then((res) => { console.log("Database Connected") }).catch((err) => { console.log(err) })

// Database connection
async function dbConnect() {
    mongoose.connect("mongodb://127.0.0.1:27017/mecare")
}

const sessionOptions = {
    secret: "mysecretsuperkey",
    resave: false,
    saveUninitialized: true,
    cookie: {
        expires: Date.now() + 7 * 24 * 60 * 60 * 1000,
        maxAge: 7 * 24 * 60 * 60 * 1000,
        httpOnly: true,
    }
}

app.use(session(sessionOptions));

app.use(passport.initialize());
app.use(passport.session());

passport.use(new LocalStrategy(User.authenticate()));
passport.serializeUser(User.serializeUser());
passport.deserializeUser(User.deserializeUser());

app.use((req, res, next) => {
    res.locals.currUser = req.user;
    next();
})

//Home Page Route
app.get("/", (req, res) => {
    res.render("./Pages/home")
});

//
app.get("/detection", isLoggedin, (req, res) => {
    res.render("./Pages/detection")
});

app.get("/chatbot", isLoggedin, wrapAsync(async (req, res) => {
    const newDetection = new DetectionData(req.body.detection);
    console.log(req.body.detection)
    newDetection.author = req.user._id;
    await newDetection.save();
    res.render("./Pages/chatbot")
}));

app.get("/patient/register", (req, res) => {
    res.render("./Pages/register")
});

app.post("/patient/register", wrapAsync(async (req, res) => {
    try {
        const { name, username, email, address, diabeteseHistory, password } = req.body;
        const newUser = new User({ name, email, username, address, diabeteseHistory })
        const registerUser = await User.register(newUser, password);
        req.login(registerUser, (err) => {
            if (err) {
                return next(err);
            }
            return res.redirect("/");
        });
    } catch (err) {
        console.log(err);
        res.redirect("/");
    }
}));

app.get("/patient/login", (req, res) => {
    res.render("./Pages/login");
})

app.post("/patient/login", saveRedirectUrl, passport.authenticate("local", { failureRedirect: "/", }), async (req, res) => {
    let redirectUrl = res.locals.redirectUrl || "/";
    res.redirect(redirectUrl);
})

//Admin routes
app.get("/admin/login", (req, res) => {
    res.render("./Admin/admin");
});

//CUSTOM ERROR HANDLING (MIDDLEWARE)

app.all("*", (req, res, next) => {
    next(new ExpressError(404, "Page not Found!"));
});

app.use((err, req, res, next) => {
    let { statusCode = 500, message } = err;
    res.status(statusCode).send(message);
    next();
});

app.listen(8080, (req, res) => {
    console.log("Server is running on port 8080");
});