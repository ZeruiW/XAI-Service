import dbConnect from "../../lib/dbConnect";
import Task from "../../models/Task";

export default async function handler(req, res) {
	const { method } = req;

	await dbConnect();

	if (method === "POST") {
		try {
			const task = await Task.create(req.body);
			res.status(201).json({ success: true, data: task });
		} catch (err) {
			res.status(400).json({ success: false });
		}
	} else {
		res.status(400).json({ success: false });
	}
}
