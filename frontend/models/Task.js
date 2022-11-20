import mongoose from "mongoose";

const TaskSchema = new mongoose.Schema({
	taskId: String,
	taskName: String,
	sampleList: [Buffer],
	stat: String,
	modelObject: String,
	xaiObject: String,
});

module.exports = mongoose.models.Task || mongoose.model("Task", TaskSchema);
