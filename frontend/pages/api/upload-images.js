import dbConnect from "../../lib/dbConnect";
import Image from "../../models/Image";

export default async function handler(req, res) {
	const { method } = req;

	await dbConnect();

	if (method === "POST") {
		try {
			const image = await Image.create(req.body);
			res.status(201).json({ success: true, data: image });
		} catch (err) {
			res.status(400).json({ success: false });
		}
	} else {
		res.status(400).json({ success: false });
	}
}
