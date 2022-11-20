import mongoose from "mongoose";

const ImageSchema = new mongoose.Schema({
	img: { data: Buffer, contentType: String },
});

module.exports = mongoose.models.Image || mongoose.model("Image", ImageSchema);
