const mongoose = require("mongoose");

const enquirySchema = new mongoose.Schema({
    name: {
        type: String,
        required: true,
    },
    email: {
        type: String,
        required: true,
    },
    topic: {
        type: String,
        required: true,
    },
    message: {
        type: String,
        required: true,
    },
    date: {
        type: Date.now(),
        required: true,
    },
});

const Enquiry = mongoose.model("Enquiry", enquirySchema);
module.exports = Enquiry;
