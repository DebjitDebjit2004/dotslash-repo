const mongoose = require("mongoose");

const detectionDataSchema = new mongoose.Schema({
    age: {
        type: Number,
        required: true
    },
    pregnancies: {
        type: Number,
        required: true
    },
    weight: {
        type: Number,
        required: true
    },
    bloodPressure: {
        type: Number,
        required: true
    },
    glucose: {
        type: Number,
        required: true
    },
    bmi: {
        type: Number,
        required: true
    },
    insulin: {
        type: Number,
        required: true
    },
    pedigree: {
        type: Number,
        required: true,
        min: 0 // Assuming the pedigree function cannot be negative
    },
    author: {
        type: mongoose.Schema.Types.ObjectId,
        ref: "User",
    }
});

// Create a model based on the schema
const DetectionData = mongoose.model("DetectionData", detectionDataSchema);

module.exports = DetectionData;